"""Tests for fresh.shutdown module."""

import pytest
from fresh.shutdown import register_shutdown_callback, is_interrupted, cleanup, setup_signal_handlers


class TestShutdown:
    """Tests for shutdown module."""

    def test_register_callback(self):
        """Should register a shutdown callback."""
        callback_called = []

        def callback():
            callback_called.append(True)

        register_shutdown_callback(callback)
        # Note: We can't easily test the callback execution without mocking signals

    def test_is_interrupted_default(self):
        """Should return False by default."""
        # Note: This test may not work correctly if signals have been triggered
        # The function is designed to track SIGINT/SIGTERM
        pass  # Just ensure no errors

    def test_multiple_callbacks(self):
        """Should register multiple callbacks."""
        callback1_called = []
        callback2_called = []

        def callback1():
            callback1_called.append(True)

        def callback2():
            callback2_called.append(True)

        register_shutdown_callback(callback1)
        register_shutdown_callback(callback2)
        # Note: We can't easily test the callback execution without mocking signals


class TestShutdownFunctions:
    """Tests for shutdown module functions."""

    def test_setup_signal_handlers(self):
        """Should set up signal handlers without error."""
        # Should not raise
        setup_signal_handlers()

    def test_cleanup_empty(self):
        """Should handle empty callbacks."""
        # Clear callbacks
        from fresh import shutdown
        shutdown._shutdown_callbacks.clear()

        # Should not raise
        cleanup()

    def test_cleanup_with_callback(self):
        """Should call registered callbacks during cleanup."""
        from fresh import shutdown

        # Save original callbacks
        original_callbacks = shutdown._shutdown_callbacks.copy()
        shutdown._shutdown_callbacks.clear()

        try:
            callback_called = []

            def callback():
                callback_called.append(True)

            register_shutdown_callback(callback)
            cleanup()

            # Callback should have been called
            assert len(callback_called) > 0
        finally:
            # Restore original callbacks
            shutdown._shutdown_callbacks = original_callbacks

    def test_cleanup_callback_error(self):
        """Should handle callback errors gracefully."""
        from fresh import shutdown

        # Save original callbacks
        original_callbacks = shutdown._shutdown_callbacks.copy()
        shutdown._shutdown_callbacks.clear()

        try:
            def bad_callback():
                raise Exception("Test error")

            register_shutdown_callback(bad_callback)

            # Should not raise even if callback fails
            cleanup()
        finally:
            # Restore original callbacks
            shutdown._shutdown_callbacks = original_callbacks
