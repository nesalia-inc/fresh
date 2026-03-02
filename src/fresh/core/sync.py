"""Core entity for sync operations.

This module contains the Sync entity which encapsulates all sync logic,
following an entity-oriented architecture pattern.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse, quote
from typing import Optional

from .config import SyncConfig, SyncResult


class Sync:
    """Entity representing a sync operation.

    This class encapsulates all the business logic for syncing documentation
    from a remote site. It can be used with different adapters for
    HTTP fetching, robots checking, and storage.
    """

    def __init__(self, config: SyncConfig) -> None:
        """Initialize Sync entity.

        Args:
            config: The sync configuration
        """
        self.config = config
        self._result = SyncResult(url=config.url)

    @property
    def result(self) -> SyncResult:
        """Get the sync result."""
        return self._result

    def should_skip_url(
        self,
        url: str,
        robots_allowed: bool,
        is_binary: bool,
        is_unchanged: bool,
    ) -> tuple[bool, str]:
        """Determine if a URL should be skipped.

        Args:
            url: The URL to check
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
        if self.config.pattern:
            return self._check_pattern(url)

        return False, ""

    def _check_pattern(self, url: str) -> tuple[bool, str]:
        """Check if URL matches the configured pattern.

        Args:
            url: The URL to check

        Returns:
            Tuple of (should_skip: bool, reason: str)
        """
        pattern = self.config.pattern
        if pattern:
            try:
                pattern_re = re.compile(pattern.replace("*", ".*"))
                if not pattern_re.search(url):
                    return True, "pattern"
            except re.error:
                pass
        return False, ""

    def compute_path(self, url: str, pages_dir: Path) -> Path:
        """Compute the local file path for a synced page.

        Args:
            url: The full URL of the page
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

    @staticmethod
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
        base_path = base_parsed.path.rstrip("/")
        if not base_path:
            base_path = "/"
        return f"{base_parsed.scheme}://{base_parsed.netloc}{base_path}/{url}"

    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL.

        Args:
            url: The URL to extract domain from

        Returns:
            The domain name with underscores instead of dots
        """
        parsed = urlparse(url)
        return parsed.netloc.replace(":", "_").replace(".", "_")

    def filter_urls(self, urls: list[str]) -> list[str]:
        """Filter URLs by configured pattern.

        Args:
            urls: List of URLs to filter

        Returns:
            Filtered list of URLs
        """
        if not self.config.pattern:
            return urls

        try:
            pattern_re = re.compile(self.config.pattern.replace("*", ".*"))
            return [u for u in urls if pattern_re.search(u)]
        except re.error:
            return urls

    def limit_urls(self, urls: list[str]) -> list[str]:
        """Limit URLs to configured maximum.

        Args:
            urls: List of URLs

        Returns:
            Limited list of URLs
        """
        return urls[:self.config.max_pages]

    def record_success(self) -> None:
        """Record a successful sync."""
        self._result.success_count += 1

    def record_failure(self) -> None:
        """Record a failed sync."""
        self._result.failed_count += 1

    def record_skipped_robots(self) -> None:
        """Record a skipped robots.txt."""
        self._result.skipped_robots += 1

    def record_skipped_binary(self) -> None:
        """Record a skipped binary URL."""
        self._result.skipped_binary += 1

    def record_skipped_unchanged(self) -> None:
        """Record a skipped unchanged page."""
        self._result.skipped_unchanged += 1


# Factory function for backwards compatibility
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
    pattern: Optional[str],
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
    return Sync.normalize_url(url, base_url)


def extract_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: The URL to extract domain from

    Returns:
        The domain name with underscores instead of dots
    """
    return Sync.extract_domain(url)


def filter_urls_by_pattern(urls: list[str], pattern: Optional[str]) -> list[str]:
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
