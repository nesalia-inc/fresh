import { attemptAsync } from '@deessejs/fp';
import { Exa } from 'exa-js';
import type {
  DeepSearchType,
  RegularSearchOptions,
  BaseSearchOptions,
  ContentsOptions,
  TextContentsOptions,
  HighlightsContentsOptions,
} from 'exa-js';
import { SearchError } from './errors';
import type { SearchOptions } from './types';

const isDeepSearchType = (type?: string): type is DeepSearchType => {
  return type === 'deep-lite' || type === 'deep' || type === 'deep-reasoning';
};

const buildExaSearchOptions = (options: SearchOptions): RegularSearchOptions => {
  const base = {
    numResults: options.numResults ?? 10,
    includeDomains: options.includeDomains,
    excludeDomains: options.excludeDomains,
    startPublishedDate: options.startPublishedDate,
    endPublishedDate: options.endPublishedDate,
    category: options.category,
    highlights: options.highlights,
    text: options.text,
  } as BaseSearchOptions & {
    numResults?: number;
    includeDomains?: string[];
    excludeDomains?: string[];
    startPublishedDate?: Date;
    endPublishedDate?: Date;
    category?: string;
    highlights?: HighlightsContentsOptions;
    text?: TextContentsOptions;
  };

  if (isDeepSearchType(options.type)) {
    return {
      ...base,
      type: options.type,
      contents: options.contents as ContentsOptions | undefined,
    } as RegularSearchOptions;
  }

  return {
    ...base,
    type: (options.type || 'auto') as RegularSearchOptions extends { type?: infer T } ? T : never,
    contents: options.contents as ContentsOptions | undefined,
  } as RegularSearchOptions;
};

export const createSearch = (exa: Exa) => {
  return async (options: SearchOptions) => {
    const result = await attemptAsync(
      () => exa.search(options.query, buildExaSearchOptions(options)),
      (error) =>
        SearchError({
          query: options.query,
          reason: error instanceof Error ? error.message : String(error),
        }).addNotes('Exa search operation failed')
    );

    if (result.ok) {
      return {
        ok: true as const,
        value: {
          results: result.value.results,
          requestId: result.value.requestId,
          autoDate: result.value.autoDate,
          costDollars: result.value.costDollars,
          statuses: result.value.statuses,
        },
      };
    }

    return {
      ok: false as const,
      error: result.error,
    };
  };
};
