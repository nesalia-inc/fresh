"""Alias configuration and management."""

from __future__ import annotations

import json
import logging
import os
import pathlib

logger = logging.getLogger(__name__)


# Built-in aliases for popular libraries
BUILTIN_ALIASES: dict[str, str] = {
    "nextjs": "https://nextjs.org/docs",
    "react": "https://react.dev",
    "vue": "https://vuejs.org/guide",
    "svelte": "https://svelte.dev/docs",
    "django": "https://docs.djangoproject.com/en/stable",
    "flask": "https://flask.palletsprojects.com/en/stable",
    "fastapi": "https://fastapi.tiangolo.com",
    "rust": "https://doc.rust-lang.org/book",
    "go": "https://go.dev/doc",
    "python": "https://docs.python.org/3",
    "typescript": "https://www.typescriptlang.org/docs",
    "astro": "https://docs.astro.build",
    "tailwind": "https://tailwindcss.com/docs",
    "vite": "https://vite.dev/guide",
    "remix": "https://remix.run/docs",
}

def get_config_dir() -> pathlib.Path:
    """Get the user configuration directory."""
    if os.name == "nt":  # Windows
        base = os.environ.get("APPDATA", pathlib.Path.home() / "AppData" / "Roaming")
    else:  # Unix-like
        base = os.environ.get("XDG_CONFIG_HOME", pathlib.Path.home() / ".config")

    return pathlib.Path(base) / "fresh"


def get_user_aliases_path() -> pathlib.Path:
    """Get the path to user aliases file."""
    return get_config_dir() / "aliases.json"


def load_aliases() -> dict[str, str]:
    """
    Load aliases from all sources with priority: Local > User > Global > Built-in.

    Returns:
        Dictionary of alias -> URL mappings
    """
    aliases = BUILTIN_ALIASES.copy()

    # Load user aliases
    user_path = get_user_aliases_path()
    if user_path.exists():
        try:
            with open(user_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "aliases" in data:
                    aliases.update(data["aliases"])
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load user aliases from {user_path}: {e}")

    return aliases


def save_aliases(aliases: dict[str, str]) -> None:
    """
    Save aliases to user config file.

    Only saves user-defined aliases (filters out built-in aliases).

    Args:
        aliases: Dictionary of alias -> URL mappings (all aliases)
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    user_path = get_user_aliases_path()

    # Filter out built-in aliases - only save user-defined ones
    user_only_aliases = {
        alias: url
        for alias, url in aliases.items()
        if alias not in BUILTIN_ALIASES or BUILTIN_ALIASES.get(alias) != url
    }

    # Load existing data to preserve other settings
    existing = {}
    if user_path.exists():
        try:
            with open(user_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load existing config from {user_path}, starting fresh: {e}")

    existing["aliases"] = user_only_aliases

    with open(user_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def resolve_alias(alias_or_url: str) -> str:
    """
    Resolve an alias to its URL.

    Args:
        alias_or_url: Either an alias or a full URL

    Returns:
        The resolved URL
    """
    aliases = load_aliases()

    # If it looks like a URL, return as-is
    if alias_or_url.startswith(("http://", "https://")):
        return alias_or_url

    # Try to find as alias
    return aliases.get(alias_or_url, alias_or_url)


def is_alias(value: str) -> bool:
    """
    Check if a value is a known alias.

    Args:
        value: The value to check

    Returns:
        True if it's a known alias (not a URL)
    """
    if value.startswith(("http://", "https://")):
        return False

    aliases = load_aliases()
    return value in aliases


def search_aliases(query: str) -> list[tuple[str, str]]:
    """
    Search for aliases matching a query.

    Args:
        query: Search query

    Returns:
        List of (alias, url) tuples matching the query
    """
    aliases = load_aliases()
    query_lower = query.lower()

    results = [
        (alias, url)
        for alias, url in aliases.items()
        if query_lower in alias.lower() or query_lower in url.lower()
    ]

    return sorted(results, key=lambda x: x[0])
