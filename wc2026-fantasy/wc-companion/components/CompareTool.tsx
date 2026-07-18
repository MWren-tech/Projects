"use client";

import { useState } from "react";
import type { Player } from "@/types";
import { Card, Badge } from "@/components/ui/primitives";
import { PosBadge, EaseBadge } from "@/components/widgets";
import { money, cn } from "@/lib/utils";

export function CompareTool({ players }: { players: Player[] }) {
  const [a, setA] = useState<Player | null>(players[0] ?? null);
  const [b, setB] = useState<Player | null>(players[1] ?? null);

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <Picker label="Player A" players={players} value={a} onChange={setA} />
        <Picker label="Player B" players={players} value={b} onChange={setB} />
      </div>

      {a && b ? (
        <Card>
          <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2">
            <Header p={a} />
            <div className="text-center text-xs text-muted">vs</div>
            <Header p={b} align="right" />
          </div>
          <div className="mt-4 space-y-1">
            <Row label="Projected pts" a={a.xp} b={b.xp} fmt={(v) => v.toFixed(1)} higher />
            <Row label="Price" a={a.price} b={b.price} fmt={money} higher={false} />
            <Row label="Value (pts/$m)" a={a.value} b={b.value} fmt={(v) => v.toFixed(2)} higher />
            <Row label="Ownership %" a={a.ownership ?? 0} b={b.ownership ?? 0} fmt={(v) => `${v}%`} higher={false} />
            <Row label="Differential" a={a.differential} b={b.differential} fmt={(v) => `${v}`} higher />
            <Row label="Goals / 90" a={a.g90} b={b.g90} fmt={(v) => v.toFixed(2)} higher />
            <Row label="Assists / 90" a={a.a90} b={b.a90} fmt={(v) => v.toFixed(2)} higher />
            <Row label="Start prob" a={a.startProb == null ? null : a.startProb * 100} b={b.startProb == null ? null : b.startProb * 100} fmt={(v) => `${Math.round(v)}%`} higher />
            <Row label="Fixture ease" a={a.fixtureEase} b={b.fixtureEase} fmt={(v) => v.toFixed(2)} higher />
            <Row label="Clean sheet %" a={(a.cleanSheet ?? 0) * 100} b={(b.cleanSheet ?? 0) * 100} fmt={(v) => `${Math.round(v)}%`} higher />
          </div>
          <div className="mt-4 rounded-xl border border-accent/30 bg-accent/5 p-3 text-sm">
            <span className="text-muted">Engine verdict: </span>
            <span className="font-semibold text-fg">
              {a.xp >= b.xp ? a.name : b.name}
            </span>{" "}
            <span className="text-muted">
              projects higher ({Math.max(a.xp, b.xp).toFixed(1)} vs {Math.min(a.xp, b.xp).toFixed(1)} xPts).
            </span>
          </div>
        </Card>
      ) : null}
    </div>
  );
}

function Picker({ label, players, value, onChange }: { label: string; players: Player[]; value: Player | null; onChange: (p: Player) => void }) {
  return (
    <div className="card-2 p-3">
      <div className="label mb-1">{label}</div>
      <select
        value={value?.id ?? ""}
        onChange={(e) => onChange(players.find((p) => p.id === e.target.value)!)}
        className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm outline-none"
      >
        {players.map((p) => (
          <option key={p.id} value={p.id}>{p.name} — {p.nation} ({p.pos})</option>
        ))}
      </select>
    </div>
  );
}

function Header({ p, align = "left" }: { p: Player; align?: "left" | "right" }) {
  return (
    <div className={cn(align === "right" && "text-right")}>
      <div className="font-semibold text-fg">{p.name}</div>
      <div className="text-xs text-muted">{p.nation}{p.club ? ` · ${p.club}` : ""}</div>
      <div className={cn("mt-1 flex gap-1.5", align === "right" && "justify-end")}>
        <PosBadge pos={p.pos} />
        <EaseBadge value={p.fixtureEase} />
      </div>
    </div>
  );
}

function Row({ label, a, b, fmt, higher }: { label: string; a: number | null; b: number | null; fmt: (v: number) => string; higher: boolean }) {
  const bothSet = a != null && b != null;
  const aWins = bothSet && (higher ? a! > b! : a! < b!);
  const bWins = bothSet && (higher ? b! > a! : b! < a!);
  return (
    <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 border-b border-border/40 py-1.5 text-sm">
      <div className={cn("num text-left", aWins ? "font-semibold text-accent" : "text-muted")}>{a == null ? "—" : fmt(a)}</div>
      <div className="px-2 text-center text-[11px] uppercase tracking-wide text-muted">{label}</div>
      <div className={cn("num text-right", bWins ? "font-semibold text-accent" : "text-muted")}>{b == null ? "—" : fmt(b)}</div>
    </div>
  );
}
