"""Console output utilities for user-facing messages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import typer

# Global state for tracking errors and warnings
_console_state: dict[str, Any] = {
    "errors": [],
    "warnings": [],
    "verbose": False,
}


def set_verbose(verbose: bool) -> None:
    """Set verbose mode globally."""
    _console_state["verbose"] = verbose


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return bool(_console_state["verbose"])


def reset_console() -> None:
    """Reset console state (for testing)."""
    _console_state["errors"] = []
    _console_state["warnings"] = []


@dataclass
class ErrorMessage:
    """Represents an error message with context."""

    message: str
    url: str | None = None
    code: str | None = None
    suggestions: list[str] = field(default_factory=list)
    details: str | None = None


@dataclass
class WarningMessage:
    """Represents a warning message."""

    message: str
    url: str | None = None
    count: int | None = None
    suggestions: list[str] = field(default_factory=list)


def echo_error(
    message: str,
    url: str | None = None,
    code: str | None = None,
    suggestions: list[str] | None = None,
    details: str | None = None,
    verbose_only: bool = False,
) -> None:
    """
    Echo an error message to the user.

    Args:
        message: The error message
        url: Optional URL related to the error
        code: Optional error code
        suggestions: Optional list of suggestions
        details: Optional detailed information
        verbose_only: If True, only show in verbose mode
    """
    # Always show errors unless verbose_only is explicitly set
    if verbose_only and not is_verbose():
        return

    error = ErrorMessage(
        message=message,
        url=url,
        code=code,
        suggestions=suggestions or [],
        details=details,
    )
    _console_state["errors"].append(error)

    # Format error message
    full_msg = f"Error: {message}"

    if url:
        full_msg = f"Error: {message}\n  URL: {url}"

    if details and is_verbose():
        full_msg += f"\n  Details: {details}"

    if code:
        full_msg += f"\n  Code: {code}"

    if suggestions:
        full_msg += "\nSuggestions:"
        for suggestion in suggestions:
            full_msg += f"\n  - {suggestion}"

    typer.echo(full_msg, err=True)


def echo_warning(
    message: str,
    url: str | None = None,
    count: int | None = None,
    verbose_only: bool = False,
    suggestions: list[str] | None = None,
) -> None:
    """
    Echo a warning message to the user.

    Args:
        message: The warning message
        url: Optional URL related to the warning
        count: Optional count of items
        verbose_only: If True, only show in verbose mode
        suggestions: Optional list of suggestions
    """
    # Show warnings in verbose mode, or summary at end in non-verbose
    if verbose_only and not is_verbose():
        return

    warning = WarningMessage(message=message, url=url, count=count, suggestions=suggestions or [])
    _console_state["warnings"].append(warning)

    # Always show warnings (unless verbose_only is set)
    full_msg = f"Warning: {message}"
    if url:
        full_msg += f"\n  URL: {url}"
    if count:
        full_msg += f"\n  Count: {count}"
    if is_verbose() and suggestions:
        full_msg += "\nSuggestions:"
        for suggestion in suggestions:
            full_msg += f"\n  - {suggestion}"
    typer.echo(full_msg, err=True)


def echo_success(message: str) -> None:
    """Echo a success message."""
    typer.echo(f"Success: {message}")


def echo_info(message: str, verbose_only: bool = False) -> None:
    """
    Echo an info message.

    Args:
        message: The info message
        verbose_only: If True, only show in verbose mode
    """
    if verbose_only and not is_verbose():
        return
    typer.echo(message)


def print_summary() -> None:
    """Print a summary of errors and warnings at the end."""
    errors = _console_state["errors"]
    warnings = _console_state["warnings"]

    if not errors and not warnings:
        return

    typer.echo("\n--- Summary ---", err=True)

    if warnings:
        typer.echo(f"Warnings: {len(warnings)}", err=True)

    if errors:
        typer.echo(f"Errors: {len(errors)}", err=True)

    # Show error details in non-verbose mode
    if not is_verbose() and errors:
        typer.echo("\nUse --verbose for more details", err=True)


def get_error_count() -> int:
    """Get the number of errors recorded."""
    return len(_console_state["errors"])


def get_warning_count() -> int:
    """Get the number of warnings recorded."""
    return len(_console_state["warnings"])


def has_errors() -> bool:
    """Check if there are any errors."""
    return len(_console_state["errors"]) > 0
