"""
Probable starting XIs for all 48 World Cup 2026 national teams.

Source: goal.com "Probable line-ups World Cup 2026 — expected starting XI of the
48 national teams" (June 2026). Used as the "consistent international starter"
filter: a club player only makes the WC shortlist if he's in his nation's
expected XI here. Forward-looking (who'll actually start at the WC) and needs no
extra API calls.

Nation keys match set_piece_takers.TAKERS so canonical_nation() resolves both.
Names are kept as published (surnames, some initials); matching is accent- and
substring-tolerant via the shared normaliser.
"""

from __future__ import annotations

from set_piece_takers import canonical_nation, name_matches

PROBABLE_XI: dict[str, list[str]] = {
    "Algeria": ["Zidane", "Belghali", "Belaid", "Bensebaini", "Ait-Nouri", "Zerrouki", "Boudaoui", "Mahrez", "Aouar", "Chaibi", "Gouiri"],
    "Saudi Arabia": ["Al-Aqidi", "Boushal", "Tambakti", "Al-Amri", "Al-Harbi", "Kanno", "Al-Khaibari", "N. Al-Dawsari", "Mandash", "Al-Buraikan", "S. Al-Dawsari"],
    "Argentina": ["Martinez", "Molina", "Otamendi", "Romero", "Tagliafico", "Mac Allister", "Paredes", "Fernandez", "Messi", "Alvarez", "Almada"],
    "Australia": ["Ryan", "Italiano", "Degenek", "Souttar", "Circati", "Bos", "Metcalfe", "Devlin", "O'Neill", "Irankunda", "Toure"],
    "Austria": ["A. Schlager", "Laimer", "Lienhart", "Alaba", "Mwene", "X. Schlager", "Seiwald", "Wimmer", "Baumgartner", "Sabitzer", "Arnautovic"],
    "Belgium": ["Courtois", "Castagne", "Debast", "Theate", "De Cuyper", "Tielemans", "Onana", "Doku", "De Bruyne", "Trossard", "De Ketelaere"],
    "Bosnia and Herzegovina": ["Vasilj", "Dedic", "Katic", "Muharemovic", "Kolasinac", "Bajraktarevic", "Sunjic", "Tahirovic", "Memic", "Demirovic", "Dzeko"],
    "Brazil": ["Alisson", "Wesley", "Marquinhos", "Gabriel", "Douglas Santos", "Luis Henrique", "Casemiro", "Bruno Guimaraes", "Raphinha", "Vinicius", "Cunha"],
    "Canada": ["Crepeau", "Sigur", "Bombito", "Jones", "Laryea", "Buchanan", "Kone", "Eustaquio", "Davies", "Oluwaseyi", "David"],
    "Cape Verde": ["Voziha", "Moreira", "Lopes", "Borges", "Lopes Cabral", "Lenini", "Duarte", "Rodrigues", "Monteiro", "Cabral", "Livramento"],
    "Colombia": ["Montero", "Munoz", "Sanchez", "Mina", "Mojica", "Lerma", "Rios", "Arias", "James", "Diaz", "Suarez"],
    "South Korea": ["Seung-gyu Kim", "Seol", "Min-jae Kim", "Han-beom Lee", "Tae-seok Lee", "Wang", "Castrop", "Kang-in Lee", "Jae-sung Lee", "Bae", "Son"],
    "Ivory Coast": ["Fofana", "Doue", "Koussonou", "Ndicka", "Konan", "Kessie", "Sangare", "Oulai", "Pepe", "Guessand", "Diomande"],
    "Curacao": ["Room", "Sambo", "Van Ejma", "Obispo", "Floranus", "J. Bacuna", "Comenancia", "L. Bacuna", "Chong", "Locadia", "Gorre"],
    "Croatia": ["Livakovic", "Stanisic", "Sutalo", "Caleta-Car", "Gvardiol", "Sucic", "Modric", "Pasalic", "Kramaric", "Perisic", "Budimir"],
    "Ecuador": ["Galindez", "Preciado", "Ordonez", "Pacho", "Hincapie", "Vite", "Caicedo", "Castillo", "Yeboah", "Valencia", "Angulo"],
    "Egypt": ["El Shenawy", "Ibrahim", "Abdelmaguif", "Rabia", "Hany", "Ateya", "Lasheen", "Fatouh", "Ashour", "Salah", "Marmoush"],
    "France": ["Maignan", "Kounde", "Saliba", "Upamecano", "Hernandez", "Rabiot", "Tchouameni", "Dembele", "Olise", "Doue", "Mbappe"],
    "Germany": ["Neuer", "Kimmich", "Tah", "Schlotterbeck", "Raum", "Pavlovic", "Goretzka", "Sane", "Musiala", "Wirtz", "Havertz"],
    "Ghana": ["Asare", "Adjetei", "Seidu", "Oppong", "Yirenkyi", "Sibo", "Partey", "Mensah", "Sulemana", "Semenyo", "Ayew"],
    "Japan": ["Suzuki", "Tomiyasu", "Taniguchi", "Itakura", "Doan", "Endo", "Tanaka", "Nakamura", "Kubo", "Ito", "Ueda"],
    "Jordan": ["Abulaila", "Abu Dahab", "Nasib", "Al-Arab", "Haddad", "Al-Rawahbdeh", "Al-Rashdan", "Abu Taha", "Tamari", "Olwan", "Al-Mardi"],
    "Haiti": ["Placide", "Arcus", "Ade", "Duverne", "Experience", "Deedson", "Bellegarde", "Pierre", "Isidor", "Nazon", "Providence"],
    "England": ["Pickford", "James", "Guehi", "Konsa", "O'Reilly", "Anderson", "Rice", "Saka", "Bellingham", "Eze", "Kane"],
    "Iran": ["Beyranvand", "Yousefi", "Kanaani", "Khalilzadeh", "Mohammadi", "Ezatolahi", "Ghoddos", "Jahanbakhsh", "Ghayedi", "Mohebi", "Taremi"],
    "Iraq": ["Hassan", "Hussein Ali", "Sulaka", "Tahseen", "Doski", "Al-Ammari", "Bayesh", "Ali Jasim", "Iqbal", "Amyn", "Aymen Hussein"],
    "Morocco": ["Bono", "Hakimi", "Diop", "Aguerd", "Salah-Eddine", "Ounahi", "El Aynaoui", "Brahim Diaz", "Saibari", "Talbi", "El Kaabi"],
    "Mexico": ["Rangel", "Sanchez", "Montes", "Vasquez", "Gallardo", "Pineda", "Alvarez", "Fidalgo", "Vega", "Jimenez", "Quinones"],
    "Norway": ["Nyland", "Ryerson", "Heggem", "Ostigard", "Wolfe", "Thorstvedt", "Berg", "Berge", "Sorloth", "Haaland", "Nusa"],
    "New Zealand": ["Crocombe", "Payne", "Bindon", "Boxall", "Cacace", "Samenic", "Bell", "McCowatt", "Singh", "Garbett", "Wood"],
    "Netherlands": ["Verbruggen", "Dumfries", "Van Dijk", "Ake", "Van de Ven", "De Jong", "Gravenberch", "Malen", "Reijnders", "Gakpo", "Depay"],
    "Panama": ["Mosquera", "Farina", "Andrade", "Cordoba", "Murillo", "Carrasquilla", "Godoy", "Davis", "Barcenas", "Diaz", "Fajardo"],
    "Paraguay": ["Gill", "Caceres", "G. Gomez", "Alderete", "Alonso", "D. Gomez", "Ojeda", "Bobadilla", "Almiron", "Enciso", "Avalos"],
    "Portugal": ["Costa", "Cancelo", "Ruben Dias", "Inacio", "Nuno Mendes", "Joao Neves", "Vitinha", "Bruno Fernandes", "Bernardo Silva", "Cristiano Ronaldo", "Joao Felix"],
    "Qatar": ["Barsham", "Al-Oui", "Khoukhi", "Pedro Miguel", "Al-Amin", "Boudiaf", "Fathy", "Laye", "Edmilson Junior", "Almoez Ali", "Afif"],
    "Czechia": ["Hornicek", "Chaloupek", "Hranac", "Krejci", "Zeleny", "Soucek", "Darida", "Coufal", "Provod", "Sulc", "Schick"],
    "DR Congo": ["Mpasi", "Wan-Bissaka", "Mbemba", "Tuanzebe", "Masuaku", "Pickel", "Moutoussamy", "Bongonda", "Kakuta", "Wissa", "Bakambu"],
    "Scotland": ["Gordon", "Hickey", "Hanley", "McKenna", "Robertson", "Ferguson", "Gannon-Doak", "Christie", "McTominay", "McGinn", "Adams"],
    "Senegal": ["Mendy", "Diatta", "Koulibaly", "Niakhate", "Jakobs", "Idrissa Gueye", "Pape Gueye", "Ismaila Sarr", "Iliman Ndiaye", "Mane", "Jackson"],
    "Spain": ["Simon", "Llorente", "Cubarsi", "Laporte", "Cucurella", "Pedri", "Rodri", "Fabian Ruiz", "Yamal", "Oyarzabal", "N. Williams"],
    "USA": ["Freese", "Freeman", "Richards", "Trusty", "Antonee Robinson", "McKennie", "Berhalter", "Adams", "Weah", "Balogun", "Pulisic"],
    "South Africa": ["Williams", "Mudau", "Sibisi", "Ndamane", "Modiba", "Sithole", "Mokoena", "Apollis", "Zwane", "Mofokeng", "Foster"],
    "Sweden": ["Nordfeldt", "Starfelt", "Lagerbielke", "Lindelof", "Svensson", "Karlstrom", "Ayari", "Gudmundsson", "Nygren", "Elanga", "Gyokeres"],
    "Switzerland": ["Kobel", "Widmer", "Akanji", "Elvedi", "Rodriguez", "Freuler", "Xhaka", "Rieder", "Ndoye", "Embolo", "Vargas"],
    "Tunisia": ["Dahmen", "Valery", "Bronn", "Talbi", "Abdi", "Gharbi", "Skhiri", "Hannibal", "Achouri", "Mastouri", "Tounekti"],
    "Turkey": ["Cakir", "Demiral", "Kabak", "Bardakci", "Celik", "Calhanoglu", "Kokcu", "Ozer", "Guler", "Yildiz", "Akturkoglu"],
    "Uruguay": ["Rochet", "Valera", "Gimenez", "Araujo", "Olivera", "Valverde", "Ugarte", "Bentancur", "Canobbio", "Nunez", "Rodriguez"],
    "Uzbekistan": ["Nematov", "Abdullaev", "Ashurmatov", "Khusanov", "Sayfiev", "Shukurov", "Khamrobekov", "Nasrullaev", "Ganiev", "Urunov", "Shomurodov"],
}


def xi_rank(nation: str, player_name: str) -> int | None:
    """1-based slot in the nation's probable XI if the player matches, else None."""
    key = canonical_nation(nation)
    if not key or key not in PROBABLE_XI:
        return None
    for idx, starter in enumerate(PROBABLE_XI[key], 1):
        if name_matches(starter, player_name):
            return idx
    return None


def is_probable_starter(nation: str, player_name: str) -> bool:
    return xi_rank(nation, player_name) is not None
