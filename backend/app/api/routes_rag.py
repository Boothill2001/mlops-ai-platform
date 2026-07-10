from __future__ import annotations

from fastapi import APIRouter

from app.schemas.rag import RagQueryRequest, RagQueryResponse
from app.services.rag_service import get_rag_service
from app.storage.vector_store import get_vector_store

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


@router.post("/query", response_model=RagQueryResponse)
async def rag_query(request: RagQueryRequest) -> RagQueryResponse:
    service = get_rag_service()
    result = await service.query(
        user_id=request.user_id,
        role=request.role,
        query_text=request.query,
        top_k=request.top_k,
    )
    return RagQueryResponse(**result)


@router.get("/documents")
async def list_documents() -> list[dict]:
    store = get_vector_store()
    seen: set[str] = set()
    docs: list[dict] = []
    for doc in store.documents:
        if doc["doc_id"] not in seen:
            seen.add(doc["doc_id"])
            docs.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "metadata": doc.get("metadata", {}),
            })
    return docs
