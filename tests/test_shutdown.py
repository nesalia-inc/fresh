"""Tests for fresh.shutdown module."""

from unittest.mock import patch
from fresh.shutdown import register_shutdown_callback, is_interrupted, cleanup, setup_signal_handlers


class TestShutdown:
    """Tests for shutdown module."""

    def test_register_callback(self):
        """Should register a shutdown callback."""
        from fresh import shutdown
        original_callbacks = shutdown._shutdown_callbacks.copy()
        shutdown._shutdown_callbacks.clear()

        try:
            callback_called = []

            def callback():
                callback_called.append(True)

            register_shutdown_callback(callback)
            assert len(shutdown._shutdown_callbacks) == 1
        finally:
            shutdown._shutdown_callbacks = original_callbacks

    def test_is_interrupted_default(self):
        """Should return False by default."""
        from fresh import shutdown
        # Reset the interrupted state
        shutdown._interrupted = False
        assert is_interrupted() is False

    def test_multiple_callbacks(self):
        """Should register multiple callbacks."""
        from fresh import shutdown
        original_callbacks = shutdown._shutdown_callbacks.copy()
        shutdown._shutdown_callbacks.clear()

        try:
            def callback1():
                pass

            def callback2():
                pass

            register_shutdown_callback(callback1)
            register_shutdown_callback(callback2)
            assert len(shutdown._shutdown_callbacks) == 2
        finally:
            shutdown._shutdown_callbacks = original_callbacks


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


class TestSignalHandler:
    """Tests for signal handler function."""

    @patch('fresh.shutdown.signal.signal')
    def test_setup_signal_handlers_calls_signal(self, mock_signal):
        """Should register signal handlers."""
        setup_signal_handlers()
        # Should have called signal.signal at least twice (SIGINT and SIGTERM)
        assert mock_signal.call_count >= 2

    @patch('sys.exit')
    def test_signal_handler_execution(self, mock_exit):
        """Should execute callbacks when signal is received."""
        from fresh import shutdown

        # Save original state
        original_callbacks = shutdown._shutdown_callbacks.copy()
        original_interrupted = shutdown._interrupted
        shutdown._shutdown_callbacks.clear()

        try:
            callback_called = []

            def callback():
                callback_called.append(True)

            register_shutdown_callback(callback)

            # Manually call the signal handler
            shutdown._signal_handler(2, None)

            # Callback should have been called
            assert len(callback_called) > 0
        finally:
            shutdown._shutdown_callbacks = original_callbacks
            shutdown._interrupted = original_interrupted
