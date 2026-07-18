// Advisory math run in the app at request time. All inputs are engine-sourced
// players (from snapshot.json); this layer only *arranges* them under the official
// WC2026 rules — it never invents players or projections.

import type { Player, Position, TeamRating, TransferSuggestion } from "@/types";

export const SQUAD_REQ: Record<Position, number> = { GK: 2, DEF: 5, MID: 5, FWD: 3 };
export const FORMATIONS = ["4-4-2", "4-3-3", "4-5-1", "3-4-3", "3-5-2", "5-4-1", "5-3-2"];
export const MAX_PER_NATION = 3; // group stage
export const HIT_COST = 3;

export interface SquadValidation {
  valid: boolean;
  errors: string[];
  totalPrice: number;
  budgetLeft: number;
}

export function validateSquad(players: Player[], budget = 100): SquadValidation {
  const errors: string[] = [];
  const counts: Record<string, number> = { GK: 0, DEF: 0, MID: 0, FWD: 0 };
  const nationCount: Record<string, number> = {};
  let totalPrice = 0;
  for (const p of players) {
    counts[p.pos]++;
    nationCount[p.nation] = (nationCount[p.nation] || 0) + 1;
    totalPrice += p.price;
  }
  if (players.length !== 15) errors.push(`Squad must be 15 players (have ${players.length}).`);
  for (const pos of Object.keys(SQUAD_REQ) as Position[]) {
    if (counts[pos] !== SQUAD_REQ[pos])
      errors.push(`Need ${SQUAD_REQ[pos]} ${pos} (have ${counts[pos]}).`);
  }
  if (totalPrice > budget + 1e-6)
    errors.push(`Over budget by $${(totalPrice - budget).toFixed(1)}m.`);
  for (const [nation, n] of Object.entries(nationCount))
    if (n > MAX_PER_NATION) errors.push(`Max ${MAX_PER_NATION} from ${nation} (have ${n}).`);
  return { valid: errors.length === 0, errors, totalPrice, budgetLeft: budget - totalPrice };
}

function parseFormation(f: string) {
  const [d, m, fwd] = f.split("-").map(Number);
  return { GK: 1, DEF: d, MID: m, FWD: fwd };
}

export interface BestXI {
  formation: string;
  xi: Player[];
  bench: Player[];
  captain: Player;
  vice: Player;
  projected: number; // XI xp + captain xp (doubled)
}

// Choose the formation + XI that maximises projected points from a 15-man squad.
export function pickBestXI(squad: Player[]): BestXI | null {
  if (squad.length < 11) return null;
  const byPos: Record<string, Player[]> = { GK: [], DEF: [], MID: [], FWD: [] };
  for (const p of squad) byPos[p.pos]?.push(p);
  for (const k of Object.keys(byPos)) byPos[k].sort((a, b) => b.xp - a.xp);

  let best: BestXI | null = null;
  for (const f of FORMATIONS) {
    const need = parseFormation(f);
    if (
      byPos.GK.length < 1 || byPos.DEF.length < need.DEF ||
      byPos.MID.length < need.MID || byPos.FWD.length < need.FWD
    )
      continue;
    const xi = [
      ...byPos.GK.slice(0, 1),
      ...byPos.DEF.slice(0, need.DEF),
      ...byPos.MID.slice(0, need.MID),
      ...byPos.FWD.slice(0, need.FWD),
    ];
    const xiSum = xi.reduce((s, p) => s + p.xp, 0);
    const captain = [...xi].sort((a, b) => b.xp - a.xp)[0];
    const projected = xiSum + captain.xp; // captain doubled
    if (!best || projected > best.projected) {
      const starterIds = new Set(xi.map((p) => p.id));
      const bench = squad
        .filter((p) => !starterIds.has(p.id))
        // auto-sub priority: outfield by likelihood-to-play × value, GK last
        .sort((a, b) => {
          if (a.pos === "GK" && b.pos !== "GK") return 1;
          if (b.pos === "GK" && a.pos !== "GK") return -1;
          return b.startProb * b.xp - a.startProb * a.xp;
        });
      const vice =
        [...xi].sort((a, b) => b.xp - a.xp).find((p) => p.nation !== captain.nation) ??
        [...xi].sort((a, b) => b.xp - a.xp)[1];
      best = { formation: f, xi, bench, captain, vice, projected };
    }
  }
  return best;
}

export function rateTeam(squad: Player[], optimalProjected: number): TeamRating {
  const xi = pickBestXI(squad);
  const projected = xi?.projected ?? 0;
  const vsOptimal = projected - optimalProjected;
  // 100 = matches the engine-optimal XI; scale gap into a 0-100 score.
  const score = Math.max(0, Math.min(100, Math.round(100 - (-vsOptimal / optimalProjected) * 100 * 2)));

  const strengths: string[] = [];
  const weaknesses: string[] = [];
  if (xi) {
    const premium = xi.xi.filter((p) => p.price >= 9).length;
    const diffs = squad.filter((p) => (p.ownership ?? 100) < 5).length;
    const benchXp = xi.bench.reduce((s, p) => s + p.xp, 0);
    const softFix = xi.xi.filter((p) => (p.fixtureEase ?? 0) >= 1.2).length;
    // guard null: depth players carry no fixtureEase, and `null < 0.9` coerces to true
    const toughFix = xi.xi.filter((p) => p.fixtureEase != null && p.fixtureEase < 0.9);

    if (xi.captain.xp >= 10) strengths.push(`Strong captain in ${xi.captain.name} (${xi.captain.xp.toFixed(1)} xPts).`);
    if (diffs >= 3) strengths.push(`${diffs} sub-5% differentials — good rank upside.`);
    if (softFix >= 5) strengths.push(`${softFix} starters with favourable fixtures.`);
    if (premium <= 1) weaknesses.push("Light on premium attackers — may lack ceiling.");
    if (benchXp < 14) weaknesses.push("Thin bench — weak auto-sub cover if a starter is benched.");
    for (const p of toughFix.slice(0, 2))
      weaknesses.push(`${p.name} has a tough fixture (ease ${p.fixtureEase.toFixed(2)}).`);
  }
  return { score, projectedPoints: Math.round(projected * 10) / 10, vsOptimal: Math.round(vsOptimal * 10) / 10, strengths, weaknesses };
}

// --- Manual lineup + substitutions ------------------------------------------

export interface Lineup {
  xi: Player[];
  bench: Player[];
  captain: Player;
  vice: Player;
  formation: string;
  manual: boolean;
}

export function isLegalXI(players: Player[]): boolean {
  if (players.length !== 11) return false;
  const c: Record<Position, number> = { GK: 0, DEF: 0, MID: 0, FWD: 0 };
  for (const p of players) c[p.pos]++;
  // Exactly one keeper, and the outfield shape must be one of the 7 allowed formations.
  return c.GK === 1 && FORMATIONS.includes(`${c.DEF}-${c.MID}-${c.FWD}`);
}

function finishLineup(xi: Player[], bench: Player[], manual: boolean): Lineup {
  const c: Record<string, number> = { DEF: 0, MID: 0, FWD: 0 };
  for (const p of xi) if (p.pos !== "GK") c[p.pos]++;
  const ranked = [...xi].sort((a, b) => b.xp - a.xp);
  const captain = ranked[0];
  const vice = ranked.find((p) => p.nation !== captain.nation) ?? ranked[1];
  return { xi, bench, captain, vice, formation: `${c.DEF}-${c.MID}-${c.FWD}`, manual };
}

// Build the displayed lineup. If a valid manual bench is given, honour it; otherwise
// fall back to the engine-optimal XI. Starters are ordered FWD→GK by the pitch.
export function buildLineup(squad: Player[], benchIds?: string[]): Lineup | null {
  if (squad.length < 11) return null;
  const byId = new Map(squad.map((p) => [p.id, p]));
  if (
    benchIds &&
    benchIds.length === squad.length - 11 &&
    benchIds.every((id) => byId.has(id))
  ) {
    const benchSet = new Set(benchIds);
    const starters = squad.filter((p) => !benchSet.has(p.id));
    if (isLegalXI(starters)) {
      return finishLineup(starters, benchIds.map((id) => byId.get(id)!), true);
    }
  }
  const best = pickBestXI(squad);
  return best ? finishLineup(best.xi, best.bench, false) : null;
}

// Swap a starter out for a bench player; returns the new bench id list if the
// resulting XI is still a legal formation, else null.
export function computeSwap(
  squad: Player[],
  benchIds: string[],
  starterId: string,
  benchId: string
): string[] | null {
  const idx = benchIds.indexOf(benchId);
  if (idx < 0 || benchIds.includes(starterId)) return null;
  const newBench = [...benchIds];
  newBench[idx] = starterId;
  const benchSet = new Set(newBench);
  const starters = squad.filter((p) => !benchSet.has(p.id));
  return isLegalXI(starters) ? newBench : null;
}

// Bench players that may legally come on for a given starter.
export function legalSubsFor(squad: Player[], benchIds: string[], starterId: string): Player[] {
  const byId = new Map(squad.map((p) => [p.id, p]));
  return benchIds
    .map((id) => byId.get(id))
    .filter((b): b is Player => !!b && computeSwap(squad, benchIds, starterId, b.id) !== null);
}

// Greedy marginal transfer suggestions: best single-swap per held player, ranked.
export function suggestTransfers(
  squad: Player[],
  pool: Player[],
  freeTransfers = 2,
  budget = 100,
  limit = 6
): TransferSuggestion[] {
  const base = pickBestXI(squad)?.projected ?? 0;
  const totalPrice = squad.reduce((s, p) => s + p.price, 0);
  const ownIds = new Set(squad.map((p) => p.id));
  const suggestions: TransferSuggestion[] = [];

  squad.forEach((out, idx) => {
    let bestForSlot: TransferSuggestion | null = null;
    for (const cand of pool) {
      if (cand.pos !== out.pos || ownIds.has(cand.id)) continue;
      if (totalPrice - out.price + cand.price > budget + 1e-6) continue;
      const nationCount = squad.filter((p) => p.nation === cand.nation && p.id !== out.id).length;
      if (nationCount >= MAX_PER_NATION) continue;
      const next = [...squad];
      next[idx] = cand;
      const proj = pickBestXI(next)?.projected ?? 0;
      const delta = proj - base;
      if (!bestForSlot || delta > bestForSlot.xpDelta) {
        bestForSlot = {
          out,
          in: cand,
          xpDelta: Math.round(delta * 100) / 100,
          free: true,
          netAfterHit: Math.round((delta - HIT_COST) * 100) / 100,
          reason: `${cand.name} (${cand.nation}) projects ${cand.xp.toFixed(1)} vs ${out.xp.toFixed(1)} — ` +
            `${cand.fixtureEase >= out.fixtureEase ? "softer fixtures" : "stronger form"}${
              (cand.ownership ?? 100) < 5 ? ", and a sub-5% differential" : ""
            }.`,
        };
      }
    }
    if (bestForSlot && bestForSlot.xpDelta > 0.01) suggestions.push(bestForSlot);
  });

  suggestions.sort((a, b) => b.xpDelta - a.xpDelta);
  return suggestions.slice(0, limit).map((s, i) => ({
    ...s,
    free: i < freeTransfers,
    netAfterHit: i < freeTransfers ? s.xpDelta : Math.round((s.xpDelta - HIT_COST) * 100) / 100,
  }));
}
