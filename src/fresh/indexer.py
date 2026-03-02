"""Search index module for fast local content search."""

from __future__ import annotations

import logging
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Default index directory
DEFAULT_INDEX_DIR = Path.home() / ".fresh" / "index"

# Valid characters for site names: alphanumeric, underscore, hyphen, dot
SAFE_SITE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.\-]+$")


def _validate_site_name(site_name: str) -> bool:
    """Validate site name to prevent path traversal.

    Returns True if valid, False otherwise.
    """
    if not site_name or len(site_name) > 255:
        return False
    return bool(SAFE_SITE_NAME_PATTERN.match(site_name))


def get_index_db(site_name: str) -> Path:
    """Get the path to the index database for a site.

    Args:
        site_name: The site name (must contain only safe characters)

    Returns:
        Path to the index database

    Raises:
        ValueError: If site_name contains invalid characters
    """
    if not _validate_site_name(site_name):
        raise ValueError(
            f"Invalid site name '{site_name}'. Site names must contain only "
            "alphanumeric characters, underscores, hyphens, and dots."
        )
    index_dir = DEFAULT_INDEX_DIR
    index_dir.mkdir(parents=True, exist_ok=True)
    return index_dir / f"{site_name}.db"


def _get_connection(db_path: Path) -> sqlite3.Connection:
    """Get a connection to the index database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_index(site_name: str) -> None:
    """Initialize the search index for a site."""
    db_path = get_index_db(site_name)
    conn = _get_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS index_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                url,
                title,
                headings,
                content,
                code,
                tokenize='porter unicode61'
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_index_age(site_name: str) -> datetime | None:
    """Get the age of the index for a site."""
    db_path = get_index_db(site_name)
    if not db_path.exists():
        return None

    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT value FROM index_metadata WHERE key = 'last_updated'",
        )
        row = cursor.fetchone()
        if row:
            return datetime.fromisoformat(row[0])
        return None
    finally:
        conn.close()


def index_page(
    site_name: str,
    url: str,
    html_content: str,
    title: str = "",
) -> None:
    """Index a single page."""
    db_path = get_index_db(site_name)

    # Parse HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Extract text content
    text_content = soup.get_text(separator="\n").strip()

    # Extract headings
    headings: list[str] = []
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        heading_text = heading.get_text(strip=True)
        if heading_text:
            headings.append(heading_text)

    # Extract code blocks
    code_blocks: list[str] = []
    for code in soup.find_all("code"):
        code_text = code.get_text(strip=True)
        if code_text and len(code_text) > 2:  # Filter out short snippets
            code_blocks.append(code_text)

    conn = _get_connection(db_path)
    try:
        # Delete existing entry for this URL
        conn.execute("DELETE FROM pages_fts WHERE url = ?", (url,))

        # Insert new entry
        conn.execute(
            """
            INSERT INTO pages_fts (url, title, headings, content, code)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                url,
                title,
                "\n".join(headings),
                text_content,
                "\n".join(code_blocks),
            ),
        )

        # Update metadata
        conn.execute(
            """
            INSERT OR REPLACE INTO index_metadata (key, value)
            VALUES ('last_updated', ?)
            """,
            (datetime.now(timezone.utc).isoformat(),),
        )

        conn.commit()
    finally:
        conn.close()


def index_page_from_file(site_name: str, file_path: Path) -> None:
    """Index a page from a local HTML file."""
    html_content = file_path.read_text(encoding="utf-8")

    # Extract title
    soup = BeautifulSoup(html_content, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Construct URL from file path
    relative_path = file_path.stem
    if relative_path == "index":
        url = "/"
    else:
        url = f"/{relative_path}"

    index_page(site_name, url, html_content, title)


def build_index_from_directory(site_name: str, pages_dir: Path) -> int:
    """Build the search index from a directory of HTML files."""
    init_index(site_name)

    count = 0
    for html_file in pages_dir.rglob("*.html"):
        try:
            index_page_from_file(site_name, html_file)
            count += 1
        except Exception as e:
            logger.warning(f"Failed to index {html_file}: {e}")

    return count


def search_index(
    site_name: str,
    query: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search the index for a query."""
    db_path = get_index_db(site_name)
    if not db_path.exists():
        return []

    conn = _get_connection(db_path)
    try:
        # Use FTS5 MATCH for full-text search
        cursor = conn.execute(
            """
            SELECT url, title, headings, snippet(pages_fts, 3, '<mark>', '</mark>', '...', 32) as snippet
            FROM pages_fts
            WHERE pages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, limit),
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                "url": row["url"],
                "title": row["title"],
                "headings": row["headings"],
                "snippet": row["snippet"],
            })

        return results
    except sqlite3.OperationalError as e:
        logger.warning(f"Index search error: {e}")
        return []
    finally:
        conn.close()


def delete_index(site_name: str) -> bool:
    """Delete the index for a site."""
    db_path = get_index_db(site_name)
    if db_path.exists():
        db_path.unlink()
        return True
    return False


def get_index_stats(site_name: str) -> dict[str, Any] | None:
    """Get statistics about the index."""
    db_path = get_index_db(site_name)
    if not db_path.exists():
        return None

    conn = _get_connection(db_path)
    try:
        # Get page count
        cursor = conn.execute("SELECT COUNT(*) FROM pages_fts")
        page_count = cursor.fetchone()[0]

        # Get last updated
        cursor = conn.execute(
            "SELECT value FROM index_metadata WHERE key = 'last_updated'"
        )
        row = cursor.fetchone()
        last_updated = row[0] if row else None

        return {
            "site_name": site_name,
            "page_count": page_count,
            "last_updated": last_updated,
            "db_path": str(db_path),
        }
    finally:
        conn.close()


def rebuild_index(site_name: str, pages_dir: Path) -> int:
    """Rebuild the entire index for a site."""
    delete_index(site_name)
    return build_index_from_directory(site_name, pages_dir)
