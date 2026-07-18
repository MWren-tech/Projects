# FIFA World Cup 2026 Fantasy — official rules (source of truth)

> Mirrored in code by `wc_scout/scoring.py` constants. If the official rules change, update both. Verified from play.fifa.com/fantasy/help/guidelines.

## Squad & budget
- **15 players**: 2 GK, 5 DEF, 5 MID, 3 FWD.
- **Budget $100m** (rises **+$5m to $105m** from the Round of 32).
- **Max per nation:** Group & R32 = 3 · R16 = 4 · QF = 5 · SF = 6 · Final = 8.
- **Formations (XI):** 4-4-2, 4-3-3, 4-5-1, 3-4-3, 3-5-2, 5-4-1, 5-3-2 (always 1 GK; DEF 3–5, MID 3–5, FWD 1–3).

## Captain / vice
- Captain scores **double**. If the captain plays 0 minutes, the **vice** doubles instead (only if no manual change was made during the live round).

## Substitutions
- Bench is ordered 1–3 (outfield) + GK. **Auto-subs** replace DNP starters at round end if you've made no manual change, keeping a valid formation.

## Transfers
| Stage | Free transfers |
|---|---|
| Pre-tournament | Unlimited |
| Before MD2 | 2 |
| Before MD3 | 2 |
| Before R32 | Unlimited |
| Before R16 | 4 |
| Before QF | 4 |
| Before SF | 5 |
| Before Final | 6 |
- **One unused transfer carries over** within the group stage.
- Each transfer **beyond the allocation costs −3 points**.

## Boosters (one-time each, one per round, can't combine)
- **Wildcard** — unlimited transfers for one round (not usable MD1 or R32).
- **12th Man** — a 13th player scores for one round (any player, no budget/cap; can't be subbed/captained/transferred).
- **Maximum Captain** — doubles whichever starter scores most that round (auto-captain).
- **Qualification** — R32+: +2 per starter who advances (min 1'); captain's +2 not doubled.
- **Mystery** — revealed at R32; used once in a knockout round.

## Scoring
**All players:** appearance **+1** (any minutes) **+1** more for 60'+ · assist **+3** · yellow **−1** · red **−2** · own goal **−2** · penalty won **+2** · penalty conceded **−1**.

**Goalkeeper:** clean sheet (60'+) **+5** · goal **+9** · penalty save **+3** · every 3 saves **+1** · each goal conceded after the first **−1**.
**Defender:** clean sheet (60'+) **+5** · goal **+7** · each goal conceded after the first **−1**.
**Midfielder:** clean sheet (60'+) **+1** · goal **+6** · every 3 tackles **+1** · every 2 chances created **+1**.
**Forward:** goal **+5** · every 2 shots on target **+1**.

**Bonuses:** goal from a direct free-kick **+1** · **Scouting bonus +2** — a player who scores **>4 pts in a match** AND is in **<5%** of squads.

## Notes for the model
- The **scouting bonus** is the one bonus we can model from ownership we already have → priced into projections for <5%-owned players (see [projection-model.md](projection-model.md)).
- The **FK-goal bonus** isn't detectable from our stats feeds; not modelled.
- "Points so far" displayed in the app uses **FIFA's own `totalPoints`** (authoritative); our stat breakdown is indicative where providers disagree.
