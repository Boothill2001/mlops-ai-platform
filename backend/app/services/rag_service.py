from __future__ import annotations

import threading

from app.core.config import settings
from app.core.tracing import new_trace
from app.services.permission_service import ROLE_HIERARCHY, get_accessible_doc_count
from app.services.rerank_service import get_rerank_service
from app.services.retrieval_service import get_retrieval_service
from app.storage.vector_store import get_vector_store


class RagService:
    async def query(
        self,
        user_id: str,
        role: str,
        query_text: str,
        top_k: int = 5,
    ) -> dict:
        if role not in ROLE_HIERARCHY:
            return {
                "answer": "Access denied: invalid role.",
                "citations": [],
                "grounded": False,
                "latency_ms": 0.0,
                "cache_hit": False,
                "permission_filtered_count": 0,
                "chunks_retrieved": 0,
                "request_id": "",
            }

        trace = new_trace()

        # Check cache if available
        cache_result = None
        cache_service = _get_cache_service_safe()
        if cache_service:
            cache_result = cache_service.get(
                namespace="rag", role=role, query=query_text
            )

        if cache_result is not None:
            cache_result["cache_hit"] = True
            cache_result["request_id"] = trace.request_id
            cache_result["latency_ms"] = trace.elapsed_ms
            return cache_result

        retrieval_service = get_retrieval_service()
        results = retrieval_service.retrieve(
            query=query_text,
            user_id=user_id,
            user_role=role,
            top_k=top_k * 2,
        )

        store = get_vector_store()
        total_docs = len(store.documents)
        accessible = get_accessible_doc_count(role, store.documents)
        permission_filtered_count = total_docs - accessible

        if not results:
            response = {
                "answer": "No relevant documents found for your query.",
                "citations": [],
                "grounded": False,
                "latency_ms": trace.elapsed_ms,
                "cache_hit": False,
                "permission_filtered_count": permission_filtered_count,
                "chunks_retrieved": 0,
                "request_id": trace.request_id,
            }
            return response

        rerank_service = get_rerank_service()
        reranked = rerank_service.rerank(query_text, results, top_k=top_k)

        answer = self._generate_answer(query_text, reranked)

        citations = [
            {
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
                "chunk_text": chunk["chunk_text"],
                "relevance_score": round(chunk["score"], 4),
            }
            for chunk in reranked
        ]

        response = {
            "answer": answer,
            "citations": citations,
            "grounded": True,
            "latency_ms": trace.elapsed_ms,
            "cache_hit": False,
            "permission_filtered_count": permission_filtered_count,
            "chunks_retrieved": len(reranked),
            "request_id": trace.request_id,
        }

        if cache_service:
            cache_service.set(
                "rag", response.copy(), role=role, query=query_text
            )

        history_service = _get_history_service_safe()
        if history_service:
            history_service.log_request(
                request_id=trace.request_id,
                endpoint="rag_query",
                latency_ms=trace.elapsed_ms,
                status="ok",
                cache_hit=False,
                model_version="mock",
                payload={"query": query_text, "role": role, "chunks": len(reranked)},
            )

        return response

    def _generate_answer(self, query: str, chunks: list[dict]) -> str:
        if settings.llm_provider != "mock":
            return f"[LLM integration pending] Query: {query}"

        lines = [
            f"Based on the available documentation, here is what I found regarding '{query}':\n"
        ]
        for i, chunk in enumerate(chunks[:3], 1):
            text = chunk["chunk_text"]
            sentences = text.split(". ")
            key_sentence = sentences[0] + "." if sentences else text[:120]
            lines.append(f"- {key_sentence} [Source: {chunk['title']}]")

        lines.append(
            f"\nThis answer is based on {len(chunks)} relevant document(s)."
        )
        return "\n".join(lines)


def _get_cache_service_safe():
    try:
        from app.services.cache_service import get_cache_service
        return get_cache_service()
    except (ImportError, Exception):
        return None


def _get_history_service_safe():
    try:
        from app.services.history_service import get_history_service
        return get_history_service()
    except (ImportError, Exception):
        return None


_instance: RagService | None = None
_instance_lock = threading.Lock()


def get_rag_service() -> RagService:
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = RagService()
    return _instance
