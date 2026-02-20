# Future Features

This document outlines potential features for future releases.

## Core Features

### Sitemap Parsing
Use website sitemaps for more reliable page discovery in `list` command, instead of relying solely on HTML scraping.

### Retry & Rate Limiting
Automatic retry with exponential backoff and rate limiting to avoid getting blocked by websites.

### Config File
Support for `~/.freshrc` configuration file to remember frequently accessed sites and default settings.

### Custom Output Path
`--output /path/to/save` flag to choose where to save downloaded documentation.

### Format Choice
`--format md` (default), but also support HTML or JSON output formats.

### Diff Mode
`--diff` flag to see what has changed since the last fetch.

### Parallel Fetching
Multi-threaded fetching to download multiple pages simultaneously for better performance.

### Proxy Support
`--proxy http://...` flag to route requests through a proxy for sites that block scraping.

### Verbose Mode
`-v` flag for detailed debug output when something doesn't work.

## Nice to Have

### Watch Mode
`fresh watch <url>` command to monitor a documentation site and notify when changes occur.

### Plugins
Plugin system to add custom extractors for specific websites with unique structures.

### CI Integration
CI-friendly output to verify if documentation has changed between builds.

### Version Pinning
Ability to lock documentation to a specific date or version.

## Implementation Priority

1. **Sitemap parsing** - Improves reliability of `list` command
2. **Retry + rate limiting** - Essential for production use
3. **Config file** - Better UX for repeated use
4. **Output path custom** - Common need
5. **Format choice** - Depends on use case
6. **Diff mode** - Very useful for change tracking
7. **Parallel fetching** - Performance optimization
8. **Proxy support** - Edge case but important when needed
9. **Verbose mode** - Debugging tool
10. **Watch mode** - Advanced feature
11. **Plugins** - Only if needed for specific sites
12. **CI integration** - Niche use case
13. **Version pinning** - Low priority for MVP
