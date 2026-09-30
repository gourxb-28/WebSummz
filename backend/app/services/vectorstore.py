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

    def score_all(self, query_vector: np.ndarray) -> np.ndarray:
        """Similarity score of EVERY chunk to the query, indexed by chunk position."""
        scores, ids = self.index.search(query_vector, len(self.chunks))
        by_position = np.zeros(len(self.chunks), dtype="float32")
        by_position[ids[0]] = scores[0]
        return by_position