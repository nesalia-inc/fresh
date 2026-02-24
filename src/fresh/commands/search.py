"""Search command - search for content across documentation pages."""

from __future__ import annotations

import json
import re

import typer
from rich.console import Console
from rich.table import Table

from ..config import resolve_alias
from ..scraper import crawler, filter as filter_module, sitemap
from ..scraper.http import fetch_with_retry, validate_url
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
        response = fetch_with_retry(page_url, max_retries=2)
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


@app.command()
def search(
    query: str = typer.Argument(..., help="The search query"),
    url: str = typer.Argument(..., help="The URL or alias of the documentation website"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Use verbose output"),
    max_pages: int = typer.Option(50, "--max-pages", help="Maximum number of pages to search"),
    depth: int = typer.Option(3, "--depth", "-d", help="Maximum crawl depth"),
    context: int = typer.Option(1, "--context", "-c", help="Number of context lines around matches"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", help="Enable case-sensitive search"),
    regex: bool = typer.Option(False, "--regex", "-r", help="Treat query as regular expression"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of results to show"),
) -> None:
    """Search for content across documentation pages."""
    # Resolve alias to URL
    resolved_url = resolve_alias(url)

    if verbose:
        typer.echo(f"Searching \"{query}\" on {resolved_url}...")

    # Validate URL
    if not validate_url(resolved_url):
        typer.echo(f"Error: Invalid URL: {resolved_url}", err=True)
        raise typer.Exit(1)

    # Perform search with appropriate UI
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
        typer.echo(f"Error: Search error: {e}", err=True)
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
