"""Websearch command - Search the web for general queries."""

from __future__ import annotations

import json
import sys

import typer
from rich.console import Console
from rich.table import Table

from ..scraper import websearch as websearch_module
from ..ui import _is_windows

app = typer.Typer(help="Search the web for general queries.")

# Initialize console with Windows-safe settings
try:
    console = Console(no_color=_is_windows(), force_terminal=None)
except Exception:
    console = Console(file=sys.stdout, no_color=True, force_terminal=False)


@app.command()
def websearch(
    query: str = typer.Argument(..., help="The search query"),
    count: int = typer.Option(10, "--count", "-n", help="Maximum number of results"),
    engine: str = typer.Option("auto", "--engine", "-e", help="Search engine: auto, ddg, brave"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output results as JSON"),
    table_output: bool = typer.Option(False, "--table", "-t", help="Output results as table"),
) -> None:
    """Search the web for general queries.

    Results can be used with 'fresh get <url>' to fetch content as Markdown.
    """
    try:
        results = websearch_module.websearch(
            query=query,
            count=count,
            engine=engine,
        )
    except Exception as e:
        typer.echo(f"Search error: {e}", err=True)
        raise typer.Exit(1)

    # No results
    if not results:
        typer.echo("No results found.")
        return

    # Output
    if table_output or not json_output:
        # Table output
        table = Table(title=f"Web Search Results: {query}")
        table.add_column("Title", style="cyan")
        table.add_column("URL", style="dim")
        table.add_column("Description", style="green")

        for r in results:
            # Truncate description for table
            desc = r.description[:80] if len(r.description) > 80 else r.description
            if r.description and len(r.description) > 80:
                desc += "..."

            # Truncate URL for display
            url = r.url
            if len(url) > 50:
                url = "..." + url[-47:]

            table.add_row(r.title, url, desc)

        console.print(table)

    if json_output or not table_output:
        # JSON output
        output = [r.to_dict() for r in results]
        typer.echo(json.dumps(output, indent=2))


# Export for main app
__all__ = ["websearch", "websearch_app"]
websearch_app = app
