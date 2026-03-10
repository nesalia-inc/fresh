"""Web search functionality for Fresh."""

from __future__ import annotations

import logging
import os
import time
import urllib.parse
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

# DuckDuckGo HTML search URL
DDG_SEARCH_URL = "https://html.duckduckgo.com/html/"

# Brave Search API URL
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

# User-Agent to mimic a real browser
DDG_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Default number of results
DEFAULT_RESULT_COUNT = 10


@dataclass
class WebSearchResult:
    """Represents a web search result."""

    title: str
    url: str
    description: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
        }


def _parse_ddg_html(html_content: str) -> list[WebSearchResult]:
    """Parse DuckDuckGo HTML search results.

    Args:
        html_content: The HTML content from DuckDuckGo search

    Returns:
        List of WebSearchResult objects
    """
    from bs4 import BeautifulSoup

    results: list[WebSearchResult] = []

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all result links
        for result in soup.select("a.result__a"):
            try:
                title = result.get_text(strip=True)
                url = result.get("href", "")

                if not title or not url:
                    continue

                # Skip ads - they redirect through duckduckgo.com/y.js with ad_provider
                if "duckduckgo.com/y.js" in url and "ad_provider" in url:
                    continue

                # Find the description (usually in the next sibling or result__snippet)
                description = ""
                parent = result.find_parent("div", class_="result__body")
                if parent:
                    snippet = parent.select_one("a.result__snippet")
                    if snippet:
                        description = snippet.get_text(strip=True)
                    else:
                        # Try to get from result__rich
                        rich = parent.select_one("div.result__rich")
                        if rich:
                            description = rich.get_text(strip=True)

                # Clean up URL (DDG redirects through their own URL)
                if "uddg=" in url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                    actual_url = parsed.get("uddg", [url])[0]
                    # Make sure it's a valid URL
                    if actual_url.startswith("http"):
                        url = actual_url

                # Skip if URL is not valid
                if not url.startswith("http"):
                    continue

                results.append(
                    WebSearchResult(
                        title=title,
                        url=url,
                        description=description,
                    )
                )
            except Exception as e:
                logger.debug(f"Failed to parse a result: {e}")
                continue

    except Exception as e:
        logger.error(f"Failed to parse DuckDuckGo HTML: {e}")

    return results


def search_duckduckgo(
    query: str,
    count: int = DEFAULT_RESULT_COUNT,
) -> list[WebSearchResult]:
    """Search using DuckDuckGo HTML interface.

    Args:
        query: The search query
        count: Maximum number of results to return

    Returns:
        List of WebSearchResult objects
    """
    # Rate limiting - be respectful
    time.sleep(0.5)

    # Prepare the request
    data = {
        "q": query,
        "b": "",  # Pagination offset
    }

    client = httpx.Client(
        headers=DDG_HEADERS,
        timeout=30.0,
        follow_redirects=True,
    )

    try:
        response = client.post(DDG_SEARCH_URL, data=data)
        response.raise_for_status()

        results = _parse_ddg_html(response.text)

        # Limit results
        return results[:count]

    except httpx.HTTPError as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during DuckDuckGo search: {e}")
        return []
    finally:
        client.close()


def search_brave(
    query: str,
    count: int = DEFAULT_RESULT_COUNT,
    api_key: str | None = None,
) -> list[WebSearchResult]:
    """Search using Brave Search API.

    Args:
        query: The search query
        count: Maximum number of results to return
        api_key: Brave Search API key (optional, uses BRAVE_API_KEY env var if not provided)

    Returns:
        List of WebSearchResult objects
    """
    if api_key is None:
        api_key = os.environ.get("BRAVE_API_KEY")

    if not api_key:
        logger.warning("Brave API key not provided")
        return []

    # Rate limiting
    time.sleep(0.5)

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
    }

    params = {
        "q": query,
        "count": min(count, 20),  # Brave max is 20
    }

    try:
        response = httpx.get(
            BRAVE_SEARCH_URL,
            headers=headers,
            params=params,
            timeout=30.0,
        )
        response.raise_for_status()

        data = response.json()
        results: list[WebSearchResult] = []

        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                results.append(
                    WebSearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        description=item.get("description", ""),
                    )
                )

        return results[:count]

    except httpx.HTTPError as e:
        logger.error(f"Brave Search API failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during Brave search: {e}")
        return []


def websearch(
    query: str,
    count: int = DEFAULT_RESULT_COUNT,
    engine: str = "auto",
) -> list[WebSearchResult]:
    """Perform a web search with automatic fallback.

    Args:
        query: The search query
        count: Maximum number of results to return
        engine: Search engine to use ("auto", "ddg", "brave")

    Returns:
        List of WebSearchResult objects
    """
    if not query or not query.strip():
        logger.warning("Empty search query")
        return []

    query = query.strip()

    # Determine which engine to use
    use_engine = engine

    if engine == "auto":
        # Check if Brave API key is available
        if os.environ.get("BRAVE_API_KEY"):
            use_engine = "brave"
        else:
            use_engine = "ddg"

    # Try the primary engine
    if use_engine == "brave":
        results = search_brave(query, count)
        if results:
            return results
        # Fallback to DuckDuckGo if Brave fails
        logger.info("Brave search failed, falling back to DuckDuckGo")
        return search_duckduckgo(query, count)

    elif use_engine == "ddg":
        return search_duckduckgo(query, count)

    else:
        logger.warning(f"Unknown search engine: {engine}")
        return []
