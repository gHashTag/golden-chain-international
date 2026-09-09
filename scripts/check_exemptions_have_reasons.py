#!/usr/bin/env python3
"""Every exemption must carry a reason, and the reason must say something.

W-INTL-249, found because a control was wrong. Restoring W-INTL-217's defect - an exclusion
kept without a reason - the mutation removed the exclusion entirely instead, and the check
passed. That was the control being wrong rather than the check being weak, which is the
third time in three loops that a control perturbed the computation instead of breaking the
claim. Writing the right mutation raised the real question: does anything require an
exclusion's reason to exist?

Nothing did. Nine exemption registries across eight checks, every one carrying reasons by
convention, and an empty string would have passed all of them. Several checks print "with
reasons" in their OK line, which is a claim nobody was verifying.

And one registry is a set rather than a mapping - `ALLOWED` in check_input_coverage, whose
single entry keeps its reason in a comment above the declaration. A comment is where a
reason goes to stop being checkable, which is the finding this project has made about
prose next to code four times.

Discovered by walking the syntax rather than listed, because W-INTL-243 and W-INTL-244 are
what a list does. Any module-level dict or set whose name is an exemption name is a
registry; a dict entry must map to a non-empty string of some substance, and a set is
reported as carrying no reasons at all.

Exit code 1 on an exemption without a reason.
"""

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
RESEARCH = ROOT / "research"

# Names that mean "these are the ones we are not checking, and here is why".
REGISTRY_NAMES = {
    "_SKIP", "EXEMPT", "RETAINED", "UNPINNED", "NOT_REVERIFIABLE", "GENERIC",
    "ALLOWED", "HEAVY", "WAIVED", "SINGLE",
}

# A reason shorter than this is a label rather than an explanation.
MINIMUM = 24


def registries():
    """(file, name, entries, is_mapping) for every exemption registry."""
    out = []
    for path in sorted(list(SCRIPTS.glob("*.py")) + list(RESEARCH.glob("*.py"))):
        if path.name == pathlib.Path(__file__).name:
            continue
        for node in ast.parse(path.read_text()).body:
            if not (isinstance(node, ast.Assign)
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id in REGISTRY_NAMES):
                continue
            value = node.value
            if isinstance(value, ast.Dict):
                pairs = []
                for key, val in zip(value.keys, value.values):
                    label = ast.unparse(key) if key is not None else "?"
                    text = val.value if isinstance(val, ast.Constant) and \
                        isinstance(val.value, str) else None
                    if text is None and isinstance(val, ast.BinOp):
                        try:
                            text = ast.literal_eval(val)
                        except Exception:
                            text = None
                    if text is None and isinstance(val, ast.JoinedStr):
                        text = "".join(v.value for v in val.values
                                       if isinstance(v, ast.Constant))
                    pairs.append((label, text))
                out.append((path.name, node.targets[0].id, pairs, True))
            elif isinstance(value, ast.Set):
                labels = [(ast.unparse(e), None) for e in value.elts]
                out.append((path.name, node.targets[0].id, labels, False))
    return out


def main():
    found = registries()
    if not found:
        print("FAIL: no exemption registries found, so this check read nothing",
              file=sys.stderr)
        return 1

    failures = []
    entries = 0
    for filename, name, pairs, is_mapping in found:
        if not is_mapping:
            failures.append(
                f"{filename}: {name} is a set, so its {len(pairs)} entries carry no "
                f"reason where the check can see one - make it a mapping from the entry "
                f"to why it is exempt")
            continue
        for label, text in pairs:
            entries += 1
            if text is None:
                failures.append(f"{filename}: {name}[{label}] has no literal reason")
            elif len(text.strip()) < MINIMUM:
                failures.append(
                    f"{filename}: {name}[{label}] gives {len(text.strip())} characters "
                    f"of reason - under {MINIMUM} that is a label, not an explanation")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_exemptions_have_reasons: {len(failures)} exemptions cannot say "
              f"why they are exempt")
        return 1

    print(f"check_exemptions_have_reasons: OK ({len(found)} registries, {entries} "
          f"exemptions, each with at least {MINIMUM} characters of reason)")
    for filename, name, pairs, _ in found:
        print(f"  {filename}: {name}, {len(pairs)} exempt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
