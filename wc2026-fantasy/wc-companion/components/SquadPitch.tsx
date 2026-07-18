"use client";

import { useState } from "react";
import Link from "next/link";
import type { Player, Position, NationFixture } from "@/types";
import { SQUAD_REQ, type Lineup } from "@/lib/engine";
import { kitFor, abbr, easeColor } from "@/lib/kits";
import { cn, money } from "@/lib/utils";

type FixtureMap = Record<string, NationFixture>;
type SlotClick = (allowed: Position[], replaceId: string | null) => void;

const ROW_ORDER: Position[] = ["FWD", "MID", "DEF", "GK"];

export function SquadPitch({
  squad,
  lineup,
  fixtures,
  onRemove,
  onSlotClick,
  onSub,
  onReorderBench,
  getLegalSubs,
  toolbar,
}: {
  squad: Player[];
  lineup: Lineup | null;
  fixtures: FixtureMap;
  onRemove: (id: string) => void;
  onSlotClick: SlotClick;
  onSub: (starterId: string, benchId: string) => void;
  onReorderBench: (benchIds: string[]) => void;
  getLegalSubs: (starterId: string) => Player[];
  toolbar?: React.ReactNode;
}) {
  const shortPositions = (Object.keys(SQUAD_REQ) as Position[]).filter(
    (pos) => squad.filter((p) => p.pos === pos).length < SQUAD_REQ[pos]
  );

  if (!lineup) {
    const rows = ROW_ORDER.map((pos) => {
      const picked = squad.filter((p) => p.pos === pos);
      const slots: (Player | null)[] = [...picked];
      while (slots.length < SQUAD_REQ[pos]) slots.push(null);
      return { pos, slots };
    });
    return (
      <PitchShell formation="Building…" toolbar={toolbar}>
        {rows.map(({ pos, slots }) => (
          <Row key={pos}>
            {slots.map((p, j) =>
              p ? (
                <Shirt key={p.id} player={p} fixture={fixtures[p.nation]} onRemove={onRemove}
                  onClick={() => onSlotClick([p.pos], p.id)} />
              ) : (
                <EmptySlot key={`e-${pos}-${j}`} label={pos} onClick={() => onSlotClick([pos], null)} />
              )
            )}
          </Row>
        ))}
      </PitchShell>
    );
  }

  const benchIds = new Set(lineup.bench.map((p) => p.id));
  const benchSlots: (Player | null)[] = [...lineup.bench, ...Array(Math.max(0, 4 - lineup.bench.length)).fill(null)];

  function reorderSwap(aId: string, bId: string) {
    const order = lineup!.bench.map((p) => p.id);
    const i = order.indexOf(aId);
    const j = order.indexOf(bId);
    if (i < 0 || j < 0) return;
    [order[i], order[j]] = [order[j], order[i]];
    onReorderBench(order);
  }

  function dropOn(targetId: string, draggedId: string) {
    if (!draggedId || draggedId === targetId) return;
    const tBench = benchIds.has(targetId);
    const dBench = benchIds.has(draggedId);
    if (tBench && dBench) { reorderSwap(targetId, draggedId); return; } // reorder within bench
    if (tBench === dBench) return;
    const starterId = tBench ? draggedId : targetId;
    const benchId = tBench ? targetId : draggedId;
    onSub(starterId, benchId);
  }

  const rows = ROW_ORDER.map((pos) => ({ pos, slots: lineup.xi.filter((p) => p.pos === pos) }));

  const dugout = (
    <Dugout>
      {benchSlots.map((p, i) =>
        p ? (
          <Shirt key={p.id} player={p} fixture={fixtures[p.nation]} onRemove={onRemove}
            onClick={() => onSlotClick([p.pos], p.id)} benchOrder={i + 1} small draggable
            onDropPlayer={(dragged) => dropOn(p.id, dragged)}
            menuTitle="Reorder bench"
            menuItems={lineup.bench.filter((b) => b.id !== p.id)}
            onMenuPick={(otherId) => reorderSwap(p.id, otherId)} />
        ) : (
          <EmptySlot key={`be-${i}`} label="Sub" small
            onClick={() => onSlotClick(shortPositions.length ? shortPositions : ["GK", "DEF", "MID", "FWD"], null)} />
        )
      )}
    </Dugout>
  );

  return (
    <PitchShell formation={lineup.formation} dugout={dugout} toolbar={toolbar}>
      {rows.map(({ pos, slots }) => (
        <Row key={pos}>
          {slots.map((p) => (
            <Shirt key={p.id} player={p} fixture={fixtures[p.nation]} onRemove={onRemove}
              onClick={() => onSlotClick([p.pos], p.id)}
              isCaptain={p.id === lineup.captain.id} isVice={p.id === lineup.vice.id}
              draggable onDropPlayer={(dragged) => dropOn(p.id, dragged)}
              menuTitle="Sub on" menuItems={getLegalSubs(p.id)} onMenuPick={(benchId) => onSub(p.id, benchId)} />
          ))}
        </Row>
      ))}
    </PitchShell>
  );
}

function Shirt({
  player, fixture, onRemove, onClick, isCaptain, isVice, benchOrder, small,
  draggable, onDropPlayer, menuItems, onMenuPick, menuTitle,
}: {
  player: Player;
  fixture?: NationFixture;
  onRemove: (id: string) => void;
  onClick: () => void;
  isCaptain?: boolean;
  isVice?: boolean;
  benchOrder?: number;
  small?: boolean;
  draggable?: boolean;
  onDropPlayer?: (draggedId: string) => void;
  menuItems?: Player[];
  onMenuPick?: (id: string) => void;
  menuTitle?: string;
}) {
  const kit = kitFor(player.nation);
  const ease = easeColor(player.fixtureEase);
  const [menu, setMenu] = useState(false);

  return (
    <div
      className="group relative flex min-w-0 flex-col items-center"
      style={{ flexBasis: 0, flexGrow: 1, maxWidth: small ? 74 : 98 }}
      draggable={draggable}
      onDragStart={(e) => e.dataTransfer.setData("text/plain", player.id)}
      onDragOver={(e) => onDropPlayer && e.preventDefault()}
      onDrop={(e) => { if (!onDropPlayer) return; e.preventDefault(); onDropPlayer(e.dataTransfer.getData("text/plain")); }}
    >
      <div className="relative" style={{ width: "100%", maxWidth: small ? 44 : 56 }}>
        <button
          type="button"
          onClick={(e) => { e.stopPropagation(); onRemove(player.id); }}
          aria-label={`Remove ${player.name} from squad`}
          title="Remove from squad"
          className="absolute -right-2 -top-2 z-20 grid h-6 w-6 place-items-center rounded-full bg-danger text-[11px] font-bold text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 focus-visible:opacity-100"
        >✕</button>

        {menuItems && menuItems.length > 0 && (
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); setMenu((m) => !m); }}
            aria-label={`${menuTitle ?? "Options"} for ${player.name}`}
            aria-haspopup="menu"
            aria-expanded={menu}
            title={menuTitle ?? "Options"}
            className="absolute -left-2 top-5 z-20 grid h-6 w-6 place-items-center rounded-full bg-info text-[11px] font-bold text-bg opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 focus-visible:opacity-100"
          >⇅</button>
        )}

        {(isCaptain || isVice || benchOrder) && (
          <span
            role="img"
            aria-label={isCaptain ? "Captain" : isVice ? "Vice-captain" : `Bench ${benchOrder}`}
            className={cn(
              "absolute -left-2 -top-2 z-20 grid h-5 w-5 place-items-center rounded-full text-[10px] font-bold ring-2 ring-surface",
              isCaptain ? "bg-gold text-bg" : isVice ? "bg-info text-bg" : "bg-surface-2 text-muted"
            )}
          >
            {isCaptain ? "C" : isVice ? "V" : benchOrder}
          </span>
        )}

        <button
          type="button"
          onClick={onClick}
          aria-label={`Transfer ${player.name} — ${player.pos}, ${player.nation}`}
          className="block w-full cursor-pointer rounded-md transition-transform hover:-translate-y-0.5"
        >
          <JerseySVG bg={kit.bg} text={kit.text} />
        </button>
      </div>

      {/* Dark name plate for readability over the green pitch. */}
      <div className="mt-1.5 w-full rounded-lg bg-black/60 px-1 py-1 text-center shadow-sm ring-1 ring-white/5">
        <Link href={`/players/${player.id}`}
          className="block truncate text-[12px] font-bold leading-tight text-white hover:text-accent">
          {player.name.split(" ").pop()}
        </Link>
        <div className="mt-0.5 flex items-center justify-center gap-1">
          <span className="rounded bg-white/10 px-1 py-px text-[8px] font-bold uppercase leading-none text-white/75">
            {player.pos}
          </span>
          <span className="truncate text-[9px] font-medium uppercase tracking-wide text-white/55">{player.nation}</span>
        </div>

        <div className="mt-1 flex items-center justify-center">
          <span className="inline-block max-w-full truncate rounded px-1.5 py-0.5 text-[10px] font-bold"
            style={{ background: ease.bg, color: ease.text }}
            title={`Next: ${fixture?.nextOpponent ?? "TBD"} · ${ease.label}`}>
            vs {abbr(fixture?.nextOpponent)}
          </span>
        </div>

        <div className="num mt-1 flex items-center justify-center gap-1.5 text-[11px] leading-none">
          <span className="font-semibold text-white">{money(player.price)}</span>
          <span className="text-white/40">·</span>
          <span className="text-white/70">{player.ownership ?? "?"}%</span>
        </div>
      </div>

      {menu && menuItems && (
        <div
          role="menu"
          aria-label={`${menuTitle ?? "Options"} for ${player.name}`}
          onKeyDown={(e) => { if (e.key === "Escape") setMenu(false); }}
          className="absolute top-12 z-30 w-40 rounded-xl border border-border bg-surface p-1 shadow-[var(--elev-2)]"
        >
          <div className="px-2 py-1 text-[10px] uppercase tracking-wide text-muted">{menuTitle ?? "Options"}</div>
          {menuItems.map((b) => (
            <button key={b.id} role="menuitem"
              onClick={(e) => { e.stopPropagation(); onMenuPick?.(b.id); setMenu(false); }}
              className="block w-full truncate rounded-lg px-2 py-1.5 text-left text-xs text-fg hover:bg-surface-2">
              {b.name.split(" ").pop()} <span className="text-muted">({b.pos})</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function EmptySlot({ label, onClick, small }: { label: string; onClick: () => void; small?: boolean }) {
  return (
    <button onClick={onClick} className="flex min-w-0 flex-col items-center transition hover:-translate-y-0.5"
      style={{ flexBasis: 0, flexGrow: 1, maxWidth: small ? 74 : 98 }}>
      <div className="relative mx-auto" style={{ width: "100%", maxWidth: small ? 42 : 54 }}>
        <JerseySVG bg="#161b23" text="#39414f" />
        <span className="absolute inset-0 grid translate-y-[1px] place-items-center text-lg font-bold text-fg/40">+</span>
      </div>
      <div className="mt-1 truncate text-[10px] uppercase tracking-wide text-muted/70">{label}</div>
    </button>
  );
}

function PitchShell({ formation, children, dugout, toolbar }: { formation: string; children: React.ReactNode; dugout?: React.ReactNode; toolbar?: React.ReactNode }) {
  return (
    <section className="card overflow-hidden p-0" aria-label="Squad pitch">
      <div className="flex items-center justify-between gap-2 border-b border-border px-4 py-2.5">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-fg">Your XI</h2>
          <span className="chip border-accent/40 bg-accent/10 text-accent" aria-label={`Formation ${formation}`}>{formation}</span>
        </div>
        {toolbar}
      </div>
      <div className="relative px-2 py-5 sm:px-3" style={pitchStyle}>
        <PitchMarkings />
        <div className="relative z-10 flex flex-col gap-5">{children}</div>
      </div>
      {dugout}
    </section>
  );
}

function Row({ children }: { children: React.ReactNode }) {
  return <div className="flex flex-nowrap items-start justify-center gap-1.5 sm:gap-2.5">{children}</div>;
}

function Dugout({ children }: { children: React.ReactNode }) {
  return (
    <div className="border-t-2 border-border bg-gradient-to-b from-surface-2 to-surface">
      <div className="flex items-center justify-between border-b border-border/60 px-4 py-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted">Substitutes&apos; bench</span>
        <span className="hidden text-[11px] text-muted sm:block">drag a sub onto the pitch to swap</span>
      </div>
      <div className="flex flex-nowrap items-start justify-center gap-2 px-3 py-4">{children}</div>
    </div>
  );
}

function JerseySVG({ bg, text }: { bg: string; text: string }) {
  return (
    <svg viewBox="0 0 48 42" className="h-auto w-full drop-shadow">
      <path d="M16 3 L24 7 L32 3 L46 10 L40 19 L34 16 L34 40 L14 40 L14 16 L8 19 L2 10 Z"
        fill={bg} stroke="rgba(0,0,0,0.35)" strokeWidth="1.2" />
      <path d="M19 4 L24 9 L29 4" fill="none" stroke={text} strokeWidth="2" />
      <path d="M40 19 L34 16 M8 19 L14 16" stroke={text} strokeWidth="1.5" opacity="0.6" />
    </svg>
  );
}

const pitchStyle: React.CSSProperties = {
  background: "repeating-linear-gradient(0deg, #0f5132 0px, #0f5132 36px, #11603a 36px, #11603a 72px)",
};

function PitchMarkings() {
  return (
    <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-25" preserveAspectRatio="none" viewBox="0 0 100 140">
      <g fill="none" stroke="#ffffff" strokeWidth="0.4">
        <rect x="2" y="2" width="96" height="136" />
        <line x1="2" y1="70" x2="98" y2="70" />
        <circle cx="50" cy="70" r="11" />
        <circle cx="50" cy="70" r="0.8" fill="#fff" />
        <rect x="28" y="2" width="44" height="20" />
        <rect x="40" y="2" width="20" height="8" />
        <rect x="28" y="118" width="44" height="20" />
        <rect x="40" y="130" width="20" height="8" />
      </g>
    </svg>
  );
}
