import type { Player, Snapshot } from "@/types";

// The assistant persona + hard grounding rules. The model must never reference a
// player that isn't in the injected data (the official FIFA WC list).
export const SYSTEM_PROMPT = `You are the WC2026 Fantasy Companion — a sharp, premium fantasy-football analyst, not a generic chatbot.

You sit on top of a validated analytics ENGINE that projects expected fantasy points (xPts), fixture ease, clean-sheet probability, ownership, value and a booster plan. The engine is the source of truth for all numbers.

HARD RULES:
- ONLY reference players that appear in the DATA provided in the user message. Never invent players, prices, clubs or stats. If a player isn't in the data, say you don't have them.
- All numeric claims (xPts, price, ownership, fixture ease) must come from the DATA. Do not estimate numbers that aren't given.
- Respect the official WC2026 rules given in the DATA (squad 2/5/5/3, $100m budget, max 3 per nation in the group stage, transfer allocations, -3 hits, the five boosters: Wildcard, 12th Man, Maximum Captain, Qualification, Mystery).
- Be decisive. Give a clear recommendation, the reasoning, the expected outcome, the risk level, and a backup option.
- Captaincy doubles a player's points. Differentials (sub-5% ownership) gain rank, not just raw points.

STYLE: concise, confident, analytical. Use the player's xPts and fixture ease to justify picks. Flag risk honestly (rotation, tough fixtures, single-game samples).`;

// Build a compact, token-bounded DATA block: rules + booster schedule + the user's
// squad + a relevant shortlist (top players plus anyone named in the question).
export function buildContext(
  snapshot: Snapshot,
  question: string,
  squad: Player[] = []
): string {
  const q = question.toLowerCase();
  const named = snapshot.players.filter((p) => {
    const last = p.name.split(" ").pop()?.toLowerCase() ?? "";
    return last.length >= 4 && q.includes(last);
  });
  const top = snapshot.players.slice(0, 45);
  const relevant = dedupe([...squad, ...named, ...top]).slice(0, 70);

  const line = (p: Player) =>
    `${p.name} | ${p.nation} | ${p.pos} | $${p.price}m | xPts ${p.xp} | own ${p.ownership ?? "?"}% | ` +
    `fixEase ${p.fixtureEase} | CS ${Math.round((p.cleanSheet ?? 0) * 100)}% | start ${Math.round(p.startProb * 100)}% | ` +
    `setpieces ${p.setPieces || "-"} | diff ${p.differential}`;

  const fixtures = Object.entries(snapshot.fixtures)
    .filter(([nat]) => relevant.some((p) => p.nation === nat))
    .map(([nat, f]) => `${nat}: next ${f.nextOpponent ?? "?"}, ease ${f.fixtureEase ?? "?"}, CS ${f.cleanSheet ?? "?"}`)
    .slice(0, 24)
    .join("\n");

  const boost = Object.entries(snapshot.boosterPlan.schedule)
    .map(([chip, s]) => `${chip}: ${s.round}${s.ev != null ? ` (+${s.ev})` : ""}`)
    .join("; ");

  const squadBlock = squad.length
    ? `\nUSER'S CURRENT SQUAD (${squad.length}):\n${squad.map(line).join("\n")}`
    : "\nUSER'S CURRENT SQUAD: (none entered yet)";

  return `CURRENT ROUND: ${snapshot.meta.currentRound}  |  data generated ${snapshot.meta.generatedAt}

RULES: squad ${JSON.stringify(snapshot.rules.squad)}, budget $${snapshot.rules.budget}m, max ${snapshot.rules.maxPerNation.Group}/nation (group), transfer hit -${snapshot.rules.transfers.hitCost}.
Free transfers — MD2: ${snapshot.rules.transfers.MD2}, MD3: ${snapshot.rules.transfers.MD3}, R32: ${snapshot.rules.transfers.R32}.
BOOSTER PLAN (engine): ${boost}

ENGINE OPTIMAL XI projects ${snapshot.optimalSquad.projectedPoints} pts; captain ${snapshot.optimalSquad.captain.name}.
${squadBlock}

RELEVANT PLAYERS (engine projections — use ONLY these):
${relevant.map(line).join("\n")}

UPCOMING FIXTURES:
${fixtures}

USER QUESTION: ${question}`;
}

function dedupe(players: Player[]): Player[] {
  const seen = new Set<string>();
  return players.filter((p) => (seen.has(p.id) ? false : (seen.add(p.id), true)));
}
