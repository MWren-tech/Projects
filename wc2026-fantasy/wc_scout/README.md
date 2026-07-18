# WC2026 Fantasy Scout — API-Football pipeline

A cache-backed Python client for [API-Football v3](https://www.api-football.com/documentation-v3)
plus a fantasy scoring layer transcribed from the WC2026 Fantasy ruleset.

## Files
- `api_football.py` — REST client. Reads your key from `API_FOOTBALL_KEY` (or `.env`), caches
  every response to disk (default `.api_cache/`, 12h TTL), backs off on 429s (and the per-minute
  `rateLimit` 200-payload), and tracks your remaining daily quota. Endpoints: `fixtures`, `odds`,
  `predictions`, `players`/`player_stats_paginated`, `injuries`, `standings`, `teams`, `lineups`.
- `scoring.py` — single source of truth for the ruleset (verified against the official FIFA World
  Cup Fantasy 2026 scoring table). `score_actual()` backtests a real stat line; `expected_points()`
  is the forward-looking xPts model — a fully itemised expectation over every scored event
  (goals, assists, clean sheet, goals-conceded penalty, saves, penalties won/conceded/saved,
  card downside, position bonuses); `value_score()` is xPts/$m.
- `player_form.py` — shared extraction. Turns a `/players` entry into a `PlayerForm` carrying every
  scored stat (incl. saves, penalties scored/won/conceded/saved, cards, shots total), per-90 rates,
  a `pen_taker` flag, and derived `start_prob`/`p_sixty` (minutes security from lineups÷appearances).
  Both tools below use it so they never drift apart.
- `recent_form.py` — opt-in last-N CLUB form. Pulls the league's most recent finished fixtures via
  `/fixtures?last=N` + `/fixtures/players`, aggregates per player, and scores that window with the
  same ruleset — so recent xPts can be compared against season xPts.
- `country_form.py` — recent INTERNATIONAL form. For each WC nation pulls its last-N internationals
  (`/fixtures?team=<id>&last=N` + `/fixtures/players`), aggregates per player (by global player id),
  and builds a PlayerForm. The shortlist blends this as a 3rd form component (cXP) alongside club
  season + club recent (default weights 50/30/20, sample-weighted; country counts from ~45 intl mins).
- `league_report.py` — generates the per-league `.txt` reports (one file per league; mapping in the
  `LEAGUES` dict). Columns: xPts, minutes, start%, per-90 rates, saves/clean-sheet, PK (pens
  scored/attempted, `*`=designated taker), cards, rating, injury flag, and optional `rXP`/`rGp`
  (recent form). Run `python league_report.py [--only stem...] [--min-minutes N] [--top N] [--recent N]`.
- `set_piece_takers.py` — national-team penalty / free-kick / corner takers for all 48 WC2026 teams
  (leftmost = primary). For the World Cup, a player's CLUB penalty record is the wrong threat — his
  NATIONAL set-piece role is what matters. `apply_set_pieces(form, nation)` overlays this; the primary
  penalty taker gets a graded `pen_share` boost, the primary FK/corner taker small expected FK/assist
  bumps. Auto-applied by scout.py and wc_picker.py for league=1 (no-op for club team names). Output
  carries a `set_piece_role` tag (e.g. `P1 FK1 C1`).
- `probable_xi.py` — probable WC2026 starting XI for all 48 nations (goal.com). Used as the
  "consistent international starter" filter in the shortlist.
- `national_strength.py` — national-team attack/defence ratings from recent international GF/GA,
  plus WC group opponents, producing per-nation clean-sheet prob, expected goals against, and an
  attacking fixture-difficulty multiplier (vs the actual group draw).
- `wc_shortlist.py` — the WC2026 best-by-position ranker. Pool = Big-5 + POR/NED/BRA, scored by
  expected points after: league-strength multiplier, recent+season form blend (sample-weighted),
  probable-XI starter filter, national set-piece duty, and NATIONAL clean-sheet + group fixture
  difficulty. `python wc_shortlist.py --top 15`. Writes wc_shortlist.txt.
- `fifa_fantasy.py` — pulls the official FIFA WC2026 Fantasy feeds (`players.json` price + `percentSelected`
  ownership; `squads.json` squad→nation map; cached to `.fifa_cache/`). `match_price()` links a player to
  their FIFA price/ownership by nation + name. NOTE: use `squads.json` (2026), NOT `squads_fifa.json` (stale 2022).
- `best_by_position.py` — simpler raw cross-league top-N (no WC adjustments). Writes best_by_position.txt.

`wc_shortlist.py` now adds `$` (price), `Own%` (ownership, `*`=differential <5%) and `Val` (xPts/$m).
`--sort value` ranks by value for budget building; `--max-price N` filters to affordable picks.

- `optimise.py` — exact 15-player squad optimiser (FIFA rules: 2 GK/5 DEF/5 MID/3 FWD, $100m, valid XI
  formation, captain doubled, optional `--max-per-nation`). Integer program solved with PuLP/CBC
  (`pip install pulp`); falls back to a greedy heuristic if PuLP is absent. Writes wc_squad.txt.
  `python optimise.py [--budget 100] [--max-per-nation 3] [--bench-weight 0.1]`
- `PRICE_OWNERSHIP_PLAN.md` — plan for adding FIFA-game price & ownership (needed for value/$m and the
  scouting bonus), which API-Football does not provide.
- `scout.py` — fixtures → match signals (`/predictions` Poisson clean-sheet, `/odds` fallback) →
  `/injuries` flags → player form → ranked xPts table (JSON + CSV).
- `wc_picker.py` — standalone ranker: `/players` + `/standings` (Poisson clean-sheet) + `/injuries`
  exclusion → ranked shortlist + best-by-position, printed and written to `wc_picks.csv`.

## Setup

```bash
pip install requests
export API_FOOTBALL_KEY="your_key_here"   # never hardcode this
```

Your key lives only in the environment. Nothing in this code writes it to disk or logs it.

## Run

```bash
python scout.py --league 1 --season 2026 --next 10 --out scout_output
```

Outputs `scout_output.json` (full) and `scout_output_players.csv` (ranked by xPts/match).

Or the standalone ranker (defaults to WC2026, league=1 season=2026):

```bash
python wc_picker.py --top 30 --min-minutes 90
```

Both CSVs now include per-90 columns (minutes, `tackles_per90`, `goals_per90`, …), `start_prob`,
`p_sixty`, `clean_sheet_prob`, `expected_goals_against`, and an `injured` flag.

## Important caveats

1. **WC2026 data won't exist until the tournament is live.** Point this at qualifiers,
   friendlies, or club seasons to build player form, then map those players onto your
   squad list manually. League/season ids: find them via the `/leagues` endpoint or the
   API-Football dashboard.
2. **Free tier ≈ 100 requests/day.** A full scout run touches fixtures + odds-per-fixture +
   players-per-team, which adds up fast. Caching protects you; tune `API_FOOTBALL_CACHE_TTL`.
3. **Clean-sheet probability is modelled, not a market.** `scout.py` prefers `/predictions`
   (Poisson `P(0 conceded) = exp(-opponent_xG)` from each side's season scoring average) and
   falls back to the `/odds` Over/Under 2.5 proxy. `wc_picker.py` derives it from `/standings`
   goals-conceded-per-game. Both are transparent estimates — refine the rates as data fills in.
4. **xPts is deliberately transparent, not a black box.** Tune the rate inputs in `scoring.py`
   from real form and the output stays explainable and directly comparable across players.

## Tuning the ruleset
If the official game changes any value, edit the constants block at the top of `scoring.py`.
Everything downstream reads from there.
