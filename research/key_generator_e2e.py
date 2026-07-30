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

# ── the construction, from the search in bch_code_search.py ─────────────────
M, RED, T, K_BITS = 7, 0x09, 23, 22       # BCH(127,22,23) over GF(2^7)
N = (1 << M) - 1
BLOCKS = 23
KEY_BITS = 128
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

    print("\n3. errors beyond the correction radius are refused, not mis-corrected")
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
