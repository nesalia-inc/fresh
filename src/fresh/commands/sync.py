"""Sync command - download entire documentation for offline use."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, quote

import typer

from ..config import resolve_alias
from ..scraper import crawler, filter as filter_module, sitemap
from ..scraper.http import fetch_with_retry, is_allowed_by_robots, validate_url

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


def _save_metadata(sync_dir: Path, base_url: str, page_count: int) -> None:
    """Save sync metadata."""
    metadata = {
        "site": base_url,
        "last_sync": datetime.now().isoformat(),
        "page_count": page_count,
    }
    metadata_file = sync_dir / "_sync.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))


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
    pattern: str | None = typer.Option(None, "--pattern", "-p", help="Filter paths matching pattern"),
) -> None:
    """Download entire documentation for offline use."""
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
    if sitemap_url:
        if verbose:
            typer.echo(f"Found sitemap at {sitemap_url}")
        # Extract domain from sitemap URL for consistent robots.txt checks
        sitemap_parsed = urlparse(sitemap_url)
        sitemap_domain = sitemap_parsed.netloc
        if verbose:
            typer.echo(f"Using domain for robots.txt checks: {sitemap_domain}")
        xml_content = sitemap.fetch_with_retry(sitemap_url)
        if xml_content and isinstance(xml_content, str):
            urls = sitemap.parse_sitemap(xml_content)
            if urls:
                filtered = [u for u in urls if filter_module.is_relevant_url(u)]
                discovered_urls.update(filtered)

    # Fallback to crawler if no sitemap
    if not discovered_urls:
        if verbose:
            typer.echo("No sitemap found, using crawler...")
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

    for i, page_url in enumerate(urls_to_sync):
        if verbose:
            typer.echo(f"[{i + 1}/{len(urls_to_sync)}] Syncing: {page_url}")

        # Check robots.txt before fetching (use sitemap domain if available)
        if not is_allowed_by_robots(page_url, domain=sitemap_domain):
            if verbose:
                typer.echo(f"  Skipping (disallowed by robots.txt): {page_url}")
            fail_count += 1
            continue

        # Fetch the page
        try:
            response = fetch_with_retry(page_url)
            if response and isinstance(response, str):
                parsed = urlparse(page_url)
                path = parsed.path.lstrip("/")
                if not path or path.endswith("/"):
                    path = path + "index.html"

                # Sanitize filename
                filename = quote(path, safe="")
                if len(filename) > 200:
                    filename = filename[:200]

                page_file = pages_dir / filename
                page_file.parent.mkdir(parents=True, exist_ok=True)
                page_file.write_text(response, encoding="utf-8")
                success_count += 1
            else:
                fail_count += 1
        except Exception:
            fail_count += 1

    # Save metadata
    _save_metadata(sync_dir, resolved_url, success_count)

    # Summary
    typer.echo("\nSync complete!")
    typer.echo(f"  Success: {success_count} pages")
    typer.echo(f"  Failed: {fail_count} pages")
    typer.echo(f"  Saved to: {sync_dir}")
