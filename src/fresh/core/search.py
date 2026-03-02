"""Core business logic for search command.

This module contains pure business logic for searching documentation,
independent of CLI concerns.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional
from urllib.parse import quote, urlparse

from ..scraper.searcher import search_in_content, create_snippet
from ..scraper.filter import extract_name_from_url  # noqa: F401 - used in functions
from ..scraper.sitemap import discover_sitemap, fetch_with_retry, parse_sitemap
from ..scraper import crawler


# Default sync directory (same as get.py)
DEFAULT_SYNC_DIR = Path.home() / ".fresh" / "docs"

# Parallel search settings
PARALLEL_THRESHOLD = 10
DEFAULT_MAX_WORKERS = 4


def get_sync_dir() -> Path:
    """Get the default sync directory."""
    return DEFAULT_SYNC_DIR


def _get_sync_dir_for_url(url: str) -> Path:
    """Get the sync directory for a URL's domain."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace(":", "_").replace(".", "_")
    return DEFAULT_SYNC_DIR / domain / "pages"


def _format_freshness_age(timestamp: str) -> str:
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


def _get_result_freshness(url: str, base_url: str) -> Optional[str]:
    """Get freshness info for a URL if available."""
    # Import from commands.sync to avoid circular imports
    from ..commands.sync import get_page_freshness

    if freshness := get_page_freshness(url, base_url):
        if synced_at := freshness.get("synced_at"):
            return _format_freshness_age(synced_at)
    return None


def _url_to_local_path(url: str) -> Optional[Path]:
    """Convert a URL to its potential local file path."""
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")

    if not path or path.endswith("/"):
        path = path + "index.html"

    # Sanitize filename - use hash to avoid collisions from truncation
    filename = quote(path, safe="")
    if len(filename) > 200:
        # Use hash prefix to ensure uniqueness after truncation
        hash_suffix = hashlib.sha256(path.encode()).hexdigest()[:8]
        filename = filename[:191] + "_" + hash_suffix + ".html"

    sync_dir = _get_sync_dir_for_url(url)
    file_path = sync_dir / filename

    return file_path


def get_local_content(url: str) -> Optional[str]:
    """Get locally synced content for a URL."""
    local_path = _url_to_local_path(url)
    if local_path and local_path.exists():
        try:
            return local_path.read_text(encoding="utf-8")
        except (OSError, IOError):
            return None
    return None


def local_content_exists(url: str) -> bool:
    """Check if local synced content exists for a URL."""
    local_path = _url_to_local_path(url)
    return local_path is not None and local_path.exists()


def discover_local_urls(base_url: str, max_pages: int = 50) -> list[str]:
    """Discover all locally available URLs for a documentation site."""
    parsed = urlparse(base_url)
    domain = parsed.netloc.replace(":", "_").replace(".", "_")
    pages_dir = DEFAULT_SYNC_DIR / domain / "pages"

    if not pages_dir.exists():
        return []

    urls = []
    for file_path in pages_dir.rglob("*.html"):
        # Convert file path back to URL
        rel_path = file_path.relative_to(pages_dir)
        path_str = str(rel_path)

        # Handle index.html files
        if path_str.endswith("/index.html"):
            path_str = path_str[:-11]

        url_path = "/" + path_str.replace("\\", "/")
        url = f"{parsed.scheme}://{parsed.netloc}{url_path}"
        urls.append(url)

        if len(urls) >= max_pages:
            break

    return urls[:max_pages]


def _search_page_content(
    page_url: str,
    query: str,
    case_sensitive: bool,
    regex: bool,
    context_lines: int,
) -> Optional[tuple[str, str]]:
    """Search a single page's content for a query."""
    from ..scraper.http import fetch_binary_aware

    # Fetch the page
    response = fetch_binary_aware(page_url, max_retries=2)
    if not response:
        return None

    # Convert to text content
    if hasattr(response, "text"):
        html_content = response.text
    else:
        html_content = str(response)

    # Parse and extract text
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    text_content = soup.get_text(separator="\n")

    # Search in the content
    matches = search_in_content(
        text_content,
        query,
        case_sensitive=case_sensitive,
        regex=regex,
    )

    if not matches:
        return None

    # Extract title and create snippet

    title = extract_name_from_url(page_url)
    snippet = create_snippet(
        text_content, query, context_lines=context_lines, case_sensitive=case_sensitive, regex=regex
    )

    return title, snippet


def discover_documentation_urls(
    base_url: str,
    max_pages: int = 50,
    verbose: bool = False,
) -> list[str]:
    """Discover documentation URLs from a site.

    Uses sitemap if available, falls back to crawling.
    """
    # Try sitemap first
    sitemap_url = discover_sitemap(base_url)

    if sitemap_url:
        content = fetch_with_retry(sitemap_url)
        if content:
            urls = parse_sitemap(content)  # type: ignore[arg-type]
            if urls:
                return urls[:max_pages]

    # Fall back to crawling
    try:
        crawled = crawler.crawl(base_url, max_pages=max_pages)
        return list(crawled)[:max_pages]
    except Exception:
        return []


def extract_words_for_suggestions(query: str) -> list[str]:
    """Extract words from query for suggestions."""
    # Split on whitespace and special characters
    words = re.split(r"[\s\-_/.]+", query.lower())
    # Filter out short words and common stopwords
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    return [w for w in words if len(w) > 2 and w not in stopwords][:5]


def search_in_local(
    query: str,
    base_url: str,
    case_sensitive: bool = False,
    regex: bool = False,
    context_lines: int = 1,
    max_results: int = 50,
) -> list[dict]:
    """Search within locally synced documentation.

    Returns list of search results with url, title, snippet, source.
    """
    # Get all local URLs
    urls = discover_local_urls(base_url, max_pages=max_results * 2)

    results = []
    for url in urls:
        content = get_local_content(url)
        if not content:
            continue

        # Parse and extract text
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text_content = soup.get_text(separator="\n")

        # Search in the content
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
