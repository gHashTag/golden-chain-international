#!/usr/bin/env python3
"""No analysis module may run its demonstration on import.

W-INTL-169: a module that computes on import cannot be cross-checked against, because
anything wanting to call one function in it has to run the whole program first. It was
recorded from one model, fixed there, and two more files kept doing it - the coverage
sweep, found in W-INTL-217, and the SLLC generator, found here by running the rule across
everything rather than waiting for it to bite.

Definitions at module level are fine: constants, tables, function bodies. What is not fine
is output and loops that produce it. The test is whether importing the module prints
anything or takes measurable time, which is approximated statically: a top-level call or
loop after the definitions, other than the small setup this project uses to put research/
on the path.

Exit code 1 if any module would compute on import.
"""

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETUP = ("sys.path.insert", "sys.path.append")


def offending(path):
    tree = ast.parse(path.read_text())
    src = path.read_text()
    out = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef,
                             ast.Assign, ast.AnnAssign)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue                                  # a docstring
        if isinstance(node, ast.If):
            test = ast.get_source_segment(src, node.test) or ""
            if "__main__" in test:
                continue
        seg = (ast.get_source_segment(src, node) or "").strip()
        if any(s in seg for s in SETUP):
            continue
        # A top-level loop that builds a lookup table is a definition, not a
        # demonstration, and the property that matters is that importing is silent. So
        # the test is output, not shape: a table build stays, a printing loop does not.
        # The first version of this check flagged a two-line power table and would have
        # taught its reader to add exemptions rather than fix anything.
        if "print(" not in seg and not isinstance(node, ast.Expr):
            continue
        out.append(f"line {node.lineno}: {seg.splitlines()[0][:60]}")
    return out


def main():
    files = sorted(list((ROOT / "research").glob("*.py"))
                   + list((ROOT / "scripts").glob("*.py")))
    if not files:
        print("FAIL: no modules found, so this check read nothing", file=sys.stderr)
        return 1
    failures = []
    for path in files:
        bad = offending(path)
        if bad:
            failures.append(f"{path.name} computes on import: {bad[0]}")
    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_module_hygiene: {len(failures)} of {len(files)} modules compute "
              f"on import")
        return 1
    print(f"check_module_hygiene: OK ({len(files)} modules, none computes on import)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
