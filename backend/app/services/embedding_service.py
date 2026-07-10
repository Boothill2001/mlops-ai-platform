from __future__ import annotations

import threading
from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

from app.core.config import settings
from app.storage.vector_store import get_vector_store


class EmbeddingBackend(Protocol):
    def embed(self, text: str) -> np.ndarray: ...
    def embed_batch(self, texts: list[str]) -> np.ndarray: ...


class MockEmbedding:
    def __init__(self) -> None:
        self._vectorizer = HashingVectorizer(n_features=256, norm="l2", alternate_sign=False)

    def embed(self, text: str) -> np.ndarray:
        vec = self._vectorizer.transform([text]).toarray()[0]
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        vecs = self._vectorizer.transform(texts).toarray()
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        return vecs / norms


class SentenceTransformerEmbedding:
    def __init__(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for SentenceTransformerEmbedding. "
                "Install with: pip install sentence-transformers"
            ) from exc

    def embed(self, text: str) -> np.ndarray:
        return self._model.encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        return self._model.encode(texts, normalize_embeddings=True)


class EmbeddingService:
    def __init__(self) -> None:
        if settings.embedding_provider == "sentence-transformers":
            self._backend: EmbeddingBackend = SentenceTransformerEmbedding()
        else:
            self._backend = MockEmbedding()
        self._init_lock = threading.Lock()
        self._initialized = False

    def _ensure_store_embeddings(self) -> None:
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return
            store = get_vector_store()
            if store.documents and store.embeddings is None:
                texts = [doc["chunk_text"] for doc in store.documents]
                embeddings = self.embed_batch(texts)
                store.embeddings = embeddings
            self._initialized = True

    def embed(self, text: str) -> np.ndarray:
        self._ensure_store_embeddings()
        return self._backend.embed(text)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        return self._backend.embed_batch(texts)


_instance: EmbeddingService | None = None
_instance_lock = threading.Lock()


def get_embedding_service() -> EmbeddingService:
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = EmbeddingService()
    return _instance
