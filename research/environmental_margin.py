#!/usr/bin/env python3
"""The error budget has a noise term and an aging term and no environmental term at all.

W-INTL-235, from putting `RAW_NOISE_BER` through the question that found W-INTL-231, 232
and 233. That input is declared "measured here, in the sense that 0.06 is the fresh-device
figure this project has used throughout" - which is not a measurement, and says so. Asking
what it is a figure *of* turns up the larger problem: it is a figure at one temperature,
and nothing else in this work carries another.

`research/constraint_register.md` lists five constraints. None is environmental variation.
The only mention anywhere is inside the aging row - "the literature reports ring-oscillator
PUFs as resilient to temperature but *less* resilient to aging" - and that sentence is
carrying a whole missing constraint.

It is also weaker than it sounds. Ring oscillator PUFs are relatively robust to temperature
because both oscillators of a pair shift together, but pairs whose frequencies are close
reverse - and reliable-bit selection is the thing that is supposed to have discarded those,
so what survives selection is exactly the residual nobody has budgeted.

What the literature gives, and what it does not
-----------------------------------------------
A configurable RO-PUF measured from 25 to 70 degrees reports intra-chip variation averaging
2.63 percent, with a maximum of 11 percent and a minimum of zero. Three conditions differ
from this design and are stated rather than absorbed: it is a *configurable* RO-PUF, which
is a different circuit; the span is 45 degrees where an industrial part sees 125; and the
maximum is over the chips measured, not a bound.

The average and the maximum are not interchangeable here, and that is the point of this
file. A word-failure target of one in a million is a claim about every part, so the figure
that has to fit is the worst chip's, not the average chip's. Budgeting a per-part guarantee
against a population mean is the same category error as sizing a fuzzy extractor against a
Shannon entropy: an average where a worst case is required.

How it enters the model
-----------------------
As a second drift, not as noise. A temperature offset shifts the difference and holds while
the temperature holds; it is not resampled per read, and it is not present at enrolment,
which enrols at one temperature. That is the same shape as aging, so `aged_selected_ber`
takes it unchanged and the two drifts add in quadrature.

Usage: environmental_margin.py    prints the budget and what each term costs
"""

import sys
from math import sqrt

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import aging_margin as AM
import inputs as I
import reliable_bit_selection as R
import selection_with_bch as S

# The two declared figures with three fillers between them, so the table shows where
# the recommendation stops carrying the term rather than only its endpoints.
PROBES = (0.0, I.TEMPERATURE_FLIP_TYPICAL, 0.05, 0.08, I.TEMPERATURE_FLIP_WORST)


def selected_ber_at(temperature_flip):
    """Selected error rate with aging and this temperature term, both as drifts."""
    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    drift = sqrt(R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT) ** 2
                 + R.sigma_for_raw_ber(max(temperature_flip, 1e-6)) ** 2)
    return R.aged_selected_ber(noise, drift, 1.0 - I.SELECTION_LOSS, I.ENROLMENT_READS)


def construction_at(temperature_flip):
    """(tiles, n, k, t, blocks, oscillators) the budget needs at this temperature term."""
    keep = 1.0 - I.SELECTION_LOSS
    best = S.best_at(keep, selected_ber_at(temperature_flip), S.need_k_at(keep))
    if best is None:
        return None
    _, n, k, t, blocks, _, raw = best
    osc = max(S.floor_ent(I.KEY_BITS), S._r(raw))
    tiles = I.tiles(I.decoder_area(7, t) + I.SLLC_AREA[t] + osc * I.OSCILLATOR_AREA
                    + I.COUNTERMEASURE_AREA["spongent_permutation"])
    return tiles, n, k, t, blocks, osc


def absorbed_without_change():
    """Largest temperature term the recommendation carries at no cost."""
    at_zero = construction_at(0.0)
    lo, hi = 0.0, 0.5
    for _ in range(30):
        mid = (lo + hi) / 2
        here = construction_at(mid)
        if here is not None and here[:6] == at_zero[:6]:
            lo = mid
        else:
            hi = mid
    return lo


if __name__ == "__main__":
    tol = AM.tolerated_ber()
    print(f"tolerated selected error rate {tol:.5f}\n")
    print(f"{'temperature term':>17} {'selected BER':>13} {'meets 1e-6':>11} "
          f"{'construction':>18} {'osc':>4} {'tiles':>7}")
    for probe in PROBES:
        eff = selected_ber_at(probe)
        here = construction_at(probe)
        if here is None:
            print(f"{probe:>16.2%} {eff:>13.6f} {'no':>11} {'nothing fits':>18}")
            continue
        tiles, n, k, t, blocks, osc = here
        print(f"{probe:>16.2%} {eff:>13.6f} {'yes' if eff <= tol else 'no':>11} "
              f"{f'BCH({n},{k},{t}) x {blocks}':>18} {osc:>4} {tiles:>7.2f}")

    free = absorbed_without_change()
    print(f"\nthe recommendation absorbs a temperature term up to {free:.1%} without")
    print("changing - the six blocks that the density headroom rule and the min-entropy")
    print("correction bought already carry it, which is margin arriving from somewhere")
    print("other than where it was aimed for the second time.")
    print("\nIt does not carry the worst chip in the measurement cited above. Closing")
    worst = construction_at(I.TEMPERATURE_FLIP_WORST)
    zero = construction_at(0.0)
    print(f"that costs {worst[0] - zero[0]:.2f} of a tile - {zero[0]:.2f} to {worst[0]:.2f} -")
    print("and is NOT done here. One borrowed figure, from a different circuit over a")
    print("narrower span, is not enough to spend sixty percent more area on; and its")
    print("absence is not enough to spend nothing. What settles it is a temperature")
    print("sweep of the characteriser this project has already built and never run.")
