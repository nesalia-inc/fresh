"""Signal handling for graceful shutdown."""

from __future__ import annotations

import atexit
import signal
import sys
from typing import Any, Callable

# Global state for shutdown handling
_shutdown_callbacks: list[Callable[[], None]] = []
_interrupted = False


def register_shutdown_callback(callback: Callable[[], None]) -> None:
    """
    Register a callback to be called during graceful shutdown.

    Args:
        callback: Function to call during shutdown
    """
    _shutdown_callbacks.append(callback)


def _signal_handler(signum: int, frame: Any) -> None:
    """Handle interrupt signal for graceful shutdown."""
    global _interrupted
    _interrupted = True

    print("\nReceived interrupt (Ctrl+C) - Shutting down gracefully...")

    # Call registered callbacks in reverse order
    for callback in reversed(_shutdown_callbacks):
        try:
            callback()
        except Exception:
            pass  # Ignore errors during shutdown

    print("Shutdown complete.")
    sys.exit(0)


def is_interrupted() -> bool:
    """Check if the application was interrupted."""
    return _interrupted


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""
    # Register signal handlers
    signal.signal(signal.SIGINT, _signal_handler)

    # Also handle SIGTERM for container environments
    signal.signal(signal.SIGTERM, _signal_handler)


# Set up signal handlers when module is imported
setup_signal_handlers()


def cleanup() -> None:
    """Clean up resources on exit."""
    # Call registered callbacks
    for callback in reversed(_shutdown_callbacks):
        try:
            callback()
        except Exception:
            pass


# Register cleanup handler
atexit.register(cleanup)
