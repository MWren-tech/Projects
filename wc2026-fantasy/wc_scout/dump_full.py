"""Write full_ranked.txt: every player in the model, ranked per position."""
import sys
from collections import defaultdict
from api_football import ApiFootball
from wc_shortlist import build_priced_survivors

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sp(f):
    parts = []
    if f.sp_pen_rank: parts.append(f"P{f.sp_pen_rank}")
    if f.sp_fk_rank: parts.append(f"FK{f.sp_fk_rank}")
    if f.sp_corner_rank: parts.append(f"C{f.sp_corner_rank}")
    return " ".join(parts)


def cell_price(c):
    return f"{c['price']:.1f}" if c.get("price") else "-"

def cell_own(c):
    o = c.get("ownership")
    if o is None:
        return "-"
    return f"{o:.1f}*" if o < 5 else f"{o:.1f}"

def cell_val(c):
    return f"{c['value']:.2f}" if c.get("value") is not None else "-"

def cell_cxp(c):
    return f"{c['country_xp']:.2f}" if c.get("country_xp") is not None else "-"


def main():
    api = ApiFootball()
    surv = build_priced_survivors(api, 600, 40, verbose=True)
    bp = defaultdict(list)
    for c in surv:
        bp[c["form"].position].append(c)

    L = [f"WC2026 FULL RANKED LIST - {len(surv)} players (FIFA-game players only; FIFA positions)",
         "final = league-strength x form(season+club-recent+country) | $=FIFA price | Own%(*=<5%) | "
         "Val=pts/$m | sXP/cXP=club-season/country form | CS%=natl clean sheet | Dif=fixture ease | SP=set-piece",
         ""]
    for pos in ("GK", "DEF", "MID", "FWD"):
        rows = sorted(bp[pos], key=lambda c: c["final_xp"], reverse=True)
        head = (f"{'#':>3} {'xPts':>5} {'Player':<22}{'Nation':<13}{'Lg':<5}{'$':>5}{'Own%':>6}"
                f"{'Val':>5}{'sXP':>5}{'cXP':>5} {'CS%':>4}{'Dif':>5} SP")
        L += [f"===== {pos} ({len(rows)}) =====", head, "-" * len(head)]
        for i, c in enumerate(rows, 1):
            f = c["form"]
            L.append(f"{i:>3} {c['final_xp']:>5.2f} {f.name[:21]:<22}{c['nation'][:12]:<13}"
                     f"{c['league_tag']:<5}{cell_price(c):>5}{cell_own(c):>6}{cell_val(c):>5}"
                     f"{c['season_xp']:>5.2f}{cell_cxp(c):>5} {c['cs']*100:>3.0f}%{c['diff']:>5.2f} {sp(f)}")
        L.append("")
    open("full_ranked.txt", "w", encoding="utf-8").write("\n".join(L))
    print(f"\nwrote full_ranked.txt ({len(surv)} players)")
    print("Vinicius variants:", [(c['form'].name, c['form'].position) for c in surv if 'vinic' in c['form'].name.lower()])
    print("Gabriels:", [c['form'].name for c in surv if c['form'].name.lower().startswith('gabriel')])


if __name__ == "__main__":
    main()
