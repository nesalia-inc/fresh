"""HTML crawler for websites without sitemaps."""

from __future__ import annotations

import logging
import threading
import time
import urllib.parse

from bs4 import BeautifulSoup

from .http import fetch_binary_aware, is_binary_url, is_allowed_by_robots, validate_url
from .sitemap import normalize_urls

logger = logging.getLogger(__name__)

DEFAULT_DELAY = 0.5  # seconds between requests
RATE_LIMIT_TTL = 3600  # Clean up entries older than 1 hour
RATE_LIMIT_MAX_DOMAINS = 100  # Max domains to track
_RATE_LIMIT_CLEANUP_INTERVAL = 100  # Cleanup every 100 requests

# Per-domain rate limiting
_domain_last_request: dict[str, float] = {}
_domain_lock: threading.Lock = threading.Lock()
_request_counter = 0


def _cleanup_rate_limit_dict() -> None:
    """Clean up old entries from the rate limit dictionary."""
    global _domain_last_request
    now = time.time()
    # Remove entries older than TTL
    expired = [
        domain
        for domain, timestamp in _domain_last_request.items()
        if now - timestamp > RATE_LIMIT_TTL
    ]
    for domain in expired:
        del _domain_last_request[domain]

    # If still too large, remove oldest entries
    if len(_domain_last_request) > RATE_LIMIT_MAX_DOMAINS:
        sorted_domains = sorted(
            _domain_last_request.keys(),
            key=lambda d: _domain_last_request[d],
        )
        for domain in sorted_domains[: len(_domain_last_request) - RATE_LIMIT_MAX_DOMAINS]:
            del _domain_last_request[domain]

    if expired:
        logger.debug(f"Cleaned up {len(expired)} expired rate limit entries")


def reset() -> None:
    """Reset the rate limit dictionary. For testing purposes."""
    global _domain_last_request, _request_counter
    with _domain_lock:
        _domain_last_request.clear()
        _request_counter = 0


def _rate_limit_per_domain(url: str, delay: float) -> None:
    """Apply per-domain rate limiting.

    Args:
        url: The URL being requested
        delay: Minimum delay between requests to the same domain
    """
    if delay <= 0:
        return

    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc

    global _request_counter

    with _domain_lock:
        # Periodic cleanup every N requests
        _request_counter += 1
        if _request_counter >= _RATE_LIMIT_CLEANUP_INTERVAL:
            _cleanup_rate_limit_dict()
            _request_counter = 0

        now = time.time()
        last_request = _domain_last_request.get(domain, 0)
        time_since_last = now - last_request

        if time_since_last < delay:
            wait_time = delay - time_since_last
            logger.debug(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
            time.sleep(wait_time)

        _domain_last_request[domain] = time.time()


def fetch_page(url: str) -> str | None:
    """
    Download an HTML page.

    Args:
        url: The URL to fetch

    Returns:
        HTML content or None on failure
    """
    # Skip binary URLs (images, archives, etc.)
    if is_binary_url(url):
        logger.debug(f"Skipping binary URL: {url}")
        return None

    result = fetch_binary_aware(url, skip_binary=True)
    if isinstance(result, str):
        return result
    return None


def extract_links(html: str, base_url: str) -> list[str]:
    """
    Extract all <a href> links from HTML.

    Args:
        html: The HTML content
        base_url: The base URL to resolve relative links

    Returns:
        List of absolute URLs
    """
    # Use BeautifulSoup to parse HTML
    soup = BeautifulSoup(html, "html.parser")

    # Extract all href values from <a> tags
    hrefs: list[str] = []
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if href and isinstance(href, str):
            hrefs.append(href)

    # Normalize to absolute URLs
    normalized = normalize_urls(hrefs, base_url)

    # Filter to same domain only
    parsed_base = urllib.parse.urlparse(base_url)
    domain = parsed_base.netloc

    filtered = []
    for url in normalized:
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc == domain:
            filtered.append(url)

    return filtered


def crawl(
    start_url: str,
    max_pages: int = 100,
    max_depth: int = 3,
    delay: float = DEFAULT_DELAY,
    respect_robots: bool = True,
    allowed_domains: list[str] | None = None,
) -> set[str]:
    """
    BFS crawl of the website.

    Args:
        start_url: The starting URL
        max_pages: Maximum number of pages to fetch
        max_depth: Maximum crawl depth
        delay: Delay in seconds between requests
        respect_robots: Whether to respect robots.txt rules
        allowed_domains: Optional list of allowed domains for validation

    Returns:
        Set of unique URLs discovered
    """
    visited: set[str] = set()
    urls_by_depth: dict[int, list[str]] = {0: [start_url]}

    for depth in range(max_depth + 1):
        if depth not in urls_by_depth:
            break

        current_urls = urls_by_depth[depth]
        next_urls: list[str] = []

        for url in current_urls:
            if len(visited) >= max_pages:
                break

            if url in visited:
                continue

            # Validate URL against allowed domains
            if not validate_url(url, allowed_domains):
                logger.debug(f"Skipping {url} - failed validation")
                continue

            # Check robots.txt if enabled
            if respect_robots and not is_allowed_by_robots(url):
                logger.debug(f"Skipping {url} - disallowed by robots.txt")
                continue

            logger.debug(f"Crawling (depth={depth}): {url}")
            visited.add(url)

            html = fetch_page(url)
            if html is None:
                continue

            links = extract_links(html, url)

            for link in links:
                if link not in visited and len(visited) < max_pages:
                    next_urls.append(link)

            # Per-domain rate limiting
            if len(visited) < max_pages:
                _rate_limit_per_domain(url, delay)

        if next_urls:
            urls_by_depth[depth + 1] = next_urls

        if len(visited) >= max_pages:
            break

    logger.info(f"Crawl complete: {len(visited)} pages discovered")
    return visited


def parallel_fetch_page(args: tuple[str, bool, list[str] | None]) -> tuple[str, str | None, list[str]]:
    """
    Fetch a single page (for parallel execution).

    Args:
        args: Tuple of (url, respect_robots, allowed_domains)

    Returns:
        Tuple of (url, html_content, links)
    """
    url, respect_robots, allowed_domains = args

    # Validate URL
    if not validate_url(url, allowed_domains):
        return (url, None, [])

    # Check robots.txt if enabled
    if respect_robots and not is_allowed_by_robots(url):
        return (url, None, [])

    # Skip binary URLs
    if is_binary_url(url):
        return (url, None, [])

    # Fetch the page
    html = fetch_binary_aware(url)
    if html is None:
        return (url, None, [])

    # Extract links
    links = extract_links(html, url)

    return (url, html, links)


def parallel_crawl(
    start_url: str,
    max_pages: int = 100,
    max_depth: int = 3,
    delay: float = DEFAULT_DELAY,
    respect_robots: bool = True,
    allowed_domains: list[str] | None = None,
    max_workers: int = 5,
) -> set[str]:
    """
    BFS crawl with parallel page fetching.

    Args:
        start_url: The starting URL
        max_pages: Maximum number of pages to fetch
        max_depth: Maximum crawl depth
        delay: Delay in seconds between requests (per domain)
        respect_robots: Whether to respect robots.txt rules
        allowed_domains: Optional list of allowed domains for validation
        max_workers: Maximum number of parallel workers

    Returns:
        Set of unique URLs discovered
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    visited: set[str] = set()
    urls_by_depth: dict[int, list[str]] = {0: [start_url]}

    for depth in range(max_depth + 1):
        if depth not in urls_by_depth:
            break

        current_urls = urls_by_depth[depth]
        next_urls: list[str] = []

        # Prepare args for parallel fetch
        fetch_args = [
            (url, respect_robots, allowed_domains)
            for url in current_urls
            if url not in visited
        ]

        if not fetch_args:
            continue

        # Process URLs in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(parallel_fetch_page, args): args[0]
                for args in fetch_args
            }

            for future in as_completed(futures):
                url = futures[future]
                with visited_lock:
                    if len(visited) >= max_pages:
                        break
                    if url in visited:
                        continue

                try:
                    result_url, html, links = future.result()
                    if html is not None:
                        visited.add(result_url)
                        logger.debug(f"Parallel crawl (depth={depth}): {result_url}")

                        for link in links:
                            if link not in visited and len(visited) < max_pages:
                                next_urls.append(link)

                        # Per-domain rate limiting
                        if len(visited) < max_pages:
                            _rate_limit_per_domain(result_url, delay)
                except Exception as e:
                    logger.debug(f"Error fetching {url}: {e}")

        if next_urls:
            urls_by_depth[depth + 1] = next_urls

        if len(visited) >= max_pages:
            break

    logger.info(f"Parallel crawl complete: {len(visited)} pages discovered")
    return visited
