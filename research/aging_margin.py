#!/usr/bin/env python3
"""Aging, which the constraint register has listed as unchecked since it was written.

Every error-rate figure in this work is a fresh-device figure. The register says so and
names the gap. This turns the gap into a number.

The source is read rather than summarised. Rahman, Forte, Fahrny and Tehranipoor,
"ARO-PUF: An Aging-Resistant Ring Oscillator PUF Design", DATE 2014:

    "After 10 years, the average error in response of the ARO-PUF is 7.73%, whereas it
    is 32.41% in the conventional RO-PUF."

and on the mechanism:

    "The frequency degradation in 10 years is about 1.8%"

Those two figures together are the whole point. The *common* drift is 1.8 percent and it
does not flip anything, because a response bit is a comparison between two oscillators
and a drift they share cancels. What flips bits is the *differential* part - the two
oscillators of a pair age at different rates because they carry different duty cycles -
and after ten years that differential exceeds the manufacturing difference for a third
of the pairs.

Conditions, which travel with the figure: HSPICE Monte Carlo, 100 chip instances, 90 nm,
64 conventional ring oscillators, three-sigma process variation. Simulation, not silicon,
and not this process. 130 nm is the less aggressive node, so 32.41 percent is expected to
be pessimistic here - but that is an argument, and the figure used below is the measured
one rather than the argued one.

What this computes: aging as an additional differential term in this project's own source
model, calibrated so that the unselected flip rate reproduces the published figure, and
then the flip rate of the positions the design actually keeps. Reliable-bit selection was
adopted for noise. Whether it also buys anything against aging is not something the
literature figure answers, because that figure is for an unselected population.
"""

import sys
from math import sqrt

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I
import reliable_bit_selection as R

# measured there: DATE 2014, conditions above. Response-bit flip rate at ten years for a
# conventional ring-oscillator PUF, and for the aging-resistant variant the same paper
# proposes.
AGED_FLIP_CONVENTIONAL = 0.3241
AGED_FLIP_RESISTANT = 0.0773
COMMON_DRIFT = 0.018

# The condition that matters most and is easiest to miss. Their Table I sweeps
# "activation time" - the fraction of wall-clock time the oscillators are running - and
# the ten-year figures above are taken at 23 percent. The paper says so itself: "the
# activation time of a PUF in security applications should be much less than 23% used
# earlier. Lower activation time further reduces the error rate".
#
# This identity root runs once at power-up for a few thousand cycles. Its activation time
# is orders below one percent. Their Table I gives the aging-resistant variant across
# activation times - 7.81, 7.03, 7.01 percent at 23, 10, 5 and 1 percent activation - and
# does not give the conventional oscillator's figure at low activation. So the number
# this design would actually see is not in the source.
PUBLISHED_ACTIVATION = 0.23

RAW_NOISE_BER = 0.06          # the fresh-device figure this project has been using
KEEP = 1 - I.SELECTION_LOSS   # the design keeps eighty percent


def combined_sigma(*sigmas):
    """Independent Gaussian perturbations of the difference add in quadrature."""
    return sqrt(sum(s * s for s in sigmas))


def effective(sigma, keep):
    return R.selected_ber(sigma, keep)[0] if keep < 1.0 else R.raw_ber(sigma)


if __name__ == "__main__":
    sigma_noise = R.sigma_for_raw_ber(RAW_NOISE_BER)
    sigma_age = R.sigma_for_raw_ber(AGED_FLIP_CONVENTIONAL)
    sigma_age_r = R.sigma_for_raw_ber(AGED_FLIP_RESISTANT)

    print("1. the model is calibrated to the published figure, not to a guess")
    print(f"   read noise      sigma {sigma_noise:.4f} reproduces {RAW_NOISE_BER:.1%} "
          f"fresh-device error")
    print(f"   aging, plain RO sigma {sigma_age:.4f} reproduces "
          f"{AGED_FLIP_CONVENTIONAL:.2%} at ten years")
    print(f"   aging, ARO      sigma {sigma_age_r:.4f} reproduces "
          f"{AGED_FLIP_RESISTANT:.2%} at ten years")
    print(f"   the common {COMMON_DRIFT:.1%} frequency drift is not modelled because a "
          f"drift both")
    print(f"   oscillators of a pair share cancels in the comparison that makes the bit")

    print("\n2. what the design sees, fresh and at ten years")
    print(f"   {'oscillator':>16} {'age':>8} {'selection':>10} {'effective BER':>14} "
          f"{'code tolerates':>15} {'verdict':>9}")
    TOLERATED = 0.0442     # BCH(127,57,11) in three blocks, one in a million word failure
    for label, s_age in (("conventional", sigma_age), ("aging-resistant", sigma_age_r)):
        for when, sig in (("fresh", combined_sigma(sigma_noise)),
                          ("10 years", combined_sigma(sigma_noise, s_age))):
            for keep in (1.0, KEEP):
                eff = effective(sig, keep)
                ok = "fits" if eff <= TOLERATED else "FAILS"
                print(f"   {label:>16} {when:>8} {keep:10.0%} {eff:14.4f} "
                      f"{TOLERATED:15.4f} {ok:>9}")

    print("\n3. how much aging the design can absorb")
    lo, hi = 0.0, 0.99
    for _ in range(200):
        mid = (lo + hi) / 2
        s = combined_sigma(sigma_noise, R.sigma_for_raw_ber(max(mid, 1e-6)))
        if effective(s, KEEP) <= TOLERATED:
            lo = mid
        else:
            hi = mid
    print(f"   the recommendation survives an unselected ten-year flip rate up to "
          f"{lo:.1%}")
    print(f"   published: {AGED_FLIP_CONVENTIONAL:.1%} for a conventional bank, "
          f"{AGED_FLIP_RESISTANT:.1%} for the aging-resistant one")

    print("\n4. the condition the published figure carries")
    print(f"   both ten-year figures are taken at {PUBLISHED_ACTIVATION:.0%} activation "
          f"time - the fraction of")
    print(f"   wall-clock time the oscillators run. This design runs its bank once at "
          f"power-up")
    print(f"   for a few thousand cycles, so its activation time is orders below one "
          f"percent, and")
    print(f"   the paper's own Table I shows lower activation reducing the error. It "
          f"gives that")
    print(f"   sweep for the aging-resistant variant only - 7.81, 7.03, 7.01 percent at "
          f"23, 10, 5")
    print(f"   and 1 percent - and not for the conventional one. The figure this design "
          f"would see")
    print(f"   is therefore not in the source, and the requirement below is what has to "
          f"be met.")

    print("\n5. what selection buys against aging, which is not what it was adopted for")
    for label, s_age in (("conventional", sigma_age), ("aging-resistant", sigma_age_r)):
        sig = combined_sigma(sigma_noise, s_age)
        print(f"   {label:>16}: {effective(sig, 1.0):.4f} unselected -> "
              f"{effective(sig, KEEP):.4f} at {KEEP:.0%} kept "
              f"-> {effective(sig, 0.326):.4f} at 32.6%")
    print("   selection ranks by the manufacturing difference, and a large difference is")
    print("   exactly what an aging differential has to exceed - so it helps here for the")
    print("   same reason it helps against noise, and the enrolment reads that rank it")
    print("   are taken fresh, which is the part that does not transfer")
