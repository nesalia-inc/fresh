"""Tests for scraper.sitemap module."""

from unittest import mock


from fresh.scraper import sitemap as sitemap_module


class TestDiscoverSitemap:
    """Tests for discover_sitemap function."""

    @mock.patch("fresh.scraper.sitemap.get_client")
    @mock.patch("fresh.scraper.sitemap.fetch_with_retry")
    def test_find_sitemap_at_common_location(self, mock_fetch_retry, mock_get_client):
        """Should find sitemap at common location using HEAD request."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_client = mock.MagicMock()
        mock_client.head.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = sitemap_module.discover_sitemap("https://example.com")

        assert result == "https://example.com/sitemap.xml"
        mock_client.head.assert_called()

    @mock.patch("fresh.scraper.sitemap.get_client")
    @mock.patch("fresh.scraper.sitemap.fetch_with_retry")
    def test_find_sitemap_in_robots(self, mock_fetch_retry, mock_get_client):
        """Should find sitemap in robots.txt when HEAD returns 404."""
        mock_response_404 = mock.MagicMock()
        mock_response_404.status_code = 404
        mock_client = mock.MagicMock()
        mock_client.head.return_value = mock_response_404
        mock_get_client.return_value = mock_client
        # Second fetch (for robots.txt) returns content
        mock_fetch_retry.return_value = "Sitemap: https://example.com/sitemap-index.xml"

        result = sitemap_module.discover_sitemap("https://example.com")

        assert result == "https://example.com/sitemap-index.xml"

    @mock.patch("fresh.scraper.sitemap.get_client")
    @mock.patch("fresh.scraper.sitemap.fetch_with_retry")
    def test_no_sitemap_found(self, mock_fetch_retry, mock_get_client):
        """Should return None when no sitemap found."""
        mock_response_404 = mock.MagicMock()
        mock_response_404.status_code = 404
        mock_client = mock.MagicMock()
        mock_client.head.return_value = mock_response_404
        mock_get_client.return_value = mock_client
        mock_fetch_retry.return_value = None

        result = sitemap_module.discover_sitemap("https://example.com")

        assert result is None


class TestParseSitemap:
    """Tests for parse_sitemap function."""

    def test_parse_regular_sitemap(self):
        """Should parse regular sitemap XML."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
            <url>
                <loc>https://example.com/page2</loc>
            </url>
        </urlset>"""

        result = sitemap_module.parse_sitemap(xml)

        assert result is not None
        assert len(result) == 2
        assert "https://example.com/page1" in result

    def test_parse_sitemap_index(self):
        """Should parse sitemap index."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://example.com/sitemap1.xml</loc>
            </sitemap>
            <sitemap>
                <loc>https://example.com/sitemap2.xml</loc>
            </sitemap>
        </sitemapindex>"""

        result = sitemap_module.parse_sitemap(xml)

        assert result is not None
        assert len(result) == 2
        assert "https://example.com/sitemap1.xml" in result

    def test_parse_invalid_xml(self):
        """Should return None for invalid XML."""
        result = sitemap_module.parse_sitemap("not valid xml")

        assert result is None

    def test_parse_empty_sitemap(self):
        """Should return None for empty sitemap."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        </urlset>"""

        result = sitemap_module.parse_sitemap(xml)

        assert result is None


class TestNormalizeUrls:
    """Tests for normalize_urls function."""

    def test_absolute_urls_unchanged(self):
        """Absolute URLs should remain unchanged."""
        urls = ["https://example.com/page1", "https://example.com/page2"]
        result = sitemap_module.normalize_urls(urls, "https://base.com")

        assert result == urls

    def test_relative_urls_made_absolute(self):
        """Relative URLs should be made absolute."""
        urls = ["/docs/guide", "/api/users"]
        result = sitemap_module.normalize_urls(urls, "https://example.com")

        assert result[0] == "https://example.com/docs/guide"
        assert result[1] == "https://example.com/api/users"

    def test_relative_paths_appended(self):
        """Relative paths should be appended to base."""
        urls = ["page1", "page2"]
        result = sitemap_module.normalize_urls(urls, "https://example.com/docs")

        assert result[0] == "https://example.com/docs/page1"
        assert result[1] == "https://example.com/docs/page2"

    def test_protocol_relative_urls(self):
        """Protocol-relative URLs should be made absolute."""
        urls = ["//cdn.example.com/script.js"]
        result = sitemap_module.normalize_urls(urls, "https://example.com")

        assert result[0] == "https://cdn.example.com/script.js"

    def test_empty_urls_filtered(self):
        """Empty URLs should be filtered out."""
        urls = ["", "https://example.com/page", ""]
        result = sitemap_module.normalize_urls(urls, "https://example.com")

        assert len(result) == 1

    def test_whitespace_trimmed(self):
        """Whitespace should be trimmed."""
        urls = ["  /page1  ", "/page2"]
        result = sitemap_module.normalize_urls(urls, "https://example.com")

        assert result[0] == "https://example.com/page1"
        assert result[1] == "https://example.com/page2"

    def test_trailing_slash_preserved(self):
        """Trailing slash in base should be handled."""
        urls = ["/page"]
        result = sitemap_module.normalize_urls(urls, "https://example.com/")

        assert result[0] == "https://example.com/page"
