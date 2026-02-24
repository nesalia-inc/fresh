"""Alias commands for managing library aliases."""

from __future__ import annotations

import json

import typer

from ..config import (
    BUILTIN_ALIASES,
    get_user_aliases_path,
    load_aliases,
    save_aliases,
    search_aliases,
)

alias_app = typer.Typer(help="Manage library aliases")


@alias_app.command("list")
def list_aliases(
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all aliases including built-in ones",
    ),
) -> None:
    """List all available aliases."""
    user_path = get_user_aliases_path()

    if show_all:
        aliases = load_aliases()
        is_user = False
    else:
        # Show only user aliases
        if user_path.exists():
            try:
                with open(user_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    aliases = data.get("aliases", {})
            except (json.JSONDecodeError, IOError):
                aliases = {}
        else:
            aliases = {}
        is_user = True

    if not aliases:
        if is_user:
            typer.echo("No user aliases found. Use --all to see built-in aliases.")
        else:
            typer.echo("No aliases found.")
        return

    # Display in table format
    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title="Available Aliases" + (" (User)" if is_user else " (All)"))

        table.add_column("Alias", style="cyan", no_wrap=True)
        table.add_column("URL", style="green")

        for alias, url in sorted(aliases.items()):
            table.add_row(alias, url)

        console.print(table)
        typer.echo(f"\nTotal: {len(aliases)} aliases")
    except ImportError:
        # Fallback to simple output
        for alias, url in sorted(aliases.items()):
            typer.echo(f"{alias}: {url}")


@alias_app.command()
def add(
    alias: str = typer.Argument(..., help="Alias name"),
    url: str = typer.Argument(..., help="Documentation URL"),
) -> None:
    """Add a new alias."""
    # Validate URL
    if not url.startswith(("http://", "https://")):
        typer.echo("Error: URL must start with http:// or https://", err=True)
        raise typer.Exit(1)

    # Check if it's a built-in alias
    if alias in BUILTIN_ALIASES:
        typer.echo(
            f"Warning: '{alias}' is a built-in alias. "
            "Adding a user alias will override it locally.",
            err=True,
        )

    # Load existing aliases
    aliases = load_aliases()

    # Add the new alias
    old_url = aliases.get(alias)
    aliases[alias] = url
    save_aliases(aliases)

    if old_url:
        typer.echo(f"Updated alias '{alias}': {old_url} -> {url}")
    else:
        typer.echo(f"Added alias '{alias}' -> {url}")


@alias_app.command()
def remove(alias: str = typer.Argument(..., help="Alias to remove")) -> None:
    """Remove an alias."""
    aliases = load_aliases()

    if alias not in aliases:
        if alias in BUILTIN_ALIASES:
            typer.echo(
                f"Alias '{alias}' is built-in and cannot be removed. "
                "It will still work but uses the built-in URL."
            )
        else:
            typer.echo(f"Alias '{alias}' not found.")
        raise typer.Exit(1)

    # Check if it's a built-in
    if alias in BUILTIN_ALIASES:
        # Remove from user aliases (will fall back to built-in)
        del aliases[alias]
        save_aliases(aliases)
        typer.echo(f"Removed user alias '{alias}' (will use built-in)")
    else:
        del aliases[alias]
        save_aliases(aliases)
        typer.echo(f"Removed alias '{alias}'")


@alias_app.command()
def search(query: str = typer.Argument(..., help="Search query")) -> None:
    """Search for aliases."""
    results = search_aliases(query)

    if not results:
        typer.echo(f"No aliases found matching '{query}'")
        raise typer.Exit(1)

    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title=f"Aliases matching '{query}'")

        table.add_column("Alias", style="cyan", no_wrap=True)
        table.add_column("URL", style="green")

        for alias, url in results:
            table.add_row(alias, url)

        console.print(table)
        typer.echo(f"\nFound {len(results)} matching aliases")
    except ImportError:
        # Fallback to simple output
        for alias, url in results:
            typer.echo(f"{alias}: {url}")
