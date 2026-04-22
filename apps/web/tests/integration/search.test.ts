import { describe, it, expect } from 'vitest';
import { createFresh } from '../../src/core';

const EXA_API_KEY = process.env.EXA_API_KEY;

const itIfApiKey = EXA_API_KEY ? it : it.skip;

describe('Search Integration', () => {
  itIfApiKey('should perform a basic search', async () => {
    const fresh = createFresh({ apiKey: EXA_API_KEY });
    const result = await fresh.search({ query: 'TypeScript' });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      throw new Error(result.error.message);
    }

    expect(result.value.results.length).toBeGreaterThan(0);
    expect(result.value.requestId).toBeDefined();
  });

  itIfApiKey('should return search with results', async () => {
    const fresh = createFresh({ apiKey: EXA_API_KEY });
    const result = await fresh.search({
      query: 'machine learning',
      numResults: 5,
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      throw new Error(result.error.message);
    }

    expect(result.value.results.length).toBeLessThanOrEqual(5);
    expect(result.value.results[0].title).toBeDefined();
    expect(result.value.results[0].url).toBeDefined();
  });

  itIfApiKey('should handle invalid API key gracefully', async () => {
    const freshWithInvalidKey = createFresh({ apiKey: 'invalid-key' });
    const result = await freshWithInvalidKey.search({ query: 'test' });

    expect(result.ok).toBe(false);
    if (result.ok) {
      throw new Error('Should have failed with invalid key');
    }

    expect(result.error.message).toBeDefined();
  });

  itIfApiKey('should perform deep search', async () => {
    const fresh = createFresh({ apiKey: EXA_API_KEY });
    const result = await fresh.search({
      query: 'artificial intelligence trends 2024',
      type: 'deep',
      numResults: 3,
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      throw new Error(result.error.message);
    }

    expect(result.value.results.length).toBeGreaterThan(0);
  });

  itIfApiKey('should filter by domain', async () => {
    const fresh = createFresh({ apiKey: EXA_API_KEY });
    const result = await fresh.search({
      query: 'TypeScript',
      includeDomains: ['github.com'],
      numResults: 5,
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      throw new Error(result.error.message);
    }

    // All results should be from github.com (or at least one should be)
    const githubResults = result.value.results.filter((r) =>
      r.url.includes('github.com')
    );
    expect(githubResults.length).toBeGreaterThan(0);
  });
});
