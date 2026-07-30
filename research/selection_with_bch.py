"""Reliable-bit selection paired with BCH, which is the bound W-INTL-118 left open.

The routine measured selection against repetition only and said so: a stronger inner code
moves the selection column down and could reverse the conclusion. This pairs it with the
BCH codes whose decoders are measured here, reusing the routine's own selection model
rather than rebuilding it - the model is already validated against a 120,000-position
sample to within half a thousandth.
"""
import sys
sys.path.insert(0, 'research')
from math import comb, lgamma
import reliable_bit_selection as R
import selection_entropy as SE
import inputs as I

LN2 = 0.6931471805599453
SLLC = 4745


def bch_table(m):
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


def word_fail(n, t, blocks, p):
    per = sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(t + 1, n + 1))
    return 1 - (1 - per) ** blocks


def floor_ent(need):
    x = 2
    while lgamma(x + 1) / LN2 < need:
        x += 1
    return x


def _r(positions):
    x = 2
    while x * (x - 1) // 2 < positions:
        x += 1
    return x


RHO = I.MIN_ENTROPY_DENSITY
KEY = I.KEY_BITS
MU = SE.mean_for_density(RHO)


def need_k_at(fraction):
    """Bits of k the key needs, at the density the SELECTED positions actually have.

    RHO is measured on unselected positions. Selection keeps the ones furthest from the
    decision boundary, which are the ones most committed to a value, so the survivors
    are more biased - see research/selection_entropy.py and W-INTL-144. Using RHO here
    was an understatement that grew with the selection fraction, and it is why the
    deeper rows of this table used to look free.
    """
    rho = SE.density_for_bias(SE.selected_bias(MU, 1.0 - fraction)[0])
    return int(KEY / rho + 0.999)

for raw in (0.06, 0.10, 0.15):
    sigma = R.sigma_for_raw_ber(raw)
    print(f"\n=== raw bit error rate {raw:.0%} "
          f"(the routine's model, sigma {sigma:.4f}) ===")
    print(f"{'selected':>9} {'eff BER':>9} {'density':>8} {'k needed':>9} "
          f"{'code':>16} {'blocks':>7} {'selected bits':>14} {'raw positions':>14} "
          f"{'tiles':>7}")
    best_overall = None
    for frac in (1.00, 0.80, 0.60, 0.40, 0.326, 0.20, 0.10):
        eff = raw if frac >= 1.0 else R.selected_ber(sigma, frac)[0]
        need_k = need_k_at(frac)
        rho_sel = KEY / need_k
        row_best = None
        for m in (7, 8):
            n = (1 << m) - 1
            for t, k in bch_table(m):
                area = I.decoder_area(m, t)
                if area is None:
                    continue
                blocks = -(-need_k // k)
                if word_fail(n, t, blocks, eff) > 1e-6:
                    continue
                sel_bits = n * blocks
                raw_pos = int(sel_bits / frac + 0.999)
                osc = max(floor_ent(KEY), _r(raw_pos))
                tiles = I.tiles(area + SLLC + osc * I.OSCILLATOR_AREA)
                if row_best is None or tiles < row_best[0]:
                    row_best = (tiles, n, k, t, blocks, sel_bits, raw_pos)
        if row_best is None:
            print(f"{frac:9.1%} {eff:9.4f} {rho_sel:8.4f} {need_k:9d} {'none fits':>16}")
            continue
        tiles, n, k, t, blocks, sel_bits, raw_pos = row_best
        print(f"{frac:9.1%} {eff:9.4f} {rho_sel:8.4f} {need_k:9d} "
              f"{f'BCH({n},{k},{t})':>16} {blocks:7d} "
              f"{sel_bits:14d} {raw_pos:14d} {tiles:7.2f}")
        if best_overall is None or tiles < best_overall[0]:
            best_overall = (tiles, frac, n, k, t, raw_pos)
    if best_overall:
        tiles, frac, n, k, t, raw_pos = best_overall
        print(f"  best: BCH({n},{k},{t}) selecting {frac:.1%}, "
              f"{raw_pos} raw positions, {tiles:.2f} tiles")


