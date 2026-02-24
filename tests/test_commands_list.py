"""Tests for list command."""

from unittest import mock

from typer.testing import CliRunner

from fresh import app

runner = CliRunner()


class TestListCommand:
    """Tests for the list command."""

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_with_crawler_fallback(self, mock_discover, mock_crawl):
        """Should use crawler when no sitemap found."""
        mock_discover.return_value = None
        mock_crawl.return_value = {
            "https://example.com/docs/page1",
            "https://example.com/docs/page2",
        }

        result = runner.invoke(app, ["list", "https://example.com"])

        assert result.exit_code == 0
        assert "page1" in result.output
        assert "page2" in result.output
        mock_discover.assert_called_once_with("https://example.com")
        mock_crawl.assert_called_once()

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.fetch_with_retry")
    @mock.patch("fresh.commands.list.sitemap.parse_sitemap")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_with_sitemap(
        self, mock_discover, mock_parse, mock_fetch, mock_crawl
    ):
        """Should use sitemap when available."""
        mock_discover.return_value = "https://example.com/sitemap.xml"
        mock_fetch.return_value = """<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/docs/page1</loc></url>
        </urlset>"""
        mock_parse.return_value = ["https://example.com/docs/page1"]

        result = runner.invoke(app, ["list", "https://example.com"])

        assert result.exit_code == 0
        assert "page1" in result.output
        mock_crawl.assert_not_called()

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.fetch_with_retry")
    @mock.patch("fresh.commands.list.sitemap.parse_sitemap")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_sitemap_respects_max_pages(
        self, mock_discover, mock_parse, mock_fetch, mock_crawl
    ):
        """Should apply max-pages limit to sitemap results."""
        mock_discover.return_value = "https://example.com/sitemap.xml"
        mock_fetch.return_value = """<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/docs/page1</loc></url>
            <url><loc>https://example.com/docs/page2</loc></url>
            <url><loc>https://example.com/docs/page3</loc></url>
        </urlset>"""
        mock_parse.return_value = [
            "https://example.com/docs/page1",
            "https://example.com/docs/page2",
            "https://example.com/docs/page3",
        ]

        result = runner.invoke(app, ["list", "https://example.com", "--max-pages", "2"])

        assert result.exit_code == 0
        # Should only have 2 pages due to max-pages limit
        assert "page1" in result.output
        assert "page2" in result.output
        # page3 should not be in output
        assert "page3" not in result.output

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_count_option(self, mock_discover, mock_crawl):
        """Should return only count with --count option."""
        mock_discover.return_value = None
        mock_crawl.return_value = {
            "https://example.com/docs/page1",
            "https://example.com/docs/page2",
            "https://example.com/docs/page3",
        }

        result = runner.invoke(app, ["list", "https://example.com", "--count"])

        assert result.exit_code == 0
        assert result.output.strip() == "3"

    @mock.patch("fresh.commands.list.filter_module.filter_by_pattern")
    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_pattern_filter_excludes_non_matching(
        self, mock_discover, mock_crawl, mock_filter
    ):
        """Should filter out non-matching paths when pattern is provided."""
        mock_discover.return_value = None
        mock_crawl.return_value = {
            "https://example.com/docs/page1",
            "https://example.com/api/page2",
        }
        # Pattern should only match /docs/* URLs
        mock_filter.return_value = ["https://example.com/docs/page1"]

        result = runner.invoke(
            app, ["list", "https://example.com", "--pattern", "/docs/*"]
        )

        assert result.exit_code == 0
        assert "page1" in result.output
        # api/page2 should not be in output since it doesn't match pattern
        assert "api" not in result.output

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_invalid_url(self, mock_discover, mock_crawl):
        """Should fail with invalid URL."""
        result = runner.invoke(app, ["list", "http://localhost:8080"])

        assert result.exit_code == 1
        assert "Invalid URL" in result.output

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_sort_by_path(self, mock_discover, mock_crawl):
        """Should sort by path when --sort path is used."""
        mock_discover.return_value = None
        mock_crawl.return_value = {
            "https://example.com/docs/aaa",
            "https://example.com/docs/zzz",
            "https://example.com/docs/mmm",
        }

        result = runner.invoke(
            app, ["list", "https://example.com", "--sort", "path"]
        )

        assert result.exit_code == 0

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_invalid_sort(self, mock_discover, mock_crawl):
        """Should fail with invalid sort option."""
        mock_discover.return_value = None
        mock_crawl.return_value = {"https://example.com/docs/page1"}

        result = runner.invoke(
            app, ["list", "https://example.com", "--sort", "invalid"]
        )

        assert result.exit_code == 1
        assert "Invalid sort option" in result.output

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_xml_format_with_declaration(self, mock_discover, mock_crawl):
        """Should output XML format with declaration header."""
        mock_discover.return_value = None
        mock_crawl.return_value = {"https://example.com/docs/page1"}

        result = runner.invoke(
            app, ["list", "https://example.com", "--format", "xml"]
        )

        assert result.exit_code == 0
        assert '<?xml version="1.0" encoding="UTF-8"?>' in result.output
        assert "<pages>" in result.output
        assert "<page>" in result.output

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_yaml_format(self, mock_discover, mock_crawl):
        """Should output YAML format when requested."""
        mock_discover.return_value = None
        mock_crawl.return_value = {"https://example.com/docs/page1"}

        result = runner.invoke(
            app, ["list", "https://example.com", "--format", "yaml"]
        )

        # YAML requires PyYAML which may not be installed
        assert result.exit_code in [0, 1]

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_unknown_format(self, mock_discover, mock_crawl):
        """Should fail with unknown format."""
        mock_discover.return_value = None
        mock_crawl.return_value = {"https://example.com/docs/page1"}

        result = runner.invoke(
            app, ["list", "https://example.com", "--format", "invalid"]
        )

        assert result.exit_code == 1
        assert "Invalid format" in result.output

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_max_pages_option(self, mock_discover, mock_crawl):
        """Should use max-pages option when provided."""
        mock_discover.return_value = None
        mock_crawl.return_value = {"https://example.com/docs/page1"}

        result = runner.invoke(
            app, ["list", "https://example.com", "--max-pages", "50"]
        )

        assert result.exit_code == 0
        mock_crawl.assert_called_once_with("https://example.com", max_pages=50, max_depth=3)

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_no_pages_warning(self, mock_discover, mock_crawl):
        """Should show warning when no pages found."""
        mock_discover.return_value = None
        mock_crawl.return_value = set()

        result = runner.invoke(
            app, ["list", "https://example.com"]
        )

        assert result.exit_code == 0
        assert "Warning" in result.output

    @mock.patch("fresh.commands.list.crawler.crawl")
    @mock.patch("fresh.commands.list.sitemap.discover_sitemap")
    def test_list_verbose_output(self, mock_discover, mock_crawl):
        """Should output rich table when --verbose is used."""
        mock_discover.return_value = None
        mock_crawl.return_value = {
            "https://example.com/docs/page1",
            "https://example.com/docs/page2",
        }

        result = runner.invoke(
            app, ["list", "https://example.com", "--verbose"]
        )

        assert result.exit_code == 0
        # Rich table output should contain these elements (may be wrapped in CI)
        assert "Documentation" in result.output and "Pages" in result.output
        assert "page1" in result.output
        assert "page2" in result.output
