"""Core business logic for get command.

This module contains pure business logic for fetching and converting
documentation pages, independent of CLI concerns.
"""

from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, quote

from markdownify import markdownify as md


# Cache settings
CACHE_MAX_SIZE_BYTES = 1024 * 1024 * 1024  # 1GB
CACHE_TTL_DAYS = 30

# Default sync directory
DEFAULT_SYNC_DIR = Path.home() / ".fresh" / "docs"


def get_sync_dir() -> Path:
    """Get the default sync directory.

    Returns:
        Path to the sync directory
    """
    return DEFAULT_SYNC_DIR


def set_sync_dir(path: Path) -> None:
    """Set the default sync directory (for testing).

    Args:
        path: New sync directory path
    """
    global DEFAULT_SYNC_DIR
    DEFAULT_SYNC_DIR = path


def url_to_sync_path(url: str, sync_dir: Optional[Path] = None) -> Optional[Path]:
    """Convert a URL to its potential sync file path.

    Args:
        url: The URL to convert
        sync_dir: The sync directory (defaults to DEFAULT_SYNC_DIR)

    Returns:
        The potential path in the sync directory, or None if the URL cannot be mapped
    """
    if sync_dir is None:
        sync_dir = DEFAULT_SYNC_DIR

    parsed = urlparse(url)
    domain = parsed.netloc.replace(":", "_").replace(".", "_")
    path = parsed.path.lstrip("/")

    if not path or path.endswith("/"):
        path = path + "index.html"

    # Sanitize filename
    filename = quote(path, safe="")
    if len(filename) > 200:
        filename = filename[:200]

    sync_path = sync_dir / domain / "pages" / filename

    return sync_path


def get_local_content(url: str, sync_dir: Optional[Path] = None) -> Optional[str]:
    """Get locally synced content for a URL.

    Args:
        url: The URL to get local content for
        sync_dir: The sync directory (defaults to DEFAULT_SYNC_DIR)

    Returns:
        Local HTML content or None if not available locally
    """
    sync_path = url_to_sync_path(url, sync_dir)
    if sync_path and sync_path.exists():
        try:
            return sync_path.read_text(encoding="utf-8")
        except (OSError, IOError):
            return None
    return None


def local_content_exists(url: str, sync_dir: Optional[Path] = None) -> bool:
    """Check if local synced content exists for a URL.

    Args:
        url: The URL to check
        sync_dir: The sync directory (defaults to DEFAULT_SYNC_DIR)

    Returns:
        True if local content exists, False otherwise
    """
    sync_path = url_to_sync_path(url, sync_dir)
    return sync_path is not None and sync_path.exists()


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


def get_cache_dir() -> Path:
    """Get the cache directory for fresh.

    Returns:
        Path to the cache directory
    """
    cache_dir = Path.home() / ".fresh" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def set_cache_dir(path: Path) -> None:
    """Set the cache directory (for testing).

    Args:
        path: New cache directory path
    """
    # This is a module-level function, cache_dir is computed on the fly
    pass


def get_cached_content(url: str, ttl_days: Optional[int] = None) -> Optional[str]:
    """Get cached content for a URL.

    Args:
        url: The URL to get cached content for
        ttl_days: Cache TTL in days (None = use default)

    Returns:
        Cached content or None if not cached or expired
    """
    # Create a hash of the URL for the filename
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    cache_file = get_cache_dir() / f"{url_hash}.md"

    if not cache_file.exists():
        return None

    # Check TTL if not disabled
    effective_ttl = ttl_days if ttl_days is not None else CACHE_TTL_DAYS
    if effective_ttl > 0:
        ttl_seconds = effective_ttl * 24 * 60 * 60
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age > ttl_seconds:
            # Cache expired, remove it
            cache_file.unlink()
            return None

    return cache_file.read_text(encoding="utf-8")


def save_to_cache(url: str, content: str) -> None:
    """Save content to cache.

    Args:
        url: The URL the content was fetched from
        content: The Markdown content to cache
    """
    # Enforce cache limits before saving
    _enforce_cache_limits()

    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    cache_file = get_cache_dir() / f"{url_hash}.md"
    cache_file.write_text(content, encoding="utf-8")


def _get_cache_size() -> int:
    """Get total cache size in bytes."""
    total = 0
    cache_dir = get_cache_dir()
    if cache_dir.exists():
        for file in cache_dir.glob("*.md"):
            total += file.stat().st_size
    return total


def _get_cache_files() -> list[tuple[Path, float]]:
    """Get list of cache files with their modification times.

    Returns:
        List of (file_path, mtime) tuples
    """
    cache_dir = get_cache_dir()
    files = []
    if cache_dir.exists():
        for file in cache_dir.glob("*.md"):
            files.append((file, file.stat().st_mtime))
    return files


def _remove_expired_cache_entries(ttl_days: int = CACHE_TTL_DAYS) -> int:
    """Remove expired cache entries based on TTL.

    Args:
        ttl_days: Cache TTL in days

    Returns:
        Number of entries removed
    """
    removed = 0
    ttl_seconds = ttl_days * 24 * 60 * 60
    current_time = time.time()

    for cache_file in get_cache_dir().glob("*.md"):
        file_age = current_time - cache_file.stat().st_mtime
        if file_age > ttl_seconds:
            cache_file.unlink()
            removed += 1

    return removed


def _enforce_cache_limits(max_size: int = CACHE_MAX_SIZE_BYTES) -> None:
    """Enforce cache size limits by removing oldest entries if needed.

    Args:
        max_size: Maximum cache size in bytes
    """
    current_size = _get_cache_size()
    if current_size <= max_size:
        return

    # Get files sorted by modification time (oldest first)
    files = sorted(_get_cache_files(), key=lambda x: x[1])

    # Remove oldest files until under limit
    for file_path, _ in files:
        if current_size <= max_size * 0.9:  # Target 90% of max
            break
        file_size = file_path.stat().st_size
        file_path.unlink()
        current_size -= file_size


def clear_cache() -> int:
    """Clear all cached content.

    Returns:
        Number of files removed
    """
    removed = 0
    cache_dir = get_cache_dir()
    if cache_dir.exists():
        for file in cache_dir.glob("*.md"):
            file.unlink()
            removed += 1
    return removed
