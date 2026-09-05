#!/usr/bin/env python3
"""Every control must name the defect it replays.

W-INTL-248. W-INTL-247 recorded that a control replaying a real historical defect is worth
more than one invented to be large enough, because only the first says the check would have
caught the last bug of its kind. That was a lesson; this is the rule.

The repository has 140 closed findings and 57 controls. Twenty-three of the findings are
named anywhere in the workflow, and 39 of the controls name a finding near themselves. The
rest are mutations chosen to make something red, which proves the wiring and says nothing
about whether the check catches the thing it exists for.

The gap is not "117 findings are unprotected". Most closed findings are corrections to a
figure, and the sixty-nine bound figures catch those generically - that was tested rather
than assumed: restoring W-INTL-221's stale status page and W-INTL-225's wrong joint-sweep
cell both go red without any control naming them. What the gap means is narrower and worse:
for 18 controls nobody can say which defect they are the guard against, so nobody can say
whether they still guard it.

This check requires a control to name a finding within the eight lines above it, or to be
listed as generic with the reason. Generic is a real category - `control.py --self-test`
defends the harness rather than a finding - and it has to be claimed rather than defaulted
to.

Exit code 1 if a control neither cites a finding nor is listed.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "hard-rules.yml"
AUDIT = ROOT / "audits" / "gc_intl_v2_weakness_audit_addendum.md"
LOOKBACK = 8

# Controls that defend something other than a specific finding, by the text that identifies
# them. Each entry is the reason, and the reason is the point.
GENERIC = {
    "control.py --self-test":
        "defends the control harness itself - the stale-bytecode hazard of W-INTL-151 - "
        "rather than any finding about the design",
}


def controls():
    """(line number, command, whether a finding is named just above it)."""
    lines = WORKFLOW.read_text().splitlines()
    out = []
    for i, line in enumerate(lines):
        if "scripts/control.py" not in line or "python3" not in line:
            continue
        above = "\n".join(lines[max(0, i - LOOKBACK):i])
        named = re.findall(r"W-INTL-(\d+)", above)
        out.append((i + 1, line.strip(), named))
    return out


def recorded_findings():
    """Every finding the audit has a status row for, closed or not.

    Not only the closed ones. The first version of this check required a cited finding to
    be closed, and two controls guard findings the audit keeps open on purpose - W-INTL-166
    is a method finding about units, W-INTL-235 is open as a design question and closed as
    an omission. A control against an open finding is the useful kind: it is the guard that
    the thing stays fixed while the question stays open.
    """
    return {int(m.group(1)) for m in
            re.finditer(r"^\| W-INTL-(\d+) \|", AUDIT.read_text(), re.M)}


def main():
    found = controls()
    if not found:
        print("FAIL: no controls found in the workflow, so this check read nothing",
              file=sys.stderr)
        return 1

    recorded = recorded_findings()
    failures = []
    cited, generic = 0, 0
    named_findings = set()

    for line_no, command, names in found:
        if any(key in command for key in GENERIC):
            generic += 1
            continue
        if not names:
            failures.append(
                f"line {line_no}: this control names no finding within {LOOKBACK} lines "
                f"above it, so nobody can say which defect it guards against - cite the "
                f"W-INTL entry it replays, or add it to GENERIC with the reason")
            continue
        cited += 1
        named_findings.update(int(n) for n in names)

    for name, _ in GENERIC.items():
        if not any(name in command for _, command, _ in found):
            failures.append(f"GENERIC names {name!r}, which the workflow no longer runs")

    unknown = sorted(n for n in named_findings if n not in recorded)
    for n in unknown:
        failures.append(
            f"a control cites W-INTL-{n}, which the audit has no status row for")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_controls_cite_defects: {len(failures)} of {len(found)} controls "
              f"cannot say what they guard")
        return 1

    print(f"check_controls_cite_defects: OK ({cited} controls replay a named finding, "
          f"{generic} defend the harness, {len(named_findings)} distinct findings of "
          f"{len(recorded)} recorded have a control that replays them)")
    for name, why in sorted(GENERIC.items()):
        print(f"  generic: {name} - {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
