"""Guide commands for creating and managing persistent documentation guides."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

guide_app = typer.Typer(help="Create and manage persistent documentation guides")


def _is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def _create_console() -> Console:
    """Create a Console with Windows-safe settings."""
    try:
        return Console(no_color=_is_windows(), force_terminal=None)
    except Exception:
        return Console(file=sys.stdout, no_color=True, force_terminal=False)

GUIDES_DIR = Path.home() / ".fresh" / "guides"


def _get_guides_dir() -> Path:
    """Get the guides directory, creating it if needed."""
    guides_dir = GUIDES_DIR
    guides_dir.mkdir(parents=True, exist_ok=True)
    return guides_dir


def _load_guide(name: str) -> dict[str, Any] | None:
    """Load a guide by name."""
    guide_file = _get_guides_dir() / f"{name}.json"
    if not guide_file.exists():
        return None
    try:
        with open(guide_file, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
            return data
    except (json.JSONDecodeError, IOError):
        return None


def _save_guide(name: str, guide: dict[str, Any]) -> None:
    """Save a guide."""
    guide_file = _get_guides_dir() / f"{name}.json"
    with open(guide_file, "w", encoding="utf-8") as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)


def _delete_guide(name: str) -> bool:
    """Delete a guide. Returns True if deleted, False if not found."""
    guide_file = _get_guides_dir() / f"{name}.json"
    if guide_file.exists():
        guide_file.unlink()
        return True
    return False


def _list_guides() -> list[tuple[str, dict[str, Any]]]:
    """List all guides with their metadata."""
    guides = []
    guides_dir = _get_guides_dir()
    for guide_file in guides_dir.glob("*.json"):
        try:
            with open(guide_file, "r", encoding="utf-8") as f:
                guide = json.load(f)
                name = guide_file.stem
                guides.append((name, guide))
        except (json.JSONDecodeError, IOError):
            continue
    return sorted(guides, key=lambda x: x[0])


def _format_age(timestamp: str) -> str:
    """Format a timestamp as relative age."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = now - dt

        if delta.total_seconds() < 60:
            return "just now"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = int(delta.total_seconds() / 86400)
            return f"{days}d ago"
    except (ValueError, TypeError):
        return "unknown"


@guide_app.command("create")
def create_guide(
    name: str = typer.Argument(..., help="Guide name"),
    content: str = typer.Option(..., "--content", "-c", help="Guide content (markdown)"),
    title: str | None = typer.Option(None, "--title", "-t", help="Guide title (defaults to name)"),
    source_url: str | None = typer.Option(None, "--source-url", "-u", help="Source URL where content came from"),
    tags: str | None = typer.Option(None, "--tags", help="Comma-separated tags"),
) -> None:
    """Create a new guide."""
    # Check if guide already exists
    existing = _load_guide(name)
    now = datetime.now(timezone.utc).isoformat()

    guide: dict[str, Any] = {
        "title": title or name,
        "created": now,
        "updated": now,
        "content": content,
    }

    if source_url:
        guide["source_url"] = source_url
    if tags:
        guide["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]

    if existing:
        # Update existing
        guide["created"] = existing.get("created", now)
        _save_guide(name, guide)
        typer.echo(f"Updated guide '{name}'")
    else:
        _save_guide(name, guide)
        typer.echo(f"Created guide '{name}'")


@guide_app.command("list")
def list_guides() -> None:
    """List all guides."""
    guides = _list_guides()

    if not guides:
        typer.echo("No guides found. Use 'fresh guide create' to create one.")
        return

    console = _create_console()
    table = Table(title="Guides")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Title", style="green")
    table.add_column("Created", style="yellow")
    table.add_column("Updated", style="blue")

    for name, guide in guides:
        created = _format_age(guide.get("created", ""))
        updated = _format_age(guide.get("updated", ""))
        title = guide.get("title", name)
        table.add_row(name, title, created, updated)

    console.print(table)


@guide_app.command("show")
def show_guide(name: str = typer.Argument(..., help="Guide name to show")) -> None:
    """Show a guide's content."""
    guide = _load_guide(name)

    if not guide:
        typer.echo(f"Guide '{name}' not found.", err=True)
        raise typer.Exit(1)

    content = guide.get("content", "")
    typer.echo(content)

    # Show metadata
    if source_url := guide.get("source_url"):
        typer.echo(f"\nSource: {source_url}")
    if tags := guide.get("tags"):
        typer.echo(f"Tags: {', '.join(tags)}")


@guide_app.command("delete")
def delete_guide(name: str = typer.Argument(..., help="Guide name to delete")) -> None:
    """Delete a guide."""
    if _delete_guide(name):
        typer.echo(f"Deleted guide '{name}'")
    else:
        typer.echo(f"Guide '{name}' not found.", err=True)
        raise typer.Exit(1)


@guide_app.command()
def search(query: str = typer.Argument(..., help="Search query")) -> None:
    """Search guides by name, title, or content."""
    guides = _list_guides()
    results = []

    query_lower = query.lower()
    for name, guide in guides:
        # Search in name, title, content, and tags
        if query_lower in name.lower():
            results.append((name, guide, "name"))
        elif query_lower in guide.get("title", "").lower():
            results.append((name, guide, "title"))
        elif query_lower in guide.get("content", "").lower():
            results.append((name, guide, "content"))
        elif any(query_lower in tag.lower() for tag in guide.get("tags", [])):
            results.append((name, guide, "tag"))

    if not results:
        typer.echo(f"No guides found matching '{query}'")
        raise typer.Exit(1)

    console = _create_console()
    table = Table(title=f"Guides matching '{query}'")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Title", style="green")
    table.add_column("Match", style="yellow")

    for name, guide, match_type in results:
        title = guide.get("title", name)
        table.add_row(name, title, match_type)

    console.print(table)
    typer.echo(f"\nFound {len(results)} matching guides")
