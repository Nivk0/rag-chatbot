from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict
import hashlib
from ..core.config import settings

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
    
    def _get_collection_name(self, document_id: str) -> str:
        """Create a unique collection name for each document"""
        # Hash the document ID to ensure valid collection name
        hashed = hashlib.md5(document_id.encode()).hexdigest()
        return f"doc_{hashed}"
    
    def _ensure_collection(self, collection_name: str):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # BGE-small-en dimension
                    distance=models.Distance.COSINE
                )
            )
    
    def add_document(self, document_id: str, embeddings: List[List[float]], metadata: List[Dict]):
        """Add embeddings for a specific document"""
        collection_name = self._get_collection_name(document_id)
        self._ensure_collection(collection_name)
        
        points = [
            models.PointStruct(
                id=i,
                vector=embedding,
                payload=metadata[i]
            )
            for i, embedding in enumerate(embeddings)
        ]
        
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
    
    def delete_document(self, document_id: str):
        """Delete a document's collection"""
        collection_name = self._get_collection_name(document_id)
        try:
            self.client.delete_collection(collection_name=collection_name)
        except Exception:
            pass
    
    def search(self, query_vector: List[float], document_ids: List[str], limit: int = 5):
        """Search within specific documents"""
        all_results = []
        
        for doc_id in document_ids:
            collection_name = self._get_collection_name(doc_id)
            try:
                results = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit
                )
                all_results.extend(results)
            except Exception:
                continue
        
        # sort the results by score and take top k
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:limit]