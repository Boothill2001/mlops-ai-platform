from __future__ import annotations

from pydantic import BaseModel, Field


class BatchRunRequest(BaseModel):
    data_csv: str
    chunk_size: int = Field(default=10, ge=1)


class BatchJobSummary(BaseModel):
    job_id: str
    status: str
    total_records: int
    processed_records: int
    failed_records: int
    progress_pct: float
    created_at: str
    completed_at: str | None = None


class BatchJobDetail(BatchJobSummary):
    results: list[dict] = []
