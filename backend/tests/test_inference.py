import pytest
from fastapi.testclient import TestClient
from app.main import app
import app.services.cache_service as cache_mod
import app.services.inference_service as inference_mod
from app.storage.repositories import CacheRepository


VALID_PAYLOAD = {
    "supplier_id": "SUP-VN-001",
    "lead_time_days": 14,
    "defect_rate": 0.03,
    "late_delivery_count": 2,
    "order_value": 120000,
    "country": "VN",
}


def _clear_all_cache() -> None:
    from app.storage.database import get_connection
    conn = get_connection()
    try:
        conn.execute("DELETE FROM cache_entries")
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(autouse=True)
def _reset_singletons():
    cache_mod._instance = None
    inference_mod._instance = None
    _clear_all_cache()
    yield
    cache_mod._instance = None
    inference_mod._instance = None


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_inference_valid_response(client: TestClient) -> None:
    resp = client.post("/api/v1/inference/supplier-risk", json=VALID_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert data["supplier_id"] == "SUP-VN-001"
    assert "risk_score" in data
    assert "risk_level" in data
    assert "model_version" in data
    assert "latency_ms" in data
    assert "request_id" in data
    assert isinstance(data["cache_hit"], bool)
    assert isinstance(data["explanation"], list)


def test_inference_cache_hit(client: TestClient) -> None:
    resp1 = client.post("/api/v1/inference/supplier-risk", json=VALID_PAYLOAD)
    assert resp1.status_code == 200
    assert resp1.json()["cache_hit"] is False

    resp2 = client.post("/api/v1/inference/supplier-risk", json=VALID_PAYLOAD)
    assert resp2.status_code == 200
    assert resp2.json()["cache_hit"] is True


def test_inference_explanation_present(client: TestClient) -> None:
    resp = client.post("/api/v1/inference/supplier-risk", json=VALID_PAYLOAD)
    assert resp.status_code == 200
    explanation = resp.json()["explanation"]
    assert len(explanation) > 0
    factor = explanation[0]
    assert "factor" in factor
    assert "value" in factor
    assert "impact" in factor
    assert factor["direction"] in ("increases_risk", "decreases_risk")


def test_list_suppliers(client: TestClient) -> None:
    resp = client.get("/api/v1/inference/suppliers")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "supplier_id" in data[0]
    assert "country" in data[0]
