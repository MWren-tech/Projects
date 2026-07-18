"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Player } from "@/types";
import { useSquad } from "@/lib/useSquad";
import { suggestTransfers } from "@/lib/engine";
import { Card, CardTitle, Badge, Button } from "@/components/ui/primitives";
import { money } from "@/lib/utils";

export function TransferPlanner({ players }: { players: Player[] }) {
  const { ids, loaded } = useSquad();
  const [free, setFree] = useState(2);
  const map = useMemo(() => new Map(players.map((p) => [p.id, p])), [players]);
  const squad = ids.map((id) => map.get(id)).filter(Boolean) as Player[];

  const suggestions = useMemo(
    () => (squad.length >= 11 ? suggestTransfers(squad, players, free) : []),
    [squad, players, free]
  );

  if (!loaded) return null;

  if (squad.length < 11) {
    return (
      <Card>
        <div className="py-8 text-center">
          <p className="text-sm text-muted">Build a squad first to get transfer suggestions.</p>
          <Link href="/squad" className="mt-3 inline-block rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-bg">Go to Squad Builder</Link>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <div className="flex items-center justify-between">
          <CardTitle hint="engine marginal-gain ladder">Suggested transfers</CardTitle>
          <div className="flex items-center gap-2 text-xs text-muted">
            Free transfers:
            <select value={free} onChange={(e) => setFree(Number(e.target.value))} className="rounded-lg border border-border bg-surface-2 px-2 py-1">
              {[1, 2, 4, 5, 6].map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
        </div>

        {suggestions.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted">No transfer improves your squad right now — bank your transfers.</p>
        ) : (
          <div className="space-y-2">
            {suggestions.map((s, i) => {
              const worthwhile = s.free ? s.xpDelta > 0.3 : s.netAfterHit > 0;
              return (
                <div key={i} className="card-2 p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm">
                      <Badge tone="danger">OUT {s.out.name.split(" ").pop()}</Badge>
                      <span className="text-muted">→</span>
                      <Badge tone="accent">IN {s.in.name.split(" ").pop()}</Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="num text-sm font-semibold text-accent">+{s.xpDelta.toFixed(2)}</span>
                      <Badge tone={s.free ? "info" : "warn"}>{s.free ? "FREE" : `−3 hit → ${s.netAfterHit > 0 ? "+" : ""}${s.netAfterHit.toFixed(2)}`}</Badge>
                      <Badge tone={worthwhile ? "accent" : "muted"}>{worthwhile ? "USE" : "BANK"}</Badge>
                    </div>
                  </div>
                  <p className="mt-2 text-xs text-muted">{s.reason}</p>
                  <div className="mt-1 flex gap-3 text-[11px] text-muted">
                    <span>{money(s.out.price)} → {money(s.in.price)}</span>
                    <span>own {s.out.ownership ?? "?"}% → {s.in.ownership ?? "?"}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      <AskTransferAI squadIds={ids} />
    </div>
  );
}

function AskTransferAI({ squadIds }: { squadIds: string[] }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  async function go() {
    setLoading(true);
    setText("");
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Given my current squad, what 2 transfers should I make this round and why? Consider fixtures, form and the −3 hit rule.", squadIds }),
    });
    const reader = res.body?.getReader();
    const dec = new TextDecoder();
    if (!reader) { setLoading(false); return; }
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      setText((t) => t + dec.decode(value));
    }
    setLoading(false);
  }

  return (
    <Card>
      <CardTitle>AI transfer rationale</CardTitle>
      <Button onClick={go} disabled={loading}>{loading ? "Thinking…" : "Ask the AI for a transfer plan"}</Button>
      {text ? <div className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-fg/90">{text}</div> : null}
    </Card>
  );
}
