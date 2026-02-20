"""HTTP client for scraping."""

from __future__ import annotations

import atexit
import ipaddress
import logging
import re
import threading
import time
import urllib.parse
from typing import Any

import httpx

DEFAULT_HEADERS = {
    "User-Agent": "fresh/0.1.0 (https://fresh.nesalia.com)",
}

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)

logger = logging.getLogger(__name__)

_client: httpx.Client | None = None
_client_lock = threading.Lock()


def _is_private_ip(hostname: str) -> bool:
    """Check if hostname is a private or reserved IP address.

    Args:
        hostname: The hostname or IP to check

    Returns:
        True if the IP is private/reserved, False otherwise
    """
    try:
        ip = ipaddress.ip_address(hostname)
        # Check if IP is private, reserved, or loopback
        return ip.is_private or ip.is_reserved or ip.is_loopback
    except ValueError:
        # Not an IP address (probably a domain name)
        return False


def validate_url(url: str, allowed_domains: list[str] | None = None) -> bool:
    """
    Validate URL for security (SSRF prevention).

    Args:
        url: The URL to validate
        allowed_domains: Optional list of allowed domains

    Returns:
        True if URL is valid, False otherwise
    """
    try:
        parsed = urllib.parse.urlparse(url)

        # Only allow http and https schemes
        if parsed.scheme not in ("http", "https"):
            logger.warning(f"URL scheme not allowed: {parsed.scheme}")
            return False

        # Check allowed domains if specified
        if allowed_domains and parsed.netloc not in allowed_domains:
            logger.warning(f"Domain not in allowed list: {parsed.netloc}")
            return False

        # Block localhost and private IPs
        hostname = parsed.hostname or ""
        # Handle IPv6 in netloc (e.g., http://[::1]/admin or http://::1/admin)
        netloc = parsed.netloc
        if not hostname and netloc:
            # Might be IPv6 - check if netloc contains ::
            if "::" in netloc:
                # Extract IPv6 address (remove brackets if present)
                hostname = netloc.lstrip("[").rstrip("]")
            else:
                hostname = netloc.split(":")[0] if ":" in netloc else netloc
        blocked_hosts = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "::",
        ]
        # Check for IPv6 URL using proper parsing
        is_ipv6 = False
        if hostname:
            try:
                ip = ipaddress.ip_address(hostname)
                is_ipv6 = ip.version == 6
            except ValueError:
                is_ipv6 = False
        # Check for private IP ranges
        is_private_ip = _is_private_ip(hostname)
        is_localhost = (
            hostname in blocked_hosts
            or hostname.endswith(".local")
            or is_ipv6
            or is_private_ip
        )
        if is_localhost:
            logger.warning(f"Blocked localhost or private URL: {url}")
            return False

        return True
    except Exception as e:
        logger.warning(f"Failed to parse URL: {e}")
        return False


def get_client() -> httpx.Client:
    """Get or create the shared HTTP client (thread-safe)."""
    global _client
    if _client is None:
        with _client_lock:
            # Double-check after acquiring lock
            if _client is None:
                _client = httpx.Client(
                    headers=DEFAULT_HEADERS,
                    timeout=DEFAULT_TIMEOUT,
                    follow_redirects=True,
                )
    return _client


def fetch(
    url: str,
    allowed_domains: list[str] | None = None,
    **kwargs: Any,
) -> httpx.Response | None:
    """
    Fetch a URL with default configuration.

    Args:
        url: The URL to fetch
        allowed_domains: Optional list of allowed domains
        **kwargs: Additional arguments to pass to httpx.Client.get

    Returns:
        Response object or None on failure
    """
    if not validate_url(url, allowed_domains):
        return None

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
    return_response: bool = False,
    allowed_domains: list[str] | None = None,
    **kwargs: Any,
) -> str | httpx.Response | None:
    """
    Fetch a URL with exponential backoff retry.

    Args:
        url: The URL to fetch
        max_retries: Maximum number of retry attempts
        backoff: Initial backoff time in seconds
        return_response: If True, return the Response object instead of text
        allowed_domains: Optional list of allowed domains
        **kwargs: Additional arguments to pass to httpx.Client.get

    Returns:
        Response text, Response object, or None on failure
    """
    if not validate_url(url, allowed_domains):
        return None

    client = get_client()

    for attempt in range(max_retries):
        try:
            response = client.get(url, **kwargs)
            response.raise_for_status()
            if return_response:
                return response
            return response.text
        except httpx.TimeoutException as e:
            # Shorter retries for timeouts
            if attempt < max_retries - 1:
                wait_time = backoff * (2**attempt) * 0.5
                logger.warning(
                    f"Timeout on attempt {attempt + 1}/{max_retries} for {url}. "
                    f"Retrying in {wait_time}s: {e}",
                )
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} timeout attempts failed for {url}: {e}")
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
    with _client_lock:
        if _client is not None:
            _client.close()
            _client = None


class HTTPClient:
    """Thread-safe HTTP client wrapper with context manager support."""

    def __init__(self) -> None:
        """Initialize the HTTP client."""
        self._client = get_client()

    def __enter__(self) -> httpx.Client:
        """Enter context manager."""
        return self._client

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager (does not close the shared client)."""
        pass

    def get_client(self) -> httpx.Client:
        """Get the underlying httpx client."""
        return self._client


def fetch_robots_txt(base_url: str) -> str | None:
    """Fetch robots.txt for a given base URL.

    Args:
        base_url: The base URL of the website

    Returns:
        robots.txt content or None on failure
    """
    parsed = urllib.parse.urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    result = fetch_with_retry(robots_url, max_retries=1)
    if isinstance(result, str):
        return result
    return None


# Cache for robots.txt rules
_robots_cache: dict[str, tuple[float, set[str]]] = {}  # domain -> (timestamp, disallowed paths)
_robots_cache_lock = threading.Lock()
ROBOTS_CACHE_TTL = 300  # 5 minutes
ROBOTS_CACHE_MAX_SIZE = 100  # Max domains to cache


def _cleanup_robots_cache() -> None:
    """Clean up expired entries from robots cache."""
    now = time.time()
    expired = [
        domain
        for domain, (timestamp, _) in _robots_cache.items()
        if now - timestamp > ROBOTS_CACHE_TTL
    ]
    for domain in expired:
        del _robots_cache[domain]

    # If still too large, remove oldest entries
    if len(_robots_cache) > ROBOTS_CACHE_MAX_SIZE:
        sorted_domains = sorted(
            _robots_cache.keys(),
            key=lambda d: _robots_cache[d][0],
        )
        for domain in sorted_domains[: len(_robots_cache) - ROBOTS_CACHE_MAX_SIZE]:
            del _robots_cache[domain]


def is_allowed_by_robots(url: str, user_agent: str = "*") -> bool:
    """Check if a URL is allowed by robots.txt.

    Args:
        url: The URL to check
        user_agent: The user agent to check against (default: *)

    Returns:
        True if the URL is allowed, False if disallowed
    """
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc
    path = parsed.path or "/"

    disallowed_paths: set[str] = set()

    with _robots_cache_lock:
        # Periodic cleanup
        if len(_robots_cache) > ROBOTS_CACHE_MAX_SIZE:
            _cleanup_robots_cache()

        now = time.time()

        # Check cache
        if domain in _robots_cache:
            cache_time, cached_disallowed = _robots_cache[domain]
            if now - cache_time < ROBOTS_CACHE_TTL:
                # Check if path matches any disallowed pattern
                for pattern in cached_disallowed:
                    if _matches_robots_pattern(path, pattern):
                        logger.debug(f"URL {url} disallowed by robots.txt")
                        return False
                return True
            # Cache expired, remove it
            del _robots_cache[domain]

    # Fetch and parse robots.txt
    base_url = f"{parsed.scheme}://{domain}"
    robots_content = fetch_robots_txt(base_url)

    if robots_content and isinstance(robots_content, str):
        # Track which user-agent section we're in
        in_target_section = False
        user_agent_lower = user_agent.lower()

        for line in robots_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for user-agent directive - reset section when new user-agent found
            if line.lower().startswith("user-agent:"):
                agent = line.split(":", 1)[1].strip().lower()
                # Match exact user-agent or wildcard *
                in_target_section = agent == user_agent_lower or agent == "*"

            # Check for disallow only if we're in the target section
            elif line.lower().startswith("disallow:") and in_target_section:
                disallow_path = line.split(":", 1)[1].strip()
                if disallow_path:
                    disallowed_paths.add(disallow_path)

            # Reset section for other directives (crawl-delay, allow, etc.)
            else:
                in_target_section = False

    # Cache the results
    with _robots_cache_lock:
        _robots_cache[domain] = (now, disallowed_paths)

    # Check if path is disallowed
    for pattern in disallowed_paths:
        if _matches_robots_pattern(path, pattern):
            logger.debug(f"URL {url} disallowed by robots.txt (pattern: {pattern})")
            return False

    return True


def _matches_robots_pattern(path: str, pattern: str) -> bool:
    """Check if a path matches a robots.txt pattern.

    Args:
        path: The URL path
        pattern: The robots.txt pattern

    Returns:
        True if path matches pattern
    """
    if not pattern:
        return False

    # Handle $ end anchor
    if pattern.endswith("$"):
        pattern = pattern[:-1]
        return path == pattern

    # Handle * wildcard (match anything)
    if "*" in pattern:
        # Convert pattern to regex
        regex_pattern = pattern.replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}", path))

    # Simple prefix match
    return path.startswith(pattern)


# Register cleanup handler for automatic cleanup on exit
atexit.register(close)
