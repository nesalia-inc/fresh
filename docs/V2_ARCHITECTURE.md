# Fresh V2 Architecture Guide

This document outlines the architectural principles and refactoring strategy for Fresh V2. The primary goal is to **minimize branching** throughout the codebase, replacing complex conditional logic with cleaner, more maintainable patterns.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Problem Analysis](#problem-analysis)
3. [Elimination Strategies](#elimination-strategies)
4. [Implementation Plan](#implementation-plan)
5. [Patterns Reference](#patterns-reference)

---

## Core Principles

### 1. Everything is an Entity

Instead of monolithic functions that do everything, the codebase should be organized around entities that encapsulate related behavior.

**Before:**
```python
def get(url, verbose=False, local=False, remote=False, ...):
    # 200+ lines mixing URL resolution, fetching, caching, output
```

**After:**
```python
@dataclass
class GetConfig:
    url: str
    source: SourceMode
    output: OutputMode
    # ...

class GetEntity:
    def execute(self, config: GetConfig) -> Webpage:
        # Clean, focused logic
```

### 2. Separation of Concerns

- **commands/** = Presentation only (Typer, formatting, user interaction)
- **core/** = Pure business logic (no Typer, no console output)

### 3. No Duplication

Every concept should have exactly one implementation. Magic numbers and strings must become constants.

### 4. Strict Typing

Use protocols, literals, enums, and type hints to make the code self-documenting and catch errors at compile time.

### 5. Entity-Oriented Naming

Class names should represent **what they are**, not what they do. Avoid suffixes like `Handler`, `Manager`, `Service`, `Factory`, `Provider`, `Helper`, `Util`.

**Good:**
```python
class Output: ...
class Verbose(Output): ...
class Spinner(Output): ...
class Cache: ...
class Fetch: ...
class Sync: ...
```

**Bad:**
```python
class OutputHandler: ...      # "Handler" is unnecessary
class OutputManager: ...      # "Manager" is unnecessary
class CacheService: ...       # "Service" is unnecessary
class FetchHelper: ...        # "Helper" is unnecessary
class ResultFactory: ...      # "Factory" is unnecessary
```

**Rationale:** Entities represent concepts. The suffix adds no semantic value and makes names longer.

---

## Problem Analysis

### Branching Categories Found

| Category | Occurrences | Impact |
|----------|-------------|--------|
| Output mode (verbose/interactive/silent) | ~10 | High |
| Configuration options | ~15 | High |
| Format handling (json/yaml/xml) | ~8 | Medium |
| Duration thresholds | ~4 | Low |
| Data source (local/cache/remote) | ~5 | High |
| Null checking | ~20 | Already using guard clauses |
| Error handling | ~10 | Medium |

### Most Problematic Functions

| Function | Lines | Branches | Issue |
|----------|-------|----------|-------|
| `search_pages()` (search.py) | 220 | 10+ | Multiple responsibilities |
| `sync()` (sync.py) | 250 | 8+ | Triple output mode branching |
| `fetch_single_url()` (get.py) | 165 | 6+ | Source resolution logic |
| `list_urls()` (list.py) | 210 | 5+ | Mixed discovery/output |
| `_format_age()` (history.py) | 16 | 6 | Time threshold branches |

---

## Elimination Strategies

### 1. Output Strategy Pattern

**Problem:**
```python
if verbose:
    typer.echo("Loading...")
    result = do_work()
elif is_interactive():
    with spinner("Loading..."):
        result = do_work()
else:
    result = do_work()
```

This pattern repeats 10+ times across the codebase.

**Solution:**
```python
from abc import ABC, abstractmethod
from typing import Protocol

class Output(Protocol):
    """Protocol for output rendering - entities, not handlers."""
    def progress(self, message: str) -> None: ...
    def success(self, result: "Result") -> None: ...
    def error(self, message: str) -> None: ...

class Verbose(Output):
    def progress(self, message: str) -> None:
        print(f"[...] {message}")

    def success(self, result: "Result") -> None:
        print(f"[OK] {result}")

    def error(self, message: str) -> None:
        print(f"[ERROR] {message}")

class Spinner(Output):
    def progress(self, message: str) -> None:
        self._spinner = Halo(text=message)
        self._spinner.start()

    def success(self, result: "Result") -> None:
        if self._spinner:
            self._spinner.succeed()

class Silent(Output):
    def progress(self, message: str) -> None:
        pass  # No output

    def success(self, result: "Result") -> None:
        pass
```

**Usage:**
```python
def __init__(self, output: Output):
    self._output = output

def execute(self):
    self._output.progress("Loading...")
    result = self._do_work()
    self._output.success(result)
```

**Result:** Eliminates ~100 lines of duplicate branching.

---

### 2. Result Monad

**Problem:**
```python
result = fetch(url)
if result is True:
    success_count += 1
elif result is None:  # Binary file skipped
    skipped_count += 1
else:
    fail_count += 1
```

**Solution:**
```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Literal

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """Represents the outcome of an operation."""
    status: Literal["success", "failure", "skipped"]
    data: T | None = None
    error: str | None = None

    # Concise alternative constructors
    @classmethod
    def ok(cls, data: T) -> "Result[T]":
        return cls(status="success", data=data)

    @classmethod
    def err(cls, error: str) -> "Result[T]":
        return cls(status="failure", error=error)

    @classmethod
    def skip(cls, reason: str) -> "Result[T]":
        return cls(status="skipped", error=reason)

    @property
    def is_ok(self) -> bool:
        return self.status == "success"
```

**Usage:**
```python
results = [fetch(url) for url in urls]
stats = {
    "success": sum(1 for r in results if r.status == "success"),
    "skipped": sum(1 for r in results if r.status == "skipped"),
    "failed": sum(1 for r in results if r.status == "failure"),
}
```

---

### 3. Maybe Monad

**Problem:**
```python
content = get_local(url)
if content is not None:
    return process(content)
return None
```

**Solution:**
```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar('T')
U = TypeVar('U')

@dataclass
class Maybe(Generic[T]):
    """Represents a value that may or may not exist."""
    value: T | None

    # Alternative constructors - concise names
    @classmethod
    def some(cls, value: T) -> "Maybe[T]":
        """Create Maybe with a value."""
        return cls(value)

    @classmethod
    def none(cls) -> "Maybe[T]":
        """Create Maybe with no value."""
        return cls(None)

    def map(self, func: Callable[[T], U]) -> "Maybe[U]":
        """Apply function if value exists."""
        if self.value is not None:
            return self.some(func(self.value))
        return self.none()

    def flat_map(self, func: Callable[[T], "Maybe[U]"]) -> "Maybe[U]":
        """Chain Maybe-returning functions."""
        if self.value is not None:
            return func(self.value)
        return self.none()

    def get_or(self, default: T) -> T:
        """Return value or default."""
        return self.value if self.value is not None else default

    def get_or_raise(self, error: str) -> T:
        """Return value or raise exception."""
        if self.value is None:
            raise ValueError(error)
        return self.value

    @property
    def is_just(self) -> bool:
        return self.value is not None

    @property
    def is_nothing(self) -> bool:
        return self.value is None
```

**Usage:**
```python
# Before
content = get_local(url)
if content is not None:
    return html_to_markdown(content)
return None

# After - chain operations without branches
result = (
    Some(url)
    .flat_map(get_local)
    .map(html_to_markdown)
)
```

---

### 4. Try Monad

**Problem:**
```python
try:
    content = fetch(url)
    return process(content)
except TimeoutException as e:
    return error_handler(e)
except ConnectionError as e:
    return error_handler(e)
except Exception as e:
    return fallback(e)
```

**Solution:**
```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

@dataclass
class Try(Generic[T]):
    """Represents a computation that may fail."""
    value: T | None = None
    error: Exception | None = None

    # Alternative constructors - regular methods
    @classmethod
    def capture(cls, func: Callable[[], T]) -> "Try[T]":
        """Capture exceptions from a function call."""
        try:
            return cls(value=func())
        except Exception as e:
            return cls(error=e)

    @classmethod
    def ok(cls, value: T) -> "Try[T]":
        """Create a successful Try."""
        return cls(value=value)

    @classmethod
    def err(cls, error: Exception) -> "Try[T]":
        """Create a failed Try."""
        return cls(error=error)

    def map(self, func: Callable[[T], T]) -> "Try[T]":
        """Apply function if success."""
        if self.is_success:
            try:
                return self.__class__(value=func(self.value))
            except Exception as e:
                return self.__class__(error=e)
        return self

    def flat_map(self, func: Callable[[T], "Try[T]"]) -> "Try[T]":
        """Chain Try-returning functions."""
        if self.is_success and self.value is not None:
            return func(self.value)
        return self

    def recover(self, func: Callable[[Exception], T]) -> "Try[T]":
        """Recover from error."""
        if self.is_failure:
            try:
                return Try(value=func(self.error))
            except Exception:
                return self
        return self

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_failure(self) -> bool:
        return self.error is not None

    def get_or_raise(self) -> T:
        """Return value or re-raise exception."""
        if self.is_failure and self.error:
            raise self.error
        return self.value
```

**Usage:**
```python
# Before
try:
    content = fetch(url)
except TimeoutException:
    content = fetch_backup(url)
except Exception:
    content = None

# After
result = (
    Try.of(lambda: fetch(url))
    .recover(lambda e: fetch_backup(url) ifException) else None isinstance(e, Timeout)
)
```

**Key Principle:** `Try.of()` catches exceptions and converts them to values. The caller decides when to call `get_or_raise()`. In core/entities, never call `get_or_raise()` - always return the `Try`.

---

### 6. Configuration Objects

**Problem:**
```python
if fresh:
    source = "remote"
elif local:
    source = "local"
elif remote:
    source = "remote"
else:
    source = "auto"
```

**Solution:**
```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class SourceConfig:
    mode: Literal["local", "remote", "auto"]
    force: bool = False

    @classmethod
    def from_flags(cls, fresh: bool = False, local: bool = False, remote: bool = False) -> "SourceConfig":
        if fresh:
            return cls(mode="remote", force=True)
        if local:
            return cls(mode="local")
        if remote:
            return cls(mode="remote")
        return cls(mode="auto")
```

**Usage:**
```python
config = SourceConfig.from_flags(fresh=fresh, local=local, remote=remote)
# Use config.mode and config.force throughout
```

---

### 7. Dictionary Dispatch

**Problem:**
```python
if format == "json":
    output = json.dumps(data, indent=2)
elif format == "yaml":
    output = yaml.dump(data)
elif format == "xml":
    output = xmltodict.unparse({"root": data})
```

**Solution:**
```python
from typing import Callable

Formatter = Callable[[list[dict]], str]

FORMATTERS: dict[str, Formatter] = {
    "json": lambda data: json.dumps(data, indent=2),
    "yaml": lambda data: yaml.dump(data),
    "xml": lambda data: xmltodict.unparse({"items": {"item": data}}),
    "text": lambda data: "\n".join(str(x) for x in data),
}

# Usage - ZERO branches
output = FORMATTERS[format](data)
```

---

### 8. Threshold Tables

**Problem:**
```python
if seconds < 60:
    return f"{int(seconds)}s"
elif seconds < 3600:
    return f"{int(seconds/60)}m"
elif seconds < 86400:
    return f"{int(seconds/3600)}h"
elif seconds < 2592000:  # 30 days
    return f"{int(seconds/86400)}d"
else:
    return f"{int(seconds/31536000)}y"
```

**Solution:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TimeThreshold:
    seconds: int
    suffix: str
    divisor: int

THRESHOLDS = (
    TimeThreshold(60, "s", 1),
    TimeThreshold(3600, "m", 60),
    TimeThreshold(86400, "h", 3600),
    TimeThreshold(2592000, "d", 86400),
    TimeThreshold(31536000, "mo", 2592000),
)

def format_relative_time(seconds: float) -> str:
    for threshold in THRESHOLDS:
        if seconds < threshold.seconds:
            return f"{int(seconds // threshold.divisor)}{threshold.suffix}"
    return f"{int(seconds // 31536000)}y"
```

---

### 9. Pipeline/Chain Pattern

**Problem:**
```python
# Source resolution with nested branches
if not skip_local and local_exists(url):
    content = get_local(url)
elif not use_local and cached(url):
    content = get_cached(url)
else:
    content = fetch_remote(url)
```

**Solution:**
```python
from typing import Protocol

class ContentSource(Protocol):
    """Protocol for fetching content from various sources."""
    def can_provide(self, context: "FetchContext") -> bool: ...
    def fetch(self, context: "FetchContext") -> Webpage | None: ...

@dataclass
class FetchContext:
    url: str
    skip_cache: bool = False
    force_remote: bool = False

class LocalSource:
    def can_provide(self, context: FetchContext) -> bool:
        return not context.force_remote and local_exists(context.url)

    def fetch(self, context: FetchContext) -> Webpage | None:
        content = get_local(context.url)
        return Webpage(url=context.url, content=content, success=True) if content else None

class CacheSource:
    def can_provide(self, context: FetchContext) -> bool:
        return not context.skip_cache

    def fetch(self, context: FetchContext) -> Webpage | None:
        content = get_cached(context.url)
        return Webpage(url=context.url, content=content, success=True) if content else None

class RemoteSource:
    def can_provide(self, context: FetchContext) -> bool:
        return True  # Always can provide as fallback

    def fetch(self, context: FetchContext) -> Webpage:
        return fetch_remote(context.url)

# Usage - clean pipeline
sources: list[ContentSource] = [LocalSource(), CacheSource(), RemoteSource()]
for source in sources:
    if source.can_provide(context):
        return source.fetch(context)
```

---

## Implementation Plan

### Phase 1: Foundations

1. Create `core/constants.py`
   - All magic numbers/strings
   - Enum for common options

2. Create `core/types.py`
   - Protocol definitions
   - Result class
   - Literal types

### Phase 2: Core Refactoring

1. Extract output handlers → `core/output.py`
2. Create formatters registry → `core/formatters.py`
3. Create discovery service → `core/discovery.py`

### Phase 3: Command Refactoring

1. `get.py` - Use Webpage, clean fetch pipeline
2. `list.py` - Use formatter registry, output handler
3. `search.py` - Split search_pages(), use config objects
4. `sync.py` - Use output handler, result monad

---

## Patterns Reference

### Quick Reference Table

| Pattern | Before Branches | After Branches | Lines Saved |
|---------|----------------|----------------|-------------|
| Output | 3 | 0 | ~100 |
| Result | 3+ | 0 | ~30 |
| Maybe | 3+ | 0 | ~20 |
| Try | 3+ | 0 | ~25 |
| Config Objects | 4+ | 0 | ~20 |
| Dictionary Dispatch | 3+ | 0 | ~40 |
| Threshold Tables | 5+ | 0 | ~15 |
| Pipeline/Chain | 3+ | 0 | ~25 |

### Anti-Patterns to Avoid

```python
# BAD: Nested ternary
result = a if b else c if d else e

# BAD: Overly generic types
def process(x):  # No type hints
    ...

# BAD: Magic numbers
if status == 1:  # What is 1?
    ...

# BAD: Swallow exceptions
try:
    dangerous()
except:
    pass  # Never do this
```

---

## Summary

The V2 refactoring aims to:

1. **Reduce branching by ~80%** through strategic pattern application
2. **Achieve single responsibility** for every function and class
3. **Enable testability** through protocols and dependency injection
4. **Improve maintainability** with strict typing and constants

The key insight: **branching is a code smell**. Every `if` should be questioned - can it be replaced with:
- A lookup table?
- A configuration object?
- A strategy?
- An early return (guard clause)?

---

*Last updated: 2026-03-02*
*Version: 1.0*
