#!/usr/bin/env python3
"""Burn-in before enrolment, costed - and it does not do what the last loop hoped.

W-INTL-163 took a lever from a silicon source: "S-ASCH benefits from having a burn-in
process prior to enrollment", because enrolling after some aging means the required
masking ratio does not rise aggressively. It was recorded as a second route to the
ten-year aging requirement, at no area cost, needing "at most 28 percent of the
degradation still to come".

Two things are wrong with that sentence and this file fixes both.

**The 28 percent was in the wrong units.** It compared flip rates: 9.2 percent absorbed
against 32.41 percent at ten years. But the quantity that accumulates under an aging law
is the degradation, and what the source model carries is sigma - the width of the aging
differential. In sigma the requirement is 0.2974 against 1.6215, which is **18.3 percent**,
not 28. Flip rate is a saturating function of sigma, so a ratio taken in flip rates
flatters the requirement.

**And "no area cost" is not "no cost".** Burn-in costs time before enrolment, which is
the number nobody computed. It is computed here, and it is large.

The chain, with every assumption named:

  1. NBTI threshold-voltage shift follows a power law in time, dVth ~ t^n. This is
     standard and the exponent is technology-dependent; the literature range is roughly
     0.15 to 0.5, so n is swept rather than chosen.
  2. The *differential* degradation between the two oscillators of a pair inherits that
     time dependence. This is the load-bearing assumption. It is not verified by any
     source read here, so it is swept rather than assumed: the differential is taken as
     t^(k*n) with k of 1.0 (it inherits the law) and 0.5 (it grows as the square root of
     the mean, which is what a trap-counting picture gives, since a Poisson number of
     trapped charges has a standard deviation going as the square root of its mean).

     The literature searched supports only the direction - aging-induced threshold-voltage
     variability grows with stress and correlates with gate-oxide area - and no source
     read here gives the functional form. Both arms are therefore reported, and the k=0.5
     arm is the convenient one, which is reason to quote it rather than adopt it.
  3. sigma_age scales with the differential, which is how it was calibrated.
  4. Enrolling at burn-in time Tb leaves the fraction 1 - (Tb/T)^n of the ten-year
     differential still to come.

So the requirement 1 - (Tb/T)^n <= 0.183 gives Tb >= T * 0.817^(1/n).
"""

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import reliable_bit_selection as R

TEN_YEARS = 10.0
FLIP_TEN_YEAR = 0.3241        # conventional bank, DATE 2014
FLIP_ABSORBED = 0.092         # what this construction absorbs post-enrolment
EXPONENTS = (0.16, 0.20, 0.25, 0.30, 0.50)
DIFFERENTIAL_SCALING = (1.0, 0.5)   # k in differential ~ t^(k*n); see assumption 2

# measured there: He, Li, Yu and Yang, ASCH-PUF in JSSC. "A stressing of 96 hours in
# total was applied, resulting in equivalent effects of several years' aging under
# nominal conditions", at 150 C and 1.4 V. "Several" is not a number, so the wall-clock
# conversion below carries a range with an unquantified endpoint rather than a figure.
ACCEL_HOURS = 96
ACCEL_YEARS_LOW, ACCEL_YEARS_HIGH = 2.0, 5.0


if __name__ == "__main__":
    sigma_ten = R.sigma_for_raw_ber(FLIP_TEN_YEAR)
    sigma_ok = R.sigma_for_raw_ber(FLIP_ABSORBED)
    ratio = sigma_ok / sigma_ten

    print("1. the requirement, in the units that accumulate")
    print(f"   sigma at {FLIP_TEN_YEAR:.2%} (ten years, conventional bank) "
          f"{sigma_ten:.4f}")
    print(f"   sigma at {FLIP_ABSORBED:.2%} (what the construction absorbs)  "
          f"{sigma_ok:.4f}")
    print(f"   so the post-enrolment differential may be {ratio:.1%} of the ten-year one")
    print(f"   the previous loop quoted {FLIP_ABSORBED/FLIP_TEN_YEAR:.1%}, taken in flip "
          f"rates rather than in sigma;")
    print(f"   flip rate saturates in sigma, so that ratio flattered the requirement")

    print("\n2. how much of the service life must be burned in first")
    print(f"   {'exponent n':>11} " +
          "".join(f"{'k=%.1f years' % k:>16}" for k in DIFFERENTIAL_SCALING) +
          f"{'share, k=1':>12}{'share, k=0.5':>14}")
    for n in EXPONENTS:
        tbs = [TEN_YEARS * (1 - ratio) ** (1 / (k * n)) for k in DIFFERENTIAL_SCALING]
        print(f"   {n:11.2f} " + "".join(f"{t:16.2f}" for t in tbs) +
              f"{tbs[0]/TEN_YEARS:11.0%}{tbs[1]/TEN_YEARS:14.0%}")
    print("   the exponent is technology-dependent and this is the published range, so")
    print("   the answer is a bracket. Under k=1 it is between a quarter and two thirds of")
    print("   the service life; under k=0.5, where the differential grows as the square")
    print("   root of the mean degradation, it is between eight and forty-five percent.")
    print("   k=0.5 is the convenient arm and no source read here establishes the form,")
    print("   so the requirement is quoted against k=1 and the other is a sensitivity.")

    print("\n3. in oven hours, with the one acceleration figure available")
    lo = TEN_YEARS * (1 - ratio) ** (1 / max(EXPONENTS))
    hi = TEN_YEARS * (1 - ratio) ** (1 / min(EXPONENTS))
    # quoted against k = 1, the arm that is not the convenient one
    print(f"   {ACCEL_HOURS} hours at 150 C and 1.4 V is 'several years' of nominal "
          f"aging;")
    print(f"   reading 'several' as {ACCEL_YEARS_LOW:.0f} to {ACCEL_YEARS_HIGH:.0f} "
          f"years,")
    for years, label in ((lo, "n = 0.50"), (hi, "n = 0.16")):
        h_lo = ACCEL_HOURS * years / ACCEL_YEARS_HIGH
        h_hi = ACCEL_HOURS * years / ACCEL_YEARS_LOW
        print(f"   {label}: {years:.1f} equivalent years -> {h_lo:.0f} to {h_hi:.0f} "
              f"hours of burn-in per part")

    print("\n4. the conclusion, which is not the one the lever was recorded as")
    print("   burn-in cannot replace the aging-resistant oscillator. Leaving only 18")
    print("   percent of the differential still to come means pre-aging the part for a")
    print("   quarter to two thirds of its service life - days of oven time each, and a")
    print("   provisioning step that has to be qualified rather than merely scheduled.")
    print("   It remains useful as a supplement: applied to a bank that already meets the")
    print("   requirement, it widens the margin rather than creating it.")
    print("   'No area cost' was true and was not the cost that mattered.")
