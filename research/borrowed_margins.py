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
in W-INTL-85. Two inputs moving together were named as the limitation of the one-at-a-time
pass and are now swept jointly at the bottom of this file - and doing so found that the
one-at-a-time pass had been wrong about its own tightest row.

The density floor was computed as KEY_BITS / k, the raw density needed to carry the key.
That is the floor on the density *after* selection. The declared figure is the density
*before* it, and selection amplifies bias: keeping the 54.35 percent most stable positions
moves 0.9414 to 0.9113. Comparing a before-selection number against an after-selection
floor overstated the margin as 1.26x. With the selection term the floor was 0.8303 and the
margin 1.13x - still the tightest row, by more than it looked. W-INTL-228 then applied the
project's own headroom rule to it, and the fourth block that buys takes the margin to 1.35.

The joint sweep also shows why the flip-rate row is not the 1.41x it reports: that row
holds the selection fraction at its nominal value, and the fraction is free to move. Let it
move and the construction absorbs a fifteen percent flip rate. It pays for that in density,
because deeper selection costs entropy - one knob, two constraints. The two tightest
borrowed numbers are coupled, which is exactly what a one-at-a-time sweep cannot see.
"""

import sys
from math import lgamma, log, sqrt
from functools import lru_cache

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import aging_margin as AM
import inputs as I
import reliable_bit_selection as R
import selection_entropy as SE

CELLS = 35_905          # the recommendation, from check_figures_reproduce
def _k_total():
    """Bits of k the recommendation carries. Asked for, not written down.

    Was 57 * 3, then a derivation with k=57 written into it, which is the same defect one
    level in: the block count was computed and the code it multiplied was not. Both come
    from selection_with_bch.recommended_code() now - W-INTL-229.
    """
    import selection_with_bch as S
    _, k, _, blocks = S.recommended_code()
    return k * blocks


K_TOTAL = _k_total()


def utilisation_floor():
    """Below this, the recommendation no longer fits the sixteen tiles."""
    return CELLS / (I.TILE_LIMIT * I.TILE_AREA)


def density_floor():
    """Below this declared min-entropy density, the key does not survive the construction.

    KEY_BITS / K_TOTAL is the floor on the density that reaches the extractor, which is the
    density after selection, not the declared one. Selection amplifies bias, so the two are
    not the same number and comparing across them flatters the margin. Invert the selection
    term to get the floor on what inputs.py actually declares.
    """
    keep = 1.0 - I.SELECTION_LOSS
    lo, hi = 0.5, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        after = SE.density_for_bias(SE.selected_bias(SE.mean_for_density(mid), 1 - keep)[0])
        if I.KEY_BITS / after <= K_TOTAL:
            hi = mid
        else:
            lo = mid
    return hi


def inverter_area_ceiling():
    """Above this area per inverter, the oscillator bank stops fitting."""
    others = CELLS - 38 * I.OSCILLATOR_AREA
    room = I.TILE_LIMIT * I.TILE_AREA * I.UTILISATION - others
    return room / (38 * I.INVERTERS_PER_OSCILLATOR * I.AGING_RESISTANT_FACTOR)


def aged_flip_ceiling():
    """Above this ten-year flip rate, the construction misses its word failure target."""
    keep = 1.0 - I.SELECTION_LOSS
    tol = AM.tolerated_ber()
    base = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    lo, hi = 0.0, 0.99
    for _ in range(20):   # 1e-6 on a range under 1; the figures are read to four decimals
        mid = (lo + hi) / 2
        if R.aged_selected_ber(base, R.sigma_for_raw_ber(max(mid, 1e-6)),
                               keep, I.ENROLMENT_READS, steps=600) <= tol:
            lo = mid
        else:
            hi = mid
    return lo


def raw_noise_ceiling():
    """Above this fresh-device error rate, the construction misses its target."""
    keep = 1.0 - I.SELECTION_LOSS
    tol = AM.tolerated_ber()
    aged = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    lo, hi = 0.0, 0.49
    for _ in range(20):   # 1e-6 on a range under 1; the figures are read to four decimals
        mid = (lo + hi) / 2
        if R.aged_selected_ber(R.sigma_for_raw_ber(max(mid, 1e-6)), aged,
                               keep, I.ENROLMENT_READS, steps=600) <= tol:
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


KEEPS = tuple(k / 100 for k in range(95, 9, -5))


@lru_cache(maxsize=None)
def _keeps_meeting_error(flip):
    """Which selection fractions meet the word-failure target at this flip rate.

    Cached, and separated from the density test on purpose. The error side depends on the
    flip rate alone and the leakage side on the density alone; computing them together
    recomputed the expensive half once per density. That took check_figures_reproduce from
    33 to 59 seconds, and check_input_coverage runs it once per declared input in both
    directions - sixty times - so a half-minute here is half an hour there. W-INTL-227.
    """
    base = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    drift = R.sigma_for_raw_ber(max(flip, 1e-6))
    tol = AM.tolerated_ber()
    return frozenset(
        keep for keep in KEEPS
        if R.aged_selected_ber(base, drift, keep, I.ENROLMENT_READS, steps=600) <= tol)


def largest_retained(density, flip):
    """The largest fraction of positions that can be kept and still meet both, or None.

    Both borrowed figures act through the same knob. A worse flip rate is answered by
    selecting harder; selecting harder amplifies bias and costs density. Asking each
    separately asks whether one constraint can be met while the other is held at nominal,
    which is not the question the design faces.

    Named for what it returns, after the table it feeds was labelled "deepest selection
    fraction" for a loop. The error constraint is met by keeping FEWER positions and the
    leakage constraint by keeping MORE, so the answer is the largest retained fraction the
    error target still allows - the shallowest adequate selection, not the deepest one.
    The set of fractions meeting the error target is downward closed, so if that largest
    one fails on leakage every smaller one fails worse and there is nothing below it to
    find. Two constraints pulling opposite ways is the whole content of W-INTL-225, and
    the table naming it backwards undercut the point it exists to make.
    """
    ok = _keeps_meeting_error(flip)
    for keep in KEEPS:
        if keep not in ok:
            continue
        after = SE.density_for_bias(SE.selected_bias(SE.mean_for_density(density),
                                                     1 - keep)[0])
        if I.KEY_BITS / after <= K_TOTAL:
            return keep
    return None


# Bracketing the declared density and its floor. The grid was 0.80-0.9414 until
# W-INTL-231 corrected the declared figure from a Shannon entropy to a min-entropy,
# after which not one of its rows contained the operating point - a sweep whose grid
# misses the design tells you about a design you do not have.
JOINT_DENSITY = (0.7162, 0.70, 0.65, 0.60, 0.5506, 0.52)
JOINT_FLIP = (0.0773, 0.09, 0.11, 0.13, 0.15)


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
    print("\nOne input moves per row and the rest are held, including the selection")
    print("fraction. The two tightest are swept together below.\n")

    print("The two tightest, moved together. Cell = largest retained fraction meeting")
    print("both constraints; --- = no fraction does.\n")
    print(f"{'density':>9} " + "".join(f"{f:>8.0%}" for f in JOINT_FLIP))
    for density in JOINT_DENSITY:
        cells = []
        for flip in JOINT_FLIP:
            keep = largest_retained(density, flip)
            cells.append(f"{keep:8.0%}" if keep else "     ---")
        print(f"{density:9.4f} " + "".join(cells))
    print("\nThe flip rate is not the 1.41x its own row reports: that row holds the")
    print("selection fraction, and a fifteen percent flip rate is absorbed if the fraction")
    print("is allowed to move. It is paid for in density, which is why the rows below")
    print("0.85 fail at every flip rate including the nominal one. One knob, two")
    print("constraints, and the one-at-a-time sweep can see neither of them moving.")
