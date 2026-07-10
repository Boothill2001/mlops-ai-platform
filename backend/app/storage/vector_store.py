from __future__ import annotations

import threading
from typing import Callable

import numpy as np


class VectorStore:
    def __init__(self) -> None:
        self.documents: list[dict] = []
        self.embeddings: np.ndarray | None = None
        self._lock = threading.Lock()

    def add_documents(self, docs: list[dict], embeddings: np.ndarray | None = None) -> None:
        with self._lock:
            self.documents.extend(docs)
            if embeddings is not None:
                if self.embeddings is None:
                    self.embeddings = embeddings
                else:
                    self.embeddings = np.vstack([self.embeddings, embeddings])

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_fn: Callable[[dict], bool] | None = None,
    ) -> list[dict]:
        if not self.documents or self.embeddings is None:
            return []

        with self._lock:
            candidates: list[tuple[int, dict]] = []
            for i, doc in enumerate(self.documents):
                if filter_fn and not filter_fn(doc):
                    continue
                candidates.append((i, doc))

            if not candidates:
                return []

            indices = [idx for idx, _ in candidates]
            candidate_embeddings = self.embeddings[indices]

            query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
            doc_norms = candidate_embeddings / (
                np.linalg.norm(candidate_embeddings, axis=1, keepdims=True) + 1e-10
            )
            similarities = doc_norms @ query_norm

            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for rank_idx in top_indices:
                _, doc = candidates[rank_idx]
                results.append(
                    {
                        "doc_id": doc["doc_id"],
                        "title": doc["title"],
                        "chunk_text": doc["chunk_text"],
                        "score": float(similarities[rank_idx]),
                        "metadata": doc.get("metadata", {}),
                    }
                )
            return results

    def clear(self) -> None:
        with self._lock:
            self.documents = []
            self.embeddings = None


_instance: VectorStore | None = None
_instance_lock = threading.Lock()


def get_vector_store() -> VectorStore:
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = VectorStore()
    return _instance
