import type { WcStats } from "@/types";
import { Card, CardTitle, Badge } from "@/components/ui/primitives";
import { cn } from "@/lib/utils";

// Actual World Cup tournament return for a player, with the fantasy points each
// stat has yielded under the official scoring rules.
export function WcStatsCard({ stats, name }: { stats: WcStats | null; name: string }) {
  if (!stats) {
    return (
      <Card>
        <CardTitle>World Cup so far</CardTitle>
        <div className="py-6 text-center text-sm text-muted">
          {name.split(" ").pop()} hasn&apos;t recorded any minutes yet — no tournament points so far.
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardTitle hint={stats.official ? "FIFA official" : "estimated"}>World Cup so far</CardTitle>

      <div className="flex items-stretch gap-3">
        <div className="grid place-items-center rounded-xl bg-accent/10 px-4 py-2 text-center ring-1 ring-accent/30">
          <div className="num text-3xl font-bold text-accent">{stats.totalPoints}</div>
          <div className="text-[11px] uppercase tracking-wide text-muted">Fantasy pts</div>
        </div>
        <div className="grid flex-1 grid-cols-2 gap-2 sm:grid-cols-4">
          <Mini label="Apps" value={`${stats.appearances}`} sub={`${stats.starts} starts`} />
          <Mini label="Minutes" value={`${stats.minutes}`} />
          <Mini label="G / A" value={`${stats.goals} / ${stats.assists}`} />
          <Mini label="Avg rating" value={stats.rating != null ? stats.rating.toFixed(2) : "—"} />
        </div>
      </div>

      <div className="mt-4">
        <div className="label mb-1.5">Points breakdown</div>
        {stats.breakdown.length === 0 ? (
          <p className="text-sm text-muted">No point-scoring actions yet.</p>
        ) : (
          <ul className="divide-y divide-border/60">
            {stats.breakdown.map((l, i) => (
              <li key={i} className="grid grid-cols-[1fr_auto_auto] items-center gap-3 py-1.5 text-sm">
                <span className="text-fg/90">{l.label}</span>
                <span className="num text-muted">{l.count != null ? `×${l.count}` : ""}</span>
                <span className={cn("num w-10 text-right font-semibold", l.pts >= 0 ? "text-accent" : "text-danger")}>
                  {l.pts >= 0 ? `+${l.pts}` : l.pts}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <p className="mt-3 text-[11px] leading-relaxed text-muted">
        {stats.official
          ? "Total is FIFA's official figure. The breakdown is from a secondary stats provider and can differ slightly (e.g. assist attribution); any gap is shown as an “official scoring” line so it reconciles to the FIFA total."
          : "Estimated from the stats provider — FIFA's official points weren't available for this player."}
      </p>
    </Card>
  );
}

function Mini({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="card-2 px-2.5 py-1.5">
      <div className="label">{label}</div>
      <div className="num text-base font-semibold text-fg">{value}</div>
      {sub ? <div className="text-[10px] text-muted">{sub}</div> : null}
    </div>
  );
}
