#!/usr/bin/env python3
"""Restore a past defect and report which check, if any, notices.

W-INTL-250. W-INTL-248 asked how many controls name the defect they replay and found
eighteen that named none. This asks the other half: of the findings with NO control, how
many would a check catch anyway - and which check.

That question was answered three times by hand in the last loop, and the third attempt was
wrong in a way that produced W-INTL-249. Doing it by hand does not scale to 215 findings
and does not remember its results. This does both.

Each entry is a finding, the file and the substitution that restores its defect, and what
was expected. Running it mutates, runs every fast check, restores, and reports the first
check that goes red. The mutation goes through `scripts/control.py`, so the restore is
verified by hash and an ambiguous anchor is refused - both of which this project needed.

What it is not: a substitute for controls in CI. A control names one defect and one check
and runs on every push. This is a survey, run when someone wants to know where the generic
bindings do not reach, and its value is the table it prints rather than its exit code.

Usage: replay_defects.py            replay every entry
       replay_defects.py 221 225    replay these findings only
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Checks fast enough to run once per replay. check_input_coverage and a full
# check_models_run are excluded: forty-five minutes and twenty apiece, and both are
# themselves exercised by controls in CI.
FAST = [
    "check_figures_reproduce.py", "check_consistency.py", "check_status_current.py",
    "check_no_stale_literals.py", "check_module_hygiene.py", "check_inputs_are_read.py",
    "check_areas_reverifiable.py", "check_control_anchors.py",
    "check_controls_cite_defects.py", "check_exemptions_have_reasons.py",
    "check_generated_rtl.py", "check_testbench_coverage.py",
]

# (finding, file, text to replace, replacement, one line on what the defect was)
DEFECTS = [
    (99, "paper/evidence_ledger.md", "decoder 24,659,", "decoder 24,700,",
     "a measured area stated in a document and not in the model"),
    (144, "research/decoder_code_choice.md",
     "density after selection is 0.5889", "density after selection is 0.9500",
     "the density after selection stated as the density before it"),
    (177, "research/inputs.py", "SLLC_AREA = {", "SLLC_AREA = {  # noqa\n    0: 9_999,",
     "the masking stage sized to a code other than its own"),
    (221, "STATUS.md", "# Status", "# Status (edited)",
     "the generated status page edited by hand"),
    (225, "research/decoder_code_choice.md", "| 0.7000 | 65%", "| 0.7000 | 60%",
     "a joint-sweep cell asserting the wrong feasibility"),
    (231, "research/inputs.py", "MIN_ENTROPY_BITS = 183.3", "MIN_ENTROPY_BITS = 241.0",
     "a Shannon entropy declared under the min-entropy name"),
    (233, "research/borrowed_margins.py", "K_TOTAL = _k_total()", "K_TOTAL = 228",
     "a determined figure written down rather than derived"),
    (239, "research/inputs.py", "SELECTION_LOSS = 1 - 381 / 701",
     "SELECTION_LOSS = 1 - 381 / 900",
     "a declared input moving without the documents following"),
    (249, "scripts/check_quadrature_converged.py",
     '        "the primitive threshold_for bisects over, exercised through it",',
     '        "x",',
     "an exemption whose reason is a label rather than an explanation"),
]


def replay(finding, path, old, new):
    """Every check that notices this defect, in the order they were tried.

    All of them, not the first. W-INTL-250: the first firing check is not necessarily the
    one that owns the defect - restoring W-INTL-249's mutation trips check_control_anchors,
    because a CI control anchors on the very text being mutated, and reporting only that
    would credit the wrong guard and hide whether the owning check works at all.
    """
    caught = []
    for check in FAST:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "control.py"), path, old, new,
             "--", sys.executable, str(ROOT / "scripts" / check)],
            capture_output=True, text=True, cwd=ROOT)
        if "the check FIRED" in result.stdout:
            caught.append(check.replace("check_", "").replace(".py", ""))
        elif "ambiguous" in result.stdout or "ambiguous" in result.stderr:
            return ["ANCHOR AMBIGUOUS"]
    return caught


def main():
    wanted = {int(a) for a in sys.argv[1:] if a.isdigit()}
    rows = [d for d in DEFECTS if not wanted or d[0] in wanted]
    print(f"Replaying {len(rows)} past defects against {len(FAST)} fast checks.\n")
    print(f"{'finding':>8}  {'caught by':38}  what the defect was")
    uncaught = []
    for finding, path, old, new, what in rows:
        caught = replay(finding, path, old, new)
        label = ", ".join(caught) if caught else "*** NOTHING ***"
        print(f"W-INTL-{finding:<3}  {label:38}  {what}")
        if not caught:
            uncaught.append((finding, what))

    print(f"\n{len(rows) - len(uncaught)} of {len(rows)} caught by a fast check.")
    for finding, what in uncaught:
        print(f"  uncaught: W-INTL-{finding} - {what}")
    return 1 if uncaught else 0


if __name__ == "__main__":
    sys.exit(main())
