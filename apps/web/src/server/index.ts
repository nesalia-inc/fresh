import { defineContext, createAPI, createPublicAPI, ok, err } from "@deessejs/server";
import { error } from "@deessejs/fp";
import { z } from "zod";
import { createFresh } from "@/core";
import type { SearchOptions, FetchOptions } from "@/core/types";
import {
  SearchOptionsSchema,
  FetchOptionsSchema,
} from "@/core/types";

const { t, createAPI: createDeesseAPI } = defineContext({});

// Structured error factories using @deessejs/fp error()
const SearchError = error({
  name: "SEARCH_FAILED",
  schema: z.object({ message: z.string() }),
  message: (args) => args.message,
});

const FetchError = error({
  name: "FETCH_FAILED",
  schema: z.object({ message: z.string() }),
  message: (args) => args.message,
});

const InternalError = error({
  name: "INTERNAL_ERROR",
  schema: z.object({ message: z.string() }),
  message: (args) => args.message,
});

// Fresh Search Procedure
const freshSearch = t.query({
  args: SearchOptionsSchema,
  handler: async (_ctx, args) => {
    try {
      const fresh = createFresh({ apiKey: process.env.EXA_API_KEY });
      const result = await fresh.search(args as SearchOptions);

      if (!result.ok) {
        return err(SearchError({ message: result.error.message }));
      }

      return ok(result.value);
    } catch (error) {
      return err(InternalError({ message: error instanceof Error ? error.message : "Search failed" }));
    }
  },
});

// Fresh Fetch Procedure
const freshFetch = t.query({
  args: FetchOptionsSchema,
  handler: async (_ctx, args) => {
    try {
      const fresh = createFresh({ apiKey: process.env.EXA_API_KEY });
      const result = await fresh.fetch(args as FetchOptions);

      if (!result.ok) {
        return err(FetchError({ message: result.error.message }));
      }

      return ok(result.value);
    } catch (error) {
      return err(InternalError({ message: error instanceof Error ? error.message : "Fetch failed" }));
    }
  },
});

// Router
const appRouter = t.router({
  fresh: t.router({
    search: freshSearch,
    fetch: freshFetch,
  }),
});

export const api = createDeesseAPI({ router: appRouter });
export const publicAPI = createPublicAPI(api);
export type AppRouter = typeof appRouter;
