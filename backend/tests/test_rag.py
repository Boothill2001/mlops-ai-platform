from __future__ import annotations

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.core.config import settings


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset vector store and embedding singletons, and clear the seed flag
    so each test session gets a fresh in-memory store with seeded data."""
    import app.storage.vector_store as vs_mod
    import app.services.embedding_service as emb_mod
    import app.services.retrieval_service as ret_mod
    import app.services.rerank_service as rer_mod
    import app.services.rag_service as rag_mod

    vs_mod._instance = None
    emb_mod._instance = None
    ret_mod._instance = None
    rer_mod._instance = None
    rag_mod._instance = None

    flag = Path(settings.data_dir) / ".seeded"
    existed = flag.exists()
    if existed:
        flag.unlink()
    yield
    # Restore flag if it existed before
    if existed and not flag.exists():
        flag.write_text("seeded")


@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


def _query(client: TestClient, role: str, query: str, top_k: int = 5) -> dict:
    resp = client.post(
        "/api/v1/rag/query",
        json={"user_id": "test-user", "role": role, "query": query, "top_k": top_k},
    )
    assert resp.status_code == 200
    return resp.json()


def test_rag_query_analyst_access(client: TestClient) -> None:
    data = _query(client, "analyst", "What is the supplier defect rate?")
    assert data["answer"]
    assert data["grounded"] is True
    assert len(data["citations"]) > 0
    assert data["request_id"]


def test_rag_query_viewer_limited(client: TestClient) -> None:
    viewer = _query(client, "viewer", "supplier contract negotiations")
    admin = _query(client, "admin", "supplier contract negotiations")
    viewer_doc_ids = {c["doc_id"] for c in viewer["citations"]}
    admin_doc_ids = {c["doc_id"] for c in admin["citations"]}
    # DOC-005 is admin-only; viewer must not see it
    assert "DOC-005" not in viewer_doc_ids
    # Admin should have access to all docs
    assert viewer["permission_filtered_count"] >= admin["permission_filtered_count"]


def test_rag_query_admin_full_access(client: TestClient) -> None:
    data = _query(client, "admin", "supplier risk assessment")
    assert data["grounded"] is True
    assert data["permission_filtered_count"] == 0
    assert len(data["citations"]) > 0


def test_rag_query_invalid_role(client: TestClient) -> None:
    data = _query(client, "superuser", "anything")
    assert "Access denied" in data["answer"]
    assert data["grounded"] is False
    assert data["citations"] == []


def test_rag_citations_present(client: TestClient) -> None:
    data = _query(client, "manager", "What is the on-time delivery rate?")
    assert len(data["citations"]) > 0
    citation = data["citations"][0]
    assert "doc_id" in citation
    assert "title" in citation
    assert "chunk_text" in citation
    assert "relevance_score" in citation


def test_rag_documents_list(client: TestClient) -> None:
    resp = client.get("/api/v1/rag/documents")
    assert resp.status_code == 200
    docs = resp.json()
    assert isinstance(docs, list)
    assert len(docs) > 0
    assert "doc_id" in docs[0]
    assert "title" in docs[0]
    assert "metadata" in docs[0]
