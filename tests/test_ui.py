"""Tests for fresh.ui module."""

import sys
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest


class TestUIConstants:
    """Tests for UI constants."""

    def test_check_mark_defined(self):
        """Should have CHECK_MARK defined."""
        from fresh.ui import CHECK_MARK
        assert CHECK_MARK is not None
        assert len(CHECK_MARK) > 0

    def test_cross_mark_defined(self):
        """Should have CROSS_MARK defined."""
        from fresh.ui import CROSS_MARK
        assert CROSS_MARK is not None
        assert len(CROSS_MARK) > 0

    def test_info_mark_defined(self):
        """Should have INFO_MARK defined."""
        from fresh.ui import INFO_MARK
        assert INFO_MARK is not None
        assert len(INFO_MARK) > 0


class TestIsWindows:
    """Tests for _is_windows function."""

    def test_is_windows_returns_bool(self):
        """Should return a boolean."""
        from fresh.ui import _is_windows
        result = _is_windows()
        assert isinstance(result, bool)

    def test_is_windows_platform_check(self):
        """Should check platform correctly."""
        from fresh.ui import _is_windows
        # On Windows it should return True, on others False
        import platform
        expected = platform.system() == "Windows"
        assert _is_windows() == expected


class TestIsInteractive:
    """Tests for is_interactive function."""

    def test_is_interactive_returns_bool(self):
        """Should return a boolean."""
        from fresh.ui import is_interactive
        result = is_interactive()
        assert isinstance(result, bool)

    def test_is_interactive_with_tty(self):
        """Should check if stdout is a TTY."""
        from fresh.ui import is_interactive
        # When not a TTY (like in tests), should return False
        result = is_interactive()
        assert result == sys.stdout.isatty()


class TestSpinner:
    """Tests for spinner context manager."""

    def test_spinner_non_interactive(self):
        """Should work in non-interactive mode."""
        from fresh.ui import spinner
        # In non-interactive mode, should just yield
        with spinner("Test"):
            pass  # Should not raise

    def test_spinner_returns_context_manager(self):
        """Should return a context manager."""
        from fresh.ui import spinner
        result = spinner("Test")
        # Should be a context manager (has __enter__ and __exit__)
        assert hasattr(result, '__enter__')
        assert hasattr(result, '__exit__')


class TestRunWithProgress:
    """Tests for run_with_progress function."""

    def test_run_with_progress_verbose(self):
        """Should run func in verbose mode."""
        from fresh.ui import run_with_progress

        result = run_with_progress(
            description="Test",
            func=lambda: "result",
            verbose_message="Verbose message",
            verbose=True,
        )
        assert result == "result"

    def test_run_with_progress_non_verbose_non_interactive(self):
        """Should run func without spinner in non-interactive mode."""
        from fresh.ui import run_with_progress

        result = run_with_progress(
            description="Test",
            func=lambda: "result",
            verbose=False,
        )
        assert result == "result"

    def test_run_with_progress_returns_func_result(self):
        """Should return the function result."""
        from fresh.ui import run_with_progress

        result = run_with_progress(
            description="Test",
            func=lambda: 42,
            verbose=False,
        )
        assert result == 42


class TestShowErrorMessage:
    """Tests for show_error_message function."""

    def test_show_error_message_basic(self):
        """Should show error message."""
        from fresh.ui import show_error_message

        # Should not raise
        show_error_message("Test error")

    def test_show_error_message_with_exception(self):
        """Should handle exceptions gracefully."""
        from fresh.ui import show_error_message

        # Mock Console to raise exception
        with patch('fresh.ui.Console') as mock_console:
            mock_console.side_effect = Exception("Console error")
            # Should fallback to basic print
            show_error_message("Test error")


class TestShowInfoMessage:
    """Tests for show_info_message function."""

    def test_show_info_message_basic(self):
        """Should show info message."""
        from fresh.ui import show_info_message

        # Should not raise
        show_info_message("Test info")

    def test_show_info_message_with_exception(self):
        """Should handle exceptions gracefully."""
        from fresh.ui import show_info_message

        # Mock Console to raise exception
        with patch('fresh.ui.console') as mock_console:
            mock_console.print.side_effect = Exception("Console error")
            # Should fallback to basic print
            show_info_message("Test info")


class TestShowSuccessMessage:
    """Tests for show_success_message function."""

    def test_show_success_message_basic(self):
        """Should show success message."""
        from fresh.ui import show_success_message

        # Should not raise
        show_success_message("Test success")

    def test_show_success_message_with_exception(self):
        """Should handle exceptions gracefully."""
        from fresh.ui import show_success_message

        # Mock Console to raise exception
        with patch('fresh.ui.console') as mock_console:
            mock_console.print.side_effect = Exception("Console error")
            # Should fallback to basic print
            show_success_message("Test success")
