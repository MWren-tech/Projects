import type { RoundPoints } from "@/types";
import { Card, CardTitle } from "@/components/ui/primitives";
import { cn } from "@/lib/utils";

// Per-game (per-round) breakdown of a player's FIFA official points, read
// straight from snapshot `roundPoints`. Sums to wcStats.totalPoints; an empty
// array means the player hasn't featured yet.
export function RoundBreakdownCard({ rounds, name }: { rounds: RoundPoints[]; name: string }) {
  if (rounds.length === 0) {
    return (
      <Card>
        <CardTitle hint="per round">Round-by-round</CardTitle>
        <div className="py-6 text-center text-sm text-muted">
          {name.split(" ").pop()} hasn&apos;t featured yet — no per-round points to show.
        </div>
      </Card>
    );
  }

  const total = rounds.reduce((sum, r) => sum + r.pts, 0);
  const max = Math.max(1, ...rounds.map((r) => Math.abs(r.pts)));

  return (
    <Card>
      <CardTitle hint="FIFA official">Round-by-round</CardTitle>

      <ul className="space-y-1.5">
        {rounds.map((r, i) => {
          const positive = r.pts >= 0;
          return (
            <li key={i} className="grid grid-cols-[3rem_1fr_2.5rem] items-center gap-3 text-sm">
              <span className="label">{r.round}</span>
              <span className="h-2 rounded-full bg-border/60" aria-hidden>
                <span
                  className={cn("block h-full rounded-full", positive ? "bg-accent" : "bg-danger")}
                  style={{ width: `${(Math.abs(r.pts) / max) * 100}%` }}
                />
              </span>
              <span
                className={cn("num text-right font-semibold", positive ? "text-accent" : "text-danger")}
              >
                {positive ? `+${r.pts}` : r.pts}
              </span>
            </li>
          );
        })}
      </ul>

      <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2 text-sm">
        <span className="text-muted">Total ({rounds.length} {rounds.length === 1 ? "round" : "rounds"})</span>
        <span className="num font-semibold text-accent">{total >= 0 ? `+${total}` : total}</span>
      </div>

      <p className="mt-3 text-[11px] leading-relaxed text-muted">
        FIFA&apos;s official per-round points. The sum reconciles to the tournament total above.
      </p>
    </Card>
  );
}
