"""Custom exceptions for fresh."""

from __future__ import annotations


class FreshError(Exception):
    """Base exception for all fresh errors."""

    code: str | None
    message: str

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return self.message


class NetworkError(FreshError):
    """Network-related errors."""


class FetchError(NetworkError):
    """Failed to fetch a URL."""

    url: str
    reason: str

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch {url}: {reason}", code="FETCH_ERROR")


class TimeoutError(NetworkError):
    """Request timeout."""

    url: str
    timeout: float

    def __init__(self, url: str, timeout: float):
        self.url = url
        self.timeout = timeout
        super().__init__(
            f"Request timed out for {url} after {timeout}s", code="TIMEOUT_ERROR"
        )


class ValidationError(FreshError):
    """Input validation errors."""


class AliasError(FreshError):
    """Alias-related errors."""


class CacheError(FreshError):
    """Cache-related errors."""


class SitemapError(FreshError):
    """Sitemap parsing errors."""


class CrawlerError(FreshError):
    """Crawler-related errors."""


class FilterError(FreshError):
    """Filter-related errors."""


class ConfigError(FreshError):
    """Configuration-related errors."""


class CLIError(FreshError):
    """CLI-related errors."""
