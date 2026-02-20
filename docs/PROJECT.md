# Fresh - Documentation Fetcher CLI

Agent-first CLI to get the latest and freshest documentation from any website in Markdown format.

## ⚠️ Work in Progress

This project is currently under development. Features and API may change.

## Purpose

This CLI scrapes documentation websites and converts pages to Markdown, making it easy to keep documentation fresh and accessible for AI agents.

## Commands

### `fresh list <url>`

Lists all documentation pages available on a given website.

```bash
fresh list https://nextjs.org
# Output: /docs /api-reference /guides /tutorials ...
```

### `fresh get <url>`

Fetches a specific documentation page and outputs it in Markdown format.

```bash
fresh get https://nextjs.org/docs/app/api-reference/file-conventions/page
# Output: # Page API Reference\ncontent...
```

## Features

- **Documentation discovery**: Automatically find all doc pages on a website
- **Markdown output**: Convert HTML documentation pages to clean Markdown
- **Public sources only**: Works with publicly accessible documentation sites
- **Implicit cache**: Pages are cached automatically. Use `--no-cache` to bypass
- **Flexible output**: Write to file or output to STDOUT

## Use Cases

- Keep local documentation updated for offline access
- Feed documentation to AI agents for context-aware assistance
- Quickly explore the structure of unfamiliar documentation sites

## Technical Stack

- **Language**: Python
- **CLI Framework**: Typer
- **Package Manager**: uv
- **License**: MIT
