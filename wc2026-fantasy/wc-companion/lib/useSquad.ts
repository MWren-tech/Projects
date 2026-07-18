"use client";

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";

const KEY = "wc26.squad";
const BENCH_KEY = "wc26.bench";

// Shared store so EVERY component using useSquad() stays in sync. Holds the 15
// player ids plus an optional manual bench order (set by substitutions; empty means
// "auto-pick the best XI"). Backed by localStorage.
let ids: string[] = [];
let bench: string[] = [];
let initialised = false;
const listeners = new Set<() => void>();

function load() {
  if (initialised) return;
  initialised = true;
  if (typeof window !== "undefined") {
    try {
      const a = localStorage.getItem(KEY);
      if (a) ids = JSON.parse(a);
      const b = localStorage.getItem(BENCH_KEY);
      if (b) bench = JSON.parse(b);
    } catch {}
  }
}

function emit() {
  for (const l of listeners) l();
}

function persistIds(next: string[]) {
  ids = next;
  bench = []; // squad changed → drop the manual lineup, re-optimise
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
    localStorage.setItem(BENCH_KEY, "[]");
  } catch {}
  emit();
}

function persistBench(next: string[]) {
  bench = next;
  try {
    localStorage.setItem(BENCH_KEY, JSON.stringify(next));
  } catch {}
  emit();
}

function subscribe(cb: () => void) {
  load();
  listeners.add(cb);
  return () => listeners.delete(cb);
}

const EMPTY: string[] = [];

export function useSquad() {
  const currentIds = useSyncExternalStore(subscribe, () => (load(), ids), () => EMPTY);
  const currentBench = useSyncExternalStore(subscribe, () => (load(), bench), () => EMPTY);

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const add = useCallback((id: string) => {
    if (!ids.includes(id)) persistIds([...ids, id]);
  }, []);
  const remove = useCallback((id: string) => persistIds(ids.filter((x) => x !== id)), []);
  const has = useCallback((id: string) => ids.includes(id), [currentIds]);
  const clear = useCallback(() => persistIds([]), []);
  const set = useCallback((next: string[]) => persistIds(next), []);
  const setBench = useCallback((next: string[]) => persistBench(next), []);

  const saveToDb = useCallback(async () => {
    await fetch("/api/squad", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ playerIds: ids }),
    });
  }, []);

  return {
    ids: currentIds,
    bench: currentBench,
    loaded: mounted,
    add,
    remove,
    has,
    clear,
    set,
    setBench,
    saveToDb,
  };
}
