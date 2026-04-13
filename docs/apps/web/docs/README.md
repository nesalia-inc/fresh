# Fresh Documentation

Documentation site for Fresh built with Fumadocs.

## Overview

Fresh uses [Fumadocs](https://www.fumadocs.dev) as its documentation framework. Fumadocs is a fast, flexible documentation solution built on MDX with built-in search, theming, and React components.

## Why Fumadocs?

| Feature | Benefit |
|---------|---------|
| **MDX Support** | Write docs in Markdown with React components |
| **Built-in Search** | Orama search engine, no external service needed |
| **LLM Ready** | Built-in AI search integration |
| **Fast** | Optimized for performance with static generation |
| **Components** | Pre-built UI components for documentation |
| **Theming** | Light/dark mode with system preference |
| **i18n** | Internationalization support |

## Stack

- **Framework**: Next.js 15+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Content**: MDX with frontmatter
- **Search**: Orama (built-in)

## Project Structure

```
apps/web/
├── docs/
│   ├── content/
│   │   ├── index.mdx          # Home page
│   │   ├── getting-started/
│   │   │   ├── index.mdx
│   │   │   ├── installation.mdx
│   │   │   └── configuration.mdx
│   │   ├── features/
│   │   │   ├── index.mdx
│   │   │   ├── search.mdx
│   │   │   ├── fetch.mdx
│   │   │   ├── ask.mdx
│   │   │   └── research.mdx
│   │   └── api/
│   │       ├── index.mdx
│   │       ├── search.mdx
│   │       ├── fetch.mdx
│   │       └── ...
│   ├──fumadocs.config.ts      # Fumadocs configuration
│   └── layout.tsx              # Docs layout
├── src/
│   ├── components/
│   │   ├── docs/
│   │   │   ├── docs-layout.tsx
│   │   │   ├── docs-page.tsx
│   │   │   └── ...
│   │   └── ui/
│   └── app/
│       └── docs/
│           └── [...slug]/
│               └── page.tsx   # Dynamic docs page
└── package.json
```

## Content Organization

### Frontmatter

Each MDX file uses frontmatter for metadata:

```mdx
---
title: Getting Started
description: Learn how to install and configure Fresh
ogImage: /images/getting-started.png
---
```

### Page Tree

Navigation is configured in `fumadocs.config.ts`:

```typescript
import { defineConfig } from "fumadocs/config";

export default defineConfig({
  docs: {
    schema: {
      title: "title",
      description: "description",
    },
  },
  pageTree: [
    {
      name: "getting-started",
      title: "Getting Started",
    },
    {
      name: "features",
      title: "Features",
      children: [
        { name: "search", title: "Search" },
        { name: "fetch", title: "Fetch" },
        { name: "ask", title: "Ask" },
        { name: "research", title: "Research" },
      ],
    },
  ],
});
```

## Writing Content

### Basic MDX

```mdx
# My Heading

This is a paragraph with **bold** and *italic* text.

## Code Blocks

```typescript
const client = createClient({
  apiKey: 'fresh_sk_...',
});
```

### Using Components

Fumadocs provides built-in components:

```mdx
import { Steps, Callout, Tabs } from "fumadocs-ui/components";

<Steps>
  ### Step 1
  Install the SDK

  ### Step 2
  Configure your API key

  ### Step 3
  Start building
</Steps>

<Callout title="Note">
  This is a helpful tip.
</Callout>
```

## Available Components

### Callout

```tsx
<Callout title="Warning" type="warning">
  This action cannot be undone.
</Callout>
```

Types: `default`, `info`, `warning`, `error`, `success`

### Steps

```tsx
<Steps>
  ### First Step
  Content here

  ### Second Step
  More content
</Steps>
```

### Tabs

```tsx
<Tabs items={["npm", "yarn", "pnpm"]}>
  <Tab>npm install @fresh/sdk</Tab>
  <Tab>yarn add @fresh/sdk</Tab>
  <Tab>pnpm add @fresh/sdk</Tab>
</Tabs>
```

### Code Block

````mdx
```typescript title="example.ts"
const hello = "world";
```
````

Features: syntax highlighting, line numbers, copy button, title, highlighting

### Accordion

```tsx
<Accordion>
  <AccordionItem title="What is Fresh?">
    Fresh is a deep research platform for AI agents.
  </AccordionItem>
</Accordion>
```

### Type Table

```tsx
<TypeTable
  rows={[
    { type: "string", name: "apiKey", description: "Your API key" },
    { type: "number", name: "timeout", description: "Request timeout in ms" },
  ]}
/>
```

### Banner

```tsx
<Banner variant="success" href="/changelog">
  New features available in v2.0!
</Banner>
```

## Search

Fresh docs use Orama search by default.

### Configuration

```typescript
// fumadocs.config.ts
export default defineConfig({
  search: {
    enabled: true,
    options: {
      indexKind: "memory", // or "dom"
    },
  },
});
```

### Custom Search

Use Algolia, Typesense, or custom providers:

```typescript
import { algoliaSearch } from "fumadocs-ui/search/algolia";

export default defineConfig({
  search: {
    provider: algoliaSearch({
      appId: process.env.ALGOLIA_APP_ID,
      apiKey: process.env.ALGOLIA_SEARCH_KEY,
      indexName: "fresh_docs",
    }),
  },
});
```

## Layouts

### Docs Layout

Standard documentation layout with sidebar:

```tsx
// app/docs/layout.tsx
import { DocsLayout } from "fumadocs-ui/layouts/docs";

export default function Layout({ children }) {
  return (
    <DocsLayout
      title="Fresh Docs"
      description="AI-powered web research"
      links={[]}
    >
      {children}
    </DocsLayout>
  );
}
```

### Home Layout

Landing page layout:

```tsx
import { HomeLayout } from "fumadocs-ui/layouts/home";

export default function Layout({ children }) {
  return (
    <HomeLayout
      name="Fresh"
      description="Deep research for AI agents"
    >
      {children}
    </HomeLayout>
  );
}
```

### Flux Layout

Full-width layout with enhanced navigation:

```tsx
import { FluxLayout } from "fumadocs-ui/layouts/flux";
```

## Theming

Fumadocs supports light/dark mode with system preference:

```tsx
import { ThemeProvider } from "next-themes";

export function Provider({ children }: { children: React.ReactNode }) {
  return <ThemeProvider attribute="class" defaultTheme="system" />;
}
```

### Custom Colors

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          light: "#3B82F6",
          dark: "#60A5FA",
        },
      },
    },
  },
};
```

## i18n Support

Fresh docs support multiple languages:

```typescript
// fumadocs.config.ts
export default defineConfig({
  docs: {
    defaultLanguage: "en",
    languages: ["en", "fr", "es", "de", "ja"],
  },
});
```

Content structure:
```
docs/
├── content/
│   ├── en/
│   │   └── getting-started.mdx
│   ├── fr/
│   │   └── getting-started.mdx
│   └── ...
```

## CLI Commands

```bash
# Initialize Fumadocs in a new project
npm create fumadocs-app

# Generate pages from content
npx fumadocs generate

# Build documentation
npx fumadocs build
```

## Deployment

Fresh documentation is deployed on Vercel:

```bash
# Production
git push main
# Vercel auto-deploys

# Preview
git push preview
```

### Environment Variables

```bash
# Optional: Algolia search
ALGOLIA_APP_ID=
ALGOLIA_SEARCH_KEY=
ALGOLIA_INDEX_NAME=

# Optional: LLM provider for AI search
LLM_API_KEY=
```

## Contributing

### Adding New Docs

1. Create MDX file in `docs/content/<section>/`
2. Add frontmatter with `title` and `description`
3. Update `pageTree` in `fumadocs.config.ts`
4. Submit PR

### Writing Guidelines

- Use clear, concise language
- Include code examples
- Add screenshots if UI changes
- Update related docs when making breaking changes

## Related

- [Fumadocs](https://www.fumadocs.dev) - Documentation framework
- [Next.js](https://nextjs.org) - React framework
- [MDX](https://mdxjs.com) - Markdown with JSX
