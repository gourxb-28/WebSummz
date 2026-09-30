from app.services.embeddings import embed_chunks, embed_query
from app.services.vectorstore import VectorStore

chunks = [
    "The Eiffel Tower is a wrought-iron tower in Paris, France.",
    "Python is a popular programming language used for data science.",
    "Paris is the capital of France and is known for its landmarks.",
    "Cats are small domesticated carnivorous mammals.",
]
store = VectorStore(chunks, embed_chunks(chunks))

for chunk, score in store.search(embed_query("Tell me about landmarks in Paris"), k=2):
    print(f"{score:.3f}  {chunk}")