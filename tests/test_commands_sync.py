"""Tests for sync command utilities."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from fresh.commands.sync import (
    _get_sync_dir,
    get_sync_metadata,
    is_locally_synced,
)


class TestGetSyncDir:
    """Tests for _get_sync_dir function."""

    def test_get_sync_dir_default(self):
        """Test default sync directory is created based on domain."""
        url = "https://docs.python.org/3/"
        result = _get_sync_dir(url, None)
        assert "docs_python_org" in result.name

    def test_get_sync_dir_custom_output(self):
        """Test custom output directory is used when provided."""
        url = "https://docs.python.org/3/"
        custom_dir = Path("/custom/docs")
        result = _get_sync_dir(url, custom_dir)
        assert result == custom_dir

    def test_get_sync_dir_port_replaced(self):
        """Test port numbers are replaced in domain."""
        url = "http://localhost:8080/docs/"
        result = _get_sync_dir(url, None)
        assert "8080" in result.name
        assert ":" not in result.name


class TestGetSyncMetadata:
    """Tests for get_sync_metadata function."""

    @patch("fresh.commands.sync._get_sync_dir")
    def test_get_sync_metadata_exists(self, mock_get_sync_dir, tmp_path):
        """Test getting metadata when sync directory exists."""
        mock_sync_dir = tmp_path / "docs_python_org_3"
        mock_sync_dir.mkdir(parents=True)

        metadata = {
            "site": "https://docs.python.org/3/",
            "last_sync": "2026-03-01T10:00:00Z",
            "page_count": 100,
        }
        metadata_file = mock_sync_dir / "_sync.json"
        metadata_file.write_text(json.dumps(metadata))

        mock_get_sync_dir.return_value = mock_sync_dir

        result = get_sync_metadata("https://docs.python.org/3/")

        assert result is not None
        assert result["site"] == "https://docs.python.org/3/"
        assert result["page_count"] == 100

    @patch("fresh.commands.sync._get_sync_dir")
    def test_get_sync_metadata_not_exists(self, mock_get_sync_dir, tmp_path):
        """Test getting metadata when sync directory doesn't exist."""
        mock_sync_dir = tmp_path / "nonexistent"
        mock_get_sync_dir.return_value = mock_sync_dir

        result = get_sync_metadata("https://example.com/")

        assert result is None

    @patch("fresh.commands.sync._get_sync_dir")
    def test_get_sync_metadata_invalid_json(self, mock_get_sync_dir, tmp_path):
        """Test getting metadata with invalid JSON."""
        mock_sync_dir = tmp_path / "docs_python_org_3"
        mock_sync_dir.mkdir(parents=True)

        metadata_file = mock_sync_dir / "_sync.json"
        metadata_file.write_text("invalid json")

        mock_get_sync_dir.return_value = mock_sync_dir

        result = get_sync_metadata("https://docs.python.org/3/")

        assert result is None


class TestIsLocallySynced:
    """Tests for is_locally_synced function."""

    @patch("fresh.commands.sync.get_sync_metadata")
    def test_is_locally_synced_true(self, mock_get_metadata):
        """Test returns True when metadata exists."""
        mock_get_metadata.return_value = {
            "site": "https://docs.python.org/3/",
            "page_count": 100,
        }

        result = is_locally_synced("https://docs.python.org/3/")

        assert result is True

    @patch("fresh.commands.sync.get_sync_metadata")
    def test_is_locally_synced_false(self, mock_get_metadata):
        """Test returns False when metadata doesn't exist."""
        mock_get_metadata.return_value = None

        result = is_locally_synced("https://example.com/")

        assert result is False

    @patch("fresh.commands.sync.get_sync_metadata")
    def test_is_locally_synced_with_alias(self, mock_get_metadata):
        """Test resolves alias before checking."""
        mock_get_metadata.return_value = {"page_count": 50}

        result = is_locally_synced("python")

        assert result is True
        mock_get_metadata.assert_called_once()
