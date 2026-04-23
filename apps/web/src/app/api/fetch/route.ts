import { NextRequest } from "next/server";
import { deesseAuth } from "@/lib/deesse";
import { createFresh } from "@/core";
import { FetchOptionsSchema } from "@/core/types";

export async function POST(request: NextRequest) {
  // 1. Validate authentication
  const session = await deesseAuth.api.getSession({
    headers: request.headers,
  });

  if (!session) {
    return Response.json(
      { error: "Unauthorized", message: "Not authenticated" },
      { status: 401 }
    );
  }

  // 2. Parse and validate request body
  const body = await request.json();
  const parsed = FetchOptionsSchema.safeParse(body);

  if (!parsed.success) {
    return Response.json(
      { error: "Validation Error", message: parsed.error.message },
      { status: 400 }
    );
  }

  // 3. Execute fetch
  try {
    const fresh = createFresh({ apiKey: process.env.EXA_API_KEY });
    const result = await fresh.fetch(parsed.data);

    if (!result.ok) {
      return Response.json(
        { error: "Fetch Failed", message: result.error.message },
        { status: 500 }
      );
    }

    return Response.json(result.value);
  } catch (error) {
    return Response.json(
      { error: "Internal Error", message: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}