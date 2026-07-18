import Link from "next/link";
import { getSnapshot } from "@/lib/snapshot";
import { PageHeader, PosBadge, EaseBadge, RatingDial } from "@/components/widgets";
import { Card, CardTitle, Badge, Stat } from "@/components/ui/primitives";
import { money } from "@/lib/utils";
import { DashboardSquad } from "@/components/DashboardSquad";

export default function Dashboard() {
  const snap = getSnapshot();
  const { optimalSquad: opt, boosterPlan, players, fixtures, meta } = snap;

  const topPicks = players.slice(0, 6);
  const differentials = players.filter((p) => (p.ownership ?? 100) < 5).slice(0, 4);
  const nextBoost = Object.entries(boosterPlan.schedule).sort((a, b) =>
    (a[1].round || "z").localeCompare(b[1].round || "z")
  )[0];

  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle={`World Cup 2026 · ${meta.currentRound} · ${meta.playerCount} players · engine ${new Date(
          meta.generatedAt
        ).toLocaleDateString()}`}
        action={
          <Link href="/chat" className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-bg">
            Ask the AI
          </Link>
        }
      />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Stat label="Engine optimal XI" value={opt.projectedPoints} sub="projected pts incl. captain" />
        <Stat label="Captain pick" value={opt.captain.name.split(" ").pop()!} sub={`${opt.captain.xp} xPts · ${opt.captain.nation}`} />
        <Stat label="Next booster" value={nextBoost?.[0] ?? "—"} sub={nextBoost ? `play ${nextBoost[1].round}` : ""} />
        <Stat label="Top differential" value={differentials[0]?.name.split(" ").pop() ?? "—"} sub={differentials[0] ? `${differentials[0].ownership}% owned` : ""} />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <DashboardSquad players={players} optimalProjected={opt.projectedPoints} />

          <Card>
            <CardTitle hint="ranked by xPts">Top recommendations</CardTitle>
            <div className="grid gap-2 sm:grid-cols-2">
              {topPicks.map((p) => (
                <Link key={p.id} href={`/players/${p.id}`} className="card-2 flex items-center justify-between p-3 hover:shadow-glow">
                  <div className="min-w-0">
                    <div className="truncate font-medium text-fg">{p.name}</div>
                    <div className="text-xs text-muted">{p.nation} · {money(p.price)}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <EaseBadge value={p.fixtureEase} />
                    <span className="num font-semibold text-accent">{p.xp.toFixed(1)}</span>
                    <PosBadge pos={p.pos} />
                  </div>
                </Link>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardTitle>Booster schedule</CardTitle>
            <div className="space-y-2">
              {Object.entries(boosterPlan.schedule).map(([chip, s]) => (
                <div key={chip} className="flex items-center justify-between text-sm">
                  <span className="text-fg">{chip}</span>
                  <div className="flex items-center gap-2">
                    {s.ev != null ? <span className="num text-xs text-muted">+{s.ev}</span> : null}
                    <Badge tone="accent">{s.round}</Badge>
                  </div>
                </div>
              ))}
            </div>
            <Link href="/boosts" className="mt-3 block text-center text-xs text-accent hover:underline">
              Full boost strategy →
            </Link>
          </Card>

          <Card>
            <CardTitle>Differentials</CardTitle>
            <div className="space-y-2">
              {differentials.map((p) => (
                <Link key={p.id} href={`/players/${p.id}`} className="flex items-center justify-between text-sm hover:text-accent">
                  <span className="truncate text-fg">{p.name}</span>
                  <Badge tone="gold">{p.ownership}%</Badge>
                </Link>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}
