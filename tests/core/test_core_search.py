"""Tests for core.search module - pure business logic for search command."""

import pytest
from unittest.mock import patch, MagicMock

from fresh.core import Search, SearchConfig


class TestSearchEntity:
    """Tests for Search entity."""

    def test_init_with_config(self):
        """Should initialize with config."""
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        assert entity.config == config
        assert entity.result.query == "test"
        assert entity.result.url == "https://example.com/docs"


class TestSearchGetSyncDir:
    """Tests for get_sync_dir method."""

    def test_get_sync_dir_returns_path(self):
        """Should return default sync directory."""
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        result = entity.get_sync_dir()
        assert ".fresh" in str(result)
        assert "docs" in str(result)


class TestSearchGetSyncDirForUrl:
    """Tests for _get_sync_dir_for_url method."""

    def test_get_sync_dir_for_url_basic(self):
        """Should return sync dir for URL domain."""
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        result = entity._get_sync_dir_for_url("https://example.com/docs/page.html")
        assert "example_com" in str(result)
        assert "pages" in str(result)

    def test_get_sync_dir_for_url_with_port(self):
        """Should handle URL with port."""
        config = SearchConfig(query="test", url="https://example.com:8080/docs")
        entity = Search(config)
        result = entity._get_sync_dir_for_url("https://example.com:8080/docs/page.html")
        assert "example_com_8080" in str(result)


class TestSearchFormatFreshnessAge:
    """Tests for _format_freshness_age method."""

    def test_format_freshness_age_just_now(self):
        """Should format recent timestamp as 'just now'."""
        from datetime import datetime, timezone
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        # Current time should be "just now"
        now = datetime.now(timezone.utc).isoformat()
        result = entity._format_freshness_age(now)
        assert result == "just now"

    def test_format_freshness_age_minutes(self):
        """Should format age in minutes."""
        from datetime import datetime, timedelta, timezone
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        # 30 minutes ago
        past_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        result = entity._format_freshness_age(past_time.isoformat())
        # Should be approximately 30 minutes
        assert "m ago" in result

    def test_format_freshness_age_invalid(self):
        """Should return 'unknown' for invalid timestamp."""
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        result = entity._format_freshness_age("invalid-timestamp")
        assert result == "unknown"


class TestSearchUrlToLocalPath:
    """Tests for _url_to_local_path method."""

    def test_url_to_local_path_basic(self):
        """Should convert URL to local path."""
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        result = entity._url_to_local_path("https://example.com/docs/page.html")
        assert result is not None
        assert "example_com" in str(result)
        assert "page.html" in str(result)

    def test_url_to_local_path_index(self):
        """Should add index.html for directory paths."""
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        result = entity._url_to_local_path("https://example.com/docs/")
        assert "index.html" in str(result)

    def test_url_to_local_path_long_filename(self):
        """Should handle long filenames with hash."""
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        # Create a very long path
        long_path = "https://example.com/" + "a" * 300 + ".html"
        result = entity._url_to_local_path(long_path)
        assert result is not None
        # Should have hash suffix
        assert "_" in str(result)


class TestSearchLocalContentExists:
    """Tests for local_content_exists method."""

    def test_local_content_exists_returns_bool(self):
        """Should return boolean."""
        config = SearchConfig(query="test", url="https://example.com/docs")
        entity = Search(config)
        result = entity.local_content_exists("https://example.com/nonexistent.html")
        assert isinstance(result, bool)


class TestSearchDiscoverLocalUrls:
    """Tests for discover_local_urls method."""

    def test_discover_local_urls_no_directory(self):
        """Should return empty list when no directory exists."""
        config = SearchConfig(query="test", url="https://nonexistent.example.com/docs")
        entity = Search(config)
        result = entity.discover_local_urls("https://nonexistent.example.com/docs", max_pages=10)
        assert result == []


class TestSearchExtractWordsForSuggestions:
    """Tests for extract_words_for_suggestions method."""

    def test_extract_words_basic(self):
        """Should extract words from query."""
        config = SearchConfig(query="test query", url="https://example.com/docs")
        entity = Search(config)
        result = entity.extract_words_for_suggestions("test query")
        assert "test" in result
        assert "query" in result

    def test_extract_words_removes_stopwords(self):
        """Should remove stopwords."""
        config = SearchConfig(query="the test and query", url="https://example.com/docs")
        entity = Search(config)
        result = entity.extract_words_for_suggestions("the test and query")
        assert "the" not in result
        assert "and" not in result
        assert "test" in result
        assert "query" in result

    def test_extract_words_filters_short(self):
        """Should filter out short words."""
        config = SearchConfig(query="a to test", url="https://example.com/docs")
        entity = Search(config)
        result = entity.extract_words_for_suggestions("a to test")
        assert "a" not in result
        assert "to" not in result
        assert "test" in result

    def test_extract_words_limits_count(self):
        """Should limit to 5 words."""
        config = SearchConfig(query=" ".join(["word" + str(i) for i in range(10)]), url="https://example.com/docs")
        entity = Search(config)
        result = entity.extract_words_for_suggestions(config.query)
        assert len(result) <= 5


# Standalone function tests

class TestStandaloneDiscoverLocalUrls:
    """Tests for standalone discover_local_urls function."""

    def test_discover_local_urls_returns_list(self):
        """Should return list."""
        from fresh.core import discover_local_urls
        result = discover_local_urls("https://nonexistent.example.com/docs", max_pages=10)
        assert isinstance(result, list)


class TestStandaloneDiscoverDocumentationUrls:
    """Tests for standalone discover_documentation_urls function."""

    def test_discover_documentation_urls_returns_list(self):
        """Should return list."""
        from fresh.core import discover_documentation_urls
        result = discover_documentation_urls("https://nonexistent.example.com/docs", max_pages=10)
        assert isinstance(result, list)


class TestStandaloneExtractWordsForSuggestions:
    """Tests for standalone extract_words_for_suggestions function."""

    def test_extract_words_for_suggestions_returns_list(self):
        """Should return list of words."""
        from fresh.core import extract_words_for_suggestions
        result = extract_words_for_suggestions("test query")
        assert isinstance(result, list)
        assert "test" in result
        assert "query" in result


class TestStandaloneSearchInLocal:
    """Tests for standalone search_in_local function."""

    def test_search_in_local_returns_list(self):
        """Should return list."""
        from fresh.core import search_in_local
        result = search_in_local("test", "https://nonexistent.example.com/docs")
        assert isinstance(result, list)
