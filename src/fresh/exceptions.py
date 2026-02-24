"""Custom exceptions for fresh."""

from __future__ import annotations


class FreshError(Exception):
    """Base exception for all fresh errors."""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message


class NetworkError(FreshError):
    """Network-related errors."""

    pass


class FetchError(NetworkError):
    """Failed to fetch a URL."""

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch {url}: {reason}", code="FETCH_ERROR")


class TimeoutError(NetworkError):
    """Request timeout."""

    def __init__(self, url: str, timeout: float):
        self.url = url
        self.timeout = timeout
        super().__init__(
            f"Request timed out for {url} after {timeout}s", code="TIMEOUT_ERROR"
        )


class ValidationError(FreshError):
    """Input validation errors."""

    pass


class AliasError(FreshError):
    """Alias-related errors."""

    pass


class CacheError(FreshError):
    """Cache-related errors."""

    pass


class SitemapError(FreshError):
    """Sitemap parsing errors."""

    pass


class CrawlerError(FreshError):
    """Crawler-related errors."""

    pass


class FilterError(FreshError):
    """Filter-related errors."""

    pass


class ConfigError(FreshError):
    """Configuration-related errors."""

    pass


class CLIError(FreshError):
    """CLI-related errors."""

    pass
