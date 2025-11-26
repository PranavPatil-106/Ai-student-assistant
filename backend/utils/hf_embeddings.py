
from sentence_transformers import SentenceTransformer
import os
from typing import List

class HuggingFaceEmbeddings:

    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):

        self.model_name = model_name
        print(f"Loading embedding model: {model_name}...")
        print("Note: Model will be downloaded on first use and cached locally.")
        
        # Load model - it will download to cache if not present
        # Cache location: ~/.cache/torch/sentence_transformers/
        self.model = SentenceTransformer(model_name)
        print(f"✓ Model '{model_name}' loaded successfully!")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def get_embedding_dimension(self) -> int:

        return self.model.get_sentence_embedding_dimension()

# Global instance (lazy loaded)
_embeddings_instance = None

def get_embeddings(model_name: str = "all-MiniLM-L6-v2") -> HuggingFaceEmbeddings:

    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(model_name)
    return _embeddings_instance
