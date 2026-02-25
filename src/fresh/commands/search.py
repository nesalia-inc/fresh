"""Search command - search for content across documentation pages."""

from __future__ import annotations

import json
import re

import typer
from rich.console import Console
from rich.table import Table

from ..config import resolve_alias
from ..console import echo_error, print_summary, reset_console, set_verbose
from ..scraper import crawler, filter as filter_module, sitemap
from ..scraper.http import fetch_binary_aware, validate_url
from ..scraper.searcher import (
    SearchResult,
    create_snippet,
    search_in_content,
)
from bs4 import BeautifulSoup

from ..ui import is_interactive, show_success_message, spinner

app = typer.Typer(help="Search for content across documentation pages.")
console = Console()


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

    Returns:
        List of SearchResult objects
    """
    results: list[SearchResult] = []

    # Discover pages using sitemap or crawler
    discovered_urls: set[str] = set()

    if verbose:
        typer.echo("Discovering pages...")

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

    # Fallback to crawler if no sitemap
    if not discovered_urls:
        if verbose:
            typer.echo("No sitemap found, using crawler...")
        discovered_urls = crawler.crawl(base_url, max_pages=max_pages, max_depth=depth)

    # Limit pages to search
    pages_to_search = list(discovered_urls)[:max_pages]

    if verbose:
        typer.echo(f"Searching {len(pages_to_search)} pages...")

    # Search in each page
    for i, page_url in enumerate(pages_to_search):
        if verbose:
            typer.echo(f"  [{i + 1}/{len(pages_to_search)}] Searching {page_url}")

        # Fetch the page
        response = fetch_binary_aware(page_url, max_retries=2)
        if not response:
            continue

        # Convert to markdown (simple extraction)
        if hasattr(response, "text"):
            html_content = response.text
        else:
            html_content = str(response)

        # Use BeautifulSoup for robust HTML parsing
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text_content = soup.get_text(separator="\n")

        # Search in the content
        # Use escaped query for create_snippet to match search_in_content behavior
        search_query = query if regex else re.escape(query)
        matches = search_in_content(
            text_content,
            search_query,
            case_sensitive=case_sensitive,
            regex=regex,
        )

        if matches:
            # Extract title from page URL
            title = filter_module.extract_name_from_url(page_url)

            # Create snippet - use same query logic as search_in_content
            snippet = create_snippet(
                text_content, search_query, context_lines=context_lines, case_sensitive=case_sensitive, regex=regex
            )

            results.append(
                SearchResult(
                    path=page_url.replace(base_url, ""),
                    title=title,
                    snippet=snippet,
                    url=page_url,
                )
            )

            # Early termination when result_limit is reached
            if result_limit and len(results) >= result_limit:
                break

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
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Use verbose output"),
    max_pages: int = typer.Option(50, "--max-pages", help="Maximum number of pages to search"),
    depth: int = typer.Option(3, "--depth", "-d", help="Maximum crawl depth"),
    context: int = typer.Option(1, "--context", "-c", help="Number of context lines around matches"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", help="Enable case-sensitive search"),
    regex: bool = typer.Option(False, "--regex", "-r", help="Treat query as regular expression"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of results to show"),
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
        return

    if verbose or is_interactive():
        show_success_message(f"Found {len(results)} results")

        # Create rich table
        table = Table(title="Search Results")
        table.add_column("Page", style="cyan")
        table.add_column("Snippet", style="green")

        for result in results:
            # Truncate snippet for table
            snippet_preview = result.snippet[:100].replace("\n", " ")
            if len(result.snippet) > 100:
                snippet_preview += "..."
            table.add_row(result.title, snippet_preview)

        console.print(table)
    else:
        # JSON output for scripting
        output = [
            {
                "path": r.path,
                "title": r.title,
                "snippet": r.snippet,
                "url": r.url,
            }
            for r in results
        ]
        typer.echo(json.dumps(output, indent=2))

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
        return

    if verbose or is_interactive():
        show_success_message(f"Found {total_results} results across {len(resolved_urls)} libraries")

        # Create rich table grouped by library
        for lib_url, results in results_by_library.items():
            if not results:
                continue

            lib_name = lib_url.replace("https://", "").replace("http://", "").split("/")[0]
            table = Table(title=f"Search Results - {lib_name}")
            table.add_column("Page", style="cyan")
            table.add_column("Snippet", style="green")

            for result in results:
                snippet_preview = result.snippet[:80].replace("\n", " ")
                if len(result.snippet) > 80:
                    snippet_preview += "..."
                table.add_row(result.title, snippet_preview)

            console.print(table)
    else:
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
                })
        typer.echo(json.dumps(output, indent=2))

    # Print error/warning summary
    print_summary()
