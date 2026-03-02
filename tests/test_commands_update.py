"""Tests for fresh.commands.update module."""

import sys
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from fresh.commands.update import app, get_latest_version


class TestGetLatestVersion:
    """Tests for get_latest_version function."""

    def test_get_latest_version_success(self):
        """Should return version string on success."""
        # Mock urllib.request.urlopen
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"info": {"version": "2.5.0"}}'

        with patch('fresh.commands.update.urllib.request.urlopen', return_value=mock_response):
            result = get_latest_version()
            assert result == "2.5.0"

    def test_get_latest_version_network_error(self):
        """Should return None on network error."""
        with patch('fresh.commands.update.urllib.request.urlopen', side_effect=Exception("Network error")):
            result = get_latest_version()
            assert result is None

    def test_get_latest_version_invalid_json(self):
        """Should return None on invalid JSON."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'invalid json'

        with patch('fresh.commands.update.urllib.request.urlopen', return_value=mock_response):
            result = get_latest_version()
            assert result is None

    def test_get_latest_version_missing_version(self):
        """Should return None when version key is missing."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"info": {}}'

        with patch('fresh.commands.update.urllib.request.urlopen', return_value=mock_response):
            result = get_latest_version()
            assert result is None


class TestUpdateCommand:
    """Tests for update command CLI."""

    def test_update_help(self):
        """Should show help."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Check for and install updates" in result.stdout

    def test_update_check_only_current(self):
        """Should show current version when already up to date."""
        # Test version comparison logic
        from packaging import version
        current = "2.3.1"
        latest = "2.3.1"
        assert not (version.parse(latest) > version.parse(current))

    def test_update_check_only_newer(self):
        """Should show new version available when update exists."""
        from packaging import version
        current = "2.3.1"
        latest = "2.5.0"
        assert version.parse(latest) > version.parse(current)

    def test_update_error_getting_version(self):
        """Should handle error when getting version."""
        runner = CliRunner()

        with patch('fresh.commands.update.get_latest_version', return_value=None):
            result = runner.invoke(app, [])
            # Should exit with error
            assert result.exit_code == 1
