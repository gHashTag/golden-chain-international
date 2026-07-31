#!/usr/bin/env python3
"""Every control in the workflow must still find the text it breaks.

A control mutates a specific string in a specific file. When that string changes - and in
this project a bound figure changes most loops - the control stops pointing at anything.
The harness refuses to run in that case rather than silently testing nothing, which is
correct and arrives one CI round per stale anchor, five minutes each.

This finds them all at once, before pushing. It has been run by hand before each of the
last two pushes, which is exactly the kind of habit W-INTL-157 says to hand to a machine.

It does not run the controls. It only asks whether each one would find its anchor, which
is cheap enough to sit in the fast job.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "hard-rules.yml"

# control.py <file> <old> <new> -- <command...>, wrapped across lines by the YAML.
PATTERN = re.compile(
    r"scripts/control\.py\s+\\?\s*\n?\s*(\S+)\s+\\?\s*\n?\s*'([^']*)'")


def main():
    if not WORKFLOW.exists():
        print(f"FAIL: no workflow at {WORKFLOW}", file=sys.stderr)
        return 1
    text = WORKFLOW.read_text()

    checked = 0
    failures = []
    for match in PATTERN.finditer(text):
        path, anchor = match.group(1), match.group(2)
        # Paths built at run time - a fetched catalog, a shell variable - cannot be
        # checked from here, and saying so is better than skipping them silently.
        if path.startswith(("/tmp", "$", "\"")):
            continue
        checked += 1
        target = ROOT / path
        if not target.exists():
            failures.append(f"control names {path}, which does not exist")
            continue
        if anchor and anchor not in target.read_text():
            failures.append(f"control anchor not found in {path}: {anchor!r}")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_control_anchors: {len(failures)} of {checked} controls point at "
              f"nothing")
        return 1
    if checked == 0:
        print("FAIL: no controls found in the workflow, so this check read nothing")
        return 1
    print(f"check_control_anchors: OK ({checked} controls, each still finds its anchor)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
