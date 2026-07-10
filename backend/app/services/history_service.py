from __future__ import annotations

from app.storage.repositories import HistoryRepository


class HistoryService:
    def __init__(self) -> None:
        self._repo = HistoryRepository()

    def log_request(
        self,
        request_id: str,
        endpoint: str,
        latency_ms: float,
        status: str,
        cache_hit: bool,
        model_version: str,
        payload: dict | None = None,
    ) -> None:
        self._repo.insert({
            "request_id": request_id,
            "endpoint": endpoint,
            "latency_ms": latency_ms,
            "status": status,
            "cache_hit": cache_hit,
            "model_version": model_version,
            "payload": payload,
        })

    def get_history(self, endpoint: str | None = None, limit: int = 100) -> list[dict]:
        return self._repo.query(endpoint=endpoint, limit=limit)

    def get_stats(self, endpoint: str | None = None) -> dict:
        rows = self._repo.query(endpoint=endpoint, limit=10_000)
        total = len(rows)
        if total == 0:
            return {"total_requests": 0, "avg_latency": 0.0, "cache_hit_rate": 0.0}

        avg_latency = sum(r.get("latency_ms", 0) for r in rows) / total
        cache_hits = sum(1 for r in rows if r.get("cache_hit"))
        return {
            "total_requests": total,
            "avg_latency": round(avg_latency, 2),
            "cache_hit_rate": round(cache_hits / total, 4),
        }


_instance: HistoryService | None = None


def get_history_service() -> HistoryService:
    global _instance
    if _instance is None:
        _instance = HistoryService()
    return _instance
