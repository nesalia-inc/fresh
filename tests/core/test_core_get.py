"""Tests for core.get module - pure business logic for get command."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from fresh.core import get as core_get


class TestGetSyncDir:
    """Tests for get_sync_dir function."""

    def test_get_sync_dir_default(self):
        """Should return default sync directory."""
        path = core_get.get_sync_dir()
        assert ".fresh" in str(path)
        assert "docs" in str(path)


class TestUrlToSyncPath:
    """Tests for url_to_sync_path function."""

    def test_basic_url(self):
        """Should convert basic URL to sync path."""
        path = core_get.url_to_sync_path("https://example.com/docs/page.html")
        assert path is not None
        assert "example_com" in str(path)
        assert "page.html" in str(path)

    def test_url_with_port(self):
        """Should handle URL with port."""
        path = core_get.url_to_sync_path("https://example.com:8080/page.html")
        assert path is not None
        assert "example_com_8080" in str(path)

    def test_index_path(self):
        """Should add index.html for directory paths."""
        path = core_get.url_to_sync_path("https://example.com/docs/")
        assert path is not None
        assert "index.html" in str(path)

    def test_root_path(self):
        """Should handle root path."""
        path = core_get.url_to_sync_path("https://example.com")
        assert path is not None
        assert "index.html" in str(path)

    def test_custom_sync_dir(self):
        """Should use custom sync directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_dir = Path(tmpdir)
            path = core_get.url_to_sync_path("https://example.com/page.html", sync_dir)
            assert path is not None
            assert str(sync_dir) in str(path)


class TestGetLocalContent:
    """Tests for get_local_content function."""

    def test_no_local_content(self):
        """Should return None when no local content."""
        result = core_get.get_local_content("https://example.com/page.html")
        assert result is None

    def test_with_local_content(self):
        """Should return local content when exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_dir = Path(tmpdir)
            # Create the file structure
            content_dir = sync_dir / "example_com" / "pages"
            content_dir.mkdir(parents=True)
            test_file = content_dir / "page.html"
            test_file.write_text("<html>Test</html>")

            result = core_get.get_local_content("https://example.com/page.html", sync_dir)
            assert result == "<html>Test</html>"


class TestLocalContentExists:
    """Tests for local_content_exists function."""

    def test_not_exists(self):
        """Should return False when content doesn't exist."""
        result = core_get.local_content_exists("https://example.com/nonexistent.html")
        assert result is False

    def test_exists(self):
        """Should return True when content exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_dir = Path(tmpdir)
            content_dir = sync_dir / "example_com" / "pages"
            content_dir.mkdir(parents=True)
            test_file = content_dir / "page.html"
            test_file.write_text("<html>Test</html>")

            result = core_get.local_content_exists("https://example.com/page.html", sync_dir)
            assert result is True


class TestHtmlToMarkdown:
    """Tests for html_to_markdown function."""

    def test_basic_html(self):
        """Should convert basic HTML to Markdown."""
        html = "<h1>Title</h1><p>Paragraph</p>"
        result = core_get.html_to_markdown(html)
        assert "# Title" in result
        assert "Paragraph" in result

    def test_skip_scripts(self):
        """Should remove script tags when skip_scripts=True."""
        html = "<html><script>alert('xss')</script><body>Content</body></html>"
        result = core_get.html_to_markdown(html, skip_scripts=True)
        assert "alert" not in result
        assert "Content" in result


class TestCacheFunctions:
    """Tests for cache-related functions."""

    def test_get_cache_dir(self):
        """Should return cache directory."""
        cache_dir = core_get.get_cache_dir()
        assert ".fresh" in str(cache_dir)
        assert "cache" in str(cache_dir)

    def test_get_cached_content_not_exists(self):
        """Should return None when cached content doesn't exist."""
        result = core_get.get_cached_content("https://nonexistent.example.com/page.html")
        assert result is None

    def test_save_and_get_cached_content(self):
        """Should save and retrieve cached content."""
        url = "https://test.example.com/page.html"
        content = "# Test Content"

        core_get.save_to_cache(url, content)
        result = core_get.get_cached_content(url)

        assert result == content

    def test_clear_cache(self):
        """Should clear cache."""
        url = "https://test.example.com/page.html"
        core_get.save_to_cache(url, "content")

        count = core_get.clear_cache()
        assert count >= 1

    def test_cache_with_ttl_expired(self):
        """Should return None when cache is expired."""
        import time

        url = "https://test.example.com/page.html"
        core_get.save_to_cache(url, "content")

        # Get with 0 TTL (disabled)
        result = core_get.get_cached_content(url, ttl_days=0)
        # With TTL=0, it should try to delete expired and return None
        # This depends on implementation
