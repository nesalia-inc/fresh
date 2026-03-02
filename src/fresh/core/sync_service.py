"""Core sync service - pure business logic without I/O.

This module contains the pure business logic for syncing documentation,
fully testable without any network or file system dependencies.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse, quote

from .config import SyncConfig, SyncResult


def create_sync_result(url: str) -> SyncResult:
    """Create a new SyncResult.

    Args:
        url: The base URL being synced

    Returns:
        A new SyncResult instance
    """
    return SyncResult(url=url)


def should_skip_url(
    url: str,
    pattern: str | None,
    robots_allowed: bool,
    is_binary: bool,
    is_unchanged: bool,
) -> tuple[bool, str]:
    """Determine if a URL should be skipped.

    Args:
        url: The URL to check
        pattern: Optional regex pattern to match
        robots_allowed: Whether URL is allowed by robots.txt
        is_binary: Whether URL is binary content
        is_unchanged: Whether page has changed since last sync

    Returns:
        Tuple of (should_skip: bool, reason: str)
    """
    # Check robots.txt
    if not robots_allowed:
        return True, "robots"

    # Check binary
    if is_binary:
        return True, "binary"

    # Check unchanged
    if is_unchanged:
        return True, "unchanged"

    # Check pattern
    if pattern:
        try:
            pattern_re = re.compile(pattern.replace("*", ".*"))
            if not pattern_re.search(url):
                return True, "pattern"
        except re.error:
            pass

    return False, ""


def compute_sync_path(url: str, base_url: str, pages_dir: Path) -> Path:
    """Compute the local file path for a synced page.

    Args:
        url: The full URL of the page
        base_url: The base URL of the documentation
        pages_dir: The directory to save pages to

    Returns:
        The computed file path
    """
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")

    if not path or path.endswith("/"):
        path = path + "index.html"

    # Sanitize filename
    filename = quote(path, safe="")
    if len(filename) > 200:
        # Use hash to avoid collisions
        hash_suffix = hashlib.sha256(path.encode()).hexdigest()[:8]
        filename = filename[:191] + "_" + hash_suffix + ".html"

    return pages_dir / filename


def normalize_url(url: str, base_url: str) -> str:
    """Normalize a URL relative to a base URL.

    Args:
        url: The URL to normalize
        base_url: The base URL

    Returns:
        The normalized absolute URL
    """
    if not url:
        return base_url

    parsed = urlparse(url)

    # Already absolute
    if parsed.scheme:
        return url

    # Protocol-relative
    if url.startswith("//"):
        return "https:" + url

    # Absolute path
    if url.startswith("/"):
        base_parsed = urlparse(base_url)
        return f"{base_parsed.scheme}://{base_parsed.netloc}{url}"

    # Relative path
    base_parsed = urlparse(base_url)
    base_path = base_parsed.path.rsplit("/", 1)[0]
    return f"{base_parsed.scheme}://{base_parsed.netloc}/{base_path}/{url}"


def extract_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: The URL to extract domain from

    Returns:
        The domain name with underscores instead of dots
    """
    parsed = urlparse(url)
    return parsed.netloc.replace(":", "_").replace(".", "_")


def filter_urls_by_pattern(urls: list[str], pattern: str | None) -> list[str]:
    """Filter URLs by a pattern.

    Args:
        urls: List of URLs to filter
        pattern: Optional regex pattern

    Returns:
        Filtered list of URLs
    """
    if not pattern:
        return urls

    try:
        pattern_re = re.compile(pattern.replace("*", ".*"))
        return [u for u in urls if pattern_re.search(u)]
    except re.error:
        return urls


def limit_urls(urls: list[str], max_pages: int) -> list[str]:
    """Limit URLs to maximum count.

    Args:
        urls: List of URLs
        max_pages: Maximum number of URLs to return

    Returns:
        Limited list of URLs
    """
    return urls[:max_pages]


def count_results(sync_result: SyncResult) -> dict:
    """Count sync result statistics.

    Args:
        sync_result: The sync result to analyze

    Returns:
        Dictionary with counts
    """
    return {
        "success": sync_result.success_count,
        "failed": sync_result.failed_count,
        "skipped_robots": sync_result.skipped_robots,
        "skipped_binary": sync_result.skipped_binary,
        "skipped_unchanged": sync_result.skipped_unchanged,
        "total": sync_result.total_pages,
    }
