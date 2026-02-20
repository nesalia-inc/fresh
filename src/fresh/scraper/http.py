"""HTTP client for scraping."""

from __future__ import annotations

import atexit
import logging
import time
from typing import Any

import httpx

DEFAULT_HEADERS = {
    "User-Agent": "fresh/0.1.0 (https://fresh.nesalia.com)",
}

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)

logger = logging.getLogger(__name__)

_client: httpx.Client | None = None


def get_client() -> httpx.Client:
    """Get or create the shared HTTP client."""
    global _client
    if _client is None:
        _client = httpx.Client(
            headers=DEFAULT_HEADERS,
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
        )
    return _client


def fetch(url: str, **kwargs: Any) -> httpx.Response | None:
    """
    Fetch a URL with default configuration.

    Args:
        url: The URL to fetch
        **kwargs: Additional arguments to pass to httpx.Client.get

    Returns:
        Response object or None on failure
    """
    client = get_client()
    try:
        response = client.get(url, **kwargs)
        response.raise_for_status()
        return response
    except httpx.HTTPError as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def fetch_with_retry(
    url: str,
    max_retries: int = 3,
    backoff: float = 1.0,
    **kwargs: Any,
) -> str | None:
    """
    Fetch a URL with exponential backoff retry.

    Args:
        url: The URL to fetch
        max_retries: Maximum number of retry attempts
        backoff: Initial backoff time in seconds
        **kwargs: Additional arguments to pass to httpx.Client.get

    Returns:
        Response text content or None on failure
    """
    client = get_client()

    for attempt in range(max_retries):
        try:
            response = client.get(url, **kwargs)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            if attempt < max_retries - 1:
                wait_time = backoff * (2**attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed for {url}. "
                    f"Retrying in {wait_time}s: {e}",
                )
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} attempts failed for {url}: {e}")

    return None


def close() -> None:
    """Close the HTTP client."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


# Register cleanup handler for automatic cleanup on exit
atexit.register(close)
