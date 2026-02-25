"""URL filtering and normalization utilities."""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

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

# Pre-compiled patterns for performance
_EXCLUDE_PATTERNS_COMPILED = [re.compile(p, re.IGNORECASE) for p in EXCLUDE_PATTERNS]
_DEFAULT_DOC_PATTERNS_COMPILED = [re.compile(p, re.IGNORECASE) for p in DEFAULT_DOC_PATTERNS]


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

    # Check exclude patterns first (using pre-compiled patterns)
    for pattern in _EXCLUDE_PATTERNS_COMPILED:
        if pattern.search(url_lower):
            return False

    # Check include patterns (using pre-compiled patterns)
    check_patterns = patterns if patterns is not None else DEFAULT_DOC_PATTERNS
    if patterns is not None:
        # Compile custom patterns
        check_compiled = [re.compile(p, re.IGNORECASE) for p in check_patterns]
    else:
        check_compiled = _DEFAULT_DOC_PATTERNS_COMPILED

    for pattern in check_compiled:
        if pattern.search(url_lower):
            return True

    # If no custom patterns, use default behavior
    if patterns is None:
        # Default: include URLs with common doc path segments
        doc_segments = ["docs", "api", "guide", "reference", "tutorial", "learn"]
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or ""
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
    path = (parsed.path or "").rstrip("/")

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


def deduplicate(
    urls: Sequence[str],
    strip_query: bool = True,
    strip_fragment: bool = True,
) -> list[str]:
    """
    Remove duplicate URLs while preserving order.

    Args:
        urls: List of URLs (may contain duplicates)
        strip_query: If True, ignore query strings when comparing
        strip_fragment: If True, ignore fragment identifiers when comparing

    Returns:
        List of unique URLs in original order
    """
    seen: set[str] = set()
    result = []

    for url in urls:
        # Normalize: remove trailing slash and lowercase
        normalized = url.rstrip("/").lower()

        # Remove fragment for comparison
        if strip_fragment:
            normalized = normalized.split("#")[0]

        # Remove query string for comparison
        if strip_query:
            normalized = normalized.split("?")[0]

        if normalized not in seen:
            seen.add(normalized)
            result.append(url)

    return result


def detect_url_pattern(url: str) -> str | None:
    """
    Detect if a URL contains a pattern (glob, regex, brace expansion).

    Args:
        url: The URL to check

    Returns:
        Pattern type: "glob", "glob_recursive", "regex", "brace", or None
    """
    # Check for regex pattern (pattern starts with re: after protocol/domain)
    # Pattern format: https://example.com/re:/path or just re:/path
    if "re:/" in url or url.startswith("re:"):
        return "regex"

    # Check for brace expansion {a,b,c}
    if "{" in url and "}" in url:
        return "brace"

    # Check for recursive glob **
    if "**" in url:
        return "glob_recursive"

    # Check for simple glob *
    if "*" in url:
        return "glob"

    return None


def expand_brace_pattern(pattern: str) -> list[str]:
    """
    Expand brace patterns like {page1,page2,page3}.

    Args:
        pattern: Pattern with brace expansion

    Returns:
        List of expanded patterns
    """
    import re

    brace_pattern = re.compile(r"\{([^}]+)\}")
    matches = brace_pattern.findall(pattern)

    if not matches:
        return [pattern]

    expansions = []
    for match in matches:
        options = [opt.strip() for opt in match.split(",")]
        for option in options:
            expanded = pattern.replace("{" + match + "}", option, 1)
            expansions.extend(expand_brace_pattern(expanded))

    return expansions


def filter_by_pattern(urls: Sequence[str], pattern: str) -> list[str]:
    """
    Filter URLs by a pattern (glob, regex, brace expansion).

    Args:
        urls: List of URLs to filter
        pattern: Pattern to match (glob, regex with re: prefix, or brace expansion)

    Returns:
        URLs matching the pattern
    """
    # Handle regex pattern (prefixed with re:)
    if pattern.startswith("re:"):
        regex_str = pattern[3:]  # Remove re: prefix
        try:
            compiled = re.compile(regex_str, re.IGNORECASE)
        except re.error as e:
            logger.warning(f"Invalid regex pattern: {e}")
            return []
        return [url for url in urls if compiled.search(url)]

    # Handle brace expansion {a,b,c}
    if "{" in pattern and "}" in pattern:
        expanded_patterns = expand_brace_pattern(pattern)
        results = []
        for exp_pattern in expanded_patterns:
            results.extend(filter_by_pattern(urls, exp_pattern))
        return list(set(results))  # Remove duplicates

    # Convert glob to regex
    # Limit pattern length to prevent catastrophic backtracking
    if len(pattern) > 200:
        logger.warning(f"Pattern too long, skipping: {pattern[:50]}...")
        return []

    regex_pattern = pattern.replace(".", r"\.")
    regex_pattern = regex_pattern.replace("**", ".*")
    regex_pattern = regex_pattern.replace("*", "[^/]*")
    regex_pattern = regex_pattern.replace("?", ".")

    try:
        compiled = re.compile(regex_pattern, re.IGNORECASE)
    except re.error as e:
        logger.warning(f"Invalid regex pattern: {e}")
        return []

    return [url for url in urls if compiled.search(url)]
