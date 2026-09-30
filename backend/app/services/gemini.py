import httpx
from google import genai
from google.genai import errors, types

from app.config import get_settings

SYSTEM_INSTRUCTION = (
    "You summarize webpages. The user message contains excerpts taken from "
    "different parts of one webpage, in page order. "
    "Use ONLY these excerpts. Do not add facts, numbers, or opinions that are not in them. "
    "Ignore navigation menus, ads, cookie notices, and other boilerplate. "
    "If something is unclear or missing, say so briefly instead of guessing. "
    "Write the summary in this format: one or two sentences saying what the page is about, "
    "then 4-6 bullet points covering the main ideas across the whole page, "
    "and finish with a one-line takeaway."
)

TIMEOUT_MS = 30_000


class GeminiError(Exception):
    """Safe, user-friendly error. The message is OK to show to the user."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def summarize_context(chunks: list[str]) -> str:
    settings = get_settings()
    if not settings.GEMINI_API_KEY or not settings.GEMINI_MODEL:
        raise GeminiError("Server is not configured correctly.", 500)

    context = "\n\n---\n\n".join(chunks)
    prompt = f"Context from the webpage:\n\n{context}\n\nWrite the summary now."

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=TIMEOUT_MS),
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2, 
            ),
        )
    except httpx.TimeoutException:
        raise GeminiError("The AI service took too long. Please try again.", 504)
    except errors.APIError as e:
        # Log only the status code. Never the prompt or the key.
        print(f"Gemini API error: status={e.code}")
        if e.code == 429:
            raise GeminiError("Rate limit reached. Please wait and try again.", 429)
        if e.code in (400, 401, 403, 404):
            # Bad key, wrong model name, or no access. Details stay in server logs.
            raise GeminiError("The AI service rejected the request. Check server configuration.", 502)
        raise GeminiError("The AI service is temporarily unavailable.", 503)
    except Exception as e:
        print(f"Unexpected Gemini failure: {type(e).__name__}")
        raise GeminiError("Could not reach the AI service.", 502)

    if not response.text:
        raise GeminiError("The AI returned no summary for this page.", 502)
    return response.text.strip()