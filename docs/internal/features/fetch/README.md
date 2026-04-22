# Fresh Fetch

Retrieve and extract clean content from any URL.

## Overview

`fresh fetch` retrieves web page content using Exa.ai's content extraction API. It fetches multiple URLs at once, extracts clean text, and returns structured data optimized for AI consumption.

## CLI Usage

```bash
fresh fetch <url> [options]
fresh fetch <url1> <url2> <url3>  # Multiple URLs
```

### Arguments

| Argument | Description |
|----------|-------------|
| `url` | One or more URLs to fetch (required) |

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--text-max <n>` | Maximum characters for text content | `1000` |
| `--highlight-query <q>` | Query for extracting relevant highlights | - |
| `--highlight-max <n>` | Maximum characters for highlights | `200` |
| `--format <type>` | Output format: `json`, `markdown`, `text` | `json` |

### Examples

```bash
# Basic fetch
fresh fetch https://example.com/article

# Multiple URLs
fresh fetch https://example.com/article1 https://example.com/article2

# With text limit and highlights
fresh fetch https://example.com/article --text-max 5000 --highlight-query "AI" --highlight-max 300
```

## API Usage

### Exa.getContents

Retrieves contents of documents based on URLs.

**Endpoint:** `POST /api/fetch`

**Input Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `urls` | `string \| string[] \| SearchResult[]` | A URL or array of URLs | Required |
| `options.text.maxCharacters` | `number` | Maximum characters for full text | `1000` |
| `options.highlights.query` | `string` | Query to extract relevant highlights | - |
| `options.highlights.maxCharacters` | `number` | Maximum characters per highlight | `200` |

### Request Example

```json
{
  "urls": [
    "https://www.example.com/article1",
    "https://www.example.com/article2"
  ],
  "options": {
    "text": {
      "maxCharacters": 1000
    },
    "highlights": {
      "query": "AI",
      "maxCharacters": 200
    }
  }
}
```

### Response Example

```json
{
  "results": [
    {
      "url": "https://example.com/article",
      "id": "https://example.com/article",
      "title": "Example Article",
      "text": "The full text content of the article truncated to maxCharacters..."
    }
  ],
  "requestId": "abc123-def456",
  "costDollars": {
    "stDollars": 0.0001,
    "totalCost": 0.0001
  },
  "statuses": [
    {
      "code": "success",
      "url": "https://example.com/article"
    }
  ]
}
```

### Result Object

| Field | Type | Description |
|-------|------|-------------|
| `results` | `SearchResult[]` | List of content results |
| `results[].url` | `string` | The source URL |
| `results[].id` | `string` | Unique identifier (mirrors URL) |
| `results[].title` | `string` | Document title |
| `results[].text` | `string` | Extracted text content |
| `requestId` | `string` | Request ID for debugging |
| `costDollars.stDollars` | `number` | Soft dollar cost |
| `costDollars.totalCost` | `number` | Total cost in dollars |
| `statuses` | `Status[]` | Per-URL status information |

### Status Codes

| Code | Description |
|------|-------------|
| `success` | Content fetched successfully |
| `error` | Failed to fetch this URL |
| `notFound` | URL returned 404 |
| `unavailable` | Content temporarily unavailable |

## Features

### Content Extraction

- **Text extraction** - Extracts clean text from web pages
- **Highlight extraction** - Uses query-based relevance to extract key passages
- **Smart truncation** - Respects maxCharacters limits
- **Batch processing** - Fetch multiple URLs in single request

### Metadata

- **Title extraction** - Pulls title from page or Open Graph tags
- **URL normalization** - Standardizes and deduplicates URLs
- **Cost tracking** - Shows soft dollar cost per request

## Error Handling

### Error Response

```json
{
  "error": {
    "code": "INVALID_URL",
    "message": "URL format is invalid",
    "details": "https:// is required"
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_URL` | URL format is invalid or missing protocol |
| `FETCH_ERROR` | Failed to fetch URL |
| `TIMEOUT` | Request exceeded timeout limit |
| `PARSE_ERROR` | Failed to parse content |
| `RATE_LIMITED` | Rate limit exceeded |
| `UNAUTHORIZED` | Invalid or missing API key |

## SDK Usage

```typescript
import { createClient } from '@fresh/sdk';

const client = createClient({ apiKey: 'your-api-key' });

// Simple text fetch
const result = await client.getContents([
  'https://example.com/article1',
  'https://example.com/article2'
], {
  text: { maxCharacters: 1000 }
});

result.results.forEach(doc => {
  console.log(doc.title);
  console.log(doc.text);
});

// With highlights for relevance
const highlighted = await client.getContents([
  'https://example.com/article'
], {
  text: { maxCharacters: 5000 },
  highlights: { query: 'AI regulations', maxCharacters: 200 }
});
```

## Rate Limits

- **Free tier:** 100 requests/minute
- **Pro tier:** 1,000 requests/minute
- **Enterprise:** Custom limits

## Related

- [search](../search/README) - Web search functionality
- [research](../research/README) - Deep research mode
- [ask](../ask/README) - Question answering
