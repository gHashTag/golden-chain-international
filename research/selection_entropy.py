#!/usr/bin/env python3
"""What reliable-bit selection costs in min-entropy, which this project assumed was nothing.

The assumption is written down in reliable_bit_selection.py:

    The reliability of a position is |d|, and it is independent of the bit value sign(d)
    because the distribution of d is symmetric. That independence is the whole reason
    pointers to reliable positions can be published [...] It is a property of this
    source, and it is checked below rather than assumed.

It is not checked. Every sampler in that file draws `d = rng.gauss(0, 1)` - mean zero,
bias exactly one half - and the check reports a value share of 0.5000 because the
sampler was told to produce one. The symmetry that makes the independence true is a
parameter of the model, not a property of the measured source, and the check runs
inside it. That is the broken-ruler error: the instrument sits inside the assumption
under test.

The measured source is not symmetric. This project's entropy input is 241.0 bits of
min-entropy in 256 response bits, which is a bias of 0.5207, not 0.5000. And Delvaux,
Gu, Schellekens and Verbauwhede - the survey this project deferred reading for five
loops - state the consequence in their abstract:

    "We disprove the intuitive assumption that bit selection schemes have no leakage."

Their section VII.A treats global thresholding, which is the scheme used here: discard
positions whose reliability falls below a threshold. Their finding, section VII.D:

    "the larger Loss, the more bias amplification. Global thresholding amplifies bias
    the most."

and the pointer family this project costed in section 77 is the one that does not:

    "IBS and C-IBS do not amplify bias [...] Rather the opposite: they remove all bias."

So the question here is quantitative, and it is answerable in this project's own source
model: by how much does selecting the reliable positions amplify the bias that is
already measured, what does the resulting min-entropy density do to the leakage budget,
and at what selection fraction does the recommendation stop meeting it.

Two things are measured and one is assumed:

  measured   the output bias and min-entropy density of the selected positions, under
             ideal ranking, in closed form and by simulation
  measured   the same under the design's actual ranking - a majority vote over nine
             enrolment reads - which is coarser and cannot be done in closed form
  assumed    that the whole of the measured entropy deficit is bias rather than
             correlation between positions. Attributing all of it to bias makes the
             amplification larger, so the assumption is the pessimistic one; a source
             whose deficit is partly correlation loses less here and more elsewhere
"""

import random
import sys
from statistics import NormalDist

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I

ND = NormalDist()


# ── the source, with the bias the measurement actually reports ──────────────
# A position holds a device-fixed difference v, Gaussian, and emits sign(v + noise) on
# each read. reliable_bit_selection.py sets v ~ N(0, 1). The mean is set here instead
# from the measured min-entropy density: a density rho corresponds to a most-likely
# value of probability 2^-rho, and a mean of Phi^-1 of that.

def mean_for_density(rho):
    """Offset of the difference distribution that reproduces a min-entropy density."""
    return ND.inv_cdf(2.0 ** -rho)


def density_for_bias(b):
    """Min-entropy per bit of a Bernoulli with the given bias."""
    p = max(b, 1.0 - b)
    return -(p and __import__("math").log2(p))


def threshold_for_loss(mu, loss):
    """Reliability threshold discarding `loss` of positions, ranking by |v|."""
    lo, hi = 0.0, 12.0
    for _ in range(200):
        mid = (lo + hi) / 2
        discarded = ND.cdf(mid - mu) - ND.cdf(-mid - mu)
        if discarded < loss:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def selected_bias(mu, loss):
    """Bias of the positions that survive selection, ranking by the true |v|.

    Both tails shrink as the threshold rises, and the tail on the side of the mean
    shrinks more slowly. The ratio between them is what amplifies: as the threshold
    goes to infinity the far tail vanishes first and the bias goes to one.
    """
    t = threshold_for_loss(mu, loss)
    hi = 1.0 - ND.cdf(t - mu)
    lo = ND.cdf(-t - mu)
    return hi / (hi + lo), t


# ── the same thing sampled, so the closed form has a witness ────────────────
def sampled_bias(rng, mu, loss, sigma, reads, n=200000):
    """Selection as the design actually performs it: rank by a majority vote.

    Enrolment reads each position `reads` times and ranks by how lopsided the vote was,
    because it has no access to |v|. The vote is a coarse ranking - at nine reads it
    takes only five distinct values - so it selects a slightly different set, and the
    enrolled bit is the vote's majority rather than sign(v).
    """
    rows = []
    for _ in range(n):
        v = rng.gauss(mu, 1.0)
        votes = sum(1 for _ in range(reads) if v + rng.gauss(0, sigma) > 0)
        rows.append((abs(2 * votes - reads), 1 if 2 * votes > reads else 0))
    rows.sort(key=lambda r: -r[0])
    keep = rows[: max(1, int(round(n * (1 - loss))))]
    return sum(b for _, b in keep) / len(keep)


def ideal_sampled_bias(rng, mu, loss, n=200000):
    """Ranking by the true |v|, which is the closed form's own assumption."""
    vs = sorted((rng.gauss(mu, 1.0) for _ in range(n)), key=abs, reverse=True)
    keep = vs[: max(1, int(round(n * (1 - loss))))]
    return sum(1 for v in keep if v > 0) / len(keep)


if __name__ == "__main__":
    import math

    rng = random.Random(20260731)
    RHO = I.MIN_ENTROPY_DENSITY
    MU = mean_for_density(RHO)
    KEY = I.KEY_BITS
    READS = I.ENROLMENT_READS
    K_TOTAL = 57 * 3            # the recommendation: BCH(127,57,11), three blocks
    DESIGN_LOSS = 1 - 381 / 477  # the recommendation selects eighty percent

    print("1. the source, with the bias the measurement reports")
    print(f"   measured density {RHO:.4f} bits per position "
          f"({I.MIN_ENTROPY_BITS} in {I.MIN_ENTROPY_OVER})")
    print(f"   most-likely value {2**-RHO:.4f}, so the difference distribution "
          f"is offset by {MU:.4f}")
    print(f"   reliable_bit_selection.py models this offset as 0, which is the "
          f"assumption under test")

    print("\n2. selection amplifies the bias, in closed form and sampled")
    print(f"   {'loss':>6} {'threshold':>10} {'bias':>8} {'sampled':>9} "
          f"{'vote-ranked':>12} {'density':>8}")
    # Derived rather than frozen: the noise that reproduces the declared fresh-device
    # rate. It was the literal 0.1908 until W-INTL-200.
    import reliable_bit_selection as _R
    sigma = _R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    for loss in (0.0, 0.20, 0.40, 0.674, 0.80, 0.90):
        b, t = selected_bias(MU, loss)
        s_ideal = ideal_sampled_bias(rng, MU, loss)
        s_vote = sampled_bias(rng, MU, loss, sigma, READS)
        print(f"   {loss:6.1%} {t:10.4f} {b:8.4f} {s_ideal:9.4f} {s_vote:12.4f} "
              f"{density_for_bias(b):8.4f}")
    print("   sampled columns rank by the true |v| and by a nine-read vote; the vote")
    print("   is the design's own ranking and is coarser, so it selects a different set")

    print("\n3. what that does to the leakage budget")
    need_raw = KEY / RHO
    print(f"   the budget requires k of {need_raw:.1f} bits at the unselected density")
    print(f"   {'loss':>6} {'density':>8} {'k required':>11} {'k available':>12} "
          f"{'margin':>8}")
    for loss in (0.0, 0.20, 0.40, 0.674, 0.80, 0.90):
        b, _ = selected_bias(MU, loss)
        rho_sel = density_for_bias(b)
        need = KEY / rho_sel
        print(f"   {loss:6.1%} {rho_sel:8.4f} {need:11.1f} {K_TOTAL:12d} "
              f"{K_TOTAL - need:8.1f}"
              + ("   <- the recommendation" if abs(loss - DESIGN_LOSS) < 0.01 else ""))

    print("\n4. where it stops paying")
    lo, hi = 0.0, 0.9999
    for _ in range(200):
        mid = (lo + hi) / 2
        b, _ = selected_bias(MU, mid)
        if KEY / density_for_bias(b) <= K_TOTAL:
            lo = mid
        else:
            hi = mid
    b, _ = selected_bias(MU, lo)
    print(f"   the recommendation carries {K_TOTAL} bits of k, so it tolerates "
          f"selection down to")
    print(f"   {1 - lo:.2%} of positions kept - a loss of {lo:.2%}, at which the "
          f"selected bias is {b:.4f}")
    print(f"   and the density is {density_for_bias(b):.4f}. The design discards "
          f"{DESIGN_LOSS:.0%}.")

    print("\n5. the effect is real and it is small at this operating point")
    b, _ = selected_bias(MU, DESIGN_LOSS)
    rho_sel = density_for_bias(b)
    print(f"   density {RHO:.4f} before selection, {rho_sel:.4f} after, "
          f"a loss of {RHO - rho_sel:.4f} bits per position")
    print(f"   k required rises from {KEY/RHO:.1f} to {KEY/rho_sel:.1f} "
          f"against {K_TOTAL} available")
    print("   the recommendation survives. The claim that selection is free does not.")

    print("\n6. the design one loop ago did not survive it")
    # BCH(127,29,21) in five blocks carried 145 bits of k, not 171. The code was
    # re-chosen for area; the re-choice happens to have taken the leakage margin from
    # nine bits to thirty-three, and nobody was choosing for that.
    print(f"   {'design':>28} {'k':>5} " + "".join(f"{l:>9.0%}" for l in
                                                   (0.20, 0.674, 0.80, 0.90)))
    for label, kt in (("BCH(127,29,21) x 5 (loop 78)", 29 * 5),
                      ("BCH(127,57,11) x 3 (loop 79)", 57 * 3)):
        cells = []
        for loss in (0.20, 0.674, 0.80, 0.90):
            bb, _ = selected_bias(MU, loss)
            need = KEY / density_for_bias(bb)
            cells.append(f"{kt - need:>+9.1f}" if kt >= need else f"{'FAILS':>9}")
        print(f"   {label:>28} {kt:5d} " + "".join(cells))
    print("   margin in bits of k. The previous design fails the leakage bound at the")
    print("   selection fraction the routine's own table used in its deeper rows, and")
    print("   the margin at 67 percent was 1.4 bits. It was never checked because the")
    print("   source model had no bias to amplify.")
