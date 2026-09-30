from app.config import get_settings
from app.services.chunking import chunk_text, clean_text
from app.services.embeddings import embed_chunks, embed_query
from app.services.vectorstore import VectorStore


SUMMARY_QUERY = "Summarize the main points and key information of this webpage."


def retrieve_context(text: str) -> list[str]:
    """Raw webpage text -> the most relevant chunks, in original page order."""
    settings = get_settings()

    cleaned = clean_text(text)
    chunks = chunk_text(cleaned)

    if len(chunks) <= settings.TOP_K:
        return chunks

    store = VectorStore(chunks, embed_chunks(chunks))
    results = store.search(embed_query(SUMMARY_QUERY), k=settings.TOP_K)

    selected = [chunk for chunk, _score in results]
    selected.sort(key=chunks.index)
    return selected