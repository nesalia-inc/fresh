# Exception Design Guide - Fresh V2

This document outlines the exception strategy for Fresh V2. All exceptions follow a consistent hierarchy and naming convention.

---

## Table of Contents

1. [Types of Errors](#types-of-errors)
2. [Hierarchy](#hierarchy)
3. [Naming Convention](#naming-convention)
4. [Required Attributes](#required-attributes)
5. [Handling Exceptions](#handling-exceptions)
6. [Raising Exceptions](#raising-exceptions)
7. [Exception Chaining](#exception-chaining)
8. [Exception Groups](#exception-groups)
9. [Enriching Exceptions with Notes](#enriching-exceptions-with-notes)
10. [Clean-up Actions](#clean-up-actions)
11. [Existing Exceptions](#existing-exceptions)
12. [New Exceptions to Add](#new-exceptions-to-add)
13. [Usage with Try Monad](#usage-with-try-monad)

---

## Types of Errors

Python distinguishes between two types of errors:

### Syntax Errors
Errors detected during parsing (before execution). These must be fixed before code runs.

```python
while True print('Hello world')
# SyntaxError: invalid syntax
```

### Exceptions
Errors detected during execution. These can be handled gracefully.

```python
10 * (1/0)  # ZeroDivisionError
4 + spam*3  # NameError
'2' + 2     # TypeError
```

---

## Hierarchy

```
FreshError (base)
├── NetworkError
│   ├── FetchError
│   ├── TimeoutError
│   └── ConnectionError
├── ValidationError
│   ├── URLValidationError
│   ├── ConfigValidationError
│   └── InputValidationError
├── CacheError
│   ├── CacheReadError
│   ├── CacheWriteError
│   └── CacheExpiredError
├── SyncError
│   ├── SyncDiscoveryError
│   └── SyncWriteError
├── SearchError
│   ├── SearchQueryError
│   └── SearchIndexError
├── DiscoveryError
│   ├── SitemapError
│   └── CrawlerError
├── StorageError
│   └── FileWriteError
└── CLIError
```

---

## Naming Convention

Exceptions are named with the `Error` suffix. They represent **what went wrong**, not **who caused it**.

**Good:**
```python
class FetchError(NetworkError): ...
class CacheReadError(CacheError): ...
class URLValidationError(ValidationError): ...
```

**Bad:**
```python
class FetchException(Exception): ...      # "Exception" is redundant
class FetcherError(Exception): ...        # "er" suffix - not a noun
class FetchFailedError(Exception): ...     # Redundant "Failed"
class UrlInvalidException(Exception): ... # CamelCase violation
```

---

## Required Attributes

All exceptions should have:

1. **`code`** - Machine-readable error code for programmatic handling
2. **`message`** - Human-readable error message
3. **Domain attributes** - Relevant context (url, path, etc.)

```python
class FetchError(NetworkError):
    """Failed to fetch a URL."""

    code: str = "FETCH_ERROR"
    url: str
    reason: str

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        message = f"Failed to fetch {url}: {reason}"
        super().__init__(message=message, code=self.code)
```

---

## Handling Exceptions

Use `try/except` to handle exceptions gracefully. Always be as specific as possible with exception types.

**Good:**
```python
try:
    content = fetch(url)
except FetchError as e:
    logger.error(f"Failed to fetch {e.url}: {e.reason}")
except TimeoutError as e:
    logger.error(f"Timeout for {e.url}")
except NetworkError as e:
    logger.error(f"Network error: {e}")
```

**Bad:**
```python
try:
    content = fetch(url)
except Exception:  # Too broad!
    logger.error("Something went wrong")
```

### Multiple Exception Types

Handle multiple exception types with a tuple:

```python
try:
    content = fetch(url)
except (TimeoutError, ConnectionError) as e:
    logger.error(f"Connection failed: {e}")
```

### The else Clause

Use `else` for code that should run only if no exception occurs:

```python
try:
    content = fetch(url)
except NetworkError as e:
    logger.error(f"Failed: {e}")
else:
    # Only runs if no exception
    process(content)
```

---

## Raising Exceptions

Use `raise` to trigger exceptions. Always provide meaningful context.

### Basic Usage

```python
raise FetchError(url, "Connection refused")

# Or with shorthand (class, not instance)
raise ValueError  # Equivalent to raise ValueError()
```

### Re-raising Exceptions

Use bare `raise` to re-raise the current exception:

```python
try:
    content = fetch(url)
except NetworkError as e:
    logger.error(f"Network issue: {e}")
    raise  # Re-raises the same exception
```

---

## Exception Chaining

Use `from` to link exceptions - show that one exception caused another.

### Implicit Chaining

When an exception occurs during handling, Python automatically chains them:

```python
try:
    open("database.sqlite")
except OSError:
    raise RuntimeError("unable to handle error")
```

Output:
```
Traceback (most recent call last):
  File "...", line 2, in <module>
    open("database.sqlite")
FileNotFoundError: ...

During handling of the above exception, another exception occurred:
...
RuntimeError: unable to handle error
```

### Explicit Chaining

Use `raise ... from` to explicitly indicate causation:

```python
try:
    open_database()
except OSError as exc:
    raise RuntimeError("Failed to open database") from exc
```

### Disabling Chaining

Use `from None` to disable automatic chaining:

```python
try:
    open("database.sqlite")
except OSError:
    raise RuntimeError from None  # Hides the original
```

---

## Exception Groups

Python 3.11+ supports grouping multiple exceptions together. Useful for concurrent operations.

### Raising Exception Groups

```python
def batch_fetch(urls: list[str]) -> None:
    errors = []
    for url in urls:
        try:
            fetch(url)
        except NetworkError as e:
            errors.append(e)

    if errors:
        raise ExceptionGroup("Failed to fetch URLs", errors)
```

### Handling with except*

Use `except*` to selectively handle exceptions in a group:

```python
try:
    batch_fetch(urls)
except* TimeoutError as eg:
    print("Timeouts:", eg.exceptions)
except* FetchError as eg:
    print("Fetch errors:", eg.exceptions)
except ExceptionGroup as eg:
    print("Other errors:", eg)
```

**Note:** `except*` catches exceptions **by type**, not by instance. The matched exceptions are extracted from the group.

---

## Enriching Exceptions with Notes

Python 3.11+ supports adding notes to exceptions via `add_note()`. Useful for adding context.

```python
try:
    raise TypeError("bad type")
except Exception as e:
    e.add_note("Add some information")
    e.add_note("Add some more information")
    raise
```

Output:
```
TypeError: bad type
Add some information
Add some more information
```

### Use Case: Context in Exception Groups

```python
def process_items(items: list[str]) -> None:
    errors = []
    for i, item in enumerate(items):
        try:
            process(item)
        except Exception as e:
            e.add_note(f"Item at index {i}")
            errors.append(e)

    if errors:
        raise ExceptionGroup("Processing failed", errors)
```

---

## Clean-up Actions

Use `finally` for code that must execute regardless of whether an exception occurred.

### Basic Usage

```python
try:
    content = fetch(url)
except NetworkError as e:
    logger.error(f"Failed: {e}")
finally:
    # Always runs - close connections, files, etc.
    cleanup()
```

### The with Statement

Use context managers for automatic resource cleanup:

```python
# BAD - file may not be closed if exception occurs
f = open("file.txt")
content = f.read()
f.close()

# GOOD - automatically closed
with open("file.txt") as f:
    content = f.read()
```

---

## Existing Exceptions

These exceptions already exist in `src/fresh/exceptions.py`:

| Exception | Code | Description |
|-----------|------|-------------|
| `FreshError` | - | Base exception for all fresh errors |
| `NetworkError` | - | Network-related errors |
| `FetchError` | `FETCH_ERROR` | Failed to fetch a URL |
| `TimeoutError` | `TIMEOUT_ERROR` | Request timeout |
| `ValidationError` | - | Input validation errors |
| `AliasError` | - | Alias-related errors |
| `CacheError` | - | Cache-related errors |
| `SitemapError` | - | Sitemap parsing errors |
| `CrawlerError` | - | Crawler-related errors |
| `FilterError` | - | Filter-related errors |
| `ConfigError` | - | Configuration-related errors |
| `CLIError` | - | CLI-related errors |

---

## New Exceptions to Add

The following exceptions should be added to complete the hierarchy:

### Network

```python
class ConnectionError(NetworkError):
    """Failed to establish connection."""

    code: str = "CONNECTION_ERROR"
    url: str
    host: str

    def __init__(self, url: str, host: str):
        self.url = url
        self.host = host
        super().__init__(
            message=f"Failed to connect to {host}",
            code=self.code
        )


class RedirectError(NetworkError):
    """Too many redirects."""

    code: str = "REDIRECT_ERROR"
    url: str
    redirect_count: int

    def __init__(self, url: str, redirect_count: int):
        self.url = url
        self.redirect_count = redirect_count
        super().__init__(
            message=f"Too many redirects ({redirect_count}) for {url}",
            code=self.code
        )
```

### Validation

```python
class URLValidationError(ValidationError):
    """Invalid URL format."""

    code: str = "URL_INVALID"
    url: str

    def __init__(self, url: str):
        self.url = url
        super().__init__(
            message=f"Invalid URL: {url}",
            code=self.code
        )


class ConfigValidationError(ValidationError):
    """Invalid configuration."""

    code: str = "CONFIG_INVALID"
    field: str
    value: str

    def __init__(self, field: str, value: str, reason: str):
        self.field = field
        self.value = value
        super().__init__(
            message=f"Invalid config '{field}': {reason}",
            code=self.code
        )


class InputValidationError(ValidationError):
    """Invalid user input."""

    code: str = "INPUT_INVALID"
    input_name: str

    def __init__(self, input_name: str, reason: str):
        self.input_name = input_name
        super().__init__(
            message=f"Invalid input '{input_name}': {reason}",
            code=self.code
        )
```

### Cache

```python
class CacheReadError(CacheError):
    """Failed to read from cache."""

    code: str = "CACHE_READ_ERROR"
    key: str
    reason: str

    def __init__(self, key: str, reason: str):
        self.key = key
        self.reason = reason
        super().__init__(
            message=f"Cache read failed for {key}: {reason}",
            code=self.code
        )


class CacheWriteError(CacheError):
    """Failed to write to cache."""

    code: str = "CACHE_WRITE_ERROR"
    key: str
    reason: str

    def __init__(self, key: str, reason: str):
        self.key = key
        self.reason = reason
        super().__init__(
            message=f"Cache write failed for {key}: {reason}",
            code=self.code
        )


class CacheExpiredError(CacheError):
    """Cache entry has expired."""

    code: str = "CACHE_EXPIRED"
    key: str
    age_seconds: float

    def __init__(self, key: str, age_seconds: float):
        self.key = key
        self.age_seconds = age_seconds
        super().__init__(
            message=f"Cache expired for {key} after {age_seconds}s",
            code=self.code
        )
```

### Sync

```python
class SyncError(FreshError):
    """Base for sync-related errors."""
    pass


class SyncDiscoveryError(SyncError):
    """Failed to discover pages to sync."""

    code: str = "SYNC_DISCOVERY_ERROR"
    url: str

    def __init__(self, url: str, reason: str):
        self.url = url
        super().__init__(
            message=f"Discovery failed for {url}: {reason}",
            code=self.code
        )


class SyncWriteError(SyncError):
    """Failed to write synced content."""

    code: str = "SYNC_WRITE_ERROR"
    url: str
    path: Path

    def __init__(self, url: str, path: Path, reason: str):
        self.url = url
        self.path = path
        super().__init__(
            message=f"Failed to write {url} to {path}: {reason}",
            code=self.code
        )
```

### Search

```python
class SearchError(FreshError):
    """Base for search-related errors."""
    pass


class SearchQueryError(SearchError):
    """Invalid search query."""

    code: str = "SEARCH_QUERY_ERROR"
    query: str

    def __init__(self, query: str, reason: str):
        self.query = query
        super().__init__(
            message=f"Invalid search query '{query}': {reason}",
            code=self.code
        )


class SearchIndexError(SearchError):
    """Search index error."""

    code: str = "SEARCH_INDEX_ERROR"
    index_name: str

    def __init__(self, index_name: str, reason: str):
        self.index_name = index_name
        super().__init__(
            message=f"Search index error for {index_name}: {reason}",
            code=self.code
        )
```

### Storage

```python
class StorageError(FreshError):
    """Base for storage-related errors."""
    pass


class FileWriteError(StorageError):
    """Failed to write file."""

    code: str = "FILE_WRITE_ERROR"
    path: Path

    def __init__(self, path: Path, reason: str):
        self.path = path
        super().__init__(
            message=f"Failed to write {path}: {reason}",
            code=self.code
        )


class FileReadError(StorageError):
    """Failed to read file."""

    code: str = "FILE_READ_ERROR"
    path: Path

    def __init__(self, path: Path, reason: str):
        self.path = path
        super().__init__(
            message=f"Failed to read {path}: {reason}",
            code=self.code
        )


class DirectoryCreateError(StorageError):
    """Failed to create directory."""

    code: str = "DIR_CREATE_ERROR"
    path: Path

    def __init__(self, path: Path, reason: str):
        self.path = path
        super().__init__(
            message=f"Failed to create directory {path}: {reason}",
            code=self.code
        )
```

---

## Philosophy: Errors as Values

The core principle: **Never raise exceptions in core business logic. Return them as values.**

### The Problem with Early Raising

```python
# BAD - raises immediately, caller has no choice
def fetch(url: str) -> str:
    if not validate(url):
        raise ValidationError(f"Invalid URL: {url}")  # Forces handling here
    response = requests.get(url)
    if response.status_code != 200:
        raise FetchError(url, response.status_code)  # Forces handling here
    return response.text
```

### The Solution: Return Errors

```python
# GOOD - returns Result, caller decides when to handle
def fetch(url: str) -> Result[str]:
    if not validate(url):
        return Result.failure(URLValidationError(url))
    response = requests.get(url)
    if response.status_code != 200:
        return Result.failure(FetchError(url, response.status_code))
    return Ok(response.text)
```

### Why This Matters

1. **Testability** - No exception handling needed in tests
2. **Composability** - Chain operations without try/except
3. **Control** - Caller decides when/where to handle
4. **Multiple Errors** - Collect all errors before failing
5. **Type Safety** - Return type tells you exactly what can go wrong

---

## Usage with Try Monad

Exceptions integrate naturally with the `Try` monad for clean error handling:

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Try(Generic[T]):
    value: T | None = None
    error: Exception | None = None

    # Try.of wraps a function that may throw - use as regular method
    @classmethod
    def capture(cls, func: Callable[[], T]) -> "Try[T]":
        """Capture exceptions from a function call."""
        try:
            return cls(value=func())
        except Exception as e:
            return cls(error=e)

    # ... other methods

# Usage
result = Try.capture(lambda: fetch(url))
if result.is_failure:
    logger.error(f"Failed: {result.error}")
```

---

## Complete Flow: Core to CLI

The complete error handling flow in Fresh V2:

### Layer 1: Core (Pure Business Logic)

Never raise. Always return `Result` or `Try`:

```python
# core/get.py - NEVER raises
# IMPORTANT: Error types are EXPLICIT in the return type
def fetch(url: str) -> Result[Webpage, URLValidationError | FetchError | TimeoutError]:
    # All errors returned as Result
    if not validate(url):
        return Result.failure(URLValidationError(...))
    if cached := get_cached(url):
        return Ok(Webpage(content=cached))
    response = http_get(url)
    if not response:
        return Result.failure(FetchError(...))
    return Ok(Webpage(content=response))
```

**Why explicit error types matter:**
- IDE autocomplete shows all possible errors
- Type checker verifies all cases are handled
- Documentation is embedded in the type signature

### Result Type Definition

The `Result` type should be defined with two type parameters:

```python
from typing import TypeVar, Generic, Union

T = TypeVar('T')  # Success type
E = TypeVar('E')  # Error type

@dataclass
class Result(Generic[T, E]):
    """Represents success (T) or failure (E)."""
    ok: bool
    value: T | None = None
    error: E | None = None

    # Concise alternative constructors
    @classmethod
    def ok(cls, value: T) -> "Result[T, E]":
        """Create a successful result."""
        return cls(ok=True, value=value)

    @classmethod
    def err(cls, error: E) -> "Result[T, E]":
        """Create a failed result."""
        return cls(ok=False, error=error)
```

**Usage with union types:**
```python
from collections.abc import Sequence

# Specific errors as union
def fetch(url: str) -> Result[Webpage, URLValidationError | FetchError | TimeoutError]:
    ...

# Use Sequence for immutable return types (prevents caller mutation)
def sync(urls: list[str]) -> Result[Sequence[Webpage], ExceptionGroup]:
    # ExceptionGroup wraps multiple errors
    results: list[Webpage] = []
    ...
    return Ok(tuple(results))  # tuple is immutable
```

**Why Sequence instead of list:**
- `list` is mutable - caller can modify it
- `Sequence` (or `tuple`) is immutable - guarantees no mutation
- Better for API contracts - what you return is what they get

### Layer 2: Entities (Orchestration)

Chain operations, collect errors:

```python
# core/entities/sync.py
def sync(urls: list[str]) -> Result[Sequence[Webpage], ExceptionGroup]:
    # Errors propagate through - ExceptionGroup contains all failures
    errors: list[FreshError] = []
    results: list[Webpage] = []

    for url in urls:
        match fetch(url):
            case Result(ok=True, value=page):
                results.append(page)
            case Result(ok=False, error=e):
                errors.append(e)

    if errors:
        # Return ALL errors, not just the first
        return Result.failure(ExceptionGroup("Sync failed", errors))

    return Ok(tuple(results))
```

### Layer 3: Commands (CLI Layer - ONLY HERE we raise)

At the boundary between CLI and core, handle or raise:

```python
# commands/get.py
@app.command()
def get(url: str):
    result = Get().fetch(url)

    # Use match/case for flow control - explicit handling
    match result:
        case Result(ok=False, error=err):
            echo_error(err)
            raise typer.Exit(1)
        case Result(ok=True, value=page):
            typer.echo(page.content)
```

---

## Never Lose an Error

### Collecting Multiple Errors

```python
# BAD - loses all errors after first failure
def sync(urls: list[str]) -> list[Webpage]:
    results = []
    for url in urls:
        results.append(fetch(url))  # Raises on first error!
    return results

# GOOD - collects ALL errors
def sync(urls: list[str]) -> Result[Sequence[Webpage], ExceptionGroup]:
    errors: list[FreshError] = []
    results: list[Webpage] = []

    for url in urls:
        result = fetch(url)  # Returns Result, not raises
        match result:
            case Ok(page):
                results.append(page)
            case Err(e):
                errors.append(e)  # Collect, don't lose!

    if errors:
        return Result.failure(
            ExceptionGroup(f"{len(errors)} errors", errors)
        )

    return Ok(results)
```

### Use ExceptionGroup for Multiple Errors

```python
# Collecting multiple failures
errors: list[FreshError] = []
for item in items:
    try:
        process(item)
    except FreshError as e:
        errors.append(e)

if errors:
    raise ExceptionGroup(f"Failed to process {len(errors)} items", errors)
```

---

## Best Practices Summary

### Design Principles

| Principle | Rule |
|-----------|------|
| Suffix | Always `Error` |
| Base | All inherit from `FreshError` |
| Attributes | Always include `code` and `message` |
| Context | Add domain-specific attributes (url, path, etc.) |
| Hierarchy | More specific exception for more specific errors |

### Handling Principles

| Principle | Rule |
|-----------|------|
| Specificity | Catch the most specific exception possible |
| No Bare Except | Never use `except:` without type |
| Re-raise | Use bare `raise` to preserve stack trace |
| Chain | Use `raise ... from` to show causation |
| Clean-up | Use `finally` or `with` for resources |
| Notes | Use `add_note()` for context (Python 3.11+) |

### Error Flow Principles (V2)

| Principle | Rule |
|-----------|------|
| Core = No Raise | Never `raise` in core/entities - return `Result` |
| CLI = Raise | Only raise at CLI boundary (commands/) |
| Never Lose Error | Use `ExceptionGroup` for multiple errors |
| Type Everything | Return types must show all error cases |
| Match for Flow | Use `match/case` for Result handling |

### Error Codes

Always define machine-readable codes for programmatic handling:

```python
class FetchError(NetworkError):
    code: str = "FETCH_ERROR"  # Class attribute for easy access

# Usage
if isinstance(e, FreshError):
    handle_error_code(e.code)  # Programmatic handling
```

---

*Last updated: 2026-03-02*
*Version: 1.1*
