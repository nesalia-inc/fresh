"""Get command - fetch a documentation page and convert to Markdown."""

from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import typer
from markdownify import markdownify as md

from ..config import resolve_alias
from ..scraper.http import fetch_with_retry, validate_url
from ..ui import is_interactive, show_error_message, show_success_message, spinner

app = typer.Typer(help="Fetch a documentation page and convert to Markdown.")

# Cache settings
CACHE_MAX_SIZE_BYTES = 1024 * 1024 * 1024  # 1GB
CACHE_TTL_DAYS = 30


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


def get_cached_content(url: str) -> str | None:
    """Get cached content for a URL.

    Args:
        url: The URL to get cached content for

    Returns:
        Cached content or None if not cached
    """
    # Create a hash of the URL for the filename
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    cache_file = get_cache_dir() / f"{url_hash}.md"

    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")
    return None


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


def _remove_expired_cache_entries() -> int:
    """Remove expired cache entries based on TTL.

    Returns:
        Number of files deleted
    """
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return 0

    now = time.time()
    ttl_seconds = CACHE_TTL_DAYS * 24 * 60 * 60
    count = 0

    for file in cache_dir.glob("*.md"):
        if now - file.stat().st_mtime > ttl_seconds:
            file.unlink()
            count += 1
    return count


def _enforce_cache_limits() -> None:
    """Enforce cache size and TTL limits."""
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return

    # Remove expired entries
    _remove_expired_cache_entries()

    # Enforce size limit (LRU eviction) - calculate size once
    total_size = _get_cache_size()
    while total_size > CACHE_MAX_SIZE_BYTES:
        files = _get_cache_files()
        if not files:
            break
        # Sort by mtime (oldest first)
        files.sort(key=lambda x: x[1])
        # Remove oldest file and update size
        file_to_remove = files[0][0]
        file_size = file_to_remove.stat().st_size
        file_to_remove.unlink()
        total_size -= file_size


def get_cache_size_human() -> str:
    """Get cache size in human-readable format."""
    size = _get_cache_size()
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def clear_cache() -> int:
    """Clear all cached content.

    Returns:
        Number of files deleted
    """
    cache_dir = get_cache_dir()
    count = 0
    if cache_dir.exists():
        for file in cache_dir.glob("*.md"):
            file.unlink()
            count += 1
    return count


def clean_expired_cache() -> int:
    """Remove expired cache entries.

    Returns:
        Number of files deleted
    """
    return _remove_expired_cache_entries()


@app.command(name="get")
def get(
    url: str = typer.Argument(..., help="The URL or alias of the documentation page to fetch"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Use verbose output"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Request timeout in seconds"),
    header: str | None = typer.Option(None, "--header", help="Custom HTTP header (format: 'Key: Value')"),
    no_follow: bool = typer.Option(False, "--no-follow", help="Do not follow redirects"),
    skip_scripts: bool = typer.Option(False, "--skip-scripts", help="Exclude JavaScript from output"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache"),
    output: str | None = typer.Option(None, "--output", "-o", help="Write output to file"),
    retry: int = typer.Option(3, "--retry", "-r", help="Number of retry attempts"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be fetched without downloading"),
) -> None:
    """Fetch a documentation page and convert it to Markdown."""
    # Resolve alias to URL
    resolved_url = resolve_alias(url)

    if verbose and resolved_url != url:
        typer.echo(f"Resolved alias '{url}' to {resolved_url}")

    # Validate URL
    if not validate_url(resolved_url):
        typer.echo(f"Error: Invalid URL: {resolved_url}", err=True)
        raise typer.Exit(1)

    # Check cache first (unless --no-cache is specified)
    content: str | None = None
    if not no_cache:
        if verbose:
            typer.echo("Checking cache...")
            content = get_cached_content(resolved_url)
        elif is_interactive():
            with spinner("Checking cache..."):
                content = get_cached_content(resolved_url)
        else:
            content = get_cached_content(resolved_url)

        if content:
            if verbose:
                typer.echo("✓ Found in cache")
            elif is_interactive():
                show_success_message("Found in cache")

    # Fetch if not cached
    if content is None:
        if dry_run:
            typer.echo(f"Would fetch: {resolved_url}")
            return

        # Prepare headers
        headers = {}
        if header:
            if ":" not in header:
                typer.echo("Error: Header must be in format 'Key: Value'", err=True)
                raise typer.Exit(1)
            key, value = header.split(":", 1)
            # Validate header value to prevent HTTP header injection
            if re.search(r"[\r\n]", value):
                typer.echo("Error: Header value must not contain newline characters", err=True)
                raise typer.Exit(1)
            headers[key.strip()] = value.strip()

        # Fetch the page with spinner in interactive mode
        if verbose:
            typer.echo(f"Fetching {resolved_url}...")
            response = fetch_with_retry(
                resolved_url,
                max_retries=retry,
                return_response=True,
                headers=headers,
                follow_redirects=not no_follow,
                timeout=timeout,
            )
        elif is_interactive():
            with spinner(f"Fetching {resolved_url}..."):
                response = fetch_with_retry(
                    resolved_url,
                    max_retries=retry,
                    return_response=True,
                    headers=headers,
                    follow_redirects=not no_follow,
                    timeout=timeout,
                )
        else:
            response = fetch_with_retry(
                resolved_url,
                max_retries=retry,
                return_response=True,
                headers=headers,
                follow_redirects=not no_follow,
                timeout=timeout,
            )

        if response is None:
            show_error_message(f"Failed to fetch {resolved_url}")
            raise typer.Exit(1)

        if hasattr(response, "text"):
            html_content = response.text
        else:
            html_content = str(response)

        if verbose:
            typer.echo(f"✓ Fetched ({len(html_content)} bytes)")

        # Convert to Markdown
        if verbose:
            typer.echo("Converting to Markdown...")
            content = html_to_markdown(html_content, skip_scripts=skip_scripts)
        elif is_interactive():
            with spinner("Converting to Markdown..."):
                content = html_to_markdown(html_content, skip_scripts=skip_scripts)
        else:
            content = html_to_markdown(html_content, skip_scripts=skip_scripts)

        # Save to cache
        if not no_cache:
            save_to_cache(resolved_url, content)  # type: ignore[arg-type]
            if verbose:
                typer.echo("✓ Saved to cache")

    # Output the content
    # At this point, content is guaranteed to be set (either from cache or fetched)
    assert content is not None

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        if verbose:
            typer.echo(f"✓ Written to {output}")
    else:
        typer.echo(content)

    if verbose:
        typer.echo(f"✓ Done ({len(content)} chars)")
