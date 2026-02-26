"""Sitemap discovery and parsing."""

from __future__ import annotations

import logging
import re
import urllib.parse
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

import httpx

from ..exceptions import SitemapError
from .http import fetch_with_retry, get_client, validate_url

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

    Checks common locations at the domain root and also looks in robots.txt.

    Args:
        base_url: The base URL of the website

    Returns:
        Absolute URL of the sitemap or None if not found
    """
    base = base_url.rstrip("/")

    # Validate base URL before making any requests
    if not validate_url(base_url):
        logger.warning(f"Base URL validation failed: {base_url}")
        return None

    # Extract domain root for sitemap discovery
    # Sitemaps are typically at the domain root, not subpaths
    parsed = urllib.parse.urlparse(base)
    domain_root = f"{parsed.scheme}://{parsed.netloc}"

    # Try common sitemap locations with HEAD requests at domain root
    for pattern in SITEMAP_PATTERNS:
        sitemap_url = f"{domain_root}{pattern}"
        logger.debug(f"Checking for sitemap: {sitemap_url}")
        # Validate sitemap URL
        if not validate_url(sitemap_url):
            continue
        # Use HEAD request for efficiency
        client = get_client()
        try:
            response = client.head(sitemap_url)
            if response.status_code == 200:
                logger.info(f"Found sitemap: {sitemap_url}")
                return sitemap_url
        except httpx.HTTPError as e:
            logger.debug(f"HEAD request failed for {sitemap_url}: {e}")

    # Fall back to GET for robots.txt since we need the content
    # Try to find sitemap from robots.txt at domain root
    robots_url = f"{domain_root}/robots.txt"
    if not validate_url(robots_url):
        logger.warning(f"Robots.txt URL validation failed: {robots_url}")
        return None
    robots_content = fetch_with_retry(robots_url)
    if robots_content and isinstance(robots_content, str):
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
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logger.error(f"Failed to parse XML: {e}")
        return None

    # Common namespace URIs
    namespaces = [
        "",  # No namespace
        "http://www.sitemaps.org/schemas/sitemap/0.9",
        "http://www.google.com/schemas/sitemap/0.9",
    ]

    # Handle sitemap index (contains other sitemaps)
    if root.tag.endswith("}sitemapindex") or root.tag == "sitemapindex":
        urls = []
        for ns in namespaces:
            for sitemap in root.findall(f".//{{{ns}}}loc"):
                if sitemap.text:
                    urls.append(sitemap.text)
            if urls:
                break
        return urls if urls else None

    # Handle regular sitemap - try multiple namespace approaches
    urls = []
    for ns in namespaces:
        for url in root.findall(f".//{{{ns}}}url"):
            loc = url.find(f"{{{ns}}}loc")
            if loc is None:
                loc = url.find("loc")  # Try without namespace
            if loc is not None and loc.text:
                urls.append(loc.text)
        if urls:
            break

    # Fallback: try to find any loc element regardless of parent
    if not urls:
        for elem in root.iter():
            if elem.tag.endswith("}loc") or elem.tag == "loc":
                if elem.text:
                    urls.append(elem.text)

    return urls if urls else None


def parse_sitemap_strict(xml_content: str) -> list[str]:
    """
    Parse XML content and raise SitemapError if parsing fails.

    Args:
        xml_content: The XML content of the sitemap

    Returns:
        List of URLs found in the sitemap

    Raises:
        SitemapError: If XML parsing fails
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise SitemapError(f"Failed to parse XML: {e}", code="PARSE_ERROR") from e

    # Common namespace URIs
    namespaces = [
        "",  # No namespace
        "http://www.sitemaps.org/schemas/sitemap/0.9",
        "http://www.google.com/schemas/sitemap/0.9",
    ]

    # Handle sitemap index (contains other sitemaps)
    if root.tag.endswith("}sitemapindex") or root.tag == "sitemapindex":
        urls = []
        for ns in namespaces:
            for sitemap in root.findall(f".//{{{ns}}}loc"):
                if sitemap.text:
                    urls.append(sitemap.text)
        return urls

    # Regular sitemap - extract URLs
    urls = []
    for ns in namespaces:
        for loc in root.findall(f".//{{{ns}}}loc"):
            if loc.text:
                urls.append(loc.text)

    # Also find in other namespace variations
    for elem in root.iter():
        if elem.tag.endswith("}loc") or elem.tag == "loc":
            if elem.text:
                urls.append(elem.text)

    if not urls:
        raise SitemapError("No URLs found in sitemap", code="EMPTY_SITEMAP")

    return urls


def normalize_urls(urls: Sequence[str], base_url: str) -> list[str]:
    """
    Convert relative URLs to absolute URLs.

    Args:
        urls: List of URLs (may be relative or absolute)
        base_url: The base URL to resolve relative URLs against

    Returns:
        List of absolute URLs with URL-encoded characters decoded
    """
    # Don't strip trailing slash - it's important for proper URL resolution
    # especially for relative paths where the base is a directory
    base = base_url
    normalized = []

    for url in urls:
        if not url:
            continue

        url = url.strip()

        # Already absolute
        if url.startswith("http://") or url.startswith("https://"):
            # Decode URL-encoded characters in the path for absolute URLs
            parsed = urllib.parse.urlparse(url)
            # Decode percent-encoded characters in the path (e.g., %7E -> ~)
            decoded_path = urllib.parse.unquote(parsed.path)
            # Reconstruct URL with decoded path, preserving query and fragment
            normalized_url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                decoded_path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            ))
            normalized.append(normalized_url)
            continue

        # Protocol-relative URL
        if url.startswith("//"):
            normalized.append(f"https:{url}")
            continue

        # Absolute path
        if url.startswith("/"):
            parsed = urllib.parse.urlparse(base)
            decoded_path = urllib.parse.unquote(url)
            normalized.append(f"{parsed.scheme}://{parsed.netloc}{decoded_path}")
            continue

        # Relative path - use urljoin for proper resolution
        # urljoin correctly handles cases where base is a file path vs directory
        joined = urllib.parse.urljoin(base, url)
        # Decode percent-encoded characters in the path
        parsed = urllib.parse.urlparse(joined)
        decoded_path = urllib.parse.unquote(parsed.path)
        normalized_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            decoded_path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        ))
        normalized.append(normalized_url)

    return normalized
