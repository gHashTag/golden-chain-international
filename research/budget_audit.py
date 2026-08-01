#!/usr/bin/env python3
"""Every mechanism that perturbs a response bit, marked present, bounded or absent.

W-INTL-236. W-INTL-235 found an absent term by asking what one input was a figure *of*.
That was luck in the sense that it came from auditing an input; a term nobody declared has
no input to audit, so the only way to find the next one is to enumerate mechanisms rather
than declarations. This file is that enumeration, and it exists because the previous
finding said an absent term has no name to check.

  mechanism                    status     figure                    where
  read noise                   present    6% fresh-device           RAW_NOISE_BER
  aging, ten years             present    7.73% aging-resistant     AGED_FLIP_RESISTANT
  temperature                  present    2.63% typical, 11% worst  TEMPERATURE_FLIP_*
  correlation between drifts   assumed    independence              priced below
  supply voltage               ABSENT     no usable figure found    nothing
  electromagnetic interference ABSENT     not looked for            nothing

Two of the six are worth more than a line.

Correlation
-----------
W-INTL-235 added the temperature drift to the aging drift in quadrature, which assumes the
two are independent per position. They are plausibly not: NBTI degradation is
temperature-accelerated, and the per-position sign of each drift is set by mismatch in the
same devices. Independence is therefore the optimistic end and correlation is the
pessimistic one, and the honest thing is to price the range rather than argue for a point.

Supply voltage
--------------
The searched literature gives designs *stated* to be stable across plus or minus ten
percent of supply, and one summary reporting "reliability degradation around ten percent"
under voltage variation, which is not a figure this work can use: it does not say ten
percent of what, over what excursion, on which circuit. So this stays ABSENT rather than
being given a number that would look like one. Naming it absent is the whole of what this
file can honestly do about it.

Usage: budget_audit.py    prints the enumeration and the correlation sweep
"""

import sys
from math import sqrt

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import aging_margin as AM
import inputs as I
import reliable_bit_selection as R
import selection_with_bch as S

# The declared fraction is imported, not written as 0.5435. inputs.py warns about this
# case in as many words - "rounding the fraction to four places turned 701 raw positions
# into 702" - and the first version of this file did it anyway and reported 1,403 raw
# positions where the recommendation has 1,402. Four decimal places, one position, and the
# defect the warning describes reproduced in the file auditing the budget for defects.
FRACTIONS = (1.0 - I.SELECTION_LOSS, 0.40, 0.326, 0.20, 0.10)
CORRELATIONS = (0.0, 0.5, 1.0)

MECHANISMS = (
    ("read noise", "present", "6% fresh-device", "RAW_NOISE_BER"),
    ("aging, ten years", "present", "7.73% aging-resistant", "AGED_FLIP_RESISTANT"),
    ("temperature", "present", "2.63% typical, 11% worst", "TEMPERATURE_FLIP_*"),
    ("correlation between drifts", "assumed", "independence", "priced below"),
    ("supply voltage", "ABSENT", "no usable figure found", "nothing"),
    ("electromagnetic interference", "ABSENT", "not looked for", "nothing"),
)


def combined_drift(temperature_flip, correlation):
    """Aging and temperature as two drifts with the given correlation coefficient."""
    age = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    temp = R.sigma_for_raw_ber(max(temperature_flip, 1e-6))
    return sqrt(age * age + temp * temp + 2 * correlation * age * temp)


def best_over_fractions(temperature_flip, correlation):
    """Cheapest admissible construction, letting the selection fraction move.

    Holding the fraction is what W-INTL-225 identified about the one-at-a-time sweep, and
    W-INTL-235 priced the worst case with it held anyway - at 2.12 of a tile. Allowing the
    knob that answers a worse error rate to move puts the same case at 0.25.
    """
    drift = combined_drift(temperature_flip, correlation)
    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    best = None
    for keep in FRACTIONS:
        eff = R.aged_selected_ber(noise, drift, keep, I.ENROLMENT_READS)
        if eff > AM.tolerated_ber():
            continue
        found = S.best_at(keep, eff, S.need_k_at(keep))
        if found is None:
            continue
        _, n, k, t, blocks, _, raw = found
        osc = max(S.floor_ent(I.KEY_BITS), S._r(raw))
        tiles = I.tiles(I.decoder_area(7, t) + I.SLLC_AREA[t] + osc * I.OSCILLATOR_AREA
                        + I.COUNTERMEASURE_AREA["spongent_permutation"])
        if best is None or tiles < best[0]:
            best = (tiles, keep, n, k, t, blocks, raw, osc)
    return best


if __name__ == "__main__":
    print("Every mechanism that perturbs a response bit.\n")
    print(f"{'mechanism':30} {'status':9} {'figure':26} {'declared as'}")
    for name, status, figure, where in MECHANISMS:
        print(f"{name:30} {status:9} {figure:26} {where}")

    print("\nThe two drifts, swept over how correlated they are, with the selection")
    print("fraction free. Independence is the optimistic end.\n")
    print(f"{'temperature':>12} {'rho':>5} {'drift':>8} {'keep':>7} "
          f"{'construction':>20} {'tiles':>7}")
    baseline = best_over_fractions(0.0, 0.0)
    for flip in (I.TEMPERATURE_FLIP_TYPICAL, 0.05, I.TEMPERATURE_FLIP_WORST):
        for rho in CORRELATIONS:
            found = best_over_fractions(flip, rho)
            if found is None:
                print(f"{flip:>12.2%} {rho:>5.1f} {combined_drift(flip, rho):>8.4f} "
                      f"{'-':>7} {'nothing fits':>20}")
                continue
            tiles, keep, n, k, t, blocks, raw, osc = found
            print(f"{flip:>12.2%} {rho:>5.1f} {combined_drift(flip, rho):>8.4f} "
                  f"{keep:>7.1%} {f'BCH({n},{k},{t}) x {blocks}':>20} {tiles:>7.2f}")

    worst = best_over_fractions(I.TEMPERATURE_FLIP_WORST, 1.0)
    print(f"\nthe worst corner costs {worst[0] - baseline[0]:.2f} of a tile - "
          f"{baseline[0]:.2f} to {worst[0]:.2f} -")
    print(f"at {worst[1]:.0%} of positions retained rather than {1 - I.SELECTION_LOSS:.0%},")
    print("and it is answered by selecting harder rather than by weakening the code.")
    print("W-INTL-235 priced this corner at 2.12 by holding the fraction, which is the")
    print("thing W-INTL-225 exists to have noticed. The correction runs the other way from")
    print("most here: the design is in better shape than the previous loop reported.")
    print("\nWhat it costs instead is oscillators - the deeper fraction needs")
    print(f"{worst[6]} raw positions and {worst[7]} of them, against "
          f"{baseline[6]} and {baseline[7]}.")
