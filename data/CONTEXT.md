# SunStack investor deck — the underlying data

Everything the deck at **https://wweisong.github.io/sunstack-investor-deck/** asserts,
as machine-readable data. Written so a Claude Code session with no prior context can
pick this up and work with it.

## What SunStack is

An Australian marketplace that turns surplus rooftop solar into sovereign AI compute.
A small sealed computer sits in a homeowner's garage, runs AI inference on spare
midday solar, and the homeowner takes a cut of every job. Buyers get inference that
never leaves Australia. Three parties: homeowner (supply), SunStack (operator),
buyer (demand).

Team: three UNSW co-founders (Huadong Mo, Yuekang Li, Wei Song). A$2.4M of capital
already committed as a mix of research grants and equity. Working system deployed on
AWS: OpenAI-compatible API, vLLM for text, Z-Image Turbo for images, Qwen3-TTS for
speech, plus operator and buyer consoles.

## The economic argument in five numbers

| | |
|---|---|
| One node earns | **A$4,044** gross, **A$2,604** net per year (base case) |
| It costs | **A$4,000** all-in (A$2,800 hardware + A$400 install + A$800 platform) |
| So it pays back in | **1.5 years**, a 65% annual return on capital |
| Company overhead clears at | **488 owned nodes** (or 1,757 customer-owned) |
| We need | **0.55%** of eligible solar homes for 10,000 nodes |

The headline framing: one kWh of surplus rooftop solar earns **A$0.04** exported,
costs **A$0.30** to buy back at night, and produces **A$10.27** of inference —
**256× the export value**.

## Files

| File | Contents |
|---|---|
| `01_assumptions.csv` | Every input, with unit, VERIFIED/ESTIMATE status, and source or test |
| `02_unit_economics.csv` | Floor / base / upside per node, plus Spark-class. The core table |
| `03_cost_stack.csv` | Annual operating cost of one node; four of seven lines are zero |
| `04_sensitivity.csv` | Payback swing for each variable across its full range (tornado data) |
| `05_fleet_1000_nodes.csv` | 1,000-node P&L under three ownership mixes |
| `06_fleet_breakeven.csv` | Break-even fleet size, owned vs sold |
| `07_arbitrage.csv` | One kWh priced three ways |
| `08_market_and_supply.csv` | TAM / SAM / SOM and the supply funnel |
| `09_demand_segments.csv` | Who buys, and how big each segment is |
| `10_benchmarks.csv` | Every external figure the deck leans on, with source |
| `11_capital.csv` | What A$1M buys; use of funds |
| `sunstack-deck-data.json` | All of the above in one JSON |

## How to recompute

`model/model.py` in the repo is the single source of truth — every number here and in
the deck derives from it. The pipeline:

```
python model/model.py     # print the whole model
python model/charts.py    # regenerate all 7 SVG charts into build/
python model/inject.py    # swap them into index.html, refresh cache-busting hashes
python model/verify.py    # recompute all 34 headline claims and check the deck states them
python model/export.py    # regenerate this data/ directory
```

Change an assumption in `model.py`, run those five, and charts, tables and prose all
stay consistent. `verify.py` exits non-zero if the deck and the model disagree.

## Things a fresh session must not get wrong

1. **Two assumptions were tested and rejected**, and the deck says so on the record.
   An earlier internal model assumed **95 tok/s** and **A$10–12 per million tokens**.
   Both were wrong: throughput understated a *batched* serving node by ~9× (real
   benchmarks: 33.5→862.8 tok/s at 256 concurrent streams), and the price was ~8×
   above market for the open-weights models this hardware serves. Do not reintroduce
   them.

2. **The floor case is a floor, not a tail.** An earlier version stacked three
   independent downside assumptions at once and produced an 11.6-year payback. The
   current floor (220 tok/s, 8 h, 50%, A$1.50/M → 5.1 years) keeps each assumption
   individually defensible.

3. **Government is gated, not open.** The deck's demand slide originally claimed
   PROTECTED-classified government data as the wedge. It is the opposite: the Hosting
   Certification Framework requires facilities built to PSPF zone specifications with
   a discernible secure perimeter, which a residential garage cannot meet. Universities
   and research are the stated beachhead; government needs a certified enclave first.

4. **Video is marked "Live today" at the founder's instruction**, but the node repo
   contains no video model and `qwen3.5-0.8b` explicitly sets
   `--limit-mm-per-prompt {"image": 0, "video": 0}`. Confirm before repeating the claim.

5. **The supply funnel filters (80% owner-occupied, 70% serviceable, 75% suitable)
   are estimates, not measured.** The 4.3M denominator is real; the three filters are
   judgement. This is the softest number in the deck.

## What the deck deliberately excludes

GST, income tax, interest, grid/VPP revenue, subsidies, extra cooling, demand charges,
battery degradation, **the ramp to scale (no J-curve or cash trough)**, and **customer
acquisition cost**. The fleet figures are steady-state.

It is a decision model showing what has to be true — not a forecast, and not a promise
of returns. Confidential.
