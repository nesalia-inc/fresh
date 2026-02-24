# fresh

A CLI tool to fetch the latest documentation from any website in Markdown format.

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
# Show help
fresh --help

# List all documentation pages on a website
fresh list https://docs.python.org/3/

# Fetch a documentation page and convert to Markdown
fresh get https://docs.python.org/3/tutorial/

# Search for content across documentation pages
fresh search "virtual environment" https://docs.python.org/3/

# Manage aliases for quick access
fresh alias add python https://docs.python.org/3/
fresh alias list
fresh alias search python

# Download entire documentation for offline use
fresh sync https://docs.python.org/3/

# Check for updates
fresh update --check

# Show enhanced documentation for a command
fresh doc get
fresh doc list
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

### `fresh alias`
Manage library aliases for quick access.

```bash
# Add an alias
fresh alias add <name> <url>

# List all aliases
fresh alias list

# Remove an alias
fresh alias remove <name>

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

### `fresh update`
Check for and install updates to fresh.

```bash
fresh update [OPTIONS]
```

Options:
- `--check` - Only check for updates without installing
- `-y, --yes` - Automatically confirm updates

### `fresh doc`
Show enhanced documentation for fresh commands.

```bash
fresh doc [COMMAND]
```

## Configuration

Fresh stores its configuration in the following locations:
- Aliases: `~/.fresh/aliases.json`
- Cache: `~/.fresh/cache/`
- Sync data: `~/.fresh/docs/`

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

## License

MIT
