"""
WC2026 Fantasy booster planner.

Estimates EV for each chip across remaining rounds using the held squad
(current_squad.json), per-90 form rates, fixture ease and team strength.
One chip per round; brute-forces the optimal assignment for the 3 quantifiable
ones, then slots Wildcard and Mystery heuristically.

Knockout numbers are strength-based proxies until draws are made.
"""

from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from statistics import mean

from api_football import ApiFootball
from national_strength import build_national_context
from fifa_rankings import fifa_strength
from optimise import build_priced_survivors, _pool, find_held
from scoring import GOAL_POINTS, ASSIST, APPEARANCE

# Remaining decision rounds in order. MD2 is essentially locking as you read this,
# so the planner targets MD3 onward but lists MD2 for completeness.
ROUNDS = ["MD3", "R32", "R16", "QF", "SF", "Final"]
GROUP_ROUNDS = {"MD2", "MD3"}
# Teams still alive at the START of each knockout round (bracket size).
STAGE_FIELD = {"R32": 32, "R16": 16, "QF": 8, "SF": 4, "Final": 2}
WILDCARD_BLOCKED = {"MD1", "R32"}
SIMS = 6000


def rates(form) -> tuple[float, float]:
    """(goals_per90, assists_per90), guards against tiny sample sizes."""
    mins = max(1, getattr(form, "minutes", 0) or 0)
    g = (getattr(form, "goals", 0) or 0) / mins * 90
    a = (getattr(form, "assists", 0) or 0) / mins * 90
    return g, a


def sim_points(pos: str, g90: float, a90: float, start_prob: float,
               am: float, n: int) -> list[float]:
    """Monte-Carlo n matches at fixture ease `am`. Right-skew matters for captaincy/12th-man."""
    out = []
    gp = GOAL_POINTS[pos]
    for _ in range(n):
        if random.random() > start_prob:        # didn't start / barely featured
            out.append(0.5 if random.random() < 0.3 else 0.0)
            continue
        pts = APPEARANCE * 2                      # ~60'+ appearance
        pts += _poisson(g90 * am) * gp
        pts += _poisson(a90 * am) * ASSIST
        if pos in ("GK", "DEF") and random.random() < 0.30 * am:
            pts += 5                              # occasional clean sheet
        out.append(float(pts))
    return out


def _poisson(lam: float) -> int:
    """Knuth Poisson sampler (lam is small here, so this is cheap)."""
    lam = max(0.0, lam)
    L, k, p = pow(2.718281828, -lam), 0, 1.0
    while True:
        k += 1
        p *= random.random()
        if p <= L:
            return k - 1


def team_overall(national: dict, fifa: dict) -> dict[str, float]:
    """nation -> normalised strength (~1.0 mean): FIFA rank nudged by gf-ga form."""
    raw = {}
    for nat, fs in fifa.items():
        ctx = national.get(nat, {})
        form_edge = (ctx.get("gf_pg", 1.3) - ctx.get("ga_pg", 1.3)) * 0.10
        raw[nat] = max(0.4, fs + form_edge)
    m = mean(raw.values())
    return {n: v / m for n, v in raw.items()}


def advance_prob(strength: float, stage_opp_avg: float) -> float:
    """P(advance) ~ own strength / (own + avg surviving opponent at this stage)."""
    return strength / (strength + stage_opp_avg)


def knockout_am(strength: float, stage_opp_avg: float) -> float:
    """Attacking ease vs a typical surviving opponent at this stage (clamped)."""
    return max(0.7, min(1.6, strength / stage_opp_avg))


def load_squad(pool, path=None):
    if path is None:
        path = Path(__file__).parent / "current_squad.json"
    cur = json.loads(open(path, encoding="utf-8").read())["squad"]
    held, missing = find_held(pool, cur)
    players = []
    for i in held:
        p = pool[i]
        f = p["form"]
        g90, a90 = rates(f)
        players.append({
            "name": p["name"], "nation": p["nation"], "pos": p["pos"],
            "xp": p["xp"], "own": p.get("ownership"), "start": getattr(f, "start_prob", 0.9),
            "g90": g90, "a90": a90,
        })
    return players, missing


def squad_xi(players):
    """Top 11 by xp — rough proxy for the starting XI."""
    return sorted(players, key=lambda p: -p["xp"])[:11]


def player_am(p, rnd, national, overall, stage_opp):
    if rnd in GROUP_ROUNDS:
        return national.get(p["nation"], {}).get("attack_multiplier", 1.0)
    s = overall.get(p["nation"], 1.0)
    return knockout_am(s, stage_opp[rnd])


def eval_round(rnd, players, pool, national, overall, stage_opp):
    xi = squad_xi(players)

    # --- Maximum Captain: E[max performer] - E[your default captain] ---
    sims = []
    capt_idx = max(range(len(xi)), key=lambda k: xi[k]["xp"])
    for p in xi:
        am = player_am(p, rnd, national, overall, stage_opp)
        sims.append(sim_points(p["pos"], p["g90"], p["a90"], p["start"], am, SIMS))
    e_max = mean(max(sims[k][s] for k in range(len(xi))) for s in range(SIMS))
    e_capt = mean(sims[capt_idx])
    max_capt_gain = e_max - e_capt   # extra points from doubling the best vs your pick

    # 12th Man: best out-of-squad player's projected round points
    # xp bakes in group fixture ease; knockout rounds rescale by strength ratio
    held_names = {p["name"] for p in players}
    best12 = None
    for q in pool:
        if q["name"] in held_names:
            continue
        base_am = national.get(q["nation"], {}).get("attack_multiplier", 1.0) or 1.0
        scale = 1.0 if rnd in GROUP_ROUNDS else player_am(q, rnd, national, overall, stage_opp) / base_am
        ev = q["xp"] * scale
        if best12 is None or ev > best12[1]:
            best12 = (q["name"], ev, q["nation"])

    # Qualification: 2 * sum of P(advance) for each XI starter
    qual = None
    if rnd in STAGE_FIELD:
        total = 0.0
        for p in xi:
            s = overall.get(p["nation"], 1.0)
            total += 2.0 * advance_prob(s, stage_opp[rnd]) * p["start"]
        qual = total

    return {
        "max_capt": max_capt_gain,
        "twelfth": best12,
        "qual": qual,
        "e_max": e_max,
    }


def plan_data(api):
    """Per-round EVs + recommended schedule, for the web app snapshot."""
    national = build_national_context(api)
    fifa = fifa_strength()
    overall = team_overall(national, fifa)
    pool = _pool(build_priced_survivors(api, 600, 0, refresh=False))
    players, _ = load_squad(pool)
    ranked = sorted(overall.values(), reverse=True)
    stage_opp = {r: mean(ranked[:n]) for r, n in STAGE_FIELD.items()}
    rows = {r: eval_round(r, players, pool, national, overall, stage_opp) for r in ROUNDS}

    chips = {
        "Maximum Captain": {r: rows[r]["max_capt"] for r in ROUNDS},
        "12th Man": {r: rows[r]["twelfth"][1] for r in ROUNDS},
        "Qualification": {r: rows[r]["qual"] for r in ROUNDS if rows[r]["qual"] is not None},
    }
    import itertools
    quant = ["Qualification", "12th Man", "Maximum Captain"]
    best_total, best_assign = -1.0, None
    for combo in itertools.permutations(ROUNDS, len(quant)):
        if any(chips[c].get(r) is None for c, r in zip(quant, combo)):
            continue
        total = sum(chips[c][r] for c, r in zip(quant, combo))
        if total > best_total:
            best_total, best_assign = total, combo
    used = set(best_assign)
    wc_round = next((r for r in ["R16", "QF", "MD3", "SF", "Final"] if r not in used), "R16")
    used.add(wc_round)
    myst_round = next((r for r in ["R16", "QF", "SF", "Final"] if r not in used), "QF")

    schedule = {c: {"round": r, "ev": round(chips[c][r], 2)} for c, r in zip(quant, best_assign)}
    schedule["Wildcard"] = {"round": wc_round, "ev": None}
    schedule["Mystery"] = {"round": myst_round, "ev": None}

    per_round = []
    for r in ROUNDS:
        d = rows[r]
        t = d["twelfth"]
        per_round.append({
            "round": r,
            "maxCaptain": round(d["max_capt"], 2),
            "twelfthMan": {"name": t[0], "nation": t[2], "ev": round(t[1], 1)} if t else None,
            "qualification": round(d["qual"], 1) if d["qual"] is not None else None,
        })
    return {"perRound": per_round, "schedule": schedule}


def main():
    api = ApiFootball(os.environ.get("API_FOOTBALL_KEY"))
    print("building national context + pool...")
    national = build_national_context(api)
    fifa = fifa_strength()
    overall = team_overall(national, fifa)
    pool = _pool(build_priced_survivors(api, 600, 0, refresh=False))
    players, missing = load_squad(pool)
    if missing:
        print("  unmatched:", [m["name"] for m in missing])

    ranked = sorted(overall.values(), reverse=True)
    stage_opp = {r: mean(ranked[:n]) for r, n in STAGE_FIELD.items()}

    rows = {r: eval_round(r, players, pool, national, overall, stage_opp) for r in ROUNDS}

    # ---- assemble report ----
    L = []
    L.append("# WC2026 Fantasy — Booster Strategy\n")
    L.append("_EV = expected fantasy points the chip adds in that round. Group rounds use "
             "real fixture ease; knockout rounds are team-strength proxies (bracket undrawn), "
             "so re-check once draws are made._\n")

    L.append("\n## Expected value by round\n")
    L.append("| Round | Max Captain (+pts) | 12th Man (best pick) | Qualification (+pts) |")
    L.append("|---|---|---|---|")
    for r in ROUNDS:
        d = rows[r]
        t = d["twelfth"]
        tw = f"{t[0]} ({t[2]}) +{t[1]:.1f}" if t else "-"
        q = f"+{d['qual']:.1f}" if d["qual"] is not None else "n/a"
        L.append(f"| {r} | +{d['max_capt']:.2f} | {tw} | {q} |")

    # ---- optimal one-chip-per-round assignment (greedy on EV) ----
    chips = {
        "Maximum Captain": {r: rows[r]["max_capt"] for r in ROUNDS},
        "12th Man": {r: rows[r]["twelfth"][1] for r in ROUNDS},
        "Qualification": {r: rows[r]["qual"] for r in ROUNDS if rows[r]["qual"] is not None},
    }
    # brute-force best assignment of 3 quantified chips to distinct rounds
    import itertools
    quant = ["Qualification", "12th Man", "Maximum Captain"]
    best_total, best_assign = -1.0, None
    for combo in itertools.permutations(ROUNDS, len(quant)):
        if any(chips[c].get(r) is None for c, r in zip(quant, combo)):
            continue
        total = sum(chips[c][r] for c, r in zip(quant, combo))
        if total > best_total:
            best_total, best_assign = total, combo
    assigned, used = {}, set()
    for chip, r in zip(quant, best_assign):
        assigned[chip] = (r, chips[chip][r])
        used.add(r)
    # Wildcard: first free knockout round (can't play at R32; value peaks once bracket thins)
    wc_round = next((r for r in ["R16", "QF", "MD3", "SF", "Final"] if r not in used), "R16")
    assigned["Wildcard"] = (wc_round, None)
    used.add(wc_round)
    myst_round = next((r for r in ["R16", "QF", "SF", "Final"] if r not in used), "QF")
    assigned["Mystery"] = (myst_round, None)

    L.append("\n## Recommended schedule\n")
    L.append("| Chip | Play in | Why |")
    L.append("|---|---|---|")
    why = {
        "Maximum Captain": "removes captain-DNP risk in the round your XI has the highest ceiling",
        "12th Man": "soft round where the best available non-squad player projects highest",
        "Qualification": "knockout round where most of your starters are favourites to advance",
        "Wildcard": "first post-R32 round — bracket has thinned, rebuild around survivors (can't use at R32)",
        "Mystery": "hold until revealed at R32, then slot into the best free knockout round",
    }
    for chip in ["Wildcard", "12th Man", "Maximum Captain", "Qualification", "Mystery"]:
        r, v = assigned[chip]
        extra = f" (≈+{v:.1f} pts)" if v else ""
        L.append(f"| **{chip}** | {r}{extra} | {why[chip]} |")

    L.append("\n## Triggers to re-evaluate\n")
    L.append("- **Re-run after each round** — eliminations and the next draw change every knockout number.")
    L.append("- **Maximum Captain**: pull it forward if a premium (Mbappé/Haaland/Kane) draws a clearly weak side in a knockout — a single soft tie can beat the averaged group ceiling.")
    L.append("- **Qualification**: only fire when your XI is concentrated in heavy favourites; if your squad spreads across coin-flip ties, bank it a round.")
    L.append("- **12th Man**: best paired with a round where a goal-machine outside your squad has the softest fixture; revisit the table's pick each round.")
    L.append("- **Wildcard**: if your group-stage squad survives R32 largely intact, save it for QF; if it's gutted, play it at R16.")

    out = "\n".join(L) + "\n"
    open("BOOSTER_STRATEGY.md", "w", encoding="utf-8").write(out)
    print("\n" + out)
    print("[wrote BOOSTER_STRATEGY.md]")


if __name__ == "__main__":
    raise SystemExit(main())
