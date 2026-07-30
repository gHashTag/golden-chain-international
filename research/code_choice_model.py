#!/usr/bin/env python3
"""Which error-correcting code the identity root should use, as a function of the
one quantity nobody has measured.

The previous loop measured two decoders and concluded the smaller one wins by a
factor of nineteen. That comparison was of decoders only, and decoders are not the
whole cost. A code with a low rate needs more raw response bits, raw bits need
oscillators, and oscillators take area too. This computes both sides.

Calibration before use. The model is checked against the published table it is
derived from - Bosch, Guajardo, Sadeghi, Shokrollahi and Tuyls, CHES 2008 - and
must reproduce that paper's own source-bit counts and word error probabilities
before any conclusion is drawn from it. If the check block below fails, nothing
downstream is worth reading.
"""

from math import comb, lgamma

LN2 = 0.6931471805599453

# ── measured inputs ─────────────────────────────────────────────────────────
# Synthesis against the SkyWater library at the typical corner, 2026-07-30.
# Every one of these decoded correctly in a self-checking testbench first.
DECODER_AREA = {
    "bch255_131_t18": 90_254,   # syndrome + Chien 23,407 corrected, solver 66,847
    "rep3_rm64":       4_596,   # R(1,6) majority logic + repetition, both decoders
    "rep3_rm32":       2_883,   # R(1,5) variant
    "bch127_15_t27":  102_267,  # syndrome + Chien 29,148 over GF(2^7), solver 73,119
                                # the table stages are the corrected ones, verified end to end;
                                # the figure they replace omitted the locator constant term
}

TILE = 18_032                   # one Tiny Tapeout tile, um^2
TILE_LIMIT = 16                 # largest submission, 8x2

# One seven-inverter ring oscillator, from the measured inverter area in the
# published tile: 6,730 um^2 across 1,792 inverters, seven per oscillator.
INVERTER_AREA = 6_730 / 1_792
RO_AREA = 7 * INVERTER_AREA

# Error-free bits needed before hashing to a 128-bit key. Taken from the paper
# rather than derived: it follows from the entropy per bit of the PUF they used,
# and this project's entropy per bit is not measured. Flagged, not fixed.
TARGET_BITS = 171


# ── the constructions ───────────────────────────────────────────────────────
# (label, repetition length, outer [n, k, d], decoder key)
CONSTRUCTIONS = [
    ("BCH(255,131) t=18, no repetition", 1, (255, 131, 37), "bch255_131_t18"),
    ("rep[3] + RM[64,7,32]",             3, (64, 7, 32),    "rep3_rm64"),
    ("rep[5] + RM[32,6,16]",             5, (32, 6, 16),    "rep3_rm32"),
    ("BCH(127,15) t=27",                 1, (127, 15, 55),  "bch127_15_t27"),
]


# ── the constraint this file was missing entirely ───────────────────────────
# Publishing helper data costs min-entropy. For a secure sketch over an (n,k)
# linear code the loss is bounded by n-k, which Gao, Su, Yang, Chen, Nepal and
# Ranasinghe (arXiv:1902.03031) call the well-known min-entropy loss and use as
# the design rule: prefer small n and small t, because a small t implies a large
# k, and a large k means fewer blocks are needed to reach a k-bit secret.
#
# Residual min-entropy per block is therefore  rho*n - (n-k)  where rho is the
# min-entropy per response bit. The count of blocks follows from the target key
# length, and the raw response width follows from the blocks.
#
# The first two versions of this file did not have this constraint at all, and
# the construction they recommended fails it outright.
MIN_ENTROPY_DENSITY = 241.0 / 256      # measured, Wilde/Hiller/Pehl
KEY_BITS = 128

# Debiasing overhead, if the response bias falls outside the range where adding raw
# bits is enough. Maes, van der Leest, van der Sluis and Willems report classic von
# Neumann debiasing costing a factor of about 4.4 at 50 percent bias and 5.3 at 30
# percent - and note that a PUF's usual reusability across enrolments does not
# necessarily survive a debiasing step, which matters for a registry that may
# re-enrol a die.
#
# Whether it is needed here is unmeasured. It is carried as a switch rather than
# folded in, because it decides whether one of the two oscillator arrangements fits
# at all.
DEBIAS_FACTOR = 4.4


def residual_entropy(rep, outer):
    """Min-entropy surviving publication of the helper data, per block."""
    n, k, _ = outer
    width = rep * n
    return MIN_ENTROPY_DENSITY * width - (width - k)


def blocks_for_key(rep, outer):
    """Blocks needed to reach KEY_BITS, or None if the block yields nothing."""
    r = residual_entropy(rep, outer)
    if r <= 0:
        return None
    return -(-KEY_BITS // int(r)) if int(r) else None


def tail(n, k_min, p):
    """P(at least k_min errors in n independent bits at rate p)."""
    if p <= 0.0:
        return 0.0
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k_min, n + 1))


def repetition_out(r, p):
    """Bit error rate out of a majority-decoded odd repetition code."""
    if r == 1:
        return p
    return tail(r, r // 2 + 1, p)


def word_error(rep, outer, p):
    """Word error probability for one outer codeword at input bit error rate p."""
    n, _, d = outer
    t = (d - 1) // 2
    return tail(n, t + 1, repetition_out(rep, p))


def raw_bits(rep, outer):
    """Raw response bits consumed.

    Two accountings, and the difference is the subject of W-INTL-63. The paper
    this model was first built from counts blocks by error-free output bits,
    ceil(171/k), which asks how much data the code delivers. The leakage bound
    asks how much secrecy survives publishing the helper data, and that is the
    binding question. Where a block has positive residual entropy the second
    accounting is used; where it does not, the construction is inadmissible and
    the first accounting is reported only so the gap is visible.
    """
    n, k, _ = outer
    blocks = blocks_for_key(rep, outer)
    if blocks is None:
        words = -(-TARGET_BITS // k)
        return rep * n * words, words
    return rep * n * blocks, blocks


def total_failure(rep, outer, p):
    _, words = raw_bits(rep, outer)
    return 1 - (1 - word_error(rep, outer, p)) ** words


# ── calibration against the published table ─────────────────────────────────
def calibrate():
    """The paper's Table 1 and Table 2 are the instrument check. Reproduce the
    numbers it states, or stop."""
    ok = True

    # Table 2, rep[3,1,3] with RM[64,7,32] at p_b = 0.15: source bits 4800.
    got, _ = raw_bits(3, (64, 7, 32))
    if got != 4800:
        print(f"  CALIBRATION FAIL: rep3+RM64 source bits {got}, paper says 4800")
        ok = False
    else:
        print(f"  ok  rep[3]+RM[64,7,32] source bits = {got}, matches the paper")

    # Same row, word error probability 1.02e-6.
    p1 = word_error(3, (64, 7, 32), 0.15)
    if not (0.5e-6 < p1 < 2.0e-6):
        print(f"  CALIBRATION FAIL: rep3+RM64 P1 = {p1:.3g}, paper says 1.02e-6")
        ok = False
    else:
        print(f"  ok  rep[3]+RM[64,7,32] P1 = {p1:.3g}, paper says 1.02e-6")

    # Table 2, rep[5,1,5] with RM[32,6,16]: 4640 source bits, P1 = 1.49e-6.
    got, _ = raw_bits(5, (32, 6, 16))
    if got != 4640:
        print(f"  CALIBRATION FAIL: rep5+RM32 source bits {got}, paper says 4640")
        ok = False
    else:
        print(f"  ok  rep[5]+RM[32,6,16] source bits = {got}, matches the paper")

    p1 = word_error(5, (32, 6, 16), 0.15)
    if not (0.7e-6 < p1 < 3.0e-6):
        print(f"  CALIBRATION FAIL: rep5+RM32 P1 = {p1:.3g}, paper says 1.49e-6")
        ok = False
    else:
        print(f"  ok  rep[5]+RM[32,6,16] P1 = {p1:.3g}, paper says 1.49e-6")

    # Table 1, plain BCH[511,19,239] at p_b = 0.15: P_total = 2.97e-7.
    p = tail(511, ((239 - 1) // 2) + 1, 0.15)
    if not (1e-7 < p < 9e-7):
        print(f"  CALIBRATION FAIL: BCH[511,19,239] {p:.3g}, paper says 2.97e-7")
        ok = False
    else:
        print(f"  ok  BCH[511,19,239] P_total = {p:.3g}, paper says 2.97e-7")

    return ok


# ── the oscillator regimes ──────────────────────────────────────────────────
# One oscillator per raw bit: the conservative reading, each response bit from its
# own physically distinct source.
def oscillators_one_per_bit(bits):
    return bits


# The pair count, which the budget document used and which is wrong as an entropy
# measure. Mansouri and Dubrova, arXiv:1207.4017, state the reason directly: for a
# traditional RO-PUF not all challenges are valid, because if A is faster than B
# and B faster than C then A is necessarily faster than C, so that third response
# is predictable from the other two. Frequency comparison is a total order.
#
# R(R-1)/2 therefore counts challenges a verifier may pose, not bits an attacker
# cannot predict. Retained only so the overstatement it produces stays visible.
def oscillators_pair_count(bits):
    n = 2
    while n * (n - 1) // 2 < bits:
        n += 1
    return n


# What the ordering carries: R oscillators ranked by frequency realise one of R!
# permutations, so at most log2(R!) bits are available however the pairs are read.
def ordering_entropy(n):
    return lgamma(n + 1) / LN2


# Measured entropy per oscillator. Wilde, Hiller and Pehl, arXiv:1910.07068,
# compute it from Maiti's silicon dataset - 512 oscillators on each of 193 parts,
# paired disjointly with their neighbours to give 256 response bits - and get 241.0
# bits by the bitwise estimate and 241.3 by a normal model, about 94 percent of what
# 256 bits could carry. That is 0.471 bits per oscillator, and the ordering bound for
# 512 oscillators is 3,875 bits, so practice sits a factor of sixteen below the
# bound. They also note the practically usable figure is lower still, because bits
# from pairs too close in frequency have to be masked for reliability.
ENTROPY_PER_OSCILLATOR = 241.0 / 512


# Two constraints, and the previous version of this file collapsed them into one.
#
# The code needs response bit positions: 4,800 of them for the recommended
# construction. Nothing about those positions has to be independent - the decoder
# consumes bits, and correlated bits decode as well as uncorrelated ones.
#
# The extractor needs min-entropy: 128 bits, plus whatever the helper data leaks.
# This is the constraint independence bears on.
#
# Requiring log2(R!) to exceed the count of response bits, as the previous version
# did, is neither of these. It demanded that the ordering entropy exceed a bit count
# that does not need to be entropy at all, and it happened to land inside the bracket
# below, which is why the number looked reasonable while the reasoning was not.
def oscillators_disjoint(bits):
    """Each response bit from its own pair, each oscillator used once. This is what
    the measured entropy figure was taken from, so it is the reading that carries a
    measurement rather than a bound."""
    return 2 * bits


def oscillators_reused(bits, leakage=0):
    """Oscillators shared across pairs: R of them supply R(R-1)/2 positions and carry
    log2(R!) bits of ordering. Both constraints are enforced, and the entropy one
    binds by a wide margin - positions need 77 oscillators where entropy needs 360."""
    n = 2
    while n * (n - 1) // 2 < bits:
        n += 1
    return max(n, entropy_floor(leakage))


def entropy_floor(leakage=0):
    """Oscillators needed for 128 bits of min-entropy SURVIVING the helper data.

    The version of this function that stood until 2026-07-30 returned 128 divided by
    the measured bits per oscillator and ignored the leakage entirely - it asked for
    128 bits of raw entropy rather than 128 bits that survive publication. That is
    exactly the distinction W-INTL-59 drew for response bits, drawn there and left
    undrawn here, in a second accounting feeding the same inequality.

    At the floor it returned, 272 oscillators, the ordering carries 1,813 bits against
    a leakage of 2,415: the residual is negative and the construction yields no key.
    """
    need = leakage + 128
    n = 2
    while ordering_entropy(n) < need:
        n += 1
    return n


def report(p_b, debias=False):
    tag = " with von Neumann debiasing" if debias else ""
    print(f"\n=== bit error probability {p_b:.3f}{tag} ===")
    header = f"{'construction':34} {'raw':>6} {'fail':>10} " \
             f"{'reuse':>7} {'disjoint':>9}  tiles"
    print(header)
    print("-" * len(header))
    for label, rep, outer, key in CONSTRUCTIONS:
        bits, _ = raw_bits(rep, outer)
        if debias:
            bits = int(bits * DEBIAS_FACTOR + 0.5)
        fail = total_failure(rep, outer, p_b)
        dec = DECODER_AREA[key]
        leakage = bits - (outer[1] * (blocks_for_key(rep, outer) or 1))
        lo = dec + oscillators_reused(bits, max(leakage, 0)) * RO_AREA
        hi = dec + oscillators_disjoint(bits) * RO_AREA
        ok = " " if fail <= 1e-6 else "!"
        star = lambda a: "*" if a / TILE > TILE_LIMIT else " "
        resid = residual_entropy(rep, outer)
        if resid <= 0:
            print(f"{label:34} {bits:6d} {fail:10.2e}{ok} "
                  f"   INADMISSIBLE: residual entropy {resid:.0f} after n-k leakage")
            continue
        print(f"{label:34} {bits:6d} {fail:10.2e}{ok} "
              f"{lo/TILE:6.2f}{star(lo)} {hi/TILE:8.2f}{star(hi)}")
    print("  ! word error probability worse than one in a million")
    print("  * does not fit the sixteen tiles a submission may use")
    print("  reuse: oscillators shared across pairs, floor set by log2(R!) exceeding")
    print("  the helper-data leakage plus 128, not by 128 alone - see W-INTL-77.")
    print("  disjoint: two oscillators per response bit, the arrangement the measured")
    print("  entropy figure was taken from. The bracket is wide because which one")
    print("  holds is not measured on this process.")


if __name__ == "__main__":
    print("Calibration against Bosch et al., CHES 2008:")
    if not calibrate():
        raise SystemExit("model does not reproduce the published table; stopping")
    print("\nDecoder areas are measured; oscillator areas scale a measured "
          "inverter area.\nThe error rate is the free variable because it is "
          "the one not measured.")
    for p in (0.02, 0.05):
        report(p)
    print("\nIf the response bias falls outside the range where extra raw bits are")
    print("enough, a debiasing stage comes first and costs a factor of 4.4:")
    report(0.05, debias=True)
