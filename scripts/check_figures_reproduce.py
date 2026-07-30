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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "research"))
import inputs as I

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "paper" / "evidence_ledger.md"
REGISTER = ROOT / "research" / "constraint_register.md"

# ── inputs ──────────────────────────────────────────────────────────────────
# Imported rather than redeclared. Every one of these used to be written out here as
# well as in two other scripts, which is the arrangement W-INTL-99 came out of: a
# quantity living in several files is a quantity that will eventually disagree with
# itself. research/inputs.py carries each with the measurement it came from.
TILE = I.TILE_AREA
TILE_LIMIT = I.TILE_LIMIT
UTILISATION = I.UTILISATION
OSC = I.OSCILLATOR_AREA
RHO = I.MIN_ENTROPY_DENSITY
KEY_BITS = I.KEY_BITS
DECODER = I.DECODER_AREA
LN2 = 0.6931471805599453

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


def check(text, name, label, pattern, expected, tol, required=True):
    """Compare a figure stated in prose against one recomputed from inputs.

    `required` distinguishes the document that must state the figure from ones that
    merely may. The first version guarded on whether a phrase appeared anywhere in the
    text, which fired on a paragraph *about* the check that quoted the phrase without a
    number - a check whose guard is looser than its pattern reports failures for prose
    rather than for arithmetic.
    """
    m = re.search(pattern, text)
    if not m:
        if required:
            failures.append(f"{name}: no figure found for {label} (pattern {pattern!r})")
        return
    got = float(m.group(1))
    if abs(got - expected) > tol:
        failures.append(
            f"{name}: {label} says {got:g}, recomputing from inputs gives "
            f"{expected:.2f} (tolerance {tol})"
        )


def rho_floor(n, k, blocks):
    """Lowest min-entropy density at which this construction still yields a key."""
    return 1 - (k - KEY_BITS / blocks) / n


def max_ber(n, t, blocks):
    lo, hi = 0.0, 0.5
    for _ in range(50):
        mid = (lo + hi) / 2
        if word_failure(n, t, blocks, mid) <= 1e-6:
            lo = mid
        else:
            hi = mid
    return lo


def recommendation():
    """The construction this project actually recommends, recomputed from inputs.

    W-INTL-147: the headline used to come from cheapest(RHO, 0.04) - no SLLC, no
    selection, a three-thousand-bit raw budget - which is the design as it stood eight
    loops ago. The ledger stated 8.49 tiles and this file recomputed 8.49 tiles, and
    they agreed because both were anchored to the same superseded operating point. A
    check that pins a document to a stale model is worse than no check: it reports green
    while the document is wrong.

    This recomputes what the recommendation is: reliable-bit selection at the design's
    fraction, the post-selection density, SLLC sized to the code's own generator degree,
    the manipulation countermeasure, and the shared-multiplier solver.
    """
    import reliable_bit_selection as R
    import selection_entropy as SE

    fraction = 1.0 - I.SELECTION_LOSS
    rho_sel = SE.density_for_bias(
        SE.selected_bias(SE.mean_for_density(RHO), I.SELECTION_LOSS)[0])
    need_k = KEY_BITS / rho_sel
    sigma = R.sigma_for_raw_ber(0.06)
    eff = R.selected_ber(sigma, fraction)[0]

    best = None
    for m in (7, 8):
        n = (1 << m) - 1
        for t, k in bch_parameters(m):
            area = I.decoder_area(m, t)
            if area is None:
                continue
            blocks = -(-int(need_k) // k)
            if word_failure(n, t, blocks, eff) > 1e-6:
                continue
            if k * blocks < need_k:
                continue
            selected = n * blocks
            raw = int(-(-selected // fraction) + 1e-9)   # ceil, without the
            # truncation that made this 478 where the design says 477
            osc = max(oscillator_floor(0), pairs_for(raw))
            cells = (area + I.SLLC_AREA.get(t, max(I.SLLC_AREA.values()))
                     + I.COUNTERMEASURE_AREA["spongent_permutation"] + osc * OSC)
            tiles = cells / UTILISATION / TILE
            if best is None or tiles < best[0]:
                best = (tiles, n, k, t, blocks, raw, osc, rho_sel)
    return best


def pairs_for(positions):
    """Oscillators needed to yield this many distinct pairs."""
    x = 2
    while x * (x - 1) // 2 < positions:
        x += 1
    return x


def check_selection_entropy():
    """The leakage bound must be checked against the density of the SELECTED bits.

    RHO is measured on unselected positions and the design discards a fifth of them.
    Selection keeps the positions furthest from the decision boundary, which are the
    positions most committed to a value, so the survivors are more biased than the
    population - Delvaux et al. name global thresholding as the scheme that amplifies
    bias the most, and this project's own source model reproduces it.

    The check is here rather than in a document because it is what would have caught
    the previous design: BCH(127,29,21) in five blocks carried 145 bits of k, and at
    the deeper selection fractions the analysis was quoting, 145 is not enough.

    All three ways it can fail were exercised before it was committed: no amplification
    (W-INTL-144), a document figure that disagrees, and a k that does not cover the
    requirement, which reproduces the previous design's failure.
    """
    import selection_entropy as SE

    mu = SE.mean_for_density(RHO)
    bias, _ = SE.selected_bias(mu, I.SELECTION_LOSS)
    rho_selected = SE.density_for_bias(bias)
    if rho_selected >= RHO:
        failures.append(
            "selection entropy: selection is computing no bias amplification, which "
            "means the source model has lost its offset - see W-INTL-144"
        )
        return None
    k_total = 57 * 3                      # the recommendation, BCH(127,57,11) x 3
    required = KEY_BITS / rho_selected
    if k_total < required:
        failures.append(
            f"selection entropy: the recommendation carries {k_total} bits of k and "
            f"needs {required:.1f} at the post-selection density {rho_selected:.4f}"
        )
    doc = ROOT / "research" / "decoder_code_choice.md"
    if doc.exists():
        check(doc.read_text(), "decoder_code_choice.md",
              "min-entropy density after selection",
              r"density after selection is ([0-9]\.[0-9]+)", rho_selected, 0.002)

    # Every model that reports this density must report the same one. The search table
    # used to display it by inverting a ceiled integer - KEY / need_k - which gave 0.9275
    # where the density is 0.9293, so two files reported two densities for one operating
    # point and neither was wrong on its own terms. Cross-checked here rather than
    # trusted, because the fix (one definition, imported) can be undone by anyone who
    # finds it convenient to recompute locally.
    import selection_with_bch as SW
    other = SW.density_at(1.0 - I.SELECTION_LOSS)
    if abs(other - rho_selected) > 1e-9:
        failures.append(
            f"selection entropy: selection_with_bch reports a post-selection density of "
            f"{other:.6f} where selection_entropy gives {rho_selected:.6f}")
    return rho_selected


def main():
    check_selection_entropy()

    # The headline: the construction recommended now, not the one recommended in loop 61.
    rec = recommendation()
    if rec is None:
        failures.append("model: nothing fits at the recommended operating point")
    else:
        tiles, n, k, t, blocks, raw, osc, rho_sel = rec
        docs = [(LEDGER, "evidence_ledger.md"),
                (ROOT / "research" / "decoder_code_choice.md", "decoder_code_choice.md")]
        for path, name in docs:
            if not path.exists():
                continue
            text = path.read_text()
            required = (name == "evidence_ledger.md")
            check(text, name, "tiles of sixteen at the recommendation",
                  r"([0-9]+\.[0-9]+) of the sixteen tiles", tiles, 0.02, required)
            check(text, name, "entropy density floor of the recommendation",
                  r"entropy density down to ([0-9]\.[0-9]+)", KEY_BITS / (k * blocks),
                  0.002, required)
            check(text, name, "oscillator floor",
                  r"oscillator floor is ([0-9]+) oscillators", osc, 0, required)

    at_measured = cheapest(RHO, 0.04)
    if at_measured is None:
        failures.append("model: no code fits at the measured entropy and 4 percent")
    else:
        # cheapest() is kept for one job only: it is the arrangement in which the
        # utilisation factor was dropped, so it still guards that. It is no longer the
        # source of any figure a document has to match.
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
    tiles, n, k, t, blocks, raw, osc, rho_sel = rec
    print(f"check_figures_reproduce: OK "
          f"(recommendation BCH({n},{k},{t}) x {blocks} at {tiles:.2f} of {TILE_LIMIT} "
          f"tiles, {raw} raw positions, {osc} oscillators, "
          f"post-selection density {rho_sel:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
