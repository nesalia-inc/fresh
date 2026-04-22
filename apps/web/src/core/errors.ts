import { error } from '@deessejs/fp';
import { z } from 'zod';

// Structured errors using deesse-fp error() factory
export const SearchError = error({
  name: 'SearchError',
  schema: z.object({
    query: z.string(),
    reason: z.string().optional(),
  }),
  message: (args) =>
    args.reason
      ? `Search failed for "${args.query}": ${args.reason}`
      : `Search failed for "${args.query}"`,
});

export const FetchError = error({
  name: 'FetchError',
  schema: z.object({
    url: z.string(),
    reason: z.string().optional(),
  }),
  message: (args) =>
    args.reason
      ? `Fetch failed for "${args.url}": ${args.reason}`
      : `Fetch failed for "${args.url}"`,
});

export const RateLimitError = error({
  name: 'RateLimitError',
  schema: z.object({
    retryAfter: z.number().optional(),
  }),
  message: (args) =>
    args.retryAfter
      ? `Rate limited. Retry after ${args.retryAfter}s`
      : 'Rate limited',
});

export type FreshError = ReturnType<typeof SearchError>;
