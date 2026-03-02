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
