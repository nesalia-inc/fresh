"""Loading indicators and progress UI components."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def is_interactive() -> bool:
    """Check if stdout is interactive (TTY)."""
    return sys.stdout.isatty()


@contextmanager
def spinner(description: str) -> Generator[None, None, None]:
    """Show a spinner with the given description.

    Usage:
        with spinner("Fetching page..."):
            # do work here
            pass
    """
    if not is_interactive():
        yield
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description, total=None)
        yield


def show_error_message(message: str) -> None:
    """Show an error message."""
    err_console = Console(stderr=True)
    err_console.print(f"[red]✗[/red] {message}")


def show_info_message(message: str) -> None:
    """Show an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")
