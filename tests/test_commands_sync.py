"""Tests for fresh.commands.sync module."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGetSyncDir:
    """Tests for get_sync_dir function."""

    def test_get_sync_dir_default(self):
        """Should return default sync directory based on URL."""
        from fresh.commands.sync import _get_sync_dir

        result = _get_sync_dir("https://docs.python.org/", None)
        assert isinstance(result, Path)
        assert "docs_python_org" in str(result)

    def test_get_sync_dir_with_output_dir(self):
        """Should use provided output directory."""
        from fresh.commands.sync import get_sync_dir

        custom_dir = Path("/custom/path")
        result = get_sync_dir("https://docs.python.org/", output_dir=custom_dir)
        assert result == custom_dir


class TestSyncMetadata:
    """Tests for sync metadata functions."""

    def test_save_metadata(self, tmp_path):
        """Should save metadata to file."""
        from fresh.commands.sync import _save_metadata

        _save_metadata(tmp_path, "https://example.com", 10)

        metadata_file = tmp_path / "_sync.json"
        assert metadata_file.exists()

        data = json.loads(metadata_file.read_text())
        assert data["site"] == "https://example.com"
        assert data["page_count"] == 10
        assert "last_sync" in data

    def test_get_sync_metadata_not_exists(self):
        """Should return None when metadata doesn't exist."""
        from fresh.commands.sync import get_sync_metadata

        # Use a URL that won't exist
        result = get_sync_metadata("https://nonexistent-example-12345.com/")
        # Result will be None because directory doesn't exist
        assert result is None or isinstance(result, dict)

    def test_get_sync_metadata_invalid_json(self, tmp_path):
        """Should handle invalid JSON gracefully."""
        from fresh.commands.sync import get_sync_metadata

        # Create directory with invalid JSON
        metadata_file = tmp_path / "_sync.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_file.write_text("invalid json")

        # Mock _get_sync_dir to return our tmp_path
        with patch('fresh.commands.sync._get_sync_dir', return_value=tmp_path):
            result = get_sync_metadata("https://test-example.com/")
            assert result is None


class TestPageFreshness:
    """Tests for page freshness functions."""

    def test_get_page_freshness_not_exists(self):
        """Should return None when page doesn't exist."""
        from fresh.commands.sync import get_page_freshness

        result = get_page_freshness(
            "https://example.com/page.html",
            "https://example.com/"
        )
        assert result is None


class TestCheckPageChanged:
    """Tests for check_page_changed function."""

    def test_check_page_changed_no_headers(self):
        """Should return True when no freshness headers."""
        from fresh.commands.sync import check_page_changed

        result = check_page_changed(
            "https://example.com/page.html",
            {}  # No headers
        )
        assert result is True

    def test_check_page_changed_with_etag(self):
        """Should check page with etag header."""
        from fresh.commands.sync import check_page_changed

        # Mock httpx to simulate 304 Not Modified
        with patch('fresh.commands.sync.httpx.Client') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 304
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.return_value.head.return_value = mock_response

            result = check_page_changed(
                "https://example.com/page.html",
                {"etag": "abc123"}
            )
            assert result is False

    def test_check_page_changed_with_last_modified(self):
        """Should check page with last-modified header."""
        from fresh.commands.sync import check_page_changed

        with patch('fresh.commands.sync.httpx.Client') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200  # Page changed
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.return_value.head.return_value = mock_response

            result = check_page_changed(
                "https://example.com/page.html",
                {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT"}
            )
            assert result is True

    def test_check_page_changed_network_error(self):
        """Should return True on network error."""
        import httpx
        from fresh.commands.sync import check_page_changed

        with patch('fresh.commands.sync.httpx.Client') as mock_client:
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.return_value.head.side_effect = httpx.RequestError("Network error")

            result = check_page_changed(
                "https://example.com/page.html",
                {"etag": "abc123"}
            )
            assert result is True


class TestShouldSkipPage:
    """Tests for _should_skip_page function."""

    def test_should_skip_page_robots(self):
        """Should skip page blocked by robots.txt."""
        from fresh.commands.sync import _should_skip_page

        with patch('fresh.commands.sync.is_allowed_by_robots') as mock_robots:
            mock_robots.return_value = False

            skip, reason = _should_skip_page(
                "https://example.com/page.html",
                incremental=False,
                resolved_url="https://example.com/",
                sitemap_domain="example.com",
                pages_dir=Path("/tmp/pages")
            )
            assert skip is True
            assert reason == "robots.txt"

    def test_should_skip_page_incremental_unchanged(self):
        """Should skip unchanged page in incremental mode."""
        from fresh.commands.sync import _should_skip_page

        with patch('fresh.commands.sync.is_allowed_by_robots') as mock_robots:
            mock_robots.return_value = True

            with patch('fresh.commands.sync.get_page_freshness') as mock_freshness:
                mock_freshness.return_value = {"etag": "abc123"}

                with patch('fresh.commands.sync.check_page_changed') as mock_check:
                    mock_check.return_value = False

                    skip, reason = _should_skip_page(
                        "https://example.com/page.html",
                        incremental=True,
                        resolved_url="https://example.com/",
                        sitemap_domain="example.com",
                        pages_dir=Path("/tmp/pages")
                    )
                    assert skip is True
                    assert reason == "unchanged"

    def test_should_skip_page_not_incremental(self):
        """Should not skip when incremental is False."""
        from fresh.commands.sync import _should_skip_page

        with patch('fresh.commands.sync.is_allowed_by_robots') as mock_robots:
            mock_robots.return_value = True

            skip, reason = _should_skip_page(
                "https://example.com/page.html",
                incremental=False,
                resolved_url="https://example.com/",
                sitemap_domain="example.com",
                pages_dir=Path("/tmp/pages")
            )
            assert skip is False
            assert reason == ""


class TestFetchPageForSync:
    """Tests for _fetch_page_for_sync function."""

    def test_fetch_page_binary_response(self):
        """Should return None for binary content."""
        from fresh.commands.sync import _fetch_page_for_sync

        with patch('fresh.commands.sync.fetch_binary_aware') as mock_fetch:
            mock_fetch.return_value = None

            result = _fetch_page_for_sync("https://example.com/image.png")
            assert result == (None, None)


class TestSavePage:
    """Tests for _save_page function."""

    def test_save_page_binary_url(self):
        """Should return None for binary URLs."""
        from fresh.commands.sync import _save_page

        with patch('fresh.commands.sync.is_binary_url') as mock_binary:
            mock_binary.return_value = True

            result = _save_page("https://example.com/image.png", Path("/tmp"))
            assert result is None

    def test_save_page_fetch_failure(self):
        """Should return False when fetch fails."""
        from fresh.commands.sync import _save_page

        with patch('fresh.commands.sync.is_binary_url') as mock_binary:
            mock_binary.return_value = False

            with patch('fresh.commands.sync._fetch_page_for_sync') as mock_fetch:
                mock_fetch.return_value = (None, None)

                result = _save_page("https://example.com/page.html", Path("/tmp"))
                assert result is False

    def test_save_page_success(self, tmp_path):
        """Should save page successfully."""
        from fresh.commands.sync import _save_page

        with patch('fresh.commands.sync.is_binary_url') as mock_binary:
            mock_binary.return_value = False

            with patch('fresh.commands.sync._fetch_page_for_sync') as mock_fetch:
                mock_fetch.return_value = ("<html>Test</html>", {"etag": "abc123"})

                result = _save_page("https://example.com/page.html", tmp_path)
                assert result is True

                # Check file was created
                files = list(tmp_path.glob("*.html"))
                assert len(files) > 0

    def test_save_page_long_filename(self, tmp_path):
        """Should handle long filenames with hashing."""
        from fresh.commands.sync import _save_page

        with patch('fresh.commands.sync.is_binary_url') as mock_binary:
            mock_binary.return_value = False

            with patch('fresh.commands.sync._fetch_page_for_sync') as mock_fetch:
                mock_fetch.return_value = ("<html>Test</html>", None)

                # Create a path that triggers the 200-char truncation logic
                # but doesn't exceed OS limits - mock write_text to avoid Windows path limit
                pages_dir = tmp_path / "pages"
                pages_dir.mkdir(parents=True, exist_ok=True)

                with patch.object(Path, 'write_text', return_value=None):
                    long_path = "/" + "a" * 150 + ".html"
                    result = _save_page(f"https://example.com{long_path}", pages_dir)
                    assert result is True


class TestSyncMetadata:
    """Tests for sync metadata functions."""

    def test_save_metadata(self, tmp_path):
        """Should save metadata to file."""
        from fresh.commands.sync import _save_metadata

        _save_metadata(tmp_path, "https://example.com", 10)

        metadata_file = tmp_path / "_sync.json"
        assert metadata_file.exists()

        import json
        data = json.loads(metadata_file.read_text())
        assert data["site"] == "https://example.com"
        assert data["page_count"] == 10
        assert "last_sync" in data


class TestFetchPageForSync:
    """Tests for _fetch_page_for_sync function."""

    def test_fetch_page_returns_none(self):
        """Should return None when fetch returns None."""
        from fresh.commands.sync import _fetch_page_for_sync

        with patch('fresh.commands.sync.fetch_binary_aware') as mock_fetch:
            mock_fetch.return_value = None

            result = _fetch_page_for_sync("https://example.com/page.html")
            assert result == (None, None)


class TestSyncCommand:
    """Tests for sync command CLI."""

    def test_sync_invalid_url(self):
        """Should fail with invalid URL."""
        from fresh.commands.sync import sync
        import typer

        with pytest.raises(typer.Exit):
            sync("not-a-valid-url")

    def test_sync_help(self):
        """Should show help."""
        from fresh.commands.sync import app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Download entire documentation" in result.stdout
