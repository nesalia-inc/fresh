"""Search command - search for content across documentation pages."""

from __future__ import annotations

import sys
from datetime import datetime, timezone

import json
import logging
import re

import typer
from rich.console import Console
from rich.table import Table

from pathlib import Path
import hashlib
from urllib.parse import urlparse, quote

from ..config import resolve_alias
from ..console import echo_error, print_summary, reset_console, set_verbose
from ..scraper import crawler, filter as filter_module, sitemap
from ..scraper.http import fetch_binary_aware, validate_url
from ..scraper.searcher import (
    SearchResult,
    create_snippet,
    find_fuzzy_suggestions,
    search_in_content,
)
from bs4 import BeautifulSoup

from ..ui import is_interactive, show_success_message, spinner, _is_windows

from .guide import _save_guide
from .sync import get_page_freshness

app = typer.Typer(help="Search for content across documentation pages.")

# Initialize console with Windows-safe settings
try:
    console = Console(no_color=_is_windows(), force_terminal=None)
except Exception:
    console = Console(file=sys.stdout, no_color=True, force_terminal=False)

logger = logging.getLogger(__name__)

# Default sync directory (same as get.py)
DEFAULT_SYNC_DIR = Path.home() / ".fresh" / "docs"


def _get_sync_dir_for_url(url: str) -> Path:
    """Get the sync directory for a URL's domain."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace(":", "_").replace(".", "_")
    return DEFAULT_SYNC_DIR / domain / "pages"


def _format_freshness_age(timestamp: str) -> str:
    """Format a timestamp as relative age."""
    from datetime import datetime, timezone

    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = now - dt

        if delta.total_seconds() < 60:
            return "just now"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"
        elif delta.total_seconds() < 604800:
            days = int(delta.total_seconds() / 86400)
            return f"{days}d ago"
        else:
            weeks = int(delta.total_seconds() / 604800)
            return f"{weeks}w ago"
    except (ValueError, TypeError):
        return "unknown"


def _get_result_freshness(url: str, base_url: str) -> str | None:
    """Get freshness info for a URL if available."""
    if freshness := get_page_freshness(url, base_url):
        if synced_at := freshness.get("synced_at"):
            return _format_freshness_age(synced_at)
    return None


def _url_to_local_path(url: str) -> Path | None:
    """Convert a URL to its potential local file path.

    Args:
        url: The URL to convert

    Returns:
        The potential path in the sync directory, or None if the URL cannot be mapped
    """
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")

    if not path or path.endswith("/"):
        path = path + "index.html"

    # Sanitize filename - use hash to avoid collisions from truncation
    filename = quote(path, safe="")
    if len(filename) > 200:
        # Use hash prefix to ensure uniqueness after truncation
        hash_suffix = hashlib.sha256(path.encode()).hexdigest()[:8]
        filename = filename[:191] + "_" + hash_suffix + ".html"

    sync_dir = _get_sync_dir_for_url(url)
    file_path = sync_dir / filename

    return file_path


def get_local_content(url: str) -> str | None:
    """Get locally synced content for a URL.

    Args:
        url: The URL to get local content for

    Returns:
        Local HTML content or None if not available locally
    """
    local_path = _url_to_local_path(url)
    if local_path and local_path.exists():
        try:
            return local_path.read_text(encoding="utf-8")
        except (OSError, IOError):
            return None
    return None


def local_content_exists(url: str) -> bool:
    """Check if local synced content exists for a URL.

    Args:
        url: The URL to check

    Returns:
        True if local content exists, False otherwise
    """
    local_path = _url_to_local_path(url)
    return local_path is not None and local_path.exists()


def discover_local_urls(base_url: str, max_pages: int = 50) -> list[str]:
    """Discover documentation URLs from local synced content.

    Args:
        base_url: The base URL of the documentation
        max_pages: Maximum number of pages to return

    Returns:
        List of discovered local URLs
    """
    sync_dir = _get_sync_dir_for_url(base_url)

    if not sync_dir.exists():
        return []

    urls: list[str] = []
    try:
        for file_path in sync_dir.rglob("*.html"):
            # Convert local path back to URL
            relative_path = file_path.relative_to(sync_dir)
            path_str = str(relative_path)

            # Handle index.html files - convert to directory path
            if file_path.stem == "index" and path_str != "index.html":
                # Remove index.html from path
                path_str = path_str[:-11]  # Remove "index.html"
                if path_str:
                    path_str = "/" + path_str
                else:
                    path_str = "/"
            else:
                path_str = "/" + path_str

            full_url = f"{base_url.rstrip('/')}{path_str}"
            urls.append(full_url)

            if len(urls) >= max_pages:
                break
    except OSError:
        pass

    return urls[:max_pages]


def _search_page_content(
    page_url: str,
    query: str,
    case_sensitive: bool,
    regex: bool,
    context_lines: int,
) -> tuple[str, str] | None:
    """Search a single page's content for a query.

    Args:
        page_url: URL of the page
        query: Search query
        case_sensitive: Whether to do case-sensitive search
        regex: Whether to treat query as regex
        context_lines: Number of context lines around matches

    Returns:
        Tuple of (title, snippet) if matches found, None otherwise
    """
    # Fetch the page
    response = fetch_binary_aware(page_url, max_retries=2)
    if not response:
        return None

    # Convert to text content
    if hasattr(response, "text"):
        html_content = response.text
    else:
        html_content = str(response)

    # Parse and extract text
    soup = BeautifulSoup(html_content, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    text_content = soup.get_text(separator="\n")

    # Search in the content
    matches = search_in_content(
        text_content,
        query,
        case_sensitive=case_sensitive,
        regex=regex,
    )

    if not matches:
        return None

    # Extract title and create snippet
    title = filter_module.extract_name_from_url(page_url)
    snippet = create_snippet(
        text_content, query, context_lines=context_lines, case_sensitive=case_sensitive, regex=regex
    )

    return title, snippet


def discover_documentation_urls(
    base_url: str,
    max_pages: int = 50,
    verbose: bool = False,
) -> list[str]:
    """
    Discover documentation URLs using sitemap or crawler.

    Args:
        base_url: The base URL of the documentation
        max_pages: Maximum number of pages to discover
        verbose: Whether to show verbose output

    Returns:
        List of discovered URLs
    """
    discovered_urls: set[str] = set()

    # Try sitemap first
    sitemap_url = sitemap.discover_sitemap(base_url)
    if sitemap_url:
        if verbose:
            typer.echo(f"Found sitemap at {sitemap_url}")
        xml_content = sitemap.fetch_with_retry(sitemap_url)
        if xml_content and isinstance(xml_content, str):
            urls = sitemap.parse_sitemap(xml_content)
            if urls:
                filtered = [u for u in urls if filter_module.is_relevant_url(u)]
                discovered_urls.update(filtered)

    # Fallback to crawler if no sitemap or no URLs found
    if not discovered_urls:
        if verbose:
            typer.echo("No sitemap found, using crawler...")
        discovered_urls = crawler.crawl(base_url, max_pages=max_pages, max_depth=3)

    return list(discovered_urls)[:max_pages]


def extract_words_for_suggestions(
    base_url: str,
    max_pages: int = 20,
    verbose: bool = False,
) -> list[str]:
    """
    Extract words from documentation pages for suggestion engine.

    Args:
        base_url: The base URL of the documentation
        max_pages: Number of pages to scan
        verbose: Whether to show verbose output

    Returns:
        List of words found in documentation
    """
    words: set[str] = set()

    # Use shared URL discovery helper
    urls_to_check = discover_documentation_urls(base_url, max_pages, verbose)

    # Extract words from pages
    for page_url in urls_to_check[:max_pages]:
        if verbose:
            typer.echo(f"  Extracting words from {page_url}")

        response = fetch_binary_aware(page_url, max_retries=1)
        if not response:
            continue

        if hasattr(response, "text"):
            html_content = response.text
        else:
            html_content = str(response)

        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()

        # Extract words (alphanumeric, 3+ chars)
        found_words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        words.update(found_words)

    # Filter out common words
    common_words = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
        "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
        "how", "its", "may", "now", "old", "see", "than", "that", "this", "with",
        "have", "from", "they", "will", "would", "there", "their", "what", "been",
        "when", "where", "which", "who", "whom", "these", "those", "being",
        "also", "into", "more", "some", "such", "only", "over", "other", "after",
        "first", "even", "back", "just", "about", "could", "because", "while",
        "before", "between", "through", "during", "under", "again", "very",
    }
    return sorted(words - common_words)


def show_suggestions(query: str, base_url: str, verbose: bool = False) -> None:
    """
    Show "Did you mean" suggestions when no results found.

    Args:
        query: The search query
        base_url: The base URL that was searched
        verbose: Whether to show verbose output
    """
    try:
        words = extract_words_for_suggestions(base_url, max_pages=20, verbose=verbose)
        if not words:
            return

        suggestions = find_fuzzy_suggestions(query, words, max_suggestions=5, max_distance=3)

        if suggestions:
            typer.echo("\nDid you mean?")
            for suggestion, distance in suggestions:
                typer.echo(f"  - {suggestion}")

            typer.echo(f"\nSearch with: fresh search \"{suggestions[0][0]}\" {base_url}")
    except Exception as e:
        # Log but don't fail if suggestions fail
        logger.debug(f"Could not generate suggestions: {e}")


def search_pages(
    base_url: str,
    query: str,
    max_pages: int = 50,
    depth: int = 3,
    case_sensitive: bool = False,
    regex: bool = False,
    context_lines: int = 1,
    verbose: bool = False,
    result_limit: int | None = None,
    source: str = "auto",  # "auto", "local", "remote"
) -> list[SearchResult]:
    """
    Search for a query across documentation pages.

    Args:
        base_url: The base URL of the documentation
        query: The search query
        max_pages: Maximum number of pages to search
        depth: Maximum crawl depth
        case_sensitive: Whether to do case-sensitive search
        regex: Whether to treat query as regex
        context_lines: Number of lines of context around matches
        verbose: Whether to show verbose output
        result_limit: Early termination when this many results found
        source: Data source - "auto" (local-first), "local", or "remote"

    Returns:
        List of SearchResult objects
    """
    results: list[SearchResult] = []

    # Determine search strategy
    use_local = source in ("local", "auto")
    use_remote = source in ("remote", "auto")

    # Try local first if auto or local
    local_results: list[SearchResult] = []
    remote_results: list[SearchResult] = []

    if use_local:
        if verbose:
            typer.echo("Checking for local content...")

        local_urls = discover_local_urls(base_url, max_pages)

        if local_urls:
            if verbose:
                typer.echo(f"Found {len(local_urls)} local pages, searching...")

            for page_url in local_urls:
                # Get content from local
                html_content = get_local_content(page_url)
                if not html_content:
                    continue

                # Parse and search
                soup = BeautifulSoup(html_content, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                text_content = soup.get_text(separator="\n")

                search_query = query
                matches = search_in_content(
                    text_content,
                    search_query,
                    case_sensitive=case_sensitive,
                    regex=regex,
                )

                if matches:
                    title = filter_module.extract_name_from_url(page_url)
                    snippet = create_snippet(
                        text_content, search_query, context_lines=context_lines, case_sensitive=case_sensitive, regex=regex
                    )

                    local_results.append(
                        SearchResult(
                            path=page_url.replace(base_url, ""),
                            title=title,
                            snippet=snippet,
                            url=page_url,
                            source="local",
                        )
                    )

                    if result_limit and len(local_results) >= result_limit:
                        return local_results[:result_limit]
        elif verbose and source == "local":
            typer.echo("No local content found")

    # Search remote if needed (auto mode with no local results, or remote-only mode)
    if use_remote and (source == "remote" or (source == "auto" and not local_results)):
        if source == "auto" and verbose:
            typer.echo("No local results, falling back to remote...")

        if verbose:
            typer.echo("Discovering pages...")

        pages_to_search = discover_documentation_urls(base_url, max_pages, verbose)

        if verbose:
            typer.echo(f"Searching {len(pages_to_search)} pages...")

        for i, page_url in enumerate(pages_to_search):
            if verbose:
                typer.echo(f"  [{i + 1}/{len(pages_to_search)}] Searching {page_url}")

            # Use helper function to search page content
            result = _search_page_content(
                page_url, query, case_sensitive, regex, context_lines
            )

            if result:
                title, snippet = result
                remote_results.append(
                    SearchResult(
                        path=page_url.replace(base_url, ""),
                        title=title,
                        snippet=snippet,
                        url=page_url,
                        source="remote",
                    )
                )

                if result_limit and len(remote_results) >= result_limit:
                    break

    # Combine results: local first, then remote
    results = local_results + remote_results
    return results


def search_multiple_libraries(
    query: str,
    base_urls: list[str],
    max_pages: int = 50,
    depth: int = 3,
    case_sensitive: bool = False,
    regex: bool = False,
    context_lines: int = 1,
    verbose: bool = False,
    result_limit: int | None = None,
) -> dict[str, list[SearchResult]]:
    """
    Search for a query across multiple documentation libraries.

    Args:
        query: The search query
        base_urls: List of base URLs to search
        max_pages: Maximum number of pages to search per library
        depth: Maximum crawl depth
        case_sensitive: Whether to do case-sensitive search
        regex: Whether to treat query as regex
        context_lines: Number of lines of context around matches
        verbose: Whether to show verbose output
        result_limit: Early termination when this many results found

    Returns:
        Dictionary mapping library URLs to their search results
    """
    results_by_library: dict[str, list[SearchResult]] = {}

    for base_url in base_urls:
        if verbose:
            typer.echo(f"\nSearching {base_url}...")

        results = search_pages(
            base_url=base_url,
            query=query,
            max_pages=max_pages,
            depth=depth,
            case_sensitive=case_sensitive,
            regex=regex,
            context_lines=context_lines,
            verbose=verbose,
            result_limit=result_limit,
        )

        results_by_library[base_url] = results

    return results_by_library


@app.command()
def search(
    query: str = typer.Argument(..., help="The search query"),
    url: list[str] = typer.Argument(None, help="The URL or alias of the documentation website(s)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output (table format)"),
    max_pages: int = typer.Option(50, "--max-pages", help="Maximum number of pages to search"),
    depth: int = typer.Option(3, "--depth", "-d", help="Maximum crawl depth"),
    context: int = typer.Option(1, "--context", "-c", help="Number of context lines around matches"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", help="Enable case-sensitive search"),
    regex: bool = typer.Option(False, "--regex", "-r", help="Treat query as regular expression"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of results to show"),
    local: bool = typer.Option(False, "--local", help="Search only in locally synced documentation"),
    remote: bool = typer.Option(False, "--remote", help="Search only in remote documentation (skip local)"),
    fresh: bool = typer.Option(False, "--fresh", help="Force fresh search (skip cache)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output results as JSON"),
    table_output: bool = typer.Option(False, "--table", "-t", help="Output results as table (verbose)"),
    save_guide: str | None = typer.Option(None, "--save-guide", help="Save search results as a guide"),
    freshness: bool = typer.Option(False, "--freshness", "-f", help="Show freshness information for local results"),
) -> None:
    """Search for content across documentation pages."""
    # Handle no URL provided - show help
    if not url:
        echo_error(
            message="No URL provided",
            code="NO_URL",
            suggestions=["Provide at least one URL to search"],
        )
        raise typer.Exit(1)

    # Initialize console with verbose mode
    set_verbose(verbose)
    reset_console()

    # Resolve and validate all URLs
    resolved_urls: list[str] = []
    for u in url:
        resolved = resolve_alias(u)
        if not validate_url(resolved):
            echo_error(
                message=f"Invalid URL: {resolved}",
                url=resolved,
                code="INVALID_URL",
                suggestions=[
                    "Check if the URL is correct",
                    "URL must start with http:// or https://",
                ],
            )
            raise typer.Exit(1)
        resolved_urls.append(resolved)

    # Determine source mode from options
    if fresh:
        # Fresh means force remote (skip local)
        source = "remote"
    elif local:
        source = "local"
    elif remote:
        source = "remote"
    else:
        source = "auto"  # Local-first

    # Single URL or multiple URLs
    if len(resolved_urls) == 1:
        # Single library search
        _search_single_library(
            query=query,
            resolved_url=resolved_urls[0],
            verbose=verbose,
            max_pages=max_pages,
            depth=depth,
            case_sensitive=case_sensitive,
            regex=regex,
            context=context,
            limit=limit,
            source=source,
            json_output=json_output,
            table_output=table_output,
            save_guide=save_guide,
            freshness=freshness,
        )
    else:
        # Multiple library search
        _search_multiple_libraries(
            query=query,
            resolved_urls=resolved_urls,
            verbose=verbose,
            max_pages=max_pages,
            depth=depth,
            case_sensitive=case_sensitive,
            regex=regex,
            context=context,
            limit=limit,
            source=source,
            json_output=json_output,
            table_output=table_output,
            save_guide=save_guide,
            freshness=freshness,
        )


def _search_single_library(
    query: str,
    resolved_url: str,
    verbose: bool,
    max_pages: int,
    depth: int,
    case_sensitive: bool,
    regex: bool,
    context: int,
    limit: int,
    source: str = "auto",
    json_output: bool = False,
    table_output: bool = False,
    save_guide: str | None = None,
    freshness: bool = False,
) -> None:
    """Search a single library."""
    if verbose:
        typer.echo(f"Searching \"{query}\" on {resolved_url}...")

    # Perform search
    def do_search() -> list[SearchResult]:
        return search_pages(
            resolved_url,
            query,
            max_pages=max_pages,
            depth=depth,
            case_sensitive=case_sensitive,
            regex=regex,
            context_lines=context,
            verbose=verbose,
            result_limit=limit,
            source=source,
        )

    try:
        if verbose:
            results = do_search()
        elif is_interactive():
            with spinner(f"Searching for \"{query}\"..."):
                results = do_search()
        else:
            results = do_search()
    except Exception as e:  # noqa: BLE001
        echo_error(
            message=f"Search error: {e}",
            code="SEARCH_ERROR",
            suggestions=["Check if the URL is accessible", "Try with --verbose for more details"],
        )
        raise typer.Exit(1)

    # Limit results
    results = results[:limit]

    # Display results
    if not results:
        typer.echo("No results found.")
        show_suggestions(query, resolved_url, verbose)
        return

    # Default to JSON output, use table only with --table or --verbose
    show_table = table_output or verbose
    show_json = json_output or not show_table

    if show_table:
        show_success_message(f"Found {len(results)} results")

        # Create rich table
        table = Table(title="Search Results")
        table.add_column("Page", style="cyan")
        table.add_column("URL", style="dim")
        table.add_column("Snippet", style="green")
        if freshness:
            table.add_column("Freshness", style="yellow")

        for result in results:
            # Truncate snippet for table
            snippet_preview = result.snippet[:80].replace("\n", " ")
            if len(result.snippet) > 80:
                snippet_preview += "..."
            # Truncate URL for display
            url_display = result.url
            if len(url_display) > 50:
                url_display = "..." + url_display[-47:]

            # Add freshness if requested and result is local
            freshness_str = ""
            if freshness and result.source == "local":
                freshness_str = _get_result_freshness(result.url, resolved_url) or ""

            table.add_row(result.title, url_display, snippet_preview, freshness_str)

        console.print(table)

    if show_json:
        # JSON output for scripting
        output = []
        for r in results:
            result_dict = {
                "path": r.path,
                "title": r.title,
                "snippet": r.snippet,
                "url": r.url,
                "source": r.source,
            }
            # Add freshness if requested and result is local
            if freshness and r.source == "local":
                _freshness = _get_result_freshness(r.url, resolved_url)
                if _freshness:
                    result_dict["freshness"] = _freshness
            output.append(result_dict)
        typer.echo(json.dumps(output, indent=2))

    # Save as guide if requested
    if save_guide and results:
        guide_content = f"# Search: {query}\n\n"
        guide_content += f"Query: {query}\n"
        guide_content += f"URL: {resolved_url}\n"
        guide_content += f"Results: {len(results)}\n\n"
        guide_content += "## Results\n\n"
        for r in results:
            guide_content += f"### {r.title}\n"
            guide_content += f"URL: {r.url}\n"
            guide_content += f"```\n{r.snippet}\n```\n\n"

        guide_data = {
            "title": f"Search: {query}",
            "content": guide_content,
            "source_url": resolved_url,
            "tags": ["search", query.lower()],
        }

        now = datetime.now(timezone.utc).isoformat()
        guide_data["created"] = now
        guide_data["updated"] = now

        _save_guide(save_guide, guide_data)
        typer.echo(f"Saved results as guide '{save_guide}'")

    # Print error/warning summary
    print_summary()


def _search_multiple_libraries(
    query: str,
    resolved_urls: list[str],
    verbose: bool,
    max_pages: int,
    depth: int,
    case_sensitive: bool,
    regex: bool,
    context: int,
    limit: int,
    source: str = "auto",
    json_output: bool = False,
    table_output: bool = False,
    save_guide: str | None = None,
    freshness: bool = False,
) -> None:
    """Search across multiple libraries."""
    if verbose:
        typer.echo(f"Searching \"{query}\" on {len(resolved_urls)} libraries...")

    # Perform multi-library search
    try:
        results_by_library: dict[str, list[SearchResult]] = {}
        total_results = 0

        for lib_url in resolved_urls:
            if verbose:
                typer.echo(f"\nSearching {lib_url}...")

            results = search_pages(
                lib_url,
                query,
                max_pages=max_pages,
                depth=depth,
                case_sensitive=case_sensitive,
                regex=regex,
                context_lines=context,
                verbose=verbose,
                result_limit=limit,
                source=source,
            )
            results_by_library[lib_url] = results[:limit]
            total_results += len(results_by_library[lib_url])

    except Exception as e:  # noqa: BLE001
        echo_error(
            message=f"Search error: {e}",
            code="SEARCH_ERROR",
            suggestions=["Check if the URLs are accessible", "Try with --verbose for more details"],
        )
        raise typer.Exit(1)

    # Display results
    if total_results == 0:
        typer.echo("No results found.")
        # Show suggestions for the first library
        if resolved_urls:
            show_suggestions(query, resolved_urls[0], verbose)
        return

    # Default to JSON output, use table only with --table or --verbose
    show_table = table_output or verbose
    show_json = json_output or not show_table

    if show_table:
        show_success_message(f"Found {total_results} results across {len(resolved_urls)} libraries")

        # Create rich table grouped by library
        for lib_url, results in results_by_library.items():
            if not results:
                continue

            lib_name = lib_url.replace("https://", "").replace("http://", "").split("/")[0]
            table = Table(title=f"Search Results - {lib_name}")
            table.add_column("Page", style="cyan")
            table.add_column("URL", style="dim")
            table.add_column("Snippet", style="green")

            for result in results:
                snippet_preview = result.snippet[:60].replace("\n", " ")
                if len(result.snippet) > 60:
                    snippet_preview += "..."
                # Truncate URL for display
                url_display = result.url
                if len(url_display) > 40:
                    url_display = "..." + url_display[-37:]
                table.add_row(result.title, url_display, snippet_preview)

            console.print(table)

    if show_json:
        # JSON output for scripting
        output = []
        for lib_url, results in results_by_library.items():
            lib_name = lib_url.replace("https://", "").replace("http://", "").split("/")[0]
            for result in results:
                output.append({
                    "library": lib_name,
                    "path": result.path,
                    "title": result.title,
                    "snippet": result.snippet,
                    "url": result.url,
                    "source": result.source,
                })
        typer.echo(json.dumps(output, indent=2))

    # Print error/warning summary
    print_summary()
