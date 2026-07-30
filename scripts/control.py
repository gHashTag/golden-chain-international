#!/usr/bin/env python3
"""Run a negative control: break something, prove the check notices, put it back.

Every check in this repository is supposed to have a control - a deliberate break that
makes it fail - because a check that has never failed is a check nobody has tested. Those
controls have been written by hand each time: mutate a file with a one-off script, run the
check, copy the backup back.

That has three failure modes, and the third one bit.

  The mutation might not apply     - a string replacement whose anchor is absent returns
                                     the input unchanged, which is W-INTL-149.
  The restore might not happen     - a control that resets or checks out can destroy
                                     untracked work, which is W-INTL-151.
  The mutation might be invisible  - and this is the one nobody would guess. Python's
                                     import cache is keyed on the source file's
                                     modification time and size. Swap a value for one of
                                     the same length within the same second and the
                                     interpreter reuses the cached bytecode, so the
                                     mutated run reads the *original* value. The control
                                     then reports that the check did not fire, and the
                                     honest conclusion from that - the check is broken -
                                     is wrong.

Demonstrated rather than asserted: research/../scripts/control.py --self-test reproduces
it, with an equal-length swap invisible and a different-length swap visible.

So controls run through here instead. The mutation is verified to have changed the file,
the check runs with bytecode caching disabled, the file is restored by content and the
restoration is verified by hash, and the exit status says whether the check fired.

Usage:
  control.py <file> <old> <new> -- <command...>
  control.py --self-test
"""

import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def self_test():
    """Reproduce the stale-cache hazard, so the reason for this file is not a claim."""
    d = pathlib.Path(tempfile.mkdtemp())
    mod = d / "probe_mod.py"
    results = []
    for label, orig, mutated in (("equal length", "0.65", "0.23"),
                                 ("different length", "0.65", "0.6500")):
        shutil.rmtree(d / "__pycache__", ignore_errors=True)
        mod.write_text(f'VALUE = "{orig}"\n')
        run = lambda: subprocess.run(
            [sys.executable, "-c",
             f"import sys;sys.path.insert(0,{str(d)!r});import probe_mod;"
             "print(probe_mod.VALUE)"],
            capture_output=True, text=True).stdout.strip()
        run()                                   # writes the cache
        backup = mod.read_bytes()
        mod.write_text(f'VALUE = "{mutated}"\n')
        during = run()
        mod.write_bytes(backup)
        results.append((label, mutated, during, during == mutated))
    print("stale bytecode cache, reproduced:")
    for label, mutated, during, saw in results:
        print(f"  {label:18s} mutated to {mutated:8s} the run saw "
              f"{during:8s} -> {'mutation visible' if saw else 'MUTATION INVISIBLE'}")
    print("  the invisible case is why a control must disable bytecode caching")
    return 0 if not results[0][3] else 1        # the equal-length case must be invisible


def main():
    if "--self-test" in sys.argv:
        return self_test()

    if "--" not in sys.argv or len(sys.argv) < 6:
        print(__doc__.strip().splitlines()[-3])
        return 2
    split = sys.argv.index("--")
    path, old, new = sys.argv[1:split]
    command = sys.argv[split + 1:]

    target = pathlib.Path(path)
    before = target.read_text()
    if old not in before:
        print(f"FAIL: the control's anchor is not in {path}, so nothing would be broken")
        return 1
    before_hash = digest(target)

    target.write_text(before.replace(old, new, 1))
    if digest(target) == before_hash:
        print(f"FAIL: the mutation left {path} unchanged")
        return 1

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(command, capture_output=True, text=True, env=env)

    target.write_text(before)
    if digest(target) != before_hash:
        print(f"FAIL: {path} was not restored; its contents differ from the original")
        return 1

    fired = result.returncode != 0
    head = (result.stdout or result.stderr or "").strip().splitlines()
    print(f"control on {path}: {'the check FIRED' if fired else 'the check DID NOT fire'}")
    if head:
        print(f"  {head[0]}")
    return 0 if fired else 1


if __name__ == "__main__":
    sys.exit(main())
