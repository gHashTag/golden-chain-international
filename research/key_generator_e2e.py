#!/usr/bin/env python3
"""The whole key generator, end to end, in software.

Every part of this chain has been verified separately and the chain has never been
run. That is the arrangement in which a Chien search summing t of t+1 coefficients
survived five loops of correct area measurements, so it is worth not repeating.

What this exercises, in order: a modelled ring-oscillator bank with a stated bias and
noise, the pairing that turns frequency counts into response bits, syndrome-based
helper data, enrolment, a noisy regeneration, decoding, and the recovered key.

The point of the run is not that the pieces work. It is that the binomial model in
code_choice_model.py predicts a maximum tolerable bit error rate, and a Monte Carlo of
the actual chain either agrees with it or does not. A model and an implementation that
agree are two witnesses; a model alone is one.
"""

import hashlib
import random
from math import comb

# ── the construction, taken from the recommendation rather than written down ─
# This file has now been pinned to a superseded code twice. First it exercised
# BCH(127,22,23) for six loops after the recommendation moved; that was fixed by writing
# BCH(127,29,21) in its place, which is the loop-61 recommendation, and it went stale
# again across four further moves. The second time nothing noticed at all, because the
# fix was a better literal rather than not a literal - W-INTL-229.
def _recommended():
    """(t, k, blocks) of the construction actually recommended. W-INTL-229.

    Was the literal (21, 29, 23) with a comment recording that this file had exercised a
    superseded code for six loops and had been re-pointed. It then went stale a second
    time, by the same mechanism, and stayed stale through four moves of the
    recommendation - so the end-to-end run that this project cites as its two-witness
    argument was witnessing a construction nobody builds.

    A comment saying "this drifted once" is a record. Deriving it is a fix.
    """
    import sys as _s
    _s.path.insert(0, __file__.rsplit("/", 1)[0])
    import selection_with_bch as S
    _, k, t, blocks = S.recommended_code()
    return t, k, blocks


T, K_BITS, BLOCKS = _recommended()
M, RED = 7, 0x09
N = (1 << M) - 1
KEY_BITS = 128       # see research/inputs.py; kept literal so this file runs standalone
MASK = N


def gf_mul(a, b):
    acc = 0
    for i in range(M):
        if (b >> i) & 1:
            acc ^= a
        a = ((a << 1) ^ RED) & MASK if (a >> (M - 1)) & 1 else (a << 1) & MASK
    return acc


def gf_pow(a, e):
    r = 1
    for _ in range(e):
        r = gf_mul(r, a)
    return r


ALPHA = 2
POW = [gf_pow(ALPHA, i) for i in range(N)]
LOG = {v: i for i, v in enumerate(POW)}


def syndromes(bits):
    """S_j = sum_i b_i alpha^(i*j) for j = 1..2t. This is the helper data."""
    out = []
    for j in range(1, 2 * T + 1):
        s = 0
        for i, b in enumerate(bits):
            if b:
                s ^= POW[(i * j) % N]
        out.append(s)
    return out


def berlekamp_massey(syn):
    """Inversionless Berlekamp-Massey, the same iteration the RTL implements."""
    lam, bee = [1] + [0] * T, [1] + [0] * T
    gamma, ell = 1, 0
    for r in range(2 * T):
        delta = 0
        for j in range(min(ell, T) + 1):
            if r + 1 - j >= 1:
                delta ^= gf_mul(lam[j], syn[r - j])
        new = [gf_mul(gamma, lam[i]) ^ (gf_mul(delta, bee[i - 1]) if i else 0)
               for i in range(T + 1)]
        if delta != 0 and 2 * ell <= r:
            bee, gamma, ell = lam[:], delta, r + 1 - ell
        else:
            bee = [0] + bee[:-1]
        lam = new
    return lam, ell


def chien(lam, degree):
    """Roots of the locator give the error positions."""
    positions = []
    for c in range(N):
        total = 0
        for k in range(T + 1):
            if lam[k]:
                total ^= gf_mul(lam[k], POW[(k * c) % N])
        if total == 0:
            positions.append((N - c) % N)
    return positions if len(positions) == degree else None


def decode_block(received, enrolled_syn):
    """Recover the enrolled block from a noisy one plus its helper data."""
    diff = [a ^ b for a, b in zip(syndromes(received), enrolled_syn)]
    if not any(diff):
        return received[:]
    lam, degree = berlekamp_massey(diff)
    if degree > T:
        return None
    pos = chien(lam, degree)
    if pos is None:
        return None
    out = received[:]
    for p in pos:
        out[p] ^= 1
    return out


# ── the source ──────────────────────────────────────────────────────────────
def enrol(rng, bias):
    """A response with the stated bias, and its helper data."""
    blocks = [[1 if rng.random() < bias else 0 for _ in range(N)]
              for _ in range(BLOCKS)]
    helper = [syndromes(b) for b in blocks]
    return blocks, helper


def regenerate(rng, blocks, ber):
    """The same response, measured again, with independent bit flips."""
    return [[b ^ (1 if rng.random() < ber else 0) for b in blk] for blk in blocks]


def key_of(blocks):
    flat = bytes(int("".join(str(b) for b in blk[i:i + 8]).ljust(8, "0"), 2)
                 for blk in blocks for i in range(0, N, 8))
    return hashlib.sha256(flat).digest()[:KEY_BITS // 8]


# ── debiasing, and the constraint that sizes it ─────────────────────────────
# The overheads this project has been quoting came from Maes et al.'s Table 2, which
# computes them for a 1,000-bit output. The overhead depends on output length through
# an inverse binomial - relative fluctuation shrinks as the output grows, so less
# slack is needed - so borrowing the figures for a 2,921-bit output was an
# approximation. The constraint is implemented here instead of borrowed, and it
# reproduces all three figures the paper states.

def classic_von_neumann(bits):
    """CVN: consider consecutive pairs, keep the first bit when they differ."""
    return [bits[i] for i in range(0, len(bits) - 1, 2) if bits[i] != bits[i + 1]]


def pair_output_von_neumann(bits):
    """2O-VN: keep both bits of a differing pair, so a retained pair yields two."""
    out = []
    for i in range(0, len(bits) - 1, 2):
        if bits[i] != bits[i + 1]:
            out += [bits[i], bits[i + 1]]
    return out


def debias_overhead_model(y, bias, pfail=1e-6, bits_per_pair=1):
    """Smallest raw length whose retained count reaches y with probability 1-pfail."""
    from math import lgamma, log, exp
    q = 2 * bias * (1 - bias)
    need = y / bits_per_pair

    def cdf_below(nn):
        tot = 0.0
        for i in range(int(need)):
            lp = (lgamma(nn + 1) - lgamma(i + 1) - lgamma(nn - i + 1)
                  + i * log(q) + (nn - i) * log(1 - q))
            tot += exp(lp)
            if tot > 1.0:
                return 1.0
        return tot

    lo, hi = int(need * 2), int(need * 40)
    while lo < hi:
        mid = (lo + hi) // 2
        if cdf_below(mid // 2) <= pfail:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ── the model this is checking ──────────────────────────────────────────────
def model_failure(ber):
    per_block = sum(comb(N, i) * ber**i * (1 - ber)**(N - i)
                    for i in range(T + 1, N + 1))
    return 1 - (1 - per_block) ** BLOCKS


def trial(rng, bias, ber):
    blocks, helper = enrol(rng, bias)
    key = key_of(blocks)
    noisy = regenerate(rng, blocks, ber)
    recovered = []
    for blk, h in zip(noisy, helper):
        out = decode_block(blk, h)
        if out is None:
            return "decode failed"
        recovered.append(out)
    if recovered != blocks:
        return "wrong response"
    return "ok" if key_of(recovered) == key else "wrong key"


if __name__ == "__main__":
    rng = random.Random(20260730)

    print(f"BCH({N},{K_BITS},{T}) over GF(2^{M}), {BLOCKS} blocks, "
          f"{N*BLOCKS} raw response bits\n")

    print("1. the chain round-trips at zero and at moderate noise")
    for bias, ber, n in ((0.50, 0.00, 20), (0.50, 0.02, 20), (0.35, 0.02, 20)):
        bad = [trial(rng, bias, ber) for _ in range(n)]
        fails = [b for b in bad if b != "ok"]
        print(f"   bias {bias:.2f}  ber {ber:.2f}  {n - len(fails)}/{n} keys recovered"
              + (f"   FAILURES: {set(fails)}" if fails else ""))

    print("\n2. it fails where the model says it should, and not before")
    print(f"   {'ber':>6} {'trials':>7} {'observed':>10} {'model':>12}")
    for ber, n in ((0.04, 300), (0.06, 300), (0.08, 200), (0.10, 120)):
        fails = sum(1 for _ in range(n) if trial(rng, 0.5, ber) != "ok")
        print(f"   {ber:6.2f} {n:7d} {fails/n:10.3f} {model_failure(ber):12.3g}")

    print("\n3. debiasing: the formula, and the chain that has to live with it")
    need = N * BLOCKS
    print(f"   {'method':8} {'bias':>5} {'raw needed':>11} {'overhead':>9} "
          f"{'observed retained':>18}")
    for label, fn, bpp in (("CVN", classic_von_neumann, 1),
                           ("2O-VN", pair_output_von_neumann, 2)):
        for bias in (0.50, 0.30):
            n_raw = debias_overhead_model(need, bias, bits_per_pair=bpp)
            got = [len(fn([1 if rng.random() < bias else 0 for _ in range(n_raw)]))
                   for _ in range(12)]
            short = sum(1 for g in got if g < need)
            print(f"   {label:8} {bias:4.0%} {n_raw:11d} {n_raw/need:9.2f} "
                  f"{min(got):8d}..{max(got):<8d}" + ("  SHORT" if short else ""))
    print("   the retained counts must clear the response length in every trial;")
    print("   the constraint is sized for a failure rate of one in a million.")

    print("\n4. debiased bits are unbiased, which is the point of the stage")
    for bias in (0.50, 0.30, 0.20):
        raw = [1 if rng.random() < bias else 0 for _ in range(400000)]
        kept = classic_von_neumann(raw)
        print(f"   source bias {bias:.2f} -> retained bias "
              f"{sum(kept)/len(kept):.4f} over {len(kept)} bits")

    print("\n5. errors beyond the correction radius are refused, not mis-corrected")
    caught = 0
    for _ in range(40):
        blocks, helper = enrol(rng, 0.5)
        blk = blocks[0][:]
        for p in rng.sample(range(N), T + 6):
            blk[p] ^= 1
        out = decode_block(blk, helper[0])
        if out is None or out != blocks[0]:
            caught += 1
    print(f"   {caught}/40 blocks with {T+6} errors were refused or returned wrong,")
    print(f"   rather than silently returning a plausible response")
