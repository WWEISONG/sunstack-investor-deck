"""Generate every SVG chart in the deck from model.py. Writes to build/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build")
os.makedirs(OUT, exist_ok=True)
F = {'ax': 16, 'tick': 17, 'lbl': 19, 'sub': 15, 'val': 19, 'call': 19}
def st(px): return f'style="font-size:{px}px"'
def svg(name, w, h, body, label):
    open(os.path.join(OUT, name), "w").write(
        f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">\n    {body}\n  </svg>')

# ── 1 · arbitrage ────────────────────────────────────────────────
def arbitrage():
    items = [("Exported to the grid", M.EXPORT_TARIFF, f"A${M.EXPORT_TARIFF:.2f}", 0),
             ("Bought back at night", M.GRID_PRICE, f"A${M.GRID_PRICE:.2f}", 0),
             ("Converted to AI tokens", M.KWH_AS_TOKENS, f"A${M.KWH_AS_TOKENS:.2f}", 1)]
    BX0, BX1, TOP, RH, GAP = 372, 1000, 66, 56, 30
    mx = M.KWH_AS_TOKENS
    b = f'<text class="axname" x="0" y="22" {st(F["ax"])}>What one kilowatt-hour of surplus rooftop solar is worth</text>'
    for i, (nm, v, lab, amber) in enumerate(items):
        y = TOP + i*(RH+GAP); cy = y + RH/2; w = max(5.0, v/mx*(BX1-BX0))
        b += f'<text class="lbl-b" x="0" y="{cy+7:.0f}" {st(F["lbl"])}>{nm}</text>'
        b += f'<rect class="{"bar-bad" if amber else "bar-neutral"}" x="{BX0}" y="{y}" width="{w:.1f}" height="{RH}" rx="5"/>'
        b += (f'<text class="val-in" x="{BX0+w-20:.1f}" y="{cy+9:.0f}" text-anchor="end" {st(26)}>{lab}</text>' if amber
              else f'<text class="val" x="{BX0+w+16:.1f}" y="{cy+7:.0f}" {st(F["val"])}>{lab}</text>')
    lc = TOP + 2*(RH+GAP) + RH/2
    b += f'<text class="bignum" x="1082" y="{lc+2:.0f}" text-anchor="middle">{M.KWH_RATIO:.0f}×</text>'
    b += f'<text class="lbl" x="1082" y="{lc+32:.0f}" text-anchor="middle" {st(F["sub"])}>vs exporting it</text>'
    svg("arbitrage.svg", 1160, 322, b,
        f"One kilowatt-hour of surplus rooftop solar: {M.EXPORT_TARIFF*100:.0f} cents exported, "
        f"{M.GRID_PRICE*100:.0f} cents bought back, A${M.KWH_AS_TOKENS:.2f} as AI tokens — {M.KWH_RATIO:.0f} times more.")

# ── 2 · unit-economics waterfall ─────────────────────────────────
def waterfall():
    n = M.U_BASE
    steps = [("Gross revenue", 0, n.gross, "tot"), ("Homeowner 25%", n.gross, -n.to_owner, "neg"),
             ("Energy", n.gross-n.to_owner, -n.energy, "neg"),
             ("Node O&M", n.gross-n.to_owner-n.energy, -M.UNIT_OM, "neg"),
             ("Net cash", 0, n.net, "tot")]
    PX0, PX1, PY0, PY1, YMAX = 104, 1120, 40, 236, 4400.
    wy = lambda v: PY1 - v/YMAX*(PY1-PY0)
    slot = (PX1-PX0)/len(steps); bw = slot*0.52; b = ""
    for v in (0, 1000, 2000, 3000, 4000):
        y = wy(v); b += f'<line class="gridline" x1="{PX0}" y1="{y:.1f}" x2="{PX1}" y2="{y:.1f}"/>'
        b += f'<text class="tick" x="{PX0-12}" y="{y+5:.1f}" text-anchor="end" {st(F["tick"])}>A${v//1000}k</text>'
    b += f'<text class="axname" x="{PX0}" y="20" {st(F["ax"])}>Per company-owned unit, per year — base case</text>'
    for i, (nm, base, d, kind) in enumerate(steps):
        x = PX0 + i*slot + (slot-bw)/2
        top = wy(base+d) if d > 0 else wy(base); bot = wy(base) if d > 0 else wy(base+d)
        h = max(2.0, abs(bot-top))
        lab = ("−" if kind == "neg" else "") + "A$" + format(int(round(abs(d))), ",")
        b += f'<rect class="{"bar-bad" if kind=="tot" else "bar-neutral"}" x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="3"/>'
        b += f'<text class="val" x="{x+bw/2:.1f}" y="{top-11:.1f}" text-anchor="middle" {st(F["val"])}>{lab}</text>'
        b += f'<text class="lbl" x="{x+bw/2:.1f}" y="{PY1+26:.0f}" text-anchor="middle" {st(F["sub"])}>{nm}</text>'
        if i < len(steps)-1:
            nb = base+d if kind != "tot" or i == 0 else base
            b += f'<line class="connector" x1="{x+bw:.1f}" y1="{wy(nb):.1f}" x2="{x+slot:.1f}" y2="{wy(nb):.1f}"/>'
    b += f'<line class="ax" x1="{PX0}" y1="{PY0}" x2="{PX0}" y2="{PY1}"/>'
    svg("waterfall.svg", 1160, 292, b,
        f"Waterfall: A${n.gross:,.0f} gross revenue per unit less homeowner share, energy and maintenance leaves A${n.net:,.0f} net cash.")

# ── 3 · payback curve ────────────────────────────────────────────
def payback():
    X0, X1, Y0, Y1 = 112, 1104, 34, 206
    YMIN, YMAX, T = -6000., 42000., 5.
    cx = lambda t: X0 + t/T*(X1-X0); cy = lambda v: Y1 - (v-YMIN)/(YMAX-YMIN)*(Y1-Y0)
    ln = lambda r: f"M {cx(0):.1f} {cy(-M.UNIT_CAPEX):.1f} L {cx(T):.1f} {cy(-M.UNIT_CAPEX+r*T):.1f}"
    fl, ba, up = M.U_FLOOR.net, M.U_BASE.net, M.U_UP.net
    b = ""
    for v in (-6000, 0, 10000, 20000, 30000, 40000):
        y = cy(v); lab = "A$0" if v == 0 else (f"−A${abs(v)/1000:.0f}k" if v < 0 else f"+A${v/1000:.0f}k")
        b += f'<line class="{"zero" if v==0 else "gridline"}" x1="{X0}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}"/>'
        b += f'<text class="tick" x="{X0-12}" y="{y+5:.1f}" text-anchor="end" {st(F["tick"])}>{lab}</text>'
    for t in range(6):
        x = cx(t); b += f'<line class="gridline" x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y1}" opacity=".5"/>'
        b += f'<text class="tick" x="{x:.1f}" y="{Y1+34:.0f}" text-anchor="middle" {st(F["tick"])}>{t} yr</text>'
    band = (f"M {cx(0):.1f} {cy(-M.UNIT_CAPEX):.1f} L {cx(T):.1f} {cy(-M.UNIT_CAPEX+up*T):.1f} "
            f"L {cx(T):.1f} {cy(-M.UNIT_CAPEX+fl*T):.1f} Z")
    bx, by = cx(M.U_BASE.payback), cy(0)
    b += (f'<path class="band" d="{band}"/><path class="ln edge" d="{ln(up)}"/><path class="ln edge" d="{ln(fl)}"/>'
          f'<path class="ln base" d="{ln(ba)}"/><line class="ax" x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}"/>'
          f'<circle class="dot" cx="{bx:.1f}" cy="{by:.1f}" r="7"/>'
          f'<rect class="callout" x="{bx-66:.1f}" y="{by-52:.1f}" width="158" height="34" rx="8"/>'
          f'<text class="callout-t" x="{bx+13:.1f}" y="{by-29:.1f}" text-anchor="middle" {st(F["call"])}>Break-even · {M.U_BASE.payback:.1f} yr</text>'
          f'<text class="val" x="{X1-8:.1f}" y="{cy(-M.UNIT_CAPEX+up*T)+18:.1f}" text-anchor="end" {st(F["val"])}>Upside · +A${(-M.UNIT_CAPEX+up*T)/1000:.1f}k</text>'
          f'<text class="val" x="{X1-8:.1f}" y="{cy(-M.UNIT_CAPEX+ba*T)-13:.1f}" text-anchor="end" {st(F["val"])}>Base · +A${(-M.UNIT_CAPEX+ba*T)/1000:.1f}k</text>'
          f'<text class="lbl" x="{X1-8:.1f}" y="{cy(-M.UNIT_CAPEX+fl*T)+24:.1f}" text-anchor="end" {st(F["sub"])}>Floor · break-even at {M.U_FLOOR.payback:.1f} yr</text>'
          f'<text class="axname" x="{X0}" y="18" {st(F["ax"])}>Cumulative cash per unit</text>')
    svg("payback.svg", 1160, 272, b,
        f"Cumulative cash per unit over five years; base case breaks even at {M.U_BASE.payback:.1f} years, floor at {M.U_FLOOR.payback:.1f}.")

# ── 4 · sensitivity tornado ──────────────────────────────────────
def tornado():
    def pb(sc, capex=M.UNIT_CAPEX): return capex / M.Node(sc, capex, M.UNIT_OM, M.UNIT_WATTS).net
    B = M.BASE
    rep = lambda **kw: M.Scenario(**{**B.__dict__, **kw})
    rows = [("Throughput", f"{M.FLOOR.tok_s:.0f} → {M.UPSIDE.tok_s:.0f} tok/s",
             pb(rep(tok_s=M.FLOOR.tok_s)), pb(rep(tok_s=M.UPSIDE.tok_s))),
            ("Sell price", f"A${M.FLOOR.price:.2f} → A${M.UPSIDE.price:.2f} / M",
             pb(rep(price=M.FLOOR.price)), pb(rep(price=M.UPSIDE.price))),
            ("Paid utilisation", f"{M.FLOOR.utilisation:.0%} → {M.UPSIDE.utilisation:.0%}",
             pb(rep(utilisation=M.FLOOR.utilisation)), pb(rep(utilisation=M.UPSIDE.utilisation))),
            ("Hardware cost", "A$3,600 → A$2,000",
             pb(B, 4800.), pb(B, 3200.)),
            ("Homeowner share", f"{M.FLOOR.owner_share:.0%} → {M.UPSIDE.owner_share:.0%}",
             pb(rep(owner_share=M.FLOOR.owner_share)), pb(rep(owner_share=M.UPSIDE.owner_share)))]
    rows.sort(key=lambda r: -(r[2]-r[3]))
    BP = M.U_BASE.payback; PX0, PX1, PMIN, PMAX = 352, 1082, 0.72, 2.40
    tx = lambda v: PX0 + (v-PMIN)/(PMAX-PMIN)*(PX1-PX0)
    RH, GAP, TOP = 40, 12, 68; body = ""
    for i, (nm, rg, worse, better) in enumerate(rows):
        y = TOP + i*(RH+GAP); xb, xw, xo = tx(better), tx(worse), tx(BP)
        body += (f'<text class="lbl-b" x="0" y="{y+18}" {st(F["lbl"])}>{nm}</text>'
                 f'<text class="lbl" x="0" y="{y+37}" {st(F["sub"])}>{rg}</text>'
                 f'<rect class="bar-good" x="{xb:.1f}" y="{y}" width="{xo-xb:.1f}" height="{RH}" rx="4"/>'
                 f'<rect class="bar-bad" x="{xo:.1f}" y="{y}" width="{xw-xo:.1f}" height="{RH}" rx="4"/>'
                 f'<text class="val" x="{xb-11:.1f}" y="{y+26}" text-anchor="end" {st(F["val"])}>{better:.2f}</text>'
                 f'<text class="val" x="{xw+11:.1f}" y="{y+26}" text-anchor="start" {st(F["val"])}>{worse:.2f}</text>')
    BOT = TOP + len(rows)*(RH+GAP) - GAP; tk = ""
    for v in (1.0, 1.5, 2.0):
        x = tx(v); tk += f'<line class="gridline" x1="{x:.1f}" y1="{TOP-14}" x2="{x:.1f}" y2="{BOT+8}"/>'
        tk += f'<text class="tick" x="{x:.1f}" y="{BOT+32}" text-anchor="middle" {st(F["tick"])}>{v:.1f} yr</text>'
    b = (f'{tk}<text class="axname" x="0" y="20" {st(F["ax"])}>Payback in years — each bar spans that variable\'s full range</text>'
         f'{body}<line class="bar-base" x1="{tx(BP):.1f}" y1="{TOP-14}" x2="{tx(BP):.1f}" y2="{BOT+8}"/>'
         f'<text class="callout-t" x="{tx(BP):.1f}" y="{TOP-22}" text-anchor="middle" {st(F["call"])}>Base {BP:.2f} yr</text>')
    svg("tornado.svg", 1160, BOT+50, b,
        f"Tornado chart of payback sensitivity; throughput and sell price dominate, worst single case {max(r[2] for r in rows):.2f} years.")
    return max(r[2] for r in rows)

# ── 5 · market share ─────────────────────────────────────────────
def market():
    MX0, MX1, MY, MH = 104, 1112, 124, 66; wpx = MX1-MX0
    w1 = max(4.0, M.SOM_1K/M.SAM_2026*wpx); w10 = max(6.0, M.SOM_10K/M.SAM_2026*wpx)
    b = (f'<text class="axname" x="{MX0}" y="20" {st(13)}>Australian spend on AI-optimised infrastructure</text>'
         f'<text class="lbl" x="{MX0}" y="52" {st(17)}>A${M.SAM_2025/1e6:.0f}M in 2025 → <tspan class="val" {st(19)}>A${M.SAM_2026/1e6:.0f}M in 2026</tspan> · +{(M.SAM_GROWTH-1)*100:.0f}% year on year</text>'
         f'<rect class="bar-neutral" x="{MX0}" y="{MY}" width="{wpx}" height="{MH}" rx="5"/>'
         f'<rect class="bar-bad" x="{MX0}" y="{MY}" width="{w10:.1f}" height="{MH}" rx="5"/>'
         f'<text class="val" x="{MX1-18}" y="{MY+MH/2+8}" text-anchor="end" {st(21)}>A${M.SAM_2026/1e6:.0f}M total market</text>'
         f'<line class="lead" x1="{MX0+w10/2:.1f}" y1="{MY-5}" x2="{MX0+w10/2:.1f}" y2="{MY-26}"/>'
         f'<text class="callout-t" x="{MX0+w10/2+10:.1f}" y="{MY-32}" {st(16)}>10,000 nodes · A${M.SOM_10K/1e6:.1f}M · {M.SHARE_10K*100:.1f}% of the market</text>'
         f'<line class="lead" x1="{MX0+w1/2:.1f}" y1="{MY+MH+5}" x2="{MX0+w1/2:.1f}" y2="{MY+MH+24}"/>'
         f'<text class="lbl" x="{MX0+w1/2+10:.1f}" y="{MY+MH+38}" {st(15)}>1,000 nodes · A${M.SOM_1K/1e6:.2f}M · {M.SHARE_1K*100:.1f}% of the market</text>')
    svg("market.svg", 1160, 246, b,
        f"Australian AI infrastructure spend is A${M.SAM_2026/1e6:.0f}M in 2026, up {(M.SAM_GROWTH-1)*100:.0f} percent; "
        f"1,000 nodes is {M.SHARE_1K*100:.1f} percent of it and 10,000 nodes {M.SHARE_10K*100:.1f} percent.")

# ── 6 · fleet break-even ─────────────────────────────────────────
def fleet():
    owned, sold, opex = M.FLEET.avg_owned, M.FLEET.avg_sold, M.COMPANY_OPEX
    FX0, FX1, FY0, FY1 = 132, 1104, 30, 182
    NMAX, FMIN, FMAX = 2000., -1_600_000., 4_400_000.
    fx = lambda n: FX0 + n/NMAX*(FX1-FX0); fy = lambda v: FY1 - (v-FMIN)/(FMAX-FMIN)*(FY1-FY0)
    fl = lambda r: f"M {fx(0):.1f} {fy(-opex):.1f} L {fx(NMAX):.1f} {fy(NMAX*r-opex):.1f}"
    bo, bs = M.FLEET.breakeven_owned, M.FLEET.breakeven_sold; b = ""
    for v in (-1_000_000, 0, 2_000_000, 4_000_000):
        y = fy(v); lab = "A$0" if v == 0 else (f"−A${abs(v)/1e6:.0f}M" if v < 0 else f"A${v/1e6:.0f}M")
        b += f'<line class="{"zero" if v==0 else "gridline"}" x1="{FX0}" y1="{y:.1f}" x2="{FX1}" y2="{y:.1f}"/>'
        b += f'<text class="tick" x="{FX0-12}" y="{y+5:.1f}" text-anchor="end" {st(F["tick"])}>{lab}</text>'
    for n in (0, 500, 1000, 1500, 2000):
        x = fx(n); b += f'<line class="gridline" x1="{x:.1f}" y1="{FY0}" x2="{x:.1f}" y2="{FY1}" opacity=".5"/>'
        b += f'<text class="tick" x="{x:.1f}" y="{FY1+30:.0f}" text-anchor="middle" {st(F["tick"])}>{n:,}</text>'
    b += (f'<path class="ln alt" d="{fl(sold)}"/><path class="ln base" d="{fl(owned)}"/>'
          f'<line class="ax" x1="{FX0}" y1="{FY0}" x2="{FX0}" y2="{FY1}"/>'
          f'<circle class="dot" cx="{fx(bo):.1f}" cy="{fy(0):.1f}" r="7"/>'
          f'<circle class="dot alt" cx="{fx(bs):.1f}" cy="{fy(0):.1f}" r="7"/>'
          f'<rect class="callout" x="{fx(bo)-58:.1f}" y="{fy(0)-48:.1f}" width="128" height="31" rx="8"/>'
          f'<text class="callout-t" x="{fx(bo)+6:.1f}" y="{fy(0)-27:.1f}" text-anchor="middle" {st(F["call"])}>{bo:,.0f} owned</text>'
          f'<text class="lbl" x="{fx(bs)-14:.1f}" y="{fy(0)+26:.1f}" text-anchor="end" {st(F["sub"])}>{bs:,.0f} sold</text>'
          f'<text class="val" x="{FX1-8:.1f}" y="{fy(NMAX*owned-opex)-12:.1f}" text-anchor="end" {st(F["val"])}>Company-owned</text>'
          f'<text class="axname" x="{FX0}" y="18" {st(F["ax"])}>Operating cash per year</text>'
          f'<text class="axname" x="{FX0}" y="{FY1+54:.0f}" {st(F["ax"])}>Nodes in the fleet</text>')
    svg("fleet.svg", 1160, FY1+66, b,
        f"Operating cash versus fleet size; company-owned break even at {bo:,.0f}, customer-owned at {bs:,.0f}.")

# ── 7 · cost stack ───────────────────────────────────────────────
def coststack():
    n = M.U_BASE
    pay = [("Homeowner revenue share", f"{M.BASE.owner_share:.0%} of gross revenue", n.to_owner),
           ("Node maintenance", "support, spares, replacement", M.UNIT_OM),
           ("Electricity", f"{n.kwh:,.0f} kWh, mostly surplus solar", n.energy)]
    free = ["Land", "Building &amp; cooling", "Grid connection", "Physical security &amp; staff"]
    LB0, LB1, RC, TOPY = 352, 648, 760, 64; mx = n.to_owner
    b = (f'<text class="axname" x="0" y="20" {st(F["ax"])}>What we pay for, per node per year</text>'
         f'<text class="axname" x="{RC}" y="20" {st(F["ax"])}>What we never pay for</text>'
         f'<line class="gridline" x1="{RC-52}" y1="34" x2="{RC-52}" y2="252"/>')
    for i, (nm, sub, v) in enumerate(pay):
        y = TOPY + i*64; cy = y+27; w = max(6.0, v/mx*(LB1-LB0))
        b += (f'<text class="lbl-b" x="0" y="{y+21:.0f}" {st(F["lbl"])}>{nm}</text>'
              f'<text class="lbl" x="0" y="{y+43:.0f}" {st(F["sub"])}>{sub}</text>'
              f'<rect class="bar-bad" x="{LB0}" y="{cy-17:.0f}" width="{w:.1f}" height="34" rx="4"/>'
              f'<text class="val" x="{LB0+w+15:.1f}" y="{cy+7:.0f}" {st(F["val"])}>A${v:,.0f}</text>')
    for i, nm in enumerate(free):
        y = TOPY + i*56; cy = y+22
        b += (f'<text class="lbl-b" x="{RC}" y="{cy+7:.0f}" {st(F["lbl"])}>{nm}</text>'
              f'<line class="zeroline" x1="1022" y1="{cy:.0f}" x2="1044" y2="{cy:.0f}"/>'
              f'<text class="zeroval" x="1060" y="{cy+8:.0f}" {st(24)}>A$0</text>')
    tot = n.to_owner + M.UNIT_OM + n.energy; margin = (n.gross-tot)/n.gross
    DIV = 282
    b += (f'<line class="ax" x1="0" y1="{DIV}" x2="1160" y2="{DIV}"/>'
          f'<text class="lbl-b" x="0" y="{DIV+38}" {st(F["lbl"])}>Total operating cost</text>'
          f'<text class="val" x="{LB0+18}" y="{DIV+39}" text-anchor="end" {st(25)}>A${tot:,.0f}</text>'
          f'<text class="lbl" x="{LB0+40}" y="{DIV+38}" {st(F["sub"])}>against A${n.gross:,.0f} of revenue</text>'
          f'<text class="callout-t" x="{RC}" y="{DIV+39}" {st(25)}>a {margin*100:.0f}% gross margin</text>')
    svg("coststack.svg", 1160, DIV+58, b,
        f"Annual operating cost of one node: homeowner share A${n.to_owner:,.0f}, maintenance A${M.UNIT_OM:,.0f}, "
        f"electricity A${n.energy:,.0f}; land, building and cooling, grid connection and physical security all zero. "
        f"Total A${tot:,.0f} against A${n.gross:,.0f} revenue, a {margin*100:.0f} percent gross margin.")


if __name__ == "__main__":
    arbitrage(); waterfall(); payback(); worst = tornado(); market(); fleet(); coststack()
    print(f"7 charts written to {os.path.normpath(OUT)}")
    print(f"  worst single-variable payback: {worst:.2f} yr")
