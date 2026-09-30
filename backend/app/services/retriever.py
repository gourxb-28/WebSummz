import numpy as np

from app.config import get_settings
from app.services.chunking import chunk_text, clean_text
from app.services.embeddings import embed_chunks, embed_query
from app.services.vectorstore import VectorStore

SUMMARY_QUERY = "Summarize the main points and key information of this webpage."


def retrieve_context(text: str) -> list[str]:
    """Raw text -> one best chunk from each section of the page, in page order."""
    settings = get_settings()

    chunks = chunk_text(clean_text(text))

    if len(chunks) <= settings.TOP_K:
        return chunks

    store = VectorStore(chunks, embed_chunks(chunks))
    scores = store.score_all(embed_query(SUMMARY_QUERY))

    sections = np.array_split(np.arange(len(chunks)), settings.TOP_K)
    picked = [int(sec[np.argmax(scores[sec])]) for sec in sections]

    print(f"chunks={len(chunks)} selected={len(picked)}")
    return [chunks[i] for i in picked]