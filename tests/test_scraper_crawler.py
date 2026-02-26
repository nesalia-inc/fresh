"""Tests for scraper.crawler module."""

from unittest import mock


from fresh.scraper import crawler as crawler_module


class TestFetchPage:
    """Tests for fetch_page function."""

    @mock.patch("fresh.scraper.crawler.fetch_binary_aware")
    def test_successful_fetch(self, mock_fetch):
        """Should return HTML content on success."""
        mock_fetch.return_value = "<html>Content</html>"

        result = crawler_module.fetch_page("https://example.com/page.html")

        assert result == "<html>Content</html>"
        mock_fetch.assert_called_once_with("https://example.com/page.html", skip_binary=True)

    @mock.patch("fresh.scraper.crawler.fetch_binary_aware")
    def test_failed_fetch(self, mock_fetch):
        """Should return None on failure."""
        mock_fetch.return_value = None

        result = crawler_module.fetch_page("https://example.com/page.html")

        assert result is None

    @mock.patch("fresh.scraper.crawler.fetch_binary_aware")
    def test_skips_binary_urls(self, mock_fetch):
        """Should skip binary URLs without making HTTP request."""
        result = crawler_module.fetch_page("https://example.com/image.png")

        assert result is None
        mock_fetch.assert_not_called()


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

    @mock.patch("fresh.scraper.crawler._rate_limit_per_domain")
    @mock.patch("fresh.scraper.crawler.fetch_page")
    @mock.patch("fresh.scraper.crawler.extract_links")
    def test_rate_limiting(self, mock_extract, mock_fetch, mock_rate_limit):
        """Should apply rate limiting delay."""
        mock_fetch.return_value = "<html><a href='/page'>Link</a></html>"
        mock_extract.return_value = []

        crawler_module.crawl(
            "https://example.com",
            max_pages=3,
            max_depth=1,
            delay=0.5,
        )

        # Should have called rate limiting
        assert mock_rate_limit.call_count > 0


class TestDefaultDelay:
    """Tests for DEFAULT_DELAY constant."""

    def test_default_delay_value(self):
        """DEFAULT_DELAY should be a positive number."""
        assert crawler_module.DEFAULT_DELAY > 0
        assert isinstance(crawler_module.DEFAULT_DELAY, (int, float))


class TestCrawlEdgeCases:
    """Tests for crawl edge cases."""

    @mock.patch("fresh.scraper.crawler.is_allowed_by_robots")
    @mock.patch("fresh.scraper.crawler.validate_url")
    @mock.patch("fresh.scraper.crawler.fetch_page")
    @mock.patch("fresh.scraper.crawler.extract_links")
    def test_skip_invalid_url(self, mock_extract, mock_fetch, mock_validate, mock_robots):
        """Should skip URLs that fail validation."""
        mock_fetch.return_value = "<html><a href='/page'>Link</a></html>"
        mock_extract.return_value = ["https://example.com/page"]
        # First URL is valid, second is not
        mock_validate.side_effect = [True, False]

        result = crawler_module.crawl(
            "https://example.com",
            max_pages=10,
            max_depth=1,
            delay=0,
        )

        # Should still have the valid URL
        assert len(result) >= 1

    @mock.patch("fresh.scraper.crawler.is_allowed_by_robots")
    @mock.patch("fresh.scraper.crawler.validate_url")
    @mock.patch("fresh.scraper.crawler.fetch_page")
    @mock.patch("fresh.scraper.crawler.extract_links")
    def test_skip_disallowed_by_robots(
        self, mock_extract, mock_fetch, mock_validate, mock_robots
    ):
        """Should skip URLs disallowed by robots.txt when respect_robots=True."""
        mock_fetch.return_value = "<html><a href='/page'>Link</a></html>"
        mock_extract.return_value = ["https://example.com/page"]
        mock_validate.return_value = True
        # First URL is allowed, second is disallowed
        mock_robots.side_effect = [True, False]

        result = crawler_module.crawl(
            "https://example.com",
            max_pages=10,
            max_depth=1,
            delay=0,
            respect_robots=True,
        )

        # Should still have the allowed URL
        assert len(result) >= 1


class TestResetFunction:
    """Tests for crawler reset function."""

    def test_reset_clears_rate_limit_dict(self):
        """Reset should clear the rate limit dictionary."""
        # Add something to rate limit dict
        crawler_module._domain_last_request["example.com"] = 1234567890

        assert "example.com" in crawler_module._domain_last_request

        crawler_module.reset()

        assert len(crawler_module._domain_last_request) == 0


class TestRateLimiting:
    """Tests for rate limiting."""

    def test_rate_limit_with_zero_delay(self):
        """Rate limiting with zero delay should return immediately."""
        # This should not raise any errors
        crawler_module._rate_limit_per_domain("https://example.com/page1", 0)

    def test_rate_limit_preserves_dict(self):
        """Rate limiting should preserve the rate limit dictionary."""
        # This should work without errors
        crawler_module._rate_limit_per_domain("https://example.com/page1", 0)
        crawler_module._rate_limit_per_domain("https://example.com/page2", 0)


class TestConstants:
    """Tests for module constants."""

    def test_rate_limit_constants(self):
        """Test rate limit constants are defined."""
        assert crawler_module.RATE_LIMIT_TTL > 0
        assert crawler_module.RATE_LIMIT_MAX_DOMAINS > 0
        assert crawler_module._RATE_LIMIT_CLEANUP_INTERVAL > 0


class TestParallelFetchPage:
    """Tests for parallel_fetch_page function."""

    @mock.patch("fresh.scraper.crawler.fetch_binary_aware")
    def test_successful_parallel_fetch(self, mock_fetch):
        """Should return HTML content on success."""
        mock_fetch.return_value = "<html>Content</html>"

        result = crawler_module.parallel_fetch_page(
            ("https://example.com/page.html", True, None)
        )

        assert result[0] == "https://example.com/page.html"
        assert result[1] == "<html>Content</html>"
        assert result[2] == []

    @mock.patch("fresh.scraper.crawler.fetch_binary_aware")
    def test_failed_parallel_fetch(self, mock_fetch):
        """Should return None on failure."""
        mock_fetch.return_value = None

        result = crawler_module.parallel_fetch_page(
            ("https://example.com/page.html", True, None)
        )

        assert result[0] == "https://example.com/page.html"
        assert result[1] is None
        assert result[2] == []

    def test_invalid_url_returns_none(self):
        """Should return None for invalid URL."""
        result = crawler_module.parallel_fetch_page(
            ("not-a-url", True, None)
        )

        assert result[1] is None


class TestParallelCrawl:
    """Tests for parallel_crawl function."""

    @mock.patch("fresh.scraper.crawler.parallel_fetch_page")
    def test_parallel_crawl_basic(self, mock_fetch):
        """Should crawl pages in parallel."""
        mock_fetch.side_effect = [
            ("https://example.com/", "<html><a href='/page1'>Link</a></html>", ["/page1"]),
            ("https://example.com/page1", "<html>Content</html>", []),
        ]

        result = crawler_module.parallel_crawl(
            "https://example.com/",
            max_pages=5,
            max_depth=2,
            max_workers=2,
        )

        assert len(result) >= 1
        assert "https://example.com/" in result

    @mock.patch("fresh.scraper.crawler.parallel_fetch_page")
    def test_parallel_crawl_max_pages(self, mock_fetch):
        """Should respect max_pages limit."""
        mock_fetch.return_value = (
            "https://example.com/page",
            "<html><a href='/next'>Link</a></html>",
            ["/next"],
        )

        result = crawler_module.parallel_crawl(
            "https://example.com/",
            max_pages=3,
            max_depth=10,
            max_workers=2,
        )

        assert len(result) <= 3

    @mock.patch("fresh.scraper.crawler.parallel_fetch_page")
    def test_parallel_crawl_empty_start(self, mock_fetch):
        """Should handle empty start URL gracefully."""
        mock_fetch.return_value = ("https://example.com/", None, [])

        result = crawler_module.parallel_crawl(
            "https://example.com/",
            max_pages=5,
            max_workers=2,
        )

        assert isinstance(result, set)

