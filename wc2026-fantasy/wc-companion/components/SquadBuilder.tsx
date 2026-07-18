"use client";

import { useMemo, useState } from "react";
import type { Player, Position, NationFixture } from "@/types";
import { useSquad } from "@/lib/useSquad";
import { validateSquad, rateTeam, buildLineup, computeSwap, legalSubsFor, SQUAD_REQ } from "@/lib/engine";
import { Card, Badge, Button, Progress, Alert, Skeleton } from "@/components/ui/primitives";
import { RatingDial } from "@/components/widgets";
import { PlayerPicker } from "@/components/PlayerPicker";
import { SquadPitch } from "@/components/SquadPitch";
import { SlotPickerModal, type SlotTarget } from "@/components/SlotPickerModal";
import { money, cn } from "@/lib/utils";
import { Users, Sparkles, RotateCcw } from "lucide-react";

const POS_ORDER: Position[] = ["GK", "DEF", "MID", "FWD"];

export function SquadBuilder({
  players,
  optimalProjected,
  optimalSquadIds,
  fixtures,
}: {
  players: Player[];
  optimalProjected: number;
  optimalSquadIds: string[];
  fixtures: Record<string, NationFixture>;
}) {
  const { ids, bench, add, remove, clear, set, saveToDb, setBench, loaded } = useSquad();
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [target, setTarget] = useState<SlotTarget | null>(null);
  const map = useMemo(() => new Map(players.map((p) => [p.id, p])), [players]);
  const squad = ids.map((id) => map.get(id)).filter(Boolean) as Player[];

  const v = validateSquad(squad);
  const lineup = useMemo(() => buildLineup(squad, bench.length ? bench : undefined), [squad, bench]);
  const rating = lineup ? rateTeam(squad, optimalProjected) : null;
  const effectiveBench = lineup ? lineup.bench.map((p) => p.id) : [];
  const counts = useMemo(() => {
    const c: Record<Position, number> = { GK: 0, DEF: 0, MID: 0, FWD: 0 };
    for (const p of squad) c[p.pos]++;
    return c;
  }, [squad]);

  async function onSave() {
    setSaving(true);
    await saveToDb();
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2200);
  }
  function handlePick(p: Player) {
    if (target?.replaceId) remove(target.replaceId);
    add(p.id);
    setTarget(null);
  }
  function handleSub(starterId: string, benchId: string) {
    const next = computeSwap(squad, effectiveBench, starterId, benchId);
    if (next) setBench(next);
  }
  // Reordering the bench keeps the same players (starters unchanged), so it's always valid.
  function handleReorderBench(benchIds: string[]) {
    setBench(benchIds);
  }

  if (!loaded) return <BuilderSkeleton />;

  const budgetPct = (v.totalPrice / 100) * 100;
  const overBudget = v.totalPrice > 100;

  return (
    <div className="space-y-4">
      {/* ---------- Status bar: visibility of system status ---------- */}
      <Card as="section" aria-label="Squad summary" className="sticky top-2 z-30 backdrop-blur supports-[backdrop-filter]:bg-surface/80">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-4">
          {/* completion + positions */}
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-surface-2 text-accent">
              <Users className="h-5 w-5" aria-hidden />
            </div>
            <div>
              <div className="num text-xl font-bold leading-none text-fg">
                {squad.length}<span className="text-muted">/15</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {POS_ORDER.map((pos) => (
                  <PositionPip key={pos} pos={pos} have={counts[pos]} need={SQUAD_REQ[pos]} />
                ))}
              </div>
            </div>
          </div>

          {/* budget */}
          <div className="min-w-[200px] flex-1">
            <div className="flex items-center justify-between text-xs">
              <span className="label">Budget</span>
              <span className={cn("num font-semibold", overBudget ? "text-danger" : "text-fg")}>
                {money(v.totalPrice)} <span className="text-muted">/ $100.0m</span>
              </span>
            </div>
            <div className="mt-1.5">
              <Progress value={budgetPct} tone={overBudget ? "danger" : budgetPct > 92 ? "warn" : "accent"} label="Budget used" />
            </div>
            <div className="mt-1 text-[11px] text-muted">
              {overBudget ? `${money(v.totalPrice - 100)} over budget` : `${money(v.budgetLeft)} remaining`}
            </div>
          </div>

          {/* projection */}
          {rating ? (
            <div className="flex items-center gap-2.5">
              <RatingDial value={rating.score} size={48} label="AI" />
              <div>
                <div className="num text-lg font-bold leading-none text-fg">{rating.projectedPoints}</div>
                <div className="text-[11px] text-muted">proj · {lineup!.formation}</div>
              </div>
            </div>
          ) : null}

          {/* validity + actions */}
          <div className="flex items-center gap-2">
            <StatusChip valid={v.valid} count={squad.length} issues={v.errors.length} />
            <Button onClick={onSave} disabled={squad.length === 0 || saving} aria-label="Save squad">
              {saving ? "Saving…" : saved ? "Saved ✓" : "Save"}
            </Button>
          </div>
        </div>
      </Card>

      {/* ---------- Validation: clear error state ---------- */}
      {squad.length > 0 && !v.valid && (
        <Alert tone={overBudget ? "danger" : "warn"} title={`${v.errors.length} ${v.errors.length === 1 ? "issue" : "issues"} to resolve`}>
          <ul className="mt-1 list-disc space-y-0.5 pl-4">
            {v.errors.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        </Alert>
      )}

      {/* ---------- Empty state ---------- */}
      {squad.length === 0 ? (
        <div className="grid gap-4 lg:grid-cols-[1.05fr_1fr]">
          <EmptyState onAutofill={() => { setBench([]); set(optimalSquadIds); }} />
          <PickerCard players={players} fixtures={fixtures} />
        </div>
      ) : (
        <div className="grid items-start gap-4 [&>*]:min-w-0 xl:grid-cols-[1.05fr_1fr]">
          <SquadPitch
            squad={squad}
            lineup={lineup}
            fixtures={fixtures}
            onRemove={remove}
            onSlotClick={(allowed, replaceId) => setTarget({ allowed, replaceId })}
            onSub={handleSub}
            onReorderBench={handleReorderBench}
            getLegalSubs={(starterId) => legalSubsFor(squad, effectiveBench, starterId)}
            toolbar={
              <div className="flex items-center gap-1">
                <Button variant="ghost" size="sm" onClick={() => { setBench([]); set(optimalSquadIds); }}>
                  <Sparkles className="h-4 w-4" aria-hidden /> Auto-pick
                </Button>
                <Button variant="ghost" size="sm" onClick={clear} aria-label="Clear squad">
                  <RotateCcw className="h-4 w-4" aria-hidden /> Reset
                </Button>
              </div>
            }
          />
          <PickerCard players={players} fixtures={fixtures} />
        </div>
      )}

      {target ? (
        <SlotPickerModal
          target={target}
          players={players}
          squad={squad}
          fixtures={fixtures}
          onPick={handlePick}
          onClose={() => setTarget(null)}
        />
      ) : null}
    </div>
  );
}

function PickerCard({ players, fixtures }: { players: Player[]; fixtures: Record<string, NationFixture> }) {
  return (
    <Card as="section" aria-label="Add players" className="flex flex-col">
      <div className="mb-1 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-fg">Add players</h2>
        <span className="text-[11px] text-muted">{players.length} available</span>
      </div>
      <p className="mb-3 text-xs text-muted">Tap a shirt or slot to transfer · drag a sub onto the pitch.</p>
      <PlayerPicker players={players} fixtures={fixtures} heightClass="max-h-[calc(100vh-17rem)]" />
    </Card>
  );
}

function PositionPip({ pos, have, need }: { pos: Position; have: number; need: number }) {
  const state = have === need ? "ok" : have > need ? "over" : "under";
  const tone =
    state === "ok" ? "border-accent/40 bg-accent/10 text-accent"
    : state === "over" ? "border-danger/40 bg-danger/10 text-danger"
    : "border-border bg-surface-2 text-muted";
  return (
    <span className={cn("chip num", tone)}>
      <span className="font-semibold">{pos}</span> {have}/{need}
    </span>
  );
}

function StatusChip({ valid, count, issues }: { valid: boolean; count: number; issues: number }) {
  if (count === 0) return <Badge tone="muted">Empty</Badge>;
  if (valid) return <Badge tone="accent">Valid ✓</Badge>;
  if (count < 15) return <Badge tone="info">{15 - count} to add</Badge>;
  return <Badge tone="warn">{issues} {issues === 1 ? "issue" : "issues"}</Badge>;
}

function EmptyState({ onAutofill }: { onAutofill: () => void }) {
  return (
    <Card className="grid place-items-center py-14 text-center">
      <div className="max-w-sm">
        <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-surface-2 text-accent">
          <Users className="h-7 w-7" aria-hidden />
        </div>
        <h2 className="mt-4 text-lg font-semibold text-fg">Build your squad</h2>
        <p className="mt-1.5 text-sm text-muted">
          Pick 15 players — 2 GK, 5 DEF, 5 MID, 3 FWD — within a $100m budget and max 3 per nation.
          Add from the panel, or let the engine pick an optimal starting point.
        </p>
        <div className="mt-5 flex justify-center gap-2">
          <Button onClick={onAutofill}>
            <Sparkles className="h-4 w-4" aria-hidden /> Auto-pick optimal squad
          </Button>
        </div>
        <p className="mt-3 text-xs text-muted">You can change every pick afterwards.</p>
      </div>
    </Card>
  );
}

function BuilderSkeleton() {
  return (
    <div className="space-y-4" aria-busy="true" aria-label="Loading squad builder">
      <Card><div className="flex items-center gap-6"><Skeleton className="h-11 w-40" /><Skeleton className="h-8 flex-1" /><Skeleton className="h-10 w-24" /></div></Card>
      <div className="grid gap-4 xl:grid-cols-[1.05fr_1fr]">
        <Skeleton className="h-[520px] w-full rounded-2xl" />
        <Skeleton className="h-[520px] w-full rounded-2xl" />
      </div>
    </div>
  );
}
