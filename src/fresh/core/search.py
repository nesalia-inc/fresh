"""Core entity for search operations.

This module contains the Search entity which encapsulates all search logic,
following an entity-oriented architecture pattern.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional
from urllib.parse import quote, urlparse

from .config import SearchConfig, SearchResult


# Default sync directory
DEFAULT_SYNC_DIR = Path.home() / ".fresh" / "docs"

# Parallel search settings
PARALLEL_THRESHOLD = 10
DEFAULT_MAX_WORKERS = 4


class Search:
    """Entity representing a search operation.

    This class encapsulates all the business logic for searching
    documentation pages.
    """

    def __init__(self, config: SearchConfig) -> None:
        """Initialize Search entity.

        Args:
            config: The search configuration
        """
        self.config = config
        self._result = SearchResult(query=config.query, url=config.url)

    @property
    def result(self) -> SearchResult:
        """Get the search result."""
        return self._result

    @staticmethod
    def get_sync_dir() -> Path:
        """Get the default sync directory."""
        return DEFAULT_SYNC_DIR

    def _get_sync_dir_for_url(self, url: str) -> Path:
        """Get the sync directory for a URL's domain."""
        parsed = urlparse(url)
        domain = parsed.netloc.replace(":", "_").replace(".", "_")
        return DEFAULT_SYNC_DIR / domain / "pages"

    def _format_freshness_age(self, timestamp: str) -> str:
        """Format a timestamp as relative age."""
        from datetime import datetime, timezone

        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            delta = now - dt

            if delta.total_seconds() < 60:
                return "just now"
            elif delta.total_seconds() < 3600:
                minutes = int(delta.total_seconds() / 60)
                return f"{minutes}m ago"
            elif delta.total_seconds() < 86400:
                hours = int(delta.total_seconds() / 3600)
                return f"{hours}h ago"
            elif delta.total_seconds() < 604800:
                days = int(delta.total_seconds() / 86400)
                return f"{days}d ago"
            else:
                weeks = int(delta.total_seconds() / 604800)
                return f"{weeks}w ago"
        except (ValueError, TypeError):
            return "unknown"

    def _url_to_local_path(self, url: str) -> Optional[Path]:
        """Convert a URL to its potential local file path."""
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")

        if not path or path.endswith("/"):
            path = path + "index.html"

        filename = quote(path, safe="")
        if len(filename) > 200:
            hash_suffix = hashlib.sha256(path.encode()).hexdigest()[:8]
            filename = filename[:191] + "_" + hash_suffix + ".html"

        sync_dir = self._get_sync_dir_for_url(url)
        file_path = sync_dir / filename

        return file_path

    def get_local_content(self, url: str) -> Optional[str]:
        """Get locally synced content for a URL."""
        local_path = self._url_to_local_path(url)
        if local_path and local_path.exists():
            try:
                return local_path.read_text(encoding="utf-8")
            except (OSError, IOError):
                return None
        return None

    def local_content_exists(self, url: str) -> bool:
        """Check if local synced content exists for a URL."""
        local_path = self._url_to_local_path(url)
        return local_path is not None and local_path.exists()

    def discover_local_urls(self, base_url: str, max_pages: int = 50) -> list[str]:
        """Discover all locally available URLs for a documentation site."""
        parsed = urlparse(base_url)
        pages_dir = self._get_sync_dir_for_url(base_url)

        if not pages_dir.exists():
            return []

        urls = []
        for file_path in pages_dir.rglob("*.html"):
            rel_path = file_path.relative_to(pages_dir)
            path_str = str(rel_path)

            # Handle index.html files - convert to directory path
            if path_str == "index.html" or path_str.endswith("/index.html"):
                path_str = path_str[:-11] if path_str.endswith("/index.html") else ""
                if path_str:
                    path_str = "/" + path_str
                else:
                    path_str = "/"
            else:
                path_str = "/" + path_str

            url = f"{parsed.scheme}://{parsed.netloc}{path_str}"
            urls.append(url)

            if len(urls) >= max_pages:
                break

        return urls[:max_pages]

    def extract_words_for_suggestions(self, query: str) -> list[str]:
        """Extract words from query for suggestions."""
        words = re.split(r"[\s\-_/.]+", query.lower())
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        return [w for w in words if len(w) > 2 and w not in stopwords][:5]

    def search_in_local(
        self,
        query: str,
        base_url: str,
        case_sensitive: bool = False,
        regex: bool = False,
        context_lines: int = 1,
        max_results: int = 50,
    ) -> list[dict]:
        """Search within locally synced documentation."""
        from ..scraper.searcher import search_in_content, create_snippet

        urls = self.discover_local_urls(base_url, max_pages=max_results * 2)
        results = []

        for url in urls:
            content = self.get_local_content(url)
            if not content:
                continue

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(content, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            text_content = soup.get_text(separator="\n")

            matches = search_in_content(
                text_content,
                query,
                case_sensitive=case_sensitive,
                regex=regex,
            )

            if matches:
                from ..scraper.filter import extract_name_from_url

                title = extract_name_from_url(url)
                snippet = create_snippet(
                    text_content,
                    query,
                    context_lines=context_lines,
                    case_sensitive=case_sensitive,
                    regex=regex,
                )

                results.append({
                    "url": url,
                    "title": title,
                    "snippet": snippet,
                    "source": "local",
                })

                if len(results) >= max_results:
                    break

        return results


# Standalone functions for backwards compatibility

def discover_documentation_urls(base_url: str, max_pages: int = 50) -> list[str]:
    """Discover all available documentation URLs for a site.

    Args:
        base_url: Base URL of the documentation
        max_pages: Maximum number of pages to discover

    Returns:
        List of discovered URLs
    """
    return Search(SearchConfig(query="", url=base_url)).discover_local_urls(base_url, max_pages)


def discover_local_urls(base_url: str, max_pages: int = 50) -> list[str]:
    """Discover all locally available URLs for a documentation site.

    Args:
        base_url: Base URL of the documentation
        max_pages: Maximum number of pages to discover

    Returns:
        List of discovered local URLs
    """
    return Search(SearchConfig(query="", url=base_url)).discover_local_urls(base_url, max_pages)


def extract_words_for_suggestions(query: str) -> list[str]:
    """Extract words from query for suggestions.

    Args:
        query: The search query

    Returns:
        List of extracted words
    """
    return Search(SearchConfig(query=query, url="")).extract_words_for_suggestions(query)


def search_in_local(
    query: str,
    base_url: str,
    case_sensitive: bool = False,
    regex: bool = False,
    context_lines: int = 1,
    max_results: int = 50,
) -> list[dict]:
    """Search within locally synced documentation.

    Args:
        query: The search query
        base_url: Base URL of the documentation
        case_sensitive: Whether to perform case-sensitive search
        regex: Whether to treat query as regex
        context_lines: Number of context lines to include in snippets
        max_results: Maximum number of results to return

    Returns:
        List of search results
    """
    return Search(SearchConfig(query=query, url=base_url)).search_in_local(
        query, base_url, case_sensitive, regex, context_lines, max_results
    )
