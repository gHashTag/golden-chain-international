#!/usr/bin/env python3
"""STATUS.md must match what its generator produces.

A hand-written status page is a claim about the repository that nothing checks, and this
project has found six of those. This one is generated; this check makes it stay that way.

Exit code 1 if the file on disk differs from scripts/gen_status.py's output.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATUS = ROOT / "STATUS.md"


def main():
    if not STATUS.exists():
        print("FAIL: STATUS.md does not exist; run scripts/gen_status.py",
              file=sys.stderr)
        return 1
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "gen_status.py"),
                             "--stdout"], capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        print("FAIL: the status generator failed", file=sys.stderr)
        return 1
    if result.stdout != STATUS.read_text():
        print("FAIL: STATUS.md differs from what scripts/gen_status.py produces; "
              "run it")
        return 1
    print(f"check_status_current: OK ({len(result.stdout.splitlines())} lines, "
          f"matching the generator)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
