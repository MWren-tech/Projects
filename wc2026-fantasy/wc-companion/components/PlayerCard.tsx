import Link from "next/link";
import type { Player } from "@/types";
import { money } from "@/lib/utils";
import { PosBadge, EaseBadge } from "@/components/widgets";
import { Badge } from "@/components/ui/primitives";

export function PlayerCard({ player, onAdd, added }: { player: Player; onAdd?: () => void; added?: boolean }) {
  const isDiff = (player.ownership ?? 100) < 5;
  return (
    <div className="card p-3 transition hover:shadow-glow">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <Link href={`/players/${player.id}`} className="block truncate font-semibold text-fg hover:text-accent">
            {player.name}
          </Link>
          <div className="mt-0.5 truncate text-xs text-muted">
            {player.nation}{player.club ? ` · ${player.club}` : ""}
          </div>
        </div>
        <PosBadge pos={player.pos} />
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2 text-center">
        <Metric label="xPts" value={player.xp.toFixed(1)} accent />
        <Metric label="Price" value={money(player.price)} />
        <Metric label="Own" value={player.ownership != null ? `${player.ownership}%` : "—"} />
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-1.5">
        <EaseBadge value={player.fixtureEase} />
        {isDiff ? <Badge tone="gold">Differential</Badge> : null}
        {player.setPieces ? <Badge tone="info">{player.setPieces}</Badge> : null}
        {player.startProb >= 0.9 ? <Badge tone="accent">Nailed</Badge> : player.startProb < 0.6 ? <Badge tone="danger">Rotation</Badge> : null}
      </div>

      {onAdd ? (
        <button
          onClick={onAdd}
          disabled={added}
          className="mt-3 w-full rounded-xl border border-accent/40 bg-accent/10 py-1.5 text-sm font-semibold text-accent transition hover:bg-accent/20 disabled:opacity-40"
        >
          {added ? "In squad" : "+ Add"}
        </button>
      ) : null}
    </div>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="card-2 py-1.5">
      <div className="label">{label}</div>
      <div className={`num text-sm font-semibold ${accent ? "text-accent" : "text-fg"}`}>{value}</div>
    </div>
  );
}
