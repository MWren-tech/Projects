"""
Unit tests for the scoring layer — the single source of truth for the ruleset.
These pin the WC2026 point values so an accidental edit to scoring.py fails loudly.

Run:  pytest            (from wc_scout/)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scoring import (  # noqa: E402
    StatLine, FixtureContext,
    score_actual, expected_points, apply_scouting_bonus, value_score, norm_pos,
)


# --- norm_pos: idempotent + maps provider strings --------------------------

def test_norm_pos_idempotent():
    for p in ("GK", "DEF", "MID", "FWD"):
        assert norm_pos(p) == p

def test_norm_pos_maps_provider_strings():
    assert norm_pos("Goalkeeper") == "GK"
    assert norm_pos("Defender") == "DEF"
    assert norm_pos("Midfielder") == "MID"
    assert norm_pos("Attacker") == "FWD"

def test_norm_pos_unknown_defaults_to_mid():
    assert norm_pos("") == "MID"
    assert norm_pos("coach") == "MID"


# --- score_actual: exact point totals under the ruleset --------------------

def test_forward_goal():
    # appearance (1) + FWD goal (5)
    assert score_actual(StatLine("FWD", minutes=90, goals=1)) == 6

def test_defender_clean_sheet():
    # appearance (1) + DEF clean sheet (5), needs 60'+
    assert score_actual(StatLine("DEF", minutes=90, clean_sheet=True)) == 6

def test_clean_sheet_needs_sixty_minutes():
    # under 60' a DEF gets no clean-sheet points
    assert score_actual(StatLine("DEF", minutes=45, clean_sheet=True)) == 1

def test_keeper_saves_and_single_concede():
    # appearance (1) + 6 saves // 3 = 2 + no penalty for the first goal conceded
    assert score_actual(StatLine("GK", minutes=90, saves=6, goals_conceded=1)) == 3

def test_keeper_concede_penalty_after_first():
    # appearance (1) - 1 for each goal beyond the first (3 conceded -> -2)
    assert score_actual(StatLine("GK", minutes=90, goals_conceded=3)) == -1

def test_midfielder_goal_tackles_chances():
    # 1 + MID goal (6) + 3 tackles//3 (1) + 2 chances//2 (1)
    assert score_actual(StatLine("MID", minutes=90, goals=1, tackles=3, chances_created=2)) == 9

def test_yellow_card_costs_a_point():
    assert score_actual(StatLine("FWD", minutes=90, yellow=1)) == 0


# --- expected_points: forward-looking xPts ---------------------------------

def _nailed(**kw):
    return FixtureContext(start_prob=1.0, p_sixty=1.0, **kw)

def test_xp_baseline_is_two_appearance_points():
    # a nailed starter with no output still earns the two appearance points
    assert expected_points(position="FWD", fixture=_nailed()) == 2.0

def test_xp_keeper_clean_sheet():
    # 2 appearance + 5 clean sheet, zero concede penalty at xGA = 1.0
    xp = expected_points(position="GK", fixture=_nailed(clean_sheet_prob=1.0, expected_goals_against=1.0))
    assert xp == 7.0

def test_xp_forward_goal_rate_adds_value():
    xp = expected_points(position="FWD", goals_per90=1.0, fixture=_nailed())
    assert xp == 7.0  # 2 baseline + 5 (one FWD goal at multiplier 1.0)

def test_xp_scales_down_with_start_probability():
    nailed = expected_points(position="FWD", goals_per90=1.0, fixture=FixtureContext(start_prob=1.0, p_sixty=1.0))
    fringe = expected_points(position="FWD", goals_per90=1.0, fixture=FixtureContext(start_prob=0.3, p_sixty=0.2))
    assert fringe < nailed


# --- helpers ---------------------------------------------------------------

def test_scouting_bonus_only_for_low_owned_hauls():
    assert apply_scouting_bonus(6, ownership_pct=3.0) == 8   # >4 pts and <5% owned
    assert apply_scouting_bonus(6, ownership_pct=10.0) == 6  # too widely owned
    assert apply_scouting_bonus(4, ownership_pct=3.0) == 4   # not a haul
    assert apply_scouting_bonus(6, ownership_pct=None) == 6  # unknown ownership

def test_value_score_guards_zero_price():
    assert value_score(10.0, 5.0) == 2.0
    assert value_score(10.0, 0.0) == 0.0
