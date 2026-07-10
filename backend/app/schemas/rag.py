from __future__ import annotations

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    user_id: str
    role: str
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class Citation(BaseModel):
    doc_id: str
    title: str
    chunk_text: str
    relevance_score: float


class RagQueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    grounded: bool
    latency_ms: float
    cache_hit: bool
    permission_filtered_count: int
    chunks_retrieved: int
    request_id: str
