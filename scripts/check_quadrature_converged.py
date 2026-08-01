#!/usr/bin/env python3
"""No figure may depend on how finely the caller asked for it.

W-INTL-242. `aged_selected_ber` integrated over the whole axis, skipped the samples inside
the selection threshold, and divided by however many survived. That makes the denominator
an integer approximation of the kept mass, so one sample lands on the answer - and one
sample is a six-hundredth of the mass at the resolution five call sites use.

The figures moved with `steps`, non-monotonically, which is the signature of a hard domain
boundary the grid does not align to:

    steps    aged figure
      300      0.0038135
      600      0.0036695     <- what aging_margin, borrowed_margins and burn_in asked for
     1200      0.0036697
     4000      0.0036769     <- what check_figures_reproduce asked for
    64000      0.0036769

Two call paths, two answers, 0.2 percent apart, and every check green throughout - because
each check compared a document against whichever value its own call produced.

Integrating over the kept tail directly fixes it, and the fixed version has five correct
figures at 150 steps. That is the sibling function's arrangement, already corrected once
for a related fault, sitting three lines below in the same file.

This check exists so the class cannot come back: every integrator that takes a `steps`
argument must agree with itself between a coarse setting and a fine one. It is not a
tolerance on accuracy - it is the statement that the answer is a property of the question
rather than of the caller.

Exit code 1 if any integrator moves by more than RELATIVE between the two resolutions.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

import inputs as I  # noqa: E402
import reliable_bit_selection as R  # noqa: E402

COARSE, FINE = 200, 20_000
RELATIVE = 1e-3


def cases():
    """(name, callable taking steps) for every integrator a caller can resolve."""
    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    aging = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    keep = 1.0 - I.SELECTION_LOSS
    return [
        ("selected_ber_counts_exact, design point",
         lambda n: R.selected_ber_counts_exact(noise, keep, I.ENROLMENT_READS, steps=n)),
        ("selected_ber_counts_exact, deep selection",
         lambda n: R.selected_ber_counts_exact(noise, 0.20, I.ENROLMENT_READS, steps=n)),
        ("aged_selected_ber, design point",
         lambda n: R.aged_selected_ber(noise, aging, keep, I.ENROLMENT_READS, steps=n)),
        ("aged_selected_ber, deep selection",
         lambda n: R.aged_selected_ber(noise, aging, 0.20, I.ENROLMENT_READS, steps=n)),
        ("aged_selected_ber, no selection",
         lambda n: R.aged_selected_ber(noise, aging, 1.0, I.ENROLMENT_READS, steps=n)),
        ("aged_selected_ber_with_burn_in, half the drift",
         lambda n: R.aged_selected_ber_with_burn_in(noise, aging, 0.5, keep,
                                                    I.ENROLMENT_READS, steps=n)),
    ]


def main():
    failures = []
    checked = 0
    for name, call in cases():
        coarse, fine = call(COARSE), call(FINE)
        checked += 1
        if fine == 0.0:
            if coarse != 0.0:
                failures.append(f"{name}: {coarse:g} at {COARSE} steps, zero at {FINE}")
            continue
        moved = abs(coarse - fine) / fine
        if moved > RELATIVE:
            failures.append(
                f"{name}: {coarse:.7g} at {COARSE} steps against {fine:.7g} at {FINE}, "
                f"{moved:.2%} apart - the figure depends on how finely it was asked for")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_quadrature_converged: {len(failures)} of {checked} integrators "
              f"move with the caller's resolution")
        return 1
    if checked == 0:
        print("FAIL: no integrators checked, so this check read nothing", file=sys.stderr)
        return 1
    print(f"check_quadrature_converged: OK ({checked} integrators agree between {COARSE} "
          f"and {FINE} steps, within {RELATIVE:.1%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
