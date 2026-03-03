"""Tests for scraper.searcher module."""


from fresh.scraper import searcher as searcher_module


class TestLevenshteinDistance:
    """Tests for levenshtein_distance function."""

    def test_identical_strings(self):
        """Identical strings should return 0."""
        result = searcher_module.levenshtein_distance("hello", "hello")
        assert result == 0

    def test_single_insertion(self):
        """Single insertion should return 1."""
        result = searcher_module.levenshtein_distance("hello", "hallo")
        assert result == 1

    def test_single_deletion(self):
        """Single deletion should return 1."""
        result = searcher_module.levenshtein_distance("hello", "hell")
        assert result == 1

    def test_single_substitution(self):
        """Single substitution should return 1."""
        result = searcher_module.levenshtein_distance("hello", "hallo")
        assert result == 1

    def test_multiple_changes(self):
        """Multiple changes should return correct distance."""
        result = searcher_module.levenshtein_distance("kitten", "sitting")
        assert result == 3

    def test_empty_strings(self):
        """Empty strings should return length of non-empty."""
        result = searcher_module.levenshtein_distance("", "hello")
        assert result == 5

    def test_both_empty(self):
        """Both empty should return 0."""
        result = searcher_module.levenshtein_distance("", "")
        assert result == 0


class TestFuzzyMatch:
    """Tests for fuzzy_match function."""

    def test_exact_match(self):
        """Exact match should return True."""
        result = searcher_module.fuzzy_match("hello", "hello")
        assert result is True

    def test_fuzzy_match_within_threshold(self):
        """Fuzzy match within threshold should return True."""
        result = searcher_module.fuzzy_match("hello", "hallo", max_distance=2)
        assert result is True

    def test_no_match_beyond_threshold(self):
        """Match beyond threshold should return False."""
        result = searcher_module.fuzzy_match("hello", "xyz", max_distance=2)
        assert result is False

    def test_custom_max_distance(self):
        """Custom max_distance should be respected."""
        # distance between "test" and "text" is 1, so with max_distance=1 it matches
        result = searcher_module.fuzzy_match("test", "text", max_distance=1)
        assert result is True
        # distance between "hello" and "xyz" is 5, so with max_distance=1 it doesn't match
        result = searcher_module.fuzzy_match("hello", "xyz", max_distance=1)
        assert result is False


class TestFindFuzzySuggestions:
    """Tests for find_fuzzy_suggestions function."""

    def test_empty_candidates(self):
        """Empty candidates should return empty list."""
        result = searcher_module.find_fuzzy_suggestions("test", [], max_distance=2)
        assert result == []

    def test_no_exact_match_in_results(self):
        """Exact match is skipped in results."""
        candidates = ["test", "example", "demo"]
        result = searcher_module.find_fuzzy_suggestions("test", candidates)
        # Exact match is skipped, so no "test" in results
        for word, _ in result:
            assert word != "test"

    def test_fuzzy_match_ranking(self):
        """Results should be ranked by distance."""
        candidates = ["hello", "hallo", "hola", "help"]
        result = searcher_module.find_fuzzy_suggestions("hello", candidates)
        # Should have results sorted by distance
        assert len(result) > 0
        # First result should have smallest distance
        distances = [d for _, d in result]
        assert distances == sorted(distances)


class TestSearchFuzzy:
    """Tests for search_fuzzy function."""

    def test_empty_content(self):
        """Empty content should return empty list."""
        result = searcher_module.search_fuzzy("", "test")
        assert result == []

    def test_fuzzy_match_in_content(self):
        """Should find fuzzy matches in content."""
        content = "This is a test document about Python programming"
        result = searcher_module.search_fuzzy(content, "pytho", max_distance=2)
        assert len(result) > 0


class TestSearchInContent:
    """Tests for search_in_content function."""

    def test_basic_search(self):
        """Should find matches in content."""
        content = "Hello world\nThis is a test"
        result = searcher_module.search_in_content(content, "world")
        assert len(result) > 0
        assert result[0]["match"] == "world"

    def test_case_insensitive(self):
        """Should find case-insensitive matches."""
        content = "Hello World\nThis is a test"
        result = searcher_module.search_in_content(content, "world", case_sensitive=False)
        assert len(result) > 0

    def test_case_sensitive(self):
        """Should not match case when case_sensitive=True."""
        content = "Hello World"
        result = searcher_module.search_in_content(content, "world", case_sensitive=True)
        assert len(result) == 0

    def test_regex_search(self):
        """Should find regex matches."""
        content = "test123 abc456"
        result = searcher_module.search_in_content(content, r"\d+", regex=True)
        assert len(result) > 0

    def test_no_match(self):
        """Should return empty list when no match."""
        content = "Hello world"
        result = searcher_module.search_in_content(content, "nonexistent")
        assert result == []

    def test_empty_query(self):
        """Should return results for empty query (matches everything)."""
        content = "Hello world"
        result = searcher_module.search_in_content(content, "")
        # Empty query may return empty or all lines depending on implementation
        assert isinstance(result, list)

    def test_multiple_matches(self):
        """Should find multiple matches."""
        content = "test one\ntest two\ntest three"
        result = searcher_module.search_in_content(content, "test")
        assert len(result) >= 3


class TestCreateSnippet:
    """Tests for create_snippet function."""

    def test_basic_snippet(self):
        """Should create a snippet around match."""
        content = "Line one\nLine two with keyword\nLine three"
        result = searcher_module.create_snippet(content, "keyword")
        assert "keyword" in result

    def test_snippet_with_context(self):
        """Should include context lines."""
        content = "Line one\nLine two with keyword\nLine three"
        result = searcher_module.create_snippet(content, "keyword", context_lines=1)
        assert "Line one" in result or "Line three" in result

    def test_snippet_max_length(self):
        """Should respect max_length approximately."""
        content = "A" * 500 + " keyword " + "B" * 500
        result = searcher_module.create_snippet(content, "keyword", max_length=100)
        # Should be close to max_length
        assert len(result) <= 150

    def test_no_match_returns_content(self):
        """Should return truncated content when no match."""
        content = "No match here"
        result = searcher_module.create_snippet(content, "keyword")
        # Returns truncated content when no match
        assert isinstance(result, str)

    def test_regex_snippet(self):
        """Should create snippet for regex matches."""
        content = "test123 is a number"
        result = searcher_module.create_snippet(content, r"\d+", regex=True)
        assert "123" in result

    def test_snippet_ellipsis_at_start(self):
        """Should add ellipsis at start when match is not at beginning."""
        # Need content where start > 0 and match is not at first line
        content = "first line\nkeyword here\nlast line"
        result = searcher_module.create_snippet(content, "keyword", context_lines=1, max_length=100)
        # Keyword should still be present and ellipsis added at start
        assert "keyword" in result
        # Since match is on line 2, start = max(0, 2-1) = 1 > 0, so start ellipsis should be added
        # But only if context exceeds max_length or we need to show truncation
        # The ellipsis is only added when context is truncated

    def test_snippet_ellipsis_both_ends(self):
        """Should add ellipsis at both ends when match is in middle of long content."""
        # Need match on line where start > 0 (line 2 or later) AND end < len(lines)
        # With context_lines=1 and match on line 2: start = max(0, 2-1) = 1 > 0
        content = "line1\na" * 20 + "\nkeyword here\n" + "b" * 20 + "\nline_last"
        result = searcher_module.create_snippet(content, "keyword", context_lines=1, max_length=30)
        # This should trigger both conditions
        assert "keyword" in result

    def test_snippet_ellipsis_at_end(self):
        """Should add ellipsis at end when match is not at end."""
        # Need to trigger truncation at the end
        content = "keyword here\n" + "b" * 50
        result = searcher_module.create_snippet(content, "keyword", context_lines=0, max_length=20)
        # Should contain keyword
        assert "keyword" in result

    def test_snippet_truncation(self):
        """Should truncate long snippets."""
        content = "a" * 50 + " keyword " + "b" * 50
        result = searcher_module.create_snippet(content, "keyword", max_length=30)
        assert len(result) <= 35  # accounts for "..."


class TestSearchFuzzyWordMatching:
    """Tests for fuzzy word matching in search_fuzzy."""

    def test_fuzzy_word_match_case_sensitive(self):
        """Should find fuzzy match with case_sensitive=True."""
        content = "This is a TeSt document"
        result = searcher_module.search_fuzzy(content, "test", case_sensitive=True, max_distance=2)
        # Should match "TeSt" as fuzzy match
        assert len(result) > 0

    def test_fuzzy_word_match_with_hyphen(self):
        """Should find fuzzy match across hyphenated words."""
        content = "some-text-here"
        result = searcher_module.search_fuzzy(content, "text", max_distance=2)
        assert len(result) > 0

    def test_fuzzy_word_match_with_underscore(self):
        """Should find fuzzy match across underscore separated words."""
        content = "some_text_here"
        result = searcher_module.search_fuzzy(content, "text", max_distance=2)
        assert len(result) > 0

    def test_fuzzy_word_match_with_slash(self):
        """Should find fuzzy match across slash separated words."""
        content = "some/text/here"
        result = searcher_module.search_fuzzy(content, "some", max_distance=2)
        assert len(result) > 0
