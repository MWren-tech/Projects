# Glossary

| Term | Meaning |
|---|---|
| **xPts / `final_xp`** | Expected fantasy points per match — the model's core projection. |
| **Snapshot** | `wc-companion/data/snapshot.json` — the model's output and the only model↔app interface. |
| **Pool / survivors** | The filtered set of players the engine projects (passed minute/league/FIFA filters). A subset of the full FIFA register. |
| **4-window blend** | Combining season / club-recent / country / WC form, sample-weighted. |
| **`team_attack`** | Own-team attacking strength (FIFA rank + recent goals) — discounts a star in a weak side. |
| **Fixture ease / `attack_multiplier`** | Opponent defensive weakness; >1 = soft, <1 = tough. Weighted to the next group game. |
| **Start prob / p_sixty** | P(in the XI) and P(reaching 60') — gate appearance points and clean sheets; corrected by actual WC lineups. |
| **Scouting bonus** | FIFA +2 for a <5%-owned player scoring >4 in a match; priced into projections as an expected value. |
| **Differential** | A low-owned player (<5%) — gains rank, not just points. |
| **wcStats** | A player's actual WC tally + per-stat points + FIFA-authoritative total. |
| **Incremental refresh** | Cheap daily update: re-pull only WC form + fixtures + FIFA feed, re-blend; reuse static windows. |
| **Booster / chip** | Wildcard, 12th Man, Maximum Captain, Qualification, Mystery (see scoring-rules). |
| **MD** | Matchday (group rounds MD1–MD3); then R32, R16, QF, SF, Final. |
| **`fifa_id` / `pid`** | Join keys: `fifa_id` = FIFA player id; `pid` = API-Football player id. |
