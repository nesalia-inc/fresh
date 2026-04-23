import { getCredential, type StoredCredential } from "./storage.js";

const API_BASE = process.env.FRESH_API_URL || "https://fresh.nesalia.com";

export interface SearchOptions {
  query: string;
  numResults?: number;
  type?: "auto" | "fast" | "deep-lite" | "deep" | "deep-reasoning" | "instant";
  includeDomains?: string[];
  excludeDomains?: string[];
  startPublishedDate?: string;
  endPublishedDate?: string;
  category?: "company" | "research paper" | "news" | "pdf" | "personal site" | "financial report" | "people";
}

export interface FetchOptions {
  urls: string | string[];
  text?: {
    maxCharacters?: number;
    includeHtmlTags?: boolean;
    verbosity?: "compact" | "standard" | "full";
    includeSections?: string[];
    excludeSections?: string[];
  };
  highlights?: {
    query?: string;
    maxCharacters?: number;
    numSentences?: number;
    highlightsPerUrl?: number;
  };
}

export interface SearchResult {
  results: Array<{
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
    entities?: Array<{
      id?: string;
      name?: string;
      type?: string;
    }>;
  }>;
  requestId: string;
  autoDate?: string;
  costDollars?: {
    stDollars: number;
    totalCost: number;
  };
  statuses?: Array<{
    code: "success" | "error" | "notFound" | "unavailable";
    url: string;
  }>;
}

export interface FetchResult {
  results: Array<{
    url: string;
    id: string;
    title?: string;
    text?: string;
    author?: string;
    publishedDate?: string;
    highlights?: string[];
    highlightScores?: number[];
  }>;
  requestId: string;
  costDollars?: {
    stDollars: number;
    totalCost: number;
  };
  statuses?: Array<{
    code: "success" | "error" | "notFound" | "unavailable";
    url: string;
  }>;
}

export class APIError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const cred = await getCredential();
  if (!cred) {
    throw new APIError("Not authenticated. Run 'fresh auth login' first.", "UNAUTHENTICATED", 401);
  }
  return {
    Authorization: `Bearer ${cred.accessToken}`,
  };
}

export async function search(options: SearchOptions): Promise<SearchResult> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: JSON.stringify(options),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Unknown error" }));
    throw new APIError(error.message || "Search failed", error.code || "SEARCH_FAILED", response.status);
  }

  return response.json();
}

export async function fetchUrl(options: FetchOptions): Promise<FetchResult> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE}/api/fetch`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: JSON.stringify(options),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Unknown error" }));
    throw new APIError(error.message || "Fetch failed", error.code || "FETCH_FAILED", response.status);
  }

  return response.json();
}