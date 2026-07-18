"""
WC2026 Fantasy 15-player squad optimiser.

Picks the squad that maximises expected points under the official rules:
  - 15 players: 2 GK, 5 DEF, 5 MID, 3 FWD
  - $100m budget
  - a valid starting XI: GK=1, DEF 3-5, MID 3-5, FWD 1-3 (totals 11)
  - captain doubles (we add the best starter's xPts once more)
  - optional max players per nation

Objective maximised = (sum of starting-XI expected points)
                     + (captain bonus = best starter's xPts)
                     + (small weight x bench expected points, as a tie-breaker)

It's an integer program solved exactly with PuLP/CBC when available; otherwise a
greedy + local-search heuristic is used. Player pool = the priced probable-starter
shortlist (wc_shortlist.build_priced_survivors).

    python optimise.py
    python optimise.py --budget 100 --max-per-nation 3 --bench-weight 0.1
"""

from __future__ import annotations

import argparse
import sys

from api_football import ApiFootball, ApiFootballError
from wc_shortlist import build_priced_survivors

SQUAD = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}          # 15 total
XI_MIN = {"GK": 1, "DEF": 3, "MID": 3, "FWD": 1}
XI_MAX = {"GK": 1, "DEF": 5, "MID": 5, "FWD": 3}
XI_TOTAL = 11


def _sp_label(form) -> str:
    parts = []
    if form.sp_pen_rank:
        parts.append(f"P{form.sp_pen_rank}")
    if form.sp_fk_rank:
        parts.append(f"FK{form.sp_fk_rank}")
    if form.sp_corner_rank:
        parts.append(f"C{form.sp_corner_rank}")
    return " ".join(parts)


def _pool(survivors: list[dict]) -> list[dict]:
    """Players usable by the optimiser: must have a price and a valid position."""
    out = []
    for c in survivors:
        f = c["form"]
        if not c.get("price") or f.position not in SQUAD:
            continue
        out.append({
            "name": f.name, "nation": c["nation"], "club": f.team, "pos": f.position,
            "pid": f.player_id, "fifa_id": c.get("fifa_id"),
            "price": float(c["price"]), "xp": float(c["final_xp"]),
            "own": c.get("ownership"), "value": c.get("value"),
            # extra player stats for the squad readout
            "goals": f.goals, "assists": f.assists,
            "g90": f.per90["goals"], "a90": f.per90["assists"],
            "cs": c.get("cs"), "diff": c.get("diff"), "sp": _sp_label(f),
            "scouting_xp": c.get("scouting_xp", 0),
            "form": c.get("recent_xp"), "rating": f.rating, "start": f.start_prob,
        })
    # de-dup by (name, nation, pos) keeping the highest xp
    best: dict[tuple, dict] = {}
    for p in out:
        k = (p["name"], p["nation"], p["pos"])
        if k not in best or p["xp"] > best[k]["xp"]:
            best[k] = p
    return list(best.values())


# --- exact ILP (PuLP) -----------------------------------------------------

def optimise_ilp(pool: list[dict], budget: float, max_per_nation: int | None,
                 bench_weight: float, held: set[int] | None = None,
                 max_transfers: int | None = None):
    import pulp

    prob = pulp.LpProblem("wc_squad", pulp.LpMaximize)
    idx = range(len(pool))
    pick = {i: pulp.LpVariable(f"pick_{i}", cat="Binary") for i in idx}
    start = {i: pulp.LpVariable(f"start_{i}", cat="Binary") for i in idx}
    capt = {i: pulp.LpVariable(f"capt_{i}", cat="Binary") for i in idx}

    # Objective: XI points + captain bonus + small bench weight
    prob += (
        pulp.lpSum(start[i] * pool[i]["xp"] for i in idx)
        + pulp.lpSum(capt[i] * pool[i]["xp"] for i in idx)
        + bench_weight * pulp.lpSum((pick[i] - start[i]) * pool[i]["xp"] for i in idx)
    )

    # Squad composition + budget
    prob += pulp.lpSum(pick[i] for i in idx) == 15
    for pos, n in SQUAD.items():
        prob += pulp.lpSum(pick[i] for i in idx if pool[i]["pos"] == pos) == n
    prob += pulp.lpSum(pick[i] * pool[i]["price"] for i in idx) <= budget

    # Starting XI: subset of the squad, valid formation
    for i in idx:
        prob += start[i] <= pick[i]
        prob += capt[i] <= start[i]
    prob += pulp.lpSum(start[i] for i in idx) == XI_TOTAL
    prob += pulp.lpSum(capt[i] for i in idx) == 1
    for pos in SQUAD:
        s = pulp.lpSum(start[i] for i in idx if pool[i]["pos"] == pos)
        prob += s >= XI_MIN[pos]
        prob += s <= XI_MAX[pos]

    if max_per_nation:
        for nation in {p["nation"] for p in pool}:
            prob += pulp.lpSum(pick[i] for i in idx if pool[i]["nation"] == nation) <= max_per_nation

    # Transfer limit: keep at least (held - max_transfers) of the current squad.
    if held and max_transfers is not None:
        prob += pulp.lpSum(pick[i] for i in held) >= len(held) - max_transfers

    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[status] != "Optimal":
        raise RuntimeError(f"solver status: {pulp.LpStatus[status]}")

    squad = [i for i in idx if pick[i].value() > 0.5]
    starters = {i for i in idx if start[i].value() > 0.5}
    captain = next(i for i in idx if capt[i].value() > 0.5)
    # Scoring value of the lineup (XI + captain bonus), the metric a transfer must
    # justify. Excludes the small bench weight so marginal gains aren't muddied.
    score = sum(pool[i]["xp"] for i in starters) + pool[captain]["xp"]
    return squad, starters, captain, score


# --- greedy + local search fallback --------------------------------------

def optimise_greedy(pool: list[dict], budget: float, max_per_nation: int | None,
                    bench_weight: float):
    # Cheapest valid bench by position, expensive/high-xp starters. Heuristic:
    # pick best XI greedily by xp within budget, fill bench cheapest, then swap.
    import itertools

    by_pos = {pos: sorted([p for p in pool if p["pos"] == pos],
                          key=lambda p: p["xp"], reverse=True) for pos in SQUAD}

    def nation_ok(chosen):
        if not max_per_nation:
            return True
        from collections import Counter
        c = Counter(p["nation"] for p in chosen)
        return all(v <= max_per_nation for v in c.values())

    best = None
    for d, m, f in itertools.product(range(XI_MIN["DEF"], XI_MAX["DEF"] + 1),
                                     range(XI_MIN["MID"], XI_MAX["MID"] + 1),
                                     range(XI_MIN["FWD"], XI_MAX["FWD"] + 1)):
        if 1 + d + m + f != XI_TOTAL:
            continue
        # starters: top by xp per position; bench: cheapest remaining to complete squad
        xi = (by_pos["GK"][:1] + by_pos["DEF"][:d] + by_pos["MID"][:m] + by_pos["FWD"][:f])
        bench = []
        for pos, need in (("GK", 2 - 1), ("DEF", 5 - d), ("MID", 5 - m), ("FWD", 3 - f)):
            cheap = sorted([p for p in by_pos[pos] if p not in xi], key=lambda p: p["price"])
            bench += cheap[:need]
        squad = xi + bench
        if len(squad) != 15:
            continue
        cost = sum(p["price"] for p in squad)
        if cost > budget or not nation_ok(squad):
            continue
        cap = max(xi, key=lambda p: p["xp"])
        score = sum(p["xp"] for p in xi) + cap["xp"] + bench_weight * sum(p["xp"] for p in bench)
        if not best or score > best[0]:
            best = (score, squad, xi, cap)
    if not best:
        raise RuntimeError("no feasible squad found under budget (heuristic)")
    _, squad, xi, cap = best
    sset = {id(p) for p in xi}
    pool_index = {id(p): i for i, p in enumerate(pool)}
    squad_i = [pool_index[id(p)] for p in squad]
    start_i = {pool_index[id(p)] for p in xi}
    cap_i = pool_index[id(cap)]
    return squad_i, start_i, cap_i


# --- output ---------------------------------------------------------------

def _formation(pool, starters) -> str:
    from collections import Counter
    c = Counter(pool[i]["pos"] for i in starters)
    return f"{c['DEF']}-{c['MID']}-{c['FWD']}  (GK {c['GK']}, DEF {c['DEF']}, MID {c['MID']}, FWD {c['FWD']})"


def render(pool, squad, starters, captain, budget) -> str:
    # Ranked by expected (projected) points, highest first.
    squad = sorted(squad, key=lambda i: pool[i]["xp"], reverse=True)
    cost = sum(pool[i]["price"] for i in squad)
    xi_pts = sum(pool[i]["xp"] for i in starters)
    cap_pts = pool[captain]["xp"]

    cols = [
        ("Pos", 4, "l"), ("Player", 21, "l"), ("Nation", 13, "l"), ("Club", 14, "l"),
        ("Price", 6, "r"), ("ProjPts", 7, "r"), ("Own%", 6, "r"), ("Value", 6, "r"),
        ("Gls", 4, "r"), ("Ast", 4, "r"), ("G/90", 5, "r"), ("A/90", 5, "r"),
        ("Start%", 6, "r"), ("CS%", 5, "r"), ("FixEase", 7, "r"),
        ("SetPiece", 9, "l"), ("Form", 5, "r"), ("Rating", 6, "r"),
    ]

    def row(cells):
        out = []
        for (name, w, align), val in zip(cols, cells):
            s = str(val)
            out.append(f"{s:<{w}}" if align == "l" else f"{s:>{w}}")
        return "  ".join(out)

    header = row([c[0] for c in cols])
    lines = [
        "WC2026 FANTASY - OPTIMAL 15-PLAYER SQUAD",
        f"Budget: ${cost:.1f}m of ${budget:.0f}m used  (${budget-cost:.1f}m free)   |   "
        f"Projected points: starting XI {xi_pts:.1f} + captain {cap_pts:.1f} = {xi_pts+cap_pts:.1f}",
        "",
        "Column guide:",
        "  ProjPts  = projected fantasy points per match (our full model)",
        "  Own%     = share of all squads picking him  (* = differential, under 5% owned)",
        "  Value    = projected points per $1m of price",
        "  Gls/Ast  = club goals / assists this season    G/90, A/90 = per-90-minute rates",
        "  Start%   = chance he starts for his country     CS% = his nation's clean-sheet chance vs its group",
        "  FixEase  = attacking fixture ease (>1.0 = soft group, <1.0 = tough group)",
        "  SetPiece = national set-piece duty: P=penalty, FK=free-kick, C=corner (rank, 1 = first choice)",
        "  Form     = recent points per match (last games)   Rating = average match rating (0-10)",
        "  (C) = captain (points doubled)    [B] = bench (other 11 are the starting XI)",
        "",
        f"  Ranked by ProjPts.  Starting formation: {_formation(pool, starters)}",
        "",
        header,
        "-" * len(header),
    ]
    for i in squad:
        p = pool[i]
        name = p["name"][:16] + (" (C)" if i == captain else (" [B]" if i not in starters else ""))
        own = p["own"]
        own_s = (f"{own:.1f}*" if (own is not None and own < 5) else
                 f"{own:.1f}" if own is not None else "-")
        lines.append(row([
            p["pos"], name, p["nation"][:13], p["club"][:14],
            f"{p['price']:.1f}", f"{p['xp']:.2f}", own_s,
            f"{p['value']:.2f}" if p["value"] is not None else "-",
            p["goals"], p["assists"], f"{p['g90']:.2f}", f"{p['a90']:.2f}",
            f"{p['start']*100:.0f}%", f"{p['cs']*100:.0f}%" if p["cs"] is not None else "-",
            f"{p['diff']:.2f}" if p["diff"] is not None else "-",
            p["sp"] or "-", f"{p['form']:.2f}" if p["form"] is not None else "-",
            f"{p['rating']:.1f}",
        ]))

    bench = [i for i in squad if i not in starters]
    lines += ["", "Bench (4): " + ", ".join(
        f"{pool[i]['name']} (${pool[i]['price']:.1f})" for i in bench),
        "[B] = bench"]
    return "\n".join(lines)


def find_held(pool, current_entries):
    """Return (set of pool indices held, list of unmatched current entries)."""
    from set_piece_takers import name_matches, canonical_nation
    held, missing = set(), []
    for e in current_entries:
        nat = canonical_nation(e["nation"]) or e["nation"]
        cands = [i for i, p in enumerate(pool)
                 if p["nation"] == nat and p["pos"] == e["pos"]
                 and name_matches(e["name"], p["name"]) and i not in held]
        if cands:
            held.add(max(cands, key=lambda i: pool[i]["xp"]))   # best match if several
        else:
            missing.append(e)
    return held, missing


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="WC2026 Fantasy squad optimiser")
    parser.add_argument("--budget", type=float, default=100.0)
    parser.add_argument("--max-per-nation", type=int, default=3,
                        help="cap players from one nation (FIFA WC Fantasy rule = max 3)")
    parser.add_argument("--bench-weight", type=float, default=0.1,
                        help="weight on bench xPts (0 = cheapest bench, higher = stronger bench)")
    parser.add_argument("--min-minutes", type=int, default=600)
    parser.add_argument("--recent", type=int, default=40)
    parser.add_argument("--free", type=int, default=2,
                        help="free transfers this round (2 before MD2/MD3; unlimited at R32; "
                             "4/4/5/6 in the knockouts)")
    parser.add_argument("--hit", type=float, default=3.0,
                        help="points lost per transfer beyond the free allocation (rules: -3)")
    parser.add_argument("--bank-hurdle", type=float, default=0.5,
                        help="a FREE transfer below this gain is banked instead (1 carries over "
                             "within the group stage)")
    parser.add_argument("--transfers", type=int, default=None,
                        help="max changes from --current squad (transfer mode)")
    parser.add_argument("--current", default="current_squad.json",
                        help="JSON of the 15 currently-held players (for transfer mode)")
    parser.add_argument("--refresh", action="store_true",
                        help="rebuild the player pool from the API (else use .pool_cache.pkl)")
    parser.add_argument("--out", default="wc_squad.txt")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    try:
        api = ApiFootball()
    except ApiFootballError as e:
        print(f"Setup error: {e}", file=sys.stderr)
        return 1

    survivors = build_priced_survivors(api, args.min_minutes, args.recent, refresh=args.refresh)
    pool = _pool(survivors)
    print(f"  optimising over {len(pool)} priced players...")

    held, missing = None, []
    transfer_note = ""
    if args.transfers is not None:
        import json
        cur = json.loads(open(args.current, encoding="utf-8").read())["squad"]
        held, missing = find_held(pool, cur)
        print(f"  transfer mode: matched {len(held)}/{len(cur)} of current squad, "
              f"max {args.transfers} transfers")
        if missing:
            print(f"  (couldn't match in pool: {', '.join(m['name'] for m in missing)})")

    if held is None:
        squad, starters, captain, _ = optimise_ilp(
            pool, args.budget, args.max_per_nation, args.bench_weight, held, args.transfers)
    else:
        # Marginal-gain ladder: solve at 0,1,...,max transfers and measure the XI-xPts
        # each ADDITIONAL transfer buys. A transfer is only worth using if its marginal
        # gain clears the hurdle (gains are non-increasing, so we stop at the first miss).
        ladder = []
        for k in range(args.transfers + 1):
            sq, st, cp, sc = optimise_ilp(pool, args.budget, args.max_per_nation,
                                          args.bench_weight, held, k)
            ladder.append((k, sq, st, cp, sc))

        # Two-tier hurdle: the first `--free` transfers cost nothing, so they only need
        # to beat the small bank-hurdle (worth saving 1 for next round otherwise). Every
        # transfer BEYOND the free allocation costs `--hit` points, so it must add more
        # than that to its net to be worth taking. Gains are non-increasing (concave),
        # so we walk the ladder and stop at the first transfer that fails its hurdle.
        best_k = 0
        for k in range(1, len(ladder)):
            marginal = ladder[k][4] - ladder[best_k][4]
            hurdle = args.bank_hurdle if k <= args.free else args.hit
            if marginal >= hurdle:
                best_k = k
            else:
                break
        squad, starters, captain = ladder[best_k][1], ladder[best_k][2], ladder[best_k][3]
        hits = max(0, best_k - args.free)
        print(f"  free={args.free}, hit={args.hit:.0f}/extra -> recommending {best_k} transfer(s)"
              f"{f' ({hits} paid, -{hits*args.hit:.0f} pts)' if hits else ''}")

        # Show the full ladder so the marginal value of each transfer is visible.
        lines = ["", "=== TRANSFER VALUE LADDER ==="]
        for k in range(1, len(ladder)):
            marg = ladder[k][4] - ladder[k - 1][4]
            if k <= args.free:
                net, tier = marg, "FREE"
            else:
                net, tier = marg - args.hit, f"-{args.hit:.0f} hit"
            flag = "USE" if k <= best_k else "BANK"
            lines.append(f"  transfer #{k}: +{marg:.2f} gross  ({tier}, net {net:+.2f})   [{flag}]")

        new_ids = set(squad)
        out_idx = [i for i in held if i not in new_ids]
        in_idx = [i for i in new_ids if i not in held]
        lines.append("")
        lines.append("=== RECOMMENDED TRANSFERS ===" if out_idx
                     else "=== NO TRANSFER CLEARS THE HURDLE — BANK ALL ===")
        for o, n in zip(sorted(out_idx, key=lambda i: pool[i]["xp"]),
                        sorted(in_idx, key=lambda i: pool[i]["xp"])):
            po, pn = pool[o], pool[n]
            lines.append(f"  OUT  {po['name']} ({po['nation']}, {po['pos']}, ${po['price']:.1f}, "
                         f"{po['xp']:.2f} xPts)")
            lines.append(f"  IN   {pn['name']} ({pn['nation']}, {pn['pos']}, ${pn['price']:.1f}, "
                         f"{pn['xp']:.2f} xPts)   [+{pn['xp']-po['xp']:.2f} xPts]")
        transfer_note = "\n".join(lines) + "\n"

    report = render(pool, squad, starters, captain, args.budget) + "\n" + transfer_note + f"\nSolver: exact ILP (PuLP/CBC)\n"
    from pathlib import Path
    Path(args.out).write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"[wrote {args.out}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
