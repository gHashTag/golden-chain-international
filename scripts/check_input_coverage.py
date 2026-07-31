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
import ast, os, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path('.')
TARGET = ROOT/'research'/'inputs.py'
src = TARGET.read_text(); tree = ast.parse(src)
backup = src
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

def run():
    # check_figures_reproduce re-derives the recommendation, which is the expensive part.
    # Nine minutes of CI for seventeen inputs is a check people wait for; -O keeps the
    # interpreter from writing bytecode we then have to invalidate, and the two checks are
    # the only ones that read inputs at all.
    outs = []
    # check_consistency reads documents rather than inputs, so it is not in this loop -
    # including it tripled the run time and could never fire.
    for cmd in (["python3","scripts/check_figures_reproduce.py"],
                ["python3","scripts/check_units.py"]):
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        outs.append((cmd[1].split('/')[-1], r.returncode))
    return outs

# RAW_BUDGET feeds only the vestigial cheapest() guard, which is kept for the utilisation
# check and is no longer the source of any recommended figure. Declared so the guard keeps
# its provenance; perturbing it legitimately changes nothing.
ALLOWED = {"RAW_BUDGET"}

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
    sys.exit(1)
print(f"\ncheck_input_coverage: OK ({len(results)} inputs, "
      f"{len(results) - len(ALLOWED)} covered, {len(ALLOWED)} deliberately unread)")
