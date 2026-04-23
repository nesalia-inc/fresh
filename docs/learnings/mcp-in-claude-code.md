# MCP (Model Context Protocol) in Claude Code

## Overview

Claude Code connects to external tools and data sources through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction), an open standard for AI-tool integrations. MCP servers give Claude Code access to tools, databases, and APIs.

## What You Can Do With MCP

With MCP servers connected, you can ask Claude Code to:

- **Implement features from issue trackers**: "Add the feature described in JIRA issue ENG-4521"
- **Analyze monitoring data**: "Check Sentry for errors in the last 24 hours"
- **Query databases**: "Find users who haven't logged in recently"
- **Integrate designs**: "Update the email template based on new Figma designs"
- **Automate workflows**: "Create Gmail drafts for these users"

## Installation Methods

### Option 1: Remote HTTP Server (Recommended)

```bash
# Basic syntax
claude mcp add --transport http <name> <url>

# Real example: Connect to Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Example with Bearer token
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

### Option 2: Remote SSE Server

> **Deprecated**: SSE transport is deprecated. Use HTTP servers instead when available.

```bash
claude mcp add --transport sse <name> <url>
```

### Option 3: Local Stdio Server

Local servers run as processes on your machine. Ideal for tools needing direct system access.

```bash
# Basic syntax
claude mcp add [options] <name> -- <command> [args...]

# Real example: Add Airtable server
claude mcp add --transport stdio --env AIRTABLE_API_KEY=YOUR_KEY airtable \
  -- npx -y airtable-mcp-server
```

> **Important**: All options (`--transport`, `--env`, `--scope`, `--header`) must come **before** the server name. The `--` separates the server name from command arguments.

### Windows Users

On native Windows (not WSL), local MCP servers using `npx` require the `cmd /c` wrapper:

```bash
claude mcp add --transport stdio my-server -- cmd /c npx -y @some/package
```

## Managing MCP Servers

```bash
# List all configured servers
claude mcp list

# Get details for a specific server
claude mcp get github

# Remove a server
claude mcp remove github

# Within Claude Code: Check server status
/mcp
```

## Installation Scopes

MCP servers can be configured at three scopes:

| Scope | Loads in | Shared | Stored in |
|-------|---------|--------|-----------|
| **Local** (default) | Current project only | No | `~/.claude.json` |
| **Project** | Current project only | Yes, via `.mcp.json` | `.mcp.json` in project root |
| **User** | All projects | No | `~/.claude.json` |

### Local Scope (Default)

```bash
claude mcp add --transport http stripe https://mcp.stripe.com
```

Stored in `~/.claude.json` under the project's path.

### Project Scope

```bash
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

Creates `.mcp.json` in project root (version controlled).

### User Scope

```bash
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

Available across all projects.

## Adding Servers via JSON Configuration

```bash
# HTTP server with JSON
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'

# Stdio server with JSON
claude mcp add-json local-weather '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'
```

## Authentication with Remote MCP Servers

### OAuth 2.0 Authentication

Many cloud-based MCP servers require OAuth:

```bash
# 1. Add the server
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# 2. Authenticate within Claude Code
/mcp
```

### Fixed OAuth Callback Port

Some servers require a specific redirect URI:

```bash
claude mcp add --transport http \
  --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

### Pre-configured OAuth Credentials

```bash
claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

Or with JSON:

```bash
claude mcp add-json my-server \
  '{"type":"http","url":"https://mcp.example.com/mcp","oauth":{"clientId":"your-client-id","callbackPort":8080}}' \
  --client-secret
```

## Environment Variable Expansion

In `.mcp.json`, environment variables are supported:

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

Syntax: `${VAR}` or `${VAR:-default}`.

## MCP as a Plugin

Plugins can bundle MCP servers that start automatically when the plugin is enabled.

### Plugin MCP Configuration

In `.mcp.json` at plugin root:

```json
{
  "mcpServers": {
    "database-tools": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_URL": "${DB_URL}"
      }
    }
  }
}
```

Or inline in `plugin.json`:

```json
{
  "name": "my-plugin",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

## Using MCP Resources

MCP servers can expose resources accessible via @ mentions:

```text
Can you analyze @github:issue://123?

Please review the API documentation at @docs:file://api/authentication

Compare @postgres:schema://users with @docs:file://database/user-model
```

## MCP Prompts as Commands

MCP servers can expose prompts available as commands:

```text
/mcp__github__list_prs

/mcp__github__pr_review 456

/mcp__jira__create_issue "Bug in login flow" high
```

## Popular MCP Servers

See the [official MCP registry](https://github.com/modelcontextprotocol/servers) for hundreds of servers including:

- **GitHub**: Code reviews, issue management, PRs
- **Sentry**: Error monitoring and debugging
- **PostgreSQL**: Database queries
- **Slack**: Team communication
- **Notion**: Documentation and wikis
- **Figma**: Design reviews
- **AWS**: Cloud resource management

## Example Workflows

### Monitor Production Errors

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

Then ask:
- "What are the most common errors in the last 24 hours?"
- "Show me the stack trace for error ID abc123"

### Connect to GitHub

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"
```

Then ask:
- "Review PR #456 and suggest improvements"
- "Create a new issue for the bug we just found"

### Query PostgreSQL

```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"
```

Then ask:
- "What's our total revenue this month?"
- "Show me the schema for the orders table"

## Tool Search

Claude Code uses "tool search" to keep MCP context usage low. Tool definitions are deferred until needed rather than loaded upfront. This means adding more MCP servers has minimal impact on your context window.

Control this behavior with `ENABLE_TOOL_SEARCH`:

| Value | Behavior |
|-------|----------|
| (unset) | Tools deferred by default, loaded on demand |
| `true` | All tools deferred |
| `auto` | Load upfront if within 10% of context, defer overflow |
| `false` | All tools loaded upfront |

## Output Limits

When MCP tools produce large outputs:

- **Warning threshold**: 10,000 tokens
- **Default max**: 25,000 tokens
- **Configurable**: Set `MAX_MCP_OUTPUT_TOKENS` environment variable

## Enterprise: Managed MCP Configuration

### Option 1: Exclusive Control

Deploy `managed-mcp.json` to system-wide directory for complete control:

- macOS: `/Library/Application Support/ClaudeCode/managed-mcp.json`
- Linux/WSL: `/etc/claude-code/managed-mcp.json`
- Windows: `C:\Program Files\ClaudeCode\managed-mcp.json`

### Option 2: Policy-based Control

Use allowlists/denylists in settings:

```json
{
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverUrl": "https://mcp.company.com/*" }
  ],
  "deniedMcpServers": [
    { "serverName": "dangerous-server" }
  ]
}
```

Restrictions can be by:
- `serverName`: Match by configured name
- `serverCommand`: Match exact command for stdio servers
- `serverUrl`: Match URL patterns with wildcards for remote servers
