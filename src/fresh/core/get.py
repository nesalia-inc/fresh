"""Core entity for get operations.

This module contains the Get entity which encapsulates all get logic,
following an entity-oriented architecture pattern.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, quote

from markdownify import markdownify as md

from .config import GetConfig, GetResult


# Default sync directory
DEFAULT_SYNC_DIR = Path.home() / ".fresh" / "docs"


class Get:
    """Entity representing a get operation.

    This class encapsulates all the business logic for fetching
    and converting documentation pages. It can be used with
    different adapters for HTTP fetching and caching.
    """

    def __init__(self, config: GetConfig) -> None:
        """Initialize Get entity.

        Args:
            config: The get configuration
        """
        self.config = config
        self._result = GetResult(url=config.url, resolved_url=config.url)

    @property
    def result(self) -> GetResult:
        """Get the get result."""
        return self._result

    def get_sync_dir(self) -> Path:
        """Get the default sync directory.

        Returns:
            Path to the sync directory
        """
        return DEFAULT_SYNC_DIR

    def url_to_sync_path(self, url: str, sync_dir: Optional[Path] = None) -> Optional[Path]:
        """Convert a URL to its potential sync file path.

        Args:
            url: The URL to convert
            sync_dir: Optional custom sync directory

        Returns:
            The potential path in the sync directory
        """
        parsed = urlparse(url)
        domain = parsed.netloc.replace(":", "_").replace(".", "_")
        path = parsed.path.lstrip("/")

        if not path or path.endswith("/"):
            path = path + "index.html"

        # Sanitize filename
        filename = quote(path, safe="")
        if len(filename) > 200:
            filename = filename[:200]

        if sync_dir is None:
            sync_dir = DEFAULT_SYNC_DIR
        file_path = sync_dir / domain / "pages" / filename

        return file_path

    def get_local_content(self, url: str, sync_dir: Optional[Path] = None) -> Optional[str]:
        """Get locally synced content for a URL.

        Args:
            url: The URL to get local content for
            sync_dir: Optional custom sync directory

        Returns:
            Local HTML content or None if not available locally
        """
        sync_path = self.url_to_sync_path(url, sync_dir)
        if sync_path and sync_path.exists():
            try:
                return sync_path.read_text(encoding="utf-8")
            except (OSError, IOError):
                return None
        return None

    def local_content_exists(self, url: str, sync_dir: Optional[Path] = None) -> bool:
        """Check if local synced content exists for a URL.

        Args:
            url: The URL to check
            sync_dir: Optional custom sync directory

        Returns:
            True if local content exists, False otherwise
        """
        sync_path = self.url_to_sync_path(url, sync_dir)
        return sync_path is not None and sync_path.exists()

    @staticmethod
    def html_to_markdown(html: str, skip_scripts: bool = False) -> str:
        """Convert HTML to Markdown.

        Args:
            html: The HTML content to convert
            skip_scripts: If True, remove script tags before conversion

        Returns:
            Markdown formatted string
        """
        if skip_scripts:
            # Remove script tags and their content
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)

        return md(html, heading_style="ATX")

    def get_cache_dir(self) -> Path:
        """Get the cache directory for fresh.

        Returns:
            Path to the cache directory
        """
        return Path.home() / ".fresh" / "cache"

    def get_cached_content(self, url: str, ttl_days: Optional[int] = None) -> Optional[str]:
        """Get cached content for a URL.

        Args:
            url: The URL to get cached content for
            ttl_days: Cache TTL in days (None = use default)

        Returns:
            Cached content or None if not cached or expired
        """
        effective_ttl = ttl_days if ttl_days is not None else 30
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        cache_file = self.get_cache_dir() / f"{url_hash}.md"

        if not cache_file.exists():
            return None

        if effective_ttl > 0:
            import time
            ttl_seconds = effective_ttl * 24 * 60 * 60
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age > ttl_seconds:
                cache_file.unlink()
                return None

        return cache_file.read_text(encoding="utf-8")

    def save_to_cache(self, url: str, content: str) -> None:
        """Save content to cache.

        Args:
            url: The URL the content was fetched from
            content: The Markdown content to cache
        """
        cache_dir = self.get_cache_dir()
        cache_dir.mkdir(parents=True, exist_ok=True)

        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        cache_file = cache_dir / f"{url_hash}.md"
        cache_file.write_text(content, encoding="utf-8")

    def clear_cache(self) -> int:
        """Clear all cached content.

        Returns:
            Number of files removed
        """
        removed = 0
        cache_dir = self.get_cache_dir()
        if cache_dir.exists():
            for file in cache_dir.glob("*.md"):
                file.unlink()
                removed += 1
        return removed


# Standalone functions for backwards compatibility

def get_sync_dir() -> Path:
    """Get the default sync directory.

    Returns:
        Path to the sync directory
    """
    return Path.home() / ".fresh" / "docs"


def url_to_sync_path(url: str, sync_dir: Optional[Path] = None) -> Optional[Path]:
    """Convert a URL to its potential sync file path.

    Args:
        url: The URL to convert
        sync_dir: Optional custom sync directory

    Returns:
        The potential path in the sync directory
    """
    return Get(GetConfig(url="")).url_to_sync_path(url, sync_dir)


def get_local_content(url: str, sync_dir: Optional[Path] = None) -> Optional[str]:
    """Get locally synced content for a URL.

    Args:
        url: The URL to get local content for
        sync_dir: Optional custom sync directory

    Returns:
        Local HTML content or None if not available locally
    """
    return Get(GetConfig(url="")).get_local_content(url, sync_dir)


def local_content_exists(url: str, sync_dir: Optional[Path] = None) -> bool:
    """Check if local synced content exists for a URL.

    Args:
        url: The URL to check
        sync_dir: Optional custom sync directory

    Returns:
        True if local content exists, False otherwise
    """
    return Get(GetConfig(url="")).local_content_exists(url, sync_dir)


def html_to_markdown(html: str, skip_scripts: bool = False) -> str:
    """Convert HTML to Markdown.

    Args:
        html: The HTML content to convert
        skip_scripts: If True, remove script tags before conversion

    Returns:
        Markdown formatted string
    """
    return Get.html_to_markdown(html, skip_scripts)


def get_cache_dir() -> Path:
    """Get the cache directory for fresh.

    Returns:
        Path to the cache directory
    """
    return Get(GetConfig(url="")).get_cache_dir()


def get_cached_content(url: str, ttl_days: Optional[int] = None) -> Optional[str]:
    """Get cached content for a URL.

    Args:
        url: The URL to get cached content for
        ttl_days: Cache TTL in days (None = use default)

    Returns:
        Cached content or None if not cached or expired
    """
    return Get(GetConfig(url="")).get_cached_content(url, ttl_days)


def save_to_cache(url: str, content: str) -> None:
    """Save content to cache.

    Args:
        url: The URL the content was fetched from
        content: The Markdown content to cache
    """
    Get(GetConfig(url="")).save_to_cache(url, content)


def clear_cache() -> int:
    """Clear all cached content.

    Returns:
        Number of files removed
    """
    return Get(GetConfig(url="")).clear_cache()
