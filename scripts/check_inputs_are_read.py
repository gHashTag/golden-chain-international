#!/usr/bin/env python3
"""Every declared input must be read by something, or be listed as retained with a reason.

W-INTL-208 audited five declared rules by hand and found one - the selection fraction -
that the search model never read, though it imported the module the fraction lives in. An
import error can never say so, and a file that imports `inputs` and uses four things from
it looks correct at a glance.

Run over all of them, five more turned out to be read by nobody at all. Two were measured
areas that nothing used *and* nothing re-synthesised: the characterisation readout and the
two solver forms. Both are now verified.

The three that remain unread are retained deliberately, with reasons, because deleting
them would lose the provenance of a decision. That is a different thing from an oversight,
and the difference has to be written down or the next reader has to rediscover it.

This is the complement of check_input_coverage.py. That one asks whether perturbing an
input makes a check fail - whether the value matters. This one asks whether any file reads
the name at all. An input can pass one and fail the other: a constant read only by a model
whose output nothing checks matters to nobody, and a constant nothing reads cannot matter
to anything.

Exit code 1 if a declared input is neither read nor retained-with-a-reason.
"""

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = ROOT / "research" / "inputs.py"

# Declared, read by nothing, kept on purpose. The reason is the point of the entry.
RETAINED = {
    "RAW_BUDGET":
        "feeds only the vestigial cheapest() guard, kept for the utilisation check",
    "DEBIAS_OVERHEAD":
        "the published debiasing overheads; debiasing was ruled out when the leakage "
        "term went, and the table is the record of what was ruled out",
    "REUSABLE_DEBIASING_AVAILABLE":
        "records that the one reusable method is not constructible here, which is a "
        "finding rather than a parameter",
}


def main():
    src = TARGET.read_text()
    names = [n.targets[0].id for n in ast.parse(src).body
             if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)]
    if not names:
        print("FAIL: no declared inputs found, so this check read nothing",
              file=sys.stderr)
        return 1

    readers = {}
    for path in sorted(list((ROOT / "research").glob("*.py"))
                       + list((ROOT / "scripts").glob("*.py"))):
        if path.name == TARGET.name:
            continue
        text = path.read_text()
        for name in names:
            if f"I.{name}" in text:
                readers.setdefault(name, []).append(path.name)

    failures = []
    for name in names:
        if readers.get(name):
            continue
        if name in RETAINED:
            continue
        failures.append(f"{name} is declared and no file reads it; either use it or add "
                        f"it to RETAINED with the reason")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_inputs_are_read: {len(failures)} of {len(names)} declared inputs "
              f"are read by nothing")
        return 1
    print(f"check_inputs_are_read: OK ({len(names)} declared, "
          f"{len(names) - len(RETAINED)} read, {len(RETAINED)} retained with reasons)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
