import fs from "fs";
import path from "path";
import type { Snapshot, Player } from "@/types";

// The engine writes data/snapshot.json (e.g. via the daily 8am refresh). We cache
// it in memory but reload automatically when the file's modified-time changes, so
// a fresh pull is picked up without restarting the server.
let cached: Snapshot | null = null;
let cachedMtimeMs = 0;

const SNAPSHOT_PATH = path.join(process.cwd(), "data", "snapshot.json");

export function getSnapshot(): Snapshot {
  if (!fs.existsSync(SNAPSHOT_PATH)) {
    throw new Error(
      `snapshot.json not found at ${SNAPSHOT_PATH}. Run \`npm run snapshot\` first.`
    );
  }
  const mtimeMs = fs.statSync(SNAPSHOT_PATH).mtimeMs;
  if (!cached || mtimeMs !== cachedMtimeMs) {
    cached = JSON.parse(fs.readFileSync(SNAPSHOT_PATH, "utf-8")) as Snapshot;
    cachedMtimeMs = mtimeMs;
  }
  return cached;
}

export function clearSnapshotCache() {
  cached = null;
}

export function getPlayers(): Player[] {
  return getSnapshot().players;
}

export function getPlayerById(id: string): Player | undefined {
  return getSnapshot().players.find((p) => p.id === id);
}

export function getPlayersByIds(ids: string[]): Player[] {
  const map = new Map(getSnapshot().players.map((p) => [p.id, p]));
  return ids.map((id) => map.get(id)).filter(Boolean) as Player[];
}

export function searchPlayers(q: string, limit = 20): Player[] {
  const needle = q.toLowerCase();
  return getSnapshot()
    .players.filter(
      (p) => p.name.toLowerCase().includes(needle) || p.nation.toLowerCase().includes(needle)
    )
    .slice(0, limit);
}
