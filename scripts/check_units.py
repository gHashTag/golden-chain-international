#!/usr/bin/env python3
"""Every ratio in inputs.py must say what units its numerator and denominator are in.

Written after W-INTL-166, where the same error appeared twice in three loops: a ratio
taken in whichever units were nearest to hand, in both cases the units that made the
answer convenient. The second instance divided two flip rates where the quantity that
accumulates is the aging differential, and flip rate is a saturating function of it.

The disposition - be careful where the answer is convenient - was already written in the
skill file when the second instance was made. So this is the mechanical form: a ratio in
the file of inputs has to carry a `units:` line naming what is being divided by what, and
the check fails if one does not.

It cannot verify that the units are *right*. What it can do is make the claim explicit, so
that a ratio of a width to a width applied to an area is visible as such rather than
buried in a constant. That is the case it caught on its first run.

Exit code 1 if any ratio is undeclared. Intended to run in CI.
"""

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = ROOT / "research" / "inputs.py"

# A name is a ratio if its value divides, or if it is dimensionless by construction.
DIMENSIONLESS_SUFFIXES = ("FACTOR", "DENSITY", "LOSS", "OVERHEAD")


def main():
    src = TARGET.read_text()
    lines = src.splitlines()
    tree = ast.parse(src)

    failures = []
    checked = 0

    for node in tree.body:
        if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        segment = ast.get_source_segment(src, node.value) or ""
        is_ratio = "/" in segment or name.endswith(DIMENSIONLESS_SUFFIXES) \
            or name == "UTILISATION"
        if not is_ratio:
            continue
        checked += 1

        # The declaration is a comment line "units: <numerator> / <denominator>" in the
        # block immediately above the assignment. Walk back over contiguous comments.
        i = node.lineno - 2
        found = False
        while i >= 0 and (lines[i].lstrip().startswith("#") or not lines[i].strip()):
            if re.search(r"#\s*units:\s*\S", lines[i]):
                found = True
                break
            if not lines[i].strip() and found:
                break
            i -= 1
        if not found:
            failures.append(
                f"{name} is a ratio with no 'units:' line above it - say what is being "
                f"divided by what")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_units: {len(failures)} of {checked} ratios undeclared")
        return 1
    if checked == 0:
        print("FAIL: no ratios found in inputs.py, which means this check read nothing")
        return 1
    print(f"check_units: OK ({checked} ratios, each declaring its units)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
