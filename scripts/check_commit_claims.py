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

Usage:  check_commit_claims.py [range] [--require-commits]
Default range is the merge base with origin/main to HEAD, so it covers a branch rather
than one commit. --require-commits turns an empty range into a failure, which is what CI
passes: a range that collapses to nothing must not report success.
Exit code 1 on any claim the diff does not support.
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
    argv = list(sys.argv[1:])
    if "--message-file" in argv:
        i = argv.index("--message-file")
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    rng = args[0] if args else default_range()

    # --message-file substitutes the commit message while leaving the diff alone. It
    # exists so this check can have a control: the message is the only input, and there
    # is no way to mutate it with a file edit. W-INTL-179.
    override = None
    if "--message-file" in sys.argv:
        override = pathlib.Path(sys.argv[sys.argv.index("--message-file") + 1]).read_text()
    messages = override if override is not None else git("log", "--format=%B", rng)
    if not messages.strip():
        # In CI this used to print "nothing to check" and exit zero. The workflow ran a
        # shallow checkout of a merge commit, the merge base was unreachable, the range
        # collapsed to nothing, and the step passed green having read no message at all -
        # the failure mode this file's own docstring warns about, found by reading the
        # log rather than the status dot. Under --require-commits an empty range fails.
        if "--require-commits" in sys.argv:
            print(f"FAIL: no commits in {rng}; the range is empty, so nothing was "
                  f"checked and this step would have passed without reading a message")
            return 1
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
