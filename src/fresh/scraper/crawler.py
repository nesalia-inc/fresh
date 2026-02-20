"""HTML crawler for websites without sitemaps."""

from __future__ import annotations

import logging
import time
import urllib.parse

from bs4 import BeautifulSoup

from .http import fetch_with_retry
from .sitemap import normalize_urls

logger = logging.getLogger(__name__)

DEFAULT_DELAY = 0.5  # seconds between requests


def fetch_page(url: str) -> str | None:
    """
    Download an HTML page.

    Args:
        url: The URL to fetch

    Returns:
        HTML content or None on failure
    """
    return fetch_with_retry(url)


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
) -> set[str]:
    """
    BFS crawl of the website.

    Args:
        start_url: The starting URL
        max_pages: Maximum number of pages to fetch
        max_depth: Maximum crawl depth
        delay: Delay in seconds between requests

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

            logger.debug(f"Crawling (depth={depth}): {url}")
            visited.add(url)

            html = fetch_page(url)
            if html is None:
                continue

            links = extract_links(html, url)

            for link in links:
                if link not in visited and len(visited) < max_pages:
                    next_urls.append(link)

            # Rate limiting: delay between requests
            if delay > 0 and len(visited) < max_pages:
                time.sleep(delay)

        if next_urls:
            urls_by_depth[depth + 1] = next_urls

        if len(visited) >= max_pages:
            break

    logger.info(f"Crawl complete: {len(visited)} pages discovered")
    return visited
