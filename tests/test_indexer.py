"""Tests for indexer module."""

import tempfile
from pathlib import Path
from unittest import mock

from fresh import indexer


class TestIndexer:
    """Tests for the indexer module."""

    def test_get_index_db_path(self):
        """Test index DB path generation."""
        db_path = indexer.get_index_db("example.com")
        assert db_path.name == "example.com.db"
        assert ".fresh" in str(db_path)

    def test_init_index_creates_tables(self):
        """Test that init_index creates required tables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                indexer.init_index("test-site")

                import sqlite3
                conn = sqlite3.connect(indexer.get_index_db("test-site"))
                try:
                    cursor = conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                    tables = [row[0] for row in cursor.fetchall()]
                    assert "index_metadata" in tables
                    assert "pages_fts" in tables
                finally:
                    conn.close()

    def test_index_page(self):
        """Test indexing a single page."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                indexer.init_index("test-site")

                html = """
                <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>Main Heading</h1>
                    <h2>Sub Heading</h2>
                    <p>Some content here.</p>
                    <code>def hello(): pass</code>
                </body>
                </html>
                """

                indexer.index_page("test-site", "/test", html, "Test Page")

                # Verify the page was indexed
                results = indexer.search_index("test-site", "hello")
                assert len(results) == 1
                assert results[0]["url"] == "/test"

    def test_search_index(self):
        """Test searching the index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                indexer.init_index("test-site")

                # Add some pages
                html1 = "<html><head><title>Page 1</title></head><body><p>Python content</p></body></html>"
                html2 = "<html><head><title>Page 2</title></head><body><p>JavaScript content</p></body></html>"

                indexer.index_page("test-site", "/python", html1, "Python")
                indexer.index_page("test-site", "/js", html2, "JavaScript")

                # Search for Python
                results = indexer.search_index("test-site", "Python")
                assert len(results) >= 1

    def test_delete_index(self):
        """Test deleting an index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                indexer.init_index("test-site")
                db_path = indexer.get_index_db("test-site")
                assert db_path.exists()

                indexer.delete_index("test-site")
                assert not db_path.exists()

    def test_get_index_stats(self):
        """Test getting index statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                indexer.init_index("test-site")

                html = "<html><body><p>Content</p></body></html>"
                indexer.index_page("test-site", "/test", html, "Test")

                stats = indexer.get_index_stats("test-site")
                assert stats is not None
                assert stats["site_name"] == "test-site"
                assert stats["page_count"] == 1
                assert stats["last_updated"] is not None

    def test_build_index_from_directory(self):
        """Test building index from directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                # Create test HTML files
                pages_dir = Path(tmpdir) / "pages"
                pages_dir.mkdir()

                (pages_dir / "index.html").write_text(
                    "<html><head><title>Home</title></head><body><p>Home page</p></body></html>"
                )
                (pages_dir / "about.html").write_text(
                    "<html><head><title>About</title></head><body><p>About us</p></body></html>"
                )

                count = indexer.build_index_from_directory("test-site", pages_dir)

                assert count == 2
                stats = indexer.get_index_stats("test-site")
                assert stats["page_count"] == 2

    def test_index_page_from_file(self):
        """Test indexing from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                indexer.init_index("test-site")

                # Create test file
                html_file = Path(tmpdir) / "test.html"
                html_file.write_text(
                    "<html><head><title>Test</title></head><body><p>Test content</p></body></html>"
                )

                indexer.index_page_from_file("test-site", html_file)

                results = indexer.search_index("test-site", "Test content")
                assert len(results) == 1

    def test_rebuild_index(self):
        """Test rebuilding index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                # Create initial index
                indexer.init_index("test-site")
                html = "<html><body><p>Old content</p></body></html>"
                indexer.index_page("test-site", "/old", html, "Old")

                # Create pages directory
                pages_dir = Path(tmpdir) / "pages"
                pages_dir.mkdir()
                (pages_dir / "new.html").write_text(
                    "<html><body><p>New content</p></body></html>"
                )

                # Rebuild
                count = indexer.rebuild_index("test-site", pages_dir)

                assert count == 1
                results = indexer.search_index("test-site", "New content")
                assert len(results) == 1

    def test_get_index_age(self):
        """Test getting index age."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(indexer, "DEFAULT_INDEX_DIR", Path(tmpdir)):
                indexer.init_index("test-site")

                # Add a page to set last_updated
                html = "<html><body><p>Content</p></body></html>"
                indexer.index_page("test-site", "/test", html, "Test")

                age = indexer.get_index_age("test-site")
                assert age is not None

    def test_get_index_age_nonexistent(self):
        """Test getting age of nonexistent index."""
        age = indexer.get_index_age("nonexistent-site")
        assert age is None
