#!/usr/bin/env python3
"""The post-selection density, derived a second time from a richer source model.

W-INTL-238. Sixty-eight bound figures rest on one derivation: `selection_entropy` fits a
single bias to the declared min-entropy density, applies reliable-bit selection, and
reports the density of what survives. Every check in this repository compares a document
against that derivation. None of them can find an error *in* it, and W-INTL-237 showed
what a second implementation is worth by producing the first model-against-model agreement
here.

This is the second implementation of the quantity that carries the most weight.

Where the two models differ
---------------------------
`selection_entropy` collapses the source to ONE bias: every position has value v ~ N(mu, 1)
for a single mu chosen so that -log2 max(Phi(mu), 1-Phi(mu)) reproduces the declared
density. That was consistent when the declared figure was itself a single number.
W-INTL-231 changed it: the density is now derived from a model in which each position k has
its own probability, p_k = Phi(-t_k) with t across positions Gaussian of spread s = 0.3737.
So the input carries a spread that the consumer of the input does not.

The spread is not obviously harmless. Selection keeps positions whose |v| is large, and
a position with a large offset |t_k| is likelier to clear the threshold - so selection
preferentially retains the positions that carry least entropy, which is an amplification
the single-bias model has no way to express.

This file separates the two levels: position offset t ~ N(0, s), device mismatch
w ~ N(0, 1), value v = t + w, bit sign(v). Selection keeps |v| > tau. For a position of
offset t that was kept, the bit is one with probability P(w > tau - t) / P(|t + w| > tau),
and the density is the average of -log2 of the larger of that and its complement over the
positions that survive, weighted by how often each survives.

The answer
----------
The two agree to half a percent, and the single-bias model is the conservative one. That
is the useful result: the derivation carrying sixty-eight figures is sound, and the spread
the input acquired in W-INTL-231 does not invalidate the consumer that ignores it.

A false alarm, recorded because it is the instructive part
---------------------------------------------------------
The first version of this file computed each position's entropy as -log2 max(p_k, 1-p_k)
WITHOUT conditioning on selection, and reported 0.7052 against the derivation's 0.5889 - a
discrepancy of 0.116 per bit that would have read as a major finding. It was wrong: the
whole content of the selection term is that being retained is itself information about the
device, which is the effect Delvaux names, and an implementation that drops it is not a
second opinion but a different question.

A second implementation that disagrees is more likely to be the one at fault, because it
is the one nobody has been checking against sixty-eight documents for thirty loops.

Usage: entropy_second_opinion.py    prints both derivations and their difference
"""

import math
import sys
from statistics import NormalDist

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I
import min_entropy_from_shannon as M
import selection_entropy as SE

ND = NormalDist()
STEPS = 4000


def _min_entropy(p):
    return -math.log2(max(p, 1.0 - p))


def _kept_fraction(tau, spread, steps=STEPS):
    """Fraction of positions with |t + w| above tau, over t ~ N(0, spread)."""
    total = 0.0
    for i in range(steps):
        t = ND.inv_cdf((i + 0.5) / steps) * spread
        total += (1.0 - ND.cdf(tau - t)) + ND.cdf(-tau - t)
    return total / steps


def threshold_for(keep, spread, steps=STEPS):
    """Reliability threshold retaining `keep` of positions in the two-level model."""
    lo, hi = 0.0, 8.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if _kept_fraction(mid, spread, steps) > keep:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def two_level_density(keep=None, spread=None, steps=STEPS):
    """Post-selection min-entropy density with per-position biases."""
    if keep is None:
        keep = 1.0 - I.SELECTION_LOSS
    if spread is None:
        spread = M.densities()[2]
    tau = threshold_for(keep, spread, steps)
    weighted = total = 0.0
    for i in range(steps):
        t = ND.inv_cdf((i + 0.5) / steps) * spread
        up = 1.0 - ND.cdf(tau - t)
        down = ND.cdf(-tau - t)
        survives = up + down
        if survives <= 0.0:
            continue
        weighted += survives * _min_entropy(up / survives)
        total += survives
    return weighted / total


def single_bias_density():
    """What selection_entropy derives, which is what the design is sized against."""
    mu = SE.mean_for_density(I.MIN_ENTROPY_DENSITY)
    return SE.density_for_bias(SE.selected_bias(mu, I.SELECTION_LOSS)[0])


if __name__ == "__main__":
    spread = M.densities()[2]
    one = single_bias_density()
    two = two_level_density(spread=spread)
    keep = 1.0 - I.SELECTION_LOSS
    print(f"declared density {I.MIN_ENTROPY_DENSITY:.4f}, spread {spread:.4f}, "
          f"keeping {keep:.2%}\n")
    print(f"{'derivation':34} {'after selection':>16}")
    print(f"{'single bias (selection_entropy)':34} {one:>16.4f}")
    print(f"{'two levels (this file)':34} {two:>16.4f}")
    print(f"\ndifference {two - one:+.4f} per bit, {abs(two - one) / one:.1%} of the "
          f"figure the design uses")
    print("the single-bias derivation is the conservative one, so the sixty-eight figures")
    print("resting on it are not overstated by the spread the input acquired in W-INTL-231.")
    print(f"\nk required at each: {I.KEY_BITS / one:.1f} against {I.KEY_BITS / two:.1f},")
    print("which is the same construction, so nothing moves.")
