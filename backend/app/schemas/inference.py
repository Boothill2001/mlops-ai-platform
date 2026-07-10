from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal


class SupplierRiskRequest(BaseModel):
    supplier_id: str
    lead_time_days: int = Field(ge=0)
    defect_rate: float = Field(ge=0.0, le=1.0)
    late_delivery_count: int = Field(ge=0)
    order_value: float = Field(ge=0.0)
    country: str = Field(min_length=2, max_length=2)


class ExplanationFactor(BaseModel):
    factor: str
    value: float
    impact: float
    direction: Literal["increases_risk", "decreases_risk"]


class SupplierRiskResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    request_id: str
    supplier_id: str
    risk_score: float
    risk_level: str
    model_version: str
    latency_ms: float
    cache_hit: bool
    explanation: list[ExplanationFactor]
