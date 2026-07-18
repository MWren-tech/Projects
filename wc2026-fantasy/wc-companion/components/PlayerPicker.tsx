"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Player, Position, NationFixture } from "@/types";
import { cn } from "@/lib/utils";
import { abbr, easeColor } from "@/lib/kits";
import { useSquad } from "@/lib/useSquad";
import { SegmentedControl } from "@/components/ui/primitives";

const ALL_POS: Position[] = ["GK", "DEF", "MID", "FWD"];
// One template drives the header AND every row so columns line up exactly.
const COLS = "grid grid-cols-[minmax(0,1fr)_2.6rem_2.4rem_2.4rem_2.6rem_2.6rem_1.6rem_1.8rem] items-center gap-1.5";

type SortKey = "name" | "xp" | "points" | "price" | "ownership" | "next" | "fixtureEase";
const DEFAULT_DIR: Record<SortKey, "asc" | "desc"> = {
  name: "asc", xp: "desc", points: "desc", price: "asc", ownership: "desc", next: "asc", fixtureEase: "desc",
};

// FIFA's authoritative tournament points so far (null until a player has featured).
function pointsOf(p: Player): number | null {
  return p.wcStats?.totalPoints ?? null;
}

export function PlayerPicker({
  players,
  fixtures,
  allowedPositions,
  mode = "browse",
  onSelect,
  disabledReason,
  heightClass = "max-h-[560px]",
}: {
  players: Player[];
  fixtures?: Record<string, NationFixture>;
  allowedPositions?: Position[];
  mode?: "browse" | "select";
  onSelect?: (p: Player) => void;
  disabledReason?: (p: Player) => string | null;
  heightClass?: string;
}) {
  const { has, add, remove } = useSquad();
  const fixedPos = allowedPositions && allowedPositions.length === 1 ? allowedPositions[0] : null;
  const [pos, setPos] = useState<Position | "ALL">(fixedPos ?? "ALL");
  const [q, setQ] = useState("");
  const [diffOnly, setDiffOnly] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("xp");
  const [dir, setDir] = useState<"asc" | "desc">("desc");

  const posChoices = allowedPositions ?? ALL_POS;

  function nextOf(p: Player) {
    return fixtures?.[p.nation]?.nextOpponent ?? "zzz";
  }
  function toggleSort(key: SortKey) {
    if (key === sortKey) setDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setDir(DEFAULT_DIR[key]); }
  }

  const rows = useMemo(() => {
    let r = players;
    if (allowedPositions) r = r.filter((p) => allowedPositions.includes(p.pos));
    if (pos !== "ALL") r = r.filter((p) => p.pos === pos);
    if (diffOnly) r = r.filter((p) => (p.ownership ?? 100) < 5);
    if (q) r = r.filter((p) => `${p.name} ${p.nation}`.toLowerCase().includes(q.toLowerCase()));
    const sign = dir === "asc" ? 1 : -1;
    return [...r].sort((a, b) => {
      if (sortKey === "name") return sign * a.name.localeCompare(b.name);
      if (sortKey === "next") return sign * nextOf(a).localeCompare(nextOf(b));
      const num = (p: Player) =>
        sortKey === "xp" ? p.xp
        : sortKey === "points" ? (pointsOf(p) ?? -1)
        : sortKey === "price" ? p.price
        : sortKey === "ownership" ? (p.ownership ?? -1)
        : p.fixtureEase;
      return sign * (num(a) - num(b));
    }).slice(0, 120);
  }, [players, allowedPositions, pos, q, diffOnly, sortKey, dir]);

  const SortBtn = ({ k, label, align }: { k: SortKey; label: string; align: "left" | "right" | "center" }) => {
    const active = sortKey === k;
    return (
      <button
        onClick={() => toggleSort(k)}
        aria-label={`Sort by ${label}${active ? `, currently ${dir === "asc" ? "ascending" : "descending"}` : ""}`}
        className={cn(
          "flex items-center gap-0.5 hover:text-fg",
          align === "right" ? "justify-end" : align === "center" ? "justify-center" : "justify-start",
          active && "text-fg"
        )}
      >
        {label}
        <span aria-hidden className="text-[8px]">{active ? (dir === "asc" ? "▲" : "▼") : ""}</span>
      </button>
    );
  };

  return (
    <div className="flex min-h-0 flex-col">
      <div className="flex flex-wrap items-center gap-2 pb-2">
        <label className="min-w-0 flex-1">
          <span className="sr-only">Search players</span>
          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search players…"
            className="w-full rounded-xl border border-border bg-surface-2 px-3 py-2 text-sm outline-none placeholder:text-muted focus:border-accent/50"
          />
        </label>
        {!fixedPos && (
          <SegmentedControl
            ariaLabel="Filter by position"
            value={pos}
            onChange={setPos}
            options={[{ value: "ALL" as const, label: "All" }, ...posChoices.map((p) => ({ value: p, label: p }))]}
          />
        )}
        <button
          onClick={() => setDiffOnly((v) => !v)}
          aria-pressed={diffOnly}
          className={cn("min-h-[32px] rounded-lg px-2.5 text-xs font-medium", diffOnly ? "bg-gold text-bg" : "bg-surface-2 text-muted hover:text-fg")}
        >
          Differentials
        </button>
      </div>

      <div className={cn("min-h-0 space-y-1 overflow-y-auto pr-1", heightClass)} role="region" aria-label="Player results">
        <div className={cn(COLS, "sticky top-0 z-10 border border-transparent bg-surface px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wide text-muted")}>
          <SortBtn k="name" label="Player" align="left" />
          <SortBtn k="xp" label="xPts" align="right" />
          <SortBtn k="points" label="Pts" align="right" />
          <SortBtn k="price" label="$m" align="right" />
          <SortBtn k="ownership" label="Own" align="right" />
          <SortBtn k="next" label="Next" align="center" />
          <SortBtn k="fixtureEase" label="Fix" align="center" />
          <span></span>
        </div>

        {rows.map((p) => {
          const reason = mode === "select" && disabledReason ? disabledReason(p) : null;
          const inSquad = has(p.id);
          const ease = easeColor(p.fixtureEase);
          const next = fixtures ? abbr(fixtures[p.nation]?.nextOpponent) : "—";
          return (
            <div key={p.id} className={cn(COLS, "rounded-xl border border-border bg-surface-2/50 px-2 py-1.5", reason && "opacity-40")}>
              <div className="min-w-0">
                <Link href={`/players/${p.id}`} className="block truncate text-sm font-medium text-fg hover:text-accent">{p.name}</Link>
                <div className="truncate text-[11px] text-muted">{p.nation} · {p.pos}</div>
              </div>
              <div className="num text-right text-sm font-semibold text-accent">{p.xp.toFixed(1)}</div>
              <div className="num text-right text-sm text-fg" title="FIFA tournament points so far">{pointsOf(p) != null ? pointsOf(p) : "—"}</div>
              <div className="num text-right text-sm text-fg">{p.price.toFixed(1)}</div>
              <div className={cn("num text-right text-xs", (p.ownership ?? 100) < 5 ? "font-semibold text-gold" : "text-muted")}>
                {p.ownership != null ? `${p.ownership}%` : "—"}
              </div>
              <div className="num text-center text-xs text-muted">{next}</div>
              <div className="flex justify-center" title={`Fixture: ${ease.label}`}>
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: ease.text }} />
                <span className="sr-only">{ease.label} fixture</span>
              </div>
              <div className="flex justify-end">
                {mode === "browse" ? (
                  <button
                    onClick={() => (inSquad ? remove(p.id) : add(p.id))}
                    aria-label={inSquad ? `Remove ${p.name}` : `Add ${p.name}`}
                    className={cn("grid h-7 w-7 place-items-center rounded-lg text-lg font-bold leading-none",
                      inSquad ? "bg-danger/15 text-danger hover:bg-danger/25" : "bg-accent/15 text-accent hover:bg-accent/25")}
                  >{inSquad ? "−" : "+"}</button>
                ) : (
                  <button
                    onClick={() => !reason && onSelect?.(p)}
                    disabled={!!reason}
                    aria-label={reason ? `${p.name} unavailable: ${reason}` : `Pick ${p.name}`}
                    title={reason ?? "Add"}
                    className="grid h-7 w-7 place-items-center rounded-lg bg-accent/15 text-lg font-bold leading-none text-accent hover:bg-accent/25 disabled:cursor-not-allowed disabled:opacity-50"
                  >+</button>
                )}
              </div>
            </div>
          );
        })}
        {rows.length === 0 ? <div className="py-8 text-center text-sm text-muted">No players match your filters.</div> : null}
      </div>
    </div>
  );
}
