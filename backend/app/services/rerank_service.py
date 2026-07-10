from __future__ import annotations

import threading


class RerankService:
    def rerank(self, query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
        query_words = set(query.lower().split())
        scored: list[dict] = []

        for chunk in chunks:
            chunk_words = set(chunk["chunk_text"].lower().split())
            keyword_score = (
                len(query_words & chunk_words) / len(query_words)
                if query_words
                else 0.0
            )
            original_score = chunk.get("score", 0.0)
            combined_score = 0.6 * original_score + 0.4 * keyword_score

            scored.append({**chunk, "score": combined_score})

        scored.sort(key=lambda c: c["score"], reverse=True)
        return scored[:top_k]


_instance: RerankService | None = None
_instance_lock = threading.Lock()


def get_rerank_service() -> RerankService:
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = RerankService()
    return _instance
