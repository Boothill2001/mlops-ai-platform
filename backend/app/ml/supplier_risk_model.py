from __future__ import annotations

import pickle
from abc import ABC, abstractmethod
from pathlib import Path


class BaseRiskModel(ABC):
    @abstractmethod
    def predict(self, features: dict) -> dict: ...

    @abstractmethod
    def explain(self, features: dict) -> list[dict]: ...


_WEIGHTS: dict[str, float] = {
    "defect_rate_norm": 0.30,
    "late_delivery_norm": 0.25,
    "country_risk": 0.20,
    "lead_time_norm": 0.15,
    "order_value_norm": 0.10,
}

_THRESHOLDS: list[tuple[float, str]] = [
    (0.85, "critical"),
    (0.70, "high"),
    (0.40, "medium"),
]


def _classify(score: float) -> str:
    for threshold, level in _THRESHOLDS:
        if score >= threshold:
            return level
    return "low"


class RuleBasedModel(BaseRiskModel):
    """Weighted linear scoring model for supplier risk."""

    def predict(self, features: dict) -> dict:
        risk_score = sum(
            features.get(factor, 0.0) * weight
            for factor, weight in _WEIGHTS.items()
        )
        risk_score = round(min(max(risk_score, 0.0), 1.0), 6)
        return {
            "risk_score": risk_score,
            "risk_level": _classify(risk_score),
        }

    def explain(self, features: dict) -> list[dict]:
        contributions: list[dict] = []
        for factor, weight in _WEIGHTS.items():
            value = features.get(factor, 0.0)
            impact = round(value * weight, 6)
            contributions.append({
                "factor": factor,
                "value": round(value, 6),
                "impact": impact,
                "direction": "increases_risk" if value > 0.5 else "decreases_risk",
            })
        contributions.sort(key=lambda c: c["impact"], reverse=True)
        return contributions


class TrainedModel(BaseRiskModel):
    """Sklearn RandomForestClassifier wrapper with rule-based fallback."""

    def __init__(self, model_path: str | Path | None = None) -> None:
        self._sklearn_model = None
        self._fallback = RuleBasedModel()
        if model_path and Path(model_path).exists():
            with open(model_path, "rb") as f:
                self._sklearn_model = pickle.load(f)  # noqa: S301

    @property
    def is_using_fallback(self) -> bool:
        return self._sklearn_model is None

    def _features_to_vector(self, features: dict) -> list[float]:
        ordered_keys = sorted(
            k for k in features if k != "supplier_id"
        )
        return [features[k] for k in ordered_keys]

    def predict(self, features: dict) -> dict:
        if self._sklearn_model is None:
            return self._fallback.predict(features)
        vec = self._features_to_vector(features)
        proba = self._sklearn_model.predict_proba([vec])[0]
        risk_score = float(proba.max())
        return {
            "risk_score": round(risk_score, 6),
            "risk_level": _classify(risk_score),
        }

    def explain(self, features: dict) -> list[dict]:
        if self._sklearn_model is None:
            return self._fallback.explain(features)
        importances = self._sklearn_model.feature_importances_
        ordered_keys = sorted(
            k for k in features if k != "supplier_id"
        )
        contributions = []
        for key, importance in zip(ordered_keys, importances):
            value = features[key]
            contributions.append({
                "factor": key,
                "value": round(value, 6),
                "impact": round(float(importance), 6),
                "direction": "increases_risk" if value > 0.5 else "decreases_risk",
            })
        contributions.sort(key=lambda c: c["impact"], reverse=True)
        return contributions
