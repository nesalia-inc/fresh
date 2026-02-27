"""Loading indicators and progress UI components."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Callable, Generator, TypeVar

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

T = TypeVar("T")


def _is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


# Unicode-safe symbols (use ASCII alternatives on Windows)
if _is_windows():
    CHECK_MARK = "[OK]"
    CROSS_MARK = "[X]"
    INFO_MARK = "[i]"
else:
    CHECK_MARK = "✓"
    CROSS_MARK = "✗"
    INFO_MARK = "ℹ"


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


def run_with_progress(
    description: str,
    func: Callable[[], T],
    verbose_message: str | None = None,
    verbose: bool = False,
) -> T:
    """Run a function with appropriate progress indication.

    Args:
        description: Description to show in interactive spinner
        func: Function to execute
        verbose_message: Message to show in verbose mode
        verbose: Whether verbose mode is enabled

    Returns:
        The result of func()
    """
    if verbose and verbose_message:
        console.print(verbose_message)
        return func()

    if is_interactive():
        with spinner(description):
            return func()

    return func()


def show_error_message(message: str) -> None:
    """Show an error message."""
    err_console = Console(stderr=True)
    err_console.print(f"[red]{CROSS_MARK}[/red] {message}")


def show_info_message(message: str) -> None:
    """Show an info message."""
    console.print(f"[blue]{INFO_MARK}[/blue] {message}")


def show_success_message(message: str) -> None:
    """Show a success message."""
    console.print(f"[green]{CHECK_MARK}[/green] {message}")
