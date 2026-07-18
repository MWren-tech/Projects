"""ranked_by_points.txt — every player ranked purely by PROJECTED POINTS.
Price plays no part in the ranking; it's shown only as a reference column."""
import sys
from api_football import ApiFootball
from wc_shortlist import build_priced_survivors
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sp(f):
    parts = []
    if f.sp_pen_rank: parts.append(f"P{f.sp_pen_rank}")
    if f.sp_fk_rank: parts.append(f"FK{f.sp_fk_rank}")
    if f.sp_corner_rank: parts.append(f"C{f.sp_corner_rank}")
    return " ".join(parts)


def main():
    surv = build_priced_survivors(ApiFootball(), 600, 40, verbose=True)
    surv.sort(key=lambda c: c["final_xp"], reverse=True)   # rank by points only
    head = (f"{'#':>3} {'xPts':>5} {'Player':<22}{'Pos':<4}{'Nation':<13}{'Lg':<5}"
            f"{'CS%':>4}{'Dif':>5} {'SP':<9}{'($ref)':>7}{'Own%':>6}")
    L = ["WC2026 PLAYERS RANKED BY PROJECTED POINTS (price NOT used in ranking)",
         "xPts = projected fantasy points/match | CS%=natl clean sheet | Dif=fixture ease | "
         "SP=set-piece | ($ref)=FIFA price (reference only) | Own%=ownership",
         "", head, "-" * len(head)]
    for i, c in enumerate(surv, 1):
        f = c["form"]
        price = f"{c['price']:.1f}" if c.get("price") else "-"
        own = c.get("ownership")
        own_s = f"{own:.1f}" if own is not None else "-"
        L.append(f"{i:>3} {c['final_xp']:>5.2f} {f.name[:21]:<22}{f.position:<4}"
                 f"{c['nation'][:12]:<13}{c['league_tag']:<5}{c['cs']*100:>3.0f}%{c['diff']:>5.2f} "
                 f"{sp(f):<9}{price:>7}{own_s:>6}")
    open("ranked_by_points.txt", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"\nwrote ranked_by_points.txt ({len(surv)} players)")
    print("TOP 30 OVERALL:")
    for i, c in enumerate(surv[:30], 1):
        print(f"  {i:>2} {c['final_xp']:>5.2f} {c['form'].name[:20]:<21}{c['form'].position:<4}"
              f"{c['nation'][:11]:<12}${c.get('price') or '-'}")


if __name__ == "__main__":
    main()
