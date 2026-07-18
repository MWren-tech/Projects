"""
Shared player-form extraction for the WC2026 Fantasy tools.

One place that turns an API-Football `/players` entry (player + statistics[])
into a rich `PlayerForm` carrying every stat the FIFA World Cup Fantasy game
actually scores, plus per-90 rates and derived availability signals.

Both scout.py and wc_picker.py import from here so they never drift apart and
both feed the SAME scoring layer (scoring.py).

API-Football field-name quirks worth knowing (transcribed as-is):
  games.appearences   (misspelled "appearances")
  penalty.commited    (misspelled "committed" — this is penalties CONCEDED)
  cards.yellowred     (second yellow -> red)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from scoring import FixtureContext, expected_points, norm_pos


@dataclass
class PlayerForm:
    player_id: int
    name: str
    team: str
    team_id: int
    position: str            # normalised GK/DEF/MID/FWD

    # raw season totals
    appearances: int
    lineups: int
    minutes: int
    rating: float

    goals: int
    assists: int
    saves: int
    goals_conceded: int
    shots_total: int
    shots_on: int
    key_passes: int
    tackles: int
    pen_won: int
    pen_conceded: int
    pen_saved: int
    pen_scored: int          # penalties converted (subset of goals) -> taker signal
    pen_missed: int
    yellows: int
    reds: int
    fouls_committed: int

    # derived availability
    start_prob: float        # P(starts) from lineups / appearances
    p_sixty: float           # P(plays 60+), drives clean-sheet eligibility

    # per-90 rates (computed in __post_init__)
    per90: dict = field(default_factory=dict)

    nationality: str = ""    # API-Football player.nationality (for WC nation mapping)

    # national-team set-piece overlay (None until apply_set_pieces; WC only)
    sp_pen_rank: int | None = None
    sp_fk_rank: int | None = None
    sp_corner_rank: int | None = None
    recent_xp: float | None = None
    recent_games: int | None = None

    def __post_init__(self):
        nineties = (self.minutes / 90.0) or 1e-9
        for name, total in (
            ("goals", self.goals),
            ("assists", self.assists),
            ("saves", self.saves),
            ("goals_conceded", self.goals_conceded),
            ("shots_total", self.shots_total),
            ("shots_on", self.shots_on),
            ("key_passes", self.key_passes),
            ("tackles", self.tackles),
            ("pen_won", self.pen_won),
            ("pen_conceded", self.pen_conceded),
            ("pen_saved", self.pen_saved),
            ("yellows", self.yellows),
            ("reds", self.reds),
            ("fouls_committed", self.fouls_committed),
        ):
            self.per90[name] = round(total / nineties, 3)

    @property
    def pen_attempts(self) -> int:
        return self.pen_scored + self.pen_missed

    @property
    def pen_taker(self) -> bool:
        """Designated taker heuristic: has actually attempted 2+ penalties."""
        return self.pen_attempts >= 2


def _num(d: dict | None, key: str) -> int:
    """Safe int pull from a possibly-None nested dict; None -> 0."""
    if not d:
        return 0
    return d.get(key) or 0


def extract_player_form(entry: dict) -> PlayerForm | None:
    """Collapse a /players response item into a PlayerForm, or None if no data."""
    p = entry.get("player", {}) or {}
    stats = entry.get("statistics", []) or []
    if not stats:
        return None

    appearances = lineups = minutes = 0
    goals = assists = saves = conceded = shots_total = shots_on = key_passes = tackles = 0
    pen_won = pen_conceded = pen_saved = pen_scored = pen_missed = yellows = reds = fouls = 0
    position = ""
    team = ""
    team_id = 0
    ratings: list[float] = []

    for s in stats:
        g = s.get("games", {}) or {}
        appearances += _num(g, "appearences")
        lineups += _num(g, "lineups")
        minutes += _num(g, "minutes")
        position = g.get("position") or position
        if g.get("rating"):
            try:
                ratings.append(float(g["rating"]))
            except (TypeError, ValueError):
                pass
        t = s.get("team", {}) or {}
        team = t.get("name") or team
        team_id = t.get("id") or team_id

        goals += _num(s.get("goals"), "total")
        assists += _num(s.get("goals"), "assists")
        saves += _num(s.get("goals"), "saves")
        conceded += _num(s.get("goals"), "conceded")
        shots_total += _num(s.get("shots"), "total")
        shots_on += _num(s.get("shots"), "on")
        key_passes += _num(s.get("passes"), "key")
        tackles += _num(s.get("tackles"), "total")
        pen_won += _num(s.get("penalty"), "won")
        pen_conceded += _num(s.get("penalty"), "commited")  # API spelling
        pen_saved += _num(s.get("penalty"), "saved")
        pen_scored += _num(s.get("penalty"), "scored")
        pen_missed += _num(s.get("penalty"), "missed")
        yellows += _num(s.get("cards"), "yellow") + _num(s.get("cards"), "yellowred")
        reds += _num(s.get("cards"), "red")
        fouls += _num(s.get("fouls"), "committed")

    if appearances == 0 and minutes == 0:
        return None

    start_prob, p_sixty = _availability(appearances, lineups, minutes)

    return PlayerForm(
        player_id=p.get("id"),
        name=p.get("name", "?"),
        team=team,
        team_id=team_id,
        position=norm_pos(position),
        nationality=p.get("nationality") or "",
        appearances=appearances,
        lineups=lineups,
        minutes=minutes,
        rating=round(sum(ratings) / len(ratings), 2) if ratings else 0.0,
        goals=goals,
        assists=assists,
        saves=saves,
        goals_conceded=conceded,
        shots_total=shots_total,
        shots_on=shots_on,
        key_passes=key_passes,
        tackles=tackles,
        pen_won=pen_won,
        pen_conceded=pen_conceded,
        pen_saved=pen_saved,
        pen_scored=pen_scored,
        pen_missed=pen_missed,
        yellows=yellows,
        reds=reds,
        fouls_committed=fouls,
        start_prob=start_prob,
        p_sixty=p_sixty,
    )


def _availability(appearances: int, lineups: int, minutes: int) -> tuple[float, float]:
    """
    Estimate P(start) and P(60+ mins) — the single biggest fantasy lever.
    Nailed-on starters (lineups ≈ appearances, high mins/app) approach ~0.95.
    """
    if appearances <= 0:
        return 0.5, 0.4
    start = lineups / appearances
    mins_per_app = minutes / appearances
    start_prob = max(0.1, min(0.97, start))
    # If they average a full match they almost always clear 60; scale down for subs.
    p_sixty = max(0.1, min(0.95, start_prob * min(1.0, mins_per_app / 75.0)))
    return round(start_prob, 3), round(p_sixty, 3)


def flat_row(form: PlayerForm) -> dict:
    """Flatten a PlayerForm (including per-90 rates) into a CSV-friendly dict."""
    row = {
        "player_id": form.player_id,
        "name": form.name,
        "team": form.team,
        "team_id": form.team_id,
        "position": form.position,
        "appearances": form.appearances,
        "lineups": form.lineups,
        "minutes": form.minutes,
        "rating": form.rating,
        "start_prob": form.start_prob,
        "p_sixty": form.p_sixty,
        "goals": form.goals,
        "assists": form.assists,
        "saves": form.saves,
        "goals_conceded": form.goals_conceded,
        "shots_total": form.shots_total,
        "shots_on": form.shots_on,
        "key_passes": form.key_passes,
        "tackles": form.tackles,
        "pen_won": form.pen_won,
        "pen_conceded": form.pen_conceded,
        "pen_saved": form.pen_saved,
        "pen_scored": form.pen_scored,
        "pen_missed": form.pen_missed,
        "pen_taker": form.pen_taker,
        "sp_pen_rank": form.sp_pen_rank,
        "sp_fk_rank": form.sp_fk_rank,
        "sp_corner_rank": form.sp_corner_rank,
        "yellows": form.yellows,
        "reds": form.reds,
        "fouls_committed": form.fouls_committed,
    }
    row.update({f"{k}_per90": v for k, v in form.per90.items()})
    return row


def form_to_xpts(form: PlayerForm, ctx: FixtureContext) -> float:
    """
    Bridge: feed a PlayerForm's per-90 rates into the scoring layer. If national
    set-piece ranks have been overlaid (apply_set_pieces, WC only), they drive the
    penalty/FK/corner threat; otherwise we fall back to the club pen_taker flag.
    """
    from set_piece_takers import PEN_SHARE_BY_RANK

    r = form.per90
    if form.sp_pen_rank is not None or form.sp_fk_rank is not None or form.sp_corner_rank is not None:
        pen_share = PEN_SHARE_BY_RANK.get(form.sp_pen_rank, 0.0)
        fk_taker = form.sp_fk_rank == 1
        corner_taker = form.sp_corner_rank == 1
        pen_duty = False
    else:
        pen_share = 0.0
        fk_taker = corner_taker = False
        pen_duty = form.pen_taker

    return expected_points(
        position=form.position,
        fixture=ctx,
        goals_per90=r["goals"],
        assists_per90=r["assists"],
        shots_on_target_per90=r["shots_on"],
        chances_per90=r["key_passes"],
        tackles_per90=r["tackles"],
        saves_per90=r["saves"],
        pen_won_per90=r["pen_won"],
        pen_conceded_per90=r["pen_conceded"],
        pen_saved_per90=r["pen_saved"],
        yellow_per90=r["yellows"],
        red_per90=r["reds"],
        pen_duty=pen_duty,
        pen_share=pen_share,
        fk_taker=fk_taker,
        corner_taker=corner_taker,
    )
