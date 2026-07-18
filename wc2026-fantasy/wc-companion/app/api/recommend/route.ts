import { NextRequest, NextResponse } from "next/server";
import { getSnapshot, getPlayersByIds } from "@/lib/snapshot";
import { isAIConfigured } from "@/services/ai/client";
import { getStructuredRecommendation } from "@/services/ai/assistant";
import { prisma, ensureLocalUser } from "@/lib/db";

export const runtime = "nodejs";

// Structured recommendation endpoint (captain / transfer / boost / differential).
export async function POST(req: NextRequest) {
  const { question, squadIds = [], kind = "chat" } = await req.json();
  if (!isAIConfigured()) {
    return NextResponse.json({ error: "AI not configured" }, { status: 503 });
  }
  const snapshot = getSnapshot();
  const squad = getPlayersByIds(squadIds);
  const rec = await getStructuredRecommendation(snapshot, question, squad);

  // Persist for history / weekly newsletter.
  try {
    const userId = await ensureLocalUser();
    await prisma.aIRecommendation.create({
      data: {
        userId,
        kind,
        prompt: question,
        recommendation: rec.recommendation,
        confidence: rec.confidence,
        reasoning: rec.reasoning,
        risks: rec.risk,
        expected: rec.expectedOutcome,
        alternatives: JSON.stringify(rec.alternatives),
      },
    });
  } catch {
    /* persistence is best-effort */
  }
  return NextResponse.json(rec);
}
