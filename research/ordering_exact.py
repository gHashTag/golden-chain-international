#!/usr/bin/env python3
"""The ordering entropy, computed exactly, at the scale the design actually uses.

W-INTL-241, and it closes what W-INTL-240 opened one loop earlier by reporting a range
between 0.99 and 1.08 and saying the question was not settled by anything in this
repository. It is settled now, and the method needed no new information - only noticing
that the integral is one-dimensional.

Why the hard problem was not hard
---------------------------------
W-INTL-240 estimated P(pi*) - the probability of the likeliest ordering - by sequential
Monte Carlo, which has variance growing with R and produced impossible figures above
fourteen oscillators. The entry recorded that more trials would not help because the
failure is structural. That was true of that method and not of the problem.

The constraints f_1 < f_2 < ... < f_R form a CHAIN, and a chain of inequalities over
independent variables collapses an R-dimensional integral into a backward recursion in one
dimension:

    G_{R+1}(x) = 1
    G_k(x)     = integral from x to infinity of phi(y - mu_k) G_{k+1}(y) dy
    P(pi*)     = G_1(-infinity)

One pass per oscillator over a grid, with the running scale factored out so the numbers do
not underflow. No sampling, no extrapolation, and it runs at fifty-four oscillators in
under a second.

The self-test is exact. With all means equal every ordering is equally likely and P must be
exactly 1/R!; the recursion reproduces -log2(R!) to 0.02 bits at R = 54.

What it says
------------
  blocks  carried   osc   ceiling   achievable   present   margin
       4      228    44     180.8        163.8     134.3    1.220
       5      285    49     208.6        188.9     167.8    1.125
       6      342    54     237.1        215.3     201.4    1.069   <- the recommendation
       7      399    58     260.3        236.6     235.0    1.007
       8      456    62     284.0        258.7     268.6    0.963   <- fails

The recommendation holds at 1.069, and this is now the tightest margin in the design by a
wide gap - the borrowed-margin sweep's tightest row is 1.30.

**And the design is two blocks from unsound, not the four W-INTL-239 estimated against the
ceiling.** At seven blocks the margin is 1.007, which is the boundary within the spread that
layout alone produces: over five draws of the systematic offsets the six-block figure ranges
1.040 to 1.069, so a seven-block design would sit on either side depending on placement.

That matters because the last two corrections each added blocks - the density headroom rule
took three to four, the min-entropy correction four to six. One more of that size crosses.

The interaction nobody would have looked for
--------------------------------------------
W-INTL-236 found two answers to the worst temperature corner: more blocks, or a deeper
selection fraction. They are not equivalent here. Deeper selection needs far more raw
positions, so it needs far more oscillators, so it RAISES the ceiling faster than it raises
the claim - the nine-block construction at twenty percent retained uses 108 oscillators and
is not close to binding. More blocks at the declared fraction is the path that crosses.

Two answers that cost the same in area differ in whether the source can supply the key.

Usage: ordering_exact.py    prints the self-test, the table and the crossing
"""

import math
import random
import sys
from statistics import NormalDist

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I
import min_entropy_from_shannon as M
import selection_with_bch as S

ND = NormalDist()
LN2 = math.log(2.0)
GRID = 6000
SPAN = 16.0
DRAWS = (7, 8, 9, 10, 11)


def log2_p_ordered(mu_sorted, grid=GRID, span=SPAN):
    """log2 P(f_1 < f_2 < ... < f_R) for independent f_k ~ N(mu_k, 1). Exact by quadrature.

    Backward recursion over one dimension, rescaled at each step so that a probability of
    the order of 2^-240 does not underflow.
    """
    step = 2.0 * span / (grid - 1)
    xs = [-span + i * step for i in range(grid)]
    tail = [1.0] * grid
    log_scale = 0.0
    for mu in reversed(mu_sorted):
        weighted = [ND.pdf(xs[i] - mu) * tail[i] for i in range(grid)]
        running, suffix = 0.0, [0.0] * grid
        for i in range(grid - 2, -1, -1):
            running += 0.5 * (weighted[i] + weighted[i + 1]) * step
            suffix[i] = running
        top = max(suffix)
        if top <= 0.0:
            return None
        tail = [value / top for value in suffix]
        log_scale += math.log(top)
    return (log_scale + math.log(tail[0])) / LN2


def achievable_bits(oscillators, spread=None, seed=7):
    """Min-entropy of the ordering of R oscillators, for one draw of the layout offsets."""
    if spread is None:
        spread = M.densities()[2]
    rng = random.Random(seed)
    mu = sorted(rng.gauss(0.0, spread) for _ in range(oscillators))
    got = log2_p_ordered(mu)
    return None if got is None else -got


def at_blocks(blocks, k=57, n=127, keep=None, seed=7):
    """(carried, oscillators, ceiling, achievable, claimed present) at this block count."""
    if keep is None:
        keep = 1.0 - I.SELECTION_LOSS
    raw = int(n * blocks / keep + 0.999)
    oscillators = max(S.floor_ent(I.KEY_BITS), S._r(raw))
    return (k * blocks, oscillators, math.lgamma(oscillators + 1) / LN2,
            achievable_bits(oscillators, seed=seed), k * blocks * S.density_at(keep))


def crossing_block_count(limit=30, seed=7):
    """Fewest blocks at which the claim exceeds what the ordering can achieve."""
    for blocks in range(2, limit):
        _, _, _, achievable, present = at_blocks(blocks, seed=seed)
        if present > achievable:
            return blocks
    return None


if __name__ == "__main__":
    import importlib
    sys.path.insert(0, __file__.rsplit("/", 1)[0].rsplit("/", 1)[0] + "/scripts")
    _rec = importlib.import_module("check_figures_reproduce").recommendation()
    recommended, at_design = _rec[4], _rec[6]

    print("self-test: with equal means every ordering is equally likely, so P = 1/R!\n")
    print(f"{'R':>4} {'computed':>12} {'-log2(R!)':>12} {'error':>10}")
    # The last row is the design's own oscillator count, derived - check_no_stale_literals
    # caught it written as 54 in the first version of this file, which is the rule working
    # on the loop that added the rule's own eighth watched figure.
    for oscillators in (8, 20, at_design):
        got = log2_p_ordered([0.0] * oscillators)
        want = -math.lgamma(oscillators + 1) / LN2
        print(f"{oscillators:>4} {got:>12.4f} {want:>12.4f} {abs(got - want):>10.2e}")

    print("\nEntropy the accounting claims, against what the ordering achieves.\n")
    print(f"{'blocks':>7} {'carried':>8} {'osc':>5} {'ceiling':>9} {'achievable':>11} "
          f"{'present':>9} {'margin':>7}")
    for blocks in range(4, 9):
        carried, osc, ceiling, achievable, present = at_blocks(blocks)
        mark = ("   <- the recommendation" if blocks == recommended
                else "   <- fails" if present > achievable else "")
        print(f"{blocks:>7} {carried:>8} {osc:>5} {ceiling:>9.1f} {achievable:>11.1f} "
              f"{present:>9.1f} {achievable / present:>7.3f}{mark}")

    carried, osc, ceiling, achievable, present = at_blocks(recommended)
    spread = [achievable_bits(osc, seed=s) for s in DRAWS]
    print(f"\nover five draws of the layout offsets the achievable figure runs "
          f"{min(spread):.1f} to {max(spread):.1f} bits,")
    print(f"so the margin runs {min(spread) / present:.3f} to {max(spread) / present:.3f}.")
    print(f"\nthe accounting stops being sound at {crossing_block_count()} blocks, "
          f"{crossing_block_count() - recommended} beyond the recommendation -")
    print("W-INTL-239 said four, measuring against the ceiling rather than against what")
    print("the ordering achieves. The last two corrections added two blocks between them.")
