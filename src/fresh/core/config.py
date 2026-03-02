"""Configuration dataclasses for fresh CLI commands.

These dataclasses define the input/output structure for each command,
making it easy to test business logic independently of CLI layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SyncConfig:
    """Configuration for sync command."""

    url: str
    output_dir: Path | None = None
    max_pages: int = 100
    depth: int = 3
    workers: int = 1
    force: bool = False
    incremental: bool = True
    pattern: str | None = None
    verbose: bool = False


@dataclass
class SyncResult:
    """Result of sync operation."""

    url: str
    success_count: int = 0
    failed_count: int = 0
    skipped_robots: int = 0
    skipped_binary: int = 0
    skipped_unchanged: int = 0
    total_pages: int = 0


@dataclass
class SearchConfig:
    """Configuration for search command."""

    query: str
    url: str
    max_pages: int = 50
    depth: int = 3
    case_sensitive: bool = False
    regex: bool = False
    context_lines: int = 1
    verbose: bool = False
    result_limit: int | None = None
    source: str = "auto"  # "auto", "local", "remote"
    parallel: bool | None = None
    fuzzy: bool = False


@dataclass
class SearchResultItem:
    """Single search result item."""

    path: str
    title: str
    snippet: str
    url: str
    source: str = "local"  # "local" or "remote"


@dataclass
class SearchResult:
    """Result of search operation."""

    query: str
    url: str
    items: list[SearchResultItem] = field(default_factory=list)
    total_count: int = 0


@dataclass
class GetConfig:
    """Configuration for get command."""

    url: str
    timeout: int = 30
    header: str | None = None
    no_follow: bool = False
    skip_scripts: bool = False
    no_cache: bool = False
    cache_ttl: int | None = None
    retry: int = 3
    dry_run: bool = False
    local: bool = False
    remote: bool = False


@dataclass
class GetResult:
    """Result of get operation."""

    url: str
    resolved_url: str
    content: str | None = None
    success: bool = False
    error: str | None = None


@dataclass
class ListConfig:
    """Configuration for list command."""

    url: str
    max_pages: int = 100
    pattern: str | None = None
    verbose: bool = False
    sort: str = "path"


@dataclass
class ListResult:
    """Result of list operation."""

    url: str
    urls: list[str] = field(default_factory=list)
    count: int = 0


@dataclass
class IndexConfig:
    """Configuration for index build command."""

    site: str
    pages_dir: Path | None = None
    force: bool = False


@dataclass
class IndexResult:
    """Result of index build operation."""

    site: str
    page_count: int = 0
    success: bool = False
