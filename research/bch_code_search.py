#!/usr/bin/env python3
"""Search the admissible BCH parameter space instead of adopting a paper's choice.

The construction in use came from Gao et al., who selected it for their constraints:
an SRAM PUF with near-full entropy density and a bit error rate around ten percent.
This project's constraints are different - ring oscillators, measured entropy density
0.9414, error rate unknown - and adopting a parameter choice along with a method
carries the source's operating point silently.

Code parameters are computed rather than looked up. The generator polynomial of a
narrow-sense binary BCH code is the lcm of the minimal polynomials of alpha^1 through
alpha^2t, and the degree of the minimal polynomial of alpha^i is the size of its
cyclotomic coset. So the parity count is the size of a union of cosets, which is
arithmetic. The calibration block below checks the result against every BCH code named
in the sources this project has read, and refuses to search if any disagrees.
"""

from math import comb, ceil

RHO = 241.0 / 256          # measured min-entropy per response bit
KEY_BITS = 128
TARGET_FAILURE = 1e-6


def bch_parameters(m):
    """[(t, k)] for narrow-sense binary BCH of length n = 2^m - 1, strongest per rate."""
    n = (1 << m) - 1
    coset = {}
    for i in range(1, n):
        if i in coset:
            continue
        c, x = set(), i
        while x not in c:
            c.add(x)
            x = (2 * x) % n
        for e in c:
            coset[e] = frozenset(c)
    seen, best = set(), {}
    for d in range(1, n):
        if d in coset:
            seen |= coset[d]
        if d % 2 == 0:
            t, k = d // 2, n - len(seen)
            if k > 0 and (k not in best or t > best[k]):
                best[k] = t
    return sorted((t, k) for k, t in best.items())


def calibrate():
    """Every BCH code named in the sources read for this project."""
    known = [(7, 27, 15, "Gao et al., arXiv:1902.03031"),
             (6, 11, 16, "Gao et al., arXiv:1902.03031"),
             (8, 18, 131, "this project's original assumption"),
             (8, 11, 171, "Bosch et al., CHES 2008, Table 2")]
    ok = True
    for m, t, k, who in known:
        got = dict(bch_parameters(m)).get(t)
        if got != k:
            print(f"  CALIBRATION FAIL: BCH({(1<<m)-1},?,t={t}) computed k={got}, "
                  f"source says {k} [{who}]")
            ok = False
        else:
            print(f"  ok  BCH({(1<<m)-1},{k},t={t})  [{who}]")
    return ok


def tail(n, kmin, p):
    if p <= 0:
        return 0.0
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(kmin, n + 1))


def max_ber(n, t, blocks):
    lo, hi = 0.0, 0.5
    for _ in range(50):
        mid = (lo + hi) / 2
        if 1 - (1 - tail(n, t + 1, mid))**blocks <= TARGET_FAILURE:
            lo = mid
        else:
            hi = mid
    return lo


def search(raw_budget, min_ber):
    """Admissible codes, ordered by margin on the entropy density.

    The entropy margin is the metric to order by because a shortfall there yields no
    key at all, while a shortfall in error tolerance only calls for a stronger code.
    """
    out = []
    for m in (6, 7, 8, 9):
        n = (1 << m) - 1
        for t, k in bch_parameters(m):
            per_block = k - n * (1 - RHO)
            if per_block <= 0:
                continue                       # leaks more than it carries
            blocks = raw_budget // n           # spend the budget on margin
            if blocks * per_block < KEY_BITS:
                continue
            rho_min = 1 - (k - KEY_BITS / blocks) / n
            if rho_min >= RHO:
                continue
            ber = max_ber(n, t, blocks)
            if ber < min_ber:
                continue
            out.append({"n": n, "k": k, "t": t, "blocks": blocks, "raw": n * blocks,
                        "rho_min": rho_min, "margin": RHO - rho_min, "max_ber": ber})
    return sorted(out, key=lambda r: -r["margin"])


# Decoder areas, measured against the SkyWater library and verified end to end first.
MEASURED_AREA = {(7, 23): 86_896, (7, 27): 102_267, (8, 18): 90_254,
                 (8, 42): 206_630, (9, 54): 304_465}
TILE = 18_032
OSC_AREA = 7 * (6_730 / 1_792)
ENTROPY_FLOOR_OSC = 272


if __name__ == "__main__":
    print("Calibration of the computed parameter table:")
    if not calibrate():
        raise SystemExit("parameter table disagrees with the sources; stopping")

    for budget in (3000,):
        print(f"\nAdmissible codes within {budget} raw response bits, "
              f"tolerating at least 5 percent bit error rate:\n")
        print(f"  {'code':>16} {'t':>3} {'blocks':>7} {'raw':>5} {'rho_min':>8} "
              f"{'margin':>7} {'max BER':>8} {'total tiles':>12}")
        print("  " + "-" * 74)
        for r in search(budget, 0.05):
            area = MEASURED_AREA.get((r["n"].bit_length(), r["t"]))
            tiles = (f"{(area + ENTROPY_FLOOR_OSC*OSC_AREA)/TILE:.2f}"
                     if area else "not measured")
            print(f"  BCH({r['n']},{r['k']}) {r['t']:5d} {r['blocks']:7d} {r['raw']:5d} "
                  f"{r['rho_min']:8.4f} {r['margin']:7.4f} {r['max_ber']*100:7.2f}% "
                  f"{tiles:>12}")
        print("\n  Tiles include the decoder and a 272-oscillator bank, the floor set by")
        print("  128 bits of min-entropy at the measured 0.471 bits per oscillator.")
