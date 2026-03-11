# Contributing to Fresh

Thank you for your interest in contributing to Fresh! This document provides guidelines for contributing.

## Quick Start

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/fresh.git`
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Make your changes
5. Run tests: `pytest`
6. Push and create a PR

## Development Setup

```bash
# Clone and install
git clone https://github.com/nesalia-inc/fresh.git
cd fresh

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[all]"
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Code Standards

### Formatting

- Line length: 100 characters max
- Use Ruff for linting: `ruff check .`
- Run formatting before commit: `ruff format .`

### Type Checking

- Use mypy for type checking: `mypy .`
- All new code should include type hints

### Testing

- Run all tests: `pytest`
- Run with coverage: `pytest --cov`
- Minimum coverage requirement: 80%

### Commit Messages

Follow conventional commits:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `refactor: restructure code`
- `test: add tests`

## Project Structure

```
fresh/
├── src/fresh/           # Main source code
│   ├── commands/        # CLI commands
│   ├── scraper/         # Web scraping modules
│   ├── config.py        # Configuration
│   └── indexer.py       # Search indexing
├── tests/               # Test suite
│   ├── test_commands/   # Command tests
│   └── test_scraper/    # Scraper tests
└── docs/                # Documentation
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Fill out the PR template completely

## Issue Types

Use the appropriate issue templates:
- **Bug Report** - For bugs and errors
- **Feature Request** - For new features
- **Documentation** - For docs improvements
- **Refactoring** - For code improvements
- **Security Issue** - For vulnerabilities (email support@nesalia.com)

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## Getting Help

- Open an issue for questions
- Join discussions in GitHub
- Email: support@nesalia.com

---

We appreciate all contributions, from bug reports to new features!