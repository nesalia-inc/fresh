"""Tests for scraper.websearch module."""

from fresh.scraper.websearch import (
    WebSearchResult,
    _parse_ddg_html,
    search_brave,
    search_duckduckgo,
    websearch,
)


class TestWebSearchResult:
    """Tests for WebSearchResult dataclass."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = WebSearchResult(
            title="Test Title",
            url="https://example.com",
            description="Test description",
        )
        d = result.to_dict()
        assert d["title"] == "Test Title"
        assert d["url"] == "https://example.com"
        assert d["description"] == "Test description"


class TestParseDDGHTML:
    """Tests for DuckDuckGo HTML parsing."""

    def test_parse_basic_results(self):
        """Test parsing basic search results."""
        html = """
        <html>
        <body>
            <div class="result__body">
                <a class="result__a" href="https://example.com">Example Site</a>
                <a class="result__snippet" href="#">This is a description</a>
            </div>
            <div class="result__body">
                <a class="result__a" href="https://example2.com">Example Site 2</a>
                <a class="result__snippet" href="#">Another description</a>
            </div>
        </body>
        </html>
        """
        results = _parse_ddg_html(html)
        assert len(results) == 2
        assert results[0].title == "Example Site"
        assert results[0].url == "https://example.com"
        assert results[0].description == "This is a description"

    def test_parse_with_uddg_redirect(self):
        """Test parsing results with DuckDuckGo URL redirect."""
        html = """
        <html>
        <body>
            <div class="result__body">
                <a class="result__a" href="https://duckduckgo.com/?uddg=https://example.com&q=test">Example</a>
            </div>
        </body>
        </html>
        """
        results = _parse_ddg_html(html)
        assert len(results) == 1
        assert results[0].url == "https://example.com"

    def test_skip_ads(self):
        """Test that ads are skipped."""
        html = """
        <html>
        <body>
            <div class="result__body">
                <a class="result__a" href="https://duckduckgo.com/y.js?ad_provider=bing&uddg=https://ad.com">Ad</a>
            </div>
            <div class="result__body">
                <a class="result__a" href="https://example.com">Real Result</a>
            </div>
        </body>
        </html>
        """
        results = _parse_ddg_html(html)
        assert len(results) == 1
        assert results[0].title == "Real Result"

    def test_empty_html(self):
        """Test parsing empty HTML."""
        results = _parse_ddg_html("")
        assert results == []

    def test_no_results(self):
        """Test parsing HTML with no results."""
        html = "<html><body><p>No results</p></body></html>"
        results = _parse_ddg_html(html)
        assert results == []


class TestSearchDuckDuckGo:
    """Tests for DuckDuckGo search (requires network)."""

    def test_empty_query_returns_empty(self):
        """Test that empty query returns empty results."""
        # Empty query should return empty list
        results = search_duckduckgo("")
        assert results == []


class TestSearchBrave:
    """Tests for Brave search (requires API key)."""

    def test_no_api_key_returns_empty(self):
        """Test that Brave search returns empty without API key."""
        # Without API key, should return empty
        results = search_brave("test")
        assert results == []


class TestWebsearch:
    """Tests for main websearch function."""

    def test_empty_query(self):
        """Test that empty query returns empty results."""
        results = websearch("")
        assert results == []

    def test_whitespace_only_query(self):
        """Test that whitespace-only query returns empty results."""
        results = websearch("   ")
        assert results == []
