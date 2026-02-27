"""Get command - fetch a documentation page and convert to Markdown."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, quote

import typer
from markdownify import markdownify as md

from ..config import resolve_alias
from ..console import echo_error, print_summary, reset_console, set_verbose
from ..scraper.http import fetch_with_retry, validate_url
from ..ui import CHECK_MARK, CROSS_MARK

app = typer.Typer(help="Fetch a documentation page and convert to Markdown.")

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


def url_to_sync_path(url: str) -> Path | None:
    """Convert a URL to its potential sync file path.

    Args:
        url: The URL to convert

    Returns:
        The potential path in the sync directory, or None if the URL cannot be mapped
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

    sync_dir = DEFAULT_SYNC_DIR / domain / "pages"
    file_path = sync_dir / filename

    return file_path


def get_local_content(url: str) -> str | None:
    """Get locally synced content for a URL.

    Args:
        url: The URL to get local content for

    Returns:
        Local HTML content or None if not available locally
    """
    sync_path = url_to_sync_path(url)
    if sync_path and sync_path.exists():
        try:
            return sync_path.read_text(encoding="utf-8")
        except (OSError, IOError):
            return None
    return None


def local_content_exists(url: str) -> bool:
    """Check if local synced content exists for a URL.

    Args:
        url: The URL to check

    Returns:
        True if local content exists, False otherwise
    """
    sync_path = url_to_sync_path(url)
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


def read_urls_from_file(file_path: str) -> list[str]:
    """Read URLs from a file.

    Args:
        file_path: Path to the file containing URLs (one per line)

    Returns:
        List of URLs
    """
    path = Path(file_path)
    if not path.exists():
        echo_error(
            message=f"File not found: {file_path}",
            code="FILE_NOT_FOUND",
        )
        raise typer.Exit(1)

    content = path.read_text(encoding="utf-8")
    urls = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
    return urls


def fetch_single_url(
    url: str,
    verbose: bool = False,
    timeout: int = 30,
    header: str | None = None,
    no_follow: bool = False,
    skip_scripts: bool = False,
    no_cache: bool = False,
    retry: int = 3,
    dry_run: bool = False,
    local: bool = False,
    remote: bool = False,
) -> dict | None:
    """Fetch a single URL and return the result.

    Args:
        url: The URL to fetch
        verbose: Use verbose output
        timeout: Request timeout in seconds
        header: Custom HTTP header
        no_follow: Do not follow redirects
        skip_scripts: Exclude JavaScript from output
        no_cache: Bypass cache
        retry: Number of retry attempts
        dry_run: Show what would be fetched without downloading
        local: Use only local synced content
        remote: Force remote fetching

    Returns:
        Dictionary with url, content, success, error keys
    """
    # Resolve alias to URL
    resolved_url = resolve_alias(url)

    if verbose and resolved_url != url:
        typer.echo(f"Resolved alias '{url}' to {resolved_url}")

    # Validate URL
    if not validate_url(resolved_url):
        return {
            "url": url,
            "resolved_url": resolved_url,
            "content": None,
            "success": False,
            "error": f"Invalid URL: {resolved_url}",
        }

    # Determine fetch strategy
    use_local_only = local
    skip_local = remote

    content: str | None = None
    html_content: str | None = None

    # Check local synced content first
    if not skip_local and local_content_exists(resolved_url):
        if verbose:
            typer.echo("Found local synced content...")
        html_content = get_local_content(resolved_url)
        if html_content:
            if verbose:
                typer.echo("Using local content")
            content = html_to_markdown(html_content, skip_scripts=skip_scripts)

    # If --local was specified but no local content found
    if use_local_only and content is None:
        return {
            "url": url,
            "resolved_url": resolved_url,
            "content": None,
            "success": False,
            "error": "Local content not found. Run 'fresh sync' first.",
        }

    # Try cache if not local-only
    if content is None and not use_local_only and not no_cache:
        if verbose:
            typer.echo("Checking cache...")
        content = get_cached_content(resolved_url)
        if content and verbose:
            typer.echo("Found in cache")

    # Fetch if not cached and not local-only
    if content is None and not use_local_only:
        if dry_run:
            typer.echo(f"Would fetch: {resolved_url}")
            return {
                "url": url,
                "resolved_url": resolved_url,
                "content": None,
                "success": True,
                "dry_run": True,
            }

        # Prepare headers
        headers = {}
        if header:
            if ":" not in header:
                return {
                    "url": url,
                    "resolved_url": resolved_url,
                    "content": None,
                    "success": False,
                    "error": "Header must be in format 'Key: Value'",
                }
            key, value = header.split(":", 1)
            if re.search("[\r\n]", key) or re.search("[\r\n]", value):
                return {
                    "url": url,
                    "resolved_url": resolved_url,
                    "content": None,
                    "success": False,
                    "error": "Header must not contain newline characters",
                }
            headers[key.strip()] = value.strip()

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

        if response is None:
            return {
                "url": url,
                "resolved_url": resolved_url,
                "content": None,
                "success": False,
                "error": f"Failed to fetch page after {retry} attempts",
            }

        if hasattr(response, "text"):
            html_content = response.text
        else:
            html_content = str(response)

        if verbose:
            typer.echo(f"{CHECK_MARK} Fetched ({len(html_content)} bytes)")

        # Convert to Markdown
        if verbose:
            typer.echo("Converting to Markdown...")
        content = html_to_markdown(html_content, skip_scripts=skip_scripts)

        # Save to cache
        if not no_cache:
            save_to_cache(resolved_url, content)
            if verbose:
                typer.echo(f"{CHECK_MARK} Saved to cache")

    if content is None:
        return {
            "url": url,
            "resolved_url": resolved_url,
            "content": None,
            "success": False,
            "error": "No content retrieved",
        }

    return {
        "url": url,
        "resolved_url": resolved_url,
        "content": content,
        "success": True,
    }


@app.command(name="get")
def get(
    url: list[str] = typer.Argument(None, help="The URL or alias of the documentation page to fetch"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Use verbose output"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Request timeout in seconds"),
    header: str | None = typer.Option(None, "--header", help="Custom HTTP header (format: 'Key: Value')"),
    no_follow: bool = typer.Option(False, "--no-follow", help="Do not follow redirects"),
    skip_scripts: bool = typer.Option(False, "--skip-scripts", help="Exclude JavaScript from output"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache"),
    output: str | None = typer.Option(None, "--output", "-o", help="Write output to file (for single URL)"),
    output_dir: Path | None = typer.Option(None, "--output-dir", help="Write each page to a separate file in directory"),
    input_file: Path | None = typer.Option(None, "--input-file", "-i", help="Read URLs from file"),
    stdin: bool = typer.Option(False, "--stdin", help="Read URLs from stdin"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json"),
    retry: int = typer.Option(3, "--retry", "-r", help="Number of retry attempts"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be fetched without downloading"),
    local: bool = typer.Option(False, "--local", "--offline", help="Use only local synced content (no network requests)"),
    remote: bool = typer.Option(False, "--remote", help="Force remote fetching (skip local content check)"),
) -> None:
    """Fetch a documentation page and convert it to Markdown.

    By default, the command uses a local-first strategy: it checks for locally
    synced content first, then falls back to remote fetching. Use --local to
    use only local content, or --remote to force remote fetching.
    """
    # Validate mutually exclusive options
    if local and remote:
        echo_error(
            message="Cannot use both --local and --remote flags",
            code="CONFLICTING_OPTIONS",
            suggestions=["Use either --local or --remote, not both"],
        )
        raise typer.Exit(1)

    if output and (output_dir or format == "json"):
        echo_error(
            message="Cannot use --output with --output-dir or --format",
            code="CONFLICTING_OPTIONS",
            suggestions=["Use either --output, --output-dir, or --format"],
        )
        raise typer.Exit(1)

    # Initialize console with verbose mode
    set_verbose(verbose)
    reset_console()

    # Collect URLs from all sources
    urls_to_fetch: list[str] = []

    # From URL arguments
    if url:
        urls_to_fetch.extend(url)

    # From --input-file
    if input_file:
        file_urls = read_urls_from_file(str(input_file))
        urls_to_fetch.extend(file_urls)

    # From --stdin
    if stdin:
        if not sys.stdin.isatty():
            stdin_content = sys.stdin.read()
            stdin_urls = [line.strip() for line in stdin_content.splitlines() if line.strip()]
            urls_to_fetch.extend(stdin_urls)
        else:
            echo_error(
                message="No input provided via stdin",
                code="NO_STDIN",
                suggestions=["Pipe URLs to the command: echo 'url' | fresh get --stdin"],
            )
            raise typer.Exit(1)

    # Validate we have URLs
    if not urls_to_fetch:
        echo_error(
            message="No URL provided",
            code="NO_URL",
            suggestions=["Provide a URL as argument, use --input-file, or --stdin"],
        )
        raise typer.Exit(1)

    # Fetch all URLs
    results: list[dict] = []
    for url_item in urls_to_fetch:
        result = fetch_single_url(
            url_item,
            verbose=verbose,
            timeout=timeout,
            header=header,
            no_follow=no_follow,
            skip_scripts=skip_scripts,
            no_cache=no_cache,
            retry=retry,
            dry_run=dry_run,
            local=local,
            remote=remote,
        )
        if result:
            results.append(result)

    # Handle output based on mode
    if format == "json":
        # JSON output for all results
        output_data = [
            {"url": r["url"], "content": r["content"], "success": r["success"], "error": r.get("error")}
            for r in results
        ]
        typer.echo(json.dumps(output_data, indent=2))
        return

    if output_dir:
        # Write each page to a separate file
        output_dir.mkdir(parents=True, exist_ok=True)
        success_count = 0
        for result in results:
            if result["success"] and result["content"]:
                # Generate filename from URL
                parsed = urlparse(result["resolved_url"])
                path = parsed.path.lstrip("/")
                if not path or path.endswith("/"):
                    path = path + "index.md"
                else:
                    # Convert to .md extension
                    if not path.endswith(".md"):
                        path = path.rsplit(".", 1)[0] + ".md"

                filename = quote(path, safe="")
                if len(filename) > 200:
                    filename = filename[:200]

                file_path = output_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(result["content"], encoding="utf-8")
                success_count += 1
                if verbose:
                    typer.echo(f"{CHECK_MARK} Written to {file_path}")

        if verbose:
            typer.echo(f"{CHECK_MARK} Done ({success_count}/{len(results)} pages)")
        return

    # Single URL with text output (legacy behavior)
    if len(results) == 1:
        result = results[0]

        # Handle dry_run case
        if result.get("dry_run"):
            typer.echo(f"Would fetch: {result['resolved_url']}")
            return

        if not result["success"]:
            echo_error(
                message=result.get("error", "Failed to fetch page"),
                url=result.get("resolved_url"),
                code="FETCH_FAILED",
            )
            raise typer.Exit(1)
        if result["content"]:
            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(result["content"], encoding="utf-8")
                if verbose:
                    typer.echo(f"{CHECK_MARK} Written to {output}")
            else:
                typer.echo(result["content"])
            if verbose:
                typer.echo(f"{CHECK_MARK} Done ({len(result['content'])} chars)")
        else:
            echo_error(
                message="No content retrieved",
                url=result.get("resolved_url"),
                code="NO_CONTENT",
            )
            raise typer.Exit(1)
    else:
        # Multiple URLs without special output option - show summary
        success_count = sum(1 for r in results if r["success"])
        typer.echo(f"Fetched {success_count}/{len(results)} pages successfully")
        if verbose:
            for result in results:
                status = CHECK_MARK if result["success"] else CROSS_MARK
                typer.echo(f"  {status} {result['url']}")

    # Print error/warning summary
    print_summary()
