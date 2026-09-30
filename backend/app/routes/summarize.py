import logging

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.schemas.summarize import SummarizeRequest, SummarizeResponse
from app.services.gemini import GeminiError, summarize_context
from app.services.retriever import retrieve_context

logger = logging.getLogger("summarizer")
router = APIRouter(prefix="/api/v1", tags=["summarize"])


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(payload: SummarizeRequest):
    settings = get_settings()
    text = payload.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="The page has no readable text.")
    if len(text) > settings.MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=413,
            detail=f"This page is too large (limit: {settings.MAX_TEXT_LENGTH} characters).",
        )
    if len(text) < settings.MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail="This page has too little text to summarize.",
        )

    try:
        chunks = retrieve_context(text)
        if not chunks:
            raise HTTPException(status_code=400, detail="The page has no readable text.")
        summary = summarize_context(chunks)
    except HTTPException:
        raise
    except GeminiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Unexpected error: %s", type(e).__name__)
        raise HTTPException(status_code=500, detail="Something went wrong on the server.")

    return SummarizeResponse(summary=summary)