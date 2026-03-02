"""Configuration dataclasses for fresh CLI commands.

These dataclasses define the input/output structure for each command,
making it easy to test business logic independently of CLI layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


# Type aliases for limited choices
SearchSource = Literal["auto", "local", "remote"]
ResultSource = Literal["local", "remote"]
ListSort = Literal["path", "alpha", "random"]


@dataclass
class SyncConfig:
    """Configuration for sync command."""

    url: str
    output_dir: Optional[Path] = None
    max_pages: int = 100
    depth: int = 3
    workers: int = 1
    force: bool = False
    incremental: bool = True
    pattern: Optional[str] = None
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
    result_limit: Optional[int] = None
    source: SearchSource = "auto"
    parallel: Optional[bool] = None
    fuzzy: bool = False


@dataclass
class SearchResultItem:
    """Single search result item."""

    path: str
    title: str
    snippet: str
    url: str
    source: ResultSource = "local"


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
    header: Optional[str] = None
    no_follow: bool = False
    skip_scripts: bool = False
    no_cache: bool = False
    cache_ttl: Optional[int] = None
    retry: int = 3
    dry_run: bool = False
    local: bool = False
    remote: bool = False


@dataclass
class GetResult:
    """Result of get operation."""

    url: str
    resolved_url: str
    content: Optional[str] = None
    success: bool = False
    error: Optional[str] = None


@dataclass
class Webpage:
    """Represents a fetched webpage with its content and metadata."""

    url: str
    resolved_url: str
    content: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    dry_run: bool = False

    def is_success(self) -> bool:
        """Check if the fetch was successful."""
        return self.success and self.content is not None

    def is_error(self) -> bool:
        """Check if there was an error."""
        return not self.success or self.error is not None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "url": self.url,
            "resolved_url": self.resolved_url,
            "content": self.content,
            "success": self.success,
            "error": self.error,
            "dry_run": self.dry_run,
        }


@dataclass
class ListConfig:
    """Configuration for list command."""

    url: str
    max_pages: int = 100
    pattern: Optional[str] = None
    verbose: bool = False
    sort: ListSort = "path"


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
    pages_dir: Optional[Path] = None
    force: bool = False


@dataclass
class IndexResult:
    """Result of index build operation."""

    site: str
    page_count: int = 0
    success: bool = False
