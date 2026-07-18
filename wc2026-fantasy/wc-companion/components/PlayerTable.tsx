"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Player, Position } from "@/types";
import { money, cn } from "@/lib/utils";
import { PosBadge, EaseBadge } from "@/components/widgets";
import { Badge } from "@/components/ui/primitives";
import { useSquad } from "@/lib/useSquad";

const POSITIONS: (Position | "ALL")[] = ["ALL", "GK", "DEF", "MID", "FWD"];
type SortKey = "xp" | "price" | "ownership" | "value" | "differential" | "points";

// FIFA's authoritative tournament points so far (null until a player has featured).
function pointsOf(p: Player): number | null {
  return p.wcStats?.totalPoints ?? null;
}

export function PlayerTable({ players, addable = false }: { players: Player[]; addable?: boolean }) {
  const [pos, setPos] = useState<Position | "ALL">("ALL");
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<SortKey>("xp");
  const [diffOnly, setDiffOnly] = useState(false);
  const { has, add, remove } = useSquad();

  const rows = useMemo(() => {
    let r = players;
    if (pos !== "ALL") r = r.filter((p) => p.pos === pos);
    if (diffOnly) r = r.filter((p) => (p.ownership ?? 100) < 5);
    if (q) r = r.filter((p) => `${p.name} ${p.nation}`.toLowerCase().includes(q.toLowerCase()));
    const num = (p: Player) => (sort === "points" ? (pointsOf(p) ?? -1) : (p[sort] ?? 0));
    return [...r].sort((a, b) => num(b) - num(a)).slice(0, 120);
  }, [players, pos, q, sort, diffOnly]);

  return (
    <div className="card overflow-hidden">
      <div className="flex flex-wrap items-center gap-2 border-b border-border p-3">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search player or nation…"
          className="w-48 rounded-xl border border-border bg-surface-2 px-3 py-1.5 text-sm outline-none focus:border-accent/50"
        />
        <div className="flex gap-1">
          {POSITIONS.map((p) => (
            <button
              key={p}
              onClick={() => setPos(p)}
              className={cn("rounded-lg px-2.5 py-1 text-xs", pos === p ? "bg-accent text-bg font-semibold" : "text-muted hover:bg-surface-2")}
            >
              {p}
            </button>
          ))}
        </div>
        <button
          onClick={() => setDiffOnly((v) => !v)}
          className={cn("rounded-lg px-2.5 py-1 text-xs", diffOnly ? "bg-gold text-bg font-semibold" : "text-muted hover:bg-surface-2")}
        >
          Differentials
        </button>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
          className="ml-auto rounded-xl border border-border bg-surface-2 px-2 py-1.5 text-sm outline-none"
        >
          <option value="xp">Sort: xPts</option>
          <option value="points">Sort: Points</option>
          <option value="value">Sort: Value</option>
          <option value="differential">Sort: Differential</option>
          <option value="ownership">Sort: Ownership</option>
          <option value="price">Sort: Price</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-[11px] uppercase tracking-wide text-muted">
              <th className="px-3 py-2">Player</th>
              <th className="px-2">Pos</th>
              <th className="px-2 text-right">Price</th>
              <th className="px-2 text-right">xPts</th>
              <th className="px-2 text-right" title="FIFA tournament points so far">Pts</th>
              <th className="px-2 text-right">Own</th>
              <th className="px-2 text-right">Value</th>
              <th className="px-2">Fixture</th>
              {addable ? <th className="px-2"></th> : null}
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id} className="border-b border-border/50 hover:bg-surface-2/50">
                <td className="px-3 py-2">
                  <Link href={`/players/${p.id}`} className="font-medium text-fg hover:text-accent">{p.name}</Link>
                  <div className="text-[11px] text-muted">{p.nation}</div>
                </td>
                <td className="px-2"><PosBadge pos={p.pos} /></td>
                <td className="num px-2 text-right text-fg">{money(p.price)}</td>
                <td className="num px-2 text-right font-semibold text-accent">{p.xp.toFixed(1)}</td>
                <td className="num px-2 text-right text-fg">{pointsOf(p) != null ? pointsOf(p) : "—"}</td>
                <td className="num px-2 text-right text-muted">{p.ownership != null ? `${p.ownership}%` : "—"}</td>
                <td className="num px-2 text-right text-fg">{p.value.toFixed(2)}</td>
                <td className="px-2"><EaseBadge value={p.fixtureEase} /></td>
                {addable ? (
                  <td className="px-2 text-right">
                    <button
                      onClick={() => (has(p.id) ? remove(p.id) : add(p.id))}
                      className={cn("rounded-lg px-2 py-1 text-xs font-semibold", has(p.id) ? "bg-danger/15 text-danger" : "bg-accent/15 text-accent")}
                    >
                      {has(p.id) ? "Remove" : "Add"}
                    </button>
                  </td>
                ) : null}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
