import faiss
import numpy as np


class VectorStore:
    """A small in-memory FAISS index built fresh for each request."""

    def __init__(self, chunks: list[str], vectors: np.ndarray):
        self.chunks = chunks
        dim = vectors.shape[1]                 # 384 for bge
        self.index = faiss.IndexFlatIP(dim)    
        self.index.add(vectors)              

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[str, float]]:
        k = min(k, len(self.chunks))      
        scores, ids = self.index.search(query_vector, k)
        return [
            (self.chunks[i], float(s))
            for i, s in zip(ids[0], scores[0])
            if i != -1                         # no results for this query
        ]