"""List command - list all documentation pages available on a website."""

from __future__ import annotations

import json
import urllib.parse
from typing import Any

import typer
from importlib import metadata as importlib_metadata

from ..config import resolve_alias
from ..console import echo_error, echo_warning, print_summary, reset_console, set_verbose
from ..scraper import crawler, filter as filter_module, sitemap
from ..scraper.http import validate_url
from ..ui import is_interactive, show_info_message, show_success_message, spinner

# Type alias for entries
Entry = dict[str, Any]
EntryList = list[Entry]

# Constants for --all option (effectively unlimited limits)
ALL_PAGES_MAX_PAGES = 999999
ALL_PAGES_DEPTH = 99


def list_urls(
    url: str = typer.Argument(..., help="The URL or alias of the documentation website"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Use rich output format"),
    pattern: str | None = typer.Option(None, "--pattern", "-p", help="Filter paths matching pattern"),
    depth: int = typer.Option(3, "--depth", "-d", help="Maximum crawl depth"),
    max_pages: int = typer.Option(100, "--max-pages", help="Maximum number of pages to discover"),
    sort: str = typer.Option("name", "--sort", help="Sort results by name or path"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml, xml"),
    count: bool = typer.Option(False, "--count", "-c", help="Show only total count"),
    all_pages: bool = typer.Option(False, "--all", help="Retrieve ALL pages without limits"),
) -> None:
    """List all documentation pages available on a website."""
    # Initialize console with verbose mode
    set_verbose(verbose)
    reset_console()

    # Handle --all flag
    if all_pages:
        max_pages = ALL_PAGES_MAX_PAGES
        depth = ALL_PAGES_DEPTH

    # Resolve alias to URL
    resolved_url = resolve_alias(url)

    if verbose and resolved_url != url:
        typer.echo(f"Resolved alias '{url}' to {resolved_url}")

    # Validate URL
    if not validate_url(resolved_url):
        echo_error(
            message=f"Invalid URL: {resolved_url}",
            url=resolved_url,
            code="INVALID_URL",
            suggestions=[
                "Check if the URL is correct",
                "URL must start with http:// or https://",
            ],
        )
        raise typer.Exit(1)

    # Validate sort option
    if sort not in ("name", "path"):
        echo_error(
            message=f"Invalid sort option '{sort}'. Must be 'name' or 'path'.",
            code="INVALID_SORT",
            suggestions=["Use --sort name or --sort path"],
        )
        raise typer.Exit(1)

    # Validate format option
    if format not in ("json", "yaml", "xml"):
        echo_error(
            message=f"Invalid format '{format}'. Must be 'json', 'yaml', or 'xml'.",
            code="INVALID_FORMAT",
            suggestions=["Use --format json, --format yaml, or --format xml"],
        )
        raise typer.Exit(1)

    # Discover pages using sitemap or crawler
    discovered_urls: set[str] = set()

    # Try sitemap first with spinner in interactive mode
    if verbose:
        typer.echo("Discovering sitemap...")
        sitemap_url = sitemap.discover_sitemap(resolved_url)
    elif is_interactive():
        with spinner("Discovering sitemap..."):
            sitemap_url = sitemap.discover_sitemap(resolved_url)
    else:
        sitemap_url = sitemap.discover_sitemap(resolved_url)

    if sitemap_url:
        if verbose:
            typer.echo(f"Found sitemap at {sitemap_url}")
        elif is_interactive():
            show_success_message(f"Found sitemap at {sitemap_url}")
            with spinner(f"Parsing {sitemap_url}..."):
                xml_content = sitemap.fetch_with_retry(sitemap_url)
        else:
            xml_content = sitemap.fetch_with_retry(sitemap_url)

        if xml_content and isinstance(xml_content, str):
            urls = sitemap.parse_sitemap(xml_content)
            if urls:
                # Filter relevant URLs
                filtered = [u for u in urls if filter_module.is_relevant_url(u)]
                # Apply max_pages limit
                filtered = filtered[:max_pages]
                discovered_urls.update(filtered)

    # Fallback to crawler if no sitemap found
    if not discovered_urls:
        if verbose:
            typer.echo("No sitemap found, using crawler...")
            typer.echo("Tip: Use 'fresh sync <URL>' to directly download pages without sitemap discovery.")
            discovered_urls = crawler.crawl(resolved_url, max_pages=max_pages, max_depth=depth)
        elif is_interactive():
            show_info_message("No sitemap found, using crawler...")
            typer.echo("Tip: Use 'fresh sync <URL>' to directly download pages without sitemap discovery.")
            with spinner(f"Crawling pages (max {max_pages})..."):
                discovered_urls = crawler.crawl(resolved_url, max_pages=max_pages, max_depth=depth)
        else:
            typer.echo("Tip: Use 'fresh sync <URL>' to directly download pages without sitemap discovery.")
            discovered_urls = crawler.crawl(resolved_url, max_pages=max_pages, max_depth=depth)

    # Apply pattern filter if specified
    if pattern:
        discovered_urls = set(filter_module.filter_by_pattern([*discovered_urls], pattern))  # type: ignore[arg-type]

    # Convert URLs to named entries
    entries: EntryList = []
    for page_url in discovered_urls:
        parsed = urllib.parse.urlparse(page_url)
        name = filter_module.extract_name_from_url(page_url)
        entries.append({
            "name": name,
            "path": parsed.path,
            "url": page_url,
        })

    # Sort entries
    if sort == "path":
        entries.sort(key=lambda e: e["path"])
    else:
        entries.sort(key=lambda e: e["name"])

    # Handle count-only mode
    if count:
        typer.echo(len(entries))
        return

    # Warn if no pages found
    if not entries:
        echo_warning(
            message="No documentation pages found",
            suggestions=[
                "Try with --depth 3 (current: " + str(depth) + ")",
                "The site may not have a sitemap",
                "Use --verbose to see what's happening",
            ],
        )

    # Output in requested format
    if verbose:
        # Rich output
        try:
            from rich.console import Console
            from rich.table import Table

            console = Console()
            table = Table(title="Documentation Pages")

            table.add_column("Name", style="cyan")
            table.add_column("Path", style="green")

            for entry in entries:
                table.add_row(entry["name"], entry["path"])

            console.print(table)
            console.print(f"\nFound {len(entries)} pages")
        except ImportError:
            # Fallback to JSON if rich not available
            typer.echo(json.dumps(entries, indent=2))
    else:
        # JSON output (default)
        if format == "json":
            typer.echo(json.dumps(entries, indent=2))
        elif format == "yaml":
            try:
                importlib_metadata.version("pyyaml")
            except importlib_metadata.PackageNotFoundError:
                typer.echo("Error: PyYAML not installed. Use --format json or install with: pip install fresh[yaml]", err=True)
                raise typer.Exit(1)
            import yaml  # type: ignore[import-untyped]
            typer.echo(yaml.dump(entries))
        elif format == "xml":
            import xml.etree.ElementTree as ET

            # Add XML declaration header
            root = ET.Element("pages")
            for entry in entries:
                page = ET.SubElement(root, "page")
                ET.SubElement(page, "name").text = entry["name"]
                ET.SubElement(page, "path").text = entry["path"]
                ET.SubElement(page, "url").text = entry["url"]

            ET.indent(root)
            # Build XML with declaration
            xml_string = ET.tostring(root, encoding="unicode")
            typer.echo('<?xml version="1.0" encoding="UTF-8"?>')
            typer.echo(xml_string)

    # Print error/warning summary
    print_summary()
