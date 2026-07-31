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


def main():
    files = sorted(p for p in MODELS.glob("*.py")
                   if not p.name.startswith("_") and p.name not in HEAVY)
    if not files:
        print("FAIL: no models found, so this check read nothing", file=sys.stderr)
        return 1

    failures = []
    for path in files:
        result = subprocess.run([sys.executable, str(path)],
                                capture_output=True, text=True, cwd=ROOT)
        if result.returncode != 0:
            last = (result.stderr or result.stdout).strip().splitlines()[-1:]
            failures.append(f"{path.name}: {last[0] if last else 'non-zero exit'}")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_models_run: {len(failures)} of {len(files)} models do not run")
        return 1
    skipped = ", ".join(f"{n} ({why})" for n, why in sorted(HEAVY.items()))
    print(f"check_models_run: OK ({len(files)} models run"
          + (f"; not run: {skipped})" if skipped else ")"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
