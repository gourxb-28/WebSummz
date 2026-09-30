from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes.summarize import router as summarize_router
from app.services.embeddings import get_model

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_model()
    yield


app = FastAPI(title="Webpage Summarizer API", version="1.0.0", lifespan=lifespan)

# Order matters: middleware added LAST is outermost. Register the size limit first
# so CORS wraps it, otherwise a 413 would be missing CORS headers.
MAX_BODY_BYTES = settings.MAX_TEXT_LENGTH * 4 + 1024  # UTF-8: up to 4 bytes per character


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Request is too large."})
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": 'Invalid request. Send JSON like {"text": "..."}.'},
    )


app.include_router(summarize_router)


@app.get("/health")
def health():
    return {"status": "ok"}