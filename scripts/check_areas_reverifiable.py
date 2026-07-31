#!/usr/bin/env python3
"""Every declared area must be re-measurable, or listed as not, with the reason.

W-INTL-233. `verify_inputs.py` re-synthesises the decoders, the SLLC stages, the
countermeasure, the pointer datapath, the characteriser and both solver forms - thirty-one
areas - and compares each against what `inputs.py` declares. Two declared areas are not in
that loop and cannot be: the numerator of `UTILISATION` and `INVERTER_AREA` both come from
synthesising the published eight-bit PUF tile, whose RTL is not in this repository.

Nothing said so. Both were declared "measured there", which reads as somebody else's
number and therefore not ours to reproduce, and the note recording where they came from -
"Synthesis of the published eight-bit implementation" - is in a different file. The result
was two figures that look exactly like the thirty-one verified ones and are the only two
that no tool in this repository has re-run since the day they were written.

That is the shape of W-INTL-201, where a measured pointer area sat outside the verify loop
and nothing noticed, one level out: there the fix was to add it to the loop, and here the
loop cannot reach it.

So the rule is not "everything must be re-measured". It is that the set of areas nothing
re-measures must be written down, with why, and must not grow silently. This check fails if
a declared area is neither covered by verify_inputs nor listed below.

Exit code 1 on an area that is in neither set.
"""

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INPUTS = ROOT / "research" / "inputs.py"
VERIFY = ROOT / "scripts" / "verify_inputs.py"

# Declared areas that verify_inputs cannot re-measure, and why. Each entry is a standing
# admission, not a waiver: it says this number has not been re-run since it was written.
NOT_REVERIFIABLE = {
    "UTILISATION":
        "its numerator is our synthesis of the published eight-bit PUF tile, whose RTL "
        "is not in this repository; the denominator is that design's declared footprint",
    "INVERTER_AREA":
        "same synthesis run as the UTILISATION numerator, same missing RTL - cross-checked "
        "instead against sky130_fd_sc_hd__inv_1 at a ratio of 1.0009, which is a different "
        "kind of evidence and the reason this one is the sounder of the two",
    "AGING_RESISTANT_FACTOR":
        "a ratio of published transistor widths, not an area measurement at all; bracketed "
        "against the library's tristate inverters at 1.33 to 1.67 and declared conservative",
    "TILE_AREA":
        "a published specification - one Tiny Tapeout tile, 161 by 112 micrometres - not "
        "a synthesis result, so there is nothing to re-run",
    "OSCILLATOR_AREA":
        "a product of INVERTER_AREA, INVERTERS_PER_OSCILLATOR and AGING_RESISTANT_FACTOR, "
        "so it is re-verifiable exactly as far as those are",
}

AREA_NAMES = ("AREA", "UTILISATION")


def declared_areas():
    """Names in inputs.py that denote an area or an area ratio."""
    src = INPUTS.read_text()
    out = []
    for node in ast.parse(src).body:
        if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        if any(marker in name for marker in AREA_NAMES) or name == "AGING_RESISTANT_FACTOR":
            out.append(name)
    return out


def main():
    verify_src = VERIFY.read_text()
    names = declared_areas()
    if not names:
        print("FAIL: no declared areas found, so this check read nothing", file=sys.stderr)
        return 1

    failures, covered = [], []
    for name in names:
        if f"I.{name}" in verify_src:
            covered.append(name)
        elif name in NOT_REVERIFIABLE:
            continue
        else:
            failures.append(
                f"{name} is a declared area that verify_inputs.py does not re-measure and "
                f"NOT_REVERIFIABLE does not list; either add it to the verify loop or "
                f"record why it cannot be")

    stale = [n for n in NOT_REVERIFIABLE if n not in names]
    for n in stale:
        failures.append(f"NOT_REVERIFIABLE names {n}, which inputs.py no longer declares")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_areas_reverifiable: {len(failures)} of {len(names)} declared areas")
        return 1

    print(f"check_areas_reverifiable: OK ({len(names)} declared areas, {len(covered)} "
          f"re-synthesised by verify_inputs, {len(NOT_REVERIFIABLE)} recorded as not)")
    for name, why in sorted(NOT_REVERIFIABLE.items()):
        print(f"  not re-measurable: {name} - {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
