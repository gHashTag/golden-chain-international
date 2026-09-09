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

# Names that mean "how finely did you ask". Discovery works from these rather than from a
# list of functions, because W-INTL-233 recorded what a list does: it covers the names its
# author thought of. The first version of this file enumerated six cases and there were
# thirteen such functions in research/ - W-INTL-243.
RESOLUTION_NAMES = ("steps", "grid", "trials", "samples")

# Discovered functions not exercised above, each with the reason. A sampling estimator has
# statistical convergence rather than deterministic, so a coarse-against-fine comparison is
# a test of luck; those carry their own validity checks instead and are named here.
EXEMPT = {
    "min_entropy_from_shannon._integrate":
        "the primitive the two densities below are built from, exercised through them",
    "min_entropy_from_shannon.fitted_spread":
        "a bisection over _integrate, and the density it fits is exercised",
    "entropy_second_opinion._kept_fraction":
        "the primitive threshold_for bisects over, exercised through it",
    "ordering_achievable.log2_p_most_likely":
        "Monte Carlo, superseded by ordering_exact; its own impossibility test is the "
        "check that matters and W-INTL-240 discarded the rows that failed it",
    "ordering_achievable.ratio_at":
        "wraps the Monte Carlo above",
    "multi_condition_enrolment.selected_ber_conditional":
        "Monte Carlo with a fixed seed, and it returns its own measured standard error - "
        "which is a stronger statement than a coarse-against-fine comparison, since that "
        "would test whether two sample sizes happened to land near each other. "
        "check_second_opinions uses that error to state what the comparison can resolve",
    "multi_condition_enrolment.selected_ber":
        "Monte Carlo with a fixed seed; its agreement with the closed form at the shared "
        "case is bound as a figure in check_models_run, which is the stronger statement",
    "reliable_bit_selection.avalanche":
        "a diagnostic that reaches no document and no recommendation",
    "reliable_bit_selection.selection_curve":
        "prints a table for reading; every figure it feeds is computed elsewhere",
}


def cases():
    """(qualified name, label, callable taking a resolution) for each covered integrator."""
    import entropy_second_opinion as E
    import min_entropy_from_shannon as M
    import ordering_exact as OE

    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    aging = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    keep = 1.0 - I.SELECTION_LOSS
    spread = M.densities()[2]
    return [
        ("entropy_second_opinion.two_level_density", "two-level density",
         lambda n: E.two_level_density(steps=n)),
        ("entropy_second_opinion.threshold_for", "two-level threshold",
         lambda n: E.threshold_for(keep, spread, n)),
        # The one whose grid dependence is real: the trapezoid converges as grid^-2, so a
        # caller asking coarsely gets a materially different answer. At the default 6,000
        # the equal-means self-test is off by 0.05 bits in 237, which is why the default is
        # what it is - W-INTL-243.
        ("ordering_exact.log2_p_ordered", "ordering probability at twenty",
         lambda n: OE.log2_p_ordered([0.0] * 20, grid=max(n, 2000))),
        ("reliable_bit_selection.selected_ber_counts_exact", "design point",
         lambda n: R.selected_ber_counts_exact(noise, keep, I.ENROLMENT_READS, steps=n)),
        ("reliable_bit_selection.selected_ber_counts_exact", "deep selection",
         lambda n: R.selected_ber_counts_exact(noise, 0.20, I.ENROLMENT_READS, steps=n)),
        ("reliable_bit_selection.aged_selected_ber", "design point",
         lambda n: R.aged_selected_ber(noise, aging, keep, I.ENROLMENT_READS, steps=n)),
        ("reliable_bit_selection.aged_selected_ber", "deep selection",
         lambda n: R.aged_selected_ber(noise, aging, 0.20, I.ENROLMENT_READS, steps=n)),
        ("reliable_bit_selection.aged_selected_ber", "no selection",
         lambda n: R.aged_selected_ber(noise, aging, 1.0, I.ENROLMENT_READS, steps=n)),
        ("reliable_bit_selection.aged_selected_ber_with_burn_in", "half the drift",
         lambda n: R.aged_selected_ber_with_burn_in(noise, aging, 0.5, keep,
                                                    I.ENROLMENT_READS, steps=n)),
    ]


def discovered():
    """Every function in research/ taking a resolution argument, as module.name."""
    import ast
    found = []
    for path in sorted((ROOT / "research").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            names = [a.arg for a in node.args.posonlyargs + node.args.args
                     + node.args.kwonlyargs]
            if any(n in RESOLUTION_NAMES for n in names):
                found.append(f"{path.stem}.{node.name}")
    return found


def main():
    failures = []
    checked = 0

    covered = {name for name, _, _ in cases()}
    for name in discovered():
        if name in covered or name in EXEMPT:
            continue
        failures.append(
            f"{name} takes a resolution argument and is neither exercised here nor listed "
            f"in EXEMPT with a reason")
    for name in EXEMPT:
        if name not in discovered():
            failures.append(f"EXEMPT names {name}, which research/ no longer defines")
    for qualified, name, call in cases():
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
    print(f"check_quadrature_converged: OK ({checked} cases over "
          f"{len({q for q, _, _ in cases()})} integrators agree between {COARSE} and "
          f"{FINE}, within {RELATIVE:.1%}; {len(discovered())} take a resolution argument, "
          f"{len(EXEMPT)} exempt)")
    for name, why in sorted(EXEMPT.items()):
        print(f"  exempt: {name} - {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
