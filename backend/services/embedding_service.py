
import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Optional
from utils.text_extractor import extract_text, chunk_text
from utils.hf_embeddings import get_embeddings
from services.file_service import get_file_service
import uuid

class EmbeddingService:

    
    def __init__(self, chroma_base_path: str = "./chroma"):
        self.chroma_base_path = chroma_base_path
        os.makedirs(chroma_base_path, exist_ok=True)
    
    def get_collection_name(self, subject: str, unit: str) -> str:

        # ChromaDB collection names must be alphanumeric with underscores
        return f"{subject}_{unit}".replace(" ", "_").replace("-", "_").lower()
    
    def get_or_create_collection(self, subject: str, unit: str):

        collection_name = self.get_collection_name(subject, unit)
        
        # Create persistent client
        client = chromadb.PersistentClient(
            path=os.path.join(self.chroma_base_path, collection_name)
        )
        
        # Get embeddings function
        embeddings = get_embeddings()
        
        # Get or create collection
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"subject": subject, "unit": unit}
        )
        
        return collection, embeddings
    
    def process_and_embed_documents(self, subject: str, unit: str) -> Dict:

        file_service = get_file_service()
        
        # Get all documents
        documents = file_service.get_all_documents(subject, unit)
        
        if not documents:
            return {
                "status": "error",
                "message": "No documents found for this subject/unit"
            }
        
        # Get or create collection
        collection, embeddings = self.get_or_create_collection(subject, unit)
        
        total_chunks = 0
        processed_files = []
        
        for doc_path in documents:
            try:
                # Extract text
                text = extract_text(doc_path)
                
                if not text:
                    continue
                
                # Chunk text
                chunks = chunk_text(text, chunk_size=1000, chunk_overlap=200)
                
                if not chunks:
                    continue
                
                # Generate embeddings
                chunk_embeddings = embeddings.embed_documents(chunks)
                
                # Prepare data for ChromaDB
                ids = [str(uuid.uuid4()) for _ in chunks]
                metadatas = [
                    {
                        "source": os.path.basename(doc_path),
                        "subject": subject,
                        "unit": unit,
                        "chunk_index": i
                    }
                    for i in range(len(chunks))
                ]
                
                # Add to collection
                collection.add(
                    ids=ids,
                    embeddings=chunk_embeddings,
                    documents=chunks,
                    metadatas=metadatas
                )
                
                total_chunks += len(chunks)
                processed_files.append({
                    "file": os.path.basename(doc_path),
                    "chunks": len(chunks)
                })
                
            except Exception as e:
                print(f"Error processing {doc_path}: {str(e)}")
                continue
        
        # Mark embedding as done
        file_service.mark_embedding_done(subject, unit)
        
        return {
            "status": "success",
            "subject": subject,
            "unit": unit,
            "total_chunks": total_chunks,
            "processed_files": processed_files,
            "collection_name": self.get_collection_name(subject, unit)
        }
    
    def query_documents(self, subject: str, unit: str, query: str, n_results: int = 5) -> List[Dict]:

        collection, embeddings = self.get_or_create_collection(subject, unit)
        
        # Generate query embedding
        query_embedding = embeddings.embed_query(query)
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results.get('distances') else None
                })
        
        return formatted_results
    
    def get_all_documents_content(self, subject: str, unit: str) -> str:

        collection, _ = self.get_or_create_collection(subject, unit)
        
        # Get all documents from collection
        results = collection.get()
        
        if results and results['documents']:
            # Concatenate all chunks
            return "\n\n".join(results['documents'])
        
        return ""

# Global instance
_embedding_service_instance = None

def get_embedding_service() -> EmbeddingService:

    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance
