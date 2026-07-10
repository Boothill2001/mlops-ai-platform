from __future__ import annotations

from typing import Callable


ROLE_HIERARCHY: dict[str, int] = {
    "admin": 4,
    "manager": 3,
    "analyst": 2,
    "viewer": 1,
}

ROLE_ACCESS_LEVEL: dict[str, int] = ROLE_HIERARCHY


def can_access(user_role: str, doc_metadata: dict) -> bool:
    allowed_roles = doc_metadata.get("allowed_roles", [])
    if user_role in allowed_roles:
        return True
    user_level = ROLE_ACCESS_LEVEL.get(user_role, 0)
    min_required = min(
        (ROLE_ACCESS_LEVEL.get(r, 0) for r in allowed_roles),
        default=0,
    )
    return user_level >= min_required


def get_permission_filter(user_id: str, user_role: str) -> Callable[[dict], bool]:
    """Return a filter function for vector_store.search().

    SECURITY: This filter is applied PRE-RETRIEVAL so that unauthorized
    documents are excluded before similarity ranking. Never filter after
    ranking -- that leaks information about document existence via result
    count changes.
    """
    def _filter(doc: dict) -> bool:
        metadata = doc.get("metadata", {})
        return can_access(user_role, metadata)
    return _filter


def get_accessible_doc_count(user_role: str, documents: list[dict]) -> int:
    return sum(
        1 for doc in documents
        if can_access(user_role, doc.get("metadata", {}))
    )
