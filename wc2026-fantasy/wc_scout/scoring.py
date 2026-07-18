"""
Fantasy scoring layer for WC2026 Fantasy Scout.

Two jobs:
1. score_actual(...)  -> points a player WOULD have earned in a real match,
   given their API-Football stat line, under the WC2026 ruleset. Useful for
   backtesting form from qualifiers / friendlies / WC2022 data.
2. expected_points(...) -> a forward-looking xPts estimate built from
   per-match rate stats plus fixture inputs (clean-sheet prob, expected goals).

The ruleset here is transcribed from the project system prompt. If the
official game tweaks anything, change it in ONE place: SCORING below.
"""

from __future__ import annotations

from dataclasses import dataclass

POSITIONS = ("GK", "DEF", "MID", "FWD")

# --- Ruleset constants (single source of truth) --------------------------

APPEARANCE = 1
ASSIST = 3
YELLOW = -1
RED = -2
OWN_GOAL = -2
WIN_PEN = 2
CONCEDE_PEN = -1
FK_GOAL_BONUS = 1  # direct free-kick goal

# Set-piece threat model (used for WC national-team takers; see set_piece_takers.py)
TEAM_PENS_PER_MATCH = 0.18      # assumed penalties awarded to a team per match
CORNER_ASSIST_PER_MATCH = 0.06  # extra expected assists for the primary corner taker
FK_GOAL_PER_MATCH = 0.04        # expected direct free-kick goals for the primary FK taker

GOAL_POINTS = {"GK": 9, "DEF": 7, "MID": 6, "FWD": 5}
CLEAN_SHEET = {"GK": 5, "DEF": 5, "MID": 1, "FWD": 0}

# Per-position incremental rules
GK_PEN_SAVE = 3
GK_SAVES_PER_POINT = 3          # every 3 saves -> +1
CONCEDE_AFTER_FIRST = -1        # each goal conceded after the first (GK & DEF)
GK_CONCEDE_AFTER_FIRST = CONCEDE_AFTER_FIRST
DEF_CONCEDE_AFTER_FIRST = CONCEDE_AFTER_FIRST
MID_TACKLES_PER_POINT = 3       # every 3 tackles -> +1
MID_CHANCES_PER_POINT = 2       # every 2 chances created -> +1
FWD_SOT_PER_POINT = 2           # every 2 shots on target -> +1

SCOUTING_BONUS = 2              # >4 pts in a match AND <5% owned
SCOUTING_PTS_THRESHOLD = 4
SCOUTING_OWNERSHIP_THRESHOLD = 5.0  # percent


def _norm_pos(pos: str) -> str:
    """
    Map API-Football position strings to our four buckets. Idempotent: passing
    an already-normalised "GK"/"DEF"/"MID"/"FWD" returns it unchanged (so it's
    safe to re-normalise a PlayerForm.position without silently demoting GKs/FWDs
    to MID).
    """
    p = (pos or "").strip().lower()
    if p in ("gk", "g") or p.startswith("goal"):
        return "GK"
    if p in ("def", "d") or p.startswith("def"):
        return "DEF"
    if p in ("fwd", "fw", "f") or p.startswith("att") or p.startswith("for"):
        return "FWD"
    if p in ("mid", "m") or p.startswith("mid"):
        return "MID"
    return "MID"  # safe default


# Public alias — shared modules import this name.
norm_pos = _norm_pos


@dataclass
class StatLine:
    """A single match's stats. Fields default to 0/None so partial data works."""
    position: str
    minutes: int = 0
    goals: int = 0
    assists: int = 0
    goals_conceded: int = 0
    saves: int = 0
    tackles: int = 0
    chances_created: int = 0   # key passes
    shots_on_target: int = 0
    yellow: int = 0
    red: int = 0
    own_goals: int = 0
    pen_won: int = 0
    pen_conceded: int = 0
    pen_saved: int = 0
    fk_goals: int = 0
    clean_sheet: bool = False


def score_actual(s: StatLine) -> float:
    """Points this stat line earns under the WC2026 ruleset (no captaincy)."""
    pos = _norm_pos(s.position)
    pts = 0.0

    if s.minutes > 0:
        pts += APPEARANCE

    pts += GOAL_POINTS[pos] * s.goals
    pts += ASSIST * s.assists
    pts += YELLOW * s.yellow
    pts += RED * s.red
    pts += OWN_GOAL * s.own_goals
    pts += WIN_PEN * s.pen_won
    pts += CONCEDE_PEN * s.pen_conceded
    pts += FK_GOAL_BONUS * s.fk_goals

    # Clean sheet — GK/DEF need 60+ mins to count; the StatLine.clean_sheet
    # flag should already encode "kept a clean sheet while on the pitch".
    if s.clean_sheet and s.minutes >= 60:
        pts += CLEAN_SHEET[pos]
    elif s.clean_sheet and pos == "MID":
        pts += CLEAN_SHEET["MID"]

    if pos == "GK":
        pts += GK_PEN_SAVE * s.pen_saved
        pts += s.saves // GK_SAVES_PER_POINT
        pts += GK_CONCEDE_AFTER_FIRST * max(0, s.goals_conceded - 1)
    elif pos == "DEF":
        pts += DEF_CONCEDE_AFTER_FIRST * max(0, s.goals_conceded - 1)
    elif pos == "MID":
        pts += s.tackles // MID_TACKLES_PER_POINT
        pts += s.chances_created // MID_CHANCES_PER_POINT
    elif pos == "FWD":
        pts += s.shots_on_target // FWD_SOT_PER_POINT

    return pts


def apply_scouting_bonus(match_pts: float, ownership_pct: float | None) -> float:
    """Add the differential bonus if it qualifies."""
    if (
        ownership_pct is not None
        and match_pts > SCOUTING_PTS_THRESHOLD
        and ownership_pct < SCOUTING_OWNERSHIP_THRESHOLD
    ):
        return match_pts + SCOUTING_BONUS
    return match_pts


# --- Forward-looking expected points --------------------------------------

@dataclass
class FixtureContext:
    """Inputs for one upcoming match, ideally derived from odds/predictions."""
    clean_sheet_prob: float = 0.0          # P(team keeps clean sheet)
    expected_goals_against: float = 1.1    # team xGA this match (for GK/DEF concede penalty)
    team_expected_goals: float = 1.2       # team xG this match
    start_prob: float = 0.8                # P(player is in the XI)
    p_sixty: float = 0.8                   # P(player reaches 60' — gates clean sheet)
    attack_multiplier: float = 1.0         # fixture difficulty for attackers (opp defence)
    team_attack: float = 1.0               # own team's attacking quality (lone-star penalty)


def expected_points(
    *,
    position: str,
    fixture: FixtureContext,
    # per-90 rates (from recent form):
    goals_per90: float = 0.0,
    assists_per90: float = 0.0,
    shots_on_target_per90: float = 0.0,
    chances_per90: float = 0.0,
    tackles_per90: float = 0.0,
    saves_per90: float = 0.0,
    pen_won_per90: float = 0.0,
    pen_conceded_per90: float = 0.0,
    pen_saved_per90: float = 0.0,
    yellow_per90: float = 0.0,
    red_per90: float = 0.0,
    pen_duty: bool = False,
    pen_share: float = 0.0,
    fk_taker: bool = False,
    corner_taker: bool = False,
    ownership_pct: float | None = None,
) -> float:
    """
    A transparent, fully-itemised xPts estimate for one match. Every component
    the FIFA WC Fantasy game scores is modelled as an expectation. Rates are
    per-90; we scale by the player's probability of being on the pitch. Still
    explainable rather than a black box, and directly comparable across players.
    """
    pos = _norm_pos(position)
    p_play = fixture.start_prob          # in the XI -> earns the rate stats
    p_60 = fixture.p_sixty               # gates clean-sheet points
    # Effective attacking multiplier = opponent fixture difficulty x own-team attacking
    # quality. The latter discounts a great player stuck in a weak side (fewer chances).
    am = fixture.attack_multiplier * fixture.team_attack
    xp = 0.0

    # Appearance: +1 for any minutes, +1 MORE for reaching 60' (rules give both).
    # A nailed 60'+ starter earns ~2; a likely cameo earns ~1.
    xp += APPEARANCE * p_play + APPEARANCE * p_60

    # Goal involvement (scaled by opponent defensive difficulty)
    xp += GOAL_POINTS[pos] * goals_per90 * am * p_play
    xp += ASSIST * assists_per90 * am * p_play

    # Penalty events (win/concede are all-player; pen save is GK only)
    xp += WIN_PEN * pen_won_per90 * p_play
    xp += CONCEDE_PEN * pen_conceded_per90 * p_play

    # Discipline downside (expected card cost)
    xp += YELLOW * yellow_per90 * p_play
    xp += RED * red_per90 * p_play

    # Clean sheet expectation (GK/DEF need 60'; MID gets a token point)
    if pos in ("GK", "DEF"):
        xp += CLEAN_SHEET[pos] * fixture.clean_sheet_prob * p_60
        # Goals-conceded penalty: -1 per goal beyond the first (expected).
        xp += CONCEDE_AFTER_FIRST * max(0.0, fixture.expected_goals_against - 1.0) * p_60
    elif pos == "MID":
        xp += CLEAN_SHEET["MID"] * fixture.clean_sheet_prob * p_60

    # Position-specific incremental scoring (expected fractional points)
    if pos == "GK":
        xp += GK_PEN_SAVE * pen_saved_per90 * p_play
        xp += (saves_per90 / GK_SAVES_PER_POINT) * p_play
    elif pos == "MID":
        xp += (tackles_per90 / MID_TACKLES_PER_POINT) * p_play
        xp += (chances_per90 / MID_CHANCES_PER_POINT) * am * p_play
    elif pos == "FWD":
        xp += (shots_on_target_per90 / FWD_SOT_PER_POINT) * am * p_play

    # Set-piece threat. pen_share is the expected fraction of the team's penalties
    # this player takes (national-team role for WC). Fall back to a default share
    # if only the legacy pen_duty bool is given.
    if pen_share <= 0 and pen_duty:
        pen_share = 0.80
    if pen_share > 0:
        xp += GOAL_POINTS[pos] * TEAM_PENS_PER_MATCH * pen_share * am * p_play
    if fk_taker:  # primary direct free-kick taker: goal pts + FK bonus, rarely
        xp += (GOAL_POINTS[pos] + FK_GOAL_BONUS) * FK_GOAL_PER_MATCH * am * p_play
    if corner_taker:  # primary corner taker: extra expected assists
        xp += ASSIST * CORNER_ASSIST_PER_MATCH * am * p_play

    return round(xp, 2)


def value_score(xpts: float, price: float) -> float:
    """xPts per $m. Higher is better. Guards against div-by-zero."""
    return round(xpts / price, 3) if price else 0.0
