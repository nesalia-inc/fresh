"""Core entity for list operations.

This module contains the List entity which encapsulates all list logic,
following an entity-oriented architecture pattern.
"""

from __future__ import annotations

import json
import urllib.parse
from typing import Any, Optional

from .config import ListConfig


# Type alias for entries
Entry = dict[str, Any]
EntryList = list[Entry]


class List:
    """Entity representing a list operation.

    This class encapsulates all the business logic for discovering
    and listing documentation pages.
    """

    # Constants for --all option
    ALL_PAGES_MAX_PAGES = 999999
    ALL_PAGES_DEPTH = 99

    def __init__(self, config: ListConfig) -> None:
        """Initialize List entity.

        Args:
            config: The list configuration
        """
        self.config = config

    def discover_pages(
        self,
        url: str,
        max_pages: Optional[int] = None,
        depth: Optional[int] = None,
        pattern: Optional[str] = None,
    ) -> EntryList:
        """Discover documentation pages from a URL.

        Args:
            url: Base URL of the documentation
            max_pages: Maximum number of pages (default from config)
            depth: Maximum crawl depth (default from config)
            pattern: Optional regex pattern to filter URLs

        Returns:
            List of entries with name, path, url
        """
        from ..scraper import crawler, filter as filter_module, sitemap

        if max_pages is None:
            max_pages = self.config.max_pages
        if depth is None:
            depth = 3

        discovered_urls: set[str] = set()

        # Try sitemap first
        sitemap_url = sitemap.discover_sitemap(url)

        if sitemap_url:
            xml_content = sitemap.fetch_with_retry(sitemap_url)
            if xml_content and isinstance(xml_content, str):
                urls = sitemap.parse_sitemap(xml_content)
                if urls:
                    filtered = [u for u in urls if filter_module.is_relevant_url(u)]
                    filtered = filtered[:max_pages]
                    discovered_urls.update(filtered)

        # Fallback to crawler if no sitemap found
        if not discovered_urls:
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

    def filter_by_pattern(self, urls: list[str], pattern: str) -> list[str]:
        """Filter URLs by regex pattern.

        Args:
            urls: List of URLs to filter
            pattern: Regex pattern

        Returns:
            Filtered list of URLs
        """
        from ..scraper import filter as filter_module
        return filter_module.filter_by_pattern(urls, pattern)

    def sort_entries(self, entries: EntryList, sort_by: str = "name") -> EntryList:
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

    def format_as_json(self, entries: EntryList, indent: int = 2) -> str:
        """Format entries as JSON.

        Args:
            entries: List of entries to format
            indent: JSON indentation

        Returns:
            JSON string
        """
        return json.dumps(entries, indent=indent)

    def format_as_yaml(self, entries: EntryList) -> str:
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

    def format_as_xml(self, entries: EntryList) -> str:
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


# Standalone functions for backwards compatibility

def create_entry(name: str, path: str, url: str) -> Entry:
    """Create a new entry.

    Args:
        name: The name of the entry
        path: The path of the entry
        url: The URL of the entry

    Returns:
        A new entry dictionary
    """
    return {"name": name, "path": path, "url": url}


def discover_pages(
    url: str,
    max_pages: Optional[int] = None,
    depth: Optional[int] = None,
    pattern: Optional[str] = None,
) -> EntryList:
    """Discover documentation pages from a URL.

    Args:
        url: Base URL of the documentation
        max_pages: Maximum number of pages (default from config)
        depth: Maximum crawl depth (default from config)
        pattern: Optional regex pattern to filter URLs

    Returns:
        List of entries with name, path, url
    """
    return List(ListConfig(url=url)).discover_pages(url, max_pages, depth, pattern)


def filter_by_pattern(urls: list[str], pattern: str) -> list[str]:
    """Filter URLs by regex pattern.

    Args:
        urls: List of URLs to filter
        pattern: Regex pattern

    Returns:
        Filtered list of URLs
    """
    return List(ListConfig(url="")).filter_by_pattern(urls, pattern)


def sort_entries(entries: EntryList, sort_by: str = "name") -> EntryList:
    """Sort entries by name or path.

    Args:
        entries: List of entries to sort
        sort_by: Sort by "name" or "path"

    Returns:
        Sorted list of entries
    """
    return List(ListConfig(url="")).sort_entries(entries, sort_by)


def format_as_json(entries: EntryList, indent: int = 2) -> str:
    """Format entries as JSON.

    Args:
        entries: List of entries to format
        indent: JSON indentation

    Returns:
        JSON string
    """
    return List(ListConfig(url="")).format_as_json(entries, indent)


def format_as_yaml(entries: EntryList) -> str:
    """Format entries as YAML.

    Args:
        entries: List of entries to format

    Returns:
        YAML string
    """
    return List(ListConfig(url="")).format_as_yaml(entries)


def format_as_xml(entries: EntryList) -> str:
    """Format entries as XML.

    Args:
        entries: List of entries to format

    Returns:
        XML string with declaration
    """
    return List(ListConfig(url="")).format_as_xml(entries)
