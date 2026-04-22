import { attemptAsync } from '@deessejs/fp';
import { Exa } from 'exa-js';
import { FetchError } from './errors';
import type { FetchOptions } from './types';

export const createFetch = (exa: Exa) => {
  return async (options: FetchOptions) => {
    const urls = options.urls;
    const result = await attemptAsync(
      () =>
        exa.getContents(urls, {
          text: options.text,
          highlights: options.highlights,
        }),
      (error) =>
        FetchError({
          url: Array.isArray(urls) ? urls[0] : urls,
          reason: error instanceof Error ? error.message : String(error),
        }).addNotes('Exa getContents operation failed')
    );

    if (result.ok) {
      return {
        ok: true as const,
        value: {
          results: result.value.results,
          requestId: result.value.requestId,
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
