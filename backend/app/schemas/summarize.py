from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Webpage text")


class SummarizeResponse(BaseModel):
    summary: str