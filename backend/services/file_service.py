
import os
import json
import shutil
from typing import Optional, Dict, List
from datetime import datetime

class FileService:

    
    def __init__(self, base_storage_path: str = "./storage"):
        self.base_storage_path = base_storage_path
        os.makedirs(base_storage_path, exist_ok=True)
    
    def get_subject_unit_path(self, subject: str, unit: str) -> str:

        path = os.path.join(self.base_storage_path, "subjects", subject, unit)
        return os.path.abspath(path)
    
    def get_docs_path(self, subject: str, unit: str) -> str:

        return os.path.join(self.get_subject_unit_path(subject, unit), "docs")
    
    def get_embeddings_path(self, subject: str, unit: str) -> str:

        return os.path.join(self.get_subject_unit_path(subject, unit), "embeddings")
    
    def get_summaries_path(self, subject: str, unit: str) -> str:

        return os.path.join(self.get_subject_unit_path(subject, unit), "summaries")
    
    def get_metadata_path(self, subject: str, unit: str) -> str:

        return os.path.join(self.get_subject_unit_path(subject, unit), "metadata.json")
    
    def create_subject_unit_structure(self, subject: str, unit: str):

        os.makedirs(self.get_docs_path(subject, unit), exist_ok=True)
        os.makedirs(self.get_embeddings_path(subject, unit), exist_ok=True)
        os.makedirs(self.get_summaries_path(subject, unit), exist_ok=True)
        
        # Initialize metadata if it doesn't exist
        metadata_path = self.get_metadata_path(subject, unit)
        if not os.path.exists(metadata_path):
            self.save_metadata(subject, unit, {
                "subject": subject,
                "unit": unit,
                "created_at": datetime.utcnow().isoformat(),
                "embedding_done": False,
                "documents": []
            })
    
    def save_file(self, subject: str, unit: str, file_path: str, file_content: bytes, replace: bool = False) -> str:

        self.create_subject_unit_structure(subject, unit)
        
        # If replace mode, clear existing documents
        if replace:
            docs_path = self.get_docs_path(subject, unit)
            if os.path.exists(docs_path):
                # Delete all files in docs folder
                for filename in os.listdir(docs_path):
                    file_to_delete = os.path.join(docs_path, filename)
                    if os.path.isfile(file_to_delete):
                        os.remove(file_to_delete)
                
                # Clear embeddings (they're now outdated)
                embeddings_path = self.get_embeddings_path(subject, unit)
                if os.path.exists(embeddings_path):
                    shutil.rmtree(embeddings_path)
                    os.makedirs(embeddings_path, exist_ok=True)
                
                # Reset metadata
                metadata = {
                    "subject": subject,
                    "unit": unit,
                    "created_at": datetime.utcnow().isoformat(),
                    "embedding_done": False,
                    "documents": [],
                    "replaced_at": datetime.utcnow().isoformat()
                }
                self.save_metadata(subject, unit, metadata)
        
        filename = os.path.basename(file_path)
        save_path = os.path.join(self.get_docs_path(subject, unit), filename)
        
        with open(save_path, 'wb') as f:
            f.write(file_content)
        
        # Update metadata
        metadata = self.load_metadata(subject, unit)
        
        # Check if this exact file already exists
        existing_doc = None
        for doc in metadata.get("documents", []):
            if doc.get("filename") == filename:
                existing_doc = doc
                break
        
        if existing_doc:
            # Update existing document timestamp
            existing_doc["updated_at"] = datetime.utcnow().isoformat()
        else:
            # Add new document
            metadata.setdefault("documents", []).append({
                "filename": filename,
                "uploaded_at": datetime.utcnow().isoformat(),
                "path": save_path
            })
        
        # Reset embedding status when files change
        metadata["embedding_done"] = False
        self.save_metadata(subject, unit, metadata)
        
        return save_path
    
    def load_metadata(self, subject: str, unit: str) -> Dict:

        metadata_path = self.get_metadata_path(subject, unit)
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        
        return {
            "subject": subject,
            "unit": unit,
            "embedding_done": False,
            "documents": []
        }
    
    def save_metadata(self, subject: str, unit: str, metadata: Dict):

        metadata_path = self.get_metadata_path(subject, unit)
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_all_documents(self, subject: str, unit: str) -> List[str]:

        docs_path = self.get_docs_path(subject, unit)
        
        if not os.path.exists(docs_path):
            return []
        
        documents = []
        for filename in os.listdir(docs_path):
            file_path = os.path.join(docs_path, filename)
            if os.path.isfile(file_path):
                documents.append(file_path)
        
        return documents
    
    def is_embedding_done(self, subject: str, unit: str) -> bool:

        metadata = self.load_metadata(subject, unit)
        return metadata.get("embedding_done", False)
    
    def mark_embedding_done(self, subject: str, unit: str):

        metadata = self.load_metadata(subject, unit)
        metadata["embedding_done"] = True
        metadata["embedding_completed_at"] = datetime.utcnow().isoformat()
        self.save_metadata(subject, unit, metadata)
    
    def get_all_subjects(self) -> List[str]:

        subjects_path = os.path.join(self.base_storage_path, "subjects")
        if not os.path.exists(subjects_path):
            return []
        
        return [d for d in os.listdir(subjects_path) 
                if os.path.isdir(os.path.join(subjects_path, d))]
    
    def get_units_for_subject(self, subject: str) -> List[str]:

        subject_path = os.path.join(self.base_storage_path, "subjects", subject)
        if not os.path.exists(subject_path):
            return []
        
        return [d for d in os.listdir(subject_path) 
                if os.path.isdir(os.path.join(subject_path, d))]

# Global instance
_file_service_instance = None

def get_file_service() -> FileService:

    global _file_service_instance
    if _file_service_instance is None:
        _file_service_instance = FileService()
    return _file_service_instance
