from __future__ import annotations

import math

from app.services.history_service import get_history_service
from app.core.config import settings


class DriftService:
    BASELINE_DISTRIBUTION: dict[str, float] = {
        "risk_assessment": 0.40,
        "compliance": 0.25,
        "pricing": 0.15,
        "quality": 0.12,
        "general": 0.08,
    }

    COMPLIANCE_KEYWORDS = {"compliance", "audit", "regulation", "policy", "standard"}
    PRICING_KEYWORDS = {"price", "cost", "pricing", "budget", "expense"}
    QUALITY_KEYWORDS = {"quality", "defect", "inspection", "damage", "grade"}

    def __init__(self) -> None:
        self._history = get_history_service()

    def _classify_intent(self, query_or_endpoint: str) -> str:
        text = query_or_endpoint.lower()

        if "/inference" in text or "risk" in text:
            return "risk_assessment"

        if "/rag" in text:
            if any(kw in text for kw in self.COMPLIANCE_KEYWORDS):
                return "compliance"
            if any(kw in text for kw in self.PRICING_KEYWORDS):
                return "pricing"
            if any(kw in text for kw in self.QUALITY_KEYWORDS):
                return "quality"

        return "general"

    @staticmethod
    def _kld(p: dict[str, float], q: dict[str, float], eps: float = 1e-10) -> float:
        return sum(p[k] * math.log((p[k] + eps) / (q[k] + eps)) for k in p)

    def _compute_jsd(self, p: dict[str, float], q: dict[str, float]) -> float:
        all_keys = set(p) | set(q)
        p_full = {k: p.get(k, 0.0) for k in all_keys}
        q_full = {k: q.get(k, 0.0) for k in all_keys}
        m = {k: 0.5 * (p_full[k] + q_full[k]) for k in all_keys}
        return 0.5 * self._kld(p_full, m) + 0.5 * self._kld(q_full, m)

    def get_drift_score(self) -> dict:
        rows = self._history.get_history(limit=1000)
        if not rows:
            return {
                "drift_score": 0.0,
                "drift_status": "ok",
                "baseline_distribution": self.BASELINE_DISTRIBUTION,
                "current_distribution": {k: 0.0 for k in self.BASELINE_DISTRIBUTION},
                "sample_size": 0,
            }

        counts: dict[str, int] = {k: 0 for k in self.BASELINE_DISTRIBUTION}
        for row in rows:
            endpoint = row.get("endpoint", "")
            payload = row.get("payload") or {}
            query = payload.get("query", "") if isinstance(payload, dict) else ""
            intent = self._classify_intent(f"{endpoint} {query}")
            counts[intent] = counts.get(intent, 0) + 1

        total = len(rows)
        current = {k: v / total for k, v in counts.items()}

        jsd = self._compute_jsd(self.BASELINE_DISTRIBUTION, current)
        drift_score = round(jsd, 6)

        if drift_score >= settings.drift_alert:
            status = "alert"
        elif drift_score >= settings.drift_warning:
            status = "warning"
        else:
            status = "ok"

        return {
            "drift_score": drift_score,
            "drift_status": status,
            "baseline_distribution": self.BASELINE_DISTRIBUTION,
            "current_distribution": {k: round(v, 4) for k, v in current.items()},
            "sample_size": total,
        }


_instance: DriftService | None = None


def get_drift_service() -> DriftService:
    global _instance
    if _instance is None:
        _instance = DriftService()
    return _instance
