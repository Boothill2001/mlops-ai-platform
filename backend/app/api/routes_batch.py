from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from app.schemas.batch import BatchJobDetail, BatchJobSummary, BatchRunRequest
from app.services.batch_service import get_batch_service
from app.storage.seed_data import SAMPLE_CSV_DATA

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])


@router.post("/run")
async def run_batch(request: BatchRunRequest) -> dict:
    service = get_batch_service()
    try:
        job_id = service.start_job(request.data_csv, request.chunk_size)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "job_id": job_id,
        "status": "queued",
        "message": f"Batch job {job_id} started with chunk_size={request.chunk_size}",
    }


@router.get("/jobs/{job_id}", response_model=BatchJobDetail)
async def get_job(job_id: str) -> BatchJobDetail:
    service = get_batch_service()
    job = service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    results = []
    if job.get("results"):
        results = json.loads(job["results"])

    total = job.get("total_records", 0)
    processed = job.get("processed_records", 0)
    progress_pct = round((processed / total) * 100, 1) if total > 0 else 0.0

    return BatchJobDetail(
        job_id=job["job_id"],
        status=job["status"],
        total_records=total,
        processed_records=processed,
        failed_records=job.get("failed_records", 0),
        progress_pct=progress_pct,
        created_at=job.get("created_at", ""),
        completed_at=job.get("completed_at"),
        results=results,
    )


@router.get("/jobs", response_model=list[BatchJobSummary])
async def list_jobs(limit: int = 20) -> list[BatchJobSummary]:
    service = get_batch_service()
    jobs = service.list_jobs(limit=limit)
    summaries = []
    for job in jobs:
        total = job.get("total_records", 0)
        processed = job.get("processed_records", 0)
        progress_pct = round((processed / total) * 100, 1) if total > 0 else 0.0
        summaries.append(
            BatchJobSummary(
                job_id=job["job_id"],
                status=job["status"],
                total_records=total,
                processed_records=processed,
                failed_records=job.get("failed_records", 0),
                progress_pct=progress_pct,
                created_at=job.get("created_at", ""),
                completed_at=job.get("completed_at"),
            )
        )
    return summaries


@router.post("/run-sample")
async def run_sample_batch() -> dict:
    service = get_batch_service()
    job_id = service.start_job(SAMPLE_CSV_DATA, chunk_size=10)
    return {
        "job_id": job_id,
        "status": "queued",
        "message": f"Sample batch job {job_id} started with 20 supplier records",
    }
