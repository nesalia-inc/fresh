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

# Binary file extensions to skip
BINARY_EXTENSIONS = frozenset([
    # Archive formats
    ".bz2", ".gz", ".zip", ".tar", ".7z", ".rar", ".xz",
    # Image formats
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".avif",
    # Video/audio
    ".mp4", ".webm", ".avi", ".mov", ".mp3", ".wav", ".ogg", ".flac",
    # Document formats
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    # Font formats
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    # Other binary formats
    ".bin", ".exe", ".dll", ".so", ".dylib",
])

# Binary magic bytes signatures
BINARY_MAGIC_BYTES = [
    (b"BZh", "bzip2"),           # bzip2 compressed
    (b"\x1f\x8b", "gzip"),       # gzip compressed
    (b"PK\x03\x04", "zip"),      # zip archive
    (b"PK\x05\x06", "zip"),      # zip archive (empty)
    (b"PK\x07\x08", "zip"),      # zip archive (spanned)
    (b"\x89PNG", "png"),         # PNG image
    (b"\xff\xd8\xff", "jpeg"),   # JPEG image
    (b"GIF87a", "gif"),          # GIF87a
    (b"GIF89a", "gif"),          # GIF89a
    (b"RIFF", "webp"),           # RIFF (WebP starts with RIFF....webp)
    (b"\x00\x00\x01\x00", "ico"), # ICO icon
    (b"%PDF", "pdf"),            # PDF document
    (b"\xca\xfe\xba\xbe", "java"), # Java/Mach-O class
    (b"MZ", "exe"),              # Windows executable
    (b"\x7fELF", "elf"),         # ELF executable
]


def is_binary_url(url: str) -> bool:
    """
    Check if a URL likely points to a binary file based on its path.

    Args:
        url: The URL to check

    Returns:
        True if the URL appears to point to a binary file
    """
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lower()

    # Check file extension
    for ext in BINARY_EXTENSIONS:
        if path.endswith(ext):
            return True

    return False


def is_binary_content(content: bytes | str, content_type: str | None = None) -> bool:
    """
    Check if content appears to be binary.

    This function checks:
    1. Content-Type header (if provided)
    2. File extension in the URL (if content is from a URL)
    3. Binary magic bytes in the content

    Args:
        content: The content to check (bytes or str)
        content_type: Optional Content-Type header value

    Returns:
        True if the content appears to be binary, False otherwise
    """
    # Check Content-Type header first
    if content_type:
        content_type_lower = content_type.lower()
        # Only allow text/html content types
        if not content_type_lower.startswith("text/html"):
            # Allow other text types that might be useful
            allowed_text_types = [
                "text/",
                "application/xhtml",
                "application/xml",
                "application/json",
            ]
            is_allowed_text = any(
                content_type_lower.startswith(t) for t in allowed_text_types
            )
            if not is_allowed_text:
                logger.debug(f"Skipping binary content based on Content-Type: {content_type}")
                return True

    # Convert string to bytes if needed
    if isinstance(content, str):
        try:
            content_bytes = content.encode("utf-8")
        except UnicodeEncodeError:
            # If we can't encode as UTF-8, it's likely binary
            return True
    else:
        content_bytes = content

    # Check for binary magic bytes
    # Only check the first 8 bytes (enough for all magic signatures)
    header = content_bytes[:8] if len(content_bytes) >= 8 else content_bytes

    for magic, fmt in BINARY_MAGIC_BYTES:
        if header.startswith(magic):
            logger.debug(f"Skipping binary content: detected {fmt} magic bytes")
            return True

    # Check for null bytes in the content (strong indicator of binary)
    # Sample the content - check first 1KB and also random positions
    sample_size = min(1024, len(content_bytes))
    if b"\x00" in content_bytes[:sample_size]:
        # Additional check: count null bytes ratio
        null_count = content_bytes[:sample_size].count(b"\x00")
        if null_count > sample_size * 0.1:  # More than 10% null bytes
            logger.debug("Skipping binary content: high ratio of null bytes")
            return True

    return False


def fetch_binary_aware(
    url: str,
    allowed_domains: list[str] | None = None,
    skip_binary: bool = True,
    **kwargs: Any,
) -> str | None:
    """
    Fetch a URL with binary content detection.

    This function wraps fetch_with_retry and optionally skips binary content
    based on Content-Type header or magic bytes detection.

    Args:
        url: The URL to fetch
        allowed_domains: Optional list of allowed domains
        skip_binary: If True, skip binary content (default: True)
        **kwargs: Additional arguments to pass to httpx.Client.get

    Returns:
        Response text or None on failure/binary content
    """
    if skip_binary and is_binary_url(url):
        logger.debug(f"Skipping binary URL: {url}")
        return None

    # Fetch with return_response=True so we can check Content-Type
    response = fetch_with_retry(
        url,
        allowed_domains=allowed_domains,
        return_response=True,
        **kwargs,
    )

    if response is None:
        return None

    # Type check: response should be httpx.Response when return_response=True
    if not isinstance(response, httpx.Response):
        return None

    # Check Content-Type header
    content_type = response.headers.get("Content-Type", "")
    if skip_binary and is_binary_content(response.content, content_type):
        logger.debug(f"Skipping binary content from: {url}")
        return None

    # Return text content
    try:
        return response.text
    except Exception as e:
        logger.warning(f"Failed to decode content from {url}: {e}")
        return None

_client: httpx.Client | None = None
_client_lock: threading.Lock = threading.Lock()

# Cache for robots.txt rules
_robots_cache: dict[str, tuple[float, set[str], set[str]]] = {}  # domain -> (timestamp, disallowed, allowed)
_robots_cache_lock: threading.Lock = threading.Lock()
ROBOTS_CACHE_TTL = 300  # 5 minutes
ROBOTS_CACHE_MAX_SIZE = 100  # Max domains to cache
_robots_request_counter = 0
_ROBOTS_CLEANUP_INTERVAL = 100  # Cleanup every 100 requests


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


# Maximum URL length to prevent DoS
MAX_URL_LENGTH = 2048


def validate_url(url: str, allowed_domains: list[str] | None = None) -> bool:
    """
    Validate URL for security (SSRF prevention).

    Args:
        url: The URL to validate
        allowed_domains: Optional list of allowed domains

    Returns:
        True if URL is valid, False otherwise
    """
    # Check URL length to prevent DoS
    if len(url) > MAX_URL_LENGTH:
        logger.warning(f"URL too long: {len(url)} characters (max {MAX_URL_LENGTH})")
        return False

    try:
        parsed = urllib.parse.urlparse(url)

        # Only allow http and https schemes
        if parsed.scheme not in ("http", "https"):
            logger.warning(f"URL scheme not allowed: {parsed.scheme}")
            return False

        # Check allowed domains if specified (extract hostname without port)
        hostname = parsed.hostname or ""
        if allowed_domains and hostname not in allowed_domains:
            logger.warning(f"Domain not in allowed list: {hostname}")
            return False

        # Block localhost and private IPs
        hostname = parsed.hostname or ""
        # Handle IPv6 in netloc (e.g., http://[::1]/admin, http://[::1]:8080/admin, http://::1/admin)
        netloc = parsed.netloc
        # Decode URL to catch encoded zone IDs (e.g., fe80::1%25eth0 -> fe80::1%eth0)
        decoded_netloc = urllib.parse.unquote(netloc)
        # Block IPv6 with zone IDs (e.g., fe80::1%eth0) - security risk
        if "%" in decoded_netloc:
            logger.warning(f"URL contains zone ID (potential security risk): {url}")
            return False

        if not hostname and netloc:
            # Check if it's IPv6 (contains ::)
            if "::" in netloc:
                # Could be IPv6 - try to parse it
                try:
                    # Extract IPv6 part (before any port)
                    ipv6_part = netloc.split(":")[0]
                    if ipv6_part.startswith("["):
                        ipv6_part = ipv6_part[1:-1]  # Remove brackets
                    elif ipv6_part == "":
                        # Full IPv6 like ::1
                        ipv6_part = netloc.rstrip("/").split("/")[0]
                    ipaddress.ip_address(ipv6_part)
                    hostname = ipv6_part
                except ValueError:
                    pass
            elif netloc.startswith("[") and "]" in netloc:
                # IPv6 with brackets
                bracket_end = netloc.index("]")
                hostname = netloc[1:bracket_end]
            else:
                # Regular host:port
                if ":" in netloc:
                    hostname = netloc.split(":")[0]
                else:
                    hostname = netloc
        blocked_hosts = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "::",
            "::1",  # IPv6 loopback
        ]

        # Check for private/reserved IP ranges (includes IPv6 private ranges)
        is_private_ip = _is_private_ip(hostname) if hostname else False
        is_localhost = (
            hostname in blocked_hosts
            or hostname.endswith(".local")
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


def reset() -> None:
    """Reset the HTTP client and clear caches. For testing purposes."""
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
            _client = None
    # Clear robots cache
    global _robots_cache
    with _robots_cache_lock:
        _robots_cache.clear()


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


def _cleanup_robots_cache() -> None:
    """Clean up expired entries from robots cache."""
    now = time.time()
    expired = [
        domain
        for domain, cached in _robots_cache.items()
        if now - cached[0] > ROBOTS_CACHE_TTL
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


def is_allowed_by_robots(url: str, user_agent: str = "*", domain: str | None = None) -> bool:
    """Check if a URL is allowed by robots.txt.

    Args:
        url: The URL to check
        user_agent: The user agent to check against (default: *)
        domain: The domain to use for robots.txt lookup. If not provided,
                it will be extracted from the URL.

    Returns:
        True if the URL is allowed, False if disallowed.
        When robots.txt returns 404 (does not exist), returns True (allows all access).
    """
    parsed = urllib.parse.urlparse(url)
    # Use provided domain or extract from URL
    robots_domain = domain or parsed.netloc
    path = parsed.path or "/"

    disallowed_paths: set[str] = set()
    allowed_paths: set[str] = set()

    global _robots_request_counter

    with _robots_cache_lock:
        # Periodic cleanup every N requests
        _robots_request_counter += 1
        if _robots_request_counter >= _ROBOTS_CLEANUP_INTERVAL:
            _cleanup_robots_cache()
            _robots_request_counter = 0

        now = time.time()

        # Check cache
        if robots_domain in _robots_cache:
            cache_time, cached_disallowed, cached_allowed = _robots_cache[robots_domain]
            if now - cache_time < ROBOTS_CACHE_TTL:
                # Check allowed first (takes precedence)
                for pattern in cached_allowed:
                    if _matches_robots_pattern(path, pattern):
                        logger.debug(f"URL {url} explicitly allowed by robots.txt")
                        return True
                # Check disallowed
                for pattern in cached_disallowed:
                    if _matches_robots_pattern(path, pattern):
                        logger.debug(f"URL {url} disallowed by robots.txt")
                        return False
                return True
            # Cache expired, remove it
            del _robots_cache[robots_domain]

    # Fetch and parse robots.txt
    base_url = f"{parsed.scheme}://{robots_domain}"
    robots_content = fetch_robots_txt(base_url)

    if robots_content and isinstance(robots_content, str):
        # Track which user-agent section we're in
        in_target_section = False
        user_agent_lower = user_agent.lower()
        seen_other_agent = False  # Track if we've seen a different user-agent

        for line in robots_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for user-agent directive
            if line.lower().startswith("user-agent:"):
                agent = line.split(":", 1)[1].strip().lower()
                # If we already saw a different agent, don't re-enter target section
                if seen_other_agent:
                    in_target_section = False
                # Match exact user-agent or wildcard *
                if agent == user_agent_lower or agent == "*":
                    in_target_section = True
                else:
                    in_target_section = False
                    seen_other_agent = True

            # Check for allow/disallow only if we're in the target section
            elif in_target_section:
                if line.lower().startswith("allow:"):
                    allow_path = line.split(":", 1)[1].strip()
                    if allow_path:
                        allowed_paths.add(allow_path)
                elif line.lower().startswith("disallow:"):
                    disallow_path = line.split(":", 1)[1].strip()
                    if disallow_path:
                        disallowed_paths.add(disallow_path)

    # Cache the results
    with _robots_cache_lock:
        _robots_cache[robots_domain] = (now, disallowed_paths, allowed_paths)

    # Check if path is explicitly allowed (Allow takes precedence)
    for pattern in allowed_paths:
        if _matches_robots_pattern(path, pattern):
            logger.debug(f"URL {url} explicitly allowed by robots.txt (pattern: {pattern})")
            return True

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
