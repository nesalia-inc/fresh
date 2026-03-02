"""Core business logic for list command.

This module contains pure business logic for discovering and listing
documentation pages, independent of CLI concerns.
"""

from __future__ import annotations

import json
import urllib.parse
from typing import Any

from ..scraper import crawler, filter as filter_module, sitemap


# Type alias for entries
Entry = dict[str, Any]
EntryList = list[Entry]


# Constants for --all option (effectively unlimited limits)
ALL_PAGES_MAX_PAGES = 999999
ALL_PAGES_DEPTH = 99


def discover_pages(
    url: str,
    max_pages: int = 100,
    depth: int = 3,
    pattern: str | None = None,
    verbose: bool = False,
) -> EntryList:
    """Discover documentation pages from a URL.

    Uses sitemap if available, falls back to crawler.

    Args:
        url: Base URL of the documentation
        max_pages: Maximum number of pages to discover
        depth: Maximum crawl depth
        pattern: Optional regex pattern to filter URLs
        verbose: Whether to show verbose output

    Returns:
        List of entries with name, path, url
    """
    discovered_urls: set[str] = set()

    # Try sitemap first
    sitemap_url = sitemap.discover_sitemap(url)

    if sitemap_url:
        if verbose:
            print(f"Found sitemap at {sitemap_url}")

        xml_content = sitemap.fetch_with_retry(sitemap_url)

        if xml_content and isinstance(xml_content, str):
            urls = sitemap.parse_sitemap(xml_content)
            if urls:
                # Filter relevant URLs
                filtered = [u for u in urls if filter_module.is_relevant_url(u)]
                # Apply max_pages limit
                filtered = filtered[:max_pages]
                discovered_urls.update(filtered)

    # Fallback to crawler if no sitemap found or sitemap yielded no results
    if not discovered_urls:
        if verbose:
            print("No sitemap found, using crawler...")
        discovered_urls = crawler.crawl(url, max_pages=max_pages, max_depth=depth)

    # Apply pattern filter if specified
    if pattern:
        discovered_urls = set(filter_module.filter_by_pattern([*discovered_urls], pattern))

    # Convert URLs to named entries
    entries: EntryList = []
    for page_url in discovered_urls:
        parsed = urllib.parse.urlparse(page_url)
        name = filter_module.extract_name_from_url(page_url)
        entries.append({
            "name": name,
            "path": parsed.path,
            "url": page_url,
        })

    return entries


def filter_by_pattern(urls: list[str], pattern: str) -> list[str]:
    """Filter URLs by regex pattern.

    Args:
        urls: List of URLs to filter
        pattern: Regex pattern

    Returns:
        Filtered list of URLs
    """
    return filter_module.filter_by_pattern(urls, pattern)


def sort_entries(entries: EntryList, sort_by: str = "name") -> EntryList:
    """Sort entries by name or path.

    Args:
        entries: List of entries to sort
        sort_by: Sort by "name" or "path"

    Returns:
        Sorted list of entries
    """
    sorted_entries = entries.copy()
    if sort_by == "path":
        sorted_entries.sort(key=lambda e: e["path"])
    else:
        sorted_entries.sort(key=lambda e: e["name"])
    return sorted_entries


def format_as_json(entries: EntryList, indent: int = 2) -> str:
    """Format entries as JSON.

    Args:
        entries: List of entries to format
        indent: JSON indentation

    Returns:
        JSON string
    """
    return json.dumps(entries, indent=indent)


def format_as_yaml(entries: EntryList) -> str:
    """Format entries as YAML.

    Args:
        entries: List of entries to format

    Returns:
        YAML string
    """
    try:
        import yaml  # type: ignore[import-untyped]
        return yaml.dump(entries)  # type: ignore[no-any-return]
    except ImportError:
        raise ImportError("PyYAML not installed. Install with: pip install pyyaml")


def format_as_xml(entries: EntryList) -> str:
    """Format entries as XML.

    Args:
        entries: List of entries to format

    Returns:
        XML string with declaration
    """
    import xml.etree.ElementTree as ET

    root = ET.Element("pages")
    for entry in entries:
        page = ET.SubElement(root, "page")
        ET.SubElement(page, "name").text = entry["name"]
        ET.SubElement(page, "path").text = entry["path"]
        ET.SubElement(page, "url").text = entry["url"]

    ET.indent(root)
    xml_string = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string


def create_entry(url: str) -> Entry:
    """Create an entry from a URL.

    Args:
        url: The URL to create entry from

    Returns:
        Entry dict with name, path, url
    """
    parsed = urllib.parse.urlparse(url)
    name = filter_module.extract_name_from_url(url)
    return {
        "name": name,
        "path": parsed.path,
        "url": url,
    }
