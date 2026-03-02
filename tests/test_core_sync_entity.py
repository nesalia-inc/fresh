"""Tests for core Sync entity."""

from pathlib import Path

from fresh.core import Sync, SyncConfig


class TestSyncEntity:
    """Tests for Sync entity class."""

    def test_initialization(self):
        """Should initialize with config."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        assert sync.config == config
        assert sync.result.url == "https://example.com"
        assert sync.result.success_count == 0

    def test_record_success(self):
        """Should record success."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        sync.record_success()

        assert sync.result.success_count == 1

    def test_record_failure(self):
        """Should record failure."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        sync.record_failure()

        assert sync.result.failed_count == 1

    def test_record_skipped_robots(self):
        """Should record skipped robots."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        sync.record_skipped_robots()

        assert sync.result.skipped_robots == 1

    def test_record_skipped_binary(self):
        """Should record skipped binary."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        sync.record_skipped_binary()

        assert sync.result.skipped_binary == 1

    def test_record_skipped_unchanged(self):
        """Should record skipped unchanged."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        sync.record_skipped_unchanged()

        assert sync.result.skipped_unchanged == 1


class TestSyncEntityShouldSkip:
    """Tests for should_skip_url method."""

    def test_skip_robots(self):
        """Should skip when robots not allowed."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        should_skip, reason = sync.should_skip_url(
            "https://example.com/page.html",
            robots_allowed=False,
            is_binary=False,
            is_unchanged=False,
        )

        assert should_skip is True
        assert reason == "robots"

    def test_skip_binary(self):
        """Should skip binary content."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        should_skip, reason = sync.should_skip_url(
            "https://example.com/image.png",
            robots_allowed=True,
            is_binary=True,
            is_unchanged=False,
        )

        assert should_skip is True
        assert reason == "binary"

    def test_skip_unchanged(self):
        """Should skip unchanged pages."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        should_skip, reason = sync.should_skip_url(
            "https://example.com/page.html",
            robots_allowed=True,
            is_binary=False,
            is_unchanged=True,
        )

        assert should_skip is True
        assert reason == "unchanged"

    def test_skip_pattern_no_match(self):
        """Should skip when pattern doesn't match."""
        config = SyncConfig(url="https://example.com", pattern=r"/docs/.*")
        sync = Sync(config)

        should_skip, reason = sync.should_skip_url(
            "https://example.com/about.html",
            robots_allowed=True,
            is_binary=False,
            is_unchanged=False,
        )

        assert should_skip is True
        assert reason == "pattern"

    def test_no_skip(self):
        """Should not skip when all conditions met."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        should_skip, reason = sync.should_skip_url(
            "https://example.com/page.html",
            robots_allowed=True,
            is_binary=False,
            is_unchanged=False,
        )

        assert should_skip is False
        assert reason == ""


class TestSyncEntityComputePath:
    """Tests for compute_path method."""

    def test_basic_path(self):
        """Should compute basic path correctly."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        path = sync.compute_path(
            "https://example.com/docs/page.html",
            Path("/tmp/pages"),
        )

        assert "page.html" in str(path)

    def test_index_path(self):
        """Should handle index paths."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        path = sync.compute_path(
            "https://example.com/docs/",
            Path("/tmp/pages"),
        )

        assert "index.html" in str(path)

    def test_root_path(self):
        """Should handle root path."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        path = sync.compute_path(
            "https://example.com",
            Path("/tmp/pages"),
        )

        assert "index.html" in str(path)


class TestSyncEntityStaticMethods:
    """Tests for static methods."""

    def test_normalize_url_absolute(self):
        """Should return absolute URL as-is."""
        result = Sync.normalize_url("https://example.com/page.html", "https://other.com")
        assert result == "https://example.com/page.html"

    def test_normalize_url_relative(self):
        """Should handle relative paths."""
        result = Sync.normalize_url("page.html", "https://example.com/docs/")
        assert "page.html" in result
        assert "example.com" in result

    def test_normalize_url_absolute_path(self):
        """Should handle absolute paths."""
        result = Sync.normalize_url("/about", "https://example.com/docs/")
        assert "/about" in result
        assert "example.com" in result

    def test_extract_domain_simple(self):
        """Should extract simple domain."""
        result = Sync.extract_domain("https://example.com/page")
        assert result == "example_com"

    def test_extract_domain_with_port(self):
        """Should handle port in domain."""
        result = Sync.extract_domain("https://localhost:8080/page")
        assert result == "localhost_8080"


class TestSyncEntityFilterAndLimit:
    """Tests for filter and limit methods."""

    def test_filter_urls_no_pattern(self):
        """Should return all URLs when no pattern."""
        config = SyncConfig(url="https://example.com")
        sync = Sync(config)

        urls = ["a.html", "b.html", "c.html"]
        result = sync.filter_urls(urls)

        assert result == urls

    def test_filter_urls_with_pattern(self):
        """Should filter by pattern."""
        config = SyncConfig(url="https://example.com", pattern=r"docs/.*")
        sync = Sync(config)

        urls = ["docs/page.html", "about.html", "docs/api.html"]
        result = sync.filter_urls(urls)

        assert len(result) == 2
        assert "docs/page.html" in result
        assert "docs/api.html" in result

    def test_limit_urls(self):
        """Should limit URLs."""
        config = SyncConfig(url="https://example.com", max_pages=2)
        sync = Sync(config)

        urls = ["a.html", "b.html", "c.html"]
        result = sync.limit_urls(urls)

        assert len(result) == 2
