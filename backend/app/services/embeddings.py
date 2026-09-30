from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings


QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


@lru_cache
def get_model() -> SentenceTransformer:
    """Load the model once and reuse it (loading is slow)."""
    return SentenceTransformer(get_settings().EMBEDDING_MODEL)


def embed_chunks(chunks: list[str]) -> np.ndarray:
    """Chunks -> matrix of shape (num_chunks, 384), float32, normalized."""
    vectors = get_model().encode(chunks, normalize_embeddings=True)
    return np.asarray(vectors, dtype="float32")


def embed_query(query: str) -> np.ndarray:
    """Query -> matrix of shape (1, 384), float32, normalized."""
    vector = get_model().encode([QUERY_INSTRUCTION + query], normalize_embeddings=True)
    return np.asarray(vector, dtype="float32")