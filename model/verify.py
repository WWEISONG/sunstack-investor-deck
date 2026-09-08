"""Recompute every headline number and confirm index.html states it."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import model as M

s = open(os.path.join(HERE, "..", "index.html")).read()
txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))

F = M.FLEET; U, S = M.U_BASE, M.S_BASE
tot = U.to_owner + M.UNIT_OM + U.energy
CHECKS = [
    ("base gross",            f"A${U.gross:,.0f}"),
    ("base homeowner",        f"{U.to_owner:,.0f}"),
    ("base net",              f"A${U.net:,.0f}"),
    ("base payback",          f"{U.payback:.1f}"),
    ("base ROC",              f"{U.roc*100:.0f}%"),
    ("base tokens",           f"{U.tokens/1e6:,.0f} M"),
    ("floor gross",           f"A${M.U_FLOOR.gross:,.0f}"),
    ("floor net",             f"A${M.U_FLOOR.net:,.0f}"),
    ("floor payback",         f"{M.U_FLOOR.payback:.1f}"),
    ("floor tokens",          f"{M.U_FLOOR.tokens/1e6:,.0f} M"),
    ("upside gross",          f"A${M.U_UP.gross:,.0f}"),
    ("upside net",            f"A${M.U_UP.net:,.0f}"),
    ("upside tokens",         f"{M.U_UP.tokens/1e6:,.0f} M"),
    ("spark net",             f"A${S.net:,.0f}"),
    ("distributable pool",    f"A${U.pool:,.0f}"),
    ("sold-node net (unit)",  f"A${U.sold_net:,.0f}"),
    ("fleet gross",           f"A${F.gross/1e6:.2f}M"),
    ("fleet contribution",    f"A${F.contrib/1e6:.2f}M"),
    ("fleet operating cash",  f"A${F.opcash/1e6:.2f}M"),
    ("fleet capital",         f"A${F.capex/1e6:.2f}M"),
    ("fleet ROC",             f"{F.roc*100:.0f}%"),
    ("break-even owned",      f"{F.breakeven_owned:,.0f}"),
    ("break-even sold",       f"{F.breakeven_sold:,.0f}"),
    ("operating cost total",  f"A${tot:,.0f}"),
    ("gross margin",          f"{(U.gross-tot)/U.gross*100:.0f}%"),
    ("kWh as tokens",         f"A${M.KWH_AS_TOKENS:.2f}"),
    ("kWh ratio",             f"{M.KWH_RATIO:.0f}×"),
    ("units per A$1M",        f"{M.PER_M_UNITS:.0f}"),
    ("gross per A$1M",        f"A${M.PER_M_GROSS/1e6:.2f}M"),
    ("net per A$1M",          f"A${M.PER_M_NET/1e6:.2f}M"),
    ("SOM at 10k nodes",      f"A${M.SOM_10K/1e6:.1f}M"),
    ("share of SAM at 10k",   f"{M.SHARE_10K*100:.1f}%"),
    ("eligible-home share",   f"{M.ELIGIBLE_SHARE_10K*100:.2f}%"),
    ("SAM 2026",              f"A${M.SAM_2026/1e6:.0f}M"),
]
bad = []
for name, want in CHECKS:
    ok = want in txt
    if not ok: bad.append((name, want))
    print(f"  {'OK  ' if ok else 'MISS'}  {name:24} {want}")
print(f"\n{len(CHECKS)-len(bad)}/{len(CHECKS)} claims consistent with the model")
if bad:
    print("MISSING FROM DECK:")
    for n, w in bad: print(f"   - {n}: expected {w}")
    sys.exit(1)
