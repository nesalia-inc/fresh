"""Tests for core types: Result, Maybe, Try."""

import pytest

from fresh.core.types import Maybe, Result, Try


class TestResult:
    """Tests for Result type."""

    def test_ok_creates_successful_result(self):
        """Should create successful result with value."""
        result = Result.ok("test value")

        assert result.ok is True
        assert result.value == "test value"
        assert result.error is None

    def test_err_creates_failed_result(self):
        """Should create failed result with error."""
        error = ValueError("test error")
        result = Result.err(error)

        assert result.ok is False
        assert result.value is None
        assert result.error == error

    def test_is_ok_true_for_success(self):
        """is_ok should return True for successful result."""
        result = Result.ok("value")
        assert result.is_ok is True

    def test_is_ok_false_for_failure(self):
        """is_ok should return False for failed result."""
        result = Result.err(ValueError("error"))
        assert result.is_ok is False

    def test_is_err_true_for_failure(self):
        """is_err should return True for failed result."""
        result = Result.err(ValueError("error"))
        assert result.is_err is True

    def test_is_err_false_for_success(self):
        """is_err should return False for successful result."""
        result = Result.ok("value")
        assert result.is_err is False

    def test_unwrap_returns_value_on_success(self):
        """unwrap should return value on success."""
        result = Result.ok("test")
        assert result.unwrap() == "test"

    def test_unwrap_raises_on_failure(self):
        """unwrap should raise error on failure."""
        error = ValueError("test error")
        result = Result.err(error)

        with pytest.raises(ValueError):
            result.unwrap()

    def test_unwrap_or_returns_default_on_failure(self):
        """unwrap_or should return default on failure."""
        result = Result.err(ValueError("error"))
        assert result.unwrap_or("default") == "default"

    def test_unwrap_or_returns_value_on_success(self):
        """unwrap_or should return value on success."""
        result = Result.ok("value")
        assert result.unwrap_or("default") == "value"

    def test_with_union_error_types(self):
        """Should work with union error types."""
        # This is the V2 pattern: Result[T, E1 | E2 | E3]
        error: str = "validation error"
        result: Result[str, str] = Result.err(error)

        assert result.is_err
        assert result.error == "validation error"


class TestMaybe:
    """Tests for Maybe type."""

    def test_some_creates_maybe_with_value(self):
        """Should create Maybe with a value."""
        maybe = Maybe.some("test value")

        assert maybe.value == "test value"
        assert maybe.is_some is True
        assert maybe.is_none is False

    def test_none_creates_maybe_without_value(self):
        """Should create Maybe without a value."""
        maybe = Maybe.none()

        assert maybe.value is None
        assert maybe.is_some is False
        assert maybe.is_none is True

    def test_from_optional_with_value(self):
        """Should create Maybe from optional with value."""
        maybe = Maybe.from_optional("test")

        assert maybe.is_some is True
        assert maybe.value == "test"

    def test_from_optional_with_none(self):
        """Should create Maybe from optional with None."""
        maybe = Maybe.from_optional(None)

        assert maybe.is_none is True

    def test_map_transforms_value(self):
        """map should transform the value if present."""
        maybe = Maybe.some(5)
        result = maybe.map(lambda x: x * 2)

        assert result.value == 10

    def test_map_does_nothing_on_none(self):
        """map should return none if Maybe is none."""
        maybe = Maybe.none()
        result = maybe.map(lambda x: x * 2)

        assert result.is_none is True

    def test_flat_map_chains_functions(self):
        """flat_map should chain Maybe-returning functions."""
        maybe = Maybe.some(5)

        def double(x: int) -> Maybe[int]:
            return Maybe.some(x * 2)

        result = maybe.flat_map(double)
        assert result.value == 10

    def test_flat_map_returns_none_on_none(self):
        """flat_map should return none if Maybe is none."""
        maybe = Maybe.none()

        def double(x: int) -> Maybe[int]:
            return Maybe.some(x * 2)

        result = maybe.flat_map(double)
        assert result.is_none is True

    def test_get_or_returns_value(self):
        """get_or should return value if present."""
        maybe = Maybe.some("test")
        assert maybe.get_or("default") == "test"

    def test_get_or_returns_default_on_none(self):
        """get_or should return default if none."""
        maybe = Maybe.none()
        assert maybe.get_or("default") == "default"


class TestTry:
    """Tests for Try type."""

    def test_ok_creates_successful_try(self):
        """Should create successful Try with value."""
        try_ = Try.ok("test value")

        assert try_.value == "test value"
        assert try_.error is None
        assert try_.is_ok is True
        assert try_.is_err is False

    def test_err_creates_failed_try(self):
        """Should create failed Try with error."""
        error = ValueError("test error")
        try_ = Try.err(error)

        assert try_.value is None
        assert try_.error == error
        assert try_.is_ok is False
        assert try_.is_err is True

    def test_capture_wraps_function_success(self):
        """capture should wrap successful function."""
        try_ = Try.capture(lambda: "success")

        assert try_.is_ok is True
        assert try_.value == "success"

    def test_capture_catches_exception(self):
        """capture should catch exception from function."""
        def failing():
            raise ValueError("test error")

        try_ = Try.capture(failing)

        assert try_.is_err is True
        assert isinstance(try_.error, ValueError)

    def test_map_transforms_value_on_success(self):
        """map should transform value on success."""
        try_ = Try.ok(5)
        result = try_.map(lambda x: x * 2)

        assert result.value == 10
        assert result.is_ok is True

    def test_map_returns_self_on_failure(self):
        """map should return self on failure."""
        error = ValueError("test")
        try_ = Try.err(error)
        result = try_.map(lambda x: x * 2)

        assert result.is_err is True
        assert result.error == error

    def test_flat_map_chains_on_success(self):
        """flat_map should chain Try-returning functions."""
        try_ = Try.ok(5)

        def double(x: int) -> Try[int]:
            return Try.ok(x * 2)

        result = try_.flat_map(double)
        assert result.value == 10

    def test_flat_map_returns_self_on_failure(self):
        """flat_map should return self on failure."""
        error = ValueError("test")
        try_ = Try.err(error)

        def double(x: int) -> Try[int]:
            return Try.ok(x * 2)

        result = try_.flat_map(double)
        assert result.is_err is True

    def test_recover_transforms_error_on_failure(self):
        """recover should transform error on failure."""
        error = ValueError("original")
        try_ = Try.err(error)

        def recover(e: Exception) -> str:
            return f"recovered: {e}"

        result = try_.recover(recover)
        assert result.is_ok is True
        assert result.value == "recovered: original"

    def test_recover_returns_self_on_success(self):
        """recover should return self on success."""
        try_ = Try.ok("value")

        def recover(e: Exception) -> str:
            return "recovered"

        result = try_.recover(recover)
        assert result.is_ok is True
        assert result.value == "value"

    def test_unwrap_returns_value_on_success(self):
        """unwrap should return value on success."""
        try_ = Try.ok("test")
        assert try_.unwrap() == "test"

    def test_unwrap_raises_error_on_failure(self):
        """unwrap should raise error on failure."""
        error = ValueError("test error")
        try_ = Try.err(error)

        with pytest.raises(ValueError):
            try_.unwrap()

    def test_map_catches_exception_when_func_raises(self):
        """map should catch exception when func raises."""
        try_ = Try.ok(5)

        def raising_func(x: int) -> int:
            raise ValueError("transform error")

        result = try_.map(raising_func)
        assert result.is_err is True
        assert isinstance(result.error, ValueError)

    def test_recover_catches_exception_when_func_raises(self):
        """recover should catch exception when recovery func raises."""
        error = ValueError("original error")
        try_ = Try.err(error)

        def recover_func(e: Exception) -> str:
            raise RuntimeError("recovery failed")

        result = try_.recover(recover_func)
        assert result.is_err is True
        assert isinstance(result.error, ValueError)

    def test_unwrap_raises_when_no_value_no_error(self):
        """unwrap should raise ValueError when no value and no error."""
        try_ = Try.ok(None)
        with pytest.raises(ValueError, match="no value"):
            try_.unwrap()
