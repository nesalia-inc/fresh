import { Exa } from 'exa-js';
import { createSearch } from './search';
import { createFetch } from './fetch';
import type { SearchOptions, FetchOptions, SearchResponse, FetchResponse } from './types';

export interface FreshOptions {
  apiKey?: string;
}

type SearchResult = { ok: true; value: SearchResponse } | { ok: false; error: Error };
type FetchResult = { ok: true; value: FetchResponse } | { ok: false; error: Error };

export interface FreshInstance {
  search: (options: SearchOptions) => Promise<SearchResult>;
  fetch: (options: FetchOptions) => Promise<FetchResult>;
}

export const createFresh = (options: FreshOptions = {}): FreshInstance => {
  const exa = new Exa(options.apiKey);
  return {
    search: createSearch(exa) as FreshInstance['search'],
    fetch: createFetch(exa) as FreshInstance['fetch'],
  };
};
