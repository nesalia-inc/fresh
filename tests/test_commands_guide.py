"""Tests for guide command."""

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from typer.testing import CliRunner

from fresh import app
from fresh.commands import guide

runner = CliRunner()


class TestGuideCommand:
    """Tests for the guide command."""

    def test_guide_help(self):
        """Should show help."""
        result = runner.invoke(app, ["guide", "--help"])
        assert result.exit_code == 0
        assert "guide" in result.output.lower()

    def test_guide_list_empty(self):
        """Should show empty message when no guides."""
        result = runner.invoke(app, ["guide", "list"])
        assert result.exit_code == 0

    def test_guide_show_not_found(self):
        """Should error when guide not found."""
        result = runner.invoke(app, ["guide", "show", "nonexistent"])
        assert result.exit_code == 1

    def test_guide_delete_not_found(self):
        """Should error when deleting nonexistent guide."""
        result = runner.invoke(app, ["guide", "delete", "nonexistent"])
        assert result.exit_code == 1


class TestGuideFunctions:
    """Tests for guide utility functions."""

    def test_load_guide_not_found(self):
        """Should return None when guide doesn't exist."""
        # Use a temp directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            original_guides_dir = guide.GUIDES_DIR
            guide.GUIDES_DIR = Path(tmpdir)

            try:
                result = guide._load_guide("nonexistent")
                assert result is None
            finally:
                guide.GUIDES_DIR = original_guides_dir

    def test_save_and_load_guide(self):
        """Should save and load guide correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_guides_dir = guide.GUIDES_DIR
            guide.GUIDES_DIR = Path(tmpdir)

            try:
                test_guide = {
                    "title": "Test Guide",
                    "content": "# Test Content",
                    "created": "2026-01-01T00:00:00+00:00",
                    "updated": "2026-01-01T00:00:00+00:00",
                    "tags": ["test", "guide"],
                }

                guide._save_guide("test-guide", test_guide)
                loaded = guide._load_guide("test-guide")

                assert loaded is not None
                assert loaded["title"] == "Test Guide"
                assert loaded["content"] == "# Test Content"
                assert loaded["tags"] == ["test", "guide"]
            finally:
                guide.GUIDES_DIR = original_guides_dir

    def test_delete_guide(self):
        """Should delete guide correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_guides_dir = guide.GUIDES_DIR
            guide.GUIDES_DIR = Path(tmpdir)

            try:
                # Create a guide first
                test_guide = {
                    "title": "Test",
                    "content": "Content",
                    "created": "2026-01-01T00:00:00+00:00",
                    "updated": "2026-01-01T00:00:00+00:00",
                }
                guide._save_guide("to-delete", test_guide)

                # Delete it
                result = guide._delete_guide("to-delete")
                assert result is True

                # Verify it's gone
                loaded = guide._load_guide("to-delete")
                assert loaded is None
            finally:
                guide.GUIDES_DIR = original_guides_dir

    def test_list_guides(self):
        """Should list all guides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_guides_dir = guide.GUIDES_DIR
            guide.GUIDES_DIR = Path(tmpdir)

            try:
                # Create multiple guides
                guide1 = {"title": "Guide 1", "content": "Content 1", "created": "2026-01-01T00:00:00+00:00", "updated": "2026-01-01T00:00:00+00:00"}
                guide2 = {"title": "Guide 2", "content": "Content 2", "created": "2026-01-02T00:00:00+00:00", "updated": "2026-01-02T00:00:00+00:00"}

                guide._save_guide("guide-1", guide1)
                guide._save_guide("guide-2", guide2)

                guides = guide._list_guides()
                assert len(guides) == 2
                names = [g[0] for g in guides]
                assert "guide-1" in names
                assert "guide-2" in names
            finally:
                guide.GUIDES_DIR = original_guides_dir

    def test_format_age(self):
        """Should format age correctly."""
        from datetime import datetime, timezone

        # Test "just now"
        now = datetime.now(timezone.utc).isoformat()
        assert guide._format_age(now) == "just now"

        # Test minutes ago
        import time
        time.sleep(1)
        now = datetime.now(timezone.utc).isoformat()
        result = guide._format_age(now)
        assert "m ago" in result or "just now" == result

        # Test invalid timestamp
        assert guide._format_age("invalid") == "unknown"
