"""Tests for alias commands."""

from __future__ import annotations

import json
import pathlib
import tempfile

import pytest
from typer.testing import CliRunner

from fresh import config
from fresh.commands.alias import alias_app

runner = CliRunner()


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        monkeypatch.setattr(config, "get_config_dir", lambda: tmp_path)
        yield tmp_path


class TestAliasList:
    """Tests for alias list command."""

    def test_list_user_aliases_empty(self, temp_config_dir):
        """Test listing with no user aliases."""
        result = runner.invoke(alias_app, ["list"])
        assert result.exit_code == 0
        assert "No user aliases found" in result.stdout

    def test_list_user_aliases(self, temp_config_dir):
        """Test listing user aliases."""
        # Create a user alias file
        aliases_file = temp_config_dir / "aliases.json"
        aliases_file.write_text(json.dumps({"aliases": {"myalias": "https://example.com"}}))

        result = runner.invoke(alias_app, ["list"])
        assert result.exit_code == 0
        assert "myalias" in result.stdout

    def test_list_all_aliases(self, temp_config_dir):
        """Test listing all aliases with --all flag."""
        result = runner.invoke(alias_app, ["list", "--all"])
        assert result.exit_code == 0
        assert "nextjs" in result.stdout
        assert "react" in result.stdout


class TestAliasAdd:
    """Tests for alias add command."""

    def test_add_alias_success(self, temp_config_dir):
        """Test adding a new alias."""
        result = runner.invoke(alias_app, ["add", "mytest", "https://test.com"])
        assert result.exit_code == 0
        assert "Added alias" in result.stdout

    def test_add_alias_invalid_url(self, temp_config_dir):
        """Test adding alias with invalid URL."""
        result = runner.invoke(alias_app, ["add", "mytest", "not-a-url"])
        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_add_alias_updates_existing(self, temp_config_dir):
        """Test adding alias updates existing one."""
        # First add
        runner.invoke(alias_app, ["add", "mytest", "https://test1.com"])
        # Then update
        result = runner.invoke(alias_app, ["add", "mytest", "https://test2.com"])

        assert result.exit_code == 0
        assert "Updated" in result.stdout

    def test_add_alias_builtin_warning(self, temp_config_dir):
        """Test adding alias shows warning for built-in."""
        result = runner.invoke(alias_app, ["add", "nextjs", "https://custom.com"])
        assert result.exit_code == 0
        assert "Warning" in result.stdout


class TestAliasRemove:
    """Tests for alias remove command."""

    def test_remove_user_alias(self, temp_config_dir):
        """Test removing a user alias."""
        # First add
        runner.invoke(alias_app, ["add", "mytest", "https://test.com"])

        # Then remove
        result = runner.invoke(alias_app, ["remove", "mytest"])
        assert result.exit_code == 0
        assert "Removed" in result.stdout

    def test_remove_nonexistent_alias(self, temp_config_dir):
        """Test removing non-existent alias."""
        result = runner.invoke(alias_app, ["remove", "nonexistent"])
        assert result.exit_code == 1

    def test_remove_builtin_alias_removes_from_user(self, temp_config_dir):
        """Test removing built-in alias removes from user config."""
        # First add a built-in alias to user config (overriding)
        runner.invoke(alias_app, ["add", "nextjs", "https://custom.com"])

        # Then remove it - should succeed
        result = runner.invoke(alias_app, ["remove", "nextjs"])
        assert result.exit_code == 0
        assert "Removed" in result.stdout


class TestAliasSearch:
    """Tests for alias search command."""

    def test_search_finds_alias(self, temp_config_dir):
        """Test searching finds matching aliases."""
        result = runner.invoke(alias_app, ["search", "next"])
        assert result.exit_code == 0
        assert "nextjs" in result.stdout

    def test_search_finds_nothing(self, temp_config_dir):
        """Test searching finds nothing."""
        result = runner.invoke(alias_app, ["search", "xyznonexistent"])
        assert result.exit_code == 1
        assert "No aliases found" in result.stdout
