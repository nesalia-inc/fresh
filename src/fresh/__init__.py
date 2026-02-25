"""fresh - CLI application."""

__version__ = "1.1.0"

import typer

from .exceptions import (
    AliasError,
    CacheError,
    CLIError,
    ConfigError,
    CrawlerError,
    FetchError,
    FilterError,
    FreshError,
    NetworkError,
    SitemapError,
    TimeoutError,
    ValidationError,
)

__all__ = [
    "FreshError",
    "NetworkError",
    "FetchError",
    "TimeoutError",
    "ValidationError",
    "AliasError",
    "CacheError",
    "SitemapError",
    "CrawlerError",
    "FilterError",
    "ConfigError",
    "CLIError",
]

from .commands.alias import alias_app
from .commands.doc import doc
from .commands.get import get
from .commands.list import list_urls
from .commands.search import search
from .commands.sync import sync

app = typer.Typer(help="fresh - A CLI application")

# Register subcommands
app.command(name="list")(list_urls)
app.command(name="get")(get)
app.command(name="search")(search)
app.command(name="doc")(doc)
app.command(name="sync")(sync)
app.add_typer(alias_app, name="alias")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
