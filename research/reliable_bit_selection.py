#!/usr/bin/env python3
"""Reliable-bit selection, measured against the row that removed the constraint.

W-INTL-115 recorded a comparison table from the cited dissertation in which
compressed Differential Sequence Coding reaches a one-in-a-million key error rate at
fifteen percent average bit error probability using 974 response bits and 1,108 helper
data bits, while every construction this project evaluated assumed all n positions had
to be corrected and needed 2,921 bits under syndrome and 635 under SLLC at less than
half that error rate.

Reading a row is not measuring it. The row is for an SRAM PUF; this project's source is
a ring-oscillator bank, and the reason DSC works is a property of the reliability
distribution, not of the code. So the question this file answers is narrower and
falsifiable: under this project's own source model, does selecting the reliable bits
give the error reduction the row depends on, does the compressed pointer encoding cost
what the row says it costs, and does the resulting response length beat 635.

Three things are measured here and one is asserted:

  measured   the effective error rate of the selected bits, as a function of how many
             are selected, in a ring-oscillator model whose raw error rate is set to
             match the row
  measured   the cost of the differential pointer encoding, in bits, against the
             thesis figure of 1,108
  measured   the avalanche of K = S xor f(W), the generic helper-data-manipulation
             countermeasure named in W-INTL-116 and absent from every design here
  asserted   nothing about slice count or area; no synthesis was run, and the 249
             slices in the row are not reproduced or endorsed

The failure mode this file is built against is the one W-INTL-117 named: adopting a
framing because a table in the literature looked better, without checking whether the
mechanism transfers to this source.
"""

import hashlib
import math
import random
from statistics import NormalDist

ND = NormalDist()

# ── the source model ────────────────────────────────────────────────────────
# A ring-oscillator pair emits sign(d + n). The device-fixed difference d is drawn once
# at manufacture; the measurement noise n is redrawn every read. Both are modelled
# Gaussian, d with unit variance by scaling, n with standard deviation SIGMA. The bit is
# wrong on a read when the noise crosses the difference, with probability Phi(-|d|/s).
#
# The reliability of a position is |d|, and it is independent of the bit value sign(d)
# because the distribution of d is symmetric. That independence is the whole reason
# pointers to reliable positions can be published: they say which positions are stable,
# not what they hold. It is a property of this source, and it is checked below rather
# than assumed.


def raw_ber(sigma):
    """Average bit error probability over the population of positions."""
    # E_d[Phi(-|d|/sigma)] with d ~ N(0,1); closed form is Phi(-1/sqrt(1+sigma^-2))
    # but the integral is done numerically so the model and the sampler cannot drift.
    steps, total = 4000, 0.0
    for i in range(steps):
        u = (i + 0.5) / steps
        d = ND.inv_cdf(u)
        total += ND.cdf(-abs(d) / sigma)
    return total / steps


def sigma_for_raw_ber(target):
    lo, hi = 1e-4, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if raw_ber(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def selected_ber(sigma, fraction):
    """Error rate of the most reliable `fraction` of positions, perfectly ranked.

    Perfect ranking is the optimistic bound: it assumes enrolment measures |d| exactly.
    The cost of estimating it from a finite number of enrolment reads is measured
    separately below, and it is not small.
    """
    # keep |d| >= thresh
    thresh = 0.0 if fraction >= 1.0 else ND.inv_cdf(0.5 + fraction / 2)
    steps, total = 4000, 0.0
    for i in range(steps):
        u = 0.5 + (1 - fraction) / 2 + (i + 0.5) / steps * (fraction / 2)
        d = ND.inv_cdf(u)
        total += ND.cdf(-d / sigma)
    return total / steps, thresh


# ── the pointer encoding ────────────────────────────────────────────────────
# Selecting a fraction f of positions and publishing them as absolute indices costs
# log2(N) per pointer. Differential Sequence Coding publishes the gaps instead. The gaps
# are geometric with parameter f, and the entropy of that geometric is the floor on what
# any entropy coder can reach.


def geometric_entropy(f):
    """Entropy in bits of the gap between consecutive selected positions."""
    if f >= 1.0:
        return 0.0
    q = 1 - f
    return -(f * math.log2(f) + q * math.log2(q)) / f


def pointer_cost(n_selected, n_total, f):
    return {
        "absolute": n_selected * math.log2(n_total),
        "differential_entropy_floor": n_selected * geometric_entropy(f),
    }


# ── the countermeasure ──────────────────────────────────────────────────────
def key_with_helper_binding(secret_bits, helper_bytes):
    """K = S xor f(W): the helper data is hashed into the key.

    W-INTL-116: this is the generic answer to helper-data manipulation, it costs one
    lightweight hash, it does not depend on the code, and no design in this repository
    currently does it.
    """
    s = hashlib.sha256(bytes(secret_bits)).digest()[:16]
    w = hashlib.sha256(helper_bytes).digest()[:16]
    return bytes(a ^ b for a, b in zip(s, w))


def avalanche(rng, trials=200):
    """Key bits changed by flipping one helper-data bit."""
    changed = []
    for _ in range(trials):
        secret = bytes(rng.getrandbits(8) for _ in range(64))
        helper = bytearray(rng.getrandbits(8) for _ in range(139))  # 1,108 bits
        k0 = key_with_helper_binding(secret, bytes(helper))
        bit = rng.randrange(len(helper) * 8)
        helper[bit // 8] ^= 1 << (bit % 8)
        k1 = key_with_helper_binding(secret, bytes(helper))
        changed.append(sum(bin(a ^ b).count("1") for a, b in zip(k0, k1)))
    return sum(changed) / len(changed), min(changed), max(changed)


# ── the length that has to beat 635 ─────────────────────────────────────────
def repetition_bits_needed(eff_ber, key_bits=128, target=1e-6):
    """Selected bits needed under a repetition code, per key bit, then in total.

    Repetition is what DSC is paired with in the source, and it is the construction
    with no helper data beyond the pointers. An odd repetition of length r fails when
    more than half its copies flip.
    """
    per_bit_target = target / key_bits
    for r in range(1, 200, 2):
        fail = sum(math.comb(r, i) * eff_ber**i * (1 - eff_ber)**(r - i)
                   for i in range(r // 2 + 1, r + 1))
        if fail <= per_bit_target:
            return r, r * key_bits, fail
    return None, None, None


def sample_check(rng, sigma, fraction, n=200000):
    """Sampled confirmation of selected_ber, and of value/reliability independence."""
    kept_err = kept = ones = 0
    thresh = 0.0 if fraction >= 1.0 else ND.inv_cdf(1 - fraction / 2)
    for _ in range(n):
        d = rng.gauss(0, 1)
        if abs(d) < thresh:
            continue
        kept += 1
        ones += 1 if d > 0 else 0
        if (d + rng.gauss(0, sigma) > 0) != (d > 0):
            kept_err += 1
    return kept_err / kept, ones / kept, kept


def selection_curve(sigma, reads, grid=1200):
    """Exact fraction/effective-error pairs for majority-vote selection.

    Enrolment reads a position `reads` times. The vote count k is binomial with
    parameter Phi(d/sigma). The enrolled bit is the majority; the confidence is the
    margin |2k - reads|. Selecting every position whose margin clears M gives one
    point on the curve, and sweeping M gives the curve. This is the achievable
    version of the perfect ranking in selected_ber, which assumes |d| is known
    exactly and is therefore a bound rather than a design.

    Returned: list of (margin, fraction selected, effective error rate).
    """
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
        if sel <= 0:
            continue
        out.append((margin, sel / grid, err / sel))
    return out


def enrolment_cost(rng, sigma, fraction, reads, n=120000):
    """Ranking by a finite number of enrolment reads instead of by the true |d|."""
    kept, err = [], 0
    for _ in range(n):
        d = rng.gauss(0, 1)
        votes = sum(1 if d + rng.gauss(0, sigma) > 0 else 0 for _ in range(reads))
        kept.append((abs(votes - reads / 2), d, 1 if votes * 2 > reads else 0))
    kept.sort(key=lambda t: -t[0])
    sel = kept[:int(n * fraction)]
    for _, d, enrolled in sel:
        if (1 if d + rng.gauss(0, sigma) > 0 else 0) != enrolled:
            err += 1
    return err / len(sel)


if __name__ == "__main__":
    rng = random.Random(20260730)
    ROW_BER, ROW_FRACTION = 0.15, 0.326
    ROW_RESPONSE, ROW_HELPER = 974, 1108

    print("1. the source model is set to the row's error rate")
    sigma = sigma_for_raw_ber(ROW_BER)
    print(f"   noise sigma {sigma:.4f} gives raw ber {raw_ber(sigma):.4f} "
          f"(target {ROW_BER})")
    samp, ones, kept = sample_check(rng, sigma, 1.0, 200000)
    print(f"   sampled raw ber {samp:.4f} over {kept} positions, "
          f"value share {ones:.4f}")

    print("\n2. does selecting the reliable bits give the row's error reduction")
    print(f"   {'selected':>9} {'effective ber':>14} {'sampled':>9} {'bit value':>10}")
    for f in (1.0, 0.60, 0.40, ROW_FRACTION, 0.20, 0.10):
        eff, _ = selected_ber(sigma, f)
        s_eff, s_ones, _ = sample_check(rng, sigma, f, 120000)
        print(f"   {f:9.3f} {eff:14.4f} {s_eff:9.4f} {s_ones:10.4f}")
    eff_row, _ = selected_ber(sigma, ROW_FRACTION)
    print(f"   the row states 0.027 at {ROW_FRACTION:.3f} selected; "
          f"this model gives {eff_row:.4f}")

    print("\n3. perfect ranking is a bound; enrolment reads a position a few times")
    print(f"   {'reads':>6} {'nearest fraction':>17} {'effective ber':>14} "
          f"{'perfect ranking':>16}")
    for reads in (1, 3, 7, 15, 31, 63):
        curve = selection_curve(sigma, reads)
        m, f, e = min(curve, key=lambda t: abs(t[1] - ROW_FRACTION))
        pb, _ = selected_ber(sigma, f)
        print(f"   {reads:6d} {f:17.3f} {e:14.4f} {pb:16.4f}")
    print(f"   the row's 0.027 sits between 7 and 15 enrolment reads at this fraction.")
    print(f"   sampled cross-check at 15 reads: "
          f"{enrolment_cost(rng, sigma, ROW_FRACTION, 15):.4f}")

    print("\n4. the pointer encoding, against the row's 1,108 helper bits")
    n_sel = round(ROW_RESPONSE * ROW_FRACTION)
    costs = pointer_cost(n_sel, ROW_RESPONSE, ROW_FRACTION)
    print(f"   {n_sel} pointers into {ROW_RESPONSE} positions")
    print(f"   absolute indices              {costs['absolute']:8.0f} bits")
    print(f"   differential, entropy floor   "
          f"{costs['differential_entropy_floor']:8.0f} bits")
    print(f"   the row states                {ROW_HELPER:8d} bits")

    print("\n5. response bits needed, with the enrolment cost carried")
    print(f"   {'raw ber':>8} {'reads':>6} {'selected':>9} {'eff ber':>9} {'rep':>4} "
          f"{'selected bits':>14} {'response bits':>14}")
    for rb in (0.15, 0.09, 0.06):
        sg = sigma_for_raw_ber(rb)
        for reads in (7, 15, 31, 63):
            best = None
            for _m, f, e in selection_curve(sg, reads):
                if f < 0.005:
                    continue
                r, tot, _ = repetition_bits_needed(e)
                if r is None:
                    continue
                resp = math.ceil(tot / f)
                if best is None or resp < best[0]:
                    best = (resp, f, e, r, tot)
            if best is None:
                print(f"   {rb:8.2f} {reads:6d} {'':>9} {'':>9} "
                      f"{'-':>4} {'-':>14} {'unreachable':>14}")
                continue
            resp, f, e, r, tot = best
            print(f"   {rb:8.2f} {reads:6d} {f:9.3f} {e:9.6f} {r:4d} "
                  f"{tot:14d} {resp:14d}")
    print("   SLLC, at 0.06 and below, needed 635 response bits, and read each")
    print("   position once. The reads column is the price of the comparison.")

    print("\n6. K = S xor f(W), the countermeasure absent from every design here")
    mean, lo, hi = avalanche(rng)
    print(f"   one helper bit flipped changes {mean:.1f} of 128 key bits "
          f"(range {lo}..{hi})")
    print("   the row's construction reports 88 of 128; both destroy the key.")
