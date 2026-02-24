"""Search functionality for documentation."""

from __future__ import annotations

import re
from dataclasses import dataclass


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
) -> list[dict[str, str]]:
    """
    Search for a query in content.

    Args:
        content: The content to search in
        query: The search query
        case_sensitive: Whether to do case-sensitive search
        regex: Whether to treat query as regex

    Returns:
        List of matches with snippet and match text

    Raises:
        re.error: If regex pattern is invalid
    """
    results: list[dict[str, str]] = []

    if not regex:
        # Escape special regex characters for literal search
        query = re.escape(query)

    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(query, flags)

    lines = content.split("\n")

    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            results.append(
                {
                    "line_number": str(i + 1),
                    "snippet": line.strip()[:200],
                    "match": match.group(),
                }
            )

    return results


def create_snippet(
    content: str,
    query: str,
    context_lines: int = 1,
    max_length: int = 200,
    case_sensitive: bool = False,
) -> str:
    """Create a short snippet around the first match.

    Args:
        content: The content to search in
        query: The search query
        context_lines: Number of lines of context around the match
        max_length: Maximum length of the snippet
        case_sensitive: Whether to do case-sensitive matching

    Returns:
        A snippet string with context around the match
    """
    lines = content.split("\n")

    # Find the line with the match
    match_line_idx = -1
    for i, line in enumerate(lines):
        if case_sensitive:
            if query in line:
                match_line_idx = i
                break
        else:
            if query.lower() in line.lower():
                match_line_idx = i
                break

    if match_line_idx == -1:
        # Return beginning of content if no match
        return content[:max_length] + "..." if len(content) > max_length else content

    # Get surrounding context
    start = max(0, match_line_idx - context_lines)
    end = min(len(lines), match_line_idx + context_lines + 1)

    context = "\n".join(lines[start:end])

    # Truncate
    if len(context) > max_length:
        context = context[:max_length] + "..."

    # Add ellipsis if truncated
    if start > 0:
        context = "..." + context
    if end < len(lines):
        context = context + "..."

    return context
