// Shared types — mirror the engine snapshot (snapshot.json) and app domain.

export type Position = "GK" | "DEF" | "MID" | "FWD";

export interface WcStatLine {
  label: string;
  count: number | null;
  pts: number;
}

export interface WcStats {
  minutes: number;
  appearances: number;
  starts: number;
  goals: number;
  assists: number;
  saves: number;
  penSaved: number;
  tackles: number;
  chances: number;
  shotsOn: number;
  yellows: number;
  reds: number;
  penWon: number;
  penConceded: number;
  goalsConceded: number;
  rating: number | null;
  breakdown: WcStatLine[];
  totalPoints: number;
  official: boolean; // true when totalPoints is FIFA's own figure
}

export interface RoundPoints {
  round: string; // "MD1".."MD3" | "R32" | "R16" | "QF" | "SF" | "Final"
  pts: number;
}

export interface Player {
  id: string;
  name: string;
  nation: string;
  club: string | null;
  pos: Position;
  price: number;
  xp: number;
  ownership: number | null;
  value: number;
  goals: number | null;
  assists: number | null;
  g90: number;
  a90: number;
  cleanSheet: number;
  fixtureEase: number;
  setPieces: string;
  rating: number | null;
  startProb: number;
  aiRating: number;       // 0-100 percentile within position
  differential: number;   // 0-100
  scoutingBonus?: number; // expected differential (scouting) bonus already in xp
  wcStats: WcStats | null; // actual tournament tally + points, null until featured
  roundPoints: RoundPoints[]; // FIFA per-round official points; empty until featured
}

export interface NationFixture {
  nextOpponent: string | null;
  opponents: string[];
  fixtureEase: number | null;
  cleanSheet: number | null;
  gfPg: number | null;
  gaPg: number | null;
  wcGames: number;
}

export interface SquadView {
  id: string;
  name: string;
  nation: string;
  pos: Position;
  price: number;
  xp: number;
}

export interface OptimalSquad {
  xi: SquadView[];
  bench: SquadView[];
  captain: SquadView;
  projectedPoints: number;
}

export interface BoosterRoundEV {
  round: string;
  maxCaptain: number;
  twelfthMan: { name: string; nation: string; ev: number } | null;
  qualification: number | null;
}

export interface BoosterPlan {
  perRound: BoosterRoundEV[];
  schedule: Record<string, { round: string; ev: number | null }>;
}

export interface Rules {
  budget: number;
  knockoutBudget: number;
  squad: Record<Position, number>;
  formations: string[];
  transfers: Record<string, number | string>;
  maxPerNation: Record<string, number>;
  boosters: string[];
  scoring: Record<string, string | number>;
}

export interface Snapshot {
  meta: { generatedAt: string; season: number; currentRound: string; playerCount: number };
  rules: Rules;
  players: Player[];
  fixtures: Record<string, NationFixture>;
  optimalSquad: OptimalSquad;
  boosterPlan: BoosterPlan;
}

// AI structured output contract (also enforced by zod in services/ai/schema.ts).
export interface AIRecommendation {
  recommendation: string;
  confidence: "Low" | "Medium" | "High";
  reasoning: string;
  expectedOutcome: string;
  risk: "Low" | "Medium" | "High";
  alternatives: string[];
}

export interface TeamRating {
  score: number;          // 0-100
  projectedPoints: number;
  vsOptimal: number;      // gap to engine-optimal XI
  strengths: string[];
  weaknesses: string[];
}

export interface TransferSuggestion {
  out: Player;
  in: Player;
  xpDelta: number;
  free: boolean;
  netAfterHit: number;
  reason: string;
}
