"""History command - track and view search and access history."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..console import echo_error, print_summary
from ..ui import _is_windows

history_app = typer.Typer(help="View and manage search history.")


def _create_console() -> Console:
    """Create a Console with Windows-safe settings."""
    try:
        return Console(no_color=_is_windows(), force_terminal=None)
    except Exception:
        return Console(file=sys.stdout, no_color=True, force_terminal=False)


@history_app.command()
def history(
    query: str | None = typer.Argument(None, help="Search query to filter history"),
    url: str | None = typer.Option(None, "--url", "-u", help="Filter by URL"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output"),
    access: bool = typer.Option(False, "--access", "-a", help="Show access history instead of search history"),
) -> None:
    """View search history.

    Examples:
        fresh history                    # Show recent searches
        fresh history "react"             # Search within history
        fresh history --url react.dev     # Filter by URL
        fresh history --access           # Show page access history
    """
    try:
        from .. import history as history_module
    except ImportError:
        echo_error(
            message="History module not available",
            code="IMPORT_ERROR",
        )
        raise typer.Exit(1)

    if access:
        # Show access history
        records = history_module.get_access_history(limit=limit, url=url or query)
        if not records:
            typer.echo("No access history found.")
            return

        console = _create_console()
        table = Table(title="Access History")
        table.add_column("Time", style="cyan")
        table.add_column("Page", style="green")
        table.add_column("Method", style="yellow")

        for record in records:
            timestamp = record.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                age = _format_age(dt)
            except Exception:
                age = timestamp

            page = record.get("page_path", "")
            method = record.get("method", "search")

            table.add_row(age, page, method)

        console.print(table)
    else:
        # Show search history
        records = history_module.get_search_history(limit=limit, query=query, url=url)

        if not records:
            typer.echo("No search history found.")
            return

        console = _create_console()

        if verbose:
            table = Table(title="Search History")
            table.add_column("Time", style="cyan")
            table.add_column("Query", style="green")
            table.add_column("URL", style="blue")
            table.add_column("Results", style="yellow")
            table.add_column("Status", style="magenta")

            for record in records:
                timestamp = record.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    age = _format_age(dt)
                except Exception:
                    age = timestamp

                query_text = record.get("query", "")
                url_text = record.get("url", "")
                results = record.get("results_count", 0)
                success = "OK" if record.get("success") else "FAIL"

                table.add_row(age, query_text, url_text, str(results), success)

            console.print(table)
        else:
            # Simple list format
            for i, record in enumerate(records, 1):
                timestamp = record.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    age = _format_age(dt)
                except Exception:
                    age = timestamp

                query_text = record.get("query", "")
                url_text = record.get("url", "")
                results = record.get("results_count", 0)
                success = "OK" if record.get("success") else "FAIL"

                typer.echo(f"{i}. \"{query_text}\" on {url_text} ({results} results, {age}) {success}")

    # Print summary
    print_summary()


def _format_age(dt: datetime) -> str:
    """Format datetime as relative age."""
    now = datetime.now(timezone.utc)
    diff = now - dt

    if diff.total_seconds() < 60:
        return f"{int(diff.total_seconds())}s ago"
    elif diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds() / 60)}m ago"
    elif diff.days < 1:
        return f"{int(diff.total_seconds() / 3600)}h ago"
    elif diff.days < 30:
        return f"{diff.days}d ago"
    elif diff.days < 365:
        return f"{diff.days // 30}mo ago"
    else:
        return f"{diff.days // 365}y ago"


@history_app.command(name="clear")
def clear_history(
    url: str | None = typer.Argument(None, help="Clear history for specific URL"),
    older_than: int | None = typer.Option(None, "--older-than", help="Clear entries older than N days"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Clear search history.

    Examples:
        fresh history clear              # Clear all history
        fresh history clear react.dev     # Clear for specific URL
        fresh history clear --older-than 30  # Clear entries older than 30 days
    """
    try:
        from .. import history as history_module
    except ImportError:
        echo_error(
            message="History module not available",
            code="IMPORT_ERROR",
        )
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(
            f"Clear history{' for ' + url if url else ''}"
            f"{' older than ' + str(older_than) + ' days' if older_than else ''}?",
        )
        if not confirm:
            typer.echo("Cancelled.")
            return

    count = history_module.clear_history(url=url, older_than_days=older_than)
    typer.echo(f"Cleared {count} record(s).")


@history_app.command(name="stats")
def history_stats() -> None:
    """Show history statistics."""
    try:
        from .. import history as history_module
    except ImportError:
        echo_error(
            message="History module not available",
            code="IMPORT_ERROR",
        )
        raise typer.Exit(1)

    stats = history_module.get_history_stats()

    console = _create_console()
    table = Table(title="History Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green", justify="right")

    table.add_row("Search queries", str(stats["search_count"]))
    table.add_row("Page accesses", str(stats["access_count"]))
    table.add_row("Unique URLs", str(stats["unique_urls"]))

    console.print(table)


@history_app.command(name="export")
def export_history(
    file: Path = typer.Argument(..., help="Output file path"),
) -> None:
    """Export history to a JSON file.

    Example:
        fresh history export history.json
    """
    try:
        from .. import history as history_module
    except ImportError:
        echo_error(
            message="History module not available",
            code="IMPORT_ERROR",
        )
        raise typer.Exit(1)

    history_module.export_history(file)
    typer.echo(f"History exported to {file}")


@history_app.command(name="import")
def import_history(
    file: Path = typer.Argument(..., help="Input file path"),
) -> None:
    """Import history from a JSON file.

    Example:
        fresh history import history.json
    """
    try:
        from .. import history as history_module
    except ImportError:
        echo_error(
            message="History module not available",
            code="IMPORT_ERROR",
        )
        raise typer.Exit(1)

    if not file.exists():
        echo_error(
            message=f"File not found: {file}",
            code="FILE_NOT_FOUND",
        )
        raise typer.Exit(1)

    count = history_module.import_history(file)
    typer.echo(f"Imported {count} record(s).")
