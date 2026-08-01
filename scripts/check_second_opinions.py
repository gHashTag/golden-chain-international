#!/usr/bin/env python3
"""Which load-bearing quantities have a second derivation, and which have one.

W-INTL-245. Comparing a figure against itself computed a different way has found four
defects in five loops - W-INTL-238, 241, 242, 244 - and every one was found by hand,
because nothing here records which quantities have a second path and which do not.

That is the wrong way round. A quantity with two derivations is checked; a quantity with
one is where the next defect is, and the list of those is the list nobody keeps.

This check keeps it. Each entry names a quantity, the two derivations, and the figure that
records their agreement - or says there is only one derivation, and why that is acceptable
or merely current. It fails when an agreement stops being bound, because an agreement
nobody re-evaluates decays exactly like the transcription it replaced.

It cannot discover its own subjects. There is no signature that says "this is a
load-bearing quantity", so the population is written down - and unlike the enumerations
W-INTL-243 and W-INTL-244 corrected, the failure mode here is visible: a quantity missing
from this file is a quantity nobody claimed had a second opinion.

Exit code 1 if a declared agreement is no longer bound by check_models_run.
"""

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "research"))
import inputs as I  # noqa: E402
import reliable_bit_selection as R  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS_CHECK = ROOT / "scripts" / "check_models_run.py"

# Quantities with one derivation, and what that costs. The half worth reading: it names
# where the next defect is. The aging drift model was here in the first version and should
# not have been - W-INTL-246 found the second path already existed and had since
# W-INTL-237, which is what a list that asserts rather than computes does within a loop.
SINGLE = {
    "every synthesised area":
        "verify_inputs re-runs yosys, which checks transcription rather than derivation - "
        "a second path would be counting cells in the netlist against the liberty file. "
        "Not done, and W-INTL-233 records that two of these cannot be re-measured at all. "
        "This is now the largest quantity in the work with one derivation",
    "tolerated bit error rate":
        "one bisection over the binomial in aging_margin. The binomial has a second "
        "witness through key_generator_e2e, so what is unchecked is the bisection",
    "the tile arithmetic":
        "cells / utilisation / tile area - a second derivation would restate the same "
        "three multiplications and witness nothing",
    "oscillator floor and pairs-for-positions":
        "two counting loops, checked by inspection; the ordering bound they feed has two "
        "derivations and is the load-bearing half",
    "word failure of the recommendation":
        "the binomial sum, with key_generator_e2e as a witness bound in check_models_run "
        "rather than computed here, because running the whole chain costs minutes",
}


def comparisons():
    """(quantity, first, second, value one, value two, tolerance, units) computed here.

    W-INTL-246: the first version of this file asserted that agreements were bound
    elsewhere and listed which quantities had one derivation. It was wrong within one
    iteration - it named the aging drift model as the largest quantity with no second
    path, and `multi_condition_enrolment` with a zero temperature term had been that path
    since W-INTL-237. A register that asserts is a register that goes stale; this one
    computes.
    """
    import entropy_second_opinion as E
    import min_entropy_from_shannon as M
    import multi_condition_enrolment as MC
    import ordering_achievable as OA
    import ordering_exact as OE
    import random

    keep = 1.0 - I.SELECTION_LOSS
    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    aging = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    out = []

    out.append((
        "post-selection min-entropy density",
        "selection_entropy, one bias fitted to the declared density",
        "entropy_second_opinion, per-position biases with a spread",
        E.single_bias_density(), E.two_level_density(), 0.02, "relative"))

    # The aging drift, which the register's first version said had no second path. The
    # sampled estimator at a zero temperature term is exactly this quantity. Conditional
    # rather than flip-counting since W-INTL-247, which took the resolution from ten
    # percent to two and a half - past the eight percent error W-INTL-232 corrected, which
    # the flip-counting version would have passed.
    mc, mc_err = MC.selected_ber_conditional(0.0, keep)
    out.append((
        "selected error rate at ten years",
        "reliable_bit_selection.aged_selected_ber, closed form",
        "multi_condition_enrolment, conditional sampling at a zero temperature term",
        R.aged_selected_ber(noise, aging, keep, I.ENROLMENT_READS), mc, 3.0,
        ("measured standard errors", mc_err)))

    # The ordering entropy, compared where the Monte Carlo is still valid - it fails its
    # own impossibility test above fourteen oscillators, which is W-INTL-240.
    spread = M.densities()[2]
    rng = random.Random(7)
    mu = sorted(rng.gauss(0.0, spread) for _ in range(12))
    out.append((
        "ordering min-entropy, twelve oscillators",
        "ordering_achievable, sequential Monte Carlo",
        "ordering_exact, the chain integral in one dimension",
        -OA.log2_p_most_likely(mu, trials=200_000, seed=91),
        -OE.log2_p_ordered(mu), 0.05, "relative"))

    return out


def sandwich():
    """(label, low, middle, high) for the bound the min-entropy conversion sits inside."""
    import min_entropy_from_shannon as M
    return ("min-entropy implied by the published Shannon figure",
            M.distribution_free_bound(), I.MIN_ENTROPY_DENSITY,
            I.SHANNON_ENTROPY_BITS / I.MIN_ENTROPY_OVER)


def main():
    failures = []
    rows = comparisons()
    for quantity, first, second, one, two, tol, units in rows:
        kind = units if isinstance(units, str) else units[0]
        if kind == "relative":
            apart = abs(one - two) / abs(two) if two else 0.0
            ok = apart <= tol
            detail = f"{apart:.2%} apart, tolerance {tol:.0%}"
        else:
            # The standard error the estimator measured on its own sample, rather than a
            # binomial band assumed from the mean - the conditional estimator is not a
            # proportion and a binomial band would overstate its noise threefold.
            band = units[1]
            apart = abs(one - two) / band if band else 0.0
            ok = apart <= tol
            # The resolution, stated rather than implied. A sampling comparison can only
            # see a difference larger than its own noise, and this one cannot resolve the
            # eight percent modelling error W-INTL-232 corrected - that is 1.4 standard
            # errors here. W-INTL-246: a check whose power is unstated reads as coverage
            # it does not have.
            resolution = tol * band / abs(two) if two else 0.0
            detail = (f"{apart:.2f} standard errors, tolerance {tol:.0f}; this comparison "
                      f"resolves differences above {resolution:.1%}")
        if not ok:
            failures.append(f"{quantity}: {one:.6g} against {two:.6g}, {detail}")

    label, low, middle, high = sandwich()
    if not low <= middle <= high:
        failures.append(
            f"{label}: the fitted {middle:.4f} is outside the proven interval "
            f"[{low:.4f}, {high:.4f}] - the floor rests on convexity and the ceiling on "
            f"min-entropy never exceeding Shannon, so one of those has stopped holding")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_second_opinions: {len(failures)} of {len(rows) + 1} "
              f"comparisons disagree")
        return 1

    print(f"check_second_opinions: OK ({len(rows)} quantities computed both ways and "
          f"agreeing, one bound sandwich, {len(SINGLE)} with one derivation)")
    for quantity, first, second, one, two, tol, units in rows:
        if isinstance(units, tuple):
            note = f"  (resolves above {tol * units[1] / abs(two):.1%})"
        else:
            note = f"  (resolves above {tol:.0%})"
        print(f"  two paths: {quantity}: {one:.6g} / {two:.6g}{note}")
    print(f"  sandwich:  {label}: {low:.4f} <= {middle:.4f} <= {high:.4f}")
    for quantity, why in sorted(SINGLE.items()):
        print(f"  one path:  {quantity} - {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
