from __future__ import annotations

import csv
import io
import json
import logging
import threading
import uuid
from typing import Any

from app.ml.feature_builder import build_features
from app.ml.model_registry import ModelRegistry
from app.schemas.inference import ExplanationFactor
from app.storage.repositories import BatchJobRepository

logger = logging.getLogger(__name__)


class BatchService:
    def __init__(self, repo: BatchJobRepository, registry: ModelRegistry) -> None:
        self._repo = repo
        self._registry = registry

    def start_job(self, data_csv: str, chunk_size: int = 10) -> str:
        records = list(csv.DictReader(io.StringIO(data_csv.strip())))
        if not records:
            raise ValueError("CSV contains no data rows")

        job_id = uuid.uuid4().hex[:16]
        self._repo.create(job_id, total_records=len(records))
        self._repo.update_status(job_id, "running")

        thread = threading.Thread(
            target=self._process_job,
            args=(job_id, records, chunk_size),
            daemon=True,
        )
        thread.start()
        return job_id

    def _predict_sync(self, supplier_data: dict) -> dict:
        features = build_features(supplier_data)
        model_version = self._registry.get_production()
        if model_version is None:
            raise RuntimeError("No production model registered")

        prediction = model_version.model_instance.predict(features)
        explanation_raw = model_version.model_instance.explain(features)
        explanation = [ExplanationFactor(**f) for f in explanation_raw]

        return {
            "supplier_id": supplier_data.get("supplier_id", "unknown"),
            "risk_score": prediction["risk_score"],
            "risk_level": prediction["risk_level"],
            "model_version": model_version.version,
            "explanation": [e.model_dump() for e in explanation],
        }

    def _map_csv_row(self, row: dict[str, str]) -> dict[str, Any]:
        return {
            "supplier_id": row.get("supplier_id", "unknown"),
            "lead_time_days": int(row.get("lead_time_days", 0)),
            "defect_rate": float(row.get("defect_rate", 0.0)),
            "late_delivery_count": int(row.get("late_delivery_count", 0)),
            "order_value": float(row.get("order_value", 0.0)),
            "country": row.get("country", "XX"),
        }

    def _process_job(self, job_id: str, records: list[dict], chunk_size: int) -> None:
        all_results: list[dict] = []
        processed = 0
        failed = 0

        try:
            for i in range(0, len(records), chunk_size):
                chunk = records[i : i + chunk_size]

                for row in chunk:
                    try:
                        supplier_data = self._map_csv_row(row)
                        result = self._predict_sync(supplier_data)
                        all_results.append(result)
                        processed += 1
                    except Exception:
                        try:
                            supplier_data = self._map_csv_row(row)
                            result = self._predict_sync(supplier_data)
                            all_results.append(result)
                            processed += 1
                        except Exception as retry_err:
                            logger.warning(
                                "Batch job %s: failed record %s: %s",
                                job_id,
                                row.get("supplier_id", "?"),
                                retry_err,
                            )
                            all_results.append({
                                "supplier_id": row.get("supplier_id", "unknown"),
                                "error": str(retry_err),
                            })
                            failed += 1
                            processed += 1

                self._repo.update_progress(job_id, processed, failed)

            self._repo.update_status(
                job_id, "completed", results=json.dumps(all_results)
            )
        except Exception as exc:
            logger.exception("Batch job %s failed: %s", job_id, exc)
            self._repo.update_status(job_id, "failed")

    def get_job(self, job_id: str) -> dict | None:
        return self._repo.get(job_id)

    def list_jobs(self, limit: int = 20) -> list[dict]:
        return self._repo.list_all(limit=limit)


_instance: BatchService | None = None


def get_batch_service() -> BatchService:
    global _instance
    if _instance is None:
        _instance = BatchService(
            repo=BatchJobRepository(),
            registry=ModelRegistry(),
        )
    return _instance
