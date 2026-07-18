import { NextRequest } from "next/server";
import { getSnapshot, getPlayersByIds } from "@/lib/snapshot";
import { isAIConfigured } from "@/services/ai/client";
import { streamChat } from "@/services/ai/assistant";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  if (!isAIConfigured()) {
    return new Response(
      "The AI chat needs an ANTHROPIC_API_KEY in .env.local (pay-as-you-go, separate from Claude Pro). " +
        "Everything else in the app works without it.",
      { status: 200 }
    );
  }
  const { message, squadIds = [], history = [] } = await req.json();
  const snapshot = getSnapshot();
  const squad = getPlayersByIds(squadIds);
  const stream = streamChat(snapshot, message, squad, history);
  return new Response(stream, {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-cache" },
  });
}
