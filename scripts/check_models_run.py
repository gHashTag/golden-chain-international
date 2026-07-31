#!/usr/bin/env python3
"""Every model in research/ must still run.

W-INTL-202: code_choice_model.py had not run since the decoder areas were re-keyed from
strings to (field bits, correction strength) tuples. Its construction table kept the old
strings, so it raised a KeyError on the first row - and nothing noticed for the whole
interval, because no check ran the models.

The checks in this repository verify that documents agree with the model and that
declared inputs are read. None of them executed the files that do the reasoning. That is
the same shape as the reproduction script that had only ever run on one machine: an
artefact nobody executes rots quietly, and the rot is invisible from every green run.

This runs each one and fails on a non-zero exit. It does not check the output - a model
whose numbers are wrong is a different problem, and one the figure checks already cover
for the numbers that reach a document. This covers the cheaper failure: the file no longer
runs at all.

Exit code 1 if any model fails. Intended to run in CI.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS = ROOT / "research"


# Models excluded, with the reason, because an exclusion nobody can see is a gap nobody
# knows about. quantiser_emulation_check.py needs torch: hundreds of megabytes on every
# CI run for one peripheral model that is not part of the identity-root recommendation.
# It is therefore unchecked here, which is a known gap rather than an unnoticed one, and
# the name is printed on every run so it stays known.
HEAVY = {"quantiser_emulation_check.py": "needs torch, which CI does not install"}


# One figure per model, recomputed from research/inputs.py and matched against what the
# model prints. W-INTL-203: running a model proves it does not raise, which is the
# cheapest failure and not the interesting one. A model can run perfectly and print a
# number that stopped being true three loops ago - which is exactly what burn_in.py did
# with its absorbable flip rate, and nothing here would have said so.
#
# Deliberately one figure each. This is not a test suite; it is a tripwire on the number
# each model exists to produce.
def _pointer_oscillators():
    """Oscillators the pointer family needs at the current recommendation. W-INTL-228.

    Was the literal 56, which was its count under the three-block construction. A
    tripwire holding a figure that the recommendation determines goes stale exactly when
    the thing it guards does.
    """
    import importlib
    P = importlib.import_module("pointer_vs_linear")
    return P.pairs_for(P.CODE[0] * P.BLOCKS * P.IBS_BLOCK)


def _k_total(I):
    """Bits of k the recommendation carries, recomputed here on an independent path."""
    import importlib
    SE = importlib.import_module("selection_entropy")
    rho = SE.density_for_bias(
        SE.selected_bias(SE.mean_for_density(SE.working_density()), I.SELECTION_LOSS)[0])
    return -(-int(I.KEY_BITS / rho) // 57) * 57


def _density_floor(I, R):
    """The declared min-entropy density below which the key stops fitting the code.

    Independent of research/borrowed_margins.py on purpose: it is the figure that model
    exists to print, and a tripwire that imports its subject checks nothing.
    """
    import importlib
    SE = importlib.import_module("selection_entropy")
    keep = 1.0 - I.SELECTION_LOSS
    lo, hi = 0.5, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        after = SE.density_for_bias(SE.selected_bias(SE.mean_for_density(mid), 1 - keep)[0])
        if I.KEY_BITS / after <= _k_total(I):
            hi = mid
        else:
            lo = mid
    return hi


def _expected():
    import importlib, math, sys as _sys
    _sys.path.insert(0, str(MODELS))
    I = importlib.import_module("inputs")
    R = importlib.import_module("reliable_bit_selection")
    _sys.path.insert(0, str(ROOT / "scripts"))
    C = importlib.import_module("check_figures_reproduce")

    absorbable = C.absorbable_flip() * 100
    return {
        "aging_margin.py": (
            r"survives an unselected ten-year flip rate up to ([\d.]+)%", absorbable, 0.06),
        "burn_in.py": (
            r"sigma at ([\d.]+)% \(what the construction absorbs\)", absorbable, 0.06),
        # Recomputed here through selection_entropy rather than imported from the model,
        # so the tripwire is an independent path. The first version of this entry copied
        # the model's own floor - KEY_BITS/k with no selection term - and so agreed with
        # a figure that was wrong by 0.13.
        "borrowed_margins.py": (
            r"tightest: min-entropy density at ([\d.]+) times",
            I.MIN_ENTROPY_DENSITY / _density_floor(I, R), 0.02),
        "min_entropy_from_shannon.py": (
            r"min-entropy, same fitted model\s+[\d.]+\s+([\d.]+)",
            I.MIN_ENTROPY_DENSITY, 0.0005),
        "nand_ring.py": (
            r"nand2_1 / inv_1 = ([\d.]+)", 1.0, 0.001),
        "selection_with_bch.py": (
            r"best: BCH\(127,(\d+),\d+\)", float(C.recommendation()[2]), 0.5),
        "selection_entropy.py": (
            r"measured density ([\d.]+) bits per position", I.MIN_ENTROPY_DENSITY, 0.0005),
        "reliable_bit_selection.py": (
            r"noise sigma [\d.]+ gives raw ber ([\d.]+)", 0.15, 0.001),
        "pointer_vs_linear.py": (
            r"pointer family is ([\d.]+) of a tile ahead",
            C.recommendation()[0] - I.tiles(
                I.decoder_area(7, 11) + I.POINTER_AREA["ibs_select_block4"]
                + I.COUNTERMEASURE_AREA["spongent_permutation"]
                + _pointer_oscillators() * I.OSCILLATOR_AREA), 0.02),
    }


def main():
    # --only <name> runs a single model. Each control re-ran all twelve, four minutes
    # each, and three controls took the job to eighteen minutes - W-INTL-211.
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    files = sorted(p for p in MODELS.glob("*.py")
                   if not p.name.startswith("_") and p.name not in HEAVY
                   and (only is None or p.name == only))
    if not files:
        print("FAIL: no models found, so this check read nothing", file=sys.stderr)
        return 1

    import re

    expected = _expected()
    failures = []
    checked = 0
    for path in files:
        result = subprocess.run([sys.executable, str(path)],
                                capture_output=True, text=True, cwd=ROOT)
        if result.returncode != 0:
            last = (result.stderr or result.stdout).strip().splitlines()[-1:]
            failures.append(f"{path.name}: {last[0] if last else 'non-zero exit'}")
            continue
        if path.name not in expected:
            continue
        pattern, want, tol = expected[path.name]
        m = re.search(pattern, result.stdout)
        if not m:
            failures.append(f"{path.name}: prints no figure matching {pattern!r}")
            continue
        checked += 1
        got = float(m.group(1))
        if abs(got - want) > tol:
            failures.append(
                f"{path.name}: prints {got:g} where inputs give {want:.4g} "
                f"(tolerance {tol})")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_models_run: {len(failures)} of {len(files)} models do not run")
        return 1
    want = len(expected) if only is None else (1 if only in expected else 0)
    if checked < want:
        print(f"FAIL: {checked} of {len(expected)} declared model figures were checked")
        return 1
    skipped = ", ".join(f"{n} ({why})" for n, why in sorted(HEAVY.items()))
    print(f"check_models_run: OK ({len(files)} models run, {checked} figures verified"
          + (f"; not run: {skipped})" if skipped else ")"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
