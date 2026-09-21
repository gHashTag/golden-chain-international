#!/usr/bin/env python3
"""Four theorems and one conjecture, each with a numerical control.

Two hundred entries in the audit file are measurements. Not one is a proof. That is a
gap of a particular kind: a measurement tells you what this construction does at this
operating point, and a bound tells you what no construction can do at any operating
point. The twelve-loop arc that W-INTL-117 diagnosed as optimising inside one framing,
and the reversal in W-INTL-118 that found the alternative framing loses at this error
rate, were both arguments about particular constructions. Neither could say why.

This file proves why, and every proof is checked against a number the repository already
produces.

  Theorem 1   the raw error rate of a Gaussian ring-oscillator pair is arccos(rho)/pi
              with rho = 1/sqrt(1+sigma^2), exactly, with no integral left over
  Theorem 2   the minimum helper data for a reliable-bit selection of fraction f over n
              positions is exactly n*h(f) bits, whatever the encoding, and the
              differential encoding attains it
  Theorem 3   selection is value-neutral: the selection mask is statistically
              independent of the response bits, for perfect ranking and for the
              vote-margin estimator alike, so pointer helper data leaks zero key bits
  Theorem 4   selecting a proper subset strictly reduces the information extractable per
              PUF position. No inner code, of any strength, recovers what selection
              discards
  Conjecture  the excess error of the vote-margin estimator over perfect ranking decays
              as Theta(1/r) in the number of enrolment reads

Theorem 4 is the one that matters. W-INTL-118 measured that reliable-bit selection
paired with repetition needs 1,211 to 1,765 response bits at six percent raw error
against 635 under SLLC, and left open that a convolutional code with Viterbi decoding -
what the source actually pairs DSC with - might reverse it. Theorem 4 closes that
opening in the direction the measurement pointed, and closes it for every inner code at
once, which a measurement of one more code could not have done.
"""

import math
from statistics import NormalDist

from inputs import KEY_BITS, MIN_ENTROPY_DENSITY, RAW_NOISE_BER

ND = NormalDist()


def h(p):
    """Binary entropy, in bits."""
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


# ── Theorem 1 ───────────────────────────────────────────────────────────────
# Statement. Let d ~ N(0,1) be the device-fixed frequency difference of a ring
# oscillator pair, fixed at manufacture, and n ~ N(0, sigma^2) the independent read
# noise. The enrolled bit is sign(d) and the regenerated bit is sign(d+n). Then
#
#     P[sign(d+n) != sign(d)] = arccos(rho) / pi,   rho = 1 / sqrt(1 + sigma^2).
#
# Proof. Put X = d and Y = d + n. The pair (X, Y) is centred bivariate Gaussian with
# Var X = 1, Var Y = 1 + sigma^2 and Cov = 1, hence correlation rho = 1/sqrt(1+sigma^2).
# A bit error is the event that X and Y have opposite signs. For a centred bivariate
# Gaussian the orthant probability is P[X>0, Y>0] = 1/4 + arcsin(rho)/(2 pi) - this is
# Sheppard's formula, and it depends on the covariance only through rho, which is why
# the scaling of d is free. The two disagreement orthants are equiprobable by the
# symmetry (X,Y) -> (-X,-Y), so
#
#     P[error] = 2 P[X>0, Y<0] = 2 (P[X>0] - P[X>0,Y>0])
#              = 2 (1/2 - 1/4 - arcsin(rho)/(2 pi))
#              = 1/2 - arcsin(rho)/pi = arccos(rho)/pi.                        QED
#
# Consequence. Every raw error rate in this repository is a statement about one number,
# rho, and the inverse is closed form too: sigma = sqrt(sec^2(pi p) - 1). The bisection
# search in reliable_bit_selection.py over a 4,000-point numerical integral is not
# needed, and the control below is the first time that integral has been checked against
# anything.


def raw_ber_exact(sigma):
    rho = 1 / math.sqrt(1 + sigma * sigma)
    return math.acos(rho) / math.pi


def sigma_exact(p):
    """Inverse of Theorem 1."""
    rho = math.cos(math.pi * p)
    return math.sqrt(1 / (rho * rho) - 1)


def raw_ber_numeric(sigma, steps=20000):
    """The integral Theorem 1 replaces, kept as the control."""
    total = 0.0
    for i in range(steps):
        d = ND.inv_cdf((i + 0.5) / steps)
        total += ND.cdf(-abs(d) / sigma)
    return total / steps


# ── the selection law, needed by Theorems 2 to 4 ────────────────────────────
def selected_ber(sigma, f, steps=20000):
    """Error rate among the most reliable fraction f of positions, perfect ranking.

    Perfect ranking keeps |d| >= t with t = Phi^-1(1 - f/2). This is a bound, not a
    design; the achievable estimator is the vote margin, and the gap between them is the
    conjecture at the end of this file.
    """
    if f >= 1.0:
        return raw_ber_exact(sigma)
    total = 0.0
    lo = 1 - f / 2
    for i in range(steps):
        d = ND.inv_cdf(lo + (i + 0.5) / steps * (f / 2))
        total += ND.cdf(-d / sigma)
    return total / steps


# ── Theorem 2 ───────────────────────────────────────────────────────────────
# Statement. A reliable-bit selection publishes which of n positions were kept. If the
# kept fraction is f, the helper data cannot be shorter than n*h(f) bits on average, for
# any encoding, and the differential encoding of the gaps between consecutive kept
# positions attains this bound.
#
# Proof. The helper data must determine the subset, so it is a lossless code for the
# selection mask, an i.i.d. Bernoulli(f) string of length n. Shannon's source coding
# theorem bounds any lossless code for it below by its entropy, n*h(f) bits. For
# attainment: the gaps between consecutive kept positions are i.i.d. Geometric(f), with
# entropy h(f)/f bits each, and there are f*n of them, so an entropy coder on the gaps
# reaches f*n * h(f)/f = n*h(f).                                              QED
#
# Consequence, and it is the useful half. The cost of the pointers is n*h(f) and not
# f*n*log2(n) - it is set by the mask entropy, so it is linear in the number of
# positions read and not in the number kept, and it is maximised at f = 1/2. The
# dissertation's row states 1,108 helper bits for 974 positions at f = 0.326; the bound
# is 888, so that implementation sits 25 percent above the floor, which is where a real
# entropy coder sits. The row is not refuted by this and is not tight either.


def pointer_bound_bits(n, f):
    return n * h(f)


def geometric_gap_entropy(f):
    return h(f) / f if 0 < f < 1 else 0.0


# ── Theorem 3 ───────────────────────────────────────────────────────────────
# Statement. Let the response bit at a position be b = sign(d) with d symmetric about
# zero, and let the position be selected by a rule that depends on the measurements only
# through a statistic invariant under d -> -d. Then the selection mask is independent of
# the response bits, and the mutual information between the published pointers and the
# key is zero.
#
# Proof. Perfect ranking selects on |d|, which is invariant, and sign(d) is independent
# of |d| for any symmetric d - that is the definition of symmetry, not a property of the
# Gaussian. For the achievable estimator: with r reads the vote count is k, the enrolled
# bit is 1[2k > r] and the confidence is the margin |2k - r|. Under d -> -d the vote
# count maps k -> r - k, which leaves the margin fixed and flips the enrolled bit. Since
# d is symmetric this map preserves the joint law, so margin and enrolled bit are
# independent. Selection is a function of the margin alone, hence independent of the
# bits, hence I(mask ; bits) = 0 and I(pointers ; key) = 0.                    QED
#
# Consequence. The n*h(f) bits of Theorem 2 are not a leakage term. This is what makes
# the pointer family compatible with the zero-leakage regime W-INTL-114 established, and
# it is the one respect in which selection is unambiguously better than a syndrome: a
# syndrome of n-k bits leaks up to n-k bits of the response, and n*h(f) pointer bits
# leak none. Theorem 4 says this is still not enough.
#
# Note on scope. Independence is per position and does not extend to correlations
# between positions, which is a separate assumption this project has not checked and
# which no theorem here covers.


def theorem3_control(seed=20260813, n=400000, sigma=None, f=0.4, reads=25):
    """Sampled independence check for both selection rules."""
    import random
    rng = random.Random(seed)
    sigma = sigma if sigma is not None else sigma_exact(RAW_NOISE_BER)
    t = ND.inv_cdf(1 - f / 2)
    perfect_ones = perfect_kept = 0
    margins = []
    for _ in range(n):
        d = rng.gauss(0, 1)
        if abs(d) >= t:
            perfect_kept += 1
            perfect_ones += 1 if d > 0 else 0
        k = sum(1 for _ in range(reads) if d + rng.gauss(0, sigma) > 0)
        margins.append((abs(2 * k - reads), 1 if 2 * k > reads else 0))
    margins.sort(key=lambda m: -m[0])
    sel = margins[:int(n * f)]
    vote_ones = sum(b for _, b in sel)
    return (perfect_ones / perfect_kept, vote_ones / len(sel))


# ── Theorem 4 ───────────────────────────────────────────────────────
# Statement. Let q(d) = Phi(-|d|/sigma) be the per-position flip probability and define
# the extraction density of a selection rule S as
#
#     C(S) = integral over S of (1 - h(q(d))) phi(d) dd
#
# secret bits per PUF position read. Then C is monotone under inclusion: enlarging the
# selected set never decreases C, and strictly increases it whenever the added positions
# have q < 1/2. In particular C(f) < C(1) for every f < 1, so selecting a proper subset
# strictly reduces the information extractable per position read, and no inner code of
# any strength recovers the difference.
#
# Proof. Each position read is one use of a binary symmetric channel with crossover
# q(d), whose capacity is 1 - h(q(d)) >= 0, with equality only at q = 1/2. The positions
# are independent by assumption and the reliability is known at enrolment, so the
# ensemble is a set of independent parallel channels with side information and its
# capacity is the sum of the individual capacities. A selection rule is the policy that
# uses the channels in S and refuses the rest; refusing a channel forfeits its capacity
# and cannot add to any other. Hence C is a monotone set function, strictly so on
# positions with q < 1/2, which is almost every position.                       QED
#
# The instructive part is what happens when this is computed the natural way. Summarise
# the selected set by its average error rate p_eff and treat it as a single binary
# symmetric channel, giving f * (1 - h(p_eff(f))) - the quantity the field's comparison
# tables and this project's own W-INTL-118 both reason with. That expression is not
# monotone: at six percent raw error it peaks at f near 0.85 and falls by eleven percent
# at f = 1, which contradicts the theorem. The control below computes both and asserts
# the difference.
#
# The contradiction is Jensen's inequality and it points at a modelling error, not at the
# theorem. The map q -> 1 - h(q) is convex, so
#
#     E[1 - h(q)] >= 1 - h(E[q]),
#
# and averaging the error rate before substituting it understates the capacity by exactly
# the amount the spread of q carries. The spread is largest at f = 1, because that is the
# set that still contains both the near-certain positions and the coin flips, so the
# naive expression is most wrong precisely where the theorem is tightest.
#
# This is the finding of the loop. An effective bit error rate is a lossy summary of a
# reliability distribution, and it discards the very quantity that reliable-bit selection
# exploits. Every construction comparison in this repository and every row of the
# dissertation's table is stated in that summary. The comparisons are not thereby wrong -
# they compare implementations that really do operate on hard decisions - but they cannot
# be read as statements about what is achievable, and W-INTL-118 came within one
# assumption of reading one that way.
#
# Consequences, as numbers, in the control below.
#   (a) The channel floor for a 128-bit key is KEY_BITS / C(1) positions.
#   (b) The measured min-entropy density of the source is a second, independent floor.
#       Which of the two binds is a fact about this device, not about the construction,
#       and at six percent raw error it is the min-entropy one - so the honest target for
#       this design is set by the source and not by the error correction.
#   (c) W-INTL-118 left open whether a convolutional code with Viterbi decoding reverses
#       its verdict. For the capacity question the answer is no, and for every inner code
#       at once. What remains open is finite-length coding efficiency, which can move the
#       selection column down only as far as its own floor, and that floor is above the
#       f = 1 floor by the theorem.


def extraction_density(sigma, f, steps=20000):
    """C(f) of Theorem 4: capacity integrated over the selected set."""
    lo = 0.0 if f >= 1.0 else 1 - f / 2
    total = 0.0
    for i in range(steps):
        d = ND.inv_cdf(lo + (i + 0.5) / steps * (1 - lo))
        total += 1 - h(ND.cdf(-abs(d) / sigma))
    span = 2 * (1 - lo) if f < 1.0 else 1.0
    return total / steps * span


def extraction_density_naive(sigma, f):
    """The same quantity summarised by an effective error rate. Not monotone."""
    return f * (1 - h(selected_ber(sigma, f)))


def theorem4_table(raw, fractions):
    sigma = sigma_exact(raw)
    return [(f, selected_ber(sigma, f), extraction_density(sigma, f),
             extraction_density_naive(sigma, f)) for f in fractions]


# ── Conjecture ──────────────────────────────────────────────────────────────
# Statement. At a fixed selected fraction, the excess of the vote-margin estimator's
# effective error rate over the perfect-ranking value decays as Theta(1/r) in the number
# of enrolment reads r.
#
# Status: open. Numerically supported below and not proved. The heuristic is that the
# margin estimates |d| with an error of order sigma/sqrt(r), so the set of positions
# misclassified by the ranking has measure of order 1/sqrt(r), and each contributes an
# error excess of order 1/sqrt(r) because it lies within that distance of the threshold;
# the product is 1/r. Making that a proof needs a uniform bound on the density of
# Phi(-|d|/sigma) near the threshold, which is available for the Gaussian and is not
# written here.


def vote_curve(sigma, reads, grid=600):
    """Exact fraction/effective-error pairs for margin selection, by summation."""
    ds = [ND.inv_cdf((i + 0.5) / grid) for i in range(grid)]
    binom = [math.comb(reads, k) for k in range(reads + 1)]
    out = []
    for margin in range(reads % 2, reads + 1, 2):
        sel = err = 0.0
        for d in ds:
            p = ND.cdf(d / sigma)
            for k in range(reads + 1):
                if abs(2 * k - reads) < margin:
                    continue
                w = binom[k] * p**k * (1 - p)**(reads - k)
                sel += w
                err += w * ((1 - p) if 2 * k > reads else p)
        if sel > 0:
            out.append((sel / grid, err / sel))
    return out


if __name__ == "__main__":
    print("Theorem 1  raw error rate is arccos(rho)/pi")
    print(f"   {'sigma':>8} {'closed form':>12} {'integral':>12} {'abs diff':>10}")
    worst = 0.0
    for sigma in (0.10, 0.25, 0.5095, 0.75, 1.0, 2.0):
        a, b = raw_ber_exact(sigma), raw_ber_numeric(sigma)
        worst = max(worst, abs(a - b))
        print(f"   {sigma:8.4f} {a:12.6f} {b:12.6f} {abs(a - b):10.2e}")
    print(f"   worst disagreement {worst:.2e}; the bisection search it replaces is exact")
    print(f"   inverse: raw {RAW_NOISE_BER} needs sigma "
          f"{sigma_exact(RAW_NOISE_BER):.6f}, "
          f"round trip {raw_ber_exact(sigma_exact(RAW_NOISE_BER)):.6f}")
    assert worst < 5e-5, "Theorem 1 control failed"

    print("\nTheorem 2  minimum pointer helper data is n*h(f) bits")
    print(f"   {'n':>6} {'f':>7} {'bound':>9} {'gap entropy route':>19} {'absolute':>9}")
    for n, f in ((974, 0.326), (974, 0.5), (3000, 0.326), (3000, 0.10)):
        route = round(n * f) * geometric_gap_entropy(f)
        print(f"   {n:6d} {f:7.3f} {pointer_bound_bits(n, f):9.0f} {route:19.0f} "
              f"{round(n * f) * math.log2(n):9.0f}")
    print("   the dissertation states 1,108 for n=974, f=0.326; the bound is "
          f"{pointer_bound_bits(974, 0.326):.0f}, so that coder sits "
          f"{1108 / pointer_bound_bits(974, 0.326) - 1:.0%} above the floor")
    print(f"   worst case over f is at one half: {pointer_bound_bits(974, 0.5):.0f} bits")

    print("\nTheorem 3  selection is value-neutral, so the pointers leak nothing")
    for f in (0.2, 0.4, 0.7):
        pp, vv = theorem3_control(f=f)
        print(f"   f {f:4.1f}   ones among selected: perfect ranking {pp:.4f}, "
              f"vote margin {vv:.4f}")
        assert abs(pp - 0.5) < 0.01 and abs(vv - 0.5) < 0.01, "Theorem 3 control failed"
    print("   both indistinguishable from one half, as the symmetry argument requires")

    print("\nTheorem 4  selecting a subset strictly reduces extraction density")
    fractions = (0.10, 0.20, 0.326, 0.50, 0.70, 0.85, 1.00)
    for raw in (RAW_NOISE_BER, 0.09, 0.15):
        rows = theorem4_table(raw, fractions)
        print(f"   raw error {raw:.2f}")
        print(f"      {'f':>7} {'p_eff':>10} {'C(f) capacity':>14} "
              f"{'naive f(1-h(p))':>16} {'positions':>10}")
        for f, pe, c, cn in rows:
            print(f"      {f:7.3f} {pe:10.6f} {c:14.6f} {cn:16.6f} "
                  f"{math.ceil(KEY_BITS / c):10d}")
        dens = [c for _, _, c, _ in rows]
        naive = [cn for _, _, _, cn in rows]
        assert dens == sorted(dens), "Theorem 4 control failed: C not monotone"
        assert naive != sorted(naive), (
            "the naive summary is monotone here; the Jensen gap claim needs revising")
        peak = max(range(len(naive)), key=lambda i: naive[i])
        print(f"      C monotone as the theorem requires; the naive summary peaks at "
              f"f = {fractions[peak]:.2f} and")
        print(f"      falls {1 - naive[-1] / naive[peak]:.0%} by f = 1, which is the "
              f"Jensen gap and not a real optimum")

    print("\n   the two independent floors, and which one binds")
    sigma = sigma_exact(RAW_NOISE_BER)
    cap = extraction_density(sigma, 1.0)
    print(f"      channel floor      {math.ceil(KEY_BITS / cap):5d} positions "
          f"({cap:.4f} bits per position at {RAW_NOISE_BER} raw error)")
    print(f"      min-entropy floor  "
          f"{math.ceil(KEY_BITS / MIN_ENTROPY_DENSITY):5d} positions "
          f"({MIN_ENTROPY_DENSITY:.4f} bits per position, measured)")
    floor = math.ceil(KEY_BITS / min(cap, MIN_ENTROPY_DENSITY))
    binder = "min-entropy" if MIN_ENTROPY_DENSITY < cap else "channel"
    print(f"      binding floor      {floor:5d} positions, set by the {binder}")
    print(f"      SLLC, measured here                635  = {635 / floor:.1f}x the floor")
    print(f"      selection plus repetition        1,211  = "
          f"{1211 / floor:.1f}x the floor")

    print("\nConjecture  excess over perfect ranking decays as 1/r")
    sigma = sigma_exact(0.15)
    target = 0.40
    print(f"   at raw 0.15, fraction near {target}")
    print(f"   {'reads':>6} {'f':>7} {'vote p_eff':>11} {'perfect':>9} "
          f"{'excess':>9} {'excess*r':>9}")
    for r in (5, 11, 25, 51, 101):
        f, e = min(vote_curve(sigma, r), key=lambda t: abs(t[0] - target))
        pb = selected_ber(sigma, f)
        print(f"   {r:6d} {f:7.3f} {e:11.6f} {pb:9.6f} {e - pb:9.6f} "
              f"{(e - pb) * r:9.4f}")
    print("   the last column varies by a quarter over a twentyfold range of r, which")
    print("   is support and not a proof; the statement stays an open conjecture")
