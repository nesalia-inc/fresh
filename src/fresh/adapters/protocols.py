"""Protocol definitions for dependency injection.

These protocols define the interfaces for I/O operations,
allowing easy mocking and testing of business logic.
"""

from __future__ import annotations

from typing import Protocol


class HTTPFetcher(Protocol):
    """Protocol for HTTP fetching operations."""

    def fetch(self, url: str) -> str | None:
        """Fetch content from URL.

        Args:
            url: The URL to fetch

        Returns:
            The content as string, or None if failed
        """
        ...

    def fetch_binary_aware(self, url: str, skip_binary: bool = True) -> str | None:
        """Fetch content, skipping binary URLs if requested.

        Args:
            url: The URL to fetch
            skip_binary: Whether to skip binary content

        Returns:
            The content as string, or None if failed/skipped
        """
        ...


class RobotsChecker(Protocol):
    """Protocol for robots.txt checking."""

    def is_allowed(self, url: str, domain: str | None = None) -> bool:
        """Check if URL is allowed by robots.txt.

        Args:
            url: The URL to check
            domain: Optional domain for caching

        Returns:
            True if allowed, False otherwise
        """
        ...


class SitemapDiscovery(Protocol):
    """Protocol for sitemap discovery."""

    def discover(self, url: str) -> str | None:
        """Discover sitemap URL for a site.

        Args:
            url: The base URL of the site

        Returns:
            The sitemap URL, or None if not found
        """
        ...

    def fetch(self, url: str) -> str | None:
        """Fetch content from URL.

        Args:
            url: The URL to fetch

        Returns:
            The content as string, or None if failed
        """
        ...

    def parse(self, xml_content: str) -> list[str]:
        """Parse sitemap XML to extract URLs.

        Args:
            xml_content: The sitemap XML content

        Returns:
            List of URLs found in sitemap
        """
        ...


class URLNormalizer(Protocol):
    """Protocol for URL normalization."""

    def normalize(self, url: str, base_url: str) -> str:
        """Normalize a URL relative to base URL.

        Args:
            url: The URL to normalize
            base_url: The base URL

        Returns:
            The normalized absolute URL
        """
        ...


class PageStorage(Protocol):
    """Protocol for page storage operations."""

    def save(self, url: str, content: str, metadata: dict) -> bool:
        """Save page content to storage.

        Args:
            url: The URL of the page
            content: The HTML content
            metadata: Metadata to save with the page

        Returns:
            True if saved successfully
        """
        ...

    def exists(self, url: str) -> bool:
        """Check if page exists in storage.

        Args:
            url: The URL of the page

        Returns:
            True if page exists
        """
        ...

    def get(self, url: str) -> str | None:
        """Get page content from storage.

        Args:
            url: The URL of the page

        Returns:
            The content, or None if not found
        """
        ...

    def get_metadata(self, url: str) -> dict | None:
        """Get metadata for a page.

        Args:
            url: The URL of the page

        Returns:
            The metadata dict, or None if not found
        """
        ...


class CacheRepository(Protocol):
    """Protocol for caching operations."""

    def get(self, key: str) -> str | None:
        """Get cached content.

        Args:
            key: The cache key (usually URL)

        Returns:
            The cached content, or None if not found
        """
        ...

    def set(self, key: str, value: str, ttl_days: int | None = None) -> None:
        """Set cached content.

        Args:
            key: The cache key
            value: The content to cache
            ttl_days: Optional TTL in days
        """
        ...

    def delete(self, key: str) -> None:
        """Delete cached content.

        Args:
            key: The cache key to delete
        """
        ...

    def clear(self) -> int:
        """Clear all cached content.

        Returns:
            Number of items deleted
        """
        ...


class HistoryRepository(Protocol):
    """Protocol for history operations."""

    def save_search(self, query: str, url: str, results_count: int, success: bool) -> None:
        """Save search to history.

        Args:
            query: The search query
            url: The URL searched
            results_count: Number of results
            success: Whether search was successful
        """
        ...

    def save_access(self, page_path: str, method: str = "search") -> None:
        """Save page access to history.

        Args:
            page_path: The path of the page accessed
            method: The method of access
        """
        ...

    def get_search_history(self, limit: int = 20, query: str | None = None, url: str | None = None) -> list[dict]:
        """Get search history.

        Args:
            limit: Maximum number of results
            query: Optional query filter
            url: Optional URL filter

        Returns:
            List of search history records
        """
        ...

    def get_access_history(self, limit: int = 20, url: str | None = None) -> list[dict]:
        """Get access history.

        Args:
            limit: Maximum number of results
            url: Optional URL filter

        Returns:
            List of access history records
        """
        ...


class SearchIndex(Protocol):
    """Protocol for search index operations."""

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Search the index.

        Args:
            query: The search query
            limit: Maximum number of results

        Returns:
            List of search results with url, title, snippet
        """
        ...

    def index(self, url: str, title: str, content: str) -> None:
        """Index a page.

        Args:
            url: The URL of the page
            title: The page title
            content: The page content
        """
        ...

    def delete(self, url: str) -> None:
        """Delete a page from index.

        Args:
            url: The URL to delete
        """
        ...
