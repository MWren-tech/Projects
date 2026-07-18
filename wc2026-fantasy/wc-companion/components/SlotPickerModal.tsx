"use client";

import { useEffect, useRef } from "react";
import type { Player, Position, NationFixture } from "@/types";
import { PlayerPicker } from "@/components/PlayerPicker";
import { Badge, IconButton } from "@/components/ui/primitives";
import { money } from "@/lib/utils";

export interface SlotTarget {
  allowed: Position[];
  replaceId: string | null;
}

export function SlotPickerModal({
  target,
  players,
  squad,
  fixtures,
  budget = 100,
  onPick,
  onClose,
}: {
  target: SlotTarget;
  players: Player[];
  squad: Player[];
  fixtures?: Record<string, NationFixture>;
  budget?: number;
  onPick: (p: Player) => void;
  onClose: () => void;
}) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const titleId = "slot-picker-title";

  // Focus management: trap Tab inside, focus the dialog on open, restore focus on close.
  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    dialogRef.current?.focus();

    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") { onClose(); return; }
      if (e.key !== "Tab") return;
      const focusables = dialogRef.current?.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusables || focusables.length === 0) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
      previouslyFocused?.focus?.();
    };
  }, [onClose]);

  const out = target.replaceId ? squad.find((p) => p.id === target.replaceId) ?? null : null;
  const spent = squad.reduce((s, p) => s + p.price, 0);
  const budgetForIn = budget - spent + (out?.price ?? 0);
  const ownIds = new Set(squad.map((p) => p.id));

  function disabledReason(p: Player): string | null {
    if (ownIds.has(p.id) && p.id !== target.replaceId) return "Already in squad";
    if (p.price > budgetForIn + 1e-6) return `Over budget (have ${money(budgetForIn)})`;
    const nationCount = squad.filter((s) => s.nation === p.nation && s.id !== target.replaceId).length;
    if (nationCount >= 3) return `Max 3 from ${p.nation}`;
    return null;
  }

  const posLabel = target.allowed.length === 1 ? target.allowed[0] : "player";

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur-sm" onClick={onClose}>
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className="card w-full max-w-lg p-4 outline-none"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h2 id={titleId} className="text-sm font-semibold text-fg">
              {out ? `Replace ${out.name.split(" ").pop()}` : `Add a ${posLabel}`}
            </h2>
            <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted">
              {out ? <Badge tone="danger">OUT {out.name.split(" ").pop()}</Badge> : null}
              <span>Budget available: <span className="num font-semibold text-accent">{money(budgetForIn)}</span></span>
            </div>
          </div>
          <IconButton label="Close" onClick={onClose}>✕</IconButton>
        </div>

        <PlayerPicker
          players={players}
          fixtures={fixtures}
          allowedPositions={target.allowed}
          mode="select"
          onSelect={onPick}
          disabledReason={disabledReason}
          heightClass="max-h-[60vh]"
        />
      </div>
    </div>
  );
}
