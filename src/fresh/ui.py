"""Loading indicators and progress UI components."""

from __future__ import annotations

import sys

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def is_interactive() -> bool:
    """Check if stdout is interactive (TTY)."""
    return sys.stdout.isatty()


def show_fetching_spinner(url: str) -> None:
    """Show a spinner while fetching a URL."""
    if not is_interactive():
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(f"Fetching {url}...", total=None)
        # The actual work is done in the calling function
        # This just shows the spinner during the fetch


def show_loading_message(message: str, end: str = "\n") -> None:
    """Show a loading message if in interactive mode."""
    if is_interactive():
        console.print(message, end=end)


def show_success_message(message: str) -> None:
    """Show a success message."""
    console.print(f"[green]✓[/green] {message}")


def show_error_message(message: str) -> None:
    """Show an error message."""
    from rich.console import Console
    err_console = Console(stderr=True)
    err_console.print(f"[red]✗[/red] {message}")


def show_info_message(message: str) -> None:
    """Show an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def show_warning_message(message: str) -> None:
    """Show a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")
