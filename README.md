# fresh

A Python CLI application created with @nesalia/create.

## Requirements

- Python 3.12+
- uv (recommended) or pip

## Installation

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

## Usage

```bash
# Run the CLI
fresh --help

# Say hello
fresh hello --name World

# Run tests
pytest
```

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run linter
ruff check .

# Run tests
pytest
```
