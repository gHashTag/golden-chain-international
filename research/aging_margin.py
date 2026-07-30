#!/usr/bin/env python3
"""Aging, which the constraint register has listed as unchecked since it was written.

Every error-rate figure in this work is a fresh-device figure. The register says so and
names the gap. This turns the gap into a number.

The source is read rather than summarised. Rahman, Forte, Fahrny and Tehranipoor,
"ARO-PUF: An Aging-Resistant Ring Oscillator PUF Design", DATE 2014:

    "After 10 years, the average error in response of the ARO-PUF is 7.73%, whereas it
    is 32.41% in the conventional RO-PUF."

and on the mechanism:

    "The frequency degradation in 10 years is about 1.8% in our proposed ARO whereas it
    is about 14.4% for a conventional RO."

The previous version of this file quoted the 1.8 percent as a *common* drift shared by
both oscillators of a pair and therefore harmless. That was a misreading, corrected here:
1.8 percent is the aging-resistant oscillator's own degradation and 14.4 percent is the
conventional one's. The reason a drift figure does not directly give a flip rate stands -
a response bit is a comparison, so what flips it is the difference between the two
oscillators' degradations rather than either one - but the numbers above are per-device
degradation rates, not a common-mode term.

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
from math import comb


def tolerated_ber(n=127, t=11, blocks=3):
    """Largest bit error rate at which the code still meets the declared target."""
    lo, hi = 0.0, 0.5
    for _ in range(60):
        mid = (lo + hi) / 2
        per = sum(comb(n, i) * mid**i * (1 - mid)**(n - i) for i in range(t + 1, n + 1))
        if 1 - (1 - per) ** blocks <= I.TARGET_FAILURE:
            lo = mid
        else:
            hi = mid
    return lo

# measured there: DATE 2014, conditions above. Response-bit flip rate at ten years for a
# conventional ring-oscillator PUF, and for the aging-resistant variant the same paper
# proposes.
AGED_FLIP_CONVENTIONAL = 0.3241
AGED_FLIP_RESISTANT = 0.0773
DEGRADATION_ARO = 0.018
DEGRADATION_CONVENTIONAL = 0.144

# Corrected. The previous version of this file argued that this design's activation time -
# the fraction of wall-clock time the oscillators run - is orders below the 23 percent the
# published figures were taken at, and that lower activation reduces the error, so the
# conventional figure was probably pessimistic here.
#
# That is true of the aging-resistant oscillator and false of the conventional one, and
# the paper says so in a passage that was already on disk when the argument was written:
#
#     "In all cases, when the conventional RO-PUF is put in the oscillating (AC stress) or
#     non-oscillating mode (DC stress) when it is not used, it will experience significant
#     amount of aging"
#
# An idle conventional ring oscillator sits with its inverter inputs at a constant value,
# which is DC stress and the worst case for NBTI on the pMOS. Not running it is not
# resting it. The ARO's whole mechanism is a transistor that holds those inputs at
# VDD - VT while idle so the pMOS never sees a zero; that is why its Table I sweep of
# activation time is given for the ARO and not for the conventional device.
#
# So low duty cycle is not a defence for the conventional bank. The 32.41 percent stands.
PUBLISHED_ACTIVATION = 0.23

RAW_NOISE_BER = 0.06          # the fresh-device figure this project has been using
KEEP = 1 - I.SELECTION_LOSS   # the design keeps eighty percent


def combined_sigma(*sigmas):
    """Independent Gaussian perturbations of the difference add in quadrature."""
    return sqrt(sum(s * s for s in sigmas))


def effective(sigma, keep):
    # The achievable figure, not the bound. This file called the bound for four loops
    # and reported the result as the design's ten-year error rate; W-INTL-186 named it
    # and W-INTL-191 is it still being called one loop after the rename made it legible.
    return R.selected_ber_counts_exact(sigma, keep, I.ENROLMENT_READS)


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
    print(f"   ten-year frequency degradation is {DEGRADATION_ARO:.1%} for the "
          f"aging-resistant oscillator")
    print(f"   and {DEGRADATION_CONVENTIONAL:.1%} for the conventional one; the flip "
          f"rates above are what")
    print(f"   those degradations produce once paired, and are the figures modelled here")

    print("\n2. what the design sees, fresh and at ten years")
    print(f"   {'oscillator':>16} {'age':>8} {'selection':>10} {'effective BER':>14} "
          f"{'code tolerates':>15} {'verdict':>9}")
    # Derived rather than written down: what the recommendation's code tolerates at the
    # declared word-failure target. It was the literal 0.0442 in three files, which is
    # the pattern inputs.py exists to prevent - see W-INTL-193.
    TOLERATED = tolerated_ber()
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

    print("\n4. low duty cycle is not a defence, which is the correction")
    print(f"   the published figures are at {PUBLISHED_ACTIVATION:.0%} activation time "
          f"and this design's bank runs")
    print(f"   once at power-up, so the previous version of this file argued the "
          f"conventional figure")
    print(f"   was pessimistic here. The paper contradicts that: an idle conventional "
          f"oscillator sits")
    print(f"   at DC stress, which is the worst case for NBTI on the pMOS. Not running "
          f"it is not")
    print(f"   resting it. The aging-resistant design exists precisely to hold those "
          f"inputs away from")
    print(f"   zero while idle, which is why the activation sweep is given for it and "
          f"not for the")
    print(f"   conventional device. The 32.41 percent stands.")

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
