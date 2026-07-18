"""
National-team set-piece takers for the 2026 World Cup — penalties, free-kicks,
and corners for all 48 teams.

Source: allaboutfpl.com "FIFA World Cup 2026 penalty and set-piece takers of all
48 teams" (June 2026). Order matters: the **leftmost name is the primary taker**;
those to the right are the next in line if the primary is off the pitch.

Why this exists: a player's CLUB penalty record (what player_form reads from
API-Football) is NOT his national-team set-piece role. For the World Cup, THIS
list is the real penalty/free-kick threat — e.g. South Korea's primary penalty
AND free-kick taker is Son, not Lee Kang-In. Apply this as an overlay on top of
club form for league=1 (WC2026) players.

Names are kept verbatim from the source (short surnames, some misspellings); the
matcher is accent- and substring-tolerant so it links to API-Football names.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

# nation -> ordered lists (index 0 = primary taker)
TAKERS: dict[str, dict[str, list[str]]] = {
    "Mexico":      {"penalty": ["Jimenez"], "freekick": ["Jimenez", "Vega"], "corner": ["Vega", "Alvarado", "Gutierrez"]},
    "South Africa":{"penalty": ["Appollis", "Foster"], "freekick": ["Modiba", "Appollis", "Mokoena"], "corner": ["Appollis", "Mokoena", "Modiba", "Mofokeng"]},
    "South Korea": {"penalty": ["Son", "Hwang"], "freekick": ["Son", "Lee Kang-In"], "corner": ["Son", "Lee Kang-In"]},
    "Czechia":     {"penalty": ["Schick", "Soucek"], "freekick": ["Hlozek", "Sulc", "Provod"], "corner": ["Coufal", "Sulc", "Provod"]},
    "Canada":      {"penalty": ["David"], "freekick": ["Davies", "Eustaquio"], "corner": ["Choniere", "Davies", "Eustaquio"]},
    "Bosnia and Herzegovina": {"penalty": ["Dzeko", "Alajbegovic", "Demirovic"], "freekick": ["Alajbegovic", "Tahirovic", "Bajraktarevic"], "corner": ["Alajbegovic", "Dedic", "Bajraktarevic"]},
    "Qatar":       {"penalty": ["Afif", "Ali"], "freekick": ["Afif", "Junior", "Ahmed"], "corner": ["Afif", "Junior"]},
    "Switzerland": {"penalty": ["Xhaka", "Embolo", "Amdouni"], "freekick": ["Vargas", "Xhaka", "Rieder"], "corner": ["Vargas", "Rieder"]},
    "Brazil":      {"penalty": ["Raphinha", "Neymar", "Thiago"], "freekick": ["Raphinha", "Paqueta", "Bruno G", "Danilo"], "corner": ["Raphinha", "Vinicius", "Bruno G"]},
    "Morocco":     {"penalty": ["Diaz", "Hakimi", "Rahimi"], "freekick": ["Hakimi", "Ounahi", "El Khannouss"], "corner": ["Hakimi", "Diaz"]},
    "Haiti":       {"penalty": ["Nazon", "Isidor"], "freekick": ["Bellegarde", "Deedson", "Providence"], "corner": ["Bellegarde", "Deedson"]},
    "Scotland":    {"penalty": ["McTominay", "Christie", "McGinn"], "freekick": ["McGinn", "Ferguson", "Christie"], "corner": ["Robertson", "Ferguson", "Christie", "McGinn"]},
    "USA":         {"penalty": ["Pulisic", "Balogun"], "freekick": ["Pulisic", "Berhalter", "Reyna"], "corner": ["Pulisic", "Tillman", "Robinson"]},
    "Paraguay":    {"penalty": ["Enciso", "Almiron"], "freekick": ["Gomez", "Enciso", "Almiron"], "corner": ["Gomez", "Enciso"]},
    "Australia":   {"penalty": ["Hrustic", "Irankunda"], "freekick": ["Irankunda", "Hrustic"], "corner": ["Irankunda", "Hrustic", "Metcalfe", "Mabil"]},
    "Turkey":      {"penalty": ["Calhanoglu", "Guler"], "freekick": ["Calhanoglu", "Guler"], "corner": ["Calhanoglu", "Guler"]},
    "Germany":     {"penalty": ["Havertz", "Kimmich"], "freekick": ["Raum", "Wirtz"], "corner": ["Raum", "Wirtz", "Kimmich"]},
    "Curacao":     {"penalty": ["L Bacuna", "J Bacuna"], "freekick": ["L Bacuna", "Antonisse"], "corner": ["L Bacuna", "Antonisse", "J Bacuna"]},
    "Ivory Coast": {"penalty": ["Kessie", "Sangare"], "freekick": ["Diallo", "Kessie"], "corner": ["Diallo", "Diomande"]},
    "Ecuador":     {"penalty": ["Valencia", "J Caicedo"], "freekick": ["Valencia", "Estupinan"], "corner": ["M Caicedo", "Alcivar", "Estupinan"]},
    "Netherlands": {"penalty": ["Gakpo", "Depay", "Weghorst"], "freekick": ["Depay", "Reijnders", "Kluivert"], "corner": ["Depay", "Gakpo", "Koopmeiners"]},
    "Japan":       {"penalty": ["Ueda", "Doan"], "freekick": ["Kubo", "Ito"], "corner": ["Kubo", "Ito", "Doan"]},
    "Sweden":      {"penalty": ["Gyokeres", "Isak"], "freekick": ["Ayari", "Svanberg", "Elanga"], "corner": ["Nygren", "Ayari", "Elanga"]},
    "Tunisia":     {"penalty": ["Abdi", "Gharbi"], "freekick": ["Mejbri", "Abdi"], "corner": ["Mejbri", "Abdi"]},
    "Belgium":     {"penalty": ["De Bruyne", "Lukaku"], "freekick": ["De Bruyne", "Tielemans"], "corner": ["De Bruyne", "Tielemans", "De Cuyper"]},
    "Egypt":       {"penalty": ["Salah", "Marmoush"], "freekick": ["Salah", "Marmoush"], "corner": ["Salah", "Marmoush"]},
    "Iran":        {"penalty": ["Taremi", "Hosseinzadeh"], "freekick": ["Ghoddos"], "corner": ["Ghoddos", "Narafkan", "Hosseinzadeh"]},
    "New Zealand": {"penalty": ["Wood"], "freekick": ["Singh", "Garbett"], "corner": ["Singh", "Payne", "Just"]},
    "Spain":       {"penalty": ["Oyarzabal"], "freekick": ["Pedri", "Yamal"], "corner": ["Yamal", "Baena", "Williams", "Porro", "Grimaldo"]},
    "Cape Verde":  {"penalty": ["Mendes", "Rodriguez"], "freekick": ["Cabral"], "corner": ["Cabral", "Monteiro"]},
    "Saudi Arabia":{"penalty": ["Al-Buraikan"], "freekick": ["Al-Shamat"], "corner": ["Al-Shamat", "S Al-Dawsari"]},
    "Uruguay":     {"penalty": ["Valverde", "Nunez"], "freekick": ["Valverde"], "corner": ["De Arrascaeta", "Valverde"]},
    "France":      {"penalty": ["Mbappe"], "freekick": ["Olise", "Cherki"], "corner": ["Olise", "Cherki"]},
    "Senegal":     {"penalty": ["Mane", "Jackson"], "freekick": ["Mane"], "corner": ["Diatta", "Camara"]},
    "Iraq":        {"penalty": ["Hussein"], "freekick": ["Al-Ammari", "Ali Jasim"], "corner": ["Al-Ammari", "Ali Jasim"]},
    "Norway":      {"penalty": ["Haaland"], "freekick": ["Odegaard"], "corner": ["Odegaard", "Ryerson", "Bobb"]},
    "Argentina":   {"penalty": ["Messi", "L Martinez"], "freekick": ["Messi", "Alvarez"], "corner": ["Messi", "Paredes", "De Paul"]},
    "Algeria":     {"penalty": ["Mahrez"], "freekick": ["Mahrez", "Chaibi"], "corner": ["Chaibi", "Mahrez", "Aouar"]},
    "Austria":     {"penalty": ["Arnautovic", "Sabitzer"], "freekick": ["Sabitzer", "Alaba"], "corner": ["Sabitzer", "Alaba"]},
    "Jordan":      {"penalty": ["Olwan", "Al-Taamari"], "freekick": ["Al-Taamari", "Olwan"], "corner": ["Al-Taamari", "Al-Mardi", "Azaizeh"]},
    "Portugal":    {"penalty": ["Ronaldo", "Fernandes"], "freekick": ["Ronaldo", "Fernandes"], "corner": ["Fernandes", "Neto", "Mendes"]},
    "DR Congo":    {"penalty": ["Wissa", "Bakambu"], "freekick": ["Bogonda", "Wissa", "Masuaku"], "corner": ["Masuaku", "Bogonda", "Wissa"]},
    "Uzbekistan":  {"penalty": ["Shomurodov", "Shukurov"], "freekick": ["Fayzullaev", "Shukurov"], "corner": ["Masharipov", "Fayzullaev"]},
    "Colombia":    {"penalty": ["J Rodriguez", "Diaz"], "freekick": ["Rodriguez"], "corner": ["Rodriguez", "Quintero", "Carrascal"]},
    "England":     {"penalty": ["Kane"], "freekick": ["Rice", "Rashford", "James"], "corner": ["Rice", "Saka"]},
    "Croatia":     {"penalty": ["Modric", "Budimir"], "freekick": ["Modric"], "corner": ["Modric", "Perisic", "Baturina"]},
    "Ghana":       {"penalty": ["Ayew", "Kudus"], "freekick": ["Ayew"], "corner": ["Ayew", "Sulemana"]},
    "Panama":      {"penalty": ["Davis", "Diaz"], "freekick": ["Murillo", "Davis", "Casaquilla"], "corner": ["Davis", "Carrasquilla"]},
}

# API-Football national-team names that differ from our keys -> canonical key.
NATION_ALIASES: dict[str, str] = {
    "korea republic": "South Korea",
    "south korea": "South Korea",
    "czech republic": "Czechia",
    "turkiye": "Turkey",
    "türkiye": "Turkey",
    "ivory coast": "Ivory Coast",
    "cote d'ivoire": "Ivory Coast",
    "côte d'ivoire": "Ivory Coast",
    "congo dr": "DR Congo",
    "dr congo": "DR Congo",
    "democratic republic of congo": "DR Congo",
    "united states": "USA",
    "usa": "USA",
    "curacao": "Curacao",
    "curaçao": "Curacao",
    "cape verde islands": "Cape Verde",
    "cape verde": "Cape Verde",
    "bosnia": "Bosnia and Herzegovina",
    "bosnia and herzegovina": "Bosnia and Herzegovina",
}

# Expected share of a team's penalties by taker rank (1 = primary).
PEN_SHARE_BY_RANK = {1: 0.80, 2: 0.15, 3: 0.05}


def _norm(s: str) -> str:
    """Lowercase, strip accents and punctuation, collapse spaces."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("-", " ").replace(".", " ")
    return " ".join(s.split())


def canonical_nation(name: str) -> str | None:
    """Resolve an API-Football team/nation name to a key in TAKERS."""
    if name in TAKERS:
        return name
    return NATION_ALIASES.get(_norm(name)) or (name if name in TAKERS else None)


def name_matches(candidate: str, player: str) -> bool:
    """
    Tolerant name match between a short list-name and an API player name.
    Substring match works for any length (so "Son" hits "Son Heung-Min"), but
    token-overlap requires tokens of >=4 chars — otherwise common romanised
    syllables ("Kim", "Lee", "Min", "Al", "El") cause false matches.
    """
    c, p = _norm(candidate), _norm(player)
    if not c or not p:
        return False
    if c in p or p in c:            # full substring (handles mononyms + initials)
        return True
    ct, pt = c.split(), p.split()
    # Require a substantial (>=4-char) token in common, to avoid matching on short
    # romanised syllables ("Kim", "Lee", "Min", "Al", "El").
    if not ({t for t in ct if len(t) >= 4} & {t for t in pt if len(t) >= 4}):
        return False
    # Initial consistency: if one name's first token is a single-letter initial and the
    # other's is a full word, the initial must match that word's first letter. Stops
    # "Y. Diomande" matching "Ousmane Diomande" (but keeps it matching "Yan Diomande").
    if len(ct[0]) == 1 and len(pt[0]) > 1 and ct[0] != pt[0][0]:
        return False
    if len(pt[0]) == 1 and len(ct[0]) > 1 and pt[0] != ct[0][0]:
        return False
    # A "distinctive" token is any >=3-char token absent from the other name entirely.
    # If BOTH names carry one, they're different people who merely share a name — reject:
    #   "Gabriel Magalhães" vs "Gabriel Brazão"   (magalhaes vs brazao)
    #   "Vinicius Junior"   vs "Carlos Vinícius"  (junior vs carlos)
    #   "Ousmane Diomande"  vs "Yan Diomande"     (ousmane vs yan)  <- 3-char first name
    #   "Nico Williams"     vs "Inaki Williams"   (nico vs inaki — different brothers)
    # while keeping reversed-order ("Lee Kang-In"/"Kang-in Lee"), subset names
    # ("Idrissa Gueye"/"Idrissa Gana Gueye"), and initials (len<3 ignored).
    c_extra = {t for t in ct if len(t) >= 3 and t not in pt}
    p_extra = {t for t in pt if len(t) >= 3 and t not in ct}
    if c_extra and p_extra:
        return False
    return True


def _rank_in(list_names: list[str], player_name: str) -> int | None:
    """1-based rank of player in an ordered taker list."""
    for idx, taker in enumerate(list_names, 1):
        if name_matches(taker, player_name):
            return idx
    return None


@dataclass
class SetPieceRole:
    nation: str
    pen_rank: int | None = None
    fk_rank: int | None = None
    corner_rank: int | None = None

    @property
    def pen_share(self) -> float:
        return PEN_SHARE_BY_RANK.get(self.pen_rank, 0.0)

    @property
    def is_pen_taker(self) -> bool:
        return self.pen_rank is not None and self.pen_rank <= 2

    @property
    def is_fk_taker(self) -> bool:
        return self.fk_rank == 1

    @property
    def is_corner_taker(self) -> bool:
        return self.corner_rank == 1

    def label(self) -> str:
        """Compact tag for reports, e.g. 'P1 FK1' or 'P2 C1' ('' if none)."""
        bits = []
        if self.pen_rank:
            bits.append(f"P{self.pen_rank}")
        if self.fk_rank:
            bits.append(f"FK{self.fk_rank}")
        if self.corner_rank:
            bits.append(f"C{self.corner_rank}")
        return " ".join(bits)


def lookup(nation: str, player_name: str) -> SetPieceRole | None:
    """Return the player's set-piece role for their nation, or None if no data."""
    key = canonical_nation(nation)
    if not key:
        return None
    t = TAKERS[key]
    return SetPieceRole(
        nation=key,
        pen_rank=_rank_in(t.get("penalty", []), player_name),
        fk_rank=_rank_in(t.get("freekick", []), player_name),
        corner_rank=_rank_in(t.get("corner", []), player_name),
    )


def apply_set_pieces(form, nation: str) -> SetPieceRole | None:
    """
    Overlay national set-piece duty onto a PlayerForm (mutates it). Sets
    sp_pen_rank / sp_fk_rank / sp_corner_rank; form_to_xpts then uses these to
    drive the WC penalty/FK/corner threat instead of the club record (the
    club-based pen_taker property is left untouched as a separate signal).
    Returns the role (or None if the nation/player isn't in the dataset).
    """
    role = lookup(nation, form.name)
    form.sp_pen_rank = role.pen_rank if role else None
    form.sp_fk_rank = role.fk_rank if role else None
    form.sp_corner_rank = role.corner_rank if role else None
    return role
