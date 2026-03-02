"""Tests for core sync service - pure business logic."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from fresh.core.sync_service import (
    create_sync_result,
    should_skip_url,
    compute_sync_path,
    normalize_url,
    extract_domain,
    filter_urls_by_pattern,
    limit_urls,
    count_results,
)


class TestCreateSyncResult:
    """Tests for create_sync_result function."""

    def test_creates_new_result(self):
        """Should create a new SyncResult with correct URL."""
        result = create_sync_result("https://example.com")

        assert result.url == "https://example.com"
        assert result.success_count == 0
        assert result.failed_count == 0
        assert result.skipped_robots == 0


class TestShouldSkipUrl:
    """Tests for should_skip_url function."""

    def test_skip_robots(self):
        """Should skip when robots not allowed."""
        should_skip, reason = should_skip_url(
            "https://example.com/page.html",
            None,
            robots_allowed=False,
            is_binary=False,
            is_unchanged=False,
        )

        assert should_skip is True
        assert reason == "robots"

    def test_skip_binary(self):
        """Should skip binary content."""
        should_skip, reason = should_skip_url(
            "https://example.com/image.png",
            None,
            robots_allowed=True,
            is_binary=True,
            is_unchanged=False,
        )

        assert should_skip is True
        assert reason == "binary"

    def test_skip_unchanged(self):
        """Should skip unchanged pages."""
        should_skip, reason = should_skip_url(
            "https://example.com/page.html",
            None,
            robots_allowed=True,
            is_binary=False,
            is_unchanged=True,
        )

        assert should_skip is True
        assert reason == "unchanged"

    def test_skip_pattern_no_match(self):
        """Should skip when pattern doesn't match."""
        should_skip, reason = should_skip_url(
            "https://example.com/about.html",
            r"/docs/.*",
            robots_allowed=True,
            is_binary=False,
            is_unchanged=False,
        )

        assert should_skip is True
        assert reason == "pattern"

    def test_no_skip(self):
        """Should not skip when all conditions met."""
        should_skip, reason = should_skip_url(
            "https://example.com/page.html",
            None,
            robots_allowed=True,
            is_binary=False,
            is_unchanged=False,
        )

        assert should_skip is False
        assert reason == ""


class TestComputeSyncPath:
    """Tests for compute_sync_path function."""

    def test_basic_path(self):
        """Should compute basic path correctly."""
        path = compute_sync_path(
            "https://example.com/docs/page.html",
            "https://example.com",
            Path("/tmp/pages"),
        )

        assert "page.html" in str(path)

    def test_index_path(self):
        """Should handle index paths."""
        path = compute_sync_path(
            "https://example.com/docs/",
            "https://example.com",
            Path("/tmp/pages"),
        )

        assert "index.html" in str(path)

    def test_root_path(self):
        """Should handle root path."""
        path = compute_sync_path(
            "https://example.com",
            "https://example.com",
            Path("/tmp/pages"),
        )

        assert "index.html" in str(path)


class TestNormalizeUrl:
    """Tests for normalize_url function."""

    def test_absolute_url(self):
        """Should return absolute URL as-is."""
        result = normalize_url("https://example.com/page.html", "https://other.com")
        assert result == "https://example.com/page.html"

    def test_relative_path(self):
        """Should handle relative paths."""
        result = normalize_url("page.html", "https://example.com/docs/")
        assert "page.html" in result
        assert "example.com" in result

    def test_absolute_path(self):
        """Should handle absolute paths."""
        result = normalize_url("/about", "https://example.com/docs/")
        assert "/about" in result
        assert "example.com" in result


class TestExtractDomain:
    """Tests for extract_domain function."""

    def test_simple_domain(self):
        """Should extract simple domain."""
        result = extract_domain("https://example.com/page")
        assert result == "example_com"

    def test_with_port(self):
        """Should handle port in domain."""
        result = extract_domain("https://localhost:8080/page")
        assert result == "localhost_8080"


class TestFilterUrlsByPattern:
    """Tests for filter_urls_by_pattern function."""

    def test_no_pattern(self):
        """Should return all URLs when no pattern."""
        urls = ["a.html", "b.html", "c.html"]
        result = filter_urls_by_pattern(urls, None)
        assert result == urls

    def test_with_pattern(self):
        """Should filter by pattern."""
        urls = ["docs/page.html", "about.html", "docs/api.html"]
        result = filter_urls_by_pattern(urls, r"docs/.*")
        assert len(result) == 2
        assert "docs/page.html" in result
        assert "docs/api.html" in result

    def test_invalid_pattern(self):
        """Should return all URLs when pattern is invalid."""
        urls = ["a.html", "b.html"]
        result = filter_urls_by_pattern(urls, r"[invalid")
        assert result == urls


class TestLimitUrls:
    """Tests for limit_urls function."""

    def test_under_limit(self):
        """Should return all URLs when under limit."""
        urls = ["a.html", "b.html"]
        result = limit_urls(urls, 10)
        assert len(result) == 2

    def test_over_limit(self):
        """Should limit URLs when over limit."""
        urls = ["a.html", "b.html", "c.html"]
        result = limit_urls(urls, 2)
        assert len(result) == 2


class TestCountResults:
    """Tests for count_results function."""

    def test_count_all_zero(self):
        """Should count all zero correctly."""
        result = create_sync_result("https://example.com")
        counts = count_results(result)

        assert counts["success"] == 0
        assert counts["failed"] == 0

    def test_count_with_values(self):
        """Should count values correctly."""
        result = create_sync_result("https://example.com")
        result.success_count = 10
        result.failed_count = 2
        result.skipped_robots = 3

        counts = count_results(result)

        assert counts["success"] == 10
        assert counts["failed"] == 2
        assert counts["skipped_robots"] == 3
