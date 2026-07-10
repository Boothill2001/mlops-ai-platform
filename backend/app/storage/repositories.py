from __future__ import annotations

import json
from datetime import datetime, timezone

from app.storage.database import get_connection


class HistoryRepository:

    def insert(self, record: dict) -> None:
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO request_history
                   (request_id, endpoint, latency_ms, status, cache_hit, model_version, payload)
                   VALUES (:request_id, :endpoint, :latency_ms, :status, :cache_hit, :model_version, :payload)""",
                {
                    "request_id": record.get("request_id"),
                    "endpoint": record.get("endpoint"),
                    "latency_ms": record.get("latency_ms"),
                    "status": record.get("status"),
                    "cache_hit": record.get("cache_hit", False),
                    "model_version": record.get("model_version"),
                    "payload": json.dumps(record.get("payload")) if record.get("payload") else None,
                },
            )
            conn.commit()
        finally:
            conn.close()

    def query(self, endpoint: str | None = None, limit: int = 100) -> list[dict]:
        conn = get_connection()
        try:
            if endpoint:
                rows = conn.execute(
                    "SELECT * FROM request_history WHERE endpoint = ? ORDER BY timestamp DESC LIMIT ?",
                    (endpoint, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM request_history ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def count(self, endpoint: str | None = None) -> int:
        conn = get_connection()
        try:
            if endpoint:
                row = conn.execute(
                    "SELECT COUNT(*) as cnt FROM request_history WHERE endpoint = ?",
                    (endpoint,),
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) as cnt FROM request_history").fetchone()
            return row["cnt"]
        finally:
            conn.close()


class BatchJobRepository:

    def create(self, job_id: str, total_records: int) -> dict:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO batch_jobs (job_id, status, total_records) VALUES (?, ?, ?)",
                (job_id, "pending", total_records),
            )
            conn.commit()
            return self.get(job_id)  # type: ignore[return-value]
        finally:
            conn.close()

    def update_progress(self, job_id: str, processed: int, failed: int) -> None:
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE batch_jobs SET processed_records = ?, failed_records = ? WHERE job_id = ?",
                (processed, failed, job_id),
            )
            conn.commit()
        finally:
            conn.close()

    def update_status(self, job_id: str, status: str, results: str | None = None) -> None:
        conn = get_connection()
        try:
            completed_at = datetime.now(timezone.utc).isoformat() if status in ("completed", "failed") else None
            conn.execute(
                "UPDATE batch_jobs SET status = ?, results = ?, completed_at = ? WHERE job_id = ?",
                (status, results, completed_at, job_id),
            )
            conn.commit()
        finally:
            conn.close()

    def get(self, job_id: str) -> dict | None:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM batch_jobs WHERE job_id = ?", (job_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_all(self, limit: int = 20) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM batch_jobs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()


class CacheRepository:

    def get(self, key: str) -> str | None:
        conn = get_connection()
        try:
            row = conn.execute(
                """SELECT value, created_at, ttl_seconds FROM cache_entries
                   WHERE cache_key = ?""",
                (key,),
            ).fetchone()
            if not row:
                return None
            created = datetime.fromisoformat(row["created_at"])
            if row["ttl_seconds"] is not None:
                elapsed = (datetime.now(timezone.utc) - created.replace(tzinfo=timezone.utc)).total_seconds()
                if elapsed > row["ttl_seconds"]:
                    self.invalidate(key)
                    return None
            return row["value"]
        finally:
            conn.close()

    def set(self, key: str, value: str, ttl: int) -> None:
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO cache_entries (cache_key, value, ttl_seconds)
                   VALUES (?, ?, ?)
                   ON CONFLICT(cache_key)
                   DO UPDATE SET value = excluded.value,
                                 ttl_seconds = excluded.ttl_seconds,
                                 created_at = CURRENT_TIMESTAMP""",
                (key, value, ttl),
            )
            conn.commit()
        finally:
            conn.close()

    def invalidate(self, key: str) -> None:
        conn = get_connection()
        try:
            conn.execute("DELETE FROM cache_entries WHERE cache_key = ?", (key,))
            conn.commit()
        finally:
            conn.close()

    def clear_expired(self) -> int:
        conn = get_connection()
        try:
            result = conn.execute(
                """DELETE FROM cache_entries
                   WHERE ttl_seconds IS NOT NULL
                   AND (julianday('now') - julianday(created_at)) * 86400 > ttl_seconds"""
            )
            conn.commit()
            return result.rowcount
        finally:
            conn.close()
