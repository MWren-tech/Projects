# WC2026 Fantasy — Squad Decision Report

This explains *why* the optimiser picked each player, with the data behind every
call, and compares the choices against the next-best options on the shortlists.
It's meant as a discussion document: where you disagree, tell me, and I'll fold
your perspective into the next version of the model.

**Quick reminder of how a player earns his "ProjPts" (projected points/match):**
appearance + goals (GK 9 / DEF 7 / MID 6 / FWD 5) + assists (3) + clean sheets
(GK/DEF 5, MID 1) − cards/concessions, with **four WC adjustments layered on top**:
league strength (club output discounted by league quality), recent+season form
blend, **national clean-sheet vs the actual group draw** (CS%), and **attacking
fixture ease** (FixEase: >1 soft group, <1 tough). Set-piece duty (penalty/FK/
corner taker for the country) adds expected goal/assist value.

**The squad (3-5-2, $99.9m, 83.3 projected pts incl. captain):**

| Pos | Starting XI | $ | ProjPts | Bench | $ |
|---|---|---|---|---|---|
| GK | E. Martínez | 5.0 | 5.38 | Pickford | 4.8 |
| DEF | Guéhi, Hakimi, Van Dijk | 16.6 | 14.8 | Romero, Bensebaïni | 9.3 |
| MID | Yamal, Çalhanoğlu, Raphinha, Saibari, Bruno Fernandes | 40.6 | 37.3 | — | |
| FWD | Kane (C), Malen | 16.6 | 16.6 | Ueda | 7.0 |

---

## 1. Goalkeepers — Martínez (start) + Pickford (bench)

Goalkeeper points are almost entirely **clean-sheet + saves driven**, so the model
is really ranking *national defences and their groups*, not shot-stopping reputation.

| # | Keeper | Nat | $ | ProjPts | Val | CS% | FixEase | Form |
|---|---|---|---|---|---|---|---|---|
| 1 | **E. Martínez** | ARG | 5.0 | 5.38 | 1.08 | 62% | 0.87 | 6.05 |
| 2 | **Pickford** | ENG | 4.8 | 4.96 | 1.03 | 68% | 1.20 | 4.85 |
| 3 | Suzuki | JPN | 4.3 | 4.54 | 1.06 | 55% | 1.23 | 4.96 |
| 4 | Unai Simón | ESP | 5.0 | 4.06 | 0.81 | 48% | — | 3.91 |
| 8 | Courtois | BEL | 4.9 | 3.48 | 0.71 | 40% | — | 3.82 |
| 16 | Maignan | FRA | 5.0 | 2.91 | 0.58 | 31% | — | 2.98 |

**Why these two.** Martínez and Pickford are the two highest-projected keepers, and
crucially they're *cheap* ($5.0 / $4.8) for elite clean-sheet odds — Argentina 62%
and England 68%, the two best CS contexts among affordable keepers. Carrying both as
a rotating pair (you can field whichever has the kinder matchday) is better value
than spending up. Martínez starts on form (recent 6.05 vs 4.85).

**Who we passed and why.** Suzuki (Japan) is the value sleeper — 4.54 pts at $4.3 in
a soft group (FixEase 1.23) — a great budget enabler if we needed the $0.5–0.7m
elsewhere; he's the first man we'd drop to. **Courtois and Maignan are the headline
omissions**: both world-class, both rated *low* here purely on context — Belgium 40%
CS, and France just 31% (toughest attacking group, FixEase 0.80, so their opponents
also score). This is the model working as intended: a great keeper behind a
average-for-the-tournament defence in a hard group is a poor *fantasy* keeper.

---

## 2. Defenders — Guéhi, Hakimi, Van Dijk (start) + Romero, Bensebaïni (bench)

DEF scoring = clean sheet (+5) first, then goals/assists and set-piece threat. So the
ranking rewards **high national CS% × soft group**, with attacking fullbacks/set-piece
takers as the tie-breaker.

| # | Defender | Nat | $ | ProjPts | Val | CS% | FixEase | G | A | SetPiece |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Guéhi** | ENG | 5.1 | 5.08 | 1.00 | 68% | 1.20 | 3 | 3 | — |
| 2 | **Hakimi** | MAR | 6.0 | 5.01 | 0.83 | 73% | 1.20 | 2 | 2 | P2 FK1 C1 |
| 3 | **Van Dijk** | NED | 5.5 | 4.74 | 0.86 | 42% | 1.11 | 6 | 0 | — |
| 4 | **Romero** | ARG | 4.9 | 4.55 | 0.93 | 62% | 0.87 | 4 | 1 | — |
| 5 | **Bensebaïni** | ALG | 4.4 | 4.43 | 1.01 | 61% | 0.87 | 5 | 2 | — |
| 6 | Doué | CIV | 3.9 | 4.32 | 1.11 | 61% | 0.99 | 2 | 6 | — |
| 7 | Aguerd | MAR | 4.3 | 4.24 | 0.99 | 73% | 1.20 | 1 | 0 | — |
| 12 | Raum | GER | 4.9 | 3.98 | 0.81 | 41% | 0.80 | 3 | 7 | FK1 C1 |
| 16 | Coufal | CZE | 3.6 | 3.70 | 1.03 | 45% | 0.92 | 1 | 8 | C1 |
| 22 | Schlotterbeck | GER | 5.3 | 3.61 | 0.68 | 41% | 0.80 | 5 | 1 | — |

**Why these five.** Guéhi is the model's #1 DEF — $5.1 for 68% CS in England's soft
group, elite value (1.00). Hakimi is the one defender worth a premium: 73% CS (the
best of any nation) **plus** Morocco's primary free-kick + corner and #2 penalty
duty — he scores like a midfielder from the back. Van Dijk is on the hottest defensive
form in the pool (recent 6.73) with genuine goal threat (6 league goals). The bench
pair are deliberate value: Romero (62% CS, $4.9) and Bensebaïni — a 0.2%-owned
differential at $4.4 with 5 goals and value 1.01.

**Who we passed and why.** Doué (Ivory Coast, $3.9, **best DEF value 1.11**, 6 assists)
is the unlucky one — he's essentially our 6th defender and the swap we'd make to free
cash. Aguerd has Hakimi's elite 73% CS for less, but no attacking/set-piece upside, so
Hakimi wins on ceiling. The instructive omissions are the **Germans**: Raum (7 assists,
set-piece duty) and Schlotterbeck (5 goals, 7.7 rating) are quality, but Germany's hard
group (FixEase 0.80) and weak 41% CS sink them — exactly the same penalty that hurt
Maignan. Coufal is the cheapest enabler ($3.6, 8 assists) if we ever need to bottom out
a bench slot.

---

## 3. Midfielders — Yamal, Çalhanoğlu, Raphinha, Saibari, Bruno (all start)

This is where the points are. MID rewards goals (6 each) + assists + set-piece threat,
so we want **goal-involved players who also take penalties/free-kicks/corners**, ideally
in soft groups and at a sensible price.

| # | Midfielder | Nat | $ | ProjPts | Val | Own% | G | A | SetPiece | FixEase |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Lamine Yamal** | ESP | 10.0 | 8.49 | 0.85 | 44.8 | 16 | 11 | FK2 C1 | 1.09 |
| 2 | **Çalhanoğlu** | TUR | 7.1 | 7.50 | 1.06 | 3.1* | 9 | 4 | P1 FK1 C1 | 1.18 |
| 3 | **Raphinha** | BRA | 8.2 | 7.23 | 0.88 | 21.4 | 13 | 3 | P1 FK1 C1 | 0.92 |
| 4 | **Saibari** | MAR | 6.8 | 7.09 | 1.04 | 0.5* | 15 | 8 | — | 1.20 |
| 5 | **Bruno Fernandes** | POR | 8.5 | 7.02 | 0.83 | 48.9 | 9 | 21 | P2 FK2 C1 | 0.94 |
| 6 | Salah | EGY | 10.0 | 5.91 | 0.59 | 6.2 | 7 | 7 | P1 FK1 C1 | 1.08 |
| 8 | Olise | FRA | 9.5 | 5.37 | 0.57 | 23.4 | 15 | 19 | FK1 C1 | 0.80 |
| 11 | L. Díaz | COL | 8.1 | 5.09 | 0.63 | 18.8 | 15 | 14 | P2 | 0.85 |
| 12 | De Bruyne | BEL | 7.5 | 4.89 | 0.65 | 5.2 | 5 | 2 | P1 FK1 C1 | 1.01 |
| 17 | Bellingham | ENG | 8.3 | 4.63 | 0.56 | 9.6 | 6 | 4 | — | 1.20 |
| 23 | Pedri | ESP | 8.1 | 4.28 | 0.53 | 9.8 | 2 | 9 | FK1 | 1.09 |

**Why these five.** Yamal is the single best outfield asset and an auto-pick despite the
$10 tag. The two value engines are **Çalhanoğlu (1.06) and Saibari (1.04)** — both
sub-$7.1, both barely owned (3.1% and 0.5%), giving us elite points-per-dollar to fund
Yamal + Kane. Çalhanoğlu is Turkey's penalty + free-kick + corner taker in a soft group;
Saibari is in Morocco's *softest-group, best-defence* context (FixEase 1.20, CS 73%) with
15 goals + 8 assists. Raphinha takes everything for Brazil (P1/FK1/C1). Bruno's 21 assists
+ set-piece volume justify him even in a neutral group.

**Who we passed and why.** This is the section the optimiser is most ruthless in:

- **Salah** ($10): premium price, but Egypt's 39% CS and only-average FixEase (1.08) drop
  his value to 0.59 — you're paying striker money for midfielder output.
- **Olise** ($9.5, 15G/19A, 7.89 rating): superb *underlying* numbers — arguably the best
  in the pool — but **France's 0.80 FixEase** (hardest group) plus real rotation risk
  (start prob 0.72) cut his projection. A prime "model says no, my eyes say yes" candidate.
- **Bellingham** ($8.3): helped by England's soft group, but no set-piece duty and 0.79
  start security leave him mid-pack; poor value at the price.
- **Pedri** ($8.1, 2G/9A): elite deep playmaker, but almost no goal threat — the model
  punishes low shot/goal volume hard.

The throughline: we prioritised **set-piece takers + value in good fixtures** over
big names whose price or group drags their return.

---

## 4. Forwards — Kane (C), Malen (start) + Ueda (bench)

| # | Forward | Nat | $ | ProjPts | Val | Own% | G | g/90 | SetPiece | FixEase |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Kane (C)** | ENG | 10.5 | 9.19 | 0.88 | 37.8 | 36 | 1.36 | P1 | 1.20 |
| 2 | **Malen** | NED | 6.1 | 7.41 | 1.21 | 1.4* | 14 | 0.85 | — | 1.11 |
| 3 | Haaland | NOR | 10.5 | 7.06 | 0.67 | 33.3 | 27 | 0.82 | P1 | 0.94 |
| 4 | **Ueda** (bench) | JPN | 7.0 | 6.30 | 0.90 | 0.7* | 25 | 0.89 | P1 | 1.23 |
| 5 | Mbappé | FRA | 10.5 | 5.63 | 0.54 | 50.9 | 25 | 0.86 | P1 | 0.80 |
| 6 | Suárez | COL | 5.7 | 5.42 | 0.95 | 2.6* | 28 | 0.93 | — | 0.85 |
| 10 | Lautaro | ARG | 8.8 | 4.60 | 0.52 | 4.0* | 17 | 0.70 | P2 | 0.87 |

**Why these three.** Kane is the #1 projected player overall — 36 club goals, England's
penalty taker, in the softest group (FixEase 1.20, 68% CS context), and red-hot
(recent 9.26). He's the **captain**: doubling the highest, most-nailed projection is the
lowest-variance call available. Malen is the squad's MVP for *value* (1.21, best of any
forward) — $6.1 lets the whole expensive spine exist, and he's a 1.4%-owned differential
in form (recent 8.15). Ueda benches as a $7.0 third striker who could start most weeks
(Japan's soft group, 25 goals, penalties).

**Who we passed and why.** We could only afford one $10.5 forward alongside Yamal —
**Haaland or Kane**, and Kane wins on group/CS context + captaincy nailness. **Mbappé is
the standout omission**: 25 goals, but France's brutal group (FixEase 0.80) collapses his
value to 0.54 at $10.5 — a textbook case of the fixture model overriding raw talent (and
he's 50.9% owned, so fading him is also a differential play). Suárez ($5.7, value 0.95)
was a close call as a cheaper striker but Malen's form + FixEase edged him.

---

## 5. Why not Kimmich? (the small section)

Kimmich is **28.6% owned — a near-template pick — yet outside our top 15.** Two reasons,
one of which is a model flaw you spotted:

1. **Position source.** Our pipeline took his position from API-Football (**Midfielder**),
   but the **FIFA game lists him as a Defender** — and FIFA's position is the one that
   matters. As a "MID" in our model he competes for goal/assist points he doesn't produce
   (just **2 goals all season**, g/90 ≈ 0.06). Re-pooled correctly as a **DEF**, his clean
   sheets would be worth **+5 not +1**, and his 8 assists + nailed minutes would rank him
   far higher among defenders. *This is a genuine fix for the next model — see below.*
2. **Even so, context is against him.** Germany has the model's **hardest attacking group
   (FixEase 0.80)** and a weak **41% clean-sheet** chance, and he's only Germany's **#2**
   penalty taker. So a corrected DEF-Kimmich rises, but Germany's group caps how far.

Net: the market is paying for his price, minutes and assist floor; our model is bearish
partly for a good reason (group/role) and partly for a bad one (wrong position bucket).

---

## 6. What to push back on — levers for the next model

These are the assumptions baked in right now. Tell me which feel wrong and I'll retune:

1. **Position source — confirmed fix:** switch the fantasy position to the **FIFA Fantasy
   value** (not API-Football). This re-pools Kimmich, Hakimi, and likely other RB/DM/wing
   hybrids, and changes clean-sheet scoring. *High-impact; I'd do this first.*
2. **League-strength coefficients** (ENG 1.00 → BRA 0.78): subjective. Should Brazil's
   league be higher? Should we drop the discount for players who are nailed internationals?
3. **Fixture difficulty** is built from each nation's recent GF/GA vs its 3 *group* games
   only. Should knockout-round projections matter? Should it weight opponent quality more
   aggressively (the 0.6–1.5 cap currently compresses extremes)?
4. **Form blend** is 40% recent / 60% season, sample-weighted. Too much? Too little?
5. **Clean-sheet model** is Poisson on national GF/GA. It ignores specific opponent
   line-ups and home advantage (USA/MEX/CAN hosts).
6. **Set-piece weighting** (primary penalty ≈ 0.8 of a team's pens; small FK/corner bumps)
   — tune the magnitudes.
7. **Ownership isn't in the score yet** — only shown. We could fold the Scouting Bonus
   (+2 for <5% owned & >4 pts) into projections to actively reward differentials.
8. **Known data gaps:** no xG/xA (API-Football lacks it); a few name-match false positives
   (e.g. Carlos Vinícius inheriting Vinícius Jr's price); club clean-sheet context still
   leaks into a couple of edge cases.

Pick any of these and we'll rebuild — #1 (FIFA positions) is the obvious next step.

### Queued for the next model (confirmed)

1. **FIFA position source** — use the FIFA Fantasy game's position (not API-Football) as the
   authoritative fantasy position/scoring bucket. Fixes Kimmich (DEF, not MID) and similar
   full-back/holding hybrids; changes their clean-sheet scoring (+5 vs +1).
2. **Country form (third form component)** — currently "form" is **club only** (both season
   sXP and recent rXP). Add a per-player **international** form input: pull each shortlisted
   player's recent national-team match stats via `/fixtures/players` on national-team
   fixtures (matched by global player ID), and blend it as a third component alongside club
   season + club recent (sample-weighted, e.g. season 0.5 / club-recent 0.3 / country 0.2).
   Costs extra API calls (national fixtures + per-fixture player stats per nation). Makes the
   form picture complete — a striker hot for country but quiet at club (or vice-versa) is
   currently invisible.

(The 2026-06-05 20:20 scheduled run for the country-form addition fired but did not complete —
no code changed — so this remains pending. Run it on request.)
