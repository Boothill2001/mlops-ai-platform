import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_response_schema():
    resp = client.get("/api/v1/monitoring/metrics")
    assert resp.status_code == 200
    data = resp.json()
    expected_fields = [
        "latency_p50", "latency_p95", "latency_p99",
        "requests_per_minute", "error_rate", "cache_hit_rate",
        "estimated_cost", "rag_citation_rate", "total_requests",
        "drift", "per_endpoint",
    ]
    for field in expected_fields:
        assert field in data, f"Missing field: {field}"
    assert "drift_score" in data["drift"]
    assert "drift_status" in data["drift"]


def test_metrics_empty_history():
    resp = client.get("/api/v1/monitoring/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["total_requests"], int)
    assert isinstance(data["error_rate"], (int, float))
    assert isinstance(data["per_endpoint"], list)


def test_drift_default_ok():
    resp = client.get("/api/v1/monitoring/drift")
    assert resp.status_code == 200
    data = resp.json()
    assert "drift_score" in data
    assert "drift_status" in data
    assert data["drift_status"] in ("ok", "warning", "alert")
    assert isinstance(data["drift_score"], (int, float))


def test_history_endpoint():
    resp = client.get("/api/v1/monitoring/history")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
