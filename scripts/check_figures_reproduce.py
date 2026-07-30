#!/usr/bin/env python3
"""The load-bearing figures in the documents must be reproducible by running the model.

Written after W-INTL-99, where a utilisation factor was measured, recorded and applied in
one document and then absent from every figure computed in the next. Nothing was
overwritten and no step was wrong; the value simply did not make the journey between
files, and eighteen loops of tile counts were optimistic by 1.7 as a result.

The existing checks compare documents against each other. This one compares a document
against a computation, which is the only thing that would have caught it: the prose said
4.92 tiles, the script computed 4.92 tiles, and both were wrong together because they
shared the same missing step.

So this recomputes each headline from its definition - cell area, oscillator floor,
utilisation, tile size - and fails if a document disagrees. Anything added here must be
recomputed from inputs, not read from another file.

Exit code 1 on any mismatch. Intended to run in CI.
"""

import pathlib
import re
import sys
from math import comb, lgamma

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "paper" / "evidence_ledger.md"
REGISTER = ROOT / "research" / "constraint_register.md"

# ── inputs, each traceable to a measurement ─────────────────────────────────
TILE = 18_032                    # Tiny Tapeout tile, um^2, from the specification
TILE_LIMIT = 16                  # largest submission
UTILISATION = 0.58               # measured on the published tile: 20,900 of 36,064
INVERTER = 6_730 / 1_792         # measured: oscillator area over inverter count
OSC = 7 * INVERTER               # seven inverters per oscillator
RHO = 241.0 / 256                # measured min-entropy per response bit
KEY_BITS = 128
LN2 = 0.6931471805599453

# Decoder areas, each verified by end-to-end decoding before being quoted.
DECODER = {(7, 21): 79_787, (7, 23): 86_896, (7, 27): 102_267, (7, 31): 116_194,
           (8, 18): 90_254, (8, 30): 147_563, (8, 31): 152_170, (8, 42): 206_630,
           (8, 43): 211_985, (8, 45): 222_024, (8, 47): 231_431, (8, 55): 268_820,
           (9, 54): 304_465}

failures = []


def bch_parameters(m):
    n = (1 << m) - 1
    coset = {}
    for i in range(1, n):
        if i in coset:
            continue
        c, x = set(), i
        while x not in c:
            c.add(x)
            x = (2 * x) % n
        for e in c:
            coset[e] = frozenset(c)
    seen, best = set(), {}
    for d in range(1, n):
        if d in coset:
            seen |= coset[d]
        if d % 2 == 0:
            t, k = d // 2, n - len(seen)
            if k > 0 and (k not in best or t > best[k]):
                best[k] = t
    return sorted((t, k) for k, t in best.items())


def word_failure(n, t, blocks, p):
    per = sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(t + 1, n + 1))
    return 1 - (1 - per) ** blocks


def oscillator_floor(leakage):
    x = 2
    while lgamma(x + 1) / LN2 < leakage + KEY_BITS:
        x += 1
    return x


def cheapest(rho, ber, raw_budget=3000):
    """Cheapest measured code meeting both constraints, in tiles of die area."""
    best = None
    for m in (7, 8, 9):
        n = (1 << m) - 1
        blocks = raw_budget // n
        for t, k in bch_parameters(m):
            if (m, t) not in DECODER:
                continue
            if blocks * (k - n * (1 - rho)) < KEY_BITS:      # leakage
                continue
            if word_failure(n, t, blocks, ber) > 1e-6:        # error target
                continue
            leakage = n * blocks - k * blocks
            cells = DECODER[(m, t)] + oscillator_floor(leakage) * OSC
            tiles = cells / UTILISATION / TILE                # die, not cell, area
            if tiles > TILE_LIMIT:
                continue
            if best is None or tiles < best[0]:
                best = (tiles, n, k, t)
    return best


def check(text, name, label, pattern, expected, tol):
    m = re.search(pattern, text)
    if not m:
        failures.append(f"{name}: no figure found for {label} (pattern {pattern!r})")
        return
    got = float(m.group(1))
    if abs(got - expected) > tol:
        failures.append(
            f"{name}: {label} says {got:g}, recomputing from inputs gives "
            f"{expected:.2f} (tolerance {tol})"
        )


def main():
    at_measured = cheapest(RHO, 0.04)
    if at_measured is None:
        failures.append("model: no code fits at the measured entropy and 4 percent")
    else:
        tiles, n, k, t = at_measured
        if LEDGER.exists():
            check(LEDGER.read_text(), "evidence_ledger.md",
                  "tiles of sixteen at the recommended operating point",
                  r"([0-9]+\.[0-9]+) of the sixteen tiles", tiles, 0.05)

        # The high error-rate columns must be absent, which is what W-INTL-99 restored.
        for ber in (0.07, 0.08):
            if cheapest(RHO, ber) is not None:
                failures.append(
                    f"model: something fits at {ber:.0%} error rate, which contradicts "
                    f"W-INTL-99 - check the utilisation factor"
                )

    if REGISTER.exists():
        reg = REGISTER.read_text()
        if "58 percent" not in reg:
            failures.append("constraint_register.md: no utilisation figure in the area row")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_figures_reproduce: {len(failures)} failure(s)")
        return 1
    tiles, n, k, t = at_measured
    print(f"check_figures_reproduce: OK "
          f"(recommendation BCH({n},{k},{t}) at {tiles:.2f} of {TILE_LIMIT} tiles, "
          f"die area at {UTILISATION:.0%} utilisation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
