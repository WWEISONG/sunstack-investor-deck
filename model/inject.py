"""Swap freshly generated charts into index.html, matched by aria-label prefix."""
import os, re, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
HTML = os.path.join(ROOT, "index.html"); BUILD = os.path.join(ROOT, "build")

# file -> the leading words of the aria-label that identify the chart in index.html
KEYS = {"arbitrage.svg": "One kilowatt-hour of surplus",
        "waterfall.svg": "Waterfall:",
        "payback.svg":   "Cumulative cash per",
        "tornado.svg":   "Tornado chart of payback",
        "market.svg":    "Australian AI infrastructure spend",
        "fleet.svg":     "Operating cash versus fleet size",
        "coststack.svg": "Annual operating cost of one node"}
# the CSS size class each chart carries in the deck
CLS = {k: "chart tall" for k in KEYS}
CLS["market.svg"] = "chart"

def main():
    s = open(HTML).read(); done = []
    for fn, key in KEYS.items():
        new = open(os.path.join(BUILD, fn)).read().replace('class="chart"', f'class="{CLS[fn]}"')
        pat = re.compile(r'<svg class="chart[^"]*"[^>]*aria-label="' + re.escape(key) + r'[\s\S]*?</svg>')
        if not pat.search(s):
            print(f"  !! no match for {fn} (key: {key!r})"); continue
        s = pat.sub(lambda m: new, s, count=1); done.append(fn)
    for asset, attr in (("assets/css/deck.css", "css"), ("assets/js/deck.js", "js")):
        h = hashlib.sha1(open(os.path.join(ROOT, asset), "rb").read()).hexdigest()[:8]
        s = re.sub(re.escape(asset) + r'\?v=[a-f0-9]+', f'{asset}?v={h}', s)
    open(HTML, "w").write(s)
    print(f"injected {len(done)}/{len(KEYS)} charts + refreshed cache-busting hashes")

if __name__ == "__main__":
    main()
