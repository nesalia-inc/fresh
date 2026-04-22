# Fresh CLI

Command-line interface for Fresh - AI-powered web research and search.

## Installation

```bash
npm install -g @fresh/cli
# or
brew install fresh-cli
# or
curl -fsSL https://get.fresh.dev | bash
```

## Authentication

Fresh uses the OAuth 2.0 Device Authorization Flow (RFC 8628), ideal for CLI applications.

### fresh auth login

Start the device authorization flow:

```bash
fresh auth login
```

**Flow:**

```
1. CLI requests device code from server
2. CLI displays verification URL and user code
3. User visits URL and enters code
4. CLI polls for token until authorized
5. Token saved to config
```

**Example:**

```bash
$ fresh auth login
To authenticate, visit:
  https://fresh.dev/device
And enter code: XXXX-XXXX

Waiting for authorization...
✓ Authenticated successfully
```

### fresh auth logout

Revoke current session and clear credentials:

```bash
fresh auth logout
```

### fresh auth status

Check authentication status:

```bash
$ fresh auth status
✓ Authenticated as user@example.com
  Token: valid (expires in 23h)
  Plan: Pro
```

### API Key (Alternative)

You can also set your API key directly via environment variable:

```bash
export FRESH_API_KEY=your-api-key
```

Or in `~/.fresh/config.json`:

```json
{
  "apiKey": "your-api-key"
}
```

Get your API key at [https://fresh.dev](https://fresh.dev).

## Global Options

These options are available for all commands:

| Flag | Description |
|------|-------------|
| `--help, -h` | Show help for a command |
| `--version, -v` | Show CLI version |
| `--api-key <key>` | Use specific API key |
| `--base-url <url>` | API base URL (for self-hosting) |
| `--quiet, -q` | Suppress non-essential output |
| `--output-format <type>` | Default output format: `json`, `markdown`, `text` |

## Commands

- [fresh search](#fresh-search) - Web search
- [fresh fetch](#fresh-fetch) - Content extraction from URLs
- [fresh ask](#fresh-ask) - AI question answering
- [fresh research](#fresh-research) - Deep multi-branch research

---

## fresh search

Perform web searches powered by Exa.ai.

### Synopsis

```bash
fresh search <query> [options]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--type <type>` | Search type: `auto`, `fast`, `deep-lite`, `deep`, `deep-reasoning`, `instant` | `auto` |
| `--num-results, -n <n>` | Number of results | `10` |
| `--highlight-query <q>` | Query for relevant highlights | - |
| `--text-max <n>` | Max characters per text result | `1000` |
| `--format, -f <type>` | Output format: `json`, `markdown`, `text` | `json` |

### Examples

```bash
# Basic search
fresh search "hottest AI startups 2024"

# Deep research search
fresh search "Impact of AI on healthcare" --type deep --num-results 20

# Fast search with highlights
fresh search "latest React news" --type fast --highlight-query "performance"

# JSON output for scripting
fresh search "weather API" --format json | jq '.results[].url'
```

### Output Formats

**JSON (default):**
```json
{
  "autopromptString": "Here is a link to...",
  "results": [...],
  "requestId": "...",
  "costDollars": {...}
}
```

**Markdown:**
```markdown
# Search Results for "query"

1. [Result Title](url)
   - Published: 2024-01-15
   - Text preview...

2. [Another Result](url)
   ...
```

---

## fresh fetch

Extract clean content from URLs using Exa.getContents.

### Synopsis

```bash
fresh fetch <url> [options]
fresh fetch <url1> <url2> ... <urlN>
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--text-max <n>` | Maximum characters for text content | `1000` |
| `--highlight-query <q>` | Query for relevant highlights | - |
| `--highlight-max <n>` | Maximum characters for highlights | `200` |
| `--format, -f <type>` | Output format: `json`, `markdown`, `text` | `json` |

### Examples

```bash
# Fetch single URL
fresh fetch https://example.com/article

# Fetch multiple URLs
fresh fetch https://example.com/1 https://example.com/2 https://example.com/3

# With text limit
fresh fetch https://example.com/long-article --text-max 5000

# Get relevant highlights
fresh fetch https://example.com/article --highlight-query "AI regulations"

# Extract to markdown
fresh fetch https://example.com/article --format markdown
```

---

## fresh ask

Ask questions with AI-powered web research. Runs in background by default.

### Synopsis

```bash
fresh ask <query> [options]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--output, -o <file>` | Write answer to file | - |
| `--format, -f <type>` | Output format: `markdown`, `json`, `text` | `markdown` |
| `--model <name>` | AI model to use | `auto` |
| `--max-sources <n>` | Maximum sources to research | `10` |
| `--no-cite` | Disable source citations | - |
| `--wait, -w` | Wait for completion | `false` |
| `--stream, -s` | Stream results as they arrive | `false` |

### Examples

```bash
# Basic question (returns job ID immediately)
fresh ask "What is the last version of React?"

# Wait for result
fresh ask "What is the last version of React?" --wait

# Stream results
fresh ask "What is the last version of React?" --stream

# Save to file
fresh ask "Latest AI news" --output news.md

# Quick answer with fewer sources
fresh ask "What is 2+2?" --max-sources 3
```

### Output

```bash
$ fresh ask "What is the last version of React?"
✓ Job started: ask_abc123
  Status: running
  Use `fresh ask status ask_abc123` to monitor
```

### Job Management

```bash
# Check status
fresh ask status ask_abc123

# Cancel job
fresh ask cancel ask_abc123

# List all jobs
fresh ask list

# Output when completed
$ fresh ask status ask_abc123
✓ Job: ask_abc123
  Status: completed
  Answer saved to: ask_abc123.md
```

---

## fresh research

Deep multi-branch research with tree-of-thought reasoning.

### Synopsis

```bash
fresh research <query> [options]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--depth, -d <n>` | Maximum analysis depth (1-5) | `3` |
| `--branches, -b <n>` | Number of main branches | `4` |
| `--output, -o <file>` | Write report to file | - |
| `--format, -f <type>` | Output format: `markdown`, `json`, `text` | `markdown` |
| `--model <name>` | AI model to use | `auto` |
| `--no-cite` | Disable citations | - |
| `--wait, -w` | Wait for completion | `false` |
| `--stream, -s` | Stream results as they arrive | `false` |

### Examples

```bash
# Basic research
fresh research "Impact of AI on software development"

# Deep research
fresh research "Impact of AI on software development" --depth 4 --branches 6

# Save report
fresh research "Future of renewable energy" --output energy-report.md

# Stream results
fresh research "AI regulations" --stream

# Quick research with shallow depth
fresh research "Python vs JavaScript" --depth 2 --branches 3
```

### Output

```bash
$ fresh research "Impact of AI on software development"
✓ Job started: res_abc123
  Status: running
  Progress: Branch 2/4 (depth 1/3)
  Use `fresh research status res_abc123` to monitor
```

### Job Management

```bash
# Check status
fresh research status res_abc123

# Cancel job
fresh research cancel res_abc123

# List all research jobs
fresh research list

# Full report when completed
fresh research status res_abc123
```

---

## Configuration

### Config File

Fresh stores configuration at `~/.fresh/config.json`:

```json
{
  "apiKey": "your-api-key",
  "defaultFormat": "json",
  "baseUrl": "https://api.fresh.dev"
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `FRESH_API_KEY` | Your API key |
| `FRESH_BASE_URL` | API base URL |
| `FRESH_OUTPUT_DIR` | Default output directory |

---

## Output Format Details

### JSON

Machine-readable output with full data:

```bash
fresh search "AI" --format json | jq '.results[] | .title'
```

### Markdown

Human-readable with formatting:

```bash
fresh ask "What is React?" --format markdown
```

### Text

Plain text without formatting:

```bash
fresh fetch https://example.com --format text
```

---

## Shell Completion

Install shell completion for better UX:

```bash
# Bash
fresh completion bash >> ~/.bashrc

# Zsh
fresh completion zsh >> ~/.zshrc

# Fish
fresh completion fish > ~/.config/fish/completions/fresh.fish
```

---

## Troubleshooting

### "Not authenticated"

Run `fresh auth login` or set `FRESH_API_KEY` environment variable.

### "Rate limit exceeded"

Wait a few seconds and retry, or upgrade your plan for higher limits.

### "Job not found"

Jobs expire after 24 hours. Start a new research job if yours is gone.

### Debug Mode

Run with debug output:

```bash
DEBUG=fresh fresh search "query"
```

---

## Related

- [SDK](../packages/sdk/README) - SDK documentation
- [fetch](../features/fetch/README) - Content extraction
- [search](../features/search/README) - Web search
- [ask](../features/ask/README) - Question answering
- [research](../features/research/README) - Deep research
