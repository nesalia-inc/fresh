"""Sync command - download entire documentation for offline use."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, quote

import httpx
import typer
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

from ..config import resolve_alias
from ..console import print_summary, reset_console, set_verbose
from ..scraper import crawler, filter as filter_module, sitemap
from ..scraper.crawler import parallel_crawl
from ..scraper.http import fetch_binary_aware, is_binary_url, is_allowed_by_robots, validate_url
from ..ui import is_interactive, spinner

app = typer.Typer(help="Download entire documentation for offline use.")

# Default sync directory
DEFAULT_SYNC_DIR = Path.home() / ".fresh" / "docs"


def _get_sync_dir(url: str, output_dir: Path | None) -> Path:
    """Get the sync directory for a URL."""
    if output_dir:
        return output_dir

    # Create directory based on domain
    parsed = urlparse(url)
    domain = parsed.netloc.replace(":", "_").replace(".", "_")
    return DEFAULT_SYNC_DIR / domain


def get_sync_dir(url: str, output_dir: Path | None = None) -> Path:
    """Get the sync directory for a URL (public version)."""
    return _get_sync_dir(url, output_dir)


def _save_metadata(sync_dir: Path, base_url: str, page_count: int) -> None:
    """Save sync metadata."""
    metadata = {
        "site": base_url,
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "page_count": page_count,
    }
    metadata_file = sync_dir / "_sync.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))


def get_sync_metadata(base_url: str) -> dict[str, str] | None:
    """
    Get sync metadata for a base URL.

    Args:
        base_url: The base URL of the documentation

    Returns:
        Dict with last_sync, page_count, or None if not synced
    """
    sync_dir = _get_sync_dir(base_url, None)
    metadata_file = sync_dir / "_sync.json"
    if not metadata_file.exists():
        return None
    try:
        data: dict[str, str] = json.loads(metadata_file.read_text(encoding="utf-8"))
        return data
    except (json.JSONDecodeError, IOError):
        return None


def is_locally_synced(url: str) -> bool:
    """
    Check if documentation has been synced locally.

    Args:
        url: The URL or alias of the documentation

    Returns:
        True if documentation is available locally, False otherwise
    """
    resolved_url = resolve_alias(url)
    metadata = get_sync_metadata(resolved_url)
    return metadata is not None


def get_page_freshness(page_url: str, base_url: str) -> dict[str, str] | None:
    """
    Get freshness metadata for a synced page.

    Args:
        page_url: The full URL of the page
        base_url: The base URL of the documentation

    Returns:
        Dict with synced_at, etag, last_modified, or None if not found
    """
    sync_dir = _get_sync_dir(base_url, None)
    pages_dir = sync_dir / "pages"
    if not pages_dir.exists():
        return None

    # Convert URL to filename
    parsed = urlparse(page_url)
    path = parsed.path.lstrip("/")
    if not path or path.endswith("/"):
        path = path + "index.html"

    filename = quote(path, safe="")
    if len(filename) > 200:
        hash_suffix = hashlib.sha256(path.encode()).hexdigest()[:8]
        filename = filename[:191] + "_" + hash_suffix + ".html"

    metadata_file = pages_dir / f"{filename}.meta.json"
    if not metadata_file.exists():
        return None

    try:
        data: dict[str, str] = json.loads(metadata_file.read_text(encoding="utf-8"))
        return data
    except (json.JSONDecodeError, IOError):
        return None


def check_page_changed(page_url: str, page_freshness: dict[str, str]) -> bool:
    """
    Check if a page has changed using HTTP conditional requests.

    Args:
        page_url: The URL to check
        page_freshness: Previous freshness metadata (etag, last_modified)

    Returns:
        True if page has changed, False if unchanged
    """
    headers: dict[str, str] = {}
    if etag := page_freshness.get("etag"):
        headers["If-None-Match"] = etag
    if last_modified := page_freshness.get("last-modified"):
        headers["If-Modified-Since"] = last_modified

    if not headers:
        return True  # No way to check, assume changed

    try:
        client = httpx.Client(timeout=10.0)
        try:
            resp = client.head(page_url, follow_redirects=True, headers=headers)
            # Log unexpected status codes
            if resp.status_code not in (200, 304):
                typer.echo(f"  Warning: Unexpected status {resp.status_code} for {page_url}")
            # 304 Not Modified means page hasn't changed
            return resp.status_code != 304
        finally:
            client.close()
    except (httpx.RequestError, httpx.TimeoutException):
        return True  # Error, assume changed to be safe


def _should_skip_page(
    page_url: str,
    incremental: bool,
    resolved_url: str,
    sitemap_domain: str | None,
    pages_dir: Path,
) -> tuple[bool, str]:
    """
    Check if a page should be skipped during sync.

    Args:
        page_url: The URL to check
        incremental: Whether incremental sync is enabled
        resolved_url: The base URL for the documentation
        sitemap_domain: Domain for robots.txt checks
        pages_dir: Directory containing page metadata

    Returns:
        Tuple of (should_skip: bool, reason: str)
    """
    # Check robots.txt
    if not is_allowed_by_robots(page_url, domain=sitemap_domain):
        return True, "robots.txt"

    # Check incremental sync
    if incremental:
        freshness = get_page_freshness(page_url, resolved_url)
        if freshness and not check_page_changed(page_url, freshness):
            return True, "unchanged"

    return False, ""


def _fetch_page_for_sync(page_url: str) -> tuple[str | None, dict[str, str] | None]:
    """
    Fetch a page for sync, skipping binary content.

    Args:
        page_url: The URL to fetch

    Returns:
        Tuple of (HTML content or None, headers dict or None)
    """
    import httpx

    # Use binary-aware fetch but also get headers
    response = fetch_binary_aware(page_url, skip_binary=True)
    if not response or not isinstance(response, str):
        return None, None

    # Get headers for freshness tracking
    headers: dict[str, str] = {}
    try:
        client = httpx.Client(timeout=10.0)
        resp = client.head(page_url, follow_redirects=True)
        if resp.status_code == 200:
            if etag := resp.headers.get("etag"):
                headers["etag"] = etag
            if last_modified := resp.headers.get("last-modified"):
                headers["last-modified"] = last_modified
        client.close()
    except Exception:
        pass

    return response, headers if headers else None


def _save_page(page_url: str, pages_dir: Path) -> bool | None:
    """
    Fetch and save a single page to the sync directory.

    Args:
        page_url: The URL of the page to save
        pages_dir: The directory to save pages to

    Returns:
        True if page was saved successfully, False if failed, None if skipped (binary)
    """
    # Check for binary URLs - skip but don't count as failure
    if is_binary_url(page_url):
        return None

    response, headers = _fetch_page_for_sync(page_url)
    if not response or not isinstance(response, str):
        return False

    parsed = urlparse(page_url)
    path = parsed.path.lstrip("/")
    if not path or path.endswith("/"):
        path = path + "index.html"

    # Sanitize filename - use hash to avoid collisions from truncation
    filename = quote(path, safe="")
    if len(filename) > 200:
        # Use hash prefix to ensure uniqueness after truncation
        hash_suffix = hashlib.sha256(path.encode()).hexdigest()[:8]
        filename = filename[:191] + "_" + hash_suffix + ".html"

    page_file = pages_dir / filename
    page_file.parent.mkdir(parents=True, exist_ok=True)
    page_file.write_text(response, encoding="utf-8")

    # Save page metadata for freshness tracking
    if headers:
        metadata_file = pages_dir / f"{filename}.meta.json"
        metadata = {
            "url": page_url,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        metadata.update(headers)
        metadata_file.write_text(json.dumps(metadata, indent=2))

    return True


@app.command(name="sync")
def sync(
    url: str = typer.Argument(..., help="The URL or alias of the documentation website"),
    output_dir: Path | None = typer.Option(
        None, "--output-dir", "-o", help="Target directory for synced docs"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Use verbose output"),
    max_pages: int = typer.Option(100, "--max-pages", help="Maximum number of pages to sync"),
    depth: int = typer.Option(3, "--depth", "-d", help="Maximum crawl depth"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-sync (delete existing files first)"),
    incremental: bool = typer.Option(True, "--incremental/--no-incremental", help="Only sync changed pages (uses etag/last-modified)"),
    pattern: str | None = typer.Option(None, "--pattern", "-p", help="Filter paths matching pattern"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of parallel workers (1 = sequential, >1 = parallel)"),
) -> None:
    """Download entire documentation for offline use."""
    # Initialize console with verbose mode
    set_verbose(verbose)
    reset_console()

    # Resolve alias to URL
    resolved_url = resolve_alias(url)

    if verbose and resolved_url != url:
        typer.echo(f"Resolved alias '{url}' to {resolved_url}")

    # Validate URL
    if not validate_url(resolved_url):
        typer.echo(f"Error: Invalid URL: {resolved_url}", err=True)
        raise typer.Exit(1)

    # Get sync directory
    sync_dir = _get_sync_dir(resolved_url, output_dir)

    # Handle --force option
    if force and sync_dir.exists():
        if verbose:
            typer.echo("Removing existing sync directory...")
        shutil.rmtree(sync_dir)

    sync_dir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"Syncing to: {sync_dir}")

    # Discover pages
    discovered_urls: set[str] = set()

    # Extract domain from sitemap for consistent robots.txt checking
    sitemap_domain: str | None = None

    if verbose:
        typer.echo("Discovering pages...")
        sitemap_url = sitemap.discover_sitemap(resolved_url)
    elif is_interactive():
        with spinner("Discovering pages..."):
            sitemap_url = sitemap.discover_sitemap(resolved_url)
    else:
        sitemap_url = sitemap.discover_sitemap(resolved_url)

    if sitemap_url:
        if verbose:
            typer.echo(f"Found sitemap at {sitemap_url}")
        # Extract domain from sitemap URL for consistent robots.txt checks
        sitemap_parsed = urlparse(sitemap_url)
        sitemap_domain = sitemap_parsed.netloc
        if verbose:
            typer.echo(f"Using domain for robots.txt checks: {sitemap_domain}")

        # Fetch sitemap content
        if is_interactive() and not verbose:
            with spinner("Fetching sitemap..."):
                xml_content = sitemap.fetch_with_retry(sitemap_url)
        else:
            xml_content = sitemap.fetch_with_retry(sitemap_url)

        if xml_content and isinstance(xml_content, str):
            urls = sitemap.parse_sitemap(xml_content)
            if urls:
                filtered = [u for u in urls if filter_module.is_relevant_url(u)]
                discovered_urls.update(filtered)

    # Fallback to crawler if no sitemap
    if not discovered_urls:
        if verbose:
            mode = "parallel" if workers > 1 else "sequential"
            typer.echo(f"No sitemap found, using {mode} crawler (workers={workers})...")
            if workers > 1:
                discovered_urls = parallel_crawl(
                    resolved_url, max_pages=max_pages, max_depth=depth, max_workers=workers
                )
            else:
                discovered_urls = crawler.crawl(resolved_url, max_pages=max_pages, max_depth=depth)
        elif is_interactive():
            with spinner(f"Crawling pages (max {max_pages}, workers={workers})..."):
                if workers > 1:
                    discovered_urls = parallel_crawl(
                        resolved_url, max_pages=max_pages, max_depth=depth, max_workers=workers
                    )
                else:
                    discovered_urls = crawler.crawl(resolved_url, max_pages=max_pages, max_depth=depth)
        else:
            if workers > 1:
                discovered_urls = parallel_crawl(
                    resolved_url, max_pages=max_pages, max_depth=depth, max_workers=workers
                )
            else:
                discovered_urls = crawler.crawl(resolved_url, max_pages=max_pages, max_depth=depth)

    # Apply pattern filter if specified
    if pattern:
        pattern_re = re.compile(pattern.replace("*", ".*"))
        discovered_urls = {u for u in discovered_urls if pattern_re.search(u)}

    # Limit pages
    urls_to_sync: list[str] = list(discovered_urls)[:max_pages]

    typer.echo(f"Found {len(urls_to_sync)} pages to sync")

    # Create pages directory
    pages_dir = sync_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    # Fetch each page
    success_count = 0
    fail_count = 0
    skipped_robots = 0
    skipped_binary = 0
    skipped_unchanged = 0
    total_pages = len(urls_to_sync)

    # Process pages based on output mode
    if verbose:
        # Verbose mode: show detailed output for each page
        for i, page_url in enumerate(urls_to_sync):
            typer.echo(f"[{i + 1}/{total_pages}] Syncing: {page_url}")

            skip, reason = _should_skip_page(page_url, incremental, resolved_url, sitemap_domain, pages_dir)
            if skip:
                if reason == "robots.txt":
                    skipped_robots += 1
                    typer.echo(f"  Skipped (robots.txt): {page_url}")
                elif reason == "unchanged":
                    skipped_unchanged += 1
                    typer.echo(f"  Skipped (unchanged): {page_url}")
                continue

            # Fetch and save the page
            try:
                result = _save_page(page_url, pages_dir)
                if result is True:
                    success_count += 1
                elif result is None:
                    # Binary file - skipped
                    skipped_binary += 1
                    typer.echo(f"  Skipped (binary): {page_url}")
                else:
                    fail_count += 1
                    typer.echo(f"  Failed (empty response): {page_url}")
            except Exception as e:
                fail_count += 1
                typer.echo(f"  Error: {page_url} - {e}")

    elif is_interactive():
        # Interactive mode: show progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(
                f"Syncing pages ({success_count}/{total_pages})...",
                total=total_pages,
            )

            for page_url in urls_to_sync:
                skip, reason = _should_skip_page(page_url, incremental, resolved_url, sitemap_domain, pages_dir)
                if skip:
                    if reason == "robots.txt":
                        skipped_robots += 1
                    elif reason == "unchanged":
                        skipped_unchanged += 1
                    progress.advance(task)
                    continue

                # Fetch and save the page
                try:
                    result = _save_page(page_url, pages_dir)
                    if result is True:
                        success_count += 1
                    elif result is None:
                        # Binary file - skipped
                        skipped_binary += 1
                    else:
                        fail_count += 1
                except Exception:
                    fail_count += 1

                progress.update(
                    task,
                    description=f"Syncing pages ({success_count}/{total_pages})...",
                )
                progress.advance(task)

    else:
        # Non-interactive mode: simple progress without spinner
        for page_url in urls_to_sync:
            skip, reason = _should_skip_page(page_url, incremental, resolved_url, sitemap_domain, pages_dir)
            if skip:
                if reason == "robots.txt":
                    skipped_robots += 1
                elif reason == "unchanged":
                    skipped_unchanged += 1
                continue

            # Fetch and save the page
            try:
                result = _save_page(page_url, pages_dir)
                if result is True:
                    success_count += 1
                elif result is None:
                    # Binary file - skipped
                    skipped_binary += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1

    # Save metadata
    _save_metadata(sync_dir, resolved_url, success_count)

    # Summary
    typer.echo("\nSync complete!")
    typer.echo(f"  Success: {success_count} pages")
    if skipped_unchanged > 0:
        typer.echo(f"  Skipped (unchanged): {skipped_unchanged} pages")
    if skipped_binary > 0:
        typer.echo(f"  Skipped (binary): {skipped_binary} pages")
    if skipped_robots > 0:
        typer.echo(f"  Skipped (robots.txt): {skipped_robots} pages")
    if fail_count > 0:
        typer.echo(f"  Failed: {fail_count} pages")
    typer.echo(f"  Saved to: {sync_dir}")

    # Print error/warning summary
    print_summary()
