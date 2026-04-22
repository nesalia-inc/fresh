import { Exa } from 'exa-js';
import { createSearch } from './search';
import { createFetch } from './fetch';
import type { SearchOptions, FetchOptions } from './types';

export interface FreshOptions {
  apiKey?: string;
}

export interface FreshInstance {
  search: (options: SearchOptions) => Promise<ReturnType<ReturnType<typeof createSearch>>>;
  fetch: (options: FetchOptions) => Promise<ReturnType<ReturnType<typeof createFetch>>>;
}

export const createFresh = (options: FreshOptions = {}): FreshInstance => {
  const exa = new Exa(options.apiKey);
  return {
    search: createSearch(exa),
    fetch: createFetch(exa),
  };
};
