"use client";

import Link from "next/link";
import type { Player } from "@/types";
import { useSquad } from "@/lib/useSquad";
import { pickBestXI, rateTeam, validateSquad } from "@/lib/engine";
import { Card, CardTitle, Badge, Progress } from "@/components/ui/primitives";
import { RatingDial } from "@/components/widgets";

export function DashboardSquad({ players, optimalProjected }: { players: Player[]; optimalProjected: number }) {
  const { ids, loaded } = useSquad();
  const map = new Map(players.map((p) => [p.id, p]));
  const squad = ids.map((id) => map.get(id)).filter(Boolean) as Player[];

  if (!loaded) return null;

  if (squad.length < 11) {
    return (
      <Card>
        <CardTitle>Your squad</CardTitle>
        <div className="py-6 text-center">
          <p className="text-sm text-muted">
            You haven&apos;t built a squad yet ({squad.length}/15).
          </p>
          <Link href="/squad" className="mt-3 inline-block rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-bg">
            Build your squad
          </Link>
        </div>
      </Card>
    );
  }

  const xi = pickBestXI(squad)!;
  const rating = rateTeam(squad, optimalProjected);
  const validation = validateSquad(squad);

  return (
    <Card>
      <CardTitle hint={`${xi.formation} · captain ${xi.captain.name.split(" ").pop()}`}>Your squad</CardTitle>
      <div className="flex items-center gap-4">
        <RatingDial value={rating.score} size={72} label="AI" />
        <div className="flex-1">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-muted">Projected (XI + captain)</span>
            <span className="num text-lg font-semibold text-fg">{rating.projectedPoints}</span>
          </div>
          <div className="mt-1.5">
            <Progress value={rating.score} tone={rating.score >= 70 ? "accent" : rating.score >= 45 ? "warn" : "danger"} />
          </div>
          <div className="mt-1.5 text-xs text-muted">
            {rating.vsOptimal >= -0.05 ? "Matches" : `${rating.vsOptimal.toFixed(1)} vs`} the engine-optimal XI ({optimalProjected})
          </div>
        </div>
      </div>

      {!validation.valid && (
        <div className="mt-3 rounded-lg border border-danger/40 bg-danger/10 p-2 text-xs text-danger">
          {validation.errors[0]}
        </div>
      )}

      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        <div>
          <div className="label mb-1">Strengths</div>
          {rating.strengths.length ? rating.strengths.map((s, i) => (
            <div key={i} className="flex gap-1.5 text-xs text-fg/80"><span className="text-accent">✓</span>{s}</div>
          )) : <div className="text-xs text-muted">—</div>}
        </div>
        <div>
          <div className="label mb-1">Watch-outs</div>
          {rating.weaknesses.length ? rating.weaknesses.map((s, i) => (
            <div key={i} className="flex gap-1.5 text-xs text-fg/80"><span className="text-warn">!</span>{s}</div>
          )) : <div className="text-xs text-muted">—</div>}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        <Badge tone="gold">C: {xi.captain.name.split(" ").pop()}</Badge>
        <Badge tone="info">VC: {xi.vice.name.split(" ").pop()}</Badge>
        <Link href="/transfers"><Badge tone="accent">Plan transfers →</Badge></Link>
      </div>
    </Card>
  );
}
