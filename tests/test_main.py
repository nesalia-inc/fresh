"""Tests for fresh."""

import pytest
from typer.testing import CliRunner

from fresh import app, main

runner = CliRunner()


class TestMain:
    """Tests for main entry point."""

    def test_main_help(self):
        """Should show help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "fresh" in result.output.lower()


class TestFreshImports:
    """Tests for fresh module imports."""

    def test_import_version(self):
        """Should have version."""
        from fresh import __version__
        assert __version__ is not None

    def test_import_exceptions(self):
        """Should have all exceptions."""
        from fresh import (
            FreshError,
            NetworkError,
            FetchError,
            TimeoutError,
            ValidationError,
            AliasError,
            CacheError,
            SitemapError,
            CrawlerError,
            FilterError,
            ConfigError,
            CLIError,
        )
        assert FreshError is not None
        assert NetworkError is not None
        assert FetchError is not None
        assert TimeoutError is not None
        assert ValidationError is not None
        assert AliasError is not None
        assert CacheError is not None
        assert SitemapError is not None
        assert CrawlerError is not None
        assert FilterError is not None
        assert ConfigError is not None
        assert CLIError is not None
