"""Tests for doc command."""

from typer.testing import CliRunner

from fresh import app

runner = CliRunner()


class TestDocCommand:
    """Tests for the doc command."""

    def test_doc_overview(self):
        """Should show overview when no argument."""
        result = runner.invoke(app, ["doc"])

        assert result.exit_code == 0
        assert "Fresh - Documentation Fetcher" in result.output
        assert "fresh list" in result.output
        assert "fresh get" in result.output

    def test_doc_get(self):
        """Should show documentation for get command."""
        result = runner.invoke(app, ["doc", "get"])

        assert result.exit_code == 0
        assert "fresh get" in result.output
        assert "--output" in result.output

    def test_doc_list(self):
        """Should show documentation for list command."""
        result = runner.invoke(app, ["doc", "list"])

        assert result.exit_code == 0
        assert "fresh list" in result.output
        assert "--pattern" in result.output

    def test_doc_search(self):
        """Should show documentation for search command."""
        result = runner.invoke(app, ["doc", "search"])

        assert result.exit_code == 0
        assert "fresh search" in result.output

    def test_doc_alias(self):
        """Should show documentation for alias command."""
        result = runner.invoke(app, ["doc", "alias"])

        assert result.exit_code == 0
        assert "fresh alias" in result.output

    def test_doc_unknown_command(self):
        """Should show error for unknown command."""
        result = runner.invoke(app, ["doc", "unknown"])

        assert result.exit_code == 1
        assert "Unknown command" in result.output
