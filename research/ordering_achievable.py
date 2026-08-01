#!/usr/bin/env python3
"""log2(R!) is an upper bound. What the ordering actually carries is less, and by enough.

W-INTL-240. W-INTL-239 compared the design's entropy accounting against log2(R!) and found
1.177 - the tightest margin in the design - while saying in as many words that the bound is
an upper bound because the frequencies are not a uniformly random permutation. This asks by
how much, and the answer is enough to matter.

Why the orderings are not equiprobable
--------------------------------------
Oscillator k has frequency mu_k + d_k: a systematic part fixed across devices, set by layout
and position, and a device-specific part which is the secret. If the systematic spread were
zero every ordering would be equally likely and the ceiling would be exact. It is not zero,
and this project has already measured the ratio - the same fit that W-INTL-231 used to turn
a Shannon figure into a min-entropy gives a systematic-to-device spread of 0.3737.

The min-entropy of the permutation is -log2 P(pi*), where pi* is the ordering of mu, because
that is the likeliest of the R! outcomes.

  R   log2(R!)   achievable   ratio    estimator valid
  8      15.30        13.06   0.853    yes
 10      21.79        18.23   0.837    yes
 12      28.84        24.04   0.834    yes
 14      36.30        30.75   0.847    yes
 16      44.25        43.89   0.992    NO
 18      52.52        55.74   1.061    NO

The validity column is a self-check with teeth: P(pi*) >= 1/R! always, since pi* is the most
likely of R! outcomes, so -log2 P can never exceed log2(R!). Above R = 14 the estimator
reports figures that exceed it, which is impossible, so those rows are discarded rather than
read. Sequential estimation of a probability this small has variance that grows with R, and
almost every finite sample underestimates.

What that leaves
----------------
The ratio sits near 0.84 across the valid range and does not trend within it, though it
varies by up to 0.13 with the particular systematic draw, which is physical - the deficit
depends on how spread the layout happens to make the frequencies.

Two ways to carry it to R = 54, and they disagree:

  constant ratio     0.84 x 237.1 = 199 bits
  constant deficit   0.4 bits per oscillator, 237.1 - 22 = 215 bits

against 201.4 bits the accounting claims. So the margin W-INTL-239 reported as 1.177 against
the ceiling is between **0.99 and 1.07** against what the ordering can actually deliver. The
design is at the boundary rather than inside it, and which side is not settled here.

This is the largest open question in the work. It is ahead of the temperature sweep, because
temperature decides between two answers that both exist, and this decides whether the
construction extracts a key the source can supply.

What would settle it
--------------------
An estimator that reaches R = 54. The one here fails at 16 and says so. A tighter analytic
bound on P(pi*) for independent Gaussians with unequal means would do it, and none was found
in the literature searched; so would exhaustive enumeration, which 54! forecloses.

Usage: ordering_achievable.py    prints the table, both extrapolations, and the consequence
"""

import math
import random
import sys
from statistics import NormalDist

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I
import min_entropy_from_shannon as M
import ordering_ceiling as OC
import selection_with_bch as S

ND = NormalDist()
LN2 = math.log(2.0)
TRIALS = 200_000
PROBE_R = (8, 10, 12, 14, 16, 18)
SEEDS = (7, 8, 9)


def _logsumexp(values):
    top = max(values)
    return top + math.log(sum(math.exp(v - top) for v in values))


def log2_p_most_likely(mu_sorted, trials=TRIALS, seed=11):
    """log2 P(the ordering matches mu), for independent f_k ~ N(mu_k, 1).

    Sequential estimation: draw the smallest unconstrained, then each next conditioned on
    exceeding the last, accumulating the log of each conditional probability. Averaged in
    log space, because the products underflow well before R reaches the design's scale.
    """
    rng = random.Random(seed)
    logs = []
    for _ in range(trials):
        total = 0.0
        x = mu_sorted[0] + rng.gauss(0.0, 1.0)
        ok = True
        for k in range(1, len(mu_sorted)):
            p = 1.0 - ND.cdf(x - mu_sorted[k])
            if p <= 1e-300:
                ok = False
                break
            total += math.log(p)
            u = min(max(rng.random() * p + (1.0 - p), 1e-15), 1.0 - 1e-15)
            x = mu_sorted[k] + ND.inv_cdf(u)
        if ok:
            logs.append(total)
    if not logs:
        return None
    return (_logsumexp(logs) - math.log(trials)) / LN2


def ratio_at(oscillators, spread=None, trials=TRIALS, seeds=SEEDS):
    """(mean ratio to log2(R!), spread over systematic draws, whether it is believable)."""
    if spread is None:
        spread = M.densities()[2]
    ceiling = math.lgamma(oscillators + 1) / LN2
    ratios = []
    for seed in seeds:
        rng = random.Random(seed)
        mu = sorted(rng.gauss(0.0, spread) for _ in range(oscillators))
        got = log2_p_most_likely(mu, trials, seed * 13)
        if got is None:
            return None, None, False
        ratios.append(-got / ceiling)
    return (sum(ratios) / len(ratios), max(ratios) - min(ratios),
            max(ratios) <= 1.0)


if __name__ == "__main__":
    rows = []
    print("Min-entropy of the ordering against log2(R!), which bounds it above.\n")
    print(f"{'R':>4} {'log2(R!)':>10} {'achievable':>11} {'ratio':>7} {'draw spread':>12} "
          f"{'valid':>6}")
    for oscillators in PROBE_R:
        ceiling = math.lgamma(oscillators + 1) / LN2
        mean, spread, valid = ratio_at(oscillators)
        print(f"{oscillators:>4} {ceiling:>10.2f} {mean * ceiling:>11.2f} {mean:>7.3f} "
              f"{spread:>12.3f} {'yes' if valid else 'NO':>6}")
        if valid:
            rows.append((oscillators, ceiling, mean))

    print("\nvalid means -log2 P does not exceed log2(R!), which it cannot: the most likely")
    print("of R! outcomes has probability at least 1/R!. Rows failing that are discarded.")

    ratio = sum(m for _, _, m in rows) / len(rows)
    deficit_per = sum(c * (1 - m) / r for r, c, m in rows) / len(rows)

    import importlib
    sys.path.insert(0, __file__.rsplit("/", 1)[0].rsplit("/", 1)[0] + "/scripts")
    rec = importlib.import_module("check_figures_reproduce").recommendation()
    _, n, k, t, blocks, _, oscillators, rho_sel = rec
    ceiling = math.lgamma(oscillators + 1) / LN2
    present = k * blocks * rho_sel

    by_ratio = ratio * ceiling
    by_deficit = ceiling - deficit_per * oscillators
    print(f"\nratio across the valid rows {ratio:.3f}, deficit {deficit_per:.3f} bits "
          f"per oscillator\n")
    print(f"at the recommendation's {oscillators} oscillators, against "
          f"{present:.1f} bits claimed:")
    print(f"  ceiling log2(R!)          {ceiling:>7.1f}   margin {ceiling / present:.3f}")
    print(f"  carried at constant ratio {by_ratio:>7.1f}   margin {by_ratio / present:.3f}")
    print(f"  carried at constant deficit {by_deficit:>5.1f}   margin "
          f"{by_deficit / present:.3f}")
    print("\nthe two extrapolations disagree and straddle the claim. The margin W-INTL-239")
    print("reported as 1.177 against the ceiling is at the boundary against what the")
    print("ordering can deliver, and which side is not settled by anything here.")
