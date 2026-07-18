# WC2026 Fantasy — Player Rankings: Data & Methodology (Writer Reference)

*Auto-generated from the `wc_scout` model. Every number below is computed, not hand-edited. Use it to write about player rankings, captaincy, differentials, value picks, set-piece threats and fixtures — for any player in the pool, not just the headline names.*

**Pool:** 328 probable World Cup 2026 starters who exist in the official FIFA Fantasy game, drawn from 20 leagues (ARG, AUT, BEL, BRA, CRO, ENG, ENG2, ESP, FRA, GER, GRE, ITA, MEX, MLS, NED, POR, SAU, SCO, SUI, TUR).

---

## 1. What a player's projection means

Every player carries one headline number — **xPts (projected points per match)** — the expected number of FIFA World Cup Fantasy points he earns in a single game. It is fully traceable: a rule × a rate × a probability, summed. Higher = better. It is per-match, so it is comparable across players and divisible by price.

Two players with the same xPts can tell very different stories — one might be a nailed-on penalty taker in a soft group, the other a hot-form differential nobody owns. The columns below let you find those angles.

## 2. How xPts is built (methodology, in depth)

The projection is assembled in layers:

**(a) The FIFA scoring rules.** Points are awarded as in the official game: appearance **+1**; a goal is worth **GK 9 / DEF 7 / MID 6 / FWD 5**; an assist **+3**; a clean sheet **GK/DEF +5, MID +1**; goalkeeper saves **+1 per 3**; penalty save **+3**, penalty won **+2**, penalty conceded **−1**; yellow **−1**, red **−2**; midfield tackles **+1 per 3** and chances created **+1 per 2**; forward shots on target **+1 per 2**.

**(b) Per-90 rates.** Each player's club output (goals, assists, shots, key passes, tackles, saves, penalties, cards) is converted to a per-90-minute rate, then multiplied by the relevant point value to get an *expected* contribution — so we don't wait for real events, we project them.

**(c) Playing-time probability.** Every term is scaled by the player's chance of being on the pitch (**Start%**, from his lineup ratio), and clean-sheet points are additionally gated by his chance of reaching 60 minutes.

**(d) National clean-sheet model.** Goalkeeper/defender clean-sheet points use the player's **nation's** chance of a shut-out, computed by Poisson from that nation's defensive rating against its **actual group opponents** (`P(0 conceded)=exp(−opp xG)`). A leaky nation's defenders get a low clean-sheet chance no matter how good the individual.

**(e) Fixture difficulty (FixEase).** Attacking output is scaled by how weak the group opponents' defences are: **>1.0 = soft group, <1.0 = tough group**. This is why stars in brutal groups are shaded down and players in kind groups get a lift.

**(f) Team-strength factor (TeamStr).** Attacking output is *also* scaled by the player's **own** national-team quality — a blend of **50% FIFA world-ranking strength + 50% recent goals-for rate**, normalised to a tournament average of 1.0. This applies the 'lone star in a weak side' tax: a brilliant attacker with poor team-mates creates fewer chances and is discounted; a player in a strong side is boosted.

**(g) National set-piece duty.** If a player is his country's penalty / free-kick / corner taker, he gets extra expected goal/assist value (the primary penalty taker is credited with ~80% of the team's penalties, assuming ~0.18 penalties awarded per game). This is national duty, not club — it overrides club penalty records.

**(h) Three-window form blend.** The projection blends three snapshots, sample-weighted: **club season (50%)**, **club recent form (30%, last ~40 league games)** and **country form (20%, last ~8 internationals)**. A player hot for his country but quiet at club (or vice versa) is captured here.

**(i) League-strength discount.** The blended figure is multiplied by a per-league coefficient (Premier League 1.00 down to weaker leagues ~0.60), so a goal in a weaker league isn't valued like a goal in a top one.

**(j) Price & ownership.** Pulled from the official FIFA Fantasy game. **Value = xPts ÷ price** (points per $m). **Own%** is the share of squads that have picked him; under 5% is a differential.

**Final formula:** `xPts = [0.5·season + 0.3·club-recent + 0.2·country] × league-strength`, where each form window is itself scored through layers (a)–(g).

## 3. Column glossary

- **xPts** — Projected fantasy points per match — the headline ranking number.
- **$** — FIFA Fantasy price in $m.
- **Own%** — Ownership: share of all squads picking him. `*` flags a differential (<5%).
- **Val** — Value = xPts per $m. Higher = more points for your money.
- **sXP / rXP / cXP** — The three form components before blending: club **s**eason, club **r**ecent, **c**ountry (international). `—` = no usable sample.
- **G / A** — Club goals / assists this season.
- **G/90 / A/90** — Per-90-minute goal / assist rates.
- **Start%** — Estimated chance he starts for his country (from club lineup security).
- **CS%** — His nation's clean-sheet chance vs its group opponents.
- **FixEase** — Attacking fixture ease from the group draw (>1 soft, <1 tough).
- **TeamStr** — Own national-team attacking strength (FIFA rank + recent scoring; ~1.0 = average; <1 weak, >1 strong).
- **SetPiece** — National set-piece duty: Pen/FK/Corner taker rank (1 = first choice).
- **Rtg** — Average club match rating this season (0–10).

## 4. National-team context (fixtures & strength)

Every attacking and clean-sheet number above is shaped by these nation-level inputs. Use this to write fixture/group angles.

| Nation | FIFA pts | Group opponents | GF/g | GA/g | TeamStr | CS% | xGA | FixEase |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Belgium | 1736 | Egypt, Iran, New Zealand | 3.07 | 0.93 | 1.25 | 45% | 0.80 | 1.03 |
| Spain | 1867 | Cape Verde, Saudi Arabia, Uruguay | 2.86 | 1.14 | 1.25 | 46% | 0.80 | 1.04 |
| Portugal | 1772 | Colombia, DR Congo, Uzbekistan | 2.60 | 1.07 | 1.25 | 39% | 0.94 | 0.87 |
| Norway | 1532 | France, Iraq, Senegal | 3.27 | 0.67 | 1.25 | 51% | 0.69 | 0.94 |
| Netherlands | 1754 | Japan, Sweden, Tunisia | 2.67 | 0.87 | 1.25 | 45% | 0.81 | 1.22 |
| England | 1820 | Croatia, Ghana, Panama | 2.40 | 0.33 | 1.22 | 72% | 0.33 | 1.22 |
| Senegal | 1652 | France, Iraq, Norway | 2.60 | 0.87 | 1.22 | 40% | 1.00 | 0.87 |
| Argentina | 1870 | Algeria, Austria, Jordan | 2.23 | 0.31 | 1.19 | 73% | 0.32 | 0.92 |
| France | 1862 | Iraq, Norway, Senegal | 2.20 | 1.07 | 1.18 | 31% | 1.31 | 0.80 |
| Germany | 1709 | Curacao, Ecuador, Ivory Coast | 2.33 | 1.13 | 1.16 | 38% | 1.00 | 0.75 |
| Switzerland | 1648 | Bosnia & Herzegovina, Canada, Qatar | 2.40 | 1.00 | 1.16 | 53% | 0.67 | 1.03 |
| Croatia | 1716 | England, Ghana, Panama | 2.27 | 0.93 | 1.15 | 39% | 0.95 | 1.01 |
| Morocco | 1710 | Brazil, Haiti, Scotland | 2.13 | 0.40 | 1.11 | 68% | 0.39 | 1.25 |
| Turkey | 1560 | Australia, Paraguay, USA | 2.27 | 1.27 | 1.10 | 34% | 1.08 | 1.22 |
| Brazil | 1758 | Haiti, Morocco, Scotland | 2.00 | 1.13 | 1.09 | 33% | 1.12 | 0.99 |
| Austria | 1576 | Algeria, Argentina, Jordan | 2.20 | 0.60 | 1.08 | 54% | 0.63 | 0.81 |
| Colombia | 1700 | DR Congo, Portugal, Uzbekistan | 1.93 | 1.07 | 1.05 | 36% | 1.07 | 0.87 |
| Algeria | 1507 | Argentina, Austria, Jordan | 2.07 | 0.47 | 1.03 | 61% | 0.50 | 0.86 |
| Japan | 1652 | Netherlands, Sweden, Tunisia | 1.87 | 0.53 | 1.02 | 57% | 0.57 | 1.34 |
| Sweden | 1530 | Japan, Netherlands, Tunisia | 2.00 | 1.67 | 1.02 | 19% | 1.75 | 0.94 |
| Czechia | 1491 | Mexico, South Africa, South Korea | 2.00 | 1.00 | 1.00 | 44% | 0.83 | 0.94 |
| Ivory Coast | 1492 | Curacao, Ecuador, Germany | 2.00 | 0.53 | 1.00 | 61% | 0.50 | 0.96 |
| Iran | 1638 | Belgium, Egypt, New Zealand | 1.79 | 0.71 | 0.99 | 48% | 0.78 | 1.10 |
| Scotland | 1497 | Brazil, Haiti, Morocco | 1.93 | 1.13 | 0.99 | 32% | 1.14 | 0.99 |
| USA | 1648 | Australia, Paraguay, Turkey | 1.73 | 1.53 | 0.98 | 24% | 1.45 | 1.13 |
| Curacao | 1377 | Ecuador, Germany, Ivory Coast | 2.00 | 1.20 | 0.97 | 34% | 1.13 | 0.73 |
| South Korea | 1572 | Czechia, Mexico, South Africa | 1.73 | 0.87 | 0.96 | 47% | 0.76 | 0.99 |
| Bosnia & Herzegovina | — | Canada, Qatar, Switzerland | 1.73 | 0.93 | 0.96 | 51% | 0.74 | 1.05 |
| Australia | 1503 | Paraguay, Turkey, USA | 1.67 | 0.93 | 0.92 | 42% | 0.89 | 1.34 |
| Cape Verde | 1391 | Saudi Arabia, Spain, Uruguay | 1.80 | 0.80 | 0.92 | 52% | 0.71 | 1.16 |
| Panama | 1452 | Croatia, England, Ghana | 1.67 | 1.27 | 0.90 | 25% | 1.42 | 0.89 |
| Ghana | 1453 | Croatia, England, Panama | 1.67 | 1.27 | 0.90 | 25% | 1.42 | 0.89 |
| Uzbekistan | 1437 | Colombia, DR Congo, Portugal | 1.67 | 0.73 | 0.90 | 47% | 0.77 | 0.99 |
| New Zealand | 1318 | Belgium, Egypt, Iran | 1.80 | 1.33 | 0.90 | 27% | 1.45 | 0.89 |
| Mexico | 1650 | Czechia, South Africa, South Korea | 1.40 | 0.80 | 0.90 | 48% | 0.75 | 1.01 |
| Canada | 1530 | Bosnia & Herzegovina, Qatar, Switzerland | 1.47 | 0.40 | 0.88 | 72% | 0.33 | 1.24 |
| Jordan | 1389 | Algeria, Argentina, Austria | 1.60 | 1.53 | 0.87 | 17% | 1.76 | 0.60 |
| South Africa | 1431 | Czechia, Mexico, South Korea | 1.53 | 1.00 | 0.86 | 41% | 0.91 | 0.94 |
| Tunisia | 1499 | Japan, Netherlands, Sweden | 1.40 | 1.27 | 0.85 | 24% | 1.47 | 1.08 |
| Paraguay | 1483 | Australia, Turkey, USA | 1.40 | 1.00 | 0.84 | 37% | 1.00 | 1.32 |
| DR Congo | 1462 | Colombia, Portugal, Uzbekistan | 1.40 | 0.67 | 0.84 | 48% | 0.73 | 1.01 |
| Haiti | 1320 | Brazil, Morocco, Scotland | 1.53 | 1.27 | 0.83 | 26% | 1.36 | 0.94 |
| Egypt | 1518 | Belgium, Iran, New Zealand | 1.27 | 0.87 | 0.82 | 37% | 1.02 | 1.05 |
| Uruguay | 1675 | Cape Verde, Saudi Arabia, Spain | 0.93 | 0.87 | 0.78 | 43% | 0.90 | 1.14 |
| Saudi Arabia | 1418 | Cape Verde, Spain, Uruguay | 1.21 | 1.29 | 0.77 | 32% | 1.27 | 0.99 |
| Ecuador | 1571 | Curacao, Germany, Ivory Coast | 1.00 | 0.40 | 0.77 | 64% | 0.45 | 1.01 |
| Iraq | 1404 | France, Norway, Senegal | 1.07 | 0.73 | 0.75 | 36% | 1.05 | 0.92 |
| Qatar | 1438 | Bosnia & Herzegovina, Canada, Switzerland | 0.58 | 1.58 | 0.75 | 22% | 1.57 | 0.82 |

## 5. Position rankings — every player

Full ranked lists (not just the top 20). Each row has everything needed to write about that player. `*` after Own% marks a differential (<5%).

### Goalkeepers — 25 ranked

| # | Player | Club | Nation | $ | Own% | Val | xPts | sXP | rXP | cXP | G | A | G/90 | A/90 | Start% | CS% | FixEase | TeamStr | SetPiece | Rtg |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | E. Martínez | Aston Villa | Argentina | 5.0 | 22.1 | 1.17 | **5.86** | 5.79 | 6.81 | 5.18 | 0 | 1 | 0.00 | 0.03 | 97% | 73% | 0.92 | 1.19 | P2 | 7.0 |
| 2 | J. Pickford | Everton | England | 4.8 | 14.9 | 1.07 | **5.13** | 5.18 | 5.03 | 5.03 | 0 | 0 | 0.00 | 0.00 | 97% | 72% | 1.22 | 1.22 | — | 7.0 |
| 3 | Z. Suzuki | Parma | Japan | 4.3 | 1.8* | 1.08 | **4.63** | 4.84 | 5.08 | 4.65 | 0 | 0 | 0.00 | 0.00 | 97% | 57% | 1.34 | 1.02 | — | 7.1 |
| 4 | Unai Simón | Athletic Club | Spain | 5.0 | 6.2 | 0.80 | **4.02** | 4.16 | 3.80 | 4.77 | 0 | 0 | 0.00 | 0.00 | 97% | 46% | 1.04 | 1.25 | — | 6.9 |
| 5 | G. Kobel | Borussia Dortmund | Switzerland | 4.7 | 6.5 | 0.84 | **3.96** | 4.25 | 4.21 | 4.13 | 0 | 0 | 0.00 | 0.00 | 97% | 53% | 1.03 | 1.16 | — | 7.2 |
| 6 | B. Verbruggen | Brighton | Netherlands | 4.7 | 3.5* | 0.84 | **3.93** | 3.98 | 3.99 | 3.42 | 0 | 0 | 0.00 | 0.00 | 97% | 45% | 1.22 | 1.25 | — | 7.0 |
| 7 | M. Ryan | Levante | Australia | 4.1 | 0.7* | 0.92 | **3.79** | 4.04 | 3.67 | 3.59 | 0 | 0 | 0.00 | 0.00 | 97% | 42% | 1.34 | 0.92 | — | 7.2 |
| 8 | M. Crépeau | Portland Timbers | Canada | 4.0 | 2.0* | 0.93 | **3.73** | 5.51 | — | 5.06 | 0 | 0 | 0.00 | 0.00 | 97% | 72% | 1.24 | 0.88 | — | 7.0 |
| 9 | T. Courtois | Real Madrid | Belgium | 4.9 | 12.5 | 0.76 | **3.70** | 3.76 | 4.09 | 3.43 | 0 | 0 | 0.00 | 0.00 | 97% | 45% | 1.03 | 1.25 | — | 6.9 |
| 10 | H. Galíndez | Huracan | Ecuador | 4.2 | 3.4* | 0.83 | **3.50** | 4.76 | — | 5.55 | 0 | 0 | 0.00 | 0.00 | 97% | 64% | 1.01 | 0.77 | — | 7.0 |
| 11 | Alisson Becker | Liverpool | Brazil | 5.0 | 5.4 | 0.63 | **3.17** | 3.05 | — | 5.00 | 0 | 0 | 0.00 | 0.00 | 97% | 33% | 0.99 | 1.09 | — | 6.8 |
| 12 | N. Vasilj | FC St. Pauli | Bosnia and Herzegovina | 4.0 | 0.7* | 0.78 | **3.10** | 3.38 | 3.39 | 2.82 | 0 | 0 | 0.00 | 0.00 | 97% | 28% | 1.00 | 1.00 | — | 7.1 |
| 13 | M. Neuer | Bayern München | Germany | 5.0 | 12.7 | 0.61 | **3.07** | 3.27 | — | — | 0 | 0 | 0.00 | 0.00 | 97% | 38% | 0.75 | 1.16 | — | 6.9 |
| 14 | L. Horníček | SC Braga | Czechia | 3.8 | 0.1* | 0.81 | **3.06** | 3.84 | 3.47 | — | 0 | 0 | 0.00 | 0.00 | 97% | 44% | 0.94 | 1.00 | — | 7.0 |
| 15 | S. Rochet | Internacional | Uruguay | 4.1 | 4.2* | 0.72 | **2.95** | 3.98 | 3.79 | 2.99 | 0 | 0 | 0.00 | 0.00 | 97% | 43% | 1.14 | 0.78 | — | 6.9 |
| 16 | M. Maignan | AC Milan | France | 5.0 | 9.8 | 0.58 | **2.92** | 3.16 | 3.04 | 2.48 | 0 | 0 | 0.00 | 0.00 | 97% | 31% | 0.80 | 1.18 | — | 7.2 |
| 17 | Diogo Costa | FC Porto | Portugal | 4.9 | 9.8 | 0.56 | **2.74** | 3.43 | 3.18 | 3.22 | 0 | 0 | 0.00 | 0.00 | 97% | 39% | 0.87 | 1.25 | — | 7.1 |
| 18 | A. Schlager | Red Bull Salzburg | Austria | 4.6 | 0.4* | 0.59 | **2.70** | 4.19 | 4.27 | 4.14 | 0 | 0 | 0.00 | 0.00 | 97% | 54% | 0.81 | 1.08 | — | 7.1 |
| 19 | O. Gill | San Lorenzo | Paraguay | 3.5 | 0.4* | 0.68 | **2.37** | 3.33 | — | 3.05 | 0 | 0 | 0.00 | 0.00 | 97% | 37% | 1.32 | 0.84 | — | 6.9 |
| 20 | É. Mendy | Al-Ahli Jeddah | Senegal | 4.5 | 1.1* | 0.52 | **2.34** | 3.43 | 3.67 | 3.95 | 0 | 0 | 0.00 | 0.00 | 97% | 40% | 0.87 | 1.22 | — | 7.0 |
| 21 | M. Crocombe | Millwall | New Zealand | 3.9 | 0.1* | 0.58 | **2.27** | 2.92 | — | 3.42 | 0 | 0 | 0.00 | 0.00 | 97% | 27% | 0.89 | 0.90 | — | 7.0 |
| 22 | D. Livaković | Dinamo Zagreb | Croatia | 4.5 | 1.5* | 0.46 | **2.05** | 3.32 | 3.54 | 3.48 | 0 | 0 | 0.00 | 0.00 | 97% | 39% | 1.01 | 1.15 | — | 7.0 |
| 23 | Nawaf Al Aqidi | Al-Nassr | Saudi Arabia | 4.0 | 0.2* | 0.50 | **2.00** | 3.02 | — | 3.47 | 0 | 1 | 0.00 | 0.09 | 97% | 32% | 0.99 | 0.77 | — | 6.9 |
| 24 | O. Mosquera | Al-Fayha | Panama | 3.9 | 0.1* | 0.48 | **1.88** | 2.90 | 3.36 | 2.16 | 0 | 0 | 0.00 | 0.00 | 97% | 25% | 0.89 | 0.90 | — | 7.0 |
| 25 | M. Freese | New York City FC | USA | 4.2 | 0.5* | 0.40 | **1.66** | 2.65 | 2.19 | 2.03 | 0 | 0 | 0.00 | 0.00 | 97% | 24% | 1.13 | 0.98 | — | 7.0 |

### Defenders — 122 ranked

| # | Player | Club | Nation | $ | Own% | Val | xPts | sXP | rXP | cXP | G | A | G/90 | A/90 | Start% | CS% | FixEase | TeamStr | SetPiece | Rtg |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | V. van Dijk | Liverpool | Netherlands | 5.5 | 20.2 | 1.12 | **6.15** | 4.61 | 8.29 | 11.14 | 6 | 0 | 0.16 | 0.00 | 97% | 45% | 1.22 | 1.25 | — | 7.3 |
| 2 | R. Dōan | Eintracht Frankfurt | Japan | 5.1 | 1.0* | 1.12 | **5.71** | 5.87 | 6.92 | — | 5 | 5 | 0.19 | 0.19 | 90% | 57% | 1.34 | 1.02 | P2 C3 | 6.8 |
| 3 | M. Guéhi | Manchester City | England | 5.1 | 8.0 | 1.07 | **5.46** | 5.52 | 5.47 | 4.39 | 3 | 3 | 0.09 | 0.09 | 97% | 72% | 1.22 | 1.22 | — | 7.4 |
| 4 | C. Romero | Tottenham | Argentina | 4.9 | 4.9* | 1.04 | **5.09** | 5.36 | — | 4.41 | 4 | 1 | 0.19 | 0.05 | 96% | 73% | 0.92 | 1.19 | — | 7.1 |
| 5 | A. Hakimi | Paris Saint Germain | Morocco | 6.0 | 21.6 | 0.82 | **4.94** | 5.69 | — | 4.38 | 2 | 2 | 0.13 | 0.13 | 83% | 68% | 1.25 | 1.11 | P2 FK1 C1 | 6.8 |
| 6 | E. Konsa | Aston Villa | England | 4.8 | 1.1* | 0.90 | **4.34** | 4.33 | 4.39 | 4.39 | 0 | 0 | 0.00 | 0.00 | 97% | 72% | 1.22 | 1.22 | — | 7.0 |
| 7 | J. Ryerson | Borussia Dortmund | Norway | 4.2 | 7.9 | 1.02 | **4.28** | 4.40 | 5.21 | 2.95 | 0 | 15 | 0.00 | 0.59 | 84% | 51% | 0.94 | 1.25 | C2 | 7.1 |
| 8 | G. Doué | Strasbourg | Ivory Coast | 3.9 | 0.9* | 1.08 | **4.22** | 5.03 | 3.87 | 3.87 | 2 | 6 | 0.09 | 0.26 | 96% | 61% | 0.96 | 1.00 | — | 6.9 |
| 9 | L. Krejčí | Wolves | Czechia | 4.4 | 0.5* | 0.95 | **4.17** | 3.45 | — | 5.98 | 2 | 1 | 0.08 | 0.04 | 96% | 44% | 0.94 | 1.00 | — | 6.7 |
| 10 | R. Bensebaïni | Borussia Dortmund | Algeria | 4.4 | 0.2* | 0.95 | **4.16** | 4.73 | — | 2.11 | 5 | 2 | 0.29 | 0.12 | 71% | 61% | 0.86 | 1.03 | — | 7.4 |
| 11 | N. Aguerd | Marseille | Morocco | 4.3 | 0.2* | 0.94 | **4.05** | 4.55 | — | 4.20 | 1 | 0 | 0.06 | 0.00 | 97% | 68% | 1.25 | 1.11 | — | 7.2 |
| 12 | E. Ndicka | AS Roma | Ivory Coast | 4.4 | 0.3* | 0.92 | **4.04** | 4.38 | 3.88 | 3.88 | 3 | 0 | 0.10 | 0.00 | 97% | 61% | 0.96 | 1.00 | — | 7.0 |
| 13 | R. James | Chelsea | England | 5.2 | 4.2* | 0.76 | **3.96** | 4.03 | — | 2.94 | 2 | 4 | 0.09 | 0.18 | 69% | 72% | 1.22 | 1.22 | FK3 | 7.2 |
| 14 | D. Raum | RB Leipzig | Germany | 4.9 | 3.7* | 0.80 | **3.93** | 4.18 | — | — | 3 | 7 | 0.11 | 0.25 | 97% | 38% | 0.75 | 1.16 | FK1 C1 | 7.4 |
| 15 | V. Coufal | 1899 Hoffenheim | Czechia | 3.6 | 3.5* | 1.08 | **3.90** | 3.93 | 3.91 | 4.95 | 1 | 8 | 0.03 | 0.24 | 97% | 44% | 0.94 | 1.00 | C1 | 7.2 |
| 16 | D. Dumfries | Inter | Netherlands | 5.7 | 15.7 | 0.68 | **3.86** | 3.95 | — | 4.90 | 3 | 1 | 0.20 | 0.07 | 75% | 45% | 1.22 | 1.25 | — | 6.6 |
| 17 | N. Otamendi | Benfica | Argentina | 4.4 | 2.1* | 0.84 | **3.71** | 4.76 | 3.68 | 4.42 | 2 | 0 | 0.07 | 0.00 | 97% | 73% | 0.92 | 1.19 | — | 7.4 |
| 18 | Marc Cucurella | Chelsea | Spain | 5.1 | 23.6 | 0.72 | **3.66** | 3.45 | 3.44 | 5.86 | 1 | 4 | 0.03 | 0.13 | 91% | 46% | 1.04 | 1.25 | — | 6.7 |
| 19 | J. Gvardiol | Manchester City | Croatia | 5.0 | 5.0 | 0.73 | **3.66** | 3.80 | — | 2.64 | 2 | 2 | 0.13 | 0.13 | 89% | 39% | 1.01 | 1.15 | — | 7.0 |
| 20 | N. Elvedi | Borussia Mönchengladbach | Switzerland | 4.3 | 2.6* | 0.84 | **3.60** | 3.61 | 4.74 | 3.49 | 0 | 2 | 0.00 | 0.06 | 97% | 53% | 1.03 | 1.16 | — | 7.0 |
| 21 | J. Vásquez | Genoa | Mexico | 4.7 | 2.0* | 0.76 | **3.59** | 3.35 | 6.31 | 3.23 | 1 | 0 | 0.03 | 0.00 | 97% | 48% | 1.01 | 0.90 | — | 6.8 |
| 22 | P. Hincapié | Arsenal | Ecuador | 4.7 | 3.2* | 0.75 | **3.53** | 3.57 | — | 3.24 | 1 | 2 | 0.05 | 0.10 | 80% | 64% | 1.01 | 0.77 | — | 6.9 |
| 23 | D. Muñoz | Crystal Palace | Colombia | 4.6 | 8.8 | 0.75 | **3.45** | 3.58 | 3.28 | 2.60 | 4 | 3 | 0.15 | 0.11 | 97% | 36% | 0.87 | 1.05 | — | 6.9 |
| 24 | P. Mwene | FSV Mainz 05 | Austria | 3.9 | 0.0* | 0.88 | **3.45** | 3.35 | 4.53 | 2.94 | 1 | 2 | 0.04 | 0.09 | 83% | 54% | 0.81 | 1.08 | — | 6.8 |
| 25 | M. Akanji | Inter | Switzerland | 5.0 | 4.9* | 0.69 | **3.44** | 3.81 | — | 3.15 | 2 | 0 | 0.06 | 0.00 | 94% | 53% | 1.03 | 1.16 | — | 7.2 |
| 26 | J. Kimmich | Bayern München | Germany | 5.5 | 30.3 | 0.63 | **3.44** | 3.47 | 3.78 | 5.28 | 2 | 8 | 0.08 | 0.32 | 83% | 38% | 0.75 | 1.16 | P2 C3 | 7.7 |
| 27 | N. Schlotterbeck | Borussia Dortmund | Germany | 5.3 | 3.8* | 0.64 | **3.40** | 3.69 | 4.02 | 1.81 | 5 | 1 | 0.18 | 0.04 | 97% | 38% | 0.75 | 1.16 | — | 7.7 |
| 28 | W. Pacho | Paris Saint Germain | Ecuador | 4.4 | 4.5* | 0.77 | **3.37** | 3.83 | 3.83 | 2.96 | 0 | 0 | 0.00 | 0.00 | 91% | 64% | 1.01 | 0.77 | — | 7.0 |
| 29 | Wesley | AS Roma | Brazil | 4.5 | 1.7* | 0.74 | **3.34** | 3.40 | 4.21 | 2.35 | 5 | 0 | 0.18 | 0.00 | 93% | 33% | 0.99 | 1.09 | — | 7.0 |
| 30 | R. Belghali | Hellas Verona | Algeria | 3.5 | 1.5* | 0.95 | **3.31** | 3.64 | 3.39 | 2.43 | 2 | 0 | 0.09 | 0.00 | 85% | 61% | 0.86 | 1.03 | — | 6.7 |
| 31 | Y. Mina | Cagliari | Colombia | 4.2 | 0.3* | 0.79 | **3.30** | 2.91 | 4.67 | 4.95 | 2 | 0 | 0.08 | 0.00 | 97% | 36% | 0.87 | 1.05 | — | 7.0 |
| 32 | Pau Cubarsí Paredes | Barcelona | Spain | 5.0 | 5.4 | 0.65 | **3.23** | 3.35 | — | 3.16 | 1 | 0 | 0.03 | 0.00 | 97% | 46% | 1.04 | 1.25 | — | 7.2 |
| 33 | João Cancelo | Barcelona | Portugal | 5.3 | 7.4 | 0.61 | **3.23** | 3.23 | 3.74 | — | 2 | 2 | 0.19 | 0.19 | 69% | 39% | 0.87 | 1.25 | — | 7.2 |
| 34 | Gonçalo Inácio | Sporting CP | Portugal | 4.6 | 1.4* | 0.70 | **3.23** | 3.53 | 5.37 | — | 2 | 3 | 0.07 | 0.11 | 97% | 39% | 0.87 | 1.25 | — | 7.6 |
| 35 | S. Widmer | FSV Mainz 05 | Switzerland | 4.2 | 1.2* | 0.76 | **3.21** | 3.37 | 3.86 | 3.22 | 2 | 1 | 0.10 | 0.05 | 82% | 53% | 1.03 | 1.16 | — | 6.8 |
| 36 | Rúben Dias | Manchester City | Portugal | 5.0 | 5.6 | 0.62 | **3.11** | 3.20 | — | 2.89 | 2 | 0 | 0.08 | 0.00 | 92% | 39% | 0.87 | 1.25 | — | 7.2 |
| 37 | R. Hranáč | 1899 Hoffenheim | Czechia | 3.9 | 0.0* | 0.79 | **3.10** | 2.92 | — | 4.23 | 1 | 0 | 0.04 | 0.00 | 90% | 44% | 0.94 | 1.00 | — | 6.7 |
| 38 | A. Freeman | Orlando City SC | USA | 4.0 | 0.4* | 0.77 | **3.06** | 3.27 | 3.10 | 15.67 | 6 | 3 | 0.21 | 0.11 | 90% | 24% | 1.13 | 0.98 | — | 7.3 |
| 39 | A. Theate | Eintracht Frankfurt | Belgium | 4.5 | 0.3* | 0.68 | **3.05** | 3.24 | — | — | 1 | 0 | 0.04 | 0.00 | 97% | 45% | 1.03 | 1.25 | — | 6.8 |
| 40 | G. Konan | GIL Vicente | Ivory Coast | 4.0 | 0.4* | 0.76 | **3.04** | 3.65 | 3.88 | — | 0 | 0 | 0.00 | 0.00 | 97% | 61% | 0.96 | 1.00 | — | 6.7 |
| 41 | Nuno Mendes | Paris Saint Germain | Portugal | 5.8 | 43.1 | 0.52 | **3.02** | 3.81 | — | 2.21 | 4 | 5 | 0.29 | 0.36 | 65% | 39% | 0.87 | 1.25 | C3 | 7.3 |
| 42 | Aymeric Laporte | Athletic Club | Spain | 5.5 | 4.9* | 0.54 | **2.98** | 3.23 | 2.38 | 3.15 | 0 | 1 | 0.00 | 0.04 | 96% | 46% | 1.04 | 1.25 | — | 6.8 |
| 43 | J. Ordoñez | Club Brugge KV | Ecuador | 3.9 | 0.8* | 0.76 | **2.98** | 4.07 | 3.81 | 3.81 | 3 | 0 | 0.10 | 0.00 | 91% | 64% | 1.01 | 0.77 | — | 7.0 |
| 44 | Gabriel Magalhães | Arsenal | Brazil | 5.5 | 23.1 | 0.53 | **2.93** | 3.33 | 2.36 | 1.43 | 3 | 4 | 0.10 | 0.13 | 94% | 33% | 0.99 | 1.09 | — | 7.4 |
| 45 | R. Laryea | Toronto FC | Canada | 3.9 | 0.1* | 0.75 | **2.92** | 4.30 | — | — | 1 | 1 | 0.07 | 0.07 | 82% | 72% | 1.24 | 0.88 | — | 6.8 |
| 46 | Z. Çelik | AS Roma | Turkey | 4.3 | 0.1* | 0.67 | **2.88** | 2.90 | 2.48 | 3.88 | 1 | 2 | 0.03 | 0.07 | 94% | 34% | 1.22 | 1.10 | — | 6.8 |
| 47 | O. Alderete | Sunderland | Paraguay | 4.1 | 0.4* | 0.69 | **2.84** | 2.88 | 2.72 | 2.72 | 1 | 1 | 0.03 | 0.03 | 97% | 37% | 1.32 | 0.84 | — | 6.8 |
| 48 | N. Tagliafico | Lyon | Argentina | 4.3 | 1.1* | 0.66 | **2.84** | 3.03 | — | 3.57 | 0 | 3 | 0.00 | 0.20 | 70% | 73% | 0.92 | 1.19 | — | 6.7 |
| 49 | A. Circati | Parma | Australia | 3.9 | 0.1* | 0.73 | **2.83** | 3.00 | 2.95 | 2.95 | 1 | 0 | 0.03 | 0.00 | 97% | 42% | 1.34 | 0.92 | — | 7.0 |
| 50 | T. Heggem | Bologna | Norway | 3.7 | 0.2* | 0.76 | **2.82** | 2.97 | — | — | 0 | 0 | 0.00 | 0.00 | 85% | 51% | 0.94 | 1.25 | — | 6.7 |
| 51 | J. Italiano | Grazer AK | Australia | 4.2 | 0.1* | 0.67 | **2.82** | 4.45 | 4.65 | 2.95 | 4 | 0 | 0.17 | 0.00 | 97% | 42% | 1.34 | 0.92 | — | 7.1 |
| 52 | J. Stanišić | Bayern München | Croatia | 4.3 | 0.5* | 0.65 | **2.81** | 3.08 | 2.10 | 3.51 | 2 | 3 | 0.10 | 0.15 | 73% | 39% | 1.01 | 1.15 | — | 6.9 |
| 53 | G. Gómez | Palmeiras | Paraguay | 4.6 | 0.3* | 0.60 | **2.78** | 3.66 | 3.25 | 3.35 | 2 | 1 | 0.08 | 0.04 | 96% | 37% | 1.32 | 0.84 | FK1 C1 | 7.2 |
| 54 | Marcos Llorente | Atletico Madrid | Spain | 5.5 | 5.1 | 0.50 | **2.73** | 3.15 | 1.65 | 2.84 | 0 | 4 | 0.00 | 0.17 | 86% | 46% | 1.04 | 1.25 | — | 6.9 |
| 55 | R. Rodríguez | Real Betis | Switzerland | 4.5 | 1.8* | 0.60 | **2.69** | 2.82 | — | 2.66 | 0 | 1 | 0.00 | 0.06 | 78% | 53% | 1.03 | 1.16 | — | 6.7 |
| 56 | K. Itakura | Ajax | Japan | 4.5 | 0.2* | 0.59 | **2.65** | 3.58 | 2.83 | 2.70 | 1 | 0 | 0.07 | 0.00 | 84% | 57% | 1.34 | 1.02 | — | 7.0 |
| 57 | J. Gallardo | Toluca | Mexico | 4.7 | 0.5* | 0.56 | **2.64** | 3.88 | — | 2.93 | 5 | 5 | 0.17 | 0.17 | 87% | 48% | 1.01 | 0.90 | — | 6.9 |
| 58 | Lee Tae-Seok | Austria Vienna | South Korea | 3.7 | 0.0* | 0.71 | **2.62** | 4.06 | 3.63 | 4.91 | 3 | 4 | 0.10 | 0.14 | 97% | 47% | 0.99 | 0.96 | — | 7.0 |
| 59 | P. Lienhart | SC Freiburg | Austria | 4.3 | 0.2* | 0.60 | **2.58** | 2.44 | 4.11 | 2.33 | 1 | 0 | 0.07 | 0.00 | 70% | 54% | 0.81 | 1.08 | — | 7.0 |
| 60 | M. Niakhaté | Lyon | Senegal | 4.3 | 0.1* | 0.60 | **2.58** | 2.88 | 2.81 | — | 0 | 2 | 0.00 | 0.07 | 94% | 40% | 0.87 | 1.22 | — | 7.2 |
| 61 | R. Aït-Nouri | Manchester City | Algeria | 4.9 | 1.2* | 0.52 | **2.56** | 2.58 | — | 2.37 | 0 | 2 | 0.00 | 0.18 | 71% | 61% | 0.86 | 1.03 | — | 6.9 |
| 62 | M. Demiral | Al-Ahli Jeddah | Turkey | 4.0 | 0.7* | 0.64 | **2.56** | 3.35 | 2.52 | 6.27 | 2 | 0 | 0.12 | 0.00 | 97% | 34% | 1.22 | 1.10 | — | 7.0 |
| 63 | Z. Debast | Sporting CP | Belgium | 4.3 | 0.2* | 0.59 | **2.53** | 2.49 | 3.09 | 9.56 | 0 | 2 | 0.00 | 0.15 | 71% | 45% | 1.03 | 1.25 | — | 7.1 |
| 64 | J. Alonso | Atletico-MG | Paraguay | 4.1 | 0.1* | 0.61 | **2.51** | 2.80 | 4.67 | 2.72 | 1 | 1 | 0.03 | 0.03 | 97% | 37% | 1.32 | 0.84 | — | 7.0 |
| 65 | S. Taniguchi | St. Truiden | Japan | 3.9 | 0.0* | 0.64 | **2.51** | 3.46 | 2.95 | 3.24 | 1 | 1 | 0.03 | 0.03 | 84% | 57% | 1.34 | 1.02 | — | 7.1 |
| 66 | D. Ćaleta-Car | Real Sociedad | Croatia | 4.0 | 0.4* | 0.62 | **2.50** | 2.64 | 2.19 | 2.64 | 1 | 0 | 0.04 | 0.00 | 89% | 39% | 1.01 | 1.15 | — | 6.8 |
| 67 | M. De Cuyper | Brighton | Belgium | 4.7 | 4.5* | 0.51 | **2.41** | 2.33 | 3.08 | 1.39 | 2 | 3 | 0.12 | 0.19 | 57% | 45% | 1.03 | 1.25 | C3 | 6.9 |
| 68 | J. Giménez | Atletico Madrid | Uruguay | 4.4 | 1.8* | 0.53 | **2.35** | 2.61 | — | 1.93 | 0 | 1 | 0.00 | 0.08 | 81% | 43% | 1.14 | 0.78 | — | 7.0 |
| 69 | A. Robinson | Fulham | USA | 5.0 | 3.1* | 0.47 | **2.33** | 1.45 | 2.44 | 4.98 | 1 | 0 | 0.06 | 0.00 | 77% | 24% | 1.13 | 0.98 | C3 | 6.8 |
| 70 | J. Mojica | Mallorca | Colombia | 3.9 | 4.0* | 0.60 | **2.33** | 2.41 | — | 2.33 | 0 | 4 | 0.00 | 0.13 | 86% | 36% | 0.87 | 1.05 | — | 6.7 |
| 71 | N. Molina | Atletico Madrid | Argentina | 4.4 | 3.7* | 0.52 | **2.30** | 2.34 | — | 2.53 | 2 | 2 | 0.14 | 0.14 | 50% | 73% | 0.92 | 1.19 | — | 6.8 |
| 72 | O. Kabak | 1899 Hoffenheim | Turkey | 4.0 | 0.4* | 0.57 | **2.29** | 3.02 | 1.47 | 1.83 | 4 | 0 | 0.20 | 0.00 | 72% | 34% | 1.22 | 1.10 | — | 6.9 |
| 73 | J. Sánchez | Cruz Azul | Mexico | 4.0 | 0.8* | 0.56 | **2.24** | 2.87 | — | 4.01 | 0 | 1 | 0.00 | 0.06 | 82% | 48% | 1.01 | 0.90 | — | 6.6 |
| 74 | A. Khusanov | Manchester City | Uzbekistan | 4.3 | 0.9* | 0.51 | **2.18** | 2.15 | 2.24 | 2.24 | 0 | 0 | 0.00 | 0.00 | 71% | 47% | 0.99 | 0.90 | — | 6.9 |
| 75 | W. Saliba | Arsenal | France | 5.3 | 15.4 | 0.41 | **2.18** | 2.30 | 1.83 | 2.15 | 1 | 0 | 0.03 | 0.00 | 97% | 31% | 0.80 | 1.18 | — | 7.0 |
| 76 | T. Muharemović | Sassuolo | Bosnia and Herzegovina | 3.9 | 0.3* | 0.54 | **2.09** | 2.41 | 1.69 | 2.01 | 2 | 2 | 0.06 | 0.06 | 97% | 28% | 1.00 | 1.00 | — | 6.9 |
| 77 | A. Abdi | Nice | Tunisia | 4.1 | 0.1* | 0.50 | **2.07** | 2.01 | 3.06 | 2.60 | 3 | 0 | 0.22 | 0.00 | 56% | 24% | 1.08 | 0.85 | P1 FK2 C2 | 6.6 |
| 78 | A. Salah-Eddine | PSV Eindhoven | Morocco | 3.9 | 0.0* | 0.53 | **2.07** | 2.59 | — | — | 0 | 0 | 0.00 | 0.00 | 71% | 68% | 1.25 | 1.11 | — | 6.7 |
| 79 | D. Upamecano | Bayern München | France | 5.3 | 4.6* | 0.39 | **2.05** | 2.20 | — | 1.96 | 1 | 1 | 0.05 | 0.05 | 88% | 31% | 0.80 | 1.18 | — | 7.2 |
| 80 | S. Floranus | PEC Zwolle | Curacao | 3.6 | 0.0* | 0.57 | **2.04** | 2.68 | 2.15 | 2.48 | 1 | 3 | 0.03 | 0.10 | 97% | 34% | 0.73 | 0.97 | — | 6.4 |
| 81 | T. Castagne | Fulham | Belgium | 4.7 | 0.4* | 0.42 | **1.98** | 1.86 | 2.27 | — | 0 | 0 | 0.00 | 0.00 | 67% | 45% | 1.03 | 1.25 | — | 6.8 |
| 82 | C. Mbemba | Lille | DR Congo | 4.2 | 0.1* | 0.46 | **1.94** | 2.14 | — | 2.21 | 0 | 0 | 0.00 | 0.00 | 69% | 48% | 1.01 | 0.84 | — | 6.8 |
| 83 | A. Dedić | Benfica | Bosnia and Herzegovina | 4.3 | 0.4* | 0.44 | **1.91** | 2.33 | 2.51 | 1.84 | 1 | 4 | 0.05 | 0.19 | 88% | 28% | 1.00 | 1.00 | C2 | 6.8 |
| 84 | J. Koundé | Barcelona | France | 5.4 | 7.3 | 0.35 | **1.87** | 2.05 | 1.40 | 1.80 | 1 | 3 | 0.04 | 0.12 | 80% | 31% | 0.80 | 1.18 | — | 6.9 |
| 85 | J. Šutalo | Ajax | Croatia | 4.3 | 0.0* | 0.43 | **1.85** | 2.30 | 2.34 | 2.34 | 0 | 0 | 0.00 | 0.00 | 79% | 39% | 1.01 | 1.15 | — | 6.9 |
| 86 | T. Hernández | Al-Hilal Saudi FC | France | 5.0 | 3.2* | 0.37 | **1.83** | 3.19 | 2.15 | 2.15 | 5 | 1 | 0.16 | 0.03 | 97% | 31% | 0.80 | 1.18 | — | 7.1 |
| 87 | A. Murillo | Marseille | Panama | 5.0 | 1.1* | 0.36 | **1.78** | 2.06 | — | 1.35 | 2 | 1 | 0.18 | 0.09 | 69% | 25% | 0.89 | 0.90 | FK1 | 6.7 |
| 88 | K. Koulibaly | Al-Hilal Saudi FC | Senegal | 4.9 | 0.7* | 0.36 | **1.75** | 3.17 | — | 0.97 | 1 | 2 | 0.06 | 0.11 | 97% | 40% | 0.87 | 1.22 | — | 7.4 |
| 89 | M. Talbi | Lorient | Tunisia | 3.9 | 0.1* | 0.44 | **1.72** | 1.64 | 1.65 | 2.80 | 0 | 1 | 0.00 | 0.03 | 97% | 24% | 1.08 | 0.85 | — | 6.9 |
| 90 | D. Sánchez | Galatasaray | Colombia | 4.3 | 0.8* | 0.40 | **1.72** | 2.50 | 1.95 | 2.60 | 1 | 0 | 0.04 | 0.00 | 97% | 36% | 0.87 | 1.05 | — | 7.1 |
| 91 | Marquinhos | Paris Saint Germain | Brazil | 5.2 | 7.1 | 0.32 | **1.66** | 1.91 | 1.98 | 0.41 | 0 | 0 | 0.00 | 0.00 | 79% | 33% | 0.99 | 1.09 | — | 7.3 |
| 92 | S. McKenna | Dinamo Zagreb | Scotland | 3.8 | 0.2* | 0.43 | **1.65** | 3.03 | 2.38 | 2.38 | 2 | 3 | 0.07 | 0.10 | 97% | 32% | 0.99 | 0.99 | — | 7.2 |
| 93 | C. Arcus | Angers | Haiti | 3.8 | 0.0* | 0.43 | **1.63** | 1.74 | — | 1.99 | 0 | 3 | 0.00 | 0.13 | 92% | 26% | 0.94 | 0.83 | — | 6.7 |
| 94 | D. Møller Wolfe | Wolves | Norway | 4.0 | 0.7* | 0.38 | **1.53** | 1.58 | 1.33 | — | 0 | 2 | 0.00 | 0.17 | 50% | 51% | 0.94 | 1.25 | — | 6.6 |
| 95 | K. Peprah Oppong | Nice | Ghana | 3.5 | 0.3* | 0.44 | **1.53** | 1.77 | 1.58 | 1.74 | 1 | 0 | 0.04 | 0.00 | 97% | 25% | 0.89 | 0.90 | — | 6.8 |
| 96 | C. Richards | Crystal Palace | USA | 4.1 | 0.7* | 0.37 | **1.52** | 1.78 | 1.29 | 0.92 | 1 | 0 | 0.03 | 0.00 | 94% | 24% | 1.13 | 0.98 | — | 6.9 |
| 97 | J. Córdoba | Norwich | Panama | 4.0 | 0.3* | 0.37 | **1.49** | 1.63 | 1.27 | 4.57 | 1 | 1 | 0.04 | 0.04 | 86% | 25% | 0.89 | 0.90 | — | 6.9 |
| 98 | G. Mensah | Auxerre | Ghana | 3.9 | 0.1* | 0.38 | **1.48** | 1.47 | 2.31 | 1.57 | 0 | 2 | 0.00 | 0.08 | 87% | 25% | 0.89 | 0.90 | — | 6.8 |
| 99 | Hassan Tambakti | Al-Hilal Saudi FC | Saudi Arabia | 4.5 | 0.1* | 0.32 | **1.45** | 2.32 | 1.98 | 2.23 | 1 | 0 | 0.04 | 0.00 | 97% | 32% | 0.99 | 0.77 | — | 7.1 |
| 100 | R. Araújo | Barcelona | Uruguay | 5.0 | 3.2* | 0.28 | **1.42** | 1.64 | — | 1.04 | 3 | 0 | 0.25 | 0.00 | 46% | 43% | 1.14 | 0.78 | — | 6.9 |
| 101 | D. Svensson | Borussia Dortmund | Sweden | 4.5 | 0.5* | 0.31 | **1.39** | 1.56 | — | 0.99 | 2 | 2 | 0.07 | 0.07 | 82% | 19% | 0.94 | 1.02 | — | 6.8 |
| 102 | Abdulelah Al Amri | Al-Nassr | Saudi Arabia | 3.7 | 0.0* | 0.38 | **1.39** | 2.40 | 1.62 | 1.82 | 2 | 2 | 0.10 | 0.10 | 80% | 32% | 0.99 | 0.77 | — | 7.1 |
| 103 | M. Olivera | Napoli | Uruguay | 4.3 | 0.9* | 0.31 | **1.34** | 1.41 | — | 1.41 | 0 | 0 | 0.00 | 0.00 | 60% | 43% | 1.14 | 0.78 | — | 6.8 |
| 104 | A. Robertson | Liverpool | Scotland | 5.0 | 4.9* | 0.26 | **1.31** | 1.23 | — | 1.50 | 1 | 0 | 0.08 | 0.00 | 46% | 32% | 0.99 | 0.99 | C1 | 6.7 |
| 105 | G. Hanley | Hibernian | Scotland | 3.5 | 0.4* | 0.37 | **1.31** | 2.02 | 1.29 | 2.37 | 0 | 0 | 0.00 | 0.00 | 96% | 32% | 0.99 | 0.99 | — | 6.7 |
| 106 | S. Kolašinac | Atalanta | Bosnia and Herzegovina | 4.3 | 0.2* | 0.30 | **1.29** | 1.36 | — | — | 0 | 0 | 0.00 | 0.00 | 79% | 28% | 1.00 | 1.00 | — | 6.7 |
| 107 | A. Andrade | Lask Linz | Panama | 3.7 | 0.0* | 0.34 | **1.26** | 2.10 | 1.74 | — | 1 | 3 | 0.03 | 0.10 | 97% | 25% | 0.89 | 0.90 | — | 7.3 |
| 108 | Y. Valery | Sheffield Wednesday | Tunisia | 3.9 | 0.0* | 0.30 | **1.18** | 1.64 | — | 1.47 | 0 | 1 | 0.00 | 0.04 | 97% | 24% | 1.08 | 0.85 | — | 6.6 |
| 109 | A. Preciado | Aldosivi | Ecuador | 4.3 | 0.1* | 0.27 | **1.14** | 1.58 | — | — | 3 | 2 | 0.27 | 0.18 | 33% | 64% | 1.01 | 0.77 | — | 6.8 |
| 110 | A. Trusty | Celtic | USA | 3.9 | 0.1* | 0.29 | **1.12** | 1.41 | 1.45 | 4.73 | 0 | 0 | 0.00 | 0.00 | 92% | 24% | 1.13 | 0.98 | — | 7.2 |
| 111 | Moteb Al Harbi | Al-Hilal Saudi FC | Saudi Arabia | 4.1 | 0.0* | 0.27 | **1.12** | 1.90 | 1.40 | 1.40 | 2 | 2 | 0.10 | 0.10 | 67% | 32% | 0.99 | 0.77 | — | 6.8 |
| 112 | I. Jakobs | Galatasaray | Senegal | 4.1 | 0.0* | 0.26 | **1.08** | 1.52 | 1.43 | 1.43 | 0 | 1 | 0.00 | 0.07 | 60% | 40% | 0.87 | 1.22 | — | 6.7 |
| 113 | M. Boxall | Minnesota United FC | New Zealand | 3.7 | 0.0* | 0.29 | **1.08** | 1.68 | 1.33 | 1.73 | 1 | 1 | 0.03 | 0.03 | 91% | 27% | 0.89 | 0.90 | — | 7.0 |
| 114 | G. Gudmundsson | Leeds | Sweden | 4.2 | 0.6* | 0.24 | **1.00** | 0.97 | — | 1.17 | 0 | 0 | 0.00 | 0.00 | 97% | 19% | 0.94 | 1.02 | — | 6.7 |
| 115 | G. Lagerbielke | SC Braga | Sweden | 3.7 | 0.2* | 0.27 | **1.00** | 1.41 | 1.12 | 0.66 | 2 | 0 | 0.07 | 0.00 | 93% | 19% | 0.94 | 1.02 | — | 7.0 |
| 116 | D. Bronn | Servette FC | Tunisia | 3.6 | 0.0* | 0.27 | **0.99** | 1.56 | — | 1.34 | 0 | 1 | 0.00 | 0.07 | 97% | 24% | 1.08 | 0.85 | — | 6.7 |
| 117 | C. Starfelt | Celta Vigo | Sweden | 4.1 | 0.1* | 0.23 | **0.94** | 0.92 | — | 1.08 | 0 | 0 | 0.00 | 0.00 | 90% | 19% | 0.94 | 1.02 | — | 6.9 |
| 118 | A. Seidu | Rennes | Ghana | 3.9 | 0.0* | 0.23 | **0.89** | 1.07 | — | 0.38 | 0 | 1 | 0.00 | 0.08 | 62% | 25% | 0.89 | 0.90 | — | 6.9 |
| 119 | V. Lindelöf | Aston Villa | Sweden | 4.0 | 1.8* | 0.21 | **0.85** | 0.92 | 0.75 | 0.75 | 0 | 1 | 0.00 | 0.09 | 65% | 19% | 0.94 | 1.02 | — | 6.7 |
| 120 | L. Cacace | Wrexham | New Zealand | 4.1 | 0.0* | 0.21 | **0.85** | 1.15 | — | 1.15 | 0 | 0 | 0.00 | 0.00 | 67% | 27% | 0.89 | 0.90 | — | 6.6 |
| 121 | N. Aké | Manchester City | Netherlands | 5.0 | 2.5* | 0.14 | **0.70** | 0.68 | 0.72 | 0.72 | 0 | 0 | 0.00 | 0.00 | 33% | 45% | 1.22 | 1.25 | — | 6.8 |
| 122 | A. Hickey | Brentford | Scotland | 4.3 | 0.2* | 0.14 | **0.61** | 0.60 | — | 0.64 | 0 | 0 | 0.00 | 0.00 | 38% | 32% | 0.99 | 0.99 | — | 6.7 |

### Midfielders — 124 ranked

| # | Player | Club | Nation | $ | Own% | Val | xPts | sXP | rXP | cXP | G | A | G/90 | A/90 | Start% | CS% | FixEase | TeamStr | SetPiece | Rtg |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | Lamine Yamal | Barcelona | Spain | 10.0 | 45.3 | 0.87 | **8.67** | 10.04 | — | 2.05 | 16 | 11 | 0.64 | 0.44 | 93% | 46% | 1.04 | 1.25 | FK2 C1 | 8.0 |
| 2 | H. Çalhanoğlu | Inter | Turkey | 7.1 | 2.7* | 1.19 | **8.48** | 8.81 | — | 9.23 | 9 | 4 | 0.49 | 0.22 | 91% | 34% | 1.22 | 1.10 | P1 FK1 C1 | 7.5 |
| 3 | Raphinha | Barcelona | Brazil | 8.2 | 21.4 | 0.98 | **8.02** | 8.51 | — | 4.56 | 13 | 3 | 0.84 | 0.20 | 82% | 33% | 0.99 | 1.09 | P1 FK1 C1 | 7.5 |
| 4 | Bruno Fernandes | Manchester United | Portugal | 8.5 | 50.3 | 0.92 | **7.81** | 7.79 | 7.87 | — | 9 | 21 | 0.26 | 0.62 | 97% | 39% | 0.87 | 1.25 | P2 FK2 C1 | 7.6 |
| 5 | I. Saibari | PSV Eindhoven | Morocco | 6.8 | 0.5* | 1.05 | **7.17** | 9.84 | — | 2.26 | 15 | 8 | 0.63 | 0.34 | 96% | 68% | 1.25 | 1.11 | — | 7.2 |
| 6 | B. Saka | Arsenal | England | 9.5 | 5.8 | 0.73 | **6.93** | 6.03 | 9.62 | 7.64 | 7 | 5 | 0.28 | 0.20 | 81% | 72% | 1.22 | 1.22 | C2 | 7.2 |
| 7 | E. Fernández | Chelsea | Argentina | 7.5 | 3.5* | 0.81 | **6.10** | 6.01 | 6.83 | 5.25 | 10 | 4 | 0.29 | 0.12 | 97% | 73% | 0.92 | 1.19 | — | 7.2 |
| 8 | M. Olise | Bayern München | France | 9.5 | 22.9 | 0.63 | **5.96** | 6.28 | 7.36 | 2.92 | 15 | 19 | 0.58 | 0.74 | 72% | 31% | 0.80 | 1.18 | FK1 C1 | 7.9 |
| 9 | Vinícius Júnior | Real Madrid | Brazil | 10.0 | 13.9 | 0.59 | **5.87** | 5.90 | 4.13 | 12.01 | 16 | 5 | 0.51 | 0.16 | 89% | 33% | 0.99 | 1.09 | C2 | 7.5 |
| 10 | K. De Bruyne | Napoli | Belgium | 7.5 | 5.6 | 0.77 | **5.75** | 6.29 | — | 3.73 | 5 | 2 | 0.39 | 0.15 | 72% | 45% | 1.03 | 1.25 | P1 FK1 C1 | 7.0 |
| 11 | Mohamed Salah | Liverpool | Egypt | 10.0 | 5.5 | 0.56 | **5.57** | 4.99 | — | 9.96 | 7 | 7 | 0.29 | 0.29 | 85% | 37% | 1.05 | 0.82 | P1 FK1 C1 | 6.9 |
| 12 | D. Rice | Arsenal | England | 7.0 | 6.8 | 0.78 | **5.45** | 5.86 | 3.68 | 5.63 | 4 | 5 | 0.12 | 0.14 | 97% | 72% | 1.22 | 1.22 | FK1 C1 | 7.5 |
| 13 | A. Güler | Real Madrid | Turkey | 7.0 | 9.0 | 0.76 | **5.31** | 5.48 | — | 5.47 | 4 | 9 | 0.18 | 0.40 | 76% | 34% | 1.22 | 1.10 | P2 FK2 C2 | 7.2 |
| 14 | L. Díaz | Bayern München | Colombia | 8.1 | 18.7 | 0.65 | **5.28** | 6.08 | 4.55 | 3.85 | 15 | 14 | 0.55 | 0.51 | 84% | 36% | 0.87 | 1.05 | P2 | 7.3 |
| 15 | J. Bellingham | Real Madrid | England | 8.3 | 9.4 | 0.63 | **5.22** | 5.44 | 5.86 | 2.35 | 6 | 4 | 0.28 | 0.19 | 79% | 72% | 1.22 | 1.22 | — | 7.3 |
| 16 | O. Kökçü | Beşiktaş | Turkey | 6.0 | 0.3* | 0.87 | **5.22** | 8.10 | 6.40 | 5.96 | 8 | 8 | 0.29 | 0.29 | 97% | 34% | 1.22 | 1.10 | — | 7.6 |
| 17 | S. Mané | Al-Nassr | Senegal | 7.6 | 2.0* | 0.66 | **4.99** | 7.11 | 6.62 | 17.50 | 10 | 6 | 0.42 | 0.25 | 97% | 40% | 0.87 | 1.22 | P1 FK1 | 7.3 |
| 18 | Casemiro | Manchester United | Brazil | 6.3 | 2.2* | 0.77 | **4.82** | 4.74 | — | 5.44 | 9 | 2 | 0.31 | 0.07 | 97% | 33% | 0.99 | 1.09 | — | 7.2 |
| 19 | J. Doku | Manchester City | Belgium | 7.5 | 13.0 | 0.64 | **4.80** | 4.29 | 7.09 | 2.39 | 5 | 5 | 0.25 | 0.25 | 63% | 45% | 1.03 | 1.25 | — | 7.4 |
| 20 | Bruno Guimarães | Newcastle | Brazil | 6.8 | 1.9* | 0.70 | **4.73** | 5.25 | 3.00 | 5.78 | 9 | 5 | 0.33 | 0.18 | 93% | 33% | 0.99 | 1.09 | FK3 C3 | 7.5 |
| 21 | G. Xhaka | Sunderland | Switzerland | 6.2 | 4.9* | 0.75 | **4.68** | 4.09 | 3.74 | 7.08 | 1 | 6 | 0.03 | 0.18 | 94% | 53% | 1.03 | 1.16 | P1 FK2 | 7.3 |
| 22 | Nico Williams | Athletic Club | Spain | 7.8 | 3.9* | 0.60 | **4.65** | 4.79 | — | — | 6 | 3 | 0.32 | 0.16 | 80% | 46% | 1.04 | 1.25 | C3 | 7.0 |
| 23 | F. Valverde | Real Madrid | Uruguay | 7.5 | 6.1 | 0.60 | **4.50** | 4.62 | — | 4.68 | 5 | 8 | 0.16 | 0.26 | 94% | 43% | 1.14 | 0.78 | P1 FK1 C2 | 7.3 |
| 24 | D. Doué | Paris Saint Germain | France | 7.5 | 3.3* | 0.60 | **4.49** | 4.61 | 5.07 | 7.77 | 7 | 4 | 0.47 | 0.27 | 70% | 31% | 0.80 | 1.18 | — | 7.1 |
| 25 | O. Dembélé | Paris Saint Germain | France | 10.0 | 19.1 | 0.45 | **4.45** | 5.13 | — | 2.77 | 10 | 7 | 0.85 | 0.59 | 50% | 31% | 0.80 | 1.18 | — | 7.4 |
| 26 | Pedri | Barcelona | Spain | 8.1 | 9.6 | 0.55 | **4.43** | 5.06 | 4.23 | 3.38 | 2 | 9 | 0.09 | 0.38 | 79% | 46% | 1.04 | 1.25 | FK1 | 7.5 |
| 27 | L. Modrić | AC Milan | Croatia | 6.2 | 2.5* | 0.71 | **4.40** | 4.80 | — | 3.36 | 2 | 3 | 0.06 | 0.10 | 94% | 39% | 1.01 | 1.15 | P1 FK1 C1 | 7.5 |
| 28 | R. Vargas | Sevilla | Switzerland | 6.8 | 0.5* | 0.64 | **4.36** | 4.67 | 4.33 | 4.15 | 3 | 6 | 0.17 | 0.34 | 83% | 53% | 1.03 | 1.16 | FK1 C1 | 6.7 |
| 29 | J. Enciso | Strasbourg | Paraguay | 6.6 | 0.2* | 0.66 | **4.34** | 4.25 | 6.95 | 2.36 | 3 | 6 | 0.14 | 0.28 | 82% | 37% | 1.32 | 0.84 | P1 FK2 C2 | 7.1 |
| 30 | S. McTominay | Napoli | Scotland | 6.5 | 10.9 | 0.66 | **4.32** | 4.65 | 3.64 | 5.21 | 10 | 3 | 0.32 | 0.10 | 94% | 32% | 0.99 | 0.99 | P1 | 7.1 |
| 31 | C. Pulišić | AC Milan | USA | 7.0 | 5.1 | 0.61 | **4.29** | 4.68 | — | 4.09 | 8 | 4 | 0.45 | 0.22 | 60% | 24% | 1.13 | 0.98 | P1 FK1 C1 | 7.0 |
| 32 | T. Kubo | Real Sociedad | Japan | 7.0 | 1.0* | 0.60 | **4.23** | 4.17 | — | 4.84 | 2 | 4 | 0.12 | 0.24 | 71% | 57% | 1.34 | 1.02 | FK1 C1 | 7.0 |
| 33 | R. Gravenberch | Liverpool | Netherlands | 6.1 | 0.9* | 0.68 | **4.17** | 4.10 | 5.05 | 2.06 | 5 | 3 | 0.15 | 0.09 | 94% | 45% | 1.22 | 1.25 | — | 7.1 |
| 34 | L. Trossard | Arsenal | Belgium | 6.6 | 2.3* | 0.63 | **4.13** | 3.96 | 3.99 | 6.02 | 6 | 6 | 0.27 | 0.27 | 68% | 45% | 1.03 | 1.25 | — | 7.0 |
| 35 | C. De Ketelaere | Atalanta | Belgium | 5.6 | 0.8* | 0.74 | **4.13** | 4.19 | 3.06 | 9.96 | 3 | 5 | 0.12 | 0.21 | 84% | 45% | 1.03 | 1.25 | — | 7.2 |
| 36 | J.  McGinn | Aston Villa | Scotland | 6.0 | 2.1* | 0.69 | **4.12** | 4.07 | 6.13 | 3.18 | 5 | 4 | 0.21 | 0.17 | 93% | 32% | 0.99 | 0.99 | P3 FK1 C4 | 7.0 |
| 37 | C. Baumgartner | RB Leipzig | Austria | 6.7 | 0.2* | 0.61 | **4.06** | 5.03 | 3.16 | 2.23 | 13 | 8 | 0.42 | 0.26 | 97% | 54% | 0.81 | 1.08 | — | 6.9 |
| 38 | A. Ounahi | Girona | Morocco | 6.2 | 0.1* | 0.65 | **4.01** | 4.67 | 3.19 | 2.12 | 5 | 2 | 0.26 | 0.10 | 83% | 68% | 1.25 | 1.11 | FK2 | 7.3 |
| 39 | T. Reijnders | Manchester City | Netherlands | 6.5 | 1.6* | 0.60 | **3.89** | 3.53 | — | 7.32 | 5 | 2 | 0.27 | 0.11 | 68% | 45% | 1.22 | 1.25 | FK2 | 6.8 |
| 40 | M. Pašalić | Orlando City SC | Croatia | 6.4 | 0.1* | 0.60 | **3.86** | 5.67 | — | — | 12 | 5 | 0.40 | 0.17 | 97% | 39% | 1.01 | 1.15 | — | 7.2 |
| 41 | R. Mahrez | Al-Ahli Jeddah | Algeria | 6.5 | 0.7* | 0.58 | **3.75** | 5.85 | 5.51 | — | 4 | 8 | 0.16 | 0.32 | 97% | 61% | 0.86 | 1.03 | P1 FK1 C2 | 7.5 |
| 42 | N. Angulo | Anderlecht | Ecuador | 6.0 | 0.2* | 0.61 | **3.68** | 5.06 | — | 2.76 | 6 | 5 | 0.28 | 0.24 | 97% | 64% | 1.01 | 0.77 | — | 7.3 |
| 43 | R. Rios | Benfica | Colombia | 4.7 | 0.6* | 0.76 | **3.58** | 3.42 | 8.06 | 1.94 | 5 | 4 | 0.20 | 0.16 | 96% | 36% | 0.87 | 1.05 | — | 7.1 |
| 44 | F. Rieder | FC Augsburg | Switzerland | 6.2 | 0.1* | 0.56 | **3.46** | 4.28 | 3.16 | 2.69 | 6 | 3 | 0.23 | 0.11 | 88% | 53% | 1.03 | 1.16 | FK3 C2 | 6.9 |
| 45 | K. Thorstvedt | Sassuolo | Norway | 6.2 | 0.0* | 0.53 | **3.26** | 3.34 | 4.00 | 1.28 | 4 | 4 | 0.15 | 0.15 | 84% | 51% | 0.94 | 1.25 | — | 6.9 |
| 46 | A. Mac Allister | Liverpool | Argentina | 6.6 | 3.3* | 0.49 | **3.25** | 3.01 | 2.37 | 4.72 | 2 | 4 | 0.07 | 0.13 | 84% | 73% | 0.92 | 1.19 | — | 6.7 |
| 47 | K. Laimer | Bayern München | Austria | 5.8 | 0.4* | 0.56 | **3.25** | 3.37 | 3.74 | — | 3 | 9 | 0.14 | 0.41 | 76% | 54% | 0.81 | 1.08 | — | 6.8 |
| 48 | M. Almirón | Atlanta United FC | Paraguay | 6.0 | 0.4* | 0.54 | **3.23** | 4.40 | — | 7.42 | 6 | 4 | 0.20 | 0.13 | 97% | 37% | 1.32 | 0.84 | P2 FK3 | 7.2 |
| 49 | Y. Tielemans | Aston Villa | Belgium | 6.1 | 1.2* | 0.52 | **3.20** | 3.45 | 2.43 | — | 0 | 4 | 0.00 | 0.19 | 84% | 45% | 1.03 | 1.25 | FK2 C2 | 7.2 |
| 50 | J. Arias | Fluminense | Colombia | 6.3 | 0.3* | 0.51 | **3.20** | 4.13 | — | 3.81 | 1 | 4 | 0.08 | 0.33 | 97% | 36% | 0.87 | 1.05 | — | 7.3 |
| 51 | F. Chaïbi | Eintracht Frankfurt | Algeria | 6.2 | 0.0* | 0.52 | **3.20** | 3.54 | — | 2.26 | 2 | 9 | 0.10 | 0.45 | 75% | 61% | 0.86 | 1.03 | FK2 C1 | 6.8 |
| 52 | P. Gueye | Villarreal | Senegal | 5.9 | 0.1* | 0.54 | **3.19** | 3.22 | 4.09 | 1.73 | 5 | 2 | 0.21 | 0.08 | 87% | 40% | 0.87 | 1.22 | — | 7.1 |
| 53 | P. Šulc | Lyon | Czechia | 5.9 | 0.2* | 0.54 | **3.18** | 3.96 | — | 2.47 | 11 | 3 | 0.63 | 0.17 | 63% | 44% | 0.94 | 1.00 | FK2 C2 | 6.9 |
| 54 | F. Wirtz | Liverpool | Germany | 7.5 | 22.9 | 0.42 | **3.15** | 3.31 | — | 1.77 | 5 | 3 | 0.19 | 0.11 | 82% | 38% | 0.75 | 1.16 | FK2 C2 | 6.8 |
| 55 | W. McKennie | Juventus | USA | 6.1 | 0.5* | 0.51 | **3.12** | 3.49 | 2.48 | 3.57 | 5 | 5 | 0.16 | 0.16 | 89% | 24% | 1.13 | 0.98 | — | 6.9 |
| 56 | P. Wimmer | VfL Wolfsburg | Austria | 6.0 | 0.2* | 0.52 | **3.11** | 3.45 | 3.12 | 1.79 | 4 | 3 | 0.22 | 0.17 | 84% | 54% | 0.81 | 1.08 | — | 6.9 |
| 57 | A. Rabiot | AC Milan | France | 6.4 | 0.3* | 0.48 | **3.10** | 3.74 | 2.47 | 1.69 | 6 | 4 | 0.21 | 0.14 | 97% | 31% | 0.80 | 1.18 | — | 7.2 |
| 58 | A. Onana | Aston Villa | Belgium | 5.9 | 0.3* | 0.52 | **3.09** | 2.60 | — | 7.86 | 2 | 0 | 0.10 | 0.00 | 84% | 45% | 1.03 | 1.25 | — | 7.0 |
| 59 | L. Goretzka | Bayern München | Germany | 6.1 | 0.4* | 0.50 | **3.08** | 2.90 | 4.12 | — | 5 | 3 | 0.23 | 0.14 | 81% | 38% | 0.75 | 1.16 | — | 7.1 |
| 60 | A. Nusa | RB Leipzig | Norway | 6.1 | 3.6* | 0.50 | **3.05** | 3.41 | — | 1.50 | 4 | 3 | 0.18 | 0.13 | 77% | 51% | 0.94 | 1.25 | — | 7.1 |
| 61 | I. Gueye | Everton | Senegal | 4.9 | 0.3* | 0.62 | **3.04** | 3.03 | — | 3.08 | 2 | 3 | 0.09 | 0.13 | 97% | 40% | 0.87 | 1.22 | — | 6.8 |
| 62 | H. Aouar | Al-Ittihad FC | Algeria | 6.0 | 0.2* | 0.50 | **3.02** | 4.36 | 5.89 | 2.42 | 8 | 3 | 0.38 | 0.14 | 96% | 61% | 0.86 | 1.03 | C3 | 7.1 |
| 63 | Bernardo Silva | Manchester City | Portugal | 7.8 | 2.4* | 0.39 | **3.01** | 2.90 | 2.37 | 3.94 | 2 | 4 | 0.06 | 0.12 | 90% | 39% | 0.87 | 1.25 | — | 6.8 |
| 64 | I. Sangaré | Nottingham Forest | Ivory Coast | 5.8 | 0.1* | 0.51 | **2.98** | 2.98 | — | — | 2 | 2 | 0.09 | 0.09 | 89% | 61% | 0.96 | 1.00 | P2 | 7.0 |
| 65 | S. Berhalter | Vancouver Whitecaps | USA | 4.7 | 0.1* | 0.63 | **2.98** | 4.58 | 2.44 | 11.58 | 4 | 10 | 0.13 | 0.32 | 87% | 24% | 1.13 | 0.98 | FK2 | 7.6 |
| 66 | A. Ito | Gent | Japan | 5.0 | 1.5* | 0.59 | **2.96** | 3.95 | — | — | 4 | 3 | 0.17 | 0.12 | 87% | 57% | 1.34 | 1.02 | FK2 C2 | 6.9 |
| 67 | L. Sané | Galatasaray | Germany | 7.4 | 1.2* | 0.40 | **2.96** | 4.32 | 2.31 | 7.57 | 7 | 5 | 0.28 | 0.20 | 96% | 38% | 0.75 | 1.16 | — | 7.2 |
| 68 | Brahim Díaz | Real Madrid | Morocco | 6.4 | 1.7* | 0.46 | **2.95** | 2.97 | 3.71 | 2.24 | 1 | 6 | 0.07 | 0.42 | 43% | 68% | 1.25 | 1.11 | P1 C2 | 6.7 |
| 69 | L. Paredes | Boca Juniors | Argentina | 5.6 | 0.2* | 0.53 | **2.95** | 4.61 | 3.33 | 3.07 | 1 | 4 | 0.06 | 0.24 | 94% | 73% | 0.92 | 1.19 | C2 | 7.8 |
| 70 | I. Koné | Sassuolo | Canada | 6.0 | 0.3* | 0.49 | **2.93** | 3.38 | 2.36 | 1.63 | 6 | 0 | 0.20 | 0.00 | 94% | 72% | 1.24 | 0.88 | — | 7.0 |
| 71 | João Neves | Paris Saint Germain | Portugal | 6.5 | 4.1* | 0.45 | **2.93** | 3.18 | 1.84 | 4.21 | 5 | 1 | 0.35 | 0.07 | 62% | 39% | 0.87 | 1.25 | — | 7.2 |
| 72 | M. Caicedo | Chelsea | Ecuador | 6.8 | 1.6* | 0.43 | **2.91** | 3.03 | 2.39 | 3.52 | 3 | 1 | 0.10 | 0.03 | 97% | 64% | 1.01 | 0.77 | P2 C1 | 7.2 |
| 73 | F. de Jong | Barcelona | Netherlands | 7.0 | 1.6* | 0.41 | **2.86** | 3.28 | — | 2.12 | 1 | 5 | 0.06 | 0.28 | 64% | 45% | 1.22 | 1.25 | — | 7.3 |
| 74 | Lee Kang-In | Paris Saint Germain | South Korea | 6.1 | 0.5* | 0.47 | **2.86** | 3.21 | 4.06 | 2.43 | 3 | 4 | 0.18 | 0.24 | 67% | 47% | 0.99 | 0.96 | FK2 C2 | 7.0 |
| 75 | Jesús Rodríguez | Como | Spain | 7.5 | 1.8* | 0.38 | **2.83** | 3.10 | — | 1.17 | 2 | 9 | 0.10 | 0.47 | 58% | 46% | 1.04 | 1.25 | — | 6.9 |
| 76 | M. Sabitzer | Borussia Dortmund | Austria | 6.8 | 3.3* | 0.41 | **2.77** | 2.62 | 2.85 | 5.46 | 1 | 2 | 0.05 | 0.10 | 81% | 54% | 0.81 | 1.08 | P2 FK1 C1 | 6.9 |
| 77 | Vitinha | Paris Saint Germain | Portugal | 6.4 | 11.3 | 0.43 | **2.73** | 3.03 | — | — | 1 | 7 | 0.04 | 0.30 | 83% | 39% | 0.87 | 1.25 | — | 7.6 |
| 78 | R. Zerrouki | Twente | Algeria | 5.3 | 0.0* | 0.52 | **2.73** | 3.49 | 3.19 | — | 4 | 1 | 0.11 | 0.03 | 97% | 61% | 0.86 | 1.03 | — | 7.2 |
| 79 | R. Freuler | Bologna | Switzerland | 5.9 | 0.0* | 0.46 | **2.72** | 2.86 | 2.03 | 3.67 | 1 | 2 | 0.04 | 0.08 | 90% | 53% | 1.03 | 1.16 | — | 6.9 |
| 80 | F. Kessié | Al-Ahli Jeddah | Ivory Coast | 5.9 | 0.1* | 0.46 | **2.72** | 4.38 | — | 2.68 | 5 | 3 | 0.22 | 0.13 | 97% | 61% | 0.96 | 1.00 | P1 FK2 | 7.0 |
| 81 | Salem Al Dawsari | Al-Hilal Saudi FC | Saudi Arabia | 7.2 | 0.2* | 0.38 | **2.70** | 4.44 | — | 1.62 | 8 | 8 | 0.38 | 0.38 | 85% | 32% | 0.99 | 0.77 | C2 | 7.3 |
| 82 | Lee Jae-Sung | FSV Mainz 05 | South Korea | 6.2 | 0.1* | 0.43 | **2.69** | 3.25 | — | 1.88 | 4 | 2 | 0.16 | 0.08 | 93% | 47% | 0.99 | 0.96 | — | 6.7 |
| 83 | T. Almada | Atletico Madrid | Argentina | 6.5 | 0.2* | 0.39 | **2.52** | 2.61 | — | 2.53 | 3 | 1 | 0.21 | 0.07 | 59% | 73% | 0.92 | 1.19 | — | 6.8 |
| 84 | Fabián Ruiz | Paris Saint Germain | Spain | 6.8 | 1.0* | 0.37 | **2.50** | 2.92 | 2.82 | 1.48 | 1 | 4 | 0.08 | 0.32 | 65% | 46% | 1.04 | 1.25 | — | 7.1 |
| 85 | E. Álvarez | Guadalajara Chivas | Mexico | 6.0 | 0.5* | 0.41 | **2.47** | 3.73 | 3.31 | 2.39 | 3 | 7 | 0.11 | 0.25 | 87% | 48% | 1.01 | 0.90 | — | 7.1 |
| 86 | C. Devlin | Heart Of Midlothian | Australia | 4.7 | 0.0* | 0.52 | **2.45** | 3.46 | 4.60 | — | 2 | 0 | 0.07 | 0.00 | 96% | 42% | 1.34 | 0.92 | — | 7.2 |
| 87 | J. Musiala | Bayern München | Germany | 8.0 | 12.2 | 0.30 | **2.44** | 2.81 | 2.55 | 0.93 | 3 | 4 | 0.39 | 0.53 | 47% | 38% | 0.75 | 1.16 | — | 6.7 |
| 88 | O. Pineda | AEK Athens FC | Mexico | 6.2 | 0.1* | 0.39 | **2.44** | 3.39 | 4.71 | — | 5 | 2 | 0.18 | 0.07 | 93% | 48% | 1.01 | 0.90 | — | 7.3 |
| 89 | T. Adams | Bournemouth | USA | 5.3 | 0.3* | 0.46 | **2.42** | 2.42 | 2.14 | 2.97 | 2 | 2 | 0.10 | 0.10 | 84% | 24% | 1.13 | 0.98 | — | 6.8 |
| 90 | P. Vite | Vancouver Whitecaps | Ecuador | 5.2 | 0.0* | 0.46 | **2.38** | 3.62 | — | 2.58 | 4 | 2 | 0.26 | 0.13 | 84% | 64% | 1.01 | 0.77 | — | 7.4 |
| 91 | S. Berge | Fulham | Norway | 4.7 | 0.3* | 0.50 | **2.36** | 2.33 | — | 2.56 | 0 | 1 | 0.00 | 0.03 | 97% | 51% | 0.94 | 1.25 | — | 6.9 |
| 92 | T. Weah | Marseille | USA | 5.8 | 0.3* | 0.39 | **2.29** | 2.80 | — | 1.90 | 2 | 2 | 0.08 | 0.08 | 90% | 24% | 1.13 | 0.98 | — | 6.8 |
| 93 | Y. Ayari | Brighton | Sweden | 5.3 | 0.2* | 0.42 | **2.22** | 2.52 | — | 0.91 | 3 | 3 | 0.14 | 0.14 | 69% | 19% | 0.94 | 1.02 | FK1 C2 | 6.8 |
| 94 | A. Tchouaméni | Real Madrid | France | 6.5 | 0.9* | 0.34 | **2.22** | 2.25 | 2.21 | 3.23 | 1 | 0 | 0.03 | 0.00 | 94% | 31% | 0.80 | 1.18 | — | 7.2 |
| 95 | N. Seiwald | RB Leipzig | Austria | 5.6 | 0.0* | 0.39 | **2.18** | 2.44 | — | 1.44 | 0 | 2 | 0.00 | 0.07 | 94% | 54% | 0.81 | 1.08 | — | 6.9 |
| 96 | D. Bobadilla | Sao Paulo | Paraguay | 5.5 | 0.0* | 0.40 | **2.18** | 2.63 | 3.91 | 1.91 | 4 | 2 | 0.17 | 0.08 | 71% | 37% | 1.32 | 0.84 | — | 7.0 |
| 97 | A. Pavlović | Bayern München | Germany | 5.5 | 0.6* | 0.39 | **2.13** | 2.28 | — | 2.16 | 3 | 1 | 0.18 | 0.06 | 67% | 38% | 0.75 | 1.16 | — | 7.2 |
| 98 | T. Souček | West Ham | Czechia | 5.6 | 0.5* | 0.38 | **2.12** | 2.25 | 1.59 | 2.27 | 5 | 0 | 0.20 | 0.00 | 69% | 44% | 0.94 | 1.00 | P2 | 6.8 |
| 99 | Y. Bárcenas | Mazatlán | Panama | 5.6 | 0.0* | 0.37 | **2.08** | 2.43 | 3.71 | 5.35 | 3 | 1 | 0.12 | 0.04 | 83% | 25% | 0.89 | 0.90 | — | 6.8 |
| 100 | R. Bentancur | Tottenham | Uruguay | 6.0 | 0.2* | 0.34 | **2.07** | 2.23 | 2.11 | 1.64 | 1 | 1 | 0.05 | 0.05 | 88% | 43% | 1.14 | 0.78 | — | 6.8 |
| 101 | L. Sučić | Real Sociedad | Croatia | 4.9 | 0.1* | 0.39 | **1.91** | 1.97 | 1.04 | 3.67 | 3 | 1 | 0.27 | 0.09 | 46% | 39% | 1.01 | 1.15 | — | 6.8 |
| 102 | J. Bacuna | FC Volendam | Curacao | 5.1 | 0.0* | 0.37 | **1.90** | 2.28 | 2.68 | 2.27 | 0 | 2 | 0.00 | 0.25 | 62% | 34% | 0.73 | 0.97 | P1 FK1 C1 | 7.0 |
| 103 | Bae Jun-Ho | Stoke City | South Korea | 5.9 | 0.0* | 0.31 | **1.85** | 2.29 | — | 3.40 | 2 | 3 | 0.06 | 0.09 | 76% | 47% | 0.99 | 0.96 | — | 6.7 |
| 104 | A. Tanaka | Leeds | Japan | 5.0 | 1.3* | 0.35 | **1.73** | 1.93 | 1.14 | 1.26 | 2 | 0 | 0.14 | 0.00 | 50% | 57% | 1.34 | 1.02 | — | 6.7 |
| 105 | H. Boudaoui | Nice | Algeria | 5.5 | 0.0* | 0.30 | **1.65** | 1.94 | 1.73 | 1.12 | 1 | 2 | 0.05 | 0.11 | 73% | 61% | 0.86 | 1.03 | — | 6.8 |
| 106 | B. Ojeda | Real Salt Lake | Paraguay | 5.6 | 0.0* | 0.28 | **1.58** | 2.32 | — | — | 2 | 0 | 0.08 | 0.00 | 84% | 37% | 1.32 | 0.84 | — | 7.0 |
| 107 | Mohamed Kanno | Al-Hilal Saudi FC | Saudi Arabia | 5.1 | 0.0* | 0.31 | **1.57** | 2.88 | 1.90 | 1.86 | 5 | 3 | 0.21 | 0.13 | 78% | 32% | 0.99 | 0.77 | — | 7.2 |
| 108 | S. Fofana | Rennes | Ivory Coast | 6.8 | 0.2* | 0.23 | **1.53** | 1.80 | — | 0.85 | 1 | 0 | 0.14 | 0.00 | 58% | 61% | 0.96 | 1.00 | — | 6.8 |
| 109 | S. Moutoussamy | Atromitos | DR Congo | 5.1 | 0.0* | 0.30 | **1.52** | 2.61 | 1.90 | 2.42 | 3 | 0 | 0.12 | 0.00 | 96% | 48% | 1.01 | 0.84 | — | 6.9 |
| 110 | J. Karlström | Udinese | Sweden | 5.6 | 0.0* | 0.26 | **1.47** | 1.83 | 1.15 | 0.78 | 1 | 0 | 0.03 | 0.00 | 97% | 19% | 0.94 | 1.02 | — | 6.8 |
| 111 | L. Ferguson | Bologna | Scotland | 4.8 | 0.2* | 0.30 | **1.46** | 1.30 | 1.34 | 2.26 | 1 | 0 | 0.06 | 0.00 | 63% | 32% | 0.99 | 0.99 | FK2 C2 | 6.7 |
| 112 | K. Diatta | Monaco | Senegal | 6.1 | 0.0* | 0.24 | **1.46** | 1.68 | — | 1.17 | 0 | 1 | 0.00 | 0.09 | 56% | 40% | 0.87 | 1.22 | C1 | 6.9 |
| 113 | R. Christie | Bournemouth | Scotland | 5.6 | 0.1* | 0.25 | **1.42** | 1.09 | — | 2.25 | 2 | 0 | 0.18 | 0.00 | 35% | 32% | 0.99 | 0.99 | P2 FK3 C3 | 6.7 |
| 114 | A. Carrasquilla | U.N.A.M. - Pumas | Panama | 6.5 | 0.1* | 0.20 | **1.32** | 2.17 | 1.67 | 0.89 | 2 | 6 | 0.06 | 0.19 | 84% | 25% | 0.89 | 0.90 | C2 | 6.9 |
| 115 | A. Godoy | San Diego | Panama | 5.6 | 0.0* | 0.23 | **1.29** | 1.94 | 1.93 | 1.44 | 1 | 1 | 0.04 | 0.04 | 86% | 25% | 0.89 | 0.90 | — | 7.1 |
| 116 | J. Lerma | Crystal Palace | Colombia | 4.9 | 0.2* | 0.25 | **1.24** | 1.25 | 1.25 | 1.15 | 0 | 2 | 0.00 | 0.10 | 58% | 36% | 0.87 | 1.05 | — | 6.7 |
| 117 | K. Sibo | Oviedo | Ghana | 4.7 | 0.0* | 0.26 | **1.24** | 1.32 | — | 0.98 | 0 | 0 | 0.00 | 0.00 | 81% | 25% | 0.89 | 0.90 | — | 6.6 |
| 118 | E. Skhiri | Eintracht Frankfurt | Tunisia | 4.7 | 0.0* | 0.26 | **1.20** | 1.03 | 1.09 | 2.05 | 0 | 0 | 0.00 | 0.00 | 64% | 24% | 1.08 | 0.85 | — | 6.7 |
| 119 | Nasser Al Dawsari | Al-Hilal Saudi FC | Saudi Arabia | 5.2 | 0.1* | 0.22 | **1.12** | 1.51 | 2.10 | 2.47 | 0 | 1 | 0.00 | 0.06 | 63% | 32% | 0.99 | 0.77 | — | 6.9 |
| 120 | N. El Aynaoui | AS Roma | Morocco | 5.6 | 0.1* | 0.19 | **1.09** | 1.20 | — | 0.83 | 1 | 2 | 0.09 | 0.18 | 32% | 68% | 1.25 | 1.11 | — | 6.7 |
| 121 | M. Ugarte | Manchester United | Uruguay | 5.9 | 0.2* | 0.15 | **0.89** | 1.02 | — | 0.56 | 0 | 0 | 0.00 | 0.00 | 36% | 43% | 1.14 | 0.78 | — | 6.7 |
| 122 | Abdullah Al Khaibari | Al-Nassr | Saudi Arabia | 5.1 | 0.0* | 0.13 | **0.65** | 0.91 | 1.38 | 0.96 | 0 | 1 | 0.00 | 0.05 | 47% | 32% | 0.99 | 0.77 | — | 6.7 |
| 123 | T. Partey | Villarreal | Ghana | 6.2 | 0.1* | 0.09 | **0.53** | 0.58 | — | 0.46 | 0 | 0 | 0.00 | 0.00 | 32% | 25% | 0.89 | 0.90 | — | 6.6 |
| 124 | C. Metcalfe | FC St. Pauli | Australia | 5.3 | 0.0* | 0.08 | **0.43** | 0.46 | 0.53 | 0.22 | 0 | 2 | 0.00 | 0.30 | 12% | 42% | 1.34 | 0.92 | C3 | 6.6 |

### Forwards — 57 ranked

| # | Player | Club | Nation | $ | Own% | Val | xPts | sXP | rXP | cXP | G | A | G/90 | A/90 | Start% | CS% | FixEase | TeamStr | SetPiece | Rtg |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | H. Kane | Bayern München | England | 10.5 | 37.6 | 1.07 | **11.26** | 12.08 | 11.26 | 14.33 | 36 | 5 | 1.36 | 0.19 | 81% | 72% | 1.22 | 1.22 | P1 | 7.9 |
| 2 | D. Malen | AS Roma | Netherlands | 6.1 | 1.4* | 1.53 | **9.33** | 10.25 | 10.87 | 1.74 | 14 | 2 | 0.85 | 0.12 | 97% | 45% | 1.22 | 1.25 | — | 7.2 |
| 3 | E. Haaland | Manchester City | Norway | 10.5 | 33.5 | 0.78 | **8.15** | 8.27 | 9.77 | 1.63 | 27 | 8 | 0.82 | 0.24 | 97% | 51% | 0.94 | 1.25 | P1 | 7.3 |
| 4 | L. Messi | Inter Miami | Argentina | 10.0 | 17.6 | 0.72 | **7.16** | 10.77 | 11.15 | 8.38 | 35 | 23 | 1.06 | 0.69 | 94% | 73% | 0.92 | 1.19 | P1 FK1 C1 | 8.6 |
| 5 | A. Ueda | Feyenoord | Japan | 7.0 | 0.7* | 0.99 | **6.90** | 9.05 | 7.21 | — | 25 | 1 | 0.89 | 0.04 | 97% | 57% | 1.34 | 1.02 | P1 | 7.2 |
| 6 | Kylian Mbappé | Real Madrid | France | 10.5 | 50.5 | 0.59 | **6.16** | 6.90 | 5.11 | 2.22 | 25 | 5 | 0.86 | 0.17 | 94% | 31% | 0.80 | 1.18 | P1 | 7.5 |
| 7 | Mikel Oyarzabal | Real Sociedad | Spain | 8.1 | 17.0 | 0.70 | **5.64** | 5.62 | 5.47 | 8.88 | 15 | 4 | 0.50 | 0.13 | 88% | 46% | 1.04 | 1.25 | P1 | 7.1 |
| 8 | L. Suárez | Sporting CP | Colombia | 5.7 | 2.6* | 0.98 | **5.58** | 7.02 | 7.21 | 0.97 | 28 | 6 | 0.93 | 0.20 | 97% | 36% | 0.87 | 1.05 | — | 7.4 |
| 9 | Son Heung-Min | Los Angeles FC | South Korea | 7.4 | 2.1* | 0.66 | **4.85** | 7.80 | 7.50 | 5.08 | 12 | 3 | 0.98 | 0.24 | 91% | 47% | 0.99 | 0.96 | P1 FK1 C1 | 8.2 |
| 10 | P. Schick | Bayer Leverkusen | Czechia | 7.3 | 0.8* | 0.66 | **4.80** | 5.09 | 7.62 | 2.66 | 16 | 3 | 0.72 | 0.14 | 82% | 44% | 0.94 | 1.00 | P1 | 7.0 |
| 11 | Cristiano Ronaldo | Al-Nassr | Portugal | 10.0 | 12.3 | 0.47 | **4.72** | 8.37 | 6.36 | 5.39 | 28 | 2 | 0.96 | 0.07 | 97% | 39% | 0.87 | 1.25 | P1 FK1 | 7.2 |
| 12 | M. Depay | Corinthians | Netherlands | 7.4 | 1.2* | 0.58 | **4.32** | 4.34 | — | 8.53 | 6 | 3 | 0.34 | 0.17 | 74% | 45% | 1.22 | 1.25 | P2 FK1 C1 | 7.0 |
| 13 | A. Kramarić | 1899 Hoffenheim | Croatia | 6.2 | 0.2* | 0.68 | **4.24** | 5.10 | 4.56 | 0.00 | 14 | 6 | 0.57 | 0.24 | 76% | 39% | 1.01 | 1.15 | — | 7.1 |
| 14 | C. Gakpo | Liverpool | Netherlands | 7.7 | 3.1* | 0.54 | **4.17** | 4.52 | 3.84 | 2.27 | 7 | 5 | 0.23 | 0.16 | 89% | 45% | 1.22 | 1.25 | P1 C2 | 6.9 |
| 15 | A. El Kaabi | Olympiakos Piraeus | Morocco | 5.9 | 0.3* | 0.69 | **4.09** | 8.00 | 3.85 | 0.89 | 18 | 2 | 0.77 | 0.09 | 89% | 68% | 1.25 | 1.11 | — | 6.8 |
| 16 | A. Budimir | Osasuna | Croatia | 6.8 | 0.2* | 0.58 | **3.91** | 4.65 | 3.07 | 1.08 | 17 | 0 | 0.52 | 0.00 | 95% | 39% | 1.01 | 1.15 | P2 | 6.8 |
| 17 | E. Demirović | VfB Stuttgart | Bosnia and Herzegovina | 6.2 | 0.1* | 0.62 | **3.83** | 3.92 | 5.22 | 2.75 | 12 | 3 | 0.72 | 0.18 | 68% | 28% | 1.00 | 1.00 | P3 | 6.9 |
| 18 | João Félix | Al-Nassr | Portugal | 6.5 | 2.1* | 0.58 | **3.78** | 6.21 | 7.34 | 2.15 | 20 | 13 | 0.62 | 0.40 | 97% | 39% | 0.87 | 1.25 | — | 7.8 |
| 19 | I. Sarr | Crystal Palace | Senegal | 6.2 | 0.5* | 0.60 | **3.75** | 3.77 | 4.78 | 2.58 | 9 | 1 | 0.37 | 0.04 | 86% | 40% | 0.87 | 1.22 | — | 6.8 |
| 20 | E. Shomurodov | Başakşehir | Uzbekistan | 6.5 | 0.1* | 0.58 | **3.75** | 5.50 | 6.30 | 2.15 | 22 | 5 | 0.68 | 0.15 | 97% | 47% | 0.99 | 0.90 | P1 | 7.2 |
| 21 | Matheus Cunha | Manchester United | Brazil | 7.3 | 3.5* | 0.50 | **3.66** | 3.38 | 4.38 | 4.30 | 10 | 2 | 0.36 | 0.07 | 88% | 33% | 0.99 | 1.09 | — | 7.1 |
| 22 | F. Balogun | Monaco | USA | 6.0 | 0.9* | 0.60 | **3.62** | 4.59 | 2.53 | — | 13 | 4 | 0.52 | 0.16 | 87% | 24% | 1.13 | 0.98 | P2 | 6.8 |
| 23 | V. Gyökeres | Arsenal | Sweden | 7.8 | 6.1 | 0.46 | **3.61** | 3.39 | 6.20 | 1.21 | 14 | 1 | 0.56 | 0.04 | 72% | 19% | 0.94 | 1.02 | P1 | 6.6 |
| 24 | A. Semenyo | Manchester City | Ghana | 7.2 | 4.6* | 0.49 | **3.54** | 3.90 | 3.17 | 0.97 | 17 | 4 | 0.48 | 0.11 | 97% | 25% | 0.89 | 0.90 | — | 7.0 |
| 25 | J. Álvarez | Atletico Madrid | Argentina | 8.6 | 16.0 | 0.37 | **3.20** | 3.23 | — | 3.67 | 8 | 4 | 0.38 | 0.19 | 76% | 73% | 0.92 | 1.19 | FK2 | 7.0 |
| 26 | I. Perišić | PSV Eindhoven | Croatia | 5.4 | 0.5* | 0.57 | **3.08** | 4.13 | — | 1.43 | 7 | 12 | 0.28 | 0.49 | 90% | 39% | 1.01 | 1.15 | C2 | 7.2 |
| 27 | K. Aktürkoğlu | Fenerbahçe | Turkey | 6.2 | 0.3* | 0.49 | **3.01** | 4.40 | 6.19 | 1.77 | 8 | 7 | 0.37 | 0.32 | 83% | 34% | 1.22 | 1.10 | — | 7.1 |
| 28 | R. Jiménez | Fulham | Mexico | 7.0 | 2.7* | 0.43 | **3.00** | 3.13 | — | 1.91 | 9 | 3 | 0.37 | 0.12 | 75% | 48% | 1.01 | 0.90 | P1 FK1 | 6.7 |
| 29 | Y. Diomande | RB Leipzig | Ivory Coast | 5.9 | 1.1* | 0.47 | **2.78** | 3.68 | 2.37 | 1.72 | 12 | 8 | 0.44 | 0.29 | 85% | 61% | 0.96 | 1.00 | C2 | 7.7 |
| 30 | N. Jackson | Bayern München | Senegal | 6.7 | 0.4* | 0.41 | **2.76** | 3.07 | 3.14 | 0.58 | 8 | 1 | 0.69 | 0.09 | 52% | 40% | 0.87 | 1.22 | P2 | 6.8 |
| 31 | B. Embolo | Rennes | Switzerland | 7.5 | 2.5* | 0.36 | **2.73** | 2.99 | 2.64 | 3.41 | 9 | 3 | 0.43 | 0.14 | 64% | 53% | 1.03 | 1.16 | P2 | 6.7 |
| 32 | N. Pépé | Villarreal | Ivory Coast | 5.9 | 0.2* | 0.46 | **2.70** | 2.78 | — | — | 8 | 8 | 0.30 | 0.30 | 72% | 61% | 0.96 | 1.00 | — | 7.2 |
| 33 | I. Ndiaye | Everton | Senegal | 6.5 | 0.6* | 0.41 | **2.69** | 3.29 | 1.48 | 1.51 | 6 | 3 | 0.19 | 0.10 | 97% | 40% | 0.87 | 1.22 | — | 6.9 |
| 34 | G. Ávalos | Independiente | Paraguay | 4.9 | 0.1* | 0.53 | **2.62** | 4.05 | — | 0.70 | 12 | 2 | 0.58 | 0.10 | 70% | 37% | 1.32 | 0.84 | — | 6.9 |
| 35 | B. Rodríguez | Club America | Uruguay | 6.2 | 0.1* | 0.39 | **2.42** | 3.75 | 4.58 | 1.67 | 13 | 7 | 0.49 | 0.26 | 75% | 43% | 1.14 | 0.78 | — | 7.3 |
| 36 | I. Díaz | Leon | Panama | 4.9 | 0.1* | 0.49 | **2.40** | 3.36 | 4.47 | 1.65 | 10 | 6 | 0.46 | 0.28 | 82% | 25% | 0.89 | 0.90 | P2 | 6.9 |
| 37 | D. Núñez | Al-Hilal Saudi FC | Uruguay | 7.5 | 1.6* | 0.31 | **2.34** | 3.97 | — | 1.40 | 6 | 4 | 0.43 | 0.29 | 88% | 43% | 1.14 | 0.78 | P2 | 6.9 |
| 38 | J. David | Juventus | Canada | 7.0 | 1.2* | 0.33 | **2.31** | 2.57 | — | 1.08 | 6 | 4 | 0.30 | 0.20 | 57% | 72% | 1.24 | 0.88 | P1 | 6.4 |
| 39 | E. Valencia | CF Pachuca | Ecuador | 5.9 | 0.7* | 0.38 | **2.26** | 3.15 | 2.74 | 5.96 | 8 | 1 | 0.52 | 0.07 | 68% | 64% | 1.01 | 0.77 | P1 FK1 | 6.8 |
| 40 | C. Wood | Nottingham Forest | New Zealand | 6.5 | 0.7* | 0.34 | **2.23** | 2.28 | — | 1.67 | 3 | 0 | 0.30 | 0.00 | 73% | 27% | 0.89 | 0.90 | P1 | 6.6 |
| 41 | B. Nygren | Celtic | Sweden | 4.9 | 0.1* | 0.44 | **2.18** | 3.73 | 1.87 | 4.84 | 16 | 5 | 0.57 | 0.18 | 76% | 19% | 0.94 | 1.02 | C1 | 7.2 |
| 42 | A. Vega | Toluca | Mexico | 5.3 | 0.1* | 0.38 | **2.04** | 3.23 | 2.33 | 2.33 | 4 | 11 | 0.24 | 0.65 | 77% | 48% | 1.01 | 0.90 | FK2 C1 | 7.6 |
| 43 | C. Adams | Torino | Scotland | 5.4 | 0.3* | 0.36 | **1.94** | 1.77 | — | 2.71 | 6 | 2 | 0.28 | 0.10 | 58% | 32% | 0.99 | 0.99 | — | 6.7 |
| 44 | Mousa Tamari | Rennes | Jordan | 5.6 | 0.1* | 0.32 | **1.79** | 1.83 | 2.12 | 3.15 | 6 | 6 | 0.24 | 0.24 | 76% | 17% | 0.60 | 0.87 | — | 6.9 |
| 45 | D. Ndoye | Nottingham Forest | Switzerland | 6.8 | 0.8* | 0.26 | **1.78** | 1.07 | — | 3.56 | 1 | 1 | 0.08 | 0.08 | 58% | 53% | 1.03 | 1.16 | — | 6.6 |
| 46 | T. Buchanan | Villarreal | Canada | 5.5 | 0.1* | 0.31 | **1.73** | 1.81 | — | 1.38 | 7 | 1 | 0.34 | 0.05 | 62% | 72% | 1.24 | 0.88 | — | 6.8 |
| 47 | A. Canobbio | Fluminense | Uruguay | 5.3 | 0.0* | 0.30 | **1.60** | 1.90 | 4.07 | 0.43 | 4 | 2 | 0.17 | 0.09 | 90% | 43% | 1.14 | 0.78 | — | 6.9 |
| 48 | C. Talbi | Sunderland | Morocco | 4.4 | 0.1* | 0.35 | **1.55** | 1.85 | 0.75 | 0.57 | 4 | 1 | 0.23 | 0.06 | 57% | 68% | 1.25 | 1.11 | — | 6.6 |
| 49 | L. Foster | Burnley | South Africa | 5.4 | 0.1* | 0.28 | **1.53** | 1.23 | — | 2.28 | 3 | 2 | 0.20 | 0.13 | 58% | 41% | 0.94 | 0.86 | P2 | 6.5 |
| 50 | J. Ayew | Leicester | Ghana | 5.3 | 0.1* | 0.28 | **1.46** | 1.87 | — | 2.25 | 6 | 3 | 0.24 | 0.12 | 57% | 25% | 0.89 | 0.90 | P1 FK1 C1 | 6.6 |
| 51 | N. Irankunda | Watford | Australia | 5.1 | 0.3* | 0.28 | **1.45** | 1.96 | — | — | 4 | 4 | 0.18 | 0.18 | 55% | 42% | 1.34 | 0.92 | P2 FK1 C1 | 6.8 |
| 52 | Sultan Mandash | Al-Hilal Saudi FC | Saudi Arabia | 4.5 | 0.0* | 0.32 | **1.45** | 1.80 | 2.92 | 4.59 | 6 | 5 | 0.40 | 0.33 | 50% | 32% | 0.99 | 0.77 | — | 7.0 |
| 53 | Hwang Ui-Jo | Alanyaspor | South Korea | 6.1 | 0.1* | 0.24 | **1.44** | 2.40 | 1.11 | — | 4 | 6 | 0.15 | 0.22 | 91% | 47% | 0.99 | 0.96 | P2 | 6.7 |
| 54 | Omar Marmoush | Manchester City | Egypt | 7.8 | 2.2* | 0.17 | **1.32** | 1.43 | — | 0.44 | 3 | 3 | 0.37 | 0.37 | 38% | 37% | 1.05 | 0.82 | P2 FK2 C2 | 6.7 |
| 55 | S. Tounekti | Celtic | Tunisia | 4.4 | 0.0* | 0.18 | **0.79** | 1.28 | 1.44 | 0.67 | 2 | 2 | 0.12 | 0.12 | 67% | 24% | 1.08 | 0.85 | — | 6.9 |
| 56 | K. Sulemana | Atalanta | Ghana | 5.1 | 0.0* | 0.13 | **0.64** | 0.70 | — | 0.52 | 2 | 1 | 0.18 | 0.09 | 36% | 25% | 0.89 | 0.90 | C2 | 6.7 |
| 57 | A. Elanga | Newcastle | Sweden | 5.8 | 0.4* | 0.10 | **0.57** | 0.58 | — | 0.44 | 0 | 1 | 0.00 | 0.07 | 44% | 19% | 0.94 | 1.02 | FK3 C3 | 6.6 |

## 6. Ready-made narrative angles

### Captaincy candidates (highest projection, nailed starters)

- **D. Malen** (Netherlands, FWD) — 9.33 xPts, 14G/2A, set-pieces: —, FixEase 1.22.
- **Lamine Yamal** (Spain, MID) — 8.67 xPts, 16G/11A, set-pieces: FK #2, Corner #1, FixEase 1.04.
- **H. Çalhanoğlu** (Turkey, MID) — 8.48 xPts, 9G/4A, set-pieces: Pen #1, FK #1, Corner #1, FixEase 1.22.
- **E. Haaland** (Norway, FWD) — 8.15 xPts, 27G/8A, set-pieces: Pen #1, FixEase 0.94.
- **Bruno Fernandes** (Portugal, MID) — 7.81 xPts, 9G/21A, set-pieces: Pen #2, FK #2, Corner #1, FixEase 0.87.
- **I. Saibari** (Morocco, MID) — 7.17 xPts, 15G/8A, set-pieces: —, FixEase 1.25.
- **L. Messi** (Argentina, FWD) — 7.16 xPts, 35G/23A, set-pieces: Pen #1, FK #1, Corner #1, FixEase 0.92.
- **A. Ueda** (Japan, FWD) — 6.90 xPts, 25G/1A, set-pieces: Pen #1, FixEase 1.34.
- **Kylian Mbappé** (France, FWD) — 6.16 xPts, 25G/5A, set-pieces: Pen #1, FixEase 0.80.
- **E. Fernández** (Argentina, MID) — 6.10 xPts, 10G/4A, set-pieces: —, FixEase 0.92.

### Best value (xPts per $m)

- **D. Malen** (Netherlands, FWD) — value 1.53 ($6.1, 9.33 xPts), 1.4% owned.
- **H. Çalhanoğlu** (Turkey, MID) — value 1.19 ($7.1, 8.48 xPts), 2.7% owned.
- **E. Martínez** (Argentina, GK) — value 1.17 ($5.0, 5.86 xPts), 22.1% owned.
- **V. van Dijk** (Netherlands, DEF) — value 1.12 ($5.5, 6.15 xPts), 20.2% owned.
- **R. Dōan** (Japan, DEF) — value 1.12 ($5.1, 5.71 xPts), 1.0% owned.
- **Z. Suzuki** (Japan, GK) — value 1.08 ($4.3, 4.63 xPts), 1.8% owned.
- **V. Coufal** (Czechia, DEF) — value 1.08 ($3.6, 3.90 xPts), 3.5% owned.
- **G. Doué** (Ivory Coast, DEF) — value 1.08 ($3.9, 4.22 xPts), 0.9% owned.
- **M. Guéhi** (England, DEF) — value 1.07 ($5.1, 5.46 xPts), 8.0% owned.
- **J. Pickford** (England, GK) — value 1.07 ($4.8, 5.13 xPts), 14.9% owned.
- **H. Kane** (England, FWD) — value 1.07 ($10.5, 11.26 xPts), 37.6% owned.
- **I. Saibari** (Morocco, MID) — value 1.05 ($6.8, 7.17 xPts), 0.5% owned.
- **C. Romero** (Argentina, DEF) — value 1.04 ($4.9, 5.09 xPts), 4.9% owned.
- **J. Ryerson** (Norway, DEF) — value 1.02 ($4.2, 4.28 xPts), 7.9% owned.
- **A. Ueda** (Japan, FWD) — value 0.99 ($7.0, 6.90 xPts), 0.7% owned.

### Biggest differentials (<5% owned, ranked by projection)

- **D. Malen** (Netherlands, FWD) — 9.33 xPts at 1.4% owned, $6.1, 14G/2A.
- **H. Çalhanoğlu** (Turkey, MID) — 8.48 xPts at 2.7% owned, $7.1, 9G/4A.
- **I. Saibari** (Morocco, MID) — 7.17 xPts at 0.5% owned, $6.8, 15G/8A.
- **A. Ueda** (Japan, FWD) — 6.90 xPts at 0.7% owned, $7.0, 25G/1A.
- **E. Fernández** (Argentina, MID) — 6.10 xPts at 3.5% owned, $7.5, 10G/4A.
- **R. Dōan** (Japan, DEF) — 5.71 xPts at 1.0% owned, $5.1, 5G/5A.
- **L. Suárez** (Colombia, FWD) — 5.58 xPts at 2.6% owned, $5.7, 28G/6A.
- **O. Kökçü** (Turkey, MID) — 5.22 xPts at 0.3% owned, $6.0, 8G/8A.
- **C. Romero** (Argentina, DEF) — 5.09 xPts at 4.9% owned, $4.9, 4G/1A.
- **S. Mané** (Senegal, MID) — 4.99 xPts at 2.0% owned, $7.6, 10G/6A.
- **Son Heung-Min** (South Korea, FWD) — 4.85 xPts at 2.1% owned, $7.4, 12G/3A.
- **Casemiro** (Brazil, MID) — 4.82 xPts at 2.2% owned, $6.3, 9G/2A.
- **P. Schick** (Czechia, FWD) — 4.80 xPts at 0.8% owned, $7.3, 16G/3A.
- **Bruno Guimarães** (Brazil, MID) — 4.73 xPts at 1.9% owned, $6.8, 9G/5A.
- **G. Xhaka** (Switzerland, MID) — 4.68 xPts at 4.9% owned, $6.2, 1G/6A.
- **Nico Williams** (Spain, MID) — 4.65 xPts at 3.9% owned, $7.8, 6G/3A.
- **Z. Suzuki** (Japan, GK) — 4.63 xPts at 1.8% owned, $4.3, 0G/0A.
- **D. Doué** (France, MID) — 4.49 xPts at 3.3% owned, $7.5, 7G/4A.
- **L. Modrić** (Croatia, MID) — 4.40 xPts at 2.5% owned, $6.2, 2G/3A.
- **R. Vargas** (Switzerland, MID) — 4.36 xPts at 0.5% owned, $6.8, 3G/6A.

### Set-piece kings (primary penalty takers)

- **H. Kane** (England, FWD) — Pen #1; 11.26 xPts.
- **H. Çalhanoğlu** (Turkey, MID) — Pen #1, FK #1, Corner #1; 8.48 xPts.
- **E. Haaland** (Norway, FWD) — Pen #1; 8.15 xPts.
- **Raphinha** (Brazil, MID) — Pen #1, FK #1, Corner #1; 8.02 xPts.
- **L. Messi** (Argentina, FWD) — Pen #1, FK #1, Corner #1; 7.16 xPts.
- **A. Ueda** (Japan, FWD) — Pen #1; 6.90 xPts.
- **Kylian Mbappé** (France, FWD) — Pen #1; 6.16 xPts.
- **K. De Bruyne** (Belgium, MID) — Pen #1, FK #1, Corner #1; 5.75 xPts.
- **Mikel Oyarzabal** (Spain, FWD) — Pen #1; 5.64 xPts.
- **Mohamed Salah** (Egypt, MID) — Pen #1, FK #1, Corner #1; 5.57 xPts.
- **S. Mané** (Senegal, MID) — Pen #1, FK #1; 4.99 xPts.
- **Son Heung-Min** (South Korea, FWD) — Pen #1, FK #1, Corner #1; 4.85 xPts.
- **P. Schick** (Czechia, FWD) — Pen #1; 4.80 xPts.
- **Cristiano Ronaldo** (Portugal, FWD) — Pen #1, FK #1; 4.72 xPts.
- **G. Xhaka** (Switzerland, MID) — Pen #1, FK #2; 4.68 xPts.
- **F. Valverde** (Uruguay, MID) — Pen #1, FK #1, Corner #2; 4.50 xPts.
- **L. Modrić** (Croatia, MID) — Pen #1, FK #1, Corner #1; 4.40 xPts.
- **J. Enciso** (Paraguay, MID) — Pen #1, FK #2, Corner #2; 4.34 xPts.
- **S. McTominay** (Scotland, MID) — Pen #1; 4.32 xPts.
- **C. Pulišić** (USA, MID) — Pen #1, FK #1, Corner #1; 4.29 xPts.

### Template players (most-owned)

- **Kylian Mbappé** (France, FWD) — 50.5% owned, 6.16 xPts, $10.5.
- **Bruno Fernandes** (Portugal, MID) — 50.3% owned, 7.81 xPts, $8.5.
- **Lamine Yamal** (Spain, MID) — 45.3% owned, 8.67 xPts, $10.0.
- **Nuno Mendes** (Portugal, DEF) — 43.1% owned, 3.02 xPts, $5.8.
- **H. Kane** (England, FWD) — 37.6% owned, 11.26 xPts, $10.5.
- **E. Haaland** (Norway, FWD) — 33.5% owned, 8.15 xPts, $10.5.
- **J. Kimmich** (Germany, DEF) — 30.3% owned, 3.44 xPts, $5.5.
- **Marc Cucurella** (Spain, DEF) — 23.6% owned, 3.66 xPts, $5.1.
- **Gabriel Magalhães** (Brazil, DEF) — 23.1% owned, 2.93 xPts, $5.5.
- **F. Wirtz** (Germany, MID) — 22.9% owned, 3.15 xPts, $7.5.
- **M. Olise** (France, MID) — 22.9% owned, 5.96 xPts, $9.5.
- **E. Martínez** (Argentina, GK) — 22.1% owned, 5.86 xPts, $5.0.

### Stars taxed by a weak national side (good player, weaker team)

*High individual club output but a sub-average team-strength factor — the model expects them to find chances harder at the World Cup.*

- **E. Shomurodov** (Uzbekistan, FWD) — 22G/5A at club, but TeamStr 0.90; projects 3.75 xPts.
- **A. Semenyo** (Ghana, FWD) — 17G/4A at club, but TeamStr 0.90; projects 3.54 xPts.
- **B. Rodríguez** (Uruguay, FWD) — 13G/7A at club, but TeamStr 0.78; projects 2.42 xPts.
- **G. Ávalos** (Paraguay, FWD) — 12G/2A at club, but TeamStr 0.84; projects 2.62 xPts.
- **I. Díaz** (Panama, FWD) — 10G/6A at club, but TeamStr 0.90; projects 2.40 xPts.
- **R. Jiménez** (Mexico, FWD) — 9G/3A at club, but TeamStr 0.90; projects 3.00 xPts.
- **E. Valencia** (Ecuador, FWD) — 8G/1A at club, but TeamStr 0.77; projects 2.26 xPts.
- **Salem Al Dawsari** (Saudi Arabia, MID) — 8G/8A at club, but TeamStr 0.77; projects 2.70 xPts.

## 7. Caveats (so articles don't over-claim)

- **It's a projection, not a prophecy** — an expected value built from rates and probabilities, blind to tactical role changes, injuries declared after the data pull, or a manager's whim.

- **No xG/xA** — the underlying feed lacks expected-goals data, so raw goals/assists are used; a player on a hot/cold finishing run can be over/under-stated.

- **FIFA world-ranking points are approximate** (hardcoded, late-2025) and the league-strength and team-strength coefficients are judgement calls — directionally sound, not exact.

- **Clean-sheet model ignores specific line-ups and home advantage** (USA/MEX/CAN hosts).

- **Start% comes from club minutes**, a proxy for international nailed-on status.


*Generated by `build_writer_doc.py` over 328 players.*
