"""Tests for websearch command."""

import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fresh import app


@pytest.fixture
def runner():
    """Fixture to provide CLI runner."""
    return CliRunner()


class TestWebsearchCommand:
    """Tests for websearch CLI command."""

    def test_websearch_help(self, runner):
        """Test that websearch help works."""
        result = runner.invoke(app, ["websearch", "--help"])
        assert result.exit_code == 0
        assert "Search the web for general queries" in result.output
        assert "--count" in result.output
        assert "--engine" in result.output
        assert "--json" in result.output
        assert "--table" in result.output
        assert "--verbose" in result.output

    def test_websearch_no_args(self, runner):
        """Test websearch without query shows error."""
        result = runner.invoke(app, ["websearch"])
        assert result.exit_code == 2
        assert "Missing argument 'QUERY'" in result.output

    @patch("fresh.commands.websearch.websearch_module.websearch")
    def test_websearch_json_output(self, mock_websearch, runner):
        """Test JSON output format."""
        # Create a proper mock result
        mock_result = type("WebSearchResult", (), {
            "title": "Test Title",
            "url": "https://example.com",
            "description": "Test description",
            "to_dict": lambda self: {
                "title": self.title,
                "url": self.url,
                "description": self.description,
            }
        })()
        mock_websearch.return_value = [mock_result]

        result = runner.invoke(app, ["websearch", "test query", "--json"])
        assert result.exit_code == 0
        # Should be valid JSON
        output = json.loads(result.output)
        assert len(output) == 1
        assert output[0]["title"] == "Test Title"

    @patch("fresh.commands.websearch.websearch_module.websearch")
    def test_websearch_table_output(self, mock_websearch, runner):
        """Test table output format."""
        mock_result = type("WebSearchResult", (), {
            "title": "Test Title",
            "url": "https://example.com",
            "description": "Test description",
        })()
        mock_websearch.return_value = [mock_result]

        result = runner.invoke(app, ["websearch", "test query", "--table"])
        assert result.exit_code == 0
        assert "Test Title" in result.output
        assert "example.com" in result.output

    @patch("fresh.commands.websearch.websearch_module.websearch")
    def test_websearch_no_results(self, mock_websearch, runner):
        """Test handling of no results."""
        mock_websearch.return_value = []

        result = runner.invoke(app, ["websearch", "nonexistent query"])
        assert result.exit_code == 0
        assert "No results found" in result.output

    @patch("fresh.commands.websearch.websearch_module.websearch")
    def test_websearch_error_handling(self, mock_websearch, runner):
        """Test error handling for network failures."""
        mock_websearch.side_effect = Exception("Network error")

        result = runner.invoke(app, ["websearch", "test"])
        assert result.exit_code == 1
        assert "Search error" in result.output
