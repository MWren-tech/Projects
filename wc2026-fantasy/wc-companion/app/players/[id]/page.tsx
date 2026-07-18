import { notFound } from "next/navigation";
import Link from "next/link";
import { getPlayerById, getSnapshot } from "@/lib/snapshot";
import { PageHeader, PosBadge, EaseBadge, RatingDial, StatBar } from "@/components/widgets";
import { Card, CardTitle, Badge, Stat } from "@/components/ui/primitives";
import { money } from "@/lib/utils";
import { PlayerAIExplain } from "@/components/PlayerAIExplain";
import { WcStatsCard } from "@/components/WcStatsCard";
import { RoundBreakdownCard } from "@/components/RoundBreakdownCard";

export default function PlayerProfile({ params }: { params: { id: string } }) {
  const player = getPlayerById(params.id);
  if (!player) notFound();
  const snap = getSnapshot();
  const fixture = snap.fixtures[player.nation];
  const isDiff = (player.ownership ?? 100) < 5;

  return (
    <>
      <Link href="/players" className="mb-3 inline-block text-sm text-muted hover:text-accent">← All players</Link>
      <PageHeader
        title={player.name}
        subtitle={`${player.nation}${player.club ? ` · ${player.club}` : ""}`}
        action={<PosBadge pos={player.pos} />}
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <WcStatsCard stats={player.wcStats} name={player.name} />

          <RoundBreakdownCard rounds={player.roundPoints} name={player.name} />

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Stat label="Price" value={money(player.price)} />
            <Stat label="Proj. pts" value={player.xp.toFixed(1)} sub={player.scoutingBonus ? `per match · +${player.scoutingBonus} diff bonus` : "per match"} />
            <Stat label="Ownership" value={player.ownership != null ? `${player.ownership}%` : "—"} />
            <Stat label="Value" value={player.value.toFixed(2)} sub="pts / $m" />
          </div>

          <Card>
            <CardTitle hint="per-90 form">Form & output</CardTitle>
            <div className="grid gap-3 sm:grid-cols-2">
              <StatBar label="Goals / 90" value={player.g90} max={1.2} />
              <StatBar label="Assists / 90" value={player.a90} max={0.9} />
              <StatBar label="Start probability" value={Math.round(player.startProb * 100)} max={100} suffix="%" />
              <StatBar label="Clean sheet %" value={Math.round((player.cleanSheet ?? 0) * 100)} max={100} suffix="%" />
            </div>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {player.setPieces ? <Badge tone="info">Set pieces: {player.setPieces}</Badge> : null}
              {player.rating ? <Badge tone="muted">Avg rating {player.rating}</Badge> : null}
              <Badge tone="muted">{player.goals ?? 0} G · {player.assists ?? 0} A (season)</Badge>
            </div>
          </Card>

          <PlayerAIExplain player={player} />
        </div>

        <div className="space-y-4">
          <Card>
            <CardTitle>AI metrics</CardTitle>
            <div className="flex items-center justify-around py-2">
              <div className="text-center">
                <RatingDial value={player.aiRating} size={72} label="rating" />
                <div className="mt-1 text-xs text-muted">vs position</div>
              </div>
              <div className="text-center">
                <RatingDial value={player.differential} size={72} label="diff" />
                <div className="mt-1 text-xs text-muted">differential</div>
              </div>
            </div>
          </Card>

          <Card>
            <CardTitle>Fixtures</CardTitle>
            {fixture ? (
              <div className="space-y-2 text-sm">
                <Row label="Next opponent" value={fixture.nextOpponent ?? "TBD"} />
                <Row label="Fixture ease" value={<EaseBadge value={fixture.fixtureEase} />} />
                <Row label="Clean sheet" value={fixture.cleanSheet != null ? `${Math.round(fixture.cleanSheet * 100)}%` : "—"} />
                <Row label="Upcoming" value={fixture.opponents.join(", ") || "—"} />
              </div>
            ) : (
              <p className="text-sm text-muted">No fixture data.</p>
            )}
          </Card>

          {isDiff ? (
            <Card>
              <div className="flex items-center gap-2 text-gold">
                <Badge tone="gold">Differential</Badge>
                <span className="text-xs text-muted">Sub-5% owned — gains rank if he hauls.</span>
              </div>
            </Card>
          ) : null}
        </div>
      </div>
    </>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted">{label}</span>
      <span className="text-fg">{value}</span>
    </div>
  );
}
