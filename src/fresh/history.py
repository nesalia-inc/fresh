"""Search history tracking module."""

from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Default history directory
DEFAULT_HISTORY_DIR = Path.home() / ".fresh"

# Default retention in days
DEFAULT_RETENTION_DAYS = 30


def get_history_db() -> Path:
    """Get the path to the history database."""
    return DEFAULT_HISTORY_DIR / "history.db"


def _get_connection() -> sqlite3.Connection:
    """Get a connection to the history database."""
    db_path = get_history_db()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the history database."""
    conn = _get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                url TEXT NOT NULL,
                results_count INTEGER DEFAULT 0,
                success INTEGER DEFAULT 1,
                timestamp TEXT NOT NULL,
                duration_ms INTEGER
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS access_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_path TEXT NOT NULL,
                url TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                method TEXT DEFAULT 'search'
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_search_query ON search_history(query)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_search_url ON search_history(url)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_search_timestamp ON search_history(timestamp)
            """
        )
        conn.commit()
    finally:
        conn.close()


def add_search_record(
    query: str,
    url: str,
    results_count: int = 0,
    success: bool = True,
    duration_ms: int | None = None,
) -> None:
    """Add a search record to history."""
    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO search_history (query, url, results_count, success, timestamp, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                query,
                url,
                results_count,
                1 if success else 0,
                datetime.now(timezone.utc).isoformat(),
                duration_ms,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def add_access_record(
    page_path: str,
    url: str,
    method: str = "search",
) -> None:
    """Add an access record to history."""
    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO access_history (page_path, url, timestamp, method)
            VALUES (?, ?, ?, ?)
            """,
            (
                page_path,
                url,
                datetime.now(timezone.utc).isoformat(),
                method,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_search_history(
    limit: int = 20,
    query: str | None = None,
    url: str | None = None,
) -> list[dict[str, Any]]:
    """Get search history records."""
    conn = _get_connection()
    try:
        sql = "SELECT * FROM search_history"
        params = []

        conditions = []
        if query:
            conditions.append("query LIKE ?")
            params.append(f"%{query}%")
        if url:
            conditions.append("url LIKE ?")
            params.append(f"%{url}%")

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_access_history(
    limit: int = 20,
    url: str | None = None,
) -> list[dict[str, Any]]:
    """Get access history records."""
    conn = _get_connection()
    try:
        sql = "SELECT * FROM access_history"
        params = []

        if url:
            sql += " WHERE url LIKE ?"
            params.append(f"%{url}%")

        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def clear_history(url: str | None = None, older_than_days: int | None = None) -> int:
    """Clear search history.

    Args:
        url: If provided, only clear history for this URL
        older_than_days: If provided, only clear entries older than this many days

    Returns:
        Number of records deleted
    """
    conn = _get_connection()
    try:
        sql = "DELETE FROM search_history WHERE 1=1"
        params = []

        if url:
            sql += " AND url = ?"
            params.append(url)

        if older_than_days:
            cutoff = datetime.now(timezone.utc).timestamp() - (older_than_days * 24 * 60 * 60)
            cutoff_iso = datetime.fromtimestamp(cutoff, timezone.utc).isoformat()
            sql += " AND timestamp < ?"
            params.append(cutoff_iso)

        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def get_history_stats() -> dict[str, int]:
    """Get history statistics."""
    conn = _get_connection()
    try:
        search_count = conn.execute("SELECT COUNT(*) FROM search_history").fetchone()[0]
        access_count = conn.execute("SELECT COUNT(*) FROM access_history").fetchone()[0]

        # Get unique URLs
        unique_urls = conn.execute("SELECT COUNT(DISTINCT url) FROM search_history").fetchone()[0]

        return {
            "search_count": search_count,
            "access_count": access_count,
            "unique_urls": unique_urls,
        }
    finally:
        conn.close()


def export_history(file_path: Path) -> None:
    """Export history to a JSON file."""
    conn = _get_connection()
    try:
        search_history = [dict(row) for row in conn.execute("SELECT * FROM search_history").fetchall()]
        access_history = [dict(row) for row in conn.execute("SELECT * FROM access_history").fetchall()]

        data = {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "search_history": search_history,
            "access_history": access_history,
        }

        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    finally:
        conn.close()


def import_history(file_path: Path) -> int:
    """Import history from a JSON file.

    Returns:
        Number of records imported
    """
    data = json.loads(file_path.read_text(encoding="utf-8"))

    conn = _get_connection()
    try:
        count = 0

        for record in data.get("search_history", []):
            conn.execute(
                """
                INSERT INTO search_history (query, url, results_count, success, timestamp, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.get("query"),
                    record.get("url"),
                    record.get("results_count", 0),
                    record.get("success", 1),
                    record.get("timestamp"),
                    record.get("duration_ms"),
                ),
            )
            count += 1

        for record in data.get("access_history", []):
            conn.execute(
                """
                INSERT INTO access_history (page_path, url, timestamp, method)
                VALUES (?, ?, ?, ?)
                """,
                (
                    record.get("page_path"),
                    record.get("url"),
                    record.get("timestamp"),
                    record.get("method", "search"),
                ),
            )
            count += 1

        conn.commit()
        return count
    finally:
        conn.close()


def cleanup_old_entries(days: int = DEFAULT_RETENTION_DAYS) -> int:
    """Clean up old history entries.

    Args:
        days: Number of days to keep

    Returns:
        Number of records deleted
    """
    conn = _get_connection()
    try:
        cutoff = datetime.now(timezone.utc).timestamp() - (days * 24 * 60 * 60)
        cutoff_iso = datetime.fromtimestamp(cutoff, timezone.utc).isoformat()

        cursor = conn.execute("DELETE FROM search_history WHERE timestamp < ?", (cutoff_iso,))
        search_deleted = cursor.rowcount

        cursor = conn.execute("DELETE FROM access_history WHERE timestamp < ?", (cutoff_iso,))
        access_deleted = cursor.rowcount

        conn.commit()
        return search_deleted + access_deleted
    finally:
        conn.close()


# Initialize database on module import
init_db()
