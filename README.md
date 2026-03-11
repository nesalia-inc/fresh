<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="public/logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="public/logo-light.png">
    <img src="public/logo.png" alt="Fresh Logo" width="100%">
  </picture>
</p>

<h1 align="center">Fresh</h1>

<p align="center">
  <a href="https://pypi.org/project/fresh-docs/">
    <img src="https://img.shields.io/pypi/v/fresh-docs" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/fresh-docs/">
    <img src="https://img.shields.io/pypi/dm/fresh-docs" alt="PyPI Downloads">
  </a>
  <a href="https://github.com/nesalia-inc/fresh/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/nesalia-inc/fresh/ci?label=tests" alt="Tests">
  </a>
  <a href="https://github.com/nesalia-inc/fresh/actions">
    <img src="https://img.shields.io/badge/coverage-80%25-yellow" alt="Coverage">
  </a>
  <a href="https://github.com/nesalia-inc/fresh/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/nesalia-inc/fresh" alt="License">
  </a>
  <a href="https://pepy.tech/projects/fresh-docs">
    <img src="https://pepy.tech/badge/fresh-docs/month" alt="Monthly Downloads">
  </a>
</p>

> A CLI tool to fetch the latest documentation from any website in Markdown format.

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

## Quick Start

```bash
# List all documentation pages on a website
fresh list https://docs.python.org/3/

# Fetch a documentation page and convert to Markdown
fresh get https://docs.python.org/3/tutorial/

# Search for content across documentation pages
fresh search "virtual environment" https://docs.python.org/3/

# Download entire documentation for offline use
fresh sync https://docs.python.org/3/

# Add an alias for quick access
fresh alias add python https://docs.python.org/3/
fresh list python
```

## Commands

### `fresh list`

List all documentation pages available on a website.

```bash
fresh list <URL> [OPTIONS]
```

Options:
- `-v, --verbose` - Use rich output format
- `-p, --pattern TEXT` - Filter paths matching pattern
- `-d, --depth INTEGER` - Maximum crawl depth (default: 3)
- `--max-pages INTEGER` - Maximum number of pages to discover (default: 100)
- `--sort TEXT` - Sort results by name or path
- `-f, --format TEXT` - Output format: json, yaml, xml
- `-c, --count` - Show only total count

### `fresh get`

Fetch a documentation page and convert it to Markdown.

```bash
fresh get <URL> [OPTIONS]
```

Options:
- `-v, --verbose` - Use verbose output
- `-t, --timeout INTEGER` - Request timeout in seconds (default: 30)
- `--header TEXT` - Custom HTTP header
- `--no-follow` - Do not follow redirects
- `--skip-scripts` - Exclude JavaScript from output
- `--no-cache` - Bypass cache
- `-o, --output TEXT` - Write output to file
- `-r, --retry INTEGER` - Number of retry attempts (default: 3)
- `--dry-run` - Show what would be fetched without downloading

### `fresh search`

Search for content across documentation pages.

```bash
fresh search <QUERY> <URL> [OPTIONS]
```

### `fresh websearch`

Search the general web for any topic.

```bash
# Basic search (uses DuckDuckGo HTML, free)
fresh websearch "python async tutorial"

# With specific number of results
fresh websearch "react hooks" --count 5

# Table output for human-readable display
fresh websearch "rust ownership" --table
```

Options:
- `-n, --count INTEGER` - Maximum number of results (default: 10)
- `-e, --engine TEXT` - Search engine: auto, ddg, brave (default: auto)
- `-j, --json` - Output as JSON (default)
- `-t, --table` - Output as table
- `-v, --verbose` - Show verbose output

**Note:** Brave Search API can be used by setting the `BRAVE_API_KEY` environment variable. DuckDuckGo is used by default (free, no API key required).

### `fresh alias`

Manage library aliases for quick access.

```bash
# Add an alias
fresh alias add <name> <url>

# List all aliases
fresh alias list

# Search aliases
fresh alias search <query>
```

### `fresh sync`

Download entire documentation for offline use.

```bash
fresh sync <URL> [OPTIONS]
```

Options:
- `-o, --output-dir PATH` - Target directory for synced docs
- `-v, --verbose` - Use verbose output
- `--max-pages INTEGER` - Maximum number of pages to sync (default: 100)
- `-d, --depth INTEGER` - Maximum crawl depth (default: 3)
- `-f, --force` - Force re-sync (delete existing files first)
- `-p, --pattern TEXT` - Filter paths matching pattern

### `fresh guide`

Manage personal guides and documentation.

```bash
# Create a new guide
fresh guide create my-guide --content "Guide content here" --title "My Guide"

# List all guides
fresh guide list

# Show a specific guide
fresh guide show my-guide

# Search across guides
fresh guide search "keyword"
```

## Configuration

Fresh stores its configuration in the following locations:
- Aliases: `~/.fresh/aliases.json`
- Cache: `~/.fresh/cache/`
- Sync data: `~/.fresh/docs/`
- History: `~/.fresh/history.db`

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run linter
ruff check .

# Run type checker
mypy src/

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

- **Nesalia Inc.**

## Security

If you discover any security vulnerabilities, please send an e-mail to support@nesalia.com.

## License

MIT License - see the [LICENSE](LICENSE) file for details.