"""Tests for core.list module - pure business logic for list command."""

import pytest

from fresh.core import List, ListConfig


class TestListEntity:
    """Tests for List entity."""

    def test_init_with_config(self):
        """Should initialize with config."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        assert entity.config == config


class TestListDiscoverPages:
    """Tests for discover_pages method."""

    def test_discover_pages_returns_list(self):
        """Should return a list of entries."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        # Without actual crawler/sitemap, this will return empty or limited results
        # but should still return a list
        result = entity.discover_pages("https://example.com/docs", max_pages=5, depth=1)
        assert isinstance(result, list)


class TestListFilterByPattern:
    """Tests for filter_by_pattern method."""

    def test_filter_by_pattern_basic(self):
        """Should filter URLs by pattern."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        urls = [
            "https://example.com/docs/api",
            "https://example.com/docs/guide",
            "https://example.com/docs/about",
        ]
        result = entity.filter_by_pattern(urls, "api")
        assert len(result) == 1
        assert "api" in result[0]


class TestListSortEntries:
    """Tests for sort_entries method."""

    def test_sort_by_name(self):
        """Should sort entries by name."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        entries = [
            {"name": "zebra", "path": "/zebra", "url": "https://example.com/zebra"},
            {"name": "apple", "path": "/apple", "url": "https://example.com/apple"},
            {"name": "banana", "path": "/banana", "url": "https://example.com/banana"},
        ]
        result = entity.sort_entries(entries, "name")
        assert result[0]["name"] == "apple"
        assert result[1]["name"] == "banana"
        assert result[2]["name"] == "zebra"

    def test_sort_by_path(self):
        """Should sort entries by path."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        entries = [
            {"name": "zebra", "path": "/zebra", "url": "https://example.com/zebra"},
            {"name": "apple", "path": "/apple", "url": "https://example.com/apple"},
            {"name": "banana", "path": "/banana", "url": "https://example.com/banana"},
        ]
        result = entity.sort_entries(entries, "path")
        assert result[0]["path"] == "/apple"
        assert result[1]["path"] == "/banana"
        assert result[2]["path"] == "/zebra"

    def test_sort_does_not_mutate_original(self):
        """Should not mutate original entries list."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        original = [
            {"name": "zebra", "path": "/zebra", "url": "https://example.com/zebra"},
            {"name": "apple", "path": "/apple", "url": "https://example.com/apple"},
        ]
        original_copy = original.copy()
        entity.sort_entries(original, "name")
        assert original == original_copy


class TestListFormatAsJson:
    """Tests for format_as_json method."""

    def test_format_as_json_basic(self):
        """Should format entries as JSON."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        entries = [
            {"name": "test", "path": "/test", "url": "https://example.com/test"},
        ]
        result = entity.format_as_json(entries, indent=2)
        assert '"name": "test"' in result
        assert '"path": "/test"' in result
        assert '"url": "https://example.com/test"' in result

    def test_format_as_json_no_indent(self):
        """Should format entries as JSON without indent."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        entries = [
            {"name": "test", "path": "/test", "url": "https://example.com/test"},
        ]
        result = entity.format_as_json(entries, indent=0)
        assert "test" in result


class TestListFormatAsXml:
    """Tests for format_as_xml method."""

    def test_format_as_xml_basic(self):
        """Should format entries as XML."""
        config = ListConfig(url="https://example.com/docs")
        entity = List(config)
        entries = [
            {"name": "test", "path": "/test", "url": "https://example.com/test"},
        ]
        result = entity.format_as_xml(entries)
        assert "<page>" in result
        assert "<name>test</name>" in result
        assert "<path>/test</path>" in result
        assert "<url>https://example.com/test</url>" in result


# Standalone function tests

class TestStandaloneDiscoverPages:
    """Tests for standalone discover_pages function."""

    def test_discover_pages_returns_list(self):
        """Should return a list."""
        from fresh.core import discover_pages
        result = discover_pages("https://example.com/docs", max_pages=5, depth=1)
        assert isinstance(result, list)


class TestStandaloneFilterByPattern:
    """Tests for standalone filter_by_pattern function."""

    def test_filter_by_pattern_returns_list(self):
        """Should return filtered list."""
        from fresh.core import filter_by_pattern
        urls = [
            "https://example.com/docs/api",
            "https://example.com/docs/guide",
        ]
        result = filter_by_pattern(urls, "api")
        assert len(result) == 1


class TestStandaloneSortEntries:
    """Tests for standalone sort_entries function."""

    def test_sort_entries_returns_sorted(self):
        """Should return sorted entries."""
        from fresh.core import sort_entries
        entries = [
            {"name": "zebra", "path": "/zebra", "url": "https://example.com/zebra"},
            {"name": "apple", "path": "/apple", "url": "https://example.com/apple"},
        ]
        result = sort_entries(entries, "name")
        assert result[0]["name"] == "apple"


class TestStandaloneFormatAsJson:
    """Tests for standalone format_as_json function."""

    def test_format_as_json_returns_string(self):
        """Should return JSON string."""
        from fresh.core import format_as_json
        entries = [{"name": "test", "path": "/test", "url": "https://example.com/test"}]
        result = format_as_json(entries)
        assert isinstance(result, str)
        assert "test" in result


class TestStandaloneFormatAsXml:
    """Tests for standalone format_as_xml function."""

    def test_format_as_xml_returns_string(self):
        """Should return XML string."""
        from fresh.core import format_as_xml
        entries = [{"name": "test", "path": "/test", "url": "https://example.com/test"}]
        result = format_as_xml(entries)
        assert isinstance(result, str)
        assert "<page>" in result


class TestStandaloneCreateEntry:
    """Tests for standalone create_entry function."""

    def test_create_entry_returns_dict(self):
        """Should return entry dict."""
        from fresh.core import create_entry
        result = create_entry("test", "/test", "https://example.com/test")
        assert result == {
            "name": "test",
            "path": "/test",
            "url": "https://example.com/test",
        }
