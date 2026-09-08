"""
SunStack investor deck — the single source of truth.

Every number in the deck derives from this file. Change an assumption here,
run `python charts.py && python inject.py && python verify.py`, and the
charts, tables and prose stay consistent.

Nothing in here is fitted to a desired answer: each assumption carries its
provenance in ASSUMPTIONS below, marked VERIFIED (third-party sourced) or
ESTIMATE (ours, with the test that would settle it).
"""
from dataclasses import dataclass

# ─────────────────────────── currency ───────────────────────────
AUD_PER_USD = 1 / 0.722          # AUD/USD 0.722, 7 Sep 2026

# ─────────────────────────── node cost ──────────────────────────
UNIT_HARDWARE   = 2800.0         # Ryzen AI Max+ 395 mini PC, 128 GB
UNIT_INSTALL    = 400.0
UNIT_PLATFORM   = 800.0          # allocated platform + deployment
UNIT_CAPEX      = UNIT_HARDWARE + UNIT_INSTALL + UNIT_PLATFORM   # 4,000

SPARK_HARDWARE  = 6500.0         # NVIDIA DGX Spark, 128 GB
SPARK_INSTALL   = 500.0
SPARK_PLATFORM  = 800.0
SPARK_CAPEX     = SPARK_HARDWARE + SPARK_INSTALL + SPARK_PLATFORM  # 7,800

UNIT_OM,  SPARK_OM     = 400.0, 500.0     # node maintenance / yr
UNIT_WATTS, SPARK_WATTS = 120.0, 200.0    # average draw while serving

GRID_PRICE      = 0.30           # A$/kWh bought from the grid
SOLAR_OPP_COST  = 0.05           # A$/kWh opportunity cost of surplus solar
SOLAR_SHARE     = 0.90           # share of node energy met by surplus solar
EXPORT_TARIFF   = 0.04           # A$/kWh paid for exported solar

# ─────────────────────── company / fleet ────────────────────────
COMPANY_OPEX    = 1_400_000.0    # ~9 FTE + infrastructure + G&A at 1,000 nodes
FLEET_UNITS, FLEET_SPARKS = 700, 300
SOLD_POOL_SHARE = 0.20           # our cut of a customer-owned node's pool
SOLD_PRICE      = 3900.0         # what a customer pays for a unit, installed
SOLD_COGS       = UNIT_HARDWARE + UNIT_INSTALL                     # 3,200

# ───────────────────────── market ───────────────────────────────
SAM_2026, SAM_GROWTH = 946e6, 1.284    # IDC: A$946M in 2026, +128.4% YoY
SAM_2025 = SAM_2026 / SAM_GROWTH
TAM_2030           = 15e9              # Australian AI market by 2030
SOLAR_HOMES        = 4.3e6             # DCCEEW / Clean Energy Regulator
OWNER_OCCUPIED, SERVICEABLE, SUITABLE = 0.80, 0.70, 0.75   # ESTIMATES
ELIGIBLE_HOMES     = SOLAR_HOMES * OWNER_OCCUPIED * SERVICEABLE * SUITABLE
ROOFTOP_TWH        = 40.0              # ~28.3 GW fleet annual output


@dataclass(frozen=True)
class Scenario:
    name: str
    tok_s: float          # aggregate throughput, batched
    hours: float          # hours serving per day
    utilisation: float    # share of those hours that are paid
    price: float          # A$ per million tokens, blended
    owner_share: float    # homeowner's cut of gross


FLOOR  = Scenario("floor",  220, 8,  0.50, 1.50, 0.30)
BASE   = Scenario("base",   300, 9,  0.60, 1.90, 0.25)
UPSIDE = Scenario("upside", 500, 10, 0.70, 2.60, 0.20)
SPARK  = Scenario("spark",  400, 9,  0.60, 1.90, 0.25)


def energy_cost(watts: float, hours: float) -> float:
    kwh = watts * hours * 365 / 1000
    return kwh * (SOLAR_SHARE * SOLAR_OPP_COST + (1 - SOLAR_SHARE) * GRID_PRICE)


def kwh_per_year(watts: float, hours: float) -> float:
    return watts * hours * 365 / 1000


class Node:
    """One node's annual economics under a scenario."""

    def __init__(self, sc: Scenario, capex: float, om: float, watts: float):
        self.sc, self.capex, self.om, self.watts = sc, capex, om, watts
        self.kwh      = kwh_per_year(watts, sc.hours)
        self.energy   = energy_cost(watts, sc.hours)
        self.tokens   = sc.tok_s * 3600 * sc.hours * 365 * sc.utilisation   # tokens/yr
        self.gross    = self.tokens / 1e6 * sc.price
        self.to_owner = self.gross * sc.owner_share
        self.net      = self.gross - self.to_owner - self.energy - self.om
        self.pool     = self.gross - self.energy - self.om     # distributable
        self.sold_net = self.pool * SOLD_POOL_SHARE            # if customer-owned

    @property
    def payback(self):  return self.capex / self.net
    @property
    def roc(self):      return self.net / self.capex


def unit(sc: Scenario) -> Node:   return Node(sc, UNIT_CAPEX,  UNIT_OM,  UNIT_WATTS)
def spark(sc: Scenario) -> Node:  return Node(sc, SPARK_CAPEX, SPARK_OM, SPARK_WATTS)

U_FLOOR, U_BASE, U_UP = unit(FLOOR), unit(BASE), unit(UPSIDE)
S_BASE = spark(SPARK)


class Fleet:
    """A 1,000-node fleet: 700 units + 300 Spark-class."""

    def __init__(self, units=FLEET_UNITS, sparks=FLEET_SPARKS, opex=COMPANY_OPEX):
        self.units, self.sparks, self.opex = units, sparks, opex
        self.capex    = units * UNIT_CAPEX + sparks * SPARK_CAPEX
        self.gross    = units * U_BASE.gross + sparks * S_BASE.gross
        self.contrib  = units * U_BASE.net   + sparks * S_BASE.net
        self.sold     = units * U_BASE.sold_net + sparks * S_BASE.sold_net
        self.n        = units + sparks

    @property
    def opcash(self):        return self.contrib - self.opex
    @property
    def roc(self):           return self.opcash / self.capex
    @property
    def payback(self):       return self.capex / self.opcash
    @property
    def avg_owned(self):     return self.contrib / self.n
    @property
    def avg_sold(self):      return self.sold / self.n
    @property
    def breakeven_owned(self): return self.opex / self.avg_owned
    @property
    def breakeven_sold(self):  return self.opex / self.avg_sold

    def mix(self, owned_frac: float):
        """Contribution and capital at an arbitrary owned/sold split."""
        c = owned_frac * self.contrib + (1 - owned_frac) * self.sold
        k = owned_frac * self.capex
        return c, k, c - self.opex


FLEET = Fleet()

# per A$1M of capital deployed into units
PER_M_UNITS = 1e6 / UNIT_CAPEX
PER_M_GROSS = PER_M_UNITS * U_BASE.gross
PER_M_NET   = PER_M_UNITS * U_BASE.net

# arbitrage: one kWh, three ways
KWH_AS_TOKENS = U_BASE.gross / U_BASE.kwh
KWH_RATIO     = KWH_AS_TOKENS / EXPORT_TARIFF

# market share required
SOM_1K, SOM_10K = FLEET.gross, FLEET.gross * 10
SHARE_1K, SHARE_10K = SOM_1K / SAM_2026, SOM_10K / SAM_2026
ELIGIBLE_SHARE_10K = 10_000 / ELIGIBLE_HOMES
ENERGY_SHARE_10K   = 10_000 * U_BASE.kwh / (ROOFTOP_TWH * 1e9)

ASSUMPTIONS = [
    ("VERIFIED", "Hardware specs and street prices", "AMD Ryzen AI Max+ 395 (128 GB, 256 GB/s); NVIDIA DGX Spark (128 GB, 273 GB/s, US$4,699)"),
    ("VERIFIED", "Batched throughput ceiling",       "DGX Spark concurrency benchmark 2026: gpt-oss 120B 33.5->862.8 tok/s; Nemotron 49B 5.8->695.1"),
    ("VERIFIED", "Token prices",                     "Groq/Fireworks/Together/DeepInfra/MiniMax published rates; global average A$1.61, Aug 2026"),
    ("VERIFIED", "Australian AI infra spend",        "IDC Australia: A$946M in 2026, +128% YoY"),
    ("VERIFIED", "Rooftop solar and tariffs",        "DCCEEW / Clean Energy Regulator: 4.3M systems; state regulators: 3-6c export, 30-40c retail"),
    ("VERIFIED", "Data centre PUE",                  "Uptime Institute Global Data Center Survey 2026: 1.52"),
    ("VERIFIED", "Demand segments",                  "ABS: 2.81M businesses, 12% using AI, A$16.4B higher-ed R&D; DTA: A$6B ICT, HCF/PSPF zoning"),
    ("ESTIMATE", "300 tok/s sustained on ROCm",      "TEST: reproduce the CUDA benchmarks on Ryzen AI Max before buying at volume"),
    ("ESTIMATE", "60% paid utilisation",             "TEST: 90-day metered pilot with paying design partners, not letters of intent"),
    ("ESTIMATE", "A$1.90/M blended price",           "TEST: signed, invoiced usage showing what the sovereignty premium is worth"),
    ("ESTIMATE", "A$1.4M company opex at 1,000",     "TEST: actual support hours and field-visit costs from the first cohort"),
    ("ESTIMATE", "Supply funnel 80/70/75%",          "TEST: conversion from the first 500 household approaches"),
    ("EXCLUDED", "Not modelled at all",              "GST, income tax, interest, grid/VPP revenue, subsidies, extra cooling, demand charges, battery degradation, ramp to scale, CAC"),
]


def dump():
    def row(k, v): print(f"  {k:34} {v}")
    print("\n=== PER-NODE (unit, A$%.0f all-in) ===" % UNIT_CAPEX)
    print(f"  {'scenario':10} {'tok/M':>9} {'gross':>9} {'owner':>8} {'net':>9} {'payback':>8} {'ROC':>6}")
    for n in (U_FLOOR, U_BASE, U_UP):
        print(f"  {n.sc.name:10} {n.tokens/1e6:9,.0f} {n.gross:9,.0f} {n.to_owner:8,.0f} "
              f"{n.net:9,.0f} {n.payback:7.2f}y {n.roc*100:5.0f}%")
    print(f"  {'spark(base)':10} {S_BASE.tokens/1e6:9,.0f} {S_BASE.gross:9,.0f} {S_BASE.to_owner:8,.0f} "
          f"{S_BASE.net:9,.0f} {S_BASE.payback:7.2f}y {S_BASE.roc*100:5.0f}%")

    print("\n=== COST STACK (base unit) ===")
    row("homeowner share",  f"A${U_BASE.to_owner:,.0f}")
    row("node maintenance", f"A${UNIT_OM:,.0f}")
    row("electricity",      f"A${U_BASE.energy:,.0f}  ({U_BASE.kwh:,.0f} kWh/yr)")
    row("total operating",  f"A${U_BASE.to_owner+UNIT_OM+U_BASE.energy:,.0f}")
    row("gross margin",     f"{(U_BASE.gross-(U_BASE.to_owner+UNIT_OM+U_BASE.energy))/U_BASE.gross*100:.1f}%")

    print("\n=== CUSTOMER-OWNED ===")
    row("distributable pool", f"A${U_BASE.pool:,.0f}")
    row("our 20% share",      f"A${U_BASE.sold_net:,.0f}")
    row("hardware margin",    f"A${SOLD_PRICE-SOLD_COGS:,.0f}")

    print("\n=== FLEET (1,000 nodes) ===")
    row("capital deployed", f"A${FLEET.capex/1e6:.2f}M")
    row("gross revenue",    f"A${FLEET.gross/1e6:.2f}M")
    row("node contribution",f"A${FLEET.contrib/1e6:.2f}M")
    row("operating cash",   f"A${FLEET.opcash/1e6:.2f}M")
    row("return on capital",f"{FLEET.roc*100:.0f}%")
    row("fleet payback",    f"{FLEET.payback:.1f}y")
    row("break-even owned", f"{FLEET.breakeven_owned:.0f} nodes")
    row("break-even sold",  f"{FLEET.breakeven_sold:.0f} nodes")
    for f, lbl in ((0.5, "50/50"), (0.0, "all sold")):
        c, k, o = FLEET.mix(f)
        row(f"mix {lbl}", f"contrib A${c/1e6:.2f}M  capex A${k/1e6:.2f}M  opcash A${o/1e6:.2f}M")

    print("\n=== ARBITRAGE ===")
    row("exported to grid",  f"A${EXPORT_TARIFF:.2f}/kWh")
    row("bought back",       f"A${GRID_PRICE:.2f}/kWh")
    row("as AI tokens",      f"A${KWH_AS_TOKENS:.2f}/kWh")
    row("ratio",             f"{KWH_RATIO:.0f}x")

    print("\n=== MARKET & SUPPLY ===")
    row("SAM 2026",           f"A${SAM_2026/1e6:.0f}M (+{(SAM_GROWTH-1)*100:.0f}% YoY from A${SAM_2025/1e6:.0f}M)")
    row("SOM @ 1,000 nodes",  f"A${SOM_1K/1e6:.2f}M = {SHARE_1K*100:.1f}% of SAM")
    row("SOM @ 10,000 nodes", f"A${SOM_10K/1e6:.1f}M = {SHARE_10K*100:.1f}% of SAM")
    row("eligible homes",     f"{ELIGIBLE_HOMES/1e6:.2f}M of {SOLAR_HOMES/1e6:.1f}M")
    row("10k as share",       f"{ELIGIBLE_SHARE_10K*100:.2f}% of eligible")
    row("energy draw @ 10k",  f"{ENERGY_SHARE_10K*100:.3f}% of national rooftop output")

    print("\n=== PER A$1M DEPLOYED ===")
    row("units", f"{PER_M_UNITS:.0f}")
    row("gross", f"A${PER_M_GROSS/1e6:.2f}M/yr")
    row("net",   f"A${PER_M_NET/1e6:.2f}M/yr")
    row("payback", f"{1e6/PER_M_NET:.2f}y")

    print("\n=== PROVENANCE ===")
    for kind, what, src in ASSUMPTIONS:
        print(f"  [{kind}] {what}\n           {src}")


if __name__ == "__main__":
    dump()
