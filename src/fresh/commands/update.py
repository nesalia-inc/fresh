"""Update command - check for and install updates to fresh."""

from __future__ import annotations

import subprocess
import sys
import urllib.request
import json

import typer

from .. import __version__

app = typer.Typer(help="Check for and install updates to fresh.")


def get_latest_version() -> str | None:
    """Get the latest version from PyPI."""
    try:
        url = "https://pypi.org/pypi/fresh-docs/json"
        response = urllib.request.urlopen(url, timeout=10)
        data: dict = json.loads(response.read().decode())
        version: str = data["info"]["version"]
        return version
    except Exception:
        return None


@app.command(name="update")
def update(
    check_only: bool = typer.Option(
        False, "--check", help="Only check for updates without installing"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Automatically confirm updates"
    ),
) -> None:
    """Check for and install updates to fresh."""
    # Get current version
    current_version = __version__

    # Check if there's a newer version available
    latest_version = get_latest_version()

    if latest_version is None:
        typer.echo("Error: Could not check for updates", err=True)
        raise typer.Exit(1)

    # Compare versions
    from packaging import version

    if version.parse(latest_version) > version.parse(current_version):
        typer.echo(f"Current version: {current_version}")
        typer.echo(f"Latest version: {latest_version}")

        if check_only:
            typer.echo("A new version is available!")
            typer.echo("Run 'fresh update' to install it.")
            return

        # Ask for confirmation unless --yes is passed
        if not yes:
            confirm = typer.confirm("Do you want to update?")
            if not confirm:
                typer.echo("Update cancelled.")
                return

        # Install the update
        typer.echo("Updating fresh...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "fresh-docs"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                typer.echo("Update successful!")
                typer.echo(f"Updated from {current_version} to {latest_version}")
            else:
                typer.echo(f"Error: Update failed: {result.stderr}", err=True)
                raise typer.Exit(1)

        except Exception as e:
            typer.echo(f"Error: Could not install update: {e}", err=True)
            raise typer.Exit(1)
    else:
        typer.echo(f"Current version: {current_version}")
        typer.echo("You are using the latest version!")
