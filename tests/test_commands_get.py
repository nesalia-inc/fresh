"""Tests for get command."""

import tempfile
from pathlib import Path
from unittest import mock

from typer.testing import CliRunner

from fresh import app
from fresh.commands import get as get_module

runner = CliRunner()


class TestHtmlToMarkdown:
    """Tests for html_to_markdown function."""

    def test_basic_html_conversion(self):
        """Should convert basic HTML to Markdown."""
        html = "<h1>Hello</h1><p>World</p>"
        result = get_module.html_to_markdown(html)

        assert "# Hello" in result
        assert "World" in result

    def test_links_converted(self):
        """Should convert links to Markdown format."""
        html = '<a href="https://example.com">Link</a>'
        result = get_module.html_to_markdown(html)

        assert "[Link]" in result
        assert "https://example.com" in result

    def test_skip_scripts(self):
        """Should remove script tags when skip_scripts=True."""
        html = "<html><script>alert('test')</script><p>Content</p></html>"
        result = get_module.html_to_markdown(html, skip_scripts=True)

        assert "alert" not in result
        assert "Content" in result


class TestGetCommand:
    """Tests for the get command."""

    @mock.patch("fresh.commands.get.get_cached_content")
    @mock.patch("fresh.commands.get.fetch_with_retry")
    def test_get_invalid_url(self, mock_fetch, mock_cache):
        """Should fail with invalid URL."""
        result = runner.invoke(app, ["get", "http://localhost:8080"])

        assert result.exit_code == 1
        assert "Invalid URL" in result.output

    def test_get_dry_run(self):
        """Should show what would be fetched with --dry-run."""
        result = runner.invoke(app, ["get", "https://example.com", "--dry-run"])

        assert result.exit_code == 0
        assert "Would fetch" in result.output

    def test_get_invalid_header_format(self):
        """Should fail with invalid header format."""
        result = runner.invoke(
            app, ["get", "https://example.com", "--header", "invalid"]
        )

        assert result.exit_code == 1
        assert "format" in result.output

    def test_get_header_injection(self):
        """Should fail with header containing newline characters."""
        result = runner.invoke(
            app, ["get", "https://example.com", "--header", "X-Test: value\ninjected"]
        )

        assert result.exit_code == 1
        assert "newline" in result.output.lower() or "invalid" in result.output.lower()

    def test_get_header_injection_crlf(self):
        """Should fail with header containing CRLF characters."""
        result = runner.invoke(
            app, ["get", "https://example.com", "--header", "X-Test: value\r\ninjected"]
        )

        assert result.exit_code == 1

    @mock.patch("fresh.commands.get.get_cached_content")
    @mock.patch("fresh.commands.get.fetch_with_retry")
    @mock.patch("fresh.commands.get.html_to_markdown")
    def test_get_success(self, mock_markdown, mock_fetch, mock_cache):
        """Should fetch and convert page on success."""
        mock_cache.return_value = None
        mock_response = mock.MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_fetch.return_value = mock_response
        mock_markdown.return_value = "# Test\nContent"

        result = runner.invoke(app, ["get", "https://example.com/docs"])

        assert result.exit_code == 0

    @mock.patch("fresh.commands.get.get_cached_content")
    @mock.patch("fresh.commands.get.fetch_with_retry")
    def test_get_fetch_failure(self, mock_fetch, mock_cache):
        """Should fail when fetch returns None."""
        mock_cache.return_value = None
        mock_fetch.return_value = None

        result = runner.invoke(app, ["get", "https://example.com/docs"])

        assert result.exit_code == 1

    @mock.patch("fresh.commands.get.get_cached_content")
    @mock.patch("fresh.commands.get.fetch_with_retry")
    @mock.patch("fresh.commands.get.html_to_markdown")
    def test_get_with_cache(self, mock_markdown, mock_fetch, mock_cache):
        """Should use cached content when available."""
        mock_cache.return_value = "# Cached\nContent"
        mock_markdown.return_value = "# Cached\nContent"

        result = runner.invoke(app, ["get", "https://example.com/docs"])

        assert result.exit_code == 0
        mock_fetch.assert_not_called()

    @mock.patch("fresh.commands.get.get_cached_content")
    @mock.patch("fresh.commands.get.fetch_with_retry")
    @mock.patch("fresh.commands.get.html_to_markdown")
    def test_get_no_cache(self, mock_markdown, mock_fetch, mock_cache):
        """Should bypass cache when --no-cache is specified."""
        mock_cache.return_value = "cached"
        mock_response = mock.MagicMock()
        mock_response.text = "<html><body>Fresh</body></html>"
        mock_fetch.return_value = mock_response
        mock_markdown.return_value = "# Fresh\nContent"

        result = runner.invoke(
            app, ["get", "https://example.com/docs", "--no-cache"]
        )

        assert result.exit_code == 0
        mock_fetch.assert_called_once()

    @mock.patch("fresh.commands.get.get_cached_content")
    @mock.patch("fresh.commands.get.fetch_with_retry")
    @mock.patch("fresh.commands.get.html_to_markdown")
    def test_get_output_to_file(self, mock_markdown, mock_fetch, mock_cache):
        """Should write to file when --output is specified."""
        mock_cache.return_value = None
        mock_response = mock.MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_fetch.return_value = mock_response
        mock_markdown.return_value = "# Test"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.md"

            result = runner.invoke(
                app,
                ["get", "https://example.com/docs", "--output", str(output_file)],
            )

            assert result.exit_code == 0
            assert output_file.exists()
            content = output_file.read_text()
            assert "Test" in content

    @mock.patch("fresh.commands.get.get_cached_content")
    @mock.patch("fresh.commands.get.fetch_with_retry")
    @mock.patch("fresh.commands.get.html_to_markdown")
    def test_get_verbose_output(self, mock_markdown, mock_fetch, mock_cache):
        """Should output verbose messages when --verbose is specified."""
        mock_cache.return_value = None
        mock_response = mock.MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_fetch.return_value = mock_response
        mock_markdown.return_value = "# Test"

        result = runner.invoke(
            app, ["get", "https://example.com/docs", "--verbose"]
        )

        assert result.exit_code == 0


class TestCacheFunctions:
    """Tests for cache functions."""

    def test_get_cache_dir(self):
        """Should return a valid cache directory."""
        cache_dir = get_module.get_cache_dir()

        assert cache_dir.exists()
        assert cache_dir.is_dir()

    @mock.patch("fresh.commands.get.get_cache_dir")
    def test_save_and_get_cached_content(self, mock_cache_dir):
        """Should save and retrieve cached content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = Path(tmpdir)

            url = "https://example.com/docs"
            content = "# Test Content"

            get_module.save_to_cache(url, content)
            retrieved = get_module.get_cached_content(url)

            assert retrieved == content

    @mock.patch("fresh.commands.get.get_cache_dir")
    def test_get_cached_content_not_found(self, mock_cache_dir):
        """Should return None when content is not cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = Path(tmpdir)

            result = get_module.get_cached_content("https://nonexistent.com")

            assert result is None

    @mock.patch("fresh.commands.get.get_cache_dir")
    def test_get_cache_size_human(self, mock_cache_dir):
        """Should return human-readable cache size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = Path(tmpdir)

            # Create some test files
            (Path(tmpdir) / "test1.md").write_text("x" * 1024)
            (Path(tmpdir) / "test2.md").write_text("x" * 2048)

            size = get_module.get_cache_size_human()
            assert "KB" in size

    @mock.patch("fresh.commands.get.get_cache_dir")
    def test_clear_cache(self, mock_cache_dir):
        """Should clear all cache files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = Path(tmpdir)

            # Create some test files
            (Path(tmpdir) / "test1.md").write_text("content1")
            (Path(tmpdir) / "test2.md").write_text("content2")

            count = get_module.clear_cache()
            assert count == 2
            assert len(list(Path(tmpdir).glob("*.md"))) == 0

    @mock.patch("fresh.commands.get.get_cache_dir")
    def test_enforce_cache_limits_removes_old_files(self, mock_cache_dir):
        """Should remove expired cache files based on TTL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = Path(tmpdir)
            import time

            # Create old file (30 days + 1 second ago)
            old_file = Path(tmpdir) / "old.md"
            old_file.write_text("old content")
            old_time = time.time() - (31 * 24 * 60 * 60)
            import os
            os.utime(old_file, (old_time, old_time))

            # Create new file
            (Path(tmpdir) / "new.md").write_text("new content")

            # Run enforce limits
            get_module._enforce_cache_limits()

            # Old file should be removed, new should remain
            assert not old_file.exists()
            assert (Path(tmpdir) / "new.md").exists()
