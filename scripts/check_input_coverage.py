#!/usr/bin/env python3
"""Perturb every declared input and fail if any check would not notice.

W-INTL-192 found the enrolment read count could be set to one with twenty-two bound
figures in place and nothing firing. This runs that experiment over every scalar in
research/inputs.py: multiply it by 1.5, run the checks, put it back.

What it found on its first run was worse than a blind input. TARGET_FAILURE - the word
error probability the whole error-correction design exists to meet - was declared here
and read by one file that is not in the recommendation path; every other site wrote 1e-6
as a literal. And the tolerated bit error rate was written as 0.0442 in three files,
which is not an input at all but a consequence of the code, and belonged to the code that
was superseded four loops earlier. The recommendation tolerates 0.0143.

An input nothing reads is not an input. This makes that a failure rather than a
discovery.

Exit code 1 if any input can move without a check noticing. ALLOWED names an input that
is deliberately unread, with the reason.
"""
import ast, os, pathlib, shutil, signal, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = ROOT/'research'/'inputs.py'
src = TARGET.read_text(); tree = ast.parse(src)
backup = src
MARKER = ROOT/'research'/'.inputs-perturbed'
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

# Which checks read research/inputs.py. Derived from the glob and narrowed here with the
# reason for each exclusion, rather than enumerated: the enumeration said two checks when
# there were three, and five more have been added since without anyone touching it.
# W-INTL-217 - the rule from W-INTL-216, applied to the file that motivated it.
_SKIP = {
    "check_input_coverage.py": "this file",
    "check_consistency.py": "reads documents, not inputs",
    "check_catalog.py": "reads a catalog in another repository",
    "check_commit_claims.py": "reads a commit message",
    "check_control_anchors.py": "reads the workflow",
    "check_generated_rtl.py": "reads generated Verilog against its generator",
    "check_models_run.py": "four minutes a pass. Its stated second reason - that its "
                           "figures reach inputs through check_figures_reproduce anyway - "
                           "was false for one interval, when the two temperature inputs "
                           "reached only this file and the sweep reported both as read by "
                           "nothing. They are bound in a document now, which is what makes "
                           "the exclusion true again rather than merely convenient. "
                           "W-INTL-235",
}
CHECKS = sorted(c for c in (ROOT / "scripts").glob("check_*.py")
                if c.name not in _SKIP)


def run():
    outs = []
    for path in CHECKS:
        r = subprocess.run([sys.executable, str(path)],
                           capture_output=True, text=True, env=env)
        outs.append((path.name, r.returncode))
    return outs

# RAW_BUDGET feeds only the vestigial cheapest() guard, which is kept for the utilisation
# check and is no longer the source of any recommended figure. Declared so the guard keeps
# its provenance; perturbing it legitimately changes nothing.
ALLOWED = {"RAW_BUDGET"}

# The driver runs under a main guard: a module that computes on import cannot be
# cross-checked against, which this project recorded in W-INTL-169 and this file has
# been violating since it was written. Importing it to read CHECKS ran the whole
# sweep.
def _restore(*_):
    """Put research/inputs.py back, whatever ends this process.

    W-INTL-226. This check perturbs the file in place and restores it a few lines later,
    which is correct while it runs to completion and wrong in every other case. Killed
    between those two writes it leaves a falsified constant on disk - and a commit taken
    while it runs captures one. Both happened: a commit went out with TILE_AREA at a
    quarter and INVERTERS_PER_OSCILLATOR at one seventh, and the interrupt left a third
    input perturbed. CI caught it, at thirteen tiles instead of 3.44.

    A handler cannot cover SIGKILL, so the marker file below is what a green run must not
    leave behind: it is the durable half of this, and the handler is the tidy half.
    """
    TARGET.write_text(backup)
    MARKER.unlink(missing_ok=True)
    raise SystemExit(130)


def main():
    if MARKER.exists():
        print(f"FAIL: {MARKER.name} is present, so a previous run of this check did not "
              f"finish and research/inputs.py may hold a perturbed value; restore it "
              f"from git and delete the marker", file=sys.stderr)
        return 1
    MARKER.write_text("research/inputs.py is being perturbed by check_input_coverage\n")
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, _restore)
    try:
        return _sweep()
    finally:
        TARGET.write_text(backup)
        MARKER.unlink(missing_ok=True)


def _sweep():
    results = []
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        seg = ast.get_source_segment(src, node.value)
        if seg is None: continue
        try:
            val = ast.literal_eval(seg)
        except Exception:
            try:
                val = eval(seg, {"__builtins__":{}}, {})
            except Exception:
                continue
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            continue
        line = f"{name} = {seg}"
        if line not in src:
            continue
        # Both directions, and a large factor. A half-step perturbation can land inside a
        # figure's tolerance and report a covered input as blind: the question is whether a
        # check is sensitive to the input at all, not whether it resolves small changes.
        fired = []
        for factor in (0.25, 4):
            if fired:
                break                     # one direction is enough to show sensitivity
            cand = val * factor
            if isinstance(val, int) and not isinstance(val, bool):
                cand = max(1, int(round(cand)))
            TARGET.write_text(src.replace(line, f"{name} = {cand:.10g}", 1))
            outs = run()
            TARGET.write_text(backup)
            fired += [n for n, rc in outs if rc != 0]
        results.append((name, val, sorted(set(fired))))

    blind = [n for n, _, f in results if not f and n not in ALLOWED]
    print(f"{'input':28s} {'value':>14}  caught by")
    for name, val, fired in results:
        mark = ", ".join(fired) if fired else ("unread, allowed" if name in ALLOWED
                                               else "*** NOTHING ***")
        print(f"{name:28s} {val:14.6g}  {mark}")
    if blind:
        print(f"\ncheck_input_coverage: {len(blind)} input(s) no check notices: "
              f"{', '.join(blind)}")
        return 1
    print(f"\ncheck_input_coverage: OK ({len(results)} inputs, "
          f"{len(results) - len(ALLOWED)} covered, {len(ALLOWED)} deliberately unread)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
