#!/usr/bin/env python3
"""No model may write down a figure the recommendation determines.

W-INTL-228 landed a design change and four models turned out to be pinned to the
construction it replaced: aging_margin's `blocks=3` default, burn_in's third copy of the
same bisection, pointer_vs_linear's `BLOCKS = 3`, borrowed_margins' `K_TOTAL = 57 * 3`.
All four were correct when written. All four were found by hand, one at a time, after
something else failed - and the count is four because that is how many turned up before
the loop ended, not because the search was exhaustive.

That was recorded as a rule in the skill file. A rule in a skill file is a thing a reader
has to remember; this is the same rule as a check.

Two passes, because they fail differently:

  by value  a literal equal to a distinctive determined figure - 935 raw positions, 44
            oscillators, 3.46 tiles. Precise when the figure is distinctive and useless
            when it is round: eight literal 200s in this repository are all loop counts,
            and 200 is what the key needs in k. Round figures are therefore skipped, and
            printed on every run so the gap stays visible rather than becoming a silence.

  by name   an assignment or default argument called `blocks`, `K_TOTAL` and the like
            bound to a plain number. This one does not care whether the value is currently
            right - a block count that is a literal is stale the next time the design
            moves, which is the whole finding.

Exit code 1 on any hit. WAIVED names a site that is deliberately a literal, with the
reason, because an exemption nobody can see is a gap nobody knows about.
"""

import ast
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS = ROOT / "research"

# Stems, not an enumeration. The exact-name version missed RECOMMENDED_BLOCKS on its own
# control, which is the failure mode an enumeration always has: it covers the names its
# author happened to think of, and a stale literal is written by whoever did not.
DETERMINED_STEMS = (
    "blocks", "k_total", "raw_position", "oscillator", "selected_bit", "need_k",
)


def names_a_determined_figure(name):
    return any(stem in name.lower() for stem in DETERMINED_STEMS)

# Deliberate literals, with the reason. (file, line-bearing name) -> why.
WAIVED = {
    ("check_no_stale_literals.py", "blocks"):
        "this file's own documentation of the rule",
}


def determined_figures():
    """What the recommendation currently fixes, recomputed rather than listed."""
    sys.path.insert(0, str(MODELS))
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_figures_reproduce as C
    import inputs as I

    rec = C.recommendation()
    if rec is None:
        return None
    tiles, n, k, t, blocks, raw, osc, _ = rec
    return {
        "block count": blocks,
        "k carried": k * blocks,
        "raw positions": raw,
        "selected positions": n * blocks,
        "oscillators": osc,
        "tiles": round(tiles, 2),
        "tolerated bit error rate": round(C.tolerated_ber(), 6),
        "after-selection density floor": round(I.KEY_BITS / (k * blocks), 4),
    }


def is_round(value):
    """Too common a number to match on. Integers under 20, and multiples of 50."""
    if isinstance(value, float):
        return False
    return value < 20 or value % 50 == 0


def _number(node):
    """The numeric value of a constant node, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return node.value
    return None


def literal_names(tree):
    """(name, lineno, value) for every assignment or default argument bound to a number.

    Tuple targets are unpacked, and that is not a refinement. The defect this check exists
    for was written `M, RED, T, K_BITS = 7, 0x09, 21, 29` - a tuple - and the first version
    of this file handled only single names, so its own negative control did not fire. A
    check written from a memory of a bug rather than from the bug catches the memory.

    Returns are not covered: a function whose body is `return 3` states a determined figure
    just as plainly and is not seen here. That is a known gap, printed on every run.
    """
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    value = _number(node.value)
                    if value is not None:
                        out.append((target.id, node.lineno, value))
                elif isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple) \
                        and len(target.elts) == len(node.value.elts):
                    for name_node, value_node in zip(target.elts, node.value.elts):
                        value = _number(value_node)
                        if isinstance(name_node, ast.Name) and value is not None:
                            out.append((name_node.id, node.lineno, value))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            positional = args.posonlyargs + args.args
            for arg, default in zip(positional[len(positional) - len(args.defaults):],
                                    args.defaults):
                if isinstance(default, ast.Constant) \
                        and isinstance(default.value, (int, float)) \
                        and not isinstance(default.value, bool):
                    out.append((arg.arg, node.lineno, default.value))
            for arg, default in zip(args.kwonlyargs, args.kw_defaults):
                if isinstance(default, ast.Constant) \
                        and isinstance(default.value, (int, float)) \
                        and not isinstance(default.value, bool):
                    out.append((arg.arg, node.lineno, default.value))
    return out


def main():
    figures = determined_figures()
    if figures is None:
        print("FAIL: no recommendation, so this check has nothing to compare against")
        return 1

    watched = {name: value for name, value in figures.items() if not is_round(value)}
    skipped = {name: value for name, value in figures.items() if is_round(value)}

    failures = []
    scanned = 0
    for path in sorted(MODELS.glob("*.py")):
        # inputs.py is the declaration file. Every literal in it is an input by
        # definition, with its provenance in the comment above it, and that is the
        # opposite of a figure the recommendation determines. The stem match caught
        # INVERTERS_PER_OSCILLATOR there on its first run, which is what a rule aimed at
        # derived quantities does when pointed at declared ones.
        if path.name == "inputs.py":
            continue
        tree = ast.parse(path.read_text())
        scanned += 1

        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant)
                    and isinstance(node.value, (int, float))
                    and not isinstance(node.value, bool)):
                continue
            for label, value in watched.items():
                same = (abs(node.value - value) < 1e-9 if isinstance(value, float)
                        else node.value == value)
                if same:
                    failures.append(
                        f"{path.name}:{node.lineno} writes {node.value:g}, which is the "
                        f"{label} the recommendation determines - compute it")

        for name, lineno, value in literal_names(tree):
            if not names_a_determined_figure(name):
                continue
            if (path.name, name) in WAIVED:
                continue
            failures.append(
                f"{path.name}:{lineno} binds {name} to the literal {value:g}; the "
                f"recommendation fixes it, so it is stale the next time the design moves")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_no_stale_literals: {len(failures)} site(s) in {scanned} models")
        return 1
    if scanned == 0:
        print("FAIL: no models scanned, so this check read nothing")
        return 1
    skip_note = ", ".join(f"{n} ({v:g})" for n, v in sorted(skipped.items()))
    print(f"check_no_stale_literals: OK ({scanned} models, {len(watched)} figures "
          f"matched by value, {len(DETERMINED_STEMS)} name stems matched)")
    print(f"  not matched by value, too round to distinguish from a loop count: "
          f"{skip_note}")
    print("  not covered: a determined figure returned directly (`return 3`) rather than "
          "bound to a name")
    return 0


if __name__ == "__main__":
    sys.exit(main())
