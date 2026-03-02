"""Tests for core config dataclasses."""

import pytest
from pathlib import Path

from fresh.core.config import (
    GetConfig,
    GetResult,
    IndexConfig,
    IndexResult,
    ListConfig,
    ListResult,
    SearchConfig,
    SearchResult,
    SearchResultItem,
    SyncConfig,
    SyncResult,
)


class TestSyncConfig:
    """Tests for SyncConfig dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        config = SyncConfig(url="https://example.com")

        assert config.url == "https://example.com"
        assert config.max_pages == 100
        assert config.depth == 3
        assert config.workers == 1
        assert config.force is False
        assert config.incremental is True
        assert config.pattern is None
        assert config.verbose is False

    def test_custom_values(self):
        """Should accept custom values."""
        config = SyncConfig(
            url="https://example.com",
            max_pages=50,
            force=True,
            verbose=True,
        )

        assert config.max_pages == 50
        assert config.force is True
        assert config.verbose is True


class TestSyncResult:
    """Tests for SyncResult dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        result = SyncResult(url="https://example.com")

        assert result.url == "https://example.com"
        assert result.success_count == 0
        assert result.failed_count == 0
        assert result.skipped_robots == 0
        assert result.skipped_binary == 0
        assert result.skipped_unchanged == 0

    def test_custom_values(self):
        """Should accept custom values."""
        result = SyncResult(
            url="https://example.com",
            success_count=10,
            failed_count=2,
            skipped_robots=1,
        )

        assert result.success_count == 10
        assert result.failed_count == 2


class TestSearchConfig:
    """Tests for SearchConfig dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        config = SearchConfig(query="test", url="https://example.com")

        assert config.query == "test"
        assert config.url == "https://example.com"
        assert config.max_pages == 50
        assert config.depth == 3
        assert config.case_sensitive is False
        assert config.regex is False
        assert config.context_lines == 1
        assert config.verbose is False
        assert config.source == "auto"
        assert config.parallel is None
        assert config.fuzzy is False


class TestSearchResultItem:
    """Tests for SearchResultItem dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        item = SearchResultItem(
            path="/page.html",
            title="Page Title",
            snippet="...snippet...",
            url="https://example.com/page.html",
        )

        assert item.source == "local"

    def test_custom_source(self):
        """Should accept custom source."""
        item = SearchResultItem(
            path="/page.html",
            title="Page Title",
            snippet="...snippet...",
            url="https://example.com/page.html",
            source="remote",
        )

        assert item.source == "remote"


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        result = SearchResult(query="test", url="https://example.com")

        assert result.items == []
        assert result.total_count == 0


class TestGetConfig:
    """Tests for GetConfig dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        config = GetConfig(url="https://example.com/page")

        assert config.url == "https://example.com/page"
        assert config.timeout == 30
        assert config.header is None
        assert config.no_follow is False
        assert config.skip_scripts is False
        assert config.no_cache is False
        assert config.cache_ttl is None
        assert config.retry == 3
        assert config.dry_run is False
        assert config.local is False
        assert config.remote is False


class TestGetResult:
    """Tests for GetResult dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        result = GetResult(url="https://example.com", resolved_url="https://example.com")

        assert result.content is None
        assert result.success is False
        assert result.error is None


class TestListConfig:
    """Tests for ListConfig dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        config = ListConfig(url="https://example.com")

        assert config.url == "https://example.com"
        assert config.max_pages == 100
        assert config.pattern is None
        assert config.verbose is False
        assert config.sort == "path"


class TestListResult:
    """Tests for ListResult dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        result = ListResult(url="https://example.com")

        assert result.urls == []
        assert result.count == 0


class TestIndexConfig:
    """Tests for IndexConfig dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        config = IndexConfig(site="example.com")

        assert config.site == "example.com"
        assert config.pages_dir is None
        assert config.force is False


class TestIndexResult:
    """Tests for IndexResult dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        result = IndexResult(site="example.com")

        assert result.page_count == 0
        assert result.success is False
