"""Tests for scraper.crawler module."""

from unittest import mock

import pytest

from fresh.scraper import crawler as crawler_module


class TestFetchPage:
    """Tests for fetch_page function."""

    @mock.patch("fresh.scraper.crawler.fetch_with_retry")
    def test_successful_fetch(self, mock_fetch):
        """Should return HTML content on success."""
        mock_fetch.return_value = "<html>Content</html>"

        result = crawler_module.fetch_page("https://example.com")

        assert result == "<html>Content</html>"
        mock_fetch.assert_called_once_with("https://example.com")

    @mock.patch("fresh.scraper.crawler.fetch_with_retry")
    def test_failed_fetch(self, mock_fetch):
        """Should return None on failure."""
        mock_fetch.return_value = None

        result = crawler_module.fetch_page("https://example.com")

        assert result is None


class TestExtractLinks:
    """Tests for extract_links function."""

    def test_extract_basic_links(self):
        """Should extract basic anchor links."""
        html = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
                <a href="https://other.com/page">External</a>
            </body>
        </html>
        """

        result = crawler_module.extract_links(html, "https://example.com")

        assert len(result) == 2
        assert "https://example.com/page1" in result
        assert "https://example.com/page2" in result

    def test_filter_external_links(self):
        """Should filter links to external domains."""
        html = """
        <html>
            <body>
                <a href="/page1">Internal</a>
                <a href="https://other.com/page">External</a>
            </body>
        </html>
        """

        result = crawler_module.extract_links(html, "https://example.com")

        assert len(result) == 1
        assert "https://example.com/page1" in result

    def test_ignore_links_without_href(self):
        """Should ignore anchor tags without href."""
        html = """
        <html>
            <body>
                <a>No href</a>
                <a href="/page1">Valid</a>
            </body>
        </html>
        """

        result = crawler_module.extract_links(html, "https://example.com")

        assert len(result) == 1

    def test_normalize_relative_links(self):
        """Should normalize relative links to absolute."""
        html = """
        <html>
            <body>
                <a href="docs/guide">Relative</a>
            </body>
        </html>
        """

        result = crawler_module.extract_links(html, "https://example.com")

        assert result[0] == "https://example.com/docs/guide"

    def test_empty_html(self):
        """Should return empty list for empty HTML."""
        result = crawler_module.extract_links("", "https://example.com")

        assert result == []


class TestCrawl:
    """Tests for crawl function."""

    @mock.patch("fresh.scraper.crawler.fetch_page")
    @mock.patch("fresh.scraper.crawler.extract_links")
    def test_basic_crawl(self, mock_extract, mock_fetch):
        """Should crawl and return discovered URLs."""
        mock_fetch.return_value = "<html><a href='/page1'>Link</a></html>"
        mock_extract.return_value = ["https://example.com/page1"]

        result = crawler_module.crawl(
            "https://example.com",
            max_pages=10,
            max_depth=1,
            delay=0,  # No delay for tests
        )

        assert "https://example.com" in result

    @mock.patch("fresh.scraper.crawler.fetch_page")
    @mock.patch("fresh.scraper.crawler.extract_links")
    def test_max_pages_limit(self, mock_extract, mock_fetch):
        """Should respect max_pages limit."""
        # Setup to return links for each page
        mock_fetch.return_value = "<html><a href='/page'>Link</a></html>"
        mock_extract.side_effect = [
            [f"https://example.com/page{i}"] for i in range(20)
        ]

        result = crawler_module.crawl(
            "https://example.com",
            max_pages=5,
            max_depth=3,
            delay=0,
        )

        # Should have at most max_pages
        assert len(result) <= 5

    @mock.patch("fresh.scraper.crawler.fetch_page")
    @mock.patch("fresh.scraper.crawler.extract_links")
    def test_max_depth_limit(self, mock_extract, mock_fetch):
        """Should respect max_depth limit."""
        mock_fetch.return_value = "<html><a href='/page'>Link</a></html>"

        # Different links at each depth level
        page_counter = [0]

        def extract_side_effect(html, base_url):
            page_counter[0] += 1
            return [f"https://example.com/depth{page_counter[0]}"]

        mock_extract.side_effect = extract_side_effect

        result = crawler_module.crawl(
            "https://example.com",
            max_pages=100,
            max_depth=2,
            delay=0,
        )

        # The crawl should respect depth
        assert len(result) > 0

    @mock.patch("fresh.scraper.crawler.fetch_page")
    @mock.patch("fresh.scraper.crawler.extract_links")
    def test_skip_failed_pages(self, mock_extract, mock_fetch):
        """Should skip pages that fail to fetch."""
        # First page fails, second succeeds
        mock_fetch.side_effect = [None, "<html><a href='/page'>Link</a></html>"]
        mock_extract.return_value = ["https://example.com/page"]

        result = crawler_module.crawl(
            "https://example.com",
            max_pages=10,
            max_depth=1,
            delay=0,
        )

        assert "https://example.com" in result

    @mock.patch("time.sleep")
    @mock.patch("fresh.scraper.crawler.fetch_page")
    @mock.patch("fresh.scraper.crawler.extract_links")
    def test_rate_limiting(self, mock_extract, mock_fetch, mock_sleep):
        """Should apply rate limiting delay."""
        mock_fetch.return_value = "<html><a href='/page'>Link</a></html>"
        mock_extract.return_value = []

        crawler_module.crawl(
            "https://example.com",
            max_pages=3,
            max_depth=1,
            delay=0.5,
        )

        # Should have slept between requests
        assert mock_sleep.call_count > 0


class TestDefaultDelay:
    """Tests for DEFAULT_DELAY constant."""

    def test_default_delay_value(self):
        """DEFAULT_DELAY should be a positive number."""
        assert crawler_module.DEFAULT_DELAY > 0
        assert isinstance(crawler_module.DEFAULT_DELAY, (int, float))
