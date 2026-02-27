"""Tests for guide management commands."""

import tempfile
from pathlib import Path
from unittest import mock

from typer.testing import CliRunner

from fresh import app
from fresh.commands import guide

runner = CliRunner()


class TestGuideManagement:
    """Tests for guide management commands."""

    def test_update_guide(self):
        """Test updating a guide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                # Create a guide first
                guide._save_guide(
                    "test-guide",
                    {
                        "title": "Test Guide",
                        "content": "Original content",
                        "created": "2024-01-01T00:00:00Z",
                        "updated": "2024-01-01T00:00:00Z",
                    },
                )

                # Update the guide
                result = runner.invoke(
                    app,
                    ["guide", "update", "test-guide", "--content", "Updated content"],
                )
                assert result.exit_code == 0
                assert "Updated guide 'test-guide'" in result.output

                # Verify the update
                updated = guide._load_guide("test-guide")
                assert updated["content"] == "Updated content"

    def test_update_nonexistent_guide(self):
        """Test updating a non-existent guide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                result = runner.invoke(
                    app,
                    ["guide", "update", "nonexistent", "--content", "Content"],
                )
                assert result.exit_code == 1
                assert "not found" in result.output

    def test_append_guide(self):
        """Test appending content to a guide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                # Create a guide first
                guide._save_guide(
                    "test-guide",
                    {
                        "title": "Test Guide",
                        "content": "Original content",
                        "created": "2024-01-01T00:00:00Z",
                        "updated": "2024-01-01T00:00:00Z",
                    },
                )

                # Append content
                result = runner.invoke(
                    app,
                    ["guide", "append", "test-guide", "Appended content"],
                )
                assert result.exit_code == 0
                assert "Appended content to guide 'test-guide'" in result.output

                # Verify the append
                updated = guide._load_guide("test-guide")
                assert "Original content" in updated["content"]
                assert "Appended content" in updated["content"]

    def test_append_nonexistent_guide(self):
        """Test appending to a non-existent guide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                result = runner.invoke(
                    app,
                    ["guide", "append", "nonexistent", "Content"],
                )
                assert result.exit_code == 1
                assert "not found" in result.output

    def test_export_guide_markdown(self):
        """Test exporting a guide to markdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                # Create a guide
                guide._save_guide(
                    "test-guide",
                    {
                        "title": "Test Guide",
                        "content": "Guide content here",
                        "tags": ["react", "javascript"],
                        "created": "2024-01-01T00:00:00Z",
                        "updated": "2024-01-01T00:00:00Z",
                    },
                )

                output_file = Path(tmpdir) / "export.md"
                result = runner.invoke(
                    app,
                    ["guide", "export", "test-guide", "--output", str(output_file)],
                )
                assert result.exit_code == 0
                assert "Exported guide 'test-guide'" in result.output

                # Verify the export
                content = output_file.read_text(encoding="utf-8")
                assert "# Test Guide" in content
                assert "Guide content here" in content
                assert "react" in content

    def test_export_guide_json(self):
        """Test exporting a guide to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                # Create a guide
                guide._save_guide(
                    "test-guide",
                    {
                        "title": "Test Guide",
                        "content": "Guide content",
                        "tags": ["tag1"],
                        "created": "2024-01-01T00:00:00Z",
                        "updated": "2024-01-01T00:00:00Z",
                    },
                )

                output_file = Path(tmpdir) / "export.json"
                result = runner.invoke(
                    app,
                    ["guide", "export", "test-guide", "--output", str(output_file), "--format", "json"],
                )
                assert result.exit_code == 0

                # Verify the export
                import json
                data = json.loads(output_file.read_text(encoding="utf-8"))
                assert data["title"] == "Test Guide"
                assert data["content"] == "Guide content"

    def test_import_guide_markdown(self):
        """Test importing a guide from markdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                # Create a markdown file
                md_file = Path(tmpdir) / "import.md"
                md_file.write_text(
                    "# Imported Guide\n\nContent of the guide", encoding="utf-8"
                )

                result = runner.invoke(
                    app,
                    ["guide", "import", str(md_file), "--name", "imported-guide"],
                )
                assert result.exit_code == 0
                assert "Imported guide 'imported-guide'" in result.output

                # Verify the import
                imported = guide._load_guide("imported-guide")
                assert imported["title"] == "Imported Guide"
                assert "Content of the guide" in imported["content"]

    def test_import_guide_json(self):
        """Test importing a guide from JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                # Create a JSON file
                import json

                json_file = Path(tmpdir) / "import.json"
                json_file.write_text(
                    json.dumps(
                        {
                            "title": "JSON Guide",
                            "content": "Content from JSON",
                            "tags": ["json", "test"],
                        }
                    ),
                    encoding="utf-8",
                )

                result = runner.invoke(
                    app,
                    ["guide", "import", str(json_file)],
                )
                assert result.exit_code == 0

                # Verify the import (name defaults to filename without extension)
                imported = guide._load_guide("import")
                assert imported["title"] == "JSON Guide"
                assert "Content from JSON" in imported["content"]

    def test_validate_guide_name_valid(self):
        """Test valid guide names."""
        assert guide._validate_guide_name("valid-name") is True
        assert guide._validate_guide_name("guide123") is True
        assert guide._validate_guide_name("my_guide") is True

    def test_validate_guide_name_invalid_chars(self):
        """Test invalid guide names with special characters."""
        assert guide._validate_guide_name("guide/name") is False
        assert guide._validate_guide_name("guide\\name") is False
        assert guide._validate_guide_name("guide:name") is False
        assert guide._validate_guide_name("guide*name") is False
        assert guide._validate_guide_name("guide?name") is False

    def test_validate_guide_name_path_traversal(self):
        """Test invalid guide names with path traversal."""
        assert guide._validate_guide_name("..") is False
        assert guide._validate_guide_name("../etc") is False
        assert guide._validate_guide_name(".hidden") is False

    def test_import_guide_json_missing_content(self):
        """Test importing JSON file without content field fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(guide, "GUIDES_DIR", Path(tmpdir)):
                import json

                json_file = Path(tmpdir) / "no-content.json"
                json_file.write_text(
                    json.dumps(
                        {
                            "title": "No Content Guide",
                            # No content field
                        }
                    ),
                    encoding="utf-8",
                )

                result = runner.invoke(
                    app,
                    ["guide", "import", str(json_file)],
                )
                assert result.exit_code == 1
                assert "must contain a 'content' field" in result.output
