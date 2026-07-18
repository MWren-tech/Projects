"""
FIFA world-ranking points for the 48 WC2026 nations (approx., late-2025 rankings).

Used as one half of the team-attack factor (blended 50/50 with each nation's recent
goals-for rate) so a great player in a weak national side is discounted for scoring
— he gets fewer chances than the same player in a strong side.

These are approximate and easy to edit; only the relative ordering matters much.
"""

from __future__ import annotations
from statistics import mean

# nation -> approx FIFA ranking points (late 2025)
FIFA_POINTS: dict[str, int] = {
    "Argentina": 1870, "Spain": 1867, "France": 1862, "England": 1820,
    "Portugal": 1772, "Brazil": 1758, "Netherlands": 1754, "Belgium": 1736,
    "Croatia": 1716, "Morocco": 1710, "Germany": 1709, "Colombia": 1700,
    "Uruguay": 1675, "Japan": 1652, "Senegal": 1652, "Mexico": 1650,
    "USA": 1648, "Switzerland": 1648, "Iran": 1638, "Austria": 1576,
    "South Korea": 1572, "Ecuador": 1571, "Turkey": 1560, "Norway": 1532,
    "Sweden": 1530, "Canada": 1530, "Egypt": 1518, "Algeria": 1507,
    "Australia": 1503, "Scotland": 1497, "Tunisia": 1499, "Ivory Coast": 1492,
    "Czechia": 1491, "Bosnia and Herzegovina": 1485, "Paraguay": 1483,
    "DR Congo": 1462, "Ghana": 1453, "Panama": 1452, "Qatar": 1438,
    "Uzbekistan": 1437, "South Africa": 1431, "Saudi Arabia": 1418,
    "Iraq": 1404, "Jordan": 1389, "Cape Verde": 1391, "Curacao": 1377,
    "Haiti": 1320, "New Zealand": 1318,
}


def fifa_strength() -> dict[str, float]:
    """nation -> FIFA-points strength, normalised so the 48-team mean is ~1.0."""
    avg = mean(FIFA_POINTS.values())
    return {n: p / avg for n, p in FIFA_POINTS.items()}
