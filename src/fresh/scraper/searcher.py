"""Search functionality for documentation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class SearchResult:
    """Represents a search result."""

    path: str
    title: str
    snippet: str
    url: str
    source: str = "remote"  # "local" or "remote"


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
    regex: bool = False,
) -> str:
    """Create a short snippet around the first match.

    Args:
        content: The content to search in
        query: The search query
        context_lines: Number of lines of context around the match
        max_length: Maximum length of the snippet
        case_sensitive: Whether to do case-sensitive matching
        regex: Whether to treat query as regex

    Returns:
        A snippet string with context around the match
    """
    lines = content.split("\n")

    # Compile pattern for matching
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(query, flags)

    # Find the line with the match
    match_line_idx = -1
    for i, line in enumerate(lines):
        if pattern.search(line):
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


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Edit distance between the strings
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row: list[int] = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def fuzzy_match(query: str, text: str, max_distance: int = 3) -> bool:
    """
    Check if query fuzzy matches text.

    Args:
        query: The search query
        text: The text to match against
        max_distance: Maximum allowed edit distance

    Returns:
        True if fuzzy match found
    """
    query_lower = query.lower()
    text_lower = text.lower()

    # Check if query is substring
    if query_lower in text_lower:
        return True

    # Check fuzzy match using word boundaries
    words = re.split(r"[\s\-_/]+", text_lower)
    for word in words:
        if len(word) >= len(query_lower):
            distance = levenshtein_distance(query_lower, word)
            if distance <= max_distance:
                return True

    return False


def find_fuzzy_suggestions(
    query: str, words: Sequence[str], max_suggestions: int = 5, max_distance: int = 3
) -> list[tuple[str, int]]:
    """
    Find fuzzy matching suggestions for a query.

    Args:
        query: The search query
        words: List of words to match against
        max_suggestions: Maximum number of suggestions to return
        max_distance: Maximum allowed edit distance

    Returns:
        List of (word, distance) tuples, sorted by distance
    """
    suggestions: list[tuple[str, int]] = []
    query_lower = query.lower()

    for word in words:
        word_lower = word.lower()
        if word_lower == query_lower:
            continue

        distance = levenshtein_distance(query_lower, word_lower)
        if distance <= max_distance:
            suggestions.append((word, distance))

    # Sort by distance, then alphabetically
    suggestions.sort(key=lambda x: (x[1], x[0]))

    return suggestions[:max_suggestions]


def search_fuzzy(
    content: str,
    query: str,
    case_sensitive: bool = False,
    max_distance: int = 3,
) -> list[dict[str, str]]:
    """
    Search for a query in content using fuzzy matching.

    Args:
        content: The content to search in
        query: The search query
        case_sensitive: Whether to do case-sensitive search
        max_distance: Maximum edit distance for fuzzy matching

    Returns:
        List of matches with snippet and match text
    """
    results: list[dict[str, str]] = []

    lines = content.split("\n")

    for i, line in enumerate(lines):
        # Try exact match first
        if (case_sensitive and query in line) or (not case_sensitive and query.lower() in line.lower()):
            results.append(
                {
                    "line_number": str(i + 1),
                    "snippet": line.strip()[:200],
                    "match": query,
                }
            )
            continue

        # Try fuzzy match on words
        words = re.split(r"[\s\-_/]+", line)
        for word in words:
            if len(word) >= len(query):
                distance = levenshtein_distance(
                    query.lower() if not case_sensitive else query,
                    word.lower() if not case_sensitive else word,
                )
                if distance <= max_distance:
                    results.append(
                        {
                            "line_number": str(i + 1),
                            "snippet": line.strip()[:200],
                            "match": word,
                        }
                    )
                    break

    return results
