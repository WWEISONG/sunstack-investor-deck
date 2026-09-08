# SunStack — Investor Brief

A web-based investor deck for [SunStack AI](https://sunstackai.com.au/) — an Australian
marketplace that turns surplus rooftop solar into sovereign AI compute.

**Live deck:** see the Pages URL in the repository's About section.

## What this is

22 slides plus an appendix, covering the pitch an investor actually needs: the arbitrage,
why Australia, working-product traction, the operating model, verified pricing, unit
economics, the payback equation and its sensitivities, capital structure, 1,000-node fleet
economics, the moat, competition, market sizing, what is and isn't de-risked, roadmap,
capital and team.

## Design

Inherits the design language of `sunstackai.com.au` — Apple-style full-bleed tiles, a single
sun-amber accent (`#e8932a`), one shadow, tight display type, self-hosted Inter and
JetBrains Mono. No CDN calls at runtime.

## Using it

| Action | How |
|---|---|
| Advance / go back | `↓` `→` `Space` / `↑` `←` |
| Jump to a slide | number keys `1`–`9`, or the dot rail on the right |
| First / last | `Home` / `End` |
| Export to PDF | press `P`, then "Save as PDF" (page size is set to 297 × 167 mm landscape) |

Deep links work: append `#s10` to jump straight to a slide.

## Structure

```
index.html          all 23 sections, self-contained
assets/css/deck.css design tokens, slide shell, components, print styles
assets/js/deck.js   keyboard nav, dot rail, progress bar, deep links
assets/fonts/       Inter + JetBrains Mono variable woff2 (self-hosted)
assets/img/         node photography
assets/shots/       operator console screenshots
assets/logos/       backer logos
```

Static HTML — no build step. Edit and push; Pages redeploys.

## A note on the numbers

Every figure is either third-party verified or explicitly flagged as our own estimate; the
appendix separates the two and lists sources. Two assumptions from an earlier internal model
were tested against the market and rejected — a 95 tok/s throughput figure (far too low for
batched serving) and an A$10–12 per-million-token price (roughly 8× the market rate for the
models this hardware serves). The deck uses benchmarked throughput and market pricing
instead, and says so on the record.

Confidential. Figures are budget estimates and do not constitute a promise of returns.
