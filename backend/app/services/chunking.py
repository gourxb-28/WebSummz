import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings


def clean_text(text: str) -> str:
    """Normalize whitespace so chunks aren't wasted on blank space."""
    text = text.replace("\r\n", "\n").replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)       
    text = re.sub(r"\n\s*\n+", "\n\n", text) 
    return text.strip()


def chunk_text(text: str) -> list[str]:
    """Split cleaned text into overlapping chunks."""
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    return splitter.split_text(text)