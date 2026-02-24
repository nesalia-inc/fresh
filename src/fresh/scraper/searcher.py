"""Search functionality for documentation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class SearchResult:
    """Represents a search result."""

    path: str
    title: str
    snippet: str
    url: str


def search_in_content(
    content: str,
    query: str,
    case_sensitive: bool = False,
    regex: bool = False,
    context_lines: int = 1,
) -> list[dict[str, Any]]:
    """
    Search for a query in markdown content.

    Args:
        content: The markdown content to search in
        query: The search query
        case_sensitive: Whether to do case-sensitive search
        regex: Whether to treat query as regex
        context_lines: Number of lines to include around the match

    Returns:
        List of matches with snippet and line number
    """
    results: list[dict[str, Any]] = []

    if not regex:
        # Escape special regex characters for literal search
        query = re.escape(query)

    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(query, flags)

    lines = content.split("\n")

    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            # Get surrounding context
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            context = "\n".join(lines[start:end])

            # Create snippet with markers
            snippet = context
            if not case_sensitive:
                # Highlight match case-insensitively
                snippet = pattern.sub(lambda m: f"[{m.group()}]", snippet, count=1)

            results.append(
                {
                    "line_number": i + 1,
                    "snippet": snippet.strip(),
                    "match": match.group(),
                }
            )

    return results


def extract_title_from_content(content: str) -> str:
    """Extract title from markdown content (first heading)."""
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            # Remove heading markers
            return line.lstrip("#").strip()
    return ""


def create_snippet(
    content: str,
    query: str,
    max_length: int = 200,
) -> str:
    """Create a short snippet around the first match."""
    query_lower = query.lower()
    content_lower = content.lower()

    # Find the position of the query
    pos = content_lower.find(query_lower)
    if pos == -1:
        # Return beginning of content if no match
        return content[:max_length] + "..." if len(content) > max_length else content

    # Get a window around the match
    start = max(0, pos - 50)
    end = min(len(content), pos + len(query) + 150)

    snippet = content[start:end]

    # Add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."

    return snippet
