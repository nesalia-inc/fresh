"""HTML crawler for websites without sitemaps."""

from __future__ import annotations

import logging
import threading
import time
import urllib.parse

from bs4 import BeautifulSoup

from .http import fetch_with_retry, is_allowed_by_robots
from .sitemap import normalize_urls

logger = logging.getLogger(__name__)

DEFAULT_DELAY = 0.5  # seconds between requests
RATE_LIMIT_TTL = 3600  # Clean up entries older than 1 hour
RATE_LIMIT_MAX_DOMAINS = 100  # Max domains to track

# Per-domain rate limiting
_domain_last_request: dict[str, float] = {}
_domain_lock = threading.Lock()


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

    with _domain_lock:
        # Periodic cleanup
        if len(_domain_last_request) > RATE_LIMIT_MAX_DOMAINS:
            _cleanup_rate_limit_dict()

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
    result = fetch_with_retry(url)
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
) -> set[str]:
    """
    BFS crawl of the website.

    Args:
        start_url: The starting URL
        max_pages: Maximum number of pages to fetch
        max_depth: Maximum crawl depth
        delay: Delay in seconds between requests
        respect_robots: Whether to respect robots.txt rules

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
