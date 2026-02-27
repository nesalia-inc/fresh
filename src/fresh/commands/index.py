"""Index commands for managing search indexes."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..indexer import (
    DEFAULT_INDEX_DIR,
    build_index_from_directory,
    delete_index,
    get_index_age,
    get_index_stats,
    rebuild_index,
)
from .search import DEFAULT_SYNC_DIR, _get_sync_dir_for_url

index_app = typer.Typer(help="Manage search indexes for fast local search.")


def _is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def _create_console() -> Console:
    """Create a Console with Windows-safe settings."""
    try:
        return Console(no_color=_is_windows(), force_terminal=None)
    except Exception:
        return Console(file=sys.stdout, no_color=True, force_terminal=False)


def _get_site_name(url: str) -> str:
    """Extract site name from URL."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return parsed.netloc.replace(":", "_").replace(".", "_")


@index_app.command("build")
def build_index(
    site: str = typer.Argument(..., help="Site name or URL to build index for"),
    pages_dir: str | None = typer.Option(
        None,
        "--pages-dir",
        "-d",
        help="Directory containing HTML pages (defaults to synced docs)",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force rebuild if index exists"),
) -> None:
    """Build or update the search index for a site."""

    # Determine site name and pages directory
    if "://" in site:
        site_name = _get_site_name(site)
        if not pages_dir:
            pages_dir = str(_get_sync_dir_for_url(site) / "pages")
    else:
        site_name = site
        if not pages_dir:
            pages_dir = str(DEFAULT_SYNC_DIR / site_name / "pages")

    pages_path = Path(pages_dir)

    if not pages_path.exists():
        typer.echo(f"Pages directory not found: {pages_path}", err=True)
        raise typer.Exit(1)

    # Check if index exists
    if not force:
        age = get_index_age(site_name)
        if age:
            typer.echo(f"Index already exists for {site_name}. Use --force to rebuild.")
            raise typer.Exit(1)

    typer.echo(f"Building index for {site_name}...")

    # Count HTML files
    html_count = len(list(pages_path.rglob("*.html")))
    if html_count == 0:
        typer.echo(f"No HTML files found in {pages_path}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Found {html_count} HTML files. Indexing...")

    count = build_index_from_directory(site_name, pages_path)

    typer.echo(f"Successfully indexed {count} pages.")


@index_app.command("rebuild")
def rebuild_index_cmd(
    site: str = typer.Argument(..., help="Site name or URL to rebuild index for"),
    pages_dir: str | None = typer.Option(
        None,
        "--pages-dir",
        "-d",
        help="Directory containing HTML pages",
    ),
) -> None:
    """Rebuild the search index for a site (deletes existing index first)."""

    # Determine site name and pages directory
    if "://" in site:
        site_name = _get_site_name(site)
        if not pages_dir:
            pages_dir = str(_get_sync_dir_for_url(site) / "pages")
    else:
        site_name = site
        if not pages_dir:
            pages_dir = str(DEFAULT_SYNC_DIR / site_name / "pages")

    pages_path = Path(pages_dir)

    if not pages_path.exists():
        typer.echo(f"Pages directory not found: {pages_path}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Rebuilding index for {site_name}...")

    count = rebuild_index(site_name, pages_path)

    typer.echo(f"Successfully rebuilt index with {count} pages.")


@index_app.command("status")
def index_status(
    site: str | None = typer.Argument(None, help="Site name to check (all if not specified)"),
) -> None:
    """Show the status of search indexes."""
    console = _create_console()

    index_dir = DEFAULT_INDEX_DIR
    if not index_dir.exists():
        typer.echo("No indexes found. Run 'fresh index build' to create one.")
        return

    # Find all index databases
    db_files = list(index_dir.glob("*.db"))

    if not db_files:
        typer.echo("No indexes found. Run 'fresh index build' to create one.")
        return

    # Filter by site if specified
    if site:
        db_files = [f for f in db_files if f.stem == site]

    if not db_files:
        typer.echo(f"No index found for {site}.")
        return

    # Display table
    table = Table(title="Search Indexes")
    table.add_column("Site", style="cyan", no_wrap=True)
    table.add_column("Pages", style="green")
    table.add_column("Last Updated", style="yellow")
    table.add_column("Location", style="blue")

    for db_file in db_files:
        stats = get_index_stats(db_file.stem)
        if stats:
            from datetime import datetime, timezone

            age_str = "unknown"
            if stats["last_updated"]:
                try:
                    dt = datetime.fromisoformat(stats["last_updated"])
                    now = datetime.now(timezone.utc)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    delta = now - dt

                    if delta.days > 0:
                        age_str = f"{delta.days} days ago"
                    elif delta.seconds // 3600 > 0:
                        age_str = f"{delta.seconds // 3600} hours ago"
                    elif delta.seconds // 60 > 0:
                        age_str = f"{delta.seconds // 60} minutes ago"
                    else:
                        age_str = "just now"
                except Exception:
                    pass

            table.add_row(
                stats["site_name"],
                str(stats["page_count"]),
                age_str,
                stats["db_path"],
            )

    console.print(table)


@index_app.command("delete")
def delete_index_cmd(
    site: str = typer.Argument(..., help="Site name to delete index for"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete the search index for a site."""
    if not force:
        confirm = typer.confirm(f"Delete index for {site}?")
        if not confirm:
            typer.echo("Cancelled.")
            return

    if delete_index(site):
        typer.echo(f"Deleted index for {site}.")
    else:
        typer.echo(f"No index found for {site}.", err=True)
        raise typer.Exit(1)


@index_app.command("search")
def search_index_cmd(
    site: str = typer.Argument(..., help="Site name to search"),
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "--limit", "-n", help="Maximum number of results"),
) -> None:
    """Search the index directly (for testing)."""
    console = _create_console()

    results = get_index_stats(site)
    if not results:
        typer.echo(f"No index found for {site}. Run 'fresh index build' first.", err=True)
        raise typer.Exit(1)

    from ..indexer import search_index as search_index_func

    search_results = search_index_func(site, query, limit)

    if not search_results:
        typer.echo("No results found.")
        return

    table = Table(title=f"Search results for '{query}'")
    table.add_column("URL", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Snippet", style="yellow")

    for result in search_results:
        table.add_row(
            result["url"],
            result["title"],
            result["snippet"][:100] + "..." if len(result.get("snippet", "")) > 100 else result.get("snippet", ""),
        )

    console.print(table)
    typer.echo(f"\nFound {len(search_results)} results.")
