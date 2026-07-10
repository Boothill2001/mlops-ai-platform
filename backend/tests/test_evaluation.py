import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_evaluation_run(client: TestClient):
    response = client.post(
        "/api/v1/evaluation/run",
        json={"top_k": 5, "role": "analyst"},
    )
    assert response.status_code == 200
    data = response.json()

    for field in [
        "recall_at_k",
        "precision_at_k",
        "faithfulness",
        "citation_accuracy",
    ]:
        assert field in data
        assert 0.0 <= data[field] <= 1.0

    assert "total_questions" in data
    assert "passed_questions" in data
    assert "regression_detected" in data
    assert data["total_questions"] > 0


def test_evaluation_failed_cases_is_list(client: TestClient):
    response = client.post(
        "/api/v1/evaluation/run",
        json={"top_k": 5, "role": "analyst"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["failed_cases"], list)


def test_golden_questions_endpoint(client: TestClient):
    response = client.get("/api/v1/evaluation/golden-questions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "question" in data[0]
    assert "expected_answer_keywords" in data[0]
    assert "expected_doc_ids" in data[0]


def test_evaluation_response_schema(client: TestClient):
    response = client.post(
        "/api/v1/evaluation/run",
        json={},
    )
    assert response.status_code == 200
    data = response.json()

    required_fields = [
        "recall_at_k",
        "precision_at_k",
        "faithfulness",
        "citation_accuracy",
        "total_questions",
        "passed_questions",
        "failed_cases",
        "regression_detected",
    ]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
