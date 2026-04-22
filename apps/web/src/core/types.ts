import { z } from 'zod';
import type {
  ContentsOptions as ExaContentsOptions,
  TextContentsOptions,
  HighlightsContentsOptions,
  RegularSearchOptions,
} from 'exa-js';

// Re-export Exa types for convenience
export type { TextContentsOptions, HighlightsContentsOptions, RegularSearchOptions };

// Zod schemas for API validation
export const TextContentsOptionsSchema = z.object({
  maxCharacters: z.number().optional(),
  includeHtmlTags: z.boolean().optional(),
  verbosity: z.enum(['compact', 'standard', 'full']).optional(),
  includeSections: z.array(z.string()).optional(),
  excludeSections: z.array(z.string()).optional(),
});

export const HighlightsContentsOptionsSchema = z.object({
  query: z.string().optional(),
  maxCharacters: z.number().optional(),
  numSentences: z.number().optional(),
  highlightsPerUrl: z.number().optional(),
});

export const SearchOptionsSchema = z.object({
  query: z.string().min(1, 'Query is required'),
  numResults: z.number().optional(),
  type: z.enum(['auto', 'fast', 'deep-lite', 'deep', 'deep-reasoning', 'instant']).optional(),
  includeDomains: z.array(z.string()).optional(),
  excludeDomains: z.array(z.string()).optional(),
  startPublishedDate: z.date().optional(),
  endPublishedDate: z.date().optional(),
  category: z.enum(['company', 'research paper', 'news', 'pdf', 'personal site', 'financial report', 'people']).optional(),
  highlights: HighlightsContentsOptionsSchema.optional(),
  text: TextContentsOptionsSchema.optional(),
  contents: z.any().optional(),
});

export const FetchOptionsSchema = z.object({
  urls: z.union([z.string().url(), z.array(z.string().url())]),
  text: TextContentsOptionsSchema.optional(),
  highlights: HighlightsContentsOptionsSchema.optional(),
}).refine(data => {
  if (Array.isArray(data.urls)) return data.urls.length > 0;
  return data.urls.length > 0;
}, { message: 'At least one URL is required' });

export type SearchOptionsInput = z.infer<typeof SearchOptionsSchema>;
export type FetchOptionsInput = z.infer<typeof FetchOptionsSchema>;

// Our simplified SearchOptions - we'll adapt to Exa types internally
export interface SearchOptions {
  query: string;
  numResults?: number;
  type?: 'auto' | 'fast' | 'deep-lite' | 'deep' | 'deep-reasoning' | 'instant';
  includeDomains?: string[];
  excludeDomains?: string[];
  startPublishedDate?: Date;
  endPublishedDate?: Date;
  category?:
    | 'company'
    | 'research paper'
    | 'news'
    | 'pdf'
    | 'personal site'
    | 'financial report'
    | 'people';
  highlights?: HighlightsContentsOptions;
  text?: TextContentsOptions;
  contents?: ExaContentsOptions;
}

export interface SearchResponse {
  results: SearchResult[];
  requestId: string;
  autoDate?: string;
  costDollars?: {
    stDollars: number;
    totalCost: number;
  };
  statuses?: Array<{
    code: 'success' | 'error' | 'notFound' | 'unavailable';
    url: string;
  }>;
}

export interface SearchResult {
  title: string;
  url: string;
  id: string;
  publishedDate?: string;
  author?: string;
  score?: number;
  image?: string;
  favicon?: string;
  text?: string;
  highlights?: string[];
  highlightScores?: number[];
  summary?: string;
  entities?: Entity[];
}

export interface Entity {
  id?: string;
  name?: string;
  type?: string;
}

// Fetch types
export interface FetchOptions {
  urls: string | string[];
  text?: TextContentsOptions;
  highlights?: HighlightsContentsOptions;
}

export interface FetchResponse {
  results: FetchResult[];
  requestId: string;
  costDollars?: {
    stDollars: number;
    totalCost: number;
  };
  statuses?: Array<{
    code: 'success' | 'error' | 'notFound' | 'unavailable';
    url: string;
  }>;
}

export interface FetchResult {
  url: string;
  id: string;
  title?: string;
  text?: string;
  author?: string;
  publishedDate?: string;
  highlights?: string[];
  highlightScores?: number[];
}

// Shared options types
export type { ExaContentsOptions as ContentsOptions };
