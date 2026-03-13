# Fresh - Agent Knowledge System

> An intelligent knowledge management system designed for AI agents.

## Purpose

Fresh is not just a documentation fetcher. It is an **agent knowledge system** that enables AI agents to:

1. **Stay informed** - Fetch and maintain up-to-date knowledge on any technology
2. **Learn continuously** - Build comprehensive guides on concepts and technologies
3. **Produce quality code** - Leverage accumulated knowledge when writing code

## The Problem

AI agents need context to produce high-quality code. Without proper knowledge management:

- Agents work with outdated or missing information
- Each conversation starts from scratch - no continuity
- There's no way to capture and reuse learned concepts
- Quality suffers without the right context

## The Solution

Fresh provides a **brain for AI agents**:

```
┌─────────────────────────────────────────────────────────────┐
│                         Agent                                │
│              (Claude Code, custom agents...)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Fresh Core                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Fetch   │  │  Index   │  │  Search  │  │  Guide   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Sources                                │
│   Web (docs, APIs)  │  Local  │  Generated  │  Plugins    │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Core Commands

| Command | Description |
|---------|-------------|
| `get` | Fetch a documentation page and convert to Markdown |
| `list` | Discover all available documentation pages on a website |
| `search` | Search for content across fetched documentation |
| `websearch` | Search the general web for any topic |
| `sync` | Download entire documentation for offline use |
| `guide` | Create and manage personal guides and knowledge |

### Key Capabilities

- **Smart Caching** - Only fetch what has changed
- **Agent-First Design** - SDK layer for direct agent integration
- **Plugin Architecture** - Extensible sources (GitHub, HuggingFace, npm, etc.)
- **Guide Generation** - Synthesize knowledge into actionable guides

## Architecture

Fresh follows clean architecture principles:

- **CLI Layer** - User-facing commands (Typer)
- **Core Layer** - Pure business logic (no I/O dependencies)
- **Source Layer** - Data providers (web, local, plugins)

### Design Principles

1. **Entity-Oriented** - Classes represent concepts, not actions
2. **Separation of Concerns** - Commands handle presentation, core handles logic
3. **Strict Typing** - Protocols, literals, and type hints throughout
4. **Minimal Branching** - Replace conditionals with patterns (Strategy, Result, Maybe)

## Use Cases

### For AI Agents

- Fetch relevant documentation before writing code
- Build personal knowledge base over time
- Create guides on best practices for specific technologies
- Search across accumulated knowledge

### For Developers

- Offline documentation access
- Quick reference lookup
- Knowledge organization
- Integration with custom agents

## Roadmap (V2)

- [ ] SDK/API layer for direct agent integration
- [ ] Plugin system for sources and formats
- [ ] Smart indexing with embeddings
- [ ] Guide synthesis from multiple sources

## License

MIT
