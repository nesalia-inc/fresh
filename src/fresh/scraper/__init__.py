"""Fresh scraping engine."""

from .http import HTTPClient, get_client, fetch, fetch_with_retry, close, validate_url
from .sitemap import discover_sitemap, parse_sitemap, normalize_urls
from .crawler import fetch_page, extract_links, crawl
from .filter import (
    is_relevant_url,
    extract_name_from_url,
    deduplicate,
    filter_by_pattern,
)

__all__ = [
    # HTTP client
    "HTTPClient",
    "get_client",
    "fetch",
    "fetch_with_retry",
    "close",
    "validate_url",
    # Sitemap
    "discover_sitemap",
    "parse_sitemap",
    "normalize_urls",
    # Crawler
    "fetch_page",
    "extract_links",
    "crawl",
    # Filter
    "is_relevant_url",
    "extract_name_from_url",
    "deduplicate",
    "filter_by_pattern",
]
