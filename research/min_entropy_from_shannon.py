#!/usr/bin/env python3
"""The source figure is Shannon entropy. The construction needs min-entropy.

W-INTL-231. `MIN_ENTROPY_BITS = 241.0` has been the tightest input in this work for
thirty loops, and it is not a min-entropy. Wilde, Hiller and Pehl compute it as

    H = -sum_{k=0}^{255} ( p_k log2 p_k + (1-p_k) log2 (1-p_k) )                    (11)

introduced with the sentence "An upper bound for the entropy of the PUF still assuming
the bits to be independent can be derived from the sum of the bitwise entropies". That is
Shannon entropy, summed per bit, and the paper says so twice: it calls the quantity an
upper bound, and it reports "about 94% of the entropy achievable in 256 bits" - which is
the 0.9414 this project has been sizing a fuzzy extractor against.

A fuzzy extractor's output length is bounded by min-entropy, not by Shannon entropy. For a
biased bit the two differ by a lot and always in the same direction: a Bernoulli at p=0.64
has 0.94 bits of Shannon entropy and 0.64 bits of min-entropy. Using the larger one
overstates how much key material the source can yield, which is the unsafe direction.

The conversion, in the paper's own model
----------------------------------------
The paper models the per-bit probability as p_k = Phi(-t_k), where t_k is the ratio of the
mean to the standard deviation of the k-th difference across the 193 devices, and supports
normality for that difference by an Anderson-Darling test. Take t across the 256 positions
to be Gaussian with spread s - that is the assumption this file adds, and it is stated
rather than buried - and fit s so the Shannon sum reproduces the published 241.0. Then
evaluate the min-entropy sum on the same fitted model.

    s = 0.3737      Shannon 241.0 bits (0.9414 per bit, matching the paper)
                    min-entropy 183.3 bits (0.7162 per bit)

A bracket that needs no assumption about the shape
--------------------------------------------------
If every position carried the same bias, the bias reproducing 241.0 Shannon bits is
p = 0.6415, whose min-entropy density is 0.6404. The real source is not uniform - the paper
shows a spread, and spread helps, because positions near unbiased contribute nearly a full
bit of min-entropy. So 0.6404 is the pessimistic end and 0.9414 is an upper bound that
cannot be attained by any biased source. The answer is between them and the design should
survive either.

Usage: min_entropy_from_shannon.py   prints the fit and both readings
"""

import sys
from math import log2
from statistics import NormalDist

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I

ND = NormalDist()
STEPS = 200_001          # the quadrature is a one-off; accuracy is cheaper than cleverness


def _integrate(spread, f, steps=STEPS):
    """E[f(t)] for t ~ N(0, spread), by plain quadrature over twelve sigma."""
    lo, hi = -12 * spread, 12 * spread
    step = (hi - lo) / (steps - 1)
    total = 0.0
    for i in range(steps):
        t = lo + i * step
        total += ND.pdf(t / spread) / spread * step * f(t)
    return total


def _p(t):
    return min(max(ND.cdf(-t), 1e-15), 1.0 - 1e-15)


def shannon(p):
    return -(p * log2(p) + (1 - p) * log2(1 - p))


def min_entropy(p):
    return -log2(max(p, 1 - p))


def fitted_spread(target_density, steps=20_001):
    """Spread of the per-bit z-score reproducing a published Shannon density."""
    lo, hi = 0.01, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _integrate(mid, lambda t: shannon(_p(t)), steps) > target_density:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def densities():
    """(Shannon density, min-entropy density) of the source, from the published figure."""
    target = I.SHANNON_ENTROPY_BITS / I.MIN_ENTROPY_OVER
    s = fitted_spread(target)
    return (_integrate(s, lambda t: shannon(_p(t))),
            _integrate(s, lambda t: min_entropy(_p(t))), s)


def min_entropy_is_convex_in_shannon(points=40):
    """Check that min-entropy is a convex function of Shannon entropy, per bit.

    Verified on every run rather than asserted, because the bound below rests on it and a
    numerical claim nobody re-evaluates is the shape this project has found six times.

    Returns (intervals tested, intervals where the midpoint sits above the chord).
    """
    xs = [i / points for i in range(1, points)]
    violations = 0
    for lo, hi in zip(xs, xs[1:]):
        chord = (_min_entropy_at_shannon(lo) + _min_entropy_at_shannon(hi)) / 2
        if _min_entropy_at_shannon((lo + hi) / 2) > chord + 1e-12:
            violations += 1
    return len(xs) - 1, violations


def _bias_for_shannon(target):
    """The bias above one half whose Shannon entropy is `target`."""
    lo, hi = 0.5, 1.0 - 1e-15
    for _ in range(200):
        mid = (lo + hi) / 2
        if shannon(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _min_entropy_at_shannon(target):
    return min_entropy(_bias_for_shannon(target))


def distribution_free_bound():
    """The least min-entropy any bias distribution with this Shannon total can have.

    W-INTL-245, and it turns the pessimistic reading below from a choice into a theorem.

    The source has 256 independent positions whose Shannon entropies sum to the published
    241.0. Min-entropy of independent bits is the sum of the per-bit min-entropies, so the
    question is: over all ways of splitting 241.0 across 256 positions, what is the least
    that sum can be?

    Min-entropy is a CONVEX function of Shannon entropy per bit - checked above, not
    assumed - so by Jensen the sum is minimised when every position carries the same
    Shannon entropy. The equal-bias reading is therefore not one interpretation among
    several: it is the floor, and it holds for any distribution consistent with the
    published figure, including ones nobody has thought of.

    The ceiling is the published figure itself, since min-entropy never exceeds Shannon.

    So the true density lies in [0.6404, 0.9414] whatever the source does, the Gaussian
    fit puts it at 0.7162, and the design is sized against 0.7162 / 1.25 = 0.5730 - below
    the floor. The construction survives any bias distribution the source could have, not
    only the one this project assumed.
    """
    return _min_entropy_at_shannon(I.SHANNON_ENTROPY_BITS / I.MIN_ENTROPY_OVER)


def equal_bias_reading():
    """Min-entropy density if every position carried the same bias. The pessimistic end."""
    target = I.SHANNON_ENTROPY_BITS / I.MIN_ENTROPY_OVER
    lo, hi = 0.5, 0.999999
    for _ in range(80):
        mid = (lo + hi) / 2
        if shannon(mid) > target:        # shannon is decreasing above one half
            lo = mid
        else:
            hi = mid
    p = (lo + hi) / 2
    return p, min_entropy(p)


if __name__ == "__main__":
    sh, mn, s = densities()
    over = I.MIN_ENTROPY_OVER
    print(f"published Shannon figure  {I.SHANNON_ENTROPY_BITS:.1f} bits over {over}")
    print(f"fitted z-score spread     s = {s:.4f}\n")
    print(f"{'reading':38} {'bits':>8} {'per bit':>9}")
    print(f"{'Shannon, reproducing the paper':38} {sh*over:8.1f} {sh:9.4f}")
    print(f"{'min-entropy, same fitted model':38} {mn*over:8.1f} {mn:9.4f}")
    p, mn_flat = equal_bias_reading()
    print(f"{'min-entropy, equal bias p=%.4f' % p:38} {mn_flat*over:8.1f} {mn_flat:9.4f}")
    print(f"\nthe construction is sized against min-entropy density {mn:.4f}")
    print(f"declared in inputs.py as {I.MIN_ENTROPY_BITS} bits over {over}")
    tested, bad = min_entropy_is_convex_in_shannon()
    floor = distribution_free_bound()
    sized = I.MIN_ENTROPY_DENSITY / I.DENSITY_HEADROOM
    print(f"\nconvexity of min-entropy in Shannon entropy: {tested - bad} of {tested} "
          f"intervals, {bad} violations")
    print(f"so the equal-bias figure is a FLOOR over every bias distribution with this")
    print(f"Shannon total, not one reading among several - W-INTL-245.")
    print(f"  distribution-free floor   {floor:.4f}   ({floor * over:.1f} bits)")
    print(f"  Gaussian fit              {mn:.4f}")
    print(f"  ceiling, the published    {sh:.4f}")
    print(f"  the design is sized at    {sized:.4f}, "
          f"{'below the floor' if sized < floor else 'ABOVE THE FLOOR'}")

    print("\nShannon entropy is an upper bound on min-entropy and the paper calls its own")
    print("figure an upper bound as well. Sizing a fuzzy extractor against it overstates")
    print("the extractable key, which is the direction that costs a key rather than area.")
