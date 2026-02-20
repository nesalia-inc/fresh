"""URL filtering and normalization utilities."""

from __future__ import annotations

import re
import urllib.parse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# Default patterns for documentation URLs
DEFAULT_DOC_PATTERNS = [
    r"/docs?/",
    r"/guide[s]?/",
    r"/api/",
    r"/reference/",
    r"/tutorial[s]?/",
    r"/learn/",
    r"/v\d+/",  # Version-specific paths like /v14/, /v3/
]

# Patterns to exclude (non-documentation pages)
EXCLUDE_PATTERNS = [
    r"/blog/",
    r"/news/",
    r"/changelog/",
    r"/community/",
    r"/about/",
    r"/contact/",
    r"/pricing/",
    r"/legal/",
    r"/terms/",
    r"/privacy/",
    r"/404",
    r"/500",
]


def is_relevant_url(
    url: str,
    patterns: Sequence[str] | None = None,
) -> bool:
    """
    Determine if a URL is documentation-related.

    Args:
        url: The URL to check
        patterns: Custom patterns to match (optional)

    Returns:
        True if the URL appears to be documentation
    """
    url_lower = url.lower()

    # Check exclude patterns first
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, url_lower):
            return False

    # Check include patterns
    check_patterns = patterns if patterns is not None else DEFAULT_DOC_PATTERNS
    for pattern in check_patterns:
        if re.search(pattern, url_lower):
            return True

    # If no custom patterns, use default behavior
    if patterns is None:
        # Default: include URLs with common doc path segments
        doc_segments = ["docs", "api", "guide", "reference", "tutorial", "learn"]
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lower()
        return any(segment in path for segment in doc_segments)

    return False


def extract_name_from_url(url: str) -> str:
    """
    Extract a human-readable name from a URL.

    Args:
        url: The URL to parse

    Returns:
        A human-readable name
    """
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.rstrip("/")

    # Get the last segment
    segments = path.split("/")
    last_segment = segments[-1] if segments else ""

    # Handle index files
    if last_segment in ("index", "index.html", "index.htm"):
        last_segment = segments[-2] if len(segments) > 1 else ""

    # Convert slug to title case
    name = last_segment.replace("-", " ").replace("_", " ")
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    name = name.title()

    # Clean up common patterns
    name = re.sub(r"\bV\d+\b", "", name)  # Remove version numbers
    name = re.sub(r"\s+", " ", name)  # Normalize whitespace
    name = name.strip()

    return name if name else url


def deduplicate(urls: Sequence[str]) -> list[str]:
    """
    Remove duplicate URLs while preserving order.

    Args:
        urls: List of URLs (may contain duplicates)

    Returns:
        List of unique URLs in original order
    """
    seen: set[str] = set()
    result = []

    for url in urls:
        normalized = url.rstrip("/").lower()
        if normalized not in seen:
            seen.add(normalized)
            result.append(url)

    return result


def filter_by_pattern(urls: Sequence[str], pattern: str) -> list[str]:
    """
    Filter URLs by a glob-style pattern.

    Args:
        urls: List of URLs to filter
        pattern: Glob pattern (e.g., "/docs/*", "/api/**")

    Returns:
        URLs matching the pattern
    """
    # Convert glob to regex
    regex_pattern = pattern.replace(".", r"\.")
    regex_pattern = regex_pattern.replace("**", ".*")
    regex_pattern = regex_pattern.replace("*", "[^/]*")
    regex_pattern = regex_pattern.replace("?", ".")

    compiled = re.compile(regex_pattern, re.IGNORECASE)

    return [url for url in urls if compiled.search(url)]
