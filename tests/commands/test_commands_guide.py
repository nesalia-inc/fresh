"""Tests for guide command."""

import tempfile
from pathlib import Path

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


class TestGuideWindows:
    """Tests for Windows-specific functions."""

    def test_is_windows(self):
        """Should check platform correctly."""
        import platform
        from fresh.commands.guide import _is_windows

        expected = platform.system() == "Windows"
        assert _is_windows() == expected

    def test_create_console(self):
        """Should create a Console object."""
        from fresh.commands.guide import _create_console

        console = _create_console()
        assert console is not None


class TestGuideLoadErrors:
    """Tests for guide loading error handling."""

    def test_load_guide_invalid_json(self):
        """Should handle invalid JSON gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_guides_dir = guide.GUIDES_DIR
            guide.GUIDES_DIR = Path(tmpdir)

            try:
                # Create a file with invalid JSON
                guide_file = Path(tmpdir) / "invalid.json"
                guide_file.write_text("not valid json")

                result = guide._load_guide("invalid")
                assert result is None
            finally:
                guide.GUIDES_DIR = original_guides_dir

    def test_list_guides_invalid_json(self):
        """Should skip invalid JSON files when listing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_guides_dir = guide.GUIDES_DIR
            guide.GUIDES_DIR = Path(tmpdir)

            try:
                # Create a valid guide
                valid_guide = {"title": "Valid", "content": "Content", "created": "2026-01-01T00:00:00+00:00", "updated": "2026-01-01T00:00:00+00:00"}
                guide._save_guide("valid", valid_guide)

                # Create an invalid JSON file
                invalid_file = Path(tmpdir) / "invalid.json"
                invalid_file.write_text("not valid json")

                # Should still list the valid guide
                guides = guide._list_guides()
                names = [g[0] for g in guides]
                assert "valid" in names
            finally:
                guide.GUIDES_DIR = original_guides_dir


class TestGuideConstants:
    """Tests for guide constants."""

    def test_guides_dir_exists(self):
        """GUIDES_DIR should be defined."""
        assert guide.GUIDES_DIR is not None

    def test_invalid_name_chars(self):
        """INVALID_NAME_CHARS should contain path separators."""
        assert "/" in guide.INVALID_NAME_CHARS
        assert "\\" in guide.INVALID_NAME_CHARS

    def test_max_name_length(self):
        """MAX_NAME_LENGTH should be defined."""
        assert guide.MAX_NAME_LENGTH > 0
