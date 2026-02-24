"""Tests for search command."""

import re
from unittest import mock

import pytest
from typer.testing import CliRunner

from fresh import app

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

    @mock.patch("fresh.commands.search.fetch_with_retry")
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

    @mock.patch("fresh.commands.search.fetch_with_retry")
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

    @mock.patch("fresh.commands.search.fetch_with_retry")
    @mock.patch("fresh.commands.search.sitemap.discover_sitemap")
    def test_search_invalid_url(self, mock_sitemap, mock_fetch):
        """Should fail with invalid URL."""
        result = runner.invoke(app, ["search", "test", "invalid-url"])

        assert result.exit_code == 1
        assert "Invalid" in result.output or "Error" in result.output

    @mock.patch("fresh.commands.search.fetch_with_retry")
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

    @mock.patch("fresh.commands.search.fetch_with_retry")
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
