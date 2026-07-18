# Plan: bringing in player price & ownership

## Why this matters
Two scoring/strategy levers depend on data **API-Football does not have**:

1. **Price ($value)** — the game gives **$100m for 15 players**. Without prices you
   can rank players by xPts but can't build a legal squad or compute **value
   (xPts per $m)**. `scoring.value_score(xpts, price)` already exists and is waiting
   for a price input.
2. **Ownership %** — needed to model the **Scouting Bonus (+2 for >4 pts AND <5%
   owned)** and to find differentials. Also drives template/risk analysis.

Both live only in the **official FIFA World Cup Fantasy game** (`play.fifa.com`),
not in any match-data API.

## Source options (in order of preference)

### A. FIFA Fantasy public JSON endpoints (best, if available)
Fantasy sites (FPL especially) expose a "bootstrap" JSON with every player's
price, ownership %, position and team in one request. FIFA's WC Fantasy almost
certainly has an equivalent (e.g. a `…/players` or `bootstrap-static`-style JSON
behind `play.fifa.com/fantasy`). Plan:
- Inspect the network tab on play.fifa.com/fantasy to find the JSON feed.
- One unauthenticated GET → all players with `price`, `selected_by_percent`,
  `team`, `position`, `id`, `name`.
- Refresh daily (prices drift, ownership moves).

**Cost:** ~1 request, no API-Football quota used. Cleanest if the feed is public.

### B. Manual CSV (reliable fallback, zero scraping)
A `prices.csv` you paste from the game once per matchday:
```
name,team,position,price,ownership
Kylian Mbappé,France,FWD,12.0,41.3
...
```
- We load it, fuzzy-match to API-Football players by (name, team), and merge.
- Pro: no dependency on FIFA's site structure. Con: manual upkeep.

### C. Scrape the rendered page (last resort)
Only if A is gated and B is too tedious. Brittle; avoid.

## The matching problem (the real work)
FIFA names ≠ API-Football names ("Kylian Mbappé" vs "K. Mbappé", accents, "Jr").
Plan a small `merge_prices.py`:
- Normalise: strip accents, lowercase, drop initials/punctuation.
- Match on (normalised surname + team), then fall back to fuzzy ratio.
- Emit an **unmatched report** so you can hand-fix the handful that don't link.
- Cache the resolved `fifa_id ↔ apifootball_id` map so it's one-time effort.

## Pipeline wiring once price/ownership exist
- Add `price`, `ownership` to the report rows.
- New columns: **$** (price), **Own%**, and **Val** = `value_score(xPts, price)`.
- Add a **value sort** mode (`--sort value`) and a **budget squad optimiser**
  (`optimise.py`): pick the best 15 (2/5/5/3) under $100m by xPts, then the best
  starting XI — a simple linear/greedy or ILP (pulp) solve.
- Feed `ownership` into `scoring.apply_scouting_bonus()` (already implemented) so
  differential value is modelled, not just raw xPts.

## Recommended first step
Try **A** for WC2026 once the game's player list is live (the squads/prices
publish before the tournament). If the JSON isn't reachable, fall back to **B**
with a one-time CSV. Either way the matching layer (`merge_prices.py`) is the
reusable core and should be built first.
