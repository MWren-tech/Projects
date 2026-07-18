"""
Generate WC2026_RANKINGS_FOR_WRITERS.md — a large, self-contained reference a
sports writer (or an article-writing skill) can use to write about the player
rankings: full methodology, a column glossary, per-nation context, complete
per-position rankings (every player, not just the top 20), and narrative angles.
"""

from __future__ import annotations
import sys
from collections import defaultdict
from statistics import mean

from api_football import ApiFootball
from wc_shortlist import (build_priced_survivors, SEASON_WEIGHT, CLUB_RECENT_WEIGHT,
                          COUNTRY_WEIGHT, POOL, LEAGUE_TAG)
from national_strength import build_national_context
from fifa_rankings import FIFA_POINTS
from scoring import (GOAL_POINTS, ASSIST, CLEAN_SHEET, TEAM_PENS_PER_MATCH)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = "WC2026_RANKINGS_FOR_WRITERS.md"


def sp_label(f):
    parts = []
    if f.sp_pen_rank: parts.append(f"Pen #{f.sp_pen_rank}")
    if f.sp_fk_rank: parts.append(f"FK #{f.sp_fk_rank}")
    if f.sp_corner_rank: parts.append(f"Corner #{f.sp_corner_rank}")
    return ", ".join(parts) or "—"


def sp_short(f):
    parts = []
    if f.sp_pen_rank: parts.append(f"P{f.sp_pen_rank}")
    if f.sp_fk_rank: parts.append(f"FK{f.sp_fk_rank}")
    if f.sp_corner_rank: parts.append(f"C{f.sp_corner_rank}")
    return " ".join(parts) or "—"


def n(x, d=2):
    return "—" if x is None else f"{x:.{d}f}"


def pct(x):
    return "—" if x is None else f"{x*100:.0f}%"


def main():
    api = ApiFootball()
    national = build_national_context(api)
    surv = build_priced_survivors(api, 600, 40, verbose=True)
    ta = {nat: national.get(nat, {}).get("team_attack", 1.0) for nat in {c["nation"] for c in surv}}

    bypos = defaultdict(list)
    for c in surv:
        bypos[c["form"].position].append(c)
    for p in bypos:
        bypos[p].sort(key=lambda c: c["final_xp"], reverse=True)

    L: list[str] = []
    w = L.append

    # ---------------------------------------------------------------- header
    w("# WC2026 Fantasy — Player Rankings: Data & Methodology (Writer Reference)\n")
    w("*Auto-generated from the `wc_scout` model. Every number below is computed, not "
      "hand-edited. Use it to write about player rankings, captaincy, differentials, "
      "value picks, set-piece threats and fixtures — for any player in the pool, not "
      "just the headline names.*\n")
    w(f"**Pool:** {len(surv)} probable World Cup 2026 starters who exist in the official "
      f"FIFA Fantasy game, drawn from {len(POOL)} leagues "
      f"({', '.join(sorted(set(LEAGUE_TAG.values())))}).\n")
    w("---\n")

    # ---------------------------------------------------------------- how to read
    w("## 1. What a player's projection means\n")
    w("Every player carries one headline number — **xPts (projected points per match)** — "
      "the expected number of FIFA World Cup Fantasy points he earns in a single game. "
      "It is fully traceable: a rule × a rate × a probability, summed. Higher = better. "
      "It is per-match, so it is comparable across players and divisible by price.\n")
    w("Two players with the same xPts can tell very different stories — one might be a "
      "nailed-on penalty taker in a soft group, the other a hot-form differential nobody "
      "owns. The columns below let you find those angles.\n")

    # ---------------------------------------------------------------- methodology
    w("## 2. How xPts is built (methodology, in depth)\n")
    w("The projection is assembled in layers:\n")
    w("**(a) The FIFA scoring rules.** Points are awarded as in the official game: "
      f"appearance **+1**; a goal is worth **GK {GOAL_POINTS['GK']} / DEF {GOAL_POINTS['DEF']} / "
      f"MID {GOAL_POINTS['MID']} / FWD {GOAL_POINTS['FWD']}**; an assist **+{ASSIST}**; a clean "
      f"sheet **GK/DEF +{CLEAN_SHEET['GK']}, MID +{CLEAN_SHEET['MID']}**; goalkeeper saves **+1 per 3**; "
      "penalty save **+3**, penalty won **+2**, penalty conceded **−1**; yellow **−1**, red **−2**; "
      "midfield tackles **+1 per 3** and chances created **+1 per 2**; forward shots on target "
      "**+1 per 2**.\n")
    w("**(b) Per-90 rates.** Each player's club output (goals, assists, shots, key passes, "
      "tackles, saves, penalties, cards) is converted to a per-90-minute rate, then multiplied "
      "by the relevant point value to get an *expected* contribution — so we don't wait for "
      "real events, we project them.\n")
    w("**(c) Playing-time probability.** Every term is scaled by the player's chance of being "
      "on the pitch (**Start%**, from his lineup ratio), and clean-sheet points are additionally "
      "gated by his chance of reaching 60 minutes.\n")
    w("**(d) National clean-sheet model.** Goalkeeper/defender clean-sheet points use the "
      "player's **nation's** chance of a shut-out, computed by Poisson from that nation's "
      "defensive rating against its **actual group opponents** (`P(0 conceded)=exp(−opp xG)`). "
      "A leaky nation's defenders get a low clean-sheet chance no matter how good the individual.\n")
    w("**(e) Fixture difficulty (FixEase).** Attacking output is scaled by how weak the group "
      "opponents' defences are: **>1.0 = soft group, <1.0 = tough group**. This is why stars in "
      "brutal groups are shaded down and players in kind groups get a lift.\n")
    w("**(f) Team-strength factor (TeamStr).** Attacking output is *also* scaled by the player's "
      "**own** national-team quality — a blend of **50% FIFA world-ranking strength + 50% recent "
      "goals-for rate**, normalised to a tournament average of 1.0. This applies the 'lone star "
      "in a weak side' tax: a brilliant attacker with poor team-mates creates fewer chances and "
      "is discounted; a player in a strong side is boosted.\n")
    w("**(g) National set-piece duty.** If a player is his country's penalty / free-kick / corner "
      "taker, he gets extra expected goal/assist value (the primary penalty taker is credited with "
      f"~80% of the team's penalties, assuming ~{TEAM_PENS_PER_MATCH:.2f} penalties awarded per game). "
      "This is national duty, not club — it overrides club penalty records.\n")
    w("**(h) Three-window form blend.** The projection blends three snapshots, sample-weighted: "
      f"**club season ({int(SEASON_WEIGHT*100)}%)**, **club recent form ({int(CLUB_RECENT_WEIGHT*100)}%, "
      f"last ~40 league games)** and **country form ({int(COUNTRY_WEIGHT*100)}%, last ~8 internationals)**. "
      "A player hot for his country but quiet at club (or vice versa) is captured here.\n")
    w("**(i) League-strength discount.** The blended figure is multiplied by a per-league "
      "coefficient (Premier League 1.00 down to weaker leagues ~0.60), so a goal in a weaker league "
      "isn't valued like a goal in a top one.\n")
    w("**(j) Price & ownership.** Pulled from the official FIFA Fantasy game. **Value = xPts ÷ price** "
      "(points per $m). **Own%** is the share of squads that have picked him; under 5% is a differential.\n")
    w("**Final formula:** `xPts = [0.5·season + 0.3·club-recent + 0.2·country] × league-strength`, "
      "where each form window is itself scored through layers (a)–(g).\n")

    # ---------------------------------------------------------------- glossary
    w("## 3. Column glossary\n")
    gloss = [
        ("xPts", "Projected fantasy points per match — the headline ranking number."),
        ("$", "FIFA Fantasy price in $m."),
        ("Own%", "Ownership: share of all squads picking him. `*` flags a differential (<5%)."),
        ("Val", "Value = xPts per $m. Higher = more points for your money."),
        ("sXP / rXP / cXP", "The three form components before blending: club **s**eason, club **r**ecent, **c**ountry (international). `—` = no usable sample."),
        ("G / A", "Club goals / assists this season."),
        ("G/90 / A/90", "Per-90-minute goal / assist rates."),
        ("Start%", "Estimated chance he starts for his country (from club lineup security)."),
        ("CS%", "His nation's clean-sheet chance vs its group opponents."),
        ("FixEase", "Attacking fixture ease from the group draw (>1 soft, <1 tough)."),
        ("TeamStr", "Own national-team attacking strength (FIFA rank + recent scoring; ~1.0 = average; <1 weak, >1 strong)."),
        ("SetPiece", "National set-piece duty: Pen/FK/Corner taker rank (1 = first choice)."),
        ("Rtg", "Average club match rating this season (0–10)."),
    ]
    for k, v in gloss:
        w(f"- **{k}** — {v}")
    w("")

    # ---------------------------------------------------------------- nations
    w("## 4. National-team context (fixtures & strength)\n")
    w("Every attacking and clean-sheet number above is shaped by these nation-level inputs. "
      "Use this to write fixture/group angles.\n")
    w("| Nation | FIFA pts | Group opponents | GF/g | GA/g | TeamStr | CS% | xGA | FixEase |")
    w("|---|---:|---|---:|---:|---:|---:|---:|---:|")
    nat_rows = sorted(national.items(), key=lambda kv: kv[1].get("team_attack", 1), reverse=True)
    for nat, d in nat_rows:
        if nat not in ta and nat not in {c["nation"] for c in surv}:
            pass
        w(f"| {nat} | {FIFA_POINTS.get(nat,'—')} | {', '.join(d.get('opponents',[])) or '—'} "
          f"| {n(d.get('gf_pg'))} | {n(d.get('ga_pg'))} | {n(d.get('team_attack'))} "
          f"| {pct(d.get('clean_sheet_prob'))} | {n(d.get('expected_goals_against'))} "
          f"| {n(d.get('attack_multiplier'))} |")
    w("")

    # ---------------------------------------------------------------- per position
    w("## 5. Position rankings — every player\n")
    w("Full ranked lists (not just the top 20). Each row has everything needed to write about "
      "that player. `*` after Own% marks a differential (<5%).\n")
    posname = {"GK": "Goalkeepers", "DEF": "Defenders", "MID": "Midfielders", "FWD": "Forwards"}
    for pos in ("GK", "DEF", "MID", "FWD"):
        rows = bypos[pos]
        w(f"### {posname[pos]} — {len(rows)} ranked\n")
        w("| # | Player | Club | Nation | $ | Own% | Val | xPts | sXP | rXP | cXP | G | A | G/90 | A/90 | Start% | CS% | FixEase | TeamStr | SetPiece | Rtg |")
        w("|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|")
        for i, c in enumerate(rows, 1):
            f = c["form"]
            own = c.get("ownership")
            own_s = ("—" if own is None else f"{own:.1f}*" if own < 5 else f"{own:.1f}")
            w(f"| {i} | {f.name} | {f.team} | {c['nation']} | {n(c.get('price'),1)} | {own_s} "
              f"| {n(c.get('value'))} | **{n(c['final_xp'])}** | {n(c['season_xp'])} "
              f"| {n(c.get('recent_xp'))} | {n(c.get('country_xp'))} | {f.goals} | {f.assists} "
              f"| {n(f.per90['goals'])} | {n(f.per90['assists'])} | {pct(f.start_prob)} "
              f"| {pct(c['cs'])} | {n(c['diff'])} | {n(ta.get(c['nation']))} | {sp_short(f)} "
              f"| {n(f.rating,1)} |")
        w("")

    # ---------------------------------------------------------------- angles
    w("## 6. Ready-made narrative angles\n")
    priced = [c for c in surv if c.get("price")]

    def top(rows, key, k=15, rev=True):
        return sorted(rows, key=key, reverse=rev)[:k]

    w("### Captaincy candidates (highest projection, nailed starters)\n")
    cap = [c for c in surv if c["form"].position in ("MID", "FWD") and c["form"].start_prob >= 0.85]
    for c in top(cap, lambda c: c["final_xp"], 10):
        f = c["form"]
        w(f"- **{f.name}** ({c['nation']}, {f.position}) — {n(c['final_xp'])} xPts, "
          f"{f.goals}G/{f.assists}A, set-pieces: {sp_label(f)}, FixEase {n(c['diff'])}.")
    w("")

    w("### Best value (xPts per $m)\n")
    for c in top([c for c in priced if c['final_xp'] > 2], lambda c: c["value"], 15):
        f = c["form"]
        w(f"- **{f.name}** ({c['nation']}, {f.position}) — value {n(c['value'])} "
          f"(${n(c['price'],1)}, {n(c['final_xp'])} xPts), {c.get('ownership',0):.1f}% owned.")
    w("")

    w("### Biggest differentials (<5% owned, ranked by projection)\n")
    diff = [c for c in priced if (c.get("ownership") or 99) < 5]
    for c in top(diff, lambda c: c["final_xp"], 20):
        f = c["form"]
        w(f"- **{f.name}** ({c['nation']}, {f.position}) — {n(c['final_xp'])} xPts at "
          f"{c['ownership']:.1f}% owned, ${n(c['price'],1)}, {f.goals}G/{f.assists}A.")
    w("")

    w("### Set-piece kings (primary penalty takers)\n")
    pens = [c for c in surv if c["form"].sp_pen_rank == 1]
    for c in top(pens, lambda c: c["final_xp"], 20):
        f = c["form"]
        w(f"- **{f.name}** ({c['nation']}, {f.position}) — {sp_label(f)}; {n(c['final_xp'])} xPts.")
    w("")

    w("### Template players (most-owned)\n")
    for c in top(priced, lambda c: c.get("ownership") or 0, 12):
        f = c["form"]
        w(f"- **{f.name}** ({c['nation']}, {f.position}) — {c['ownership']:.1f}% owned, "
          f"{n(c['final_xp'])} xPts, ${n(c['price'],1)}.")
    w("")

    w("### Stars taxed by a weak national side (good player, weaker team)\n")
    w("*High individual club output but a sub-average team-strength factor — the model "
      "expects them to find chances harder at the World Cup.*\n")
    lone = [c for c in surv if ta.get(c["nation"], 1) < 0.95 and c["form"].goals >= 8
            and c["form"].position in ("MID", "FWD")]
    for c in top(lone, lambda c: c["form"].goals, 15):
        f = c["form"]
        w(f"- **{f.name}** ({c['nation']}, {f.position}) — {f.goals}G/{f.assists}A at club, "
          f"but TeamStr {n(ta.get(c['nation']))}; projects {n(c['final_xp'])} xPts.")
    w("")

    # ---------------------------------------------------------------- caveats
    w("## 7. Caveats (so articles don't over-claim)\n")
    w("- **It's a projection, not a prophecy** — an expected value built from rates and "
      "probabilities, blind to tactical role changes, injuries declared after the data pull, "
      "or a manager's whim.\n")
    w("- **No xG/xA** — the underlying feed lacks expected-goals data, so raw goals/assists are "
      "used; a player on a hot/cold finishing run can be over/under-stated.\n")
    w("- **FIFA world-ranking points are approximate** (hardcoded, late-2025) and the league-"
      "strength and team-strength coefficients are judgement calls — directionally sound, not exact.\n")
    w("- **Clean-sheet model ignores specific line-ups and home advantage** (USA/MEX/CAN hosts).\n")
    w("- **Start% comes from club minutes**, a proxy for international nailed-on status.\n")
    w(f"\n*Generated by `build_writer_doc.py` over {len(surv)} players.*\n")

    doc = "\n".join(L)
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"\nwrote {OUT}  ({len(surv)} players, {len(doc)} chars)")


if __name__ == "__main__":
    main()
