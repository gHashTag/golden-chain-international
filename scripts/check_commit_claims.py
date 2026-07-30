#!/usr/bin/env python3
"""A commit message must not name an audit entry its diff never mentions.

Written after W-INTL-149. Two consecutive loops added rows to the audit's status table
with a string replacement whose anchor was not in the file. Python's str.replace returns
the string unchanged when it finds nothing, so both edits reported success, both commit
messages described the rows, and neither row existed.

The three checks this repository already runs compare documents against each other and
against the model. None of them compares a claim against the change that is supposed to
have made it true.

**This check would not have caught W-INTL-149.** Run against the two commits that lost
their status rows it passes both: the audit *entries* landed and only the *table rows*
did not, so the numbers do appear in the diff. That was found by running it against the
historical case before trusting it, and it is why the actual fix for W-INTL-149 is
elsewhere - the check that did detect the loss reported it as a note, and notes get read
as furniture, so those notes are now failures.

A second arm was written and cut. Matching file paths in the message against changed
files needed a list of verbs to tell "I changed X" from "X is where this lives", and a
verb list is a heuristic that reports coverage it does not have; in a verification tool
that is worse than an absent check. What survives is the narrow thing with a passing
control: a commit claiming an audit entry that nothing in the diff mentions.

Usage:  check_commit_claims.py [range]
Default range is the merge base with origin/main to HEAD, so it covers a branch rather
than one commit. Exit code 1 on any claim the diff does not support.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def git(*args):
    out = subprocess.run(["git", "-C", str(ROOT), *args],
                         capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else ""


def default_range():
    for base in ("origin/main", "main"):
        merge_base = git("merge-base", base, "HEAD").strip()
        if merge_base:
            head = git("rev-parse", "HEAD").strip()
            if merge_base != head:
                return f"{merge_base}..HEAD"
    return "HEAD~1..HEAD"


def main():
    rng = sys.argv[1] if len(sys.argv) > 1 else default_range()

    messages = git("log", "--format=%B", rng)
    if not messages.strip():
        print(f"check_commit_claims: no commits in {rng}, nothing to check")
        return 0

    diff = git("diff", "--unified=0", rng)
    added = "\n".join(l for l in diff.splitlines() if l.startswith("+"))

    failures = []
    # Entries are also referred to in passing - "the same shape as W-INTL-99" - so this
    # would over-fire if it demanded every mention be new. It demands the number appear
    # somewhere in the added lines, which a reference in a document satisfies and a
    # claim that vanished does not.
    for num in sorted(set(re.findall(r"W-INTL-(\d+)", messages)), key=int):
        if f"W-INTL-{num}" not in added:
            failures.append(
                f"the message names W-INTL-{num} and no added line mentions it")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_commit_claims: {len(failures)} claim(s) the diff does not "
              f"support")
        return 1
    print(f"check_commit_claims: OK ({rng})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
