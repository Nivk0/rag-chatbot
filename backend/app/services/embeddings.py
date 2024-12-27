from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingService:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
    
    def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
