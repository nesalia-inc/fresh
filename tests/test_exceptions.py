"""Tests for fresh.exceptions module."""

import pytest

from fresh.exceptions import (
    AliasError,
    CacheError,
    CLIError,
    ConfigError,
    CrawlerError,
    FetchError,
    FilterError,
    FreshError,
    NetworkError,
    SitemapError,
    TimeoutError,
    ValidationError,
)


class TestFreshError:
    """Tests for FreshError base exception."""

    def test_base_exception(self):
        """Should create base exception with message."""
        error = FreshError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.code is None

    def test_with_code(self):
        """Should create exception with code."""
        error = FreshError("Test error", code="TEST_CODE")
        assert error.code == "TEST_CODE"

    def test_inheritance(self):
        """FreshError should be base for all exceptions."""
        assert issubclass(NetworkError, FreshError)
        assert issubclass(FetchError, NetworkError)
        assert issubclass(TimeoutError, NetworkError)
        assert issubclass(ValidationError, FreshError)
        assert issubclass(AliasError, FreshError)
        assert issubclass(CacheError, FreshError)
        assert issubclass(SitemapError, FreshError)
        assert issubclass(CrawlerError, FreshError)
        assert issubclass(FilterError, FreshError)
        assert issubclass(ConfigError, FreshError)
        assert issubclass(CLIError, FreshError)


class TestFetchError:
    """Tests for FetchError exception."""

    def test_fetch_error(self):
        """Should create FetchError with url and reason."""
        error = FetchError("https://example.com", "Connection refused")
        assert error.url == "https://example.com"
        assert error.reason == "Connection refused"
        assert "https://example.com" in str(error)
        assert "Connection refused" in str(error)
        assert error.code == "FETCH_ERROR"


class TestTimeoutError:
    """Tests for TimeoutError exception."""

    def test_timeout_error(self):
        """Should create TimeoutError with url and timeout."""
        error = TimeoutError("https://example.com", 30.0)
        assert error.url == "https://example.com"
        assert error.timeout == 30.0
        assert "https://example.com" in str(error)
        assert "30.0" in str(error)
        assert error.code == "TIMEOUT_ERROR"


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error(self):
        """Should create ValidationError."""
        error = ValidationError("Invalid input", code="INVALID_INPUT")
        assert str(error) == "Invalid input"
        assert error.code == "INVALID_INPUT"


class TestAliasError:
    """Tests for AliasError exception."""

    def test_alias_error(self):
        """Should create AliasError."""
        error = AliasError("Alias not found", code="ALIAS_NOT_FOUND")
        assert str(error) == "Alias not found"
        assert error.code == "ALIAS_NOT_FOUND"


class TestCacheError:
    """Tests for CacheError exception."""

    def test_cache_error(self):
        """Should create CacheError."""
        error = CacheError("Cache read failed", code="CACHE_ERROR")
        assert str(error) == "Cache read failed"
        assert error.code == "CACHE_ERROR"


class TestSitemapError:
    """Tests for SitemapError exception."""

    def test_sitemap_error(self):
        """Should create SitemapError."""
        error = SitemapError("Invalid XML", code="SITEMAP_PARSE_ERROR")
        assert str(error) == "Invalid XML"
        assert error.code == "SITEMAP_PARSE_ERROR"


class TestCrawlerError:
    """Tests for CrawlerError exception."""

    def test_crawler_error(self):
        """Should create CrawlerError."""
        error = CrawlerError("Crawl failed", code="CRAWL_ERROR")
        assert str(error) == "Crawl failed"
        assert error.code == "CRAWL_ERROR"


class TestFilterError:
    """Tests for FilterError exception."""

    def test_filter_error(self):
        """Should create FilterError."""
        error = FilterError("Invalid filter", code="FILTER_ERROR")
        assert str(error) == "Invalid filter"
        assert error.code == "FILTER_ERROR"


class TestConfigError:
    """Tests for ConfigError exception."""

    def test_config_error(self):
        """Should create ConfigError."""
        error = ConfigError("Config not found", code="CONFIG_NOT_FOUND")
        assert str(error) == "Config not found"
        assert error.code == "CONFIG_NOT_FOUND"


class TestCLIError:
    """Tests for CLIError exception."""

    def test_cli_error(self):
        """Should create CLIError."""
        error = CLIError("Invalid argument", code="INVALID_ARG")
        assert str(error) == "Invalid argument"
        assert error.code == "INVALID_ARG"
