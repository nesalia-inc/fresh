"""Integration tests for websearch module.

These tests make real HTTP requests to search engines.
Run with: pytest -m integration
"""

import pytest

from fresh.scraper.websearch import (
    websearch,
    search_duckduckgo,
)


@pytest.mark.integration
def test_duckduckgo_integration():
    """Test that DuckDuckGo search returns actual results.

    Note: DuckDuckGo may rate-limit requests. This test may fail
    if too many requests are made in a short period.
    """
    results = search_duckduckgo("python", count=3)
    # DuckDuckGo may rate-limit, so we check but allow empty if rate-limited
    if len(results) == 0:
        pytest.skip("DuckDuckGo rate-limited or unavailable")
    # Verify structure
    for r in results:
        assert r.title
        assert r.url.startswith("http")
        assert hasattr(r, "to_dict")


@pytest.mark.integration
def test_websearch_empty_query():
    """Test empty query handling."""
    results = websearch("")
    assert results == []


@pytest.mark.integration
def test_websearch_whitespace_only():
    """Test whitespace-only query handling."""
    results = websearch("   ")
    assert results == []
