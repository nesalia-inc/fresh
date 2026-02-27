"""Tests for history command."""

import tempfile
from pathlib import Path
from unittest import mock

import pytest

from fresh import history


class TestHistoryModule:
    """Tests for the history module."""

    def test_get_history_db_path(self):
        """Test history DB path."""
        db_path = history.get_history_db()
        assert db_path.name == "history.db"
        assert ".fresh" in str(db_path)

    def test_init_db_creates_tables(self):
        """Test database initialization creates tables."""
        # Use temp directory for test
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db = Path(tmpdir) / "test_history.db"

            # Mock the DB path
            with mock.patch.object(history, "DEFAULT_HISTORY_DIR", Path(tmpdir)):
                with mock.patch.object(history, "get_history_db", return_value=test_db):
                    # Recreate connection to test DB
                    conn = sqlite3.connect(test_db)
                    try:
                        # Check tables exist after init
                        history.init_db()
                        cursor = conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                        tables = [row[0] for row in cursor.fetchall()]
                        assert "search_history" in tables
                        assert "access_history" in tables
                    finally:
                        conn.close()

    def test_add_and_get_search_record(self):
        """Test adding and retrieving search records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db = Path(tmpdir) / "test_history.db"

            with mock.patch.object(history, "get_history_db", return_value=test_db):
                history.init_db()

                # Add a record
                history.add_search_record(
                    query="test query",
                    url="https://example.com",
                    results_count=5,
                    success=True,
                    duration_ms=100,
                )

                # Retrieve records
                records = history.get_search_history(limit=10)
                assert len(records) == 1
                assert records[0]["query"] == "test query"
                assert records[0]["url"] == "https://example.com"
                assert records[0]["results_count"] == 5

    def test_get_search_history_with_filters(self):
        """Test filtering search history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db = Path(tmpdir) / "test_history.db"

            with mock.patch.object(history, "get_history_db", return_value=test_db):
                history.init_db()

                # Add multiple records
                history.add_search_record("react", "https://react.dev", 3, True)
                history.add_search_record("vue", "https://vuejs.org", 2, True)
                history.add_search_record("react hooks", "https://react.dev", 5, True)

                # Filter by query
                records = history.get_search_history(query="react")
                assert len(records) == 2

                # Filter by URL
                records = history.get_search_history(url="react.dev")
                assert len(records) == 2

    def test_clear_history(self):
        """Test clearing history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db = Path(tmpdir) / "test_history.db"

            with mock.patch.object(history, "get_history_db", return_value=test_db):
                history.init_db()

                # Add records
                history.add_search_record("test1", "https://example.com", 1, True)
                history.add_search_record("test2", "https://example.com", 1, True)

                # Clear all
                count = history.clear_history()
                assert count == 2

                records = history.get_search_history()
                assert len(records) == 0

    def test_get_history_stats(self):
        """Test getting history statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db = Path(tmpdir) / "test_history.db"

            with mock.patch.object(history, "get_history_db", return_value=test_db):
                history.init_db()

                # Add records
                history.add_search_record("test", "https://example.com", 1, True)
                history.add_search_record("test2", "https://example.org", 1, True)
                history.add_search_record("test3", "https://example.com", 1, True)

                stats = history.get_history_stats()
                assert stats["search_count"] == 3
                assert stats["unique_urls"] == 2

    def test_export_import_history(self):
        """Test exporting and importing history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db = Path(tmpdir) / "test_history.db"
            export_file = Path(tmpdir) / "export.json"

            with mock.patch.object(history, "get_history_db", return_value=test_db):
                history.init_db()

                # Add records
                history.add_search_record("test", "https://example.com", 1, True)

                # Export
                history.export_history(export_file)
                assert export_file.exists()

                # Clear and import
                history.clear_history()
                assert len(history.get_search_history()) == 0

                count = history.import_history(export_file)
                assert count == 1
                assert len(history.get_search_history()) == 1


import sqlite3
