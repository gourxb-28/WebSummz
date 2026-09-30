import numpy as np
from app.services.embeddings import embed_chunks, embed_query

chunks = [
    "The Eiffel Tower is a wrought-iron tower in Paris, France.",
    "Python is a popular programming language used for data science.",
    "Paris is the capital of France and is known for its landmarks.",
]
vectors = embed_chunks(chunks)
query = embed_query("Tell me about landmarks in Paris")

print("Chunk matrix shape:", vectors.shape)   # (3, 384)
print("Query shape:", query.shape)            # (1, 384
print("Vector length (should be ~1):", np.linalg.norm(vectors[0]))
print("Similarity scores:", (vectors @ query.T).flatten())