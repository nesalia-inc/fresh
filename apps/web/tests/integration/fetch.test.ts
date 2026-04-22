import { describe, it, expect } from 'vitest';
import { createFresh } from '../../src/core';

const EXA_API_KEY = process.env.EXA_API_KEY;

const itIfApiKey = EXA_API_KEY ? it : it.skip;

describe('Fetch Integration', () => {
  itIfApiKey('should fetch content from a single URL', async () => {
    const fresh = createFresh({ apiKey: EXA_API_KEY });
    const result = await fresh.fetch({
      urls: ['https://example.com'],
    });

    if (!result.ok) {
      console.error('Fetch failed:', result.error);
    }
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.value.results.length).toBeGreaterThan(0);
    expect(result.value.results[0].url).toBe('https://example.com');
    expect(result.value.requestId).toBeDefined();
  });

  itIfApiKey('should fetch content from multiple URLs', async () => {
    const fresh = createFresh({ apiKey: EXA_API_KEY });
    const result = await fresh.fetch({
      urls: ['https://example.com', 'https://example.org'],
    });

    if (!result.ok) {
      console.error('Fetch failed:', result.error);
    }
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.value.results.length).toBe(2);
  });

  itIfApiKey('should fetch with text options', async () => {
    const fresh = createFresh({ apiKey: EXA_API_KEY });
    const result = await fresh.fetch({
      urls: ['https://example.com'],
      text: {
        maxCharacters: 100,
      },
    });

    if (!result.ok) {
      console.error('Fetch failed:', result.error);
    }
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.value.results[0].text).toBeDefined();
  });

  itIfApiKey('should fetch with highlights', async () => {
    const fresh = createFresh({ apiKey: EXA_API_KEY });
    const result = await fresh.fetch({
      urls: ['https://example.com'],
      highlights: {
        query: 'example',
        maxCharacters: 50,
      },
    });

    if (!result.ok) {
      console.error('Fetch failed:', result.error);
    }
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.value.results[0].highlights).toBeDefined();
  });
});
