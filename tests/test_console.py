"""Tests for fresh.console module."""

from fresh.console import (
    ErrorMessage,
    WarningMessage,
    echo_error,
    echo_info,
    echo_success,
    echo_warning,
    get_error_count,
    get_warning_count,
    has_errors,
    is_verbose,
    reset_console,
    set_verbose,
)


class TestVerboseMode:
    """Tests for verbose mode functions."""

    def setup_method(self):
        """Reset console before each test."""
        reset_console()
        set_verbose(False)

    def test_set_verbose(self):
        """Should set verbose mode."""
        set_verbose(True)
        assert is_verbose() is True

    def test_is_verbose_default(self):
        """Should default to False."""
        assert is_verbose() is False

    def test_reset_console(self):
        """Should reset console state."""
        echo_error("test error")
        assert get_error_count() == 1

        reset_console()
        assert get_error_count() == 0
        assert get_warning_count() == 0


class TestEchoError:
    """Tests for echo_error function."""

    def setup_method(self):
        """Reset console before each test."""
        reset_console()
        set_verbose(False)

    def test_echo_error_basic(self):
        """Should add error to state."""
        echo_error("Test error")
        assert get_error_count() == 1
        assert has_errors() is True

    def test_echo_error_with_url(self):
        """Should store URL with error."""
        echo_error("Test error", url="https://example.com")
        errors = get_error_count()
        assert errors == 1

    def test_echo_error_with_code(self):
        """Should store error code."""
        echo_error("Test error", code="TEST_CODE")
        errors = get_error_count()
        assert errors == 1

    def test_echo_error_with_suggestions(self):
        """Should store suggestions."""
        echo_error("Test error", suggestions=["Try this", "Or this"])
        errors = get_error_count()
        assert errors == 1


class TestEchoWarning:
    """Tests for echo_warning function."""

    def setup_method(self):
        """Reset console before each test."""
        reset_console()
        set_verbose(False)

    def test_echo_warning_basic(self):
        """Should add warning to state."""
        echo_warning("Test warning")
        assert get_warning_count() == 1

    def test_echo_warning_with_url(self):
        """Should store URL with warning."""
        echo_warning("Test warning", url="https://example.com")
        assert get_warning_count() == 1

    def test_echo_warning_with_count(self):
        """Should store count."""
        echo_warning("Test warning", count=5)
        assert get_warning_count() == 1


class TestEchoInfo:
    """Tests for echo_info function."""

    def test_echo_info_basic(self):
        """Should work without error."""
        echo_info("Test info")
        # No exception should be raised


class TestEchoSuccess:
    """Tests for echo_success function."""

    def test_echo_success_basic(self):
        """Should work without error."""
        echo_success("Test success")
        # No exception should be raised


class TestDataClasses:
    """Tests for error and warning data classes."""

    def test_error_message(self):
        """Should create ErrorMessage."""
        error = ErrorMessage(
            message="Test error",
            url="https://example.com",
            code="TEST_CODE",
            suggestions=["suggestion1"],
            details="details",
        )
        assert error.message == "Test error"
        assert error.url == "https://example.com"
        assert error.code == "TEST_CODE"
        assert error.suggestions == ["suggestion1"]
        assert error.details == "details"

    def test_warning_message(self):
        """Should create WarningMessage."""
        warning = WarningMessage(
            message="Test warning",
            url="https://example.com",
            count=5,
        )
        assert warning.message == "Test warning"
        assert warning.url == "https://example.com"
        assert warning.count == 5
