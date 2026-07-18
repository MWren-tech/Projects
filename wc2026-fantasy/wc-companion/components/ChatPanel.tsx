"use client";

import { useRef, useState } from "react";
import { useSquad } from "@/lib/useSquad";
import { Card } from "@/components/ui/primitives";
import { cn } from "@/lib/utils";

const SUGGESTED = [
  "Who should I captain this round?",
  "Should I transfer out Mbappé?",
  "Best differential picks under 5% owned?",
  "When should I use my Wildcard?",
  "Which defenders have the best clean-sheet potential?",
  "Build me the best team for the next 3 matches",
];

type Msg = { role: "user" | "assistant"; content: string };

export function ChatPanel({ aiEnabled }: { aiEnabled: boolean }) {
  const { ids } = useSquad();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  async function send(text: string) {
    if (!text.trim() || busy) return;
    const history = messages.slice(-6);
    setMessages((m) => [...m, { role: "user", content: text }, { role: "assistant", content: "" }]);
    setInput("");
    setBusy(true);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, squadIds: ids, history }),
    });

    if (!res.body) {
      const fallback = await res.text();
      setMessages((m) => updateLast(m, fallback));
      setBusy(false);
      return;
    }
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = dec.decode(value);
      setMessages((m) => updateLast(m, m[m.length - 1].content + chunk));
      scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
    }
    setBusy(false);
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_240px]">
      <Card className="flex h-[70vh] flex-col p-0">
        <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="grid h-full place-items-center text-center">
              <div>
                <div className="text-4xl">⚽</div>
                <p className="mt-2 text-sm text-muted">
                  {aiEnabled
                    ? "Ask me anything about your World Cup fantasy team."
                    : "AI chat needs an ANTHROPIC_API_KEY in .env.local. Everything else works without it."}
                </p>
              </div>
            </div>
          ) : (
            messages.map((m, i) => (
              <div key={i} className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}>
                <div
                  className={cn(
                    "max-w-[85%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed",
                    m.role === "user" ? "bg-accent text-bg" : "card-2 text-fg/90"
                  )}
                >
                  {m.role === "assistant" ? <Rendered text={m.content || "…"} /> : m.content}
                </div>
              </div>
            ))
          )}
        </div>
        <form
          onSubmit={(e) => { e.preventDefault(); send(input); }}
          className="flex gap-2 border-t border-border p-3"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the AI…"
            className="flex-1 rounded-xl border border-border bg-surface-2 px-3 py-2 text-sm outline-none focus:border-accent/50"
          />
          <button disabled={busy} className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-bg disabled:opacity-50">
            {busy ? "…" : "Send"}
          </button>
        </form>
      </Card>

      <div className="space-y-2">
        <div className="label">Try asking</div>
        {SUGGESTED.map((s) => (
          <button
            key={s}
            onClick={() => send(s)}
            disabled={busy}
            className="w-full rounded-xl border border-border bg-surface p-2.5 text-left text-xs text-muted transition hover:border-accent/40 hover:text-fg"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

function updateLast(m: Msg[], content: string): Msg[] {
  const copy = [...m];
  copy[copy.length - 1] = { role: "assistant", content };
  return copy;
}

// Minimal **bold** rendering for the structured labels.
function Rendered({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <span className="whitespace-pre-wrap">
      {parts.map((p, i) =>
        p.startsWith("**") && p.endsWith("**") ? (
          <strong key={i} className="text-accent">{p.slice(2, -2)}</strong>
        ) : (
          <span key={i}>{p}</span>
        )
      )}
    </span>
  );
}
