from __future__ import annotations

from app.core.tracing import new_trace
from app.ml.feature_builder import build_features
from app.ml.model_registry import ModelRegistry
from app.schemas.inference import ExplanationFactor, SupplierRiskRequest, SupplierRiskResponse
from app.services.cache_service import CacheService, get_cache_service
from app.services.history_service import HistoryService, get_history_service

_CACHE_NS = "inference"
_ENDPOINT = "/api/v1/inference/supplier-risk"


class InferenceService:
    def __init__(
        self,
        cache_service: CacheService,
        history_service: HistoryService,
        model_registry: ModelRegistry,
    ) -> None:
        self._cache = cache_service
        self._history = history_service
        self._registry = model_registry

    async def predict(self, request: SupplierRiskRequest) -> SupplierRiskResponse:
        trace = new_trace()
        cache_params = request.model_dump()

        cached = self._cache.get(_CACHE_NS, **cache_params)
        if cached is not None:
            return SupplierRiskResponse(
                **cached,
                request_id=trace.request_id,
                latency_ms=trace.elapsed_ms,
                cache_hit=True,
            )

        features = build_features(request.model_dump())

        model_version = self._registry.get_production()
        if model_version is None:
            raise RuntimeError("No production model registered")

        prediction = model_version.model_instance.predict(features)
        explanation_raw = model_version.model_instance.explain(features)

        explanation = [ExplanationFactor(**f) for f in explanation_raw]

        response = SupplierRiskResponse(
            request_id=trace.request_id,
            supplier_id=request.supplier_id,
            risk_score=prediction["risk_score"],
            risk_level=prediction["risk_level"],
            model_version=model_version.version,
            latency_ms=trace.elapsed_ms,
            cache_hit=False,
            explanation=explanation,
        )

        self._cache.set(
            _CACHE_NS,
            {
                "supplier_id": response.supplier_id,
                "risk_score": response.risk_score,
                "risk_level": response.risk_level,
                "model_version": response.model_version,
                "explanation": [e.model_dump() for e in response.explanation],
            },
            **cache_params,
        )

        self._history.log_request(
            request_id=trace.request_id,
            endpoint=_ENDPOINT,
            latency_ms=response.latency_ms,
            status="ok",
            cache_hit=False,
            model_version=response.model_version,
            payload=request.model_dump(),
        )

        return response


_instance: InferenceService | None = None


def get_inference_service() -> InferenceService:
    global _instance
    if _instance is None:
        _instance = InferenceService(
            cache_service=get_cache_service(),
            history_service=get_history_service(),
            model_registry=ModelRegistry(),
        )
    return _instance
