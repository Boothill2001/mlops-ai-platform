from __future__ import annotations

import hashlib
import json
from collections import OrderedDict

from app.core.config import settings
from app.storage.repositories import CacheRepository


class CacheService:
    def __init__(self, max_size: int | None = None, ttl: int | None = None) -> None:
        self._max_size = max_size or settings.cache_max_size
        self._ttl = ttl or settings.cache_ttl_seconds
        self._memory: OrderedDict[str, dict] = OrderedDict()
        self._repo = CacheRepository()

    @staticmethod
    def _make_key(namespace: str, **params: object) -> str:
        raw = json.dumps({"ns": namespace, **dict(sorted(params.items()))}, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, namespace: str, **params: object) -> dict | None:
        key = self._make_key(namespace, **params)

        if key in self._memory:
            self._memory.move_to_end(key)
            return self._memory[key]

        raw = self._repo.get(key)
        if raw is not None:
            value = json.loads(raw)
            self._memory[key] = value
            self._memory.move_to_end(key)
            self._evict()
            return value

        return None

    def set(self, namespace: str, value: dict, **params: object) -> None:
        key = self._make_key(namespace, **params)
        self._memory[key] = value
        self._memory.move_to_end(key)
        self._evict()
        self._repo.set(key, json.dumps(value, default=str), self._ttl)

    def invalidate(self, namespace: str, **params: object) -> None:
        key = self._make_key(namespace, **params)
        self._memory.pop(key, None)
        self._repo.invalidate(key)

    def _evict(self) -> None:
        while len(self._memory) > self._max_size:
            self._memory.popitem(last=False)


_instance: CacheService | None = None


def get_cache_service() -> CacheService:
    global _instance
    if _instance is None:
        _instance = CacheService()
    return _instance
