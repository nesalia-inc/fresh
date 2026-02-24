"""Doc command - show enhanced documentation for fresh commands."""

from __future__ import annotations

import typer

app = typer.Typer(help="Show enhanced documentation for fresh commands.")


@app.command(name="doc")
def doc(
    command: str | None = typer.Argument(
        None, help="Command to show documentation for (e.g., list, get)"
    ),
) -> None:
    """Show enhanced documentation for fresh commands."""
    if command:
        _show_command_doc(command)
    else:
        _show_overview()


def _show_overview() -> None:
    """Show overview of all commands."""
    typer.echo("""
# Fresh - Documentation Fetcher

Fresh is a CLI tool to get the latest and freshest documentation from any website in Markdown format.

## Commands

### fresh list
List all documentation pages available on a website.

### fresh get
Fetch a documentation page and convert it to Markdown.

### fresh search
Search for content across documentation pages.

### fresh alias
Manage library aliases for quick access.

### fresh update
Check for and install updates to fresh.

### fresh doc
Show this documentation or detailed help for a specific command.

## Examples

# List all pages on Python docs
fresh list https://docs.python.org/3/

# Download a page to a file
fresh get https://docs.python.org/3/tutorial/ -o tutorial.md

# Search for something
fresh search "virtual environment" https://docs.python.org/3/

# Add an alias
fresh alias add python https://docs.python.org/3/

# Check for updates
fresh update --check

# Show help for a specific command
fresh doc get
""")


def _show_command_doc(command: str) -> None:
    """Show documentation for a specific command."""
    command = command.lower()

    docs = {
        "list": """
# fresh list

List all documentation pages available on a website.

## Usage

    fresh list <URL> [OPTIONS]

## Arguments

    URL    The URL or alias of the documentation website (required)

## Options

    -v, --verbose         Use rich output format
    -p, --pattern TEXT    Filter paths matching pattern
    -d, --depth INTEGER   Maximum crawl depth (default: 3)
    --max-pages INTEGER   Maximum number of pages to discover (default: 100)
    --sort TEXT           Sort results by name or path (default: name)
    -f, --format TEXT     Output format: json, yaml, xml (default: json)
    -c, --count           Show only total count
    --all                 Retrieve ALL pages without limits

## Examples

# List all pages
fresh list https://docs.python.org/3/

# List with pattern filter
fresh list https://docs.python.org/3/ --pattern "*/faq/*"

# Get count only
fresh list https://docs.python.org/3/ --count

# List all pages (no limit)
fresh list https://docs.python.org/3/ --all
""",
        "get": """
# fresh get

Fetch a documentation page and convert it to Markdown.

## Usage

    fresh get <URL> [OPTIONS]

## Arguments

    URL    The URL or alias of the documentation page to fetch (required)

## Options

    -v, --verbose           Use verbose output
    -t, --timeout INTEGER   Request timeout in seconds (default: 30)
    --header TEXT           Custom HTTP header (format: 'Key: Value')
    --no-follow             Do not follow redirects
    --skip-scripts         Exclude JavaScript from output
    --no-cache             Bypass cache
    -o, --output TEXT       Write output to file
    -r, --retry INTEGER    Number of retry attempts (default: 3)
    --dry-run              Show what would be fetched without downloading

## Examples

# Download a page
fresh get https://docs.python.org/3/tutorial/

# Download and save to file
fresh get https://docs.python.org/3/tutorial/ -o tutorial.md

# With custom headers
fresh get https://example.com --header "Authorization: Bearer xxx"

# Skip cache
fresh get https://docs.python.org/3/ --no-cache
""",
        "search": """
# fresh search

Search for content across documentation pages.

## Usage

    fresh search <QUERY> <URL> [OPTIONS]

## Arguments

    QUERY    The search query (required)
    URL      The URL or alias of the documentation website (required)

## Options

    -v, --verbose             Use verbose output
    --max-pages INTEGER       Maximum number of pages to search (default: 50)
    -d, --depth INTEGER       Maximum crawl depth (default: 3)
    -c, --context INTEGER     Number of context lines around matches (default: 1)
    --case-sensitive          Enable case-sensitive search
    -r, --regex              Treat query as regular expression
    -l, --limit INTEGER       Maximum number of results to show (default: 20)

## Examples

# Search for something
fresh search "virtual environment" https://docs.python.org/3/

# Case-sensitive search
fresh search "ImportError" https://docs.python.org/3/ --case-sensitive

# Regex search
fresh search "^import.*" https://docs.python.org/3/ --regex
""",
        "alias": """
# fresh alias

Manage library aliases for quick access.

## Usage

    fresh alias <COMMAND> [OPTIONS]

## Commands

    add <NAME> <URL>    Add a new alias
    list                List all available aliases
    remove <NAME>      Remove an alias
    search <QUERY>     Search for aliases

## Examples

# Add an alias
fresh alias add python https://docs.python.org/3/

# List aliases
fresh alias list

# Remove an alias
fresh alias remove python

# Search aliases
fresh alias search python
""",
        "update": """
# fresh update

Check for and install updates to fresh.

## Usage

    fresh update [OPTIONS]

## Options

    --check    Only check for updates without installing
    -y, --yes  Automatically confirm updates

## Examples

# Check for updates
fresh update --check

# Update to latest version
fresh update
""",
    }

    if command in docs:
        typer.echo(docs[command])
    else:
        typer.echo(f"Error: Unknown command '{command}'", err=True)
        typer.echo("Available commands: list, get, search, alias, update")
        raise typer.Exit(1)
