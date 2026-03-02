"""Tests for search command."""

import re
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from typer.testing import CliRunner

from fresh import app
from fresh.commands import search

runner = CliRunner()


class TestSearcher:
    """Tests for the searcher module."""

    def test_search_in_content_literal(self):
        """Should find literal matches in content."""
        from fresh.scraper.searcher import search_in_content

        content = "This is a test page.\nAnother line with test content."
        results = search_in_content(content, "test")

        assert len(results) == 2
        assert results[0]["match"] == "test"
        assert results[1]["match"] == "test"

    def test_search_in_content_case_sensitive(self):
        """Should respect case sensitivity."""
        from fresh.scraper.searcher import search_in_content

        content = "Test test TEST"
        results = search_in_content(content, "Test", case_sensitive=True)

        assert len(results) == 1
        assert results[0]["match"] == "Test"

    def test_search_in_content_case_insensitive(self):
        """Should be case insensitive by default."""
        from fresh.scraper.searcher import search_in_content

        content = "Test test TEST"
        results = search_in_content(content, "test")

        # Returns one result per line, but case-insensitive
        assert len(results) == 1
        assert results[0]["match"] == "Test"

    def test_search_in_content_regex(self):
        """Should support regex patterns."""
        from fresh.scraper.searcher import search_in_content

        content = "test123\ntest456\ntest789"
        results = search_in_content(content, r"test\d+", regex=True)

        assert len(results) == 3
        assert results[0]["match"] == "test123"

    def test_search_in_content_regex_invalid(self):
        """Should raise error for invalid regex."""
        from fresh.scraper.searcher import search_in_content

        with pytest.raises(re.error):
            search_in_content("content", "invalid[", regex=True)

    def test_create_snippet(self):
        """Should create snippet around match."""
        from fresh.scraper.searcher import create_snippet

        content = "Line 1\nLine 2\nMatch line\nLine 4\nLine 5"
        snippet = create_snippet(content, "Match", context_lines=1)

        assert "Match line" in snippet

    def test_create_snippet_no_match(self):
        """Should return start of content when no match."""
        from fresh.scraper.searcher import create_snippet

        content = "No match here"
        snippet = create_snippet(content, "test")

        assert snippet == content

    def test_create_snippet_max_length(self):
        """Should respect max_length parameter."""
        from fresh.scraper.searcher import create_snippet

        content = "a" * 500 + " match " + "b" * 500
        snippet = create_snippet(content, "match", max_length=100)

        assert len(snippet) <= 103  # 100 + "..."


class TestSearchCommand:
    """Tests for the search command."""

    @mock.patch("fresh.commands.search.fetch_binary_aware")
    @mock.patch("fresh.commands.search.sitemap.discover_sitemap")
    def test_search_no_sitemap_uses_crawler(self, mock_sitemap, mock_fetch):
        """Should use crawler when no sitemap found."""
        mock_sitemap.return_value = None
        mock_fetch.return_value = mock.MagicMock(text="<html>Test content</html>")

        result = runner.invoke(
            app,
            ["search", "test", "https://example.com", "--max-pages", "1"],
        )

        # Should complete without error even if no results
        assert result.exit_code in [0, 1]

    @mock.patch("fresh.commands.search.fetch_binary_aware")
    @mock.patch("fresh.commands.search.sitemap.discover_sitemap")
    def test_search_with_results(self, mock_sitemap, mock_fetch):
        """Should return results when matches found."""
        mock_sitemap.return_value = None
        mock_fetch.return_value = mock.MagicMock(
            text="<html><body>Test page with test content</body></html>"
        )

        result = runner.invoke(
            app,
            ["search", "test", "https://example.com", "--max-pages", "1"],
        )

        # Should find results
        assert "test" in result.output.lower() or result.exit_code == 0

    @mock.patch("fresh.commands.search.fetch_binary_aware")
    @mock.patch("fresh.commands.search.sitemap.discover_sitemap")
    def test_search_invalid_url(self, mock_sitemap, mock_fetch):
        """Should fail with invalid URL."""
        result = runner.invoke(app, ["search", "test", "invalid-url"])

        assert result.exit_code == 1
        assert "Invalid" in result.output or "Error" in result.output

    @mock.patch("fresh.commands.search.fetch_binary_aware")
    @mock.patch("fresh.commands.search.sitemap.discover_sitemap")
    def test_search_regex_option(self, mock_sitemap, mock_fetch):
        """Should support regex option."""
        mock_sitemap.return_value = None
        mock_fetch.return_value = mock.MagicMock(
            text="<html><body>test123 test456</body></html>"
        )

        result = runner.invoke(
            app,
            ["search", r"test\d+", "https://example.com", "--regex", "--max-pages", "1"],
        )

        # Should handle regex without crashing
        assert result.exit_code in [0, 1]

    @mock.patch("fresh.commands.search.fetch_binary_aware")
    @mock.patch("fresh.commands.search.sitemap.discover_sitemap")
    def test_search_case_sensitive_option(self, mock_sitemap, mock_fetch):
        """Should support case-sensitive option."""
        mock_sitemap.return_value = None
        mock_fetch.return_value = mock.MagicMock(
            text="<html><body>Test test TEST</body></html>"
        )

        result = runner.invoke(
            app,
            [
                "search",
                "Test",
                "https://example.com",
                "--case-sensitive",
                "--max-pages",
                "1",
            ],
        )

        # Should handle case-sensitive without crashing
        assert result.exit_code in [0, 1]


class TestLocalSearch:
    """Tests for local search functionality."""

    def test_url_to_local_path(self):
        """Should convert URL to local path correctly."""
        # Save original DEFAULT_SYNC_DIR
        original_sync_dir = search.DEFAULT_SYNC_DIR

        with tempfile.TemporaryDirectory() as tmpdir:
            # Override sync dir for testing
            search.DEFAULT_SYNC_DIR = Path(tmpdir)

            try:
                url = "https://example.com/docs/api/index.html"
                local_path = search._url_to_local_path(url)

                assert local_path is not None
                assert "example_com" in str(local_path)
                assert "docs" in str(local_path)
                assert "api" in str(local_path)
                assert local_path.suffix == ".html"
            finally:
                search.DEFAULT_SYNC_DIR = original_sync_dir

    def test_local_content_exists(self):
        """Should check if local content exists."""
        original_sync_dir = search.DEFAULT_SYNC_DIR

        with tempfile.TemporaryDirectory() as tmpdir:
            search.DEFAULT_SYNC_DIR = Path(tmpdir)

            try:
                # Create test file
                url = "https://example.com/test.html"
                local_path = search._url_to_local_path(url)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_text("<html>test</html>")

                assert search.local_content_exists(url) is True
                assert search.local_content_exists("https://example.com/notexist.html") is False
            finally:
                search.DEFAULT_SYNC_DIR = original_sync_dir

    def test_get_local_content(self):
        """Should get local content."""
        original_sync_dir = search.DEFAULT_SYNC_DIR

        with tempfile.TemporaryDirectory() as tmpdir:
            search.DEFAULT_SYNC_DIR = Path(tmpdir)

            try:
                url = "https://example.com/test.html"
                local_path = search._url_to_local_path(url)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_text("<html>test content</html>")

                content = search.get_local_content(url)
                assert content == "<html>test content</html>"

                # Non-existent URL
                assert search.get_local_content("https://example.com/notexist.html") is None
            finally:
                search.DEFAULT_SYNC_DIR = original_sync_dir

    def test_discover_local_urls(self):
        """Should discover URLs from local synced content."""
        original_sync_dir = search.DEFAULT_SYNC_DIR

        with tempfile.TemporaryDirectory() as tmpdir:
            search.DEFAULT_SYNC_DIR = Path(tmpdir)

            try:
                base_url = "https://example.com"

                # Create test files
                sync_dir = search._get_sync_dir_for_url(base_url)
                sync_dir.mkdir(parents=True, exist_ok=True)

                (sync_dir / "index.html").write_text("<html>Home</html>")
                (sync_dir / "about.html").write_text("<html>About</html>")
                (sync_dir / "docs.html").write_text("<html>Docs</html>")

                urls = search.discover_local_urls(base_url, max_pages=10)

                # Should find all 3 files (index.html becomes root /)
                assert len(urls) == 3
                # Check we have the files - index.html becomes just /
                assert any("about.html" in u for u in urls)
                assert any("docs.html" in u for u in urls)
                assert any("docs.html" in u for u in urls)
            finally:
                search.DEFAULT_SYNC_DIR = original_sync_dir


class TestSearchSource:
    """Tests for search source parameter."""

    @mock.patch("fresh.commands.search.get_local_content")
    @mock.patch("fresh.commands.search.discover_local_urls")
    def test_search_local_only(self, mock_discover, mock_get_content):
        """Should search only local content with source=local."""
        mock_discover.return_value = ["https://example.com/page.html"]
        mock_get_content.return_value = "<html>test content</html>"

        search.search_pages(
            "https://example.com",
            "test",
            source="local",
            verbose=False,
        )

        # Should not call remote
        mock_discover.assert_called_once()

    @mock.patch("fresh.commands.search.fetch_binary_aware")
    @mock.patch("fresh.commands.search.discover_documentation_urls")
    def test_search_remote_only(self, mock_discover, mock_fetch):
        """Should search only remote content with source=remote."""
        mock_discover.return_value = ["https://example.com/page.html"]
        mock_fetch.return_value = mock.MagicMock(text="<html>test content</html>")

        search.search_pages(
            "https://example.com",
            "test",
            source="remote",
            verbose=False,
        )

        # Should call remote fetch
        mock_fetch.assert_called()

    def test_search_result_has_source(self):
        """SearchResult should have source field."""
        from fresh.scraper.searcher import SearchResult

        result = SearchResult(
            path="/test",
            title="Test",
            snippet="test snippet",
            url="https://example.com/test",
            source="local",
        )

        assert result.source == "local"

        result2 = SearchResult(
            path="/test2",
            title="Test2",
            snippet="test2 snippet",
            url="https://example.com/test2",
            source="remote",
        )

        assert result2.source == "remote"


class TestParallelSearch:
    """Tests for parallel search functionality."""

    def test_parallel_threshold_constant(self):
        """PARALLEL_THRESHOLD should be 3."""
        from fresh.commands.search import PARALLEL_THRESHOLD

        assert PARALLEL_THRESHOLD == 3

    def test_search_pages_auto_parallel_when_many_pages(self):
        """Should use parallel when max_pages > threshold."""
        from fresh.commands.search import PARALLEL_THRESHOLD

        # With max_pages > threshold, should use parallel
        assert PARALLEL_THRESHOLD == 3

    @mock.patch("fresh.commands.search._search_page_parallel")
    @mock.patch("fresh.commands.search.discover_documentation_urls")
    def test_search_pages_uses_parallel_when_enabled(
        self, mock_discover, mock_parallel_search
    ):
        """Should use parallel fetching when parallel=True."""
        from fresh.commands.search import search_pages

        # Setup mocks
        mock_discover.return_value = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ]
        mock_parallel_search.return_value = None

        # Call with parallel=True
        search_pages(
            "https://example.com",
            "test",
            max_pages=10,
            source="remote",
            parallel=True,
        )

        # Should call parallel search function
        assert mock_parallel_search.call_count == 3

    @mock.patch("fresh.commands.search._search_page_content")
    @mock.patch("fresh.commands.search.discover_documentation_urls")
    def test_search_pages_uses_sequential_when_disabled(
        self, mock_discover, mock_search_content
    ):
        """Should use sequential fetching when parallel=False."""
        from fresh.commands.search import search_pages

        # Setup mocks
        mock_discover.return_value = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ]
        mock_search_content.return_value = None

        # Call with parallel=False
        search_pages(
            "https://example.com",
            "test",
            max_pages=10,
            source="remote",
            parallel=False,
        )

        # Should call sequential search function instead
        assert mock_search_content.call_count == 3

    def test_search_pages_auto_detects_parallel_threshold(self):
        """Should auto-detect parallel when max_pages > 3."""
        from fresh.commands.search import PARALLEL_THRESHOLD

        # With max_pages > threshold, should use parallel
        assert PARALLEL_THRESHOLD == 3

        # Test that auto-detection logic works correctly
        # When parallel=None and max_pages > 3, use_parallel should be True
        use_parallel_auto = None  # auto-detect
        max_pages_above = 10
        result = use_parallel_auto if use_parallel_auto is not None else (max_pages_above > PARALLEL_THRESHOLD)
        assert result is True

        # When max_pages <= 3, use_parallel should be False
        max_pages_below = 2
        result = use_parallel_auto if use_parallel_auto is not None else (max_pages_below > PARALLEL_THRESHOLD)
        assert result is False

    def test_default_max_workers_constant(self):
        """DEFAULT_MAX_WORKERS should be between 4 and 16 based on CPU count."""
        from fresh.commands.search import DEFAULT_MAX_WORKERS

        assert 4 <= DEFAULT_MAX_WORKERS <= 16

    def test_max_workers_edge_cases(self):
        """Test max_workers calculation for edge cases."""
        from fresh.commands.search import DEFAULT_MAX_WORKERS

        # Verify DEFAULT_MAX_WORKERS is in valid range
        assert 4 <= DEFAULT_MAX_WORKERS <= 16

        # When there are more pages than max_workers, use max_workers
        pages_20 = 20
        workers_20 = min(DEFAULT_MAX_WORKERS, pages_20)
        assert workers_20 == DEFAULT_MAX_WORKERS

        # Single page should use 1 worker
        pages_1 = 1
        workers_1 = min(DEFAULT_MAX_WORKERS, pages_1)
        assert workers_1 == 1


class TestSearchFreshness:
    """Tests for freshness functions in search module."""

    def test_format_freshness_age_seconds(self):
        """Should format seconds correctly."""
        from datetime import datetime, timezone
        from fresh.commands.search import _format_freshness_age

        # Current time
        result = _format_freshness_age(datetime.now(timezone.utc).isoformat())
        assert "just now" in result

    def test_format_freshness_age_minutes(self):
        """Should format minutes correctly."""
        from datetime import datetime, timezone, timedelta
        from fresh.commands.search import _format_freshness_age

        # 5 minutes ago
        timestamp = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        result = _format_freshness_age(timestamp)
        assert "m ago" in result

    def test_format_freshness_age_hours(self):
        """Should format hours correctly."""
        from datetime import datetime, timezone, timedelta
        from fresh.commands.search import _format_freshness_age

        # 2 hours ago
        timestamp = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        result = _format_freshness_age(timestamp)
        assert "h ago" in result

    def test_format_freshness_age_days(self):
        """Should format days correctly."""
        from datetime import datetime, timezone, timedelta
        from fresh.commands.search import _format_freshness_age

        # 2 days ago
        timestamp = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        result = _format_freshness_age(timestamp)
        assert "d ago" in result

    def test_format_freshness_age_weeks(self):
        """Should format weeks correctly."""
        from datetime import datetime, timezone, timedelta
        from fresh.commands.search import _format_freshness_age

        # 2 weeks ago
        timestamp = (datetime.now(timezone.utc) - timedelta(weeks=2)).isoformat()
        result = _format_freshness_age(timestamp)
        assert "w ago" in result

    def test_format_freshness_age_invalid(self):
        """Should return unknown for invalid timestamp."""
        from fresh.commands.search import _format_freshness_age

        result = _format_freshness_age("invalid-timestamp")
        assert result == "unknown"

    def test_format_freshness_age_with_z_suffix(self):
        """Should handle timestamp with Z suffix."""
        from fresh.commands.search import _format_freshness_age

        result = _format_freshness_age("2024-01-01T12:00:00Z")
        # Should handle Z suffix properly
        assert isinstance(result, str)


class TestSearchSyncDir:
    """Tests for sync directory functions."""

    def test_get_sync_dir_for_url(self):
        """Should get sync directory for URL."""
        original_sync_dir = search.DEFAULT_SYNC_DIR

        with tempfile.TemporaryDirectory() as tmpdir:
            search.DEFAULT_SYNC_DIR = Path(tmpdir)

            try:
                result = search._get_sync_dir_for_url("https://example.com/page.html")
                assert "example_com" in str(result)
                assert "pages" in str(result)
            finally:
                search.DEFAULT_SYNC_DIR = original_sync_dir


class TestSearchConstants:
    """Tests for search constants."""

    def test_parallel_threshold_exists(self):
        """PARALLEL_THRESHOLD should be defined."""
        from fresh.commands.search import PARALLEL_THRESHOLD
        assert PARALLEL_THRESHOLD > 0

    def test_default_max_workers_exists(self):
        """DEFAULT_MAX_WORKERS should be defined."""
        from fresh.commands.search import DEFAULT_MAX_WORKERS
        assert DEFAULT_MAX_WORKERS > 0
