"use client";

import { useState } from "react";
import type { Player, AIRecommendation } from "@/types";
import { Card, CardTitle, Button } from "@/components/ui/primitives";
import { RecommendationCard } from "@/components/RecommendationCard";

export function PlayerAIExplain({ player }: { player: Player }) {
  const [rec, setRec] = useState<AIRecommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function explain() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          kind: "differential",
          question: `Give a verdict on ${player.name} (${player.nation}, ${player.pos}) as a fantasy pick right now — should I own him, and why or why not?`,
        }),
      });
      if (res.status === 503) {
        setError("Add an ANTHROPIC_API_KEY in .env.local to enable AI verdicts.");
        return;
      }
      setRec(await res.json());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  if (rec) return <RecommendationCard rec={rec} />;

  return (
    <Card>
      <CardTitle>AI verdict</CardTitle>
      <p className="text-sm text-muted">
        Get a grounded verdict on {player.name.split(" ").pop()} — own, avoid, or monitor — with reasoning, risk and alternatives.
      </p>
      {error ? <p className="mt-2 text-xs text-warn">{error}</p> : null}
      <Button className="mt-3" onClick={explain} disabled={loading}>
        {loading ? "Analysing…" : "Get AI verdict"}
      </Button>
    </Card>
  );
}
