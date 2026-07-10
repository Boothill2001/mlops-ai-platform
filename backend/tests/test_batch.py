import time

from fastapi.testclient import TestClient

from app.main import app
from app.storage.seed_data import SAMPLE_CSV_DATA

client = TestClient(app)

SMALL_CSV = """supplier_id,name,country,lead_time_days,defect_rate,late_delivery_count,order_value
SUP-TEST-001,Test Supplier A,VN,14,0.03,2,120000
SUP-TEST-002,Test Supplier B,CN,21,0.05,5,350000
SUP-TEST-003,Test Supplier C,US,10,0.02,1,450000
"""


def test_batch_run_returns_job_id():
    response = client.post(
        "/api/v1/batch/run",
        json={"data_csv": SMALL_CSV, "chunk_size": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "message" in data


def test_batch_job_status():
    response = client.post(
        "/api/v1/batch/run",
        json={"data_csv": SMALL_CSV, "chunk_size": 10},
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    for _ in range(10):
        time.sleep(0.5)
        status_resp = client.get(f"/api/v1/batch/jobs/{job_id}")
        assert status_resp.status_code == 200
        job = status_resp.json()
        if job["status"] == "completed":
            break

    assert job["status"] == "completed"
    assert job["total_records"] == 3
    assert job["processed_records"] == 3
    assert job["progress_pct"] == 100.0
    assert len(job["results"]) == 3
    assert job["results"][0]["supplier_id"] == "SUP-TEST-001"
    assert "risk_score" in job["results"][0]
    assert "risk_level" in job["results"][0]


def test_batch_job_list():
    response = client.post(
        "/api/v1/batch/run",
        json={"data_csv": SMALL_CSV},
    )
    assert response.status_code == 200

    time.sleep(1)

    list_resp = client.get("/api/v1/batch/jobs")
    assert list_resp.status_code == 200
    jobs = list_resp.json()
    assert len(jobs) >= 1
    assert "job_id" in jobs[0]
    assert "status" in jobs[0]
    assert "progress_pct" in jobs[0]


def test_batch_sample_run():
    response = client.post("/api/v1/batch/run-sample")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"


def test_batch_job_not_found():
    response = client.get("/api/v1/batch/jobs/nonexistent_id_12345")
    assert response.status_code == 404
