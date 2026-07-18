# Projection model — how xPts is computed

The model estimates each player's **expected fantasy points per match (`final_xp`)**. Built in `wc_shortlist.py` + `scoring.py` + `national_strength.py`.

## 1. Per-window expected points (`scoring.form_to_xpts` / `expected_points`)
For a given form sample + fixture context, compute expected points from per-90 rates × the relevant scoring values (see [scoring-rules.md](scoring-rules.md)), gated by:
- **start probability** (`start_prob`) — earns the rate stats,
- **p_sixty** — gates 60'+ appearance point and clean sheets,
- **attacking multiplier** `am = attack_multiplier × team_attack` — scales goals/assists/shots/chances.

## 2. Four form windows, sample-weighted blend (`blend_forms`)
| Window | Weight | Source |
|---|---|---|
| Season (club) | 0.30 | club league season stats |
| Club-recent | 0.15 | last-N club matches (optional) |
| Country | 0.10 | recent internationals |
| **World Cup** | **0.45** | actual WC matches (grows as the tournament runs) |
Weights are **renormalised by available sample** (a player with no WC minutes leans on the other windows). Country & WC are scored with `team_attack = 1.0` (real output already reflects the team).

## 3. Multipliers applied
- **League strength** (`final_xp = blended × strength`) — discounts weak-league form (`POOL` table in `wc_shortlist.py`).
- **Fixture difficulty** (`national_strength.py`) — opponents' defensive weakness, **weighted to the next unplayed group game** (60/40), and **updated with WC results**.
- **Team strength / `team_attack`** (`fifa_rankings.py`) — FIFA ranking blended with recent goals-for, clamped — a great player in a weak side gets fewer chances.
- **National clean-sheet** — Poisson `exp(−opponent xG)` over the group.
- **Set-piece duty** (`set_piece_takers.py`) — national penalty/FK/corner takers (overrides club records).

## 4. WC-adjusted start probability + actual-starter pool admission
`wc_adjusted_start()` blends the club-nailed prior with **actual WC lineups** — a club-nailed player who's been benched (e.g. Guéhi: 1 app, 0 starts) is correctly down-weighted, cutting his appearance + rate points.

The same "real lineups are the truth" principle gates **pool membership**: `apply_starter_filter` normally keeps only players in the pre-tournament probable XI (`probable_xi.py`), but once the tournament is live, **any player with a genuine WC start** (`wc_forms[...].lineups >= 1`) is admitted even if the published XI missed him (e.g. Isak, Nathaniel Brown, Elijah Just). Without this they fall back to FIFA's `avgPoints` and never get a blended projection — appearing frozen at round-1 points. Impact subs who haven't started (e.g. Undav: 26' off the bench) are **not** admitted, to keep cameo players out of the pool; they remain register-fallback. Pool membership is a static-window decision, so admitting new starters requires `--refresh`.

## 5. Scouting (differential) bonus — priced into projections
`export_snapshot.expected_scouting_bonus(xp, ownership)` adds an **expected** +2 × P(haul) for **<5%-owned** players (0 for ≥5%). This rewards low-owned upside the base model ignores — a genuine rank edge. Applied to `final_xp` at export time using **fresh FIFA ownership**. Visible per player as `scoutingBonus`.

## 6. Outputs consumed downstream
`final_xp` feeds: the rankings, the **ILP optimiser** (`optimise.py`: 15-man squad, valid XI, captain, max-3/nation), the **transfer marginal-gain ladder**, and the **Monte-Carlo booster planner** (`booster_planner.py`).

## Honesty notes
- Bucketed historical stats (saves/3, tackles/3, etc.) on tournament totals are **indicative**; per-occurrence stats are exact.
- "Points so far" uses FIFA's authoritative total, not this projection.
