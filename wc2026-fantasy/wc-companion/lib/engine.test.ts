import { describe, it, expect } from "vitest";
import type { Player } from "@/types";
import { validateSquad, pickBestXI, rateTeam, SQUAD_REQ } from "./engine";

// Minimal Player factory. Cast through unknown so tests can inject the nullable
// runtime values (fixtureEase, value) that the snapshot actually carries for
// depth players — the very case that the declared types don't capture.
function mkPlayer(o: Partial<Record<keyof Player, unknown>> = {}): Player {
  return {
    id: "p", name: "Player", nation: "Nowhere", club: null, pos: "MID",
    price: 5, xp: 5, ownership: 10, value: 1, goals: 0, assists: 0,
    g90: 0, a90: 0, cleanSheet: 0, fixtureEase: 1, setPieces: "",
    rating: null, startProb: 0.9, aiRating: 50, differential: 50,
    wcStats: null, roundPoints: [], ...o,
  } as unknown as Player;
}

// A legal 15-man squad (2 GK, 5 DEF, 5 MID, 3 FWD), each from a distinct nation.
function validSquad(): Player[] {
  const plan: Array<[Player["pos"], number]> = [["GK", 2], ["DEF", 5], ["MID", 5], ["FWD", 3]];
  const squad: Player[] = [];
  let i = 0;
  for (const [pos, n] of plan)
    for (let k = 0; k < n; k++)
      squad.push(mkPlayer({ id: `${pos}${k}`, pos, nation: `nation-${i++}`, price: 5, xp: 5 }));
  return squad;
}

describe("validateSquad", () => {
  it("accepts a legal 15-man squad", () => {
    expect(validateSquad(validSquad()).valid).toBe(true);
  });

  it("rejects a 16-man squad", () => {
    const over = [...validSquad(), mkPlayer({ id: "extra", pos: "FWD", nation: "z" })];
    const v = validateSquad(over);
    expect(v.valid).toBe(false);
    expect(v.errors.some((e) => e.includes("15"))).toBe(true);
  });

  it("flags going over budget", () => {
    const pricey = validSquad().map((p) => mkPlayer({ ...p, price: 20 }));
    expect(validateSquad(pricey).valid).toBe(false);
  });

  it("flags more than three from one nation", () => {
    const squad = validSquad();
    for (let k = 0; k < 4; k++) squad[k] = mkPlayer({ ...squad[k], nation: "same" });
    expect(validateSquad(squad).valid).toBe(false);
  });

  it("requires the right position counts", () => {
    expect(SQUAD_REQ).toEqual({ GK: 2, DEF: 5, MID: 5, FWD: 3 });
  });
});

describe("rateTeam / pickBestXI", () => {
  it("builds a valid best XI from a legal squad", () => {
    const xi = pickBestXI(validSquad());
    expect(xi).not.toBeNull();
    expect(xi!.xi).toHaveLength(11);
    expect(SQUAD_REQ).toBeTruthy();
  });

  // Regression: depth players carry a null fixtureEase. `null < 0.9` coerces to
  // true, so an unguarded filter used to pull them into the "tough fixture" list
  // and then call null.toFixed(2), crashing the whole squad page. This must not throw.
  it("does not throw when a starter has a null fixtureEase", () => {
    const squad = validSquad();
    // make a high-xp forward with no fixture data a guaranteed starter
    squad[squad.length - 1] = mkPlayer({
      id: "depth-star", pos: "FWD", nation: "depthland", xp: 20, fixtureEase: null, value: null,
    });
    expect(() => rateTeam(squad, 114)).not.toThrow();
    const rating = rateTeam(squad, 114);
    expect(typeof rating.projectedPoints).toBe("number");
  });
});
