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

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS_CHECK = ROOT / "scripts" / "check_models_run.py"

# (quantity, first derivation, second derivation, where the agreement is bound)
PAIRED = [
    ("post-selection min-entropy density",
     "selection_entropy, one bias fitted to the declared density",
     "entropy_second_opinion, per-position biases with a spread",
     "entropy_second_opinion.py"),
    ("ordering min-entropy at the design's oscillator count",
     "ordering_achievable, sequential Monte Carlo",
     "ordering_exact, the chain integral in one dimension",
     "ordering_exact.py"),
    ("selected bit error rate at the declared fraction",
     "reliable_bit_selection.selected_ber_counts_exact, closed form",
     "multi_condition_enrolment, Monte Carlo with a fixed seed",
     "multi_condition_enrolment.py"),
    ("word failure of the recommendation",
     "the binomial sum in check_figures_reproduce",
     "key_generator_e2e, the whole chain in software",
     "key_generator_e2e.py"),
    ("min-entropy implied by the published Shannon figure",
     "min_entropy_from_shannon, a Gaussian spread fitted to reproduce it",
     "the same file's distribution-free floor, from convexity and Jensen",
     "min_entropy_from_shannon.py"),
]

# Quantities with one derivation, and what that costs. This is the half worth reading.
SINGLE = {
    "every synthesised area":
        "verify_inputs re-runs yosys, which checks transcription rather than derivation - "
        "a second path would be counting cells in the netlist against the liberty file. "
        "Not done; W-INTL-233 records that two of these cannot be re-measured at all",
    "tolerated bit error rate":
        "one bisection over the binomial, in aging_margin. The binomial itself now has a "
        "second witness through key_generator_e2e, so what is unchecked is the bisection",
    "the tile arithmetic":
        "cells / utilisation / tile area, three multiplications - a second derivation "
        "would restate the same arithmetic and witness nothing",
    "oscillator floor and pairs-for-positions":
        "two counting loops, checked by inspection; the ordering bound they feed has two "
        "derivations and is the load-bearing half",
    "the aging drift model":
        "aged_selected_ber has one derivation. W-INTL-232 corrected its structure and "
        "W-INTL-242 its quadrature, both by reading rather than by comparison. This is "
        "the largest quantity in the work with no second path",
}


def main():
    bound = MODELS_CHECK.read_text()
    failures = []
    for quantity, first, second, where in PAIRED:
        if f'"{where}"' not in bound:
            failures.append(
                f"{quantity}: the agreement between two derivations is recorded here as "
                f"bound in {where}, and check_models_run does not mention that file")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_second_opinions: {len(failures)} of {len(PAIRED)} agreements are "
              f"no longer bound")
        return 1

    print(f"check_second_opinions: OK ({len(PAIRED)} quantities derived twice with the "
          f"agreement bound, {len(SINGLE)} with one derivation)")
    for quantity, _, _, where in PAIRED:
        print(f"  two paths: {quantity} -> {where}")
    for quantity, why in sorted(SINGLE.items()):
        print(f"  one path:  {quantity} - {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
