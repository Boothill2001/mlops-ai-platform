from pydantic import BaseModel


class EndpointMetrics(BaseModel):
    endpoint: str
    count: int
    avg_latency: float
    error_rate: float


class DriftInfo(BaseModel):
    drift_score: float
    drift_status: str
    baseline_distribution: dict[str, float]
    current_distribution: dict[str, float]
    sample_size: int


class MetricsResponse(BaseModel):
    latency_p50: float
    latency_p95: float
    latency_p99: float
    requests_per_minute: float
    error_rate: float
    cache_hit_rate: float
    estimated_cost: float
    rag_citation_rate: float
    total_requests: int
    drift: DriftInfo
    per_endpoint: list[EndpointMetrics]
