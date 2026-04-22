import { defineContext, createPublicAPI } from "@deessejs/server";


export const { t, createAPI } = defineContext({})

export const example = t.query({
  handler: async (ctx) => {
    return "heyy"
  }
})

const appRouter = t.router({ example })

export const api = createAPI({ router: appRouter })
export const publicAPI = createPublicAPI(api);
export type AppRouter = typeof appRouter;