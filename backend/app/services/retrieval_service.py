from __future__ import annotations

import threading

from app.services.embedding_service import get_embedding_service
from app.services.permission_service import get_permission_filter
from app.storage.vector_store import get_vector_store


class RetrievalService:
    def retrieve(
        self,
        query: str,
        user_id: str,
        user_role: str,
        top_k: int = 5,
    ) -> list[dict]:
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.embed(query)

        permission_filter = get_permission_filter(user_id, user_role)
        store = get_vector_store()

        return store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_fn=permission_filter,
        )


_instance: RetrievalService | None = None
_instance_lock = threading.Lock()


def get_retrieval_service() -> RetrievalService:
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = RetrievalService()
    return _instance
