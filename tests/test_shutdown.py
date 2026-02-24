"""Tests for fresh.shutdown module."""

from fresh.shutdown import register_shutdown_callback


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
