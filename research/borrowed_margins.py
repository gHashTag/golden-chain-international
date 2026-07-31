#!/usr/bin/env python3
"""How far each borrowed number can move before the recommendation stops working.

W-INTL-74 has been open since loop 74: the code was inherited from a paper along with its
operating point, and the other borrowed parameters should be checked the same way. The
code was checked, twice. The rest were not, and this is that check, done systematically
rather than one at a time when something goes wrong.

Every "measured there" input in inputs.py is somebody else's measurement, taken under
conditions that travelled with it and conditions that did not. The useful question is not
whether those conditions match - they never exactly do - but how far the number would have
to be wrong before the design failed. A borrowed figure with a factor of five in hand is
an assumption; a borrowed figure with forty percent in hand is a dependency.

Each row moves one input and holds the rest, which is the sweep that reversed a priority
in W-INTL-85. That is a limitation and it is stated: two inputs moving together are not
covered here.
"""

import sys
from math import lgamma, log, sqrt

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import aging_margin as AM
import inputs as I
import reliable_bit_selection as R
import selection_entropy as SE

CELLS = 35_905          # the recommendation, from check_figures_reproduce
K_TOTAL = 57 * 3


def utilisation_floor():
    """Below this, the recommendation no longer fits the sixteen tiles."""
    return CELLS / (I.TILE_LIMIT * I.TILE_AREA)


def density_floor():
    """Below this min-entropy density, the key does not survive the construction."""
    return I.KEY_BITS / K_TOTAL


def inverter_area_ceiling():
    """Above this area per inverter, the oscillator bank stops fitting."""
    others = CELLS - 38 * I.OSCILLATOR_AREA
    room = I.TILE_LIMIT * I.TILE_AREA * I.UTILISATION - others
    return room / (38 * I.INVERTERS_PER_OSCILLATOR * I.AGING_RESISTANT_FACTOR)


def aged_flip_ceiling():
    """Above this ten-year flip rate, the construction misses its word failure target."""
    keep = 1.0 - I.SELECTION_LOSS
    tol = AM.tolerated_ber()
    base = R.sigma_for_raw_ber(I.RAW_NOISE_BER) ** 2
    lo, hi = 0.0, 0.99
    for _ in range(40):
        mid = (lo + hi) / 2
        sig = sqrt(base + R.sigma_for_raw_ber(max(mid, 1e-6)) ** 2)
        if R.selected_ber_counts_exact(sig, keep, I.ENROLMENT_READS, steps=600) <= tol:
            lo = mid
        else:
            hi = mid
    return lo


def raw_noise_ceiling():
    """Above this fresh-device error rate, the construction misses its target."""
    keep = 1.0 - I.SELECTION_LOSS
    tol = AM.tolerated_ber()
    aged = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT) ** 2
    lo, hi = 0.0, 0.49
    for _ in range(40):
        mid = (lo + hi) / 2
        sig = sqrt(aged + R.sigma_for_raw_ber(max(mid, 1e-6)) ** 2)
        if R.selected_ber_counts_exact(sig, keep, I.ENROLMENT_READS, steps=600) <= tol:
            lo = mid
        else:
            hi = mid
    return lo


ROWS = [
    ("tile utilisation", I.UTILISATION, utilisation_floor, "below",
     "a 1x2-tile design, applied to one of 3.4 tiles"),
    ("min-entropy density", I.MIN_ENTROPY_DENSITY, density_floor, "below",
     "Spartan-3E FPGAs at room temperature, disjoint neighbour pairing"),
    ("inverter area", I.INVERTER_AREA, inverter_area_ceiling, "above",
     "a published tile's inverter count; cross-checked against the library"),
    ("ten-year flip rate", I.AGED_FLIP_RESISTANT, aged_flip_ceiling, "above",
     "HSPICE at 90 nm, 23 percent activation, a cell this design does not use"),
    ("fresh error rate", I.RAW_NOISE_BER, raw_noise_ceiling, "above",
     "this project's own working figure rather than a measurement"),
]


if __name__ == "__main__":
    print("How far each borrowed number can move before the recommendation fails.\n")
    print(f"{'input':22} {'value':>10} {'limit':>10} {'direction':>10} {'margin':>9}")
    worst = None
    for name, value, limit_fn, direction, _ in ROWS:
        limit = limit_fn()
        margin = (value / limit) if direction == "below" else (limit / value)
        print(f"{name:22} {value:10.4f} {limit:10.4f} {direction:>10} {margin:8.2f}x")
        if worst is None or margin < worst[1]:
            worst = (name, margin)
    print(f"\ntightest: {worst[0]} at {worst[1]:.2f} times")
    print("\nconditions each figure carries:")
    for name, _, _, _, cond in ROWS:
        print(f"  {name:22} {cond}")
    print("\nOne input moves per row and the rest are held. Two moving together are not")
    print("covered here, which is the limitation that reversed a priority in W-INTL-85.")
