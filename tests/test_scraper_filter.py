"""Tests for scraper.filter module."""

import pytest

from fresh.scraper import filter as filter_module


class TestIsRelevantUrl:
    """Tests for is_relevant_url function."""

    def test_include_docs_path(self):
        """URLs with /docs/ should be included."""
        assert filter_module.is_relevant_url("https://example.com/docs/guide")
        assert filter_module.is_relevant_url("https://example.com/doc/guide")

    def test_include_api_path(self):
        """URLs with /api/ should be included."""
        assert filter_module.is_relevant_url("https://example.com/api/users")

    def test_include_guide_path(self):
        """URLs with /guide/ should be included."""
        assert filter_module.is_relevant_url("https://example.com/guides/tutorial")

    def test_include_reference_path(self):
        """URLs with /reference/ should be included."""
        assert filter_module.is_relevant_url("https://example.com/reference/api")

    def test_include_tutorial_path(self):
        """URLs with /tutorial/ should be included."""
        assert filter_module.is_relevant_url("https://example.com/tutorials/intro")

    def test_include_learn_path(self):
        """URLs with /learn/ should be included."""
        assert filter_module.is_relevant_url("https://example.com/learn/python")

    def test_include_version_path(self):
        """URLs with version numbers should be included."""
        assert filter_module.is_relevant_url("https://example.com/v14/docs")
        assert filter_module.is_relevant_url("https://example.com/v3/api")

    def test_exclude_blog(self):
        """URLs with /blog/ should be excluded."""
        assert not filter_module.is_relevant_url("https://example.com/blog/post")

    def test_exclude_news(self):
        """URLs with /news/ should be excluded."""
        assert not filter_module.is_relevant_url("https://example.com/news/updates")

    def test_exclude_pricing(self):
        """URLs with /pricing/ should be excluded."""
        assert not filter_module.is_relevant_url("https://example.com/pricing")

    def test_exclude_contact(self):
        """URLs with /contact/ should be excluded."""
        assert not filter_module.is_relevant_url("https://example.com/contact")

    def test_exclude_404(self):
        """URLs with 404 should be excluded."""
        assert not filter_module.is_relevant_url("https://example.com/404")

    def test_custom_patterns(self):
        """Custom patterns should override defaults."""
        assert filter_module.is_relevant_url(
            "https://example.com/custom/path",
            patterns=[r"/custom/"],
        )
        assert not filter_module.is_relevant_url(
            "https://example.com/docs",
            patterns=[r"/custom/"],
        )


class TestExtractNameFromUrl:
    """Tests for extract_name_from_url function."""

    def test_simple_path(self):
        """Extract name from simple path."""
        result = filter_module.extract_name_from_url(
            "https://example.com/docs/getting-started",
        )
        assert "Getting" in result and "Started" in result

    def test_index_file(self):
        """Index files should be handled."""
        result = filter_module.extract_name_from_url(
            "https://example.com/docs/index.html",
        )
        assert "docs" in result.lower()

    def test_api_endpoint(self):
        """API endpoints should be handled."""
        result = filter_module.extract_name_from_url(
            "https://api.example.com/v1/users",
        )
        assert "Users" in result

    def test_dashes_to_spaces(self):
        """Dashes should be converted to spaces."""
        result = filter_module.extract_name_from_url(
            "https://example.com/docs/quick-start-guide",
        )
        assert "Quick Start Guide" in result

    def test_version_removal(self):
        """Version numbers should be removed."""
        result = filter_module.extract_name_from_url(
            "https://example.com/docs/v14/api",
        )
        assert "v14" not in result

    def test_empty_path(self):
        """Empty path should return URL."""
        result = filter_module.extract_name_from_url("https://example.com")
        assert result == "https://example.com"


class TestDeduplicate:
    """Tests for deduplicate function."""

    def test_basic_deduplication(self):
        """Basic duplicate removal."""
        urls = [
            "https://example.com/docs",
            "https://example.com/docs",
            "https://example.com/api",
        ]
        result = filter_module.deduplicate(urls)
        assert len(result) == 2
        assert result[0] == "https://example.com/docs"

    def test_case_insensitive(self):
        """Duplicates should be case-insensitive."""
        urls = [
            "https://example.com/docs",
            "https://example.com/DOCS",
            "https://example.com/Docs",
        ]
        result = filter_module.deduplicate(urls)
        assert len(result) == 1

    def test_trailing_slash(self):
        """URLs with trailing slash should be deduplicated."""
        urls = [
            "https://example.com/docs",
            "https://example.com/docs/",
        ]
        result = filter_module.deduplicate(urls)
        assert len(result) == 1

    def test_strip_query_default(self):
        """Query strings should be stripped by default."""
        urls = [
            "https://example.com/docs?lang=en",
            "https://example.com/docs?lang=fr",
        ]
        result = filter_module.deduplicate(urls)
        assert len(result) == 1

    def test_keep_query_when_disabled(self):
        """Query strings should be kept when disabled."""
        urls = [
            "https://example.com/docs?lang=en",
            "https://example.com/docs?lang=fr",
        ]
        result = filter_module.deduplicate(urls, strip_query=False)
        assert len(result) == 2

    def test_strip_fragment_default(self):
        """Fragments should be stripped by default."""
        urls = [
            "https://example.com/docs#section1",
            "https://example.com/docs#section2",
        ]
        result = filter_module.deduplicate(urls)
        assert len(result) == 1

    def test_keep_fragment_when_disabled(self):
        """Fragments should be kept when disabled."""
        urls = [
            "https://example.com/docs#section1",
            "https://example.com/docs#section2",
        ]
        result = filter_module.deduplicate(urls, strip_fragment=False)
        assert len(result) == 2

    def test_preserve_order(self):
        """Order should be preserved."""
        urls = [
            "https://example.com/a",
            "https://example.com/b",
            "https://example.com/a",
            "https://example.com/c",
        ]
        result = filter_module.deduplicate(urls)
        assert result == [
            "https://example.com/a",
            "https://example.com/b",
            "https://example.com/c",
        ]


class TestFilterByPattern:
    """Tests for filter_by_pattern function."""

    def test_simple_glob(self):
        """Simple glob pattern matching."""
        urls = [
            "https://example.com/docs/guide",
            "https://example.com/api/users",
            "https://example.com/blog/post",
        ]
        result = filter_module.filter_by_pattern(urls, "/docs/*")
        assert len(result) == 1
        assert "docs" in result[0]

    def test_double_star_glob(self):
        """Double star glob pattern."""
        urls = [
            "https://example.com/docs/api/intro",
            "https://example.com/docs/api/advanced",
            "https://example.com/blog/post",
        ]
        result = filter_module.filter_by_pattern(urls, "/docs/**")
        assert len(result) == 2

    def test_case_insensitive_glob(self):
        """Glob should be case insensitive."""
        urls = [
            "https://example.com/Docs/Guide",
            "https://example.com/api/users",
        ]
        result = filter_module.filter_by_pattern(urls, "/docs/*")
        assert len(result) == 1

    def test_no_matches(self):
        """No matches should return empty list."""
        urls = [
            "https://example.com/blog/post",
            "https://example.com/about",
        ]
        result = filter_module.filter_by_pattern(urls, "/docs/*")
        assert len(result) == 0
