from pydantic import BaseModel, Field
from typing import Any

class QueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    dataset: str | None = None

class AnalyzeResponse(BaseModel):
    query: str
    plan: list[str]
    metrics: dict[str, Any]
    chart: dict[str, Any]
    insights: list[str]
    pipeline: list[dict[str, Any]]
    errors: list[str] = []
