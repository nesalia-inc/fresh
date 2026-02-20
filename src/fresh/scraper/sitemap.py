"""Sitemap discovery and parsing."""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import TYPE_CHECKING

from .http import fetch_with_retry

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)

SITEMAP_PATTERNS = [
    "/sitemap.xml",
    "/sitemap-index.xml",
    "/sitemap_index.xml",
    "/sitemap-index.xml.gz",
]


def discover_sitemap(base_url: str) -> str | None:
    """
    Discover sitemap.xml on the website.

    Checks common locations and also looks in robots.txt.

    Args:
        base_url: The base URL of the website

    Returns:
        Absolute URL of the sitemap or None if not found
    """
    base = base_url.rstrip("/")

    # Try common sitemap locations
    for pattern in SITEMAP_PATTERNS:
        sitemap_url = f"{base}{pattern}"
        logger.debug(f"Checking for sitemap: {sitemap_url}")
        # Just check if it exists, don't download yet
        # We'll download in parse_sitemap if needed
        return sitemap_url

    # Try to find sitemap from robots.txt
    robots_url = f"{base}/robots.txt"
    robots_content = fetch_with_retry(robots_url)
    if robots_content:
        sitemap_match = re.search(
            r"Sitemap:\s*(\S+)",
            robots_content,
            re.IGNORECASE,
        )
        if sitemap_match:
            sitemap_url = sitemap_match.group(1)
            logger.info(f"Found sitemap in robots.txt: {sitemap_url}")
            return sitemap_url

    logger.warning(f"No sitemap found for {base_url}")
    return None


def parse_sitemap(xml_content: str) -> list[str] | None:
    """
    Parse XML content and extract URLs.

    Args:
        xml_content: The XML content of the sitemap

    Returns:
        List of URLs found in the sitemap, or None if parsing fails
    """
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logger.error(f"Failed to parse XML: {e}")
        return None

    # Handle sitemap index (contains other sitemaps)
    if root.tag.endswith("}sitemapindex") or root.tag == "sitemapindex":
        urls = []
        for sitemap in root.findall(".//{*}loc"):
            if sitemap.text:
                urls.append(sitemap.text)
        return urls

    # Handle regular sitemap
    urls = []
    for url in root.findall(".//{*}url"):
        loc = url.find("{*}loc")
        if loc is not None and loc.text:
            urls.append(loc.text)

    return urls if urls else None


def normalize_urls(urls: Sequence[str], base_url: str) -> list[str]:
    """
    Convert relative URLs to absolute URLs.

    Args:
        urls: List of URLs (may be relative or absolute)
        base_url: The base URL to resolve relative URLs against

    Returns:
        List of absolute URLs
    """
    base = base_url.rstrip("/")
    normalized = []

    for url in urls:
        if not url:
            continue

        url = url.strip()

        # Already absolute
        if url.startswith("http://") or url.startswith("https://"):
            normalized.append(url)
            continue

        # Protocol-relative URL
        if url.startswith("//"):
            normalized.append(f"https:{url}")
            continue

        # Absolute path
        if url.startswith("/"):
            parsed = urllib.parse.urlparse(base)
            normalized.append(f"{parsed.scheme}://{parsed.netloc}{url}")
            continue

        # Relative path
        normalized.append(f"{base}/{url}")

    return normalized
