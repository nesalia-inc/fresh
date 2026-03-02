"""Core module - pure business logic, testable without I/O."""

from __future__ import annotations

from .config import (
    GetConfig,
    GetResult,
    IndexConfig,
    IndexResult,
    ListConfig,
    ListResult,
    SearchConfig,
    SearchResult,
    SearchResultItem,
    SyncConfig,
    SyncResult,
)

__all__ = [
    "GetConfig",
    "GetResult",
    "IndexConfig",
    "IndexResult",
    "ListConfig",
    "ListResult",
    "SearchConfig",
    "SearchResult",
    "SearchResultItem",
    "SyncConfig",
    "SyncResult",
]
