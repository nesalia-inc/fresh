"""fresh - CLI application."""

__version__ = "0.2.1"

import typer

from .commands.alias import alias_app
from .commands.get import get
from .commands.list import list_urls
from .commands.search import search

app = typer.Typer(help="fresh - A CLI application")

# Register subcommands
app.command(name="list")(list_urls)
app.command(name="get")(get)
app.command(name="search")(search)
app.add_typer(alias_app, name="alias")


@app.command()
def hello(name: str = "World") -> None:
    """Say hello to someone."""
    print(f"Hello, {name}!")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
