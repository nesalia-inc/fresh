"""Core module - pure business logic, testable without I/O."""

from __future__ import annotations

from .config import (
    GetConfig,
    GetResult,
    IndexConfig,
    IndexResult,
    ListConfig,
    ListResult,
    ListSort,
    SearchConfig,
    SearchResult,
    SearchResultItem,
    SearchSource,
    SyncConfig,
    SyncResult,
    ResultSource,
)
from .get import (
    get_cache_dir,
    get_cached_content,
    get_local_content,
    get_sync_dir,
    html_to_markdown,
    local_content_exists,
    save_to_cache,
    url_to_sync_path,
)
from .list import (
    discover_pages,
    filter_by_pattern,
    sort_entries,
    format_as_json,
    format_as_yaml,
    format_as_xml,
    create_entry,
)
from .sync import Sync

__all__ = [
    "GetConfig",
    "GetResult",
    "create_entry",
    "discover_pages",
    "filter_by_pattern",
    "format_as_json",
    "format_as_yaml",
    "format_as_xml",
    "get_cache_dir",
    "get_cached_content",
    "get_local_content",
    "get_sync_dir",
    "html_to_markdown",
    "IndexConfig",
    "IndexResult",
    "ListConfig",
    "ListResult",
    "ListSort",
    "local_content_exists",
    "save_to_cache",
    "SearchConfig",
    "SearchResult",
    "SearchResultItem",
    "SearchSource",
    "sort_entries",
    "Sync",
    "SyncConfig",
    "SyncResult",
    "ResultSource",
    "url_to_sync_path",
]
