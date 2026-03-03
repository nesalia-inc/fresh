"""Core types for functional programming patterns.

These types help minimize branching by providing Result, Maybe, and Try
monads for explicit error handling without exceptions in core business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", bound=Exception)


@dataclass
class Result(Generic[T, E]):
    """Represents success (T) or failure (E).

    This is the primary error handling mechanism in Fresh V2.
    Core business logic should NEVER raise exceptions - instead,
    always return Result.
    """

    _success: bool
    value: T | None = None
    error: E | None = None

    @classmethod
    def Ok(cls, value: T) -> Result[T, E]:
        """Create a successful result."""
        return cls(_success=True, value=value)

    @classmethod
    def Err(cls, error: E) -> Result[T, E]:
        """Create a failed result."""
        return cls(_success=False, error=error)

    @property
    def ok(self) -> bool:
        """Check if result is successful."""
        return self._success

    @property
    def is_ok(self) -> bool:
        """Check if result is successful."""
        return self._success

    @property
    def is_err(self) -> bool:
        """Check if result is an error."""
        return not self._success

    def unwrap(self) -> T:
        """Get value or raise."""
        if self._success and self.value is not None:
            return self.value
        raise self.error if self.error else ValueError("Result has no value")

    def unwrap_or(self, default: T) -> T:
        """Get value or return default."""
        if self.ok:
            return self.value if self.value is not None else default
        return default


@dataclass
class Maybe(Generic[T]):
    """Represents an optional value (may or may not exist).

    Use this instead of None checks to make absence explicit.
    """

    value: T | None

    @classmethod
    def some(cls, value: T) -> Maybe[T]:
        """Create Maybe with a value."""
        return cls(value=value)

    @classmethod
    def none(cls) -> Maybe[T]:
        """Create Maybe with no value."""
        return cls(value=None)

    @classmethod
    def from_optional(cls, value: T | None) -> Maybe[T]:
        """Create Maybe from optional value."""
        return cls(value=value)

    def map(self, func: Callable[[T], U]) -> Maybe[U]:
        """Apply function if value exists."""
        if self.value is not None:
            return Maybe(func(self.value))  # type: ignore[arg-type]
        return Maybe(None)  # type: ignore[arg-type]

    def flat_map(self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain Maybe-returning functions."""
        if self.value is not None:
            return func(self.value)
        return Maybe(None)  # type: ignore[arg-type]

    def get_or(self, default: T) -> T:
        """Return value or default."""
        return self.value if self.value is not None else default

    @property
    def is_some(self) -> bool:
        """Check if has a value."""
        return self.value is not None

    @property
    def is_none(self) -> bool:
        """Check if has no value."""
        return self.value is None


@dataclass
class Try(Generic[T]):
    """Represents a computation that may fail with an exception.

    Use this to wrap functions that may throw, converting exceptions
    to values that can be handled explicitly.
    """

    value: T | None = None
    error: Exception | None = None

    @classmethod
    def capture(cls, func: Callable[[], T]) -> Try[T]:
        """Capture exceptions from a function call."""
        try:
            return cls(value=func())
        except Exception as e:
            return cls(error=e)

    @classmethod
    def ok(cls, value: T) -> Try[T]:
        """Create a successful Try."""
        return cls(value=value)

    @classmethod
    def err(cls, error: Exception) -> Try[T]:
        """Create a failed Try."""
        return cls(error=error)

    @property
    def is_ok(self) -> bool:
        """Check if Try is successful."""
        return self.error is None

    @property
    def is_err(self) -> bool:
        """Check if Try has an error."""
        return self.error is not None

    def map(self, func: Callable[[T], T]) -> Try[T]:
        """Apply function if success."""
        if self.is_ok and self.value is not None:
            try:
                return self.__class__(value=func(self.value))
            except Exception as e:
                return self.__class__(error=e)
        return self

    def flat_map(self, func: Callable[[T], Try[T]]) -> Try[T]:
        """Chain Try-returning functions."""
        if self.is_ok and self.value is not None:
            return func(self.value)
        return self

    def recover(self, func: Callable[[Exception], T]) -> Try[T]:
        """Recover from error."""
        if self.is_err and self.error:
            try:
                return self.__class__(value=func(self.error))
            except Exception:
                return self
        return self

    def unwrap(self) -> T:
        """Get value or raise."""
        if self.is_ok and self.value is not None:
            return self.value
        if self.error:
            raise self.error
        raise ValueError("Try has no value")


# Type aliases for common usage
WebpageResult = Result[Any, Exception]
FetchResult = Result[Any, Exception]
