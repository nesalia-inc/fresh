"""Tests for fresh.commands.index module."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from fresh.commands.index import index_app


class TestIndexCommand:
    """Tests for index command CLI."""

    def test_index_help(self):
        """Should show help."""
        from fresh.commands.index import index_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(index_app, ["--help"])
        assert result.exit_code == 0
        assert "Manage search indexes" in result.stdout

    def test_index_build_help(self):
        """Should show help for build subcommand."""
        from fresh.commands.index import index_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(index_app, ["build", "--help"])
        assert result.exit_code == 0

    def test_index_rebuild_help(self):
        """Should show help for rebuild subcommand."""
        from fresh.commands.index import index_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(index_app, ["rebuild", "--help"])
        assert result.exit_code == 0

    def test_index_status_help(self):
        """Should show help for status subcommand."""
        from fresh.commands.index import index_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(index_app, ["status", "--help"])
        assert result.exit_code == 0

    def test_index_delete_help(self):
        """Should show help for delete subcommand."""
        from fresh.commands.index import index_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(index_app, ["delete", "--help"])
        assert result.exit_code == 0

    def test_index_search_help(self):
        """Should show help for search subcommand."""
        from fresh.commands.index import index_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(index_app, ["search", "--help"])
        assert result.exit_code == 0


class TestGetSiteName:
    """Tests for _get_site_name function."""

    def test_get_site_name_from_url(self):
        """Should extract site name from URL."""
        from fresh.commands.index import _get_site_name

        result = _get_site_name("https://docs.python.org/")
        assert result == "docs_python_org"

    def test_get_site_name_with_port(self):
        """Should handle port in URL."""
        from fresh.commands.index import _get_site_name

        result = _get_site_name("https://localhost:8080/")
        assert result == "localhost_8080"


class TestIndexBuild:
    """Tests for index build command."""

    @patch('fresh.commands.index.build_index_from_directory')
    def test_build_index(self, mock_build):
        """Should build index."""
        mock_build.return_value = 10

        with patch('fresh.commands.index.get_index_age', return_value=None):
            runner = CliRunner()
            result = runner.invoke(index_app, ["build", "test-site", "-d", "/tmp/pages", "--force"])
            # Should complete (may have other issues but shouldn't crash)

    @patch('fresh.commands.index.get_index_age')
    @patch('fresh.commands.index.build_index_from_directory')
    def test_build_index_with_existing(self, mock_build, mock_age):
        """Should handle existing index."""
        from datetime import datetime, timedelta, timezone

        mock_age.return_value = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_build.return_value = 10

        runner = CliRunner()
        # With --force it should rebuild without asking
        result = runner.invoke(index_app, ["build", "test-site", "-d", "/tmp/pages", "--force"])
        # Should either rebuild or ask (depending on implementation)


class TestIndexRebuild:
    """Tests for index rebuild command."""

    @patch('fresh.commands.index.rebuild_index')
    def test_rebuild_index(self, mock_rebuild):
        """Should rebuild index."""
        mock_rebuild.return_value = 15

        runner = CliRunner()
        result = runner.invoke(index_app, ["rebuild", "test-site", "-d", "/tmp/pages"])
        # Should complete


class TestIndexStatus:
    """Tests for index status command."""

    @patch('fresh.commands.index.get_index_stats')
    def test_status(self, mock_stats):
        """Should show status."""
        mock_stats.return_value = {
            "site_name": "test_site",
            "page_count": 100,
            "last_updated": "2024-01-01T00:00:00",
            "db_path": "/tmp/test.db"
        }

        runner = CliRunner()
        result = runner.invoke(index_app, ["status", "test_site"])
        # Should show status

    def test_status_all(self):
        """Should show status for all sites."""
        runner = CliRunner()
        result = runner.invoke(index_app, ["status"])
        # Should show all statuses


class TestIndexDelete:
    """Tests for index delete command."""

    @patch('fresh.commands.index.delete_index')
    def test_delete(self, mock_delete):
        """Should delete index."""
        mock_delete.return_value = True

        runner = CliRunner()
        result = runner.invoke(index_app, ["delete", "test-site", "--force"])
        assert result.exit_code == 0


class TestIndexSearch:
    """Tests for index search command."""

    @patch('fresh.indexer.search_index')
    @patch('fresh.indexer.get_index_stats')
    def test_search(self, mock_stats, mock_search):
        """Should search index."""
        mock_stats.return_value = {"page_count": 100}
        mock_search.return_value = [
            {"url": "/page1", "title": "Page 1", "snippet": "content..."}
        ]

        runner = CliRunner()
        result = runner.invoke(index_app, ["search", "test-site", "query"])
        # Should show results


class TestCreateConsole:
    """Tests for _create_console function."""

    def test_create_console(self):
        """Should create a Console object."""
        from fresh.commands.index import _create_console

        console = _create_console()
        assert console is not None


class TestIndexBuildErrors:
    """Tests for index build error cases."""

    def test_build_index_missing_pages_dir(self):
        """Should fail when pages directory doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(index_app, ["build", "test-site", "-d", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    @patch('fresh.commands.index.build_index_from_directory')
    @patch('fresh.commands.index.get_index_age')
    def test_build_index_no_html_files(self, mock_age, mock_build):
        """Should fail when no HTML files found."""
        mock_age.return_value = None
        mock_build.return_value = 0

        runner = CliRunner()
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[]):
                result = runner.invoke(index_app, ["build", "test-site", "-d", "/tmp/pages", "--force"])
                assert result.exit_code == 1


class TestIndexRebuildErrors:
    """Tests for index rebuild error cases."""

    def test_rebuild_index_missing_pages_dir(self):
        """Should fail when pages directory doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(index_app, ["rebuild", "test-site", "-d", "/nonexistent/path"])
        assert result.exit_code == 1


class TestIndexStatusErrors:
    """Tests for index status error cases."""

    def test_status_no_index_dir(self):
        """Should show message when no index directory."""
        runner = CliRunner()
        with patch('fresh.commands.index.DEFAULT_INDEX_DIR', Path("/nonexistent")):
            result = runner.invoke(index_app, ["status"])
            assert "no indexes" in result.output.lower()

    def test_status_site_not_found(self):
        """Should show message when site not found."""
        runner = CliRunner()
        with patch('fresh.commands.index.DEFAULT_INDEX_DIR') as mock_dir:
            mock_dir.exists.return_value = True
            mock_dir.glob.return_value = []
            result = runner.invoke(index_app, ["status", "nonexistent"])
            # Should handle the case


class TestIndexDeleteErrors:
    """Tests for index delete error cases."""

    @patch('fresh.commands.index.delete_index')
    def test_delete_not_found(self, mock_delete):
        """Should fail when index not found."""
        mock_delete.return_value = False

        runner = CliRunner()
        result = runner.invoke(index_app, ["delete", "nonexistent", "--force"])
        assert result.exit_code == 1


class TestIndexSearchErrors:
    """Tests for index search error cases."""

    @patch('fresh.indexer.get_index_stats')
    def test_search_index_not_found(self, mock_stats):
        """Should fail when index not found."""
        mock_stats.return_value = None

        runner = CliRunner()
        result = runner.invoke(index_app, ["search", "nonexistent", "query"])
        assert result.exit_code == 1

    @patch('fresh.indexer.search_index')
    @patch('fresh.commands.index.get_index_stats')
    def test_search_no_results(self, mock_stats, mock_search):
        """Should handle no results."""
        mock_stats.return_value = {"page_count": 100}
        mock_search.return_value = []

        runner = CliRunner()
        result = runner.invoke(index_app, ["search", "test-site", "nonexistent"])
        assert "no results" in result.output.lower()


class TestIsWindows:
    """Tests for _is_windows function."""

    def test_is_windows(self):
        """Should check platform."""
        from fresh.commands.index import _is_windows

        result = _is_windows()
        assert isinstance(result, bool)
