# SunStack — The Economics

A web-based investor brief for [SunStack AI](https://sunstackai.com.au/): the economic model
behind a national network of solar-powered AI compute nodes.

**Live:** https://wweisong.github.io/sunstack-investor-deck/

## Scope

This is the **economics companion** to the SunStack product deck. It deliberately does not
re-tell the background story or demo the product — it answers the money questions:

| # | Slide | Chart |
|---|---|---|
| 01 | Cover — four headline numbers | |
| 02 | **The arbitrage** — one kWh priced three ways | bar, 257× |
| 03 | **What a node earns** — A$4,044 → A$2,604 | waterfall |
| 04 | **Payback** — 18 months | 5-yr cumulative cash + range |
| 05 | The two assumptions — price and throughput, both benchmarked | price bars |
| 06 | **What moves it** — sensitivity | tornado |
| 07 | **Who buys it** — demand segments and their size | market share bar |
| 08 | **Who hosts it** — 4.3M solar homes → 1.8M eligible | funnel |
| 09 | **1,000 nodes** — capital buys a 4× shorter road | break-even lines |
| 10 | Why the margin holds — the cost floor | bandwidth per dollar |
| 11 | Fact vs. estimate — what's verified, what's being tested | |
| 12 | Capital and use of funds | allocation bars |
| 13 | Appendix — full model, assumptions, sources | |

Nine of thirteen slides lead with a chart. Every headline claim carries a number and a source.
Charts are hand-authored inline SVG — no chart library and no CDN, so the deck renders
identically offline, in print, and in both light and dark slide treatments.

## Using it

| Action | How |
|---|---|
| Advance / go back | `↓` `→` `Space` / `↑` `←` |
| Jump to a slide | number keys `1`–`9`, or the dot rail on the right |
| First / last | `Home` / `End` |
| Export to PDF | press `P`, then "Save as PDF" (page size preset to 297 × 167 mm landscape) |

Deep links work — append `#s4` to open straight on the payback curve.

## Design

Inherits the design language of `sunstackai.com.au`: full-bleed tiles, a single sun-amber
accent (`#e8932a`), one shadow, tight display type, self-hosted Inter and JetBrains Mono.
No CDN calls at runtime.

Layout is verified with a Playwright audit across eleven viewports (1024×768 → 1920×1080,
including short 600–820px laptop heights, plus tablet and phone), checking for slides taller
than the viewport, horizontal overflow, off-screen elements, collapsed text columns, and stray
text nodes inside grid/flex containers.

## Structure

```
index.html          13 sections + inline SVG charts, self-contained
assets/css/deck.css design tokens, slide shell, components, print styles
assets/js/deck.js   keyboard nav, dot rail, progress bar, deep links
assets/fonts/       Inter + JetBrains Mono variable woff2 (self-hosted)
assets/img/         node photography
assets/logos/       backer logos
```

Static HTML — no build step. Edit and push; Pages redeploys.

## A note on the numbers

Every figure is either third-party verified or explicitly flagged as our own estimate; slide 13
separates the two and the appendix lists sources. Two assumptions from an earlier internal model
were tested against evidence and discarded:

- **95 tok/s throughput** — understates a *batched* serving node by roughly 9×. Published DGX
  Spark benchmarks show 33.5 → 862.8 tok/s (gpt-oss 120B) and 5.8 → 695.1 tok/s (Nemotron 49B)
  going from single-stream to 256 concurrent streams.
- **A$10–12 per million tokens** — roughly 8× the market rate for the open-weights models this
  hardware serves (Llama 3.3 70B at A$0.82–1.25, MiniMax M2 output at A$1.64, global average
  A$1.61). The deck models A$1.90.

Confidential. Figures are budget estimates and do not constitute a promise of returns.
