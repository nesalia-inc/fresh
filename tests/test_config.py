"""Tests for config module."""

from __future__ import annotations

import json
import pathlib
import tempfile

import pytest

from fresh import config


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        monkeypatch.setattr(config, "get_config_dir", lambda: tmp_path)
        yield tmp_path


class TestLoadAliases:
    """Tests for load_aliases function."""

    def test_load_builtin_aliases(self):
        """Test that built-in aliases are loaded by default."""
        aliases = config.load_aliases()
        assert "nextjs" in aliases
        assert aliases["nextjs"] == "https://nextjs.org/docs"
        assert "react" in aliases
        assert "vue" in aliases

    def test_load_user_aliases(self, temp_config_dir):
        """Test that user aliases are loaded and override built-ins."""
        aliases_file = temp_config_dir / "aliases.json"
        aliases_file.write_text(json.dumps({"aliases": {"myalias": "https://example.com"}}))

        aliases = config.load_aliases()
        assert "myalias" in aliases
        assert aliases["myalias"] == "https://example.com"

    def test_user_aliases_override_builtin(self, temp_config_dir):
        """Test that user aliases override built-in aliases."""
        aliases_file = temp_config_dir / "aliases.json"
        aliases_file.write_text(json.dumps({"aliases": {"nextjs": "https://custom.com"}}))

        aliases = config.load_aliases()
        assert aliases["nextjs"] == "https://custom.com"

    def test_invalid_json_handled(self, temp_config_dir):
        """Test that invalid JSON is handled gracefully."""
        aliases_file = temp_config_dir / "aliases.json"
        aliases_file.write_text("invalid json{")

        # Should not raise, just log warning
        aliases = config.load_aliases()
        # Should still have built-in aliases
        assert "nextjs" in aliases


class TestSaveAliases:
    """Tests for save_aliases function."""

    def test_save_aliases_creates_file(self, temp_config_dir):
        """Test that save_aliases creates the config file."""
        aliases = {"testalias": "https://test.com"}
        config.save_aliases(aliases)

        aliases_file = temp_config_dir / "aliases.json"
        assert aliases_file.exists()

        with open(aliases_file) as f:
            data = json.load(f)
        assert data["aliases"] == aliases

    def test_save_overwrites_aliases(self, temp_config_dir):
        """Test that save_aliases replaces aliases, not merges."""
        # First save some data
        config.save_aliases({"alias1": "https://example1.com"})

        # Now save new aliases (this replaces, not merges)
        config.save_aliases({"alias2": "https://example2.com"})

        # Check only the new alias is present (save replaces, not merges)
        aliases_file = temp_config_dir / "aliases.json"
        with open(aliases_file) as f:
            data = json.load(f)

        assert "alias2" in data["aliases"]
        assert "alias1" not in data["aliases"]


class TestResolveAlias:
    """Tests for resolve_alias function."""

    def test_resolve_url_returns_as_is(self):
        """Test that full URLs are returned as-is."""
        url = "https://example.com/docs"
        result = config.resolve_alias(url)
        assert result == url

    def test_resolve_known_alias(self):
        """Test that known aliases are resolved."""
        result = config.resolve_alias("nextjs")
        assert result == "https://nextjs.org/docs"

    def test_resolve_unknown_returns_input(self):
        """Test that unknown strings are returned as-is."""
        result = config.resolve_alias("unknownthing")
        assert result == "unknownthing"

    def test_resolve_http_url(self):
        """Test that http URLs are handled."""
        result = config.resolve_alias("http://example.com")
        assert result == "http://example.com"


class TestIsAlias:
    """Tests for is_alias function."""

    def test_url_returns_false(self):
        """Test that URLs return False."""
        assert config.is_alias("https://example.com") is False
        assert config.is_alias("http://example.com") is False

    def test_known_alias_returns_true(self):
        """Test that known aliases return True."""
        assert config.is_alias("nextjs") is True
        assert config.is_alias("react") is True

    def test_unknown_returns_false(self):
        """Test that unknown strings return False."""
        assert config.is_alias("unknownthing") is False


class TestSearchAliases:
    """Tests for search_aliases function."""

    def test_search_by_alias_name(self):
        """Test searching by alias name."""
        results = config.search_aliases("next")
        assert len(results) > 0
        assert any(alias == "nextjs" for alias, _ in results)

    def test_search_by_url(self):
        """Test searching by URL content."""
        results = config.search_aliases("react.dev")
        assert len(results) > 0
        assert any(url == "https://react.dev" for _, url in results)

    def test_search_returns_empty_for_unknown(self):
        """Test that unknown search returns empty list."""
        results = config.search_aliases("xyznonexistent")
        assert results == []

    def test_search_results_sorted(self):
        """Test that search results are sorted by alias name."""
        results = config.search_aliases("js")
        aliases = [alias for alias, _ in results]
        assert aliases == sorted(aliases)
