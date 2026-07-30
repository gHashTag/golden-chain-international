#!/usr/bin/env python3
"""Validate the numeric format catalog against its own rules.

The catalog in gHashTag/t27 at specs/numeric/formats_catalog.t27 is the single
source of truth that every other document defers to. Two defects were found in it
by hand on 2026-07-30, and both are mechanical:

  W-INTL-42  Retracted. Two entries were reported as carrying a bias of 2. They
             carry 2^194-1 and 2^390-1, written as expressions because the values
             exceed a 64-bit integer, exactly as a published erratum said the
             repaired generator would write them. The hand check that reported
             otherwise read the value with a digits-only pattern and kept the
             leading 2. This script parses the expression form, so the same
             mistake cannot be made here.

  W-INTL-41  An entry marked verified asserts an FPGA frequency in a metadata
             field and cites an archive that contains no hardware data at all.

This script encodes the checks that would have caught them, plus the counts every
external document quotes.

Usage:
    python3 scripts/check_catalog.py [path-to-formats_catalog.t27]

With no argument it tries to fetch the catalog with the GitHub CLI. If neither a
path nor the CLI is available it skips rather than failing, so it can sit in CI
without making the build depend on another repository being reachable.
"""

import collections
import pathlib
import re
import shlex
import subprocess
import sys

DEFAULT_REPO = "gHashTag/t27"
DEFAULT_PATH = "specs/numeric/formats_catalog.t27"

EXPECTED_FORMATS = 83

# The metadata-measurement check observes an artefact in another repository, which this
# project cannot edit. That is a real reason for a note rather than a failure - and a note
# nobody counts is the pattern this project has now promoted away four times. So the
# number of outstanding observations is declared instead: the check passes while it
# matches and fails when it moves, which is the part that needs a human either way.
EXPECTED_METADATA_OBSERVATIONS = 1
EXPECTED_CLUSTERS = 13

# A metadata field is for identifying a format, not for reporting a measurement.
# Anything matching this in the standard field is a result that belongs in a
# document with an artefact behind it.
MEASUREMENT_IN_METADATA = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:MHz|GHz|ns|ps|LUTs?|DSPs?|W)\b|\b\d+\s*/\s*\d+\b",
    re.I,
)

failures: list[str] = []
notes: list[str] = []


def load(argv):
    if len(argv) > 1:
        # An unreadable path used to raise, and a traceback is not a diagnosis. It is
        # also the difference between "the catalog says something wrong" and "you gave
        # me a path that is not there", which are different problems for the reader.
        try:
            return pathlib.Path(argv[1]).read_text()
        except OSError as exc:
            print(f"FAIL: cannot read the catalog at {argv[1]}: {exc}", file=sys.stderr)
            sys.exit(1)
    cmd = f"gh api repos/{DEFAULT_REPO}/contents/{DEFAULT_PATH} --jq .content"
    try:
        out = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    import base64
    return base64.b64decode(out.stdout).decode("utf-8", "replace")


def parse(text):
    entries = []
    for line in text.splitlines():
        if "// CATALOG:" not in line:
            continue
        fields = dict(re.findall(r'(\w+)=("[^"]*"|\S+)', line.split("// CATALOG:", 1)[1]))
        entries.append({k: v.strip('"') for k, v in fields.items()})
    return entries


# The binary-float field rule - bias equals 2^(e-1)-1, width equals s+e+m - holds
# only for clusters that actually use a fixed binary layout with an IEEE-style
# bias. It is applied by whitelist rather than by exception, because a first
# version of this file worked by exception and flagged thirty-six correct entries:
# VAX excess-128 biases, Cray's own bias, tapered posits and takums whose widths
# vary with the value, IEEE decimal formats which use a different bias
# convention entirely, composite double-double rows with no single bias, and
# logarithmic number systems which have no bias in the floating-point sense.
#
# Every one of those was the checker being wrong about the format, not the
# catalog being wrong about itself. A rule applied outside its domain produces
# noise, and noise trains a reader to ignore the checker.
FIXED_LAYOUT_CLUSTERS = {
    "Ieee754Binary",
    "GoldenFloat",
    "MlLowPrecision",
    "Microscaling",
}


def uses_fixed_fields(e):
    if e.get("cluster") not in FIXED_LAYOUT_CLUSTERS:
        return False
    try:
        return int(e.get("bits", 0)) > 0 and int(e.get("e", 0)) > 0
    except ValueError:
        return False


def parse_bias(raw):
    """Bias may be a literal or the expression 2^N-1, which is how the catalog
    stores values too large for a 64-bit integer. Reading only the leading digits
    of such an expression reports a catalogue-wide corruption that is not there -
    which is exactly what a hand check did on 2026-07-30, see W-INTL-42."""
    raw = raw.strip()
    m = re.fullmatch(r"2\^(\d+)-1", raw)
    if m:
        return 2 ** int(m.group(1)) - 1
    return int(raw)


def check_field_rule(entries):
    """bias must equal 2^(e-1) - 1 for entries that use a fixed field layout."""
    for e in entries:
        if not uses_fixed_fields(e):
            continue
        try:
            ebits, bias = int(e["e"]), parse_bias(e["bias"])
        except (KeyError, ValueError):
            continue
        expected = 2 ** (ebits - 1) - 1
        if bias != expected:
            shown = expected if expected < 10 ** 12 else f"2^{ebits - 1}-1"
            failures.append(
                f"{e.get('id', '?')}: bias {bias} does not satisfy the field rule "
                f"2^(e-1)-1 for e={ebits}; expected {shown}"
            )


def check_width_rule(entries):
    """bits must equal sign + exponent + mantissa for fixed-layout entries."""
    for e in entries:
        if not uses_fixed_fields(e):
            continue
        try:
            bits, ebits, mbits, s = (int(e[k]) for k in ("bits", "e", "m", "s"))
        except (KeyError, ValueError):
            continue
        if s + ebits + mbits != bits:
            failures.append(
                f"{e.get('id', '?')}: declared {bits} bits but s+e+m = {s + ebits + mbits}"
            )


def check_no_measurements_in_metadata(entries):
    """A measurement asserted in a metadata field has no artefact attached to it.

    This is W-INTL-41: an entry marked verified carried an FPGA frequency in its
    standard field, and the archive it cited contained no hardware data."""
    for e in entries:
        blob = " ".join(e.get(k, "") for k in ("standard", "use_case", "name"))
        hit = MEASUREMENT_IN_METADATA.search(blob)
        if hit:
            notes.append(
                f"{e.get('id', '?')}: metadata asserts a measurement "
                f"({hit.group(0)!r}); a result belongs in a document with an "
                f"artefact, not in a catalog field"
            )


def check_counts(entries):
    if len(entries) != EXPECTED_FORMATS:
        failures.append(
            f"catalog holds {len(entries)} formats, external documents quote {EXPECTED_FORMATS}"
        )
    clusters = collections.Counter(e.get("cluster", "?") for e in entries)
    if len(clusters) != EXPECTED_CLUSTERS:
        failures.append(
            f"catalog holds {len(clusters)} clusters, external documents quote {EXPECTED_CLUSTERS}"
        )
    dupes = [i for i, c in collections.Counter(e.get("id") for e in entries).items() if c > 1]
    if dupes:
        failures.append(f"duplicate catalog ids: {dupes}")


def main():
    allow_missing = "--allow-missing" in sys.argv
    text = load([a for a in sys.argv if a != "--allow-missing"])
    if text is None:
        # This used to return 0 with the word "skipped", which is a green tick that read
        # nothing - the failure mode of W-INTL-153, sitting in this file the whole time.
        # Skipping is now something a caller asks for explicitly.
        if allow_missing:
            print("check_catalog: catalog not reachable; --allow-missing given, skipped")
            return 0
        print("FAIL: catalog not reachable and no path given. Pass a path, or "
              "--allow-missing to say the skip is intended.", file=sys.stderr)
        return 1

    entries = parse(text)
    if not entries:
        print("FAIL: no catalog entries parsed", file=sys.stderr)
        return 1

    check_counts(entries)
    check_field_rule(entries)
    check_width_rule(entries)
    check_no_measurements_in_metadata(entries)
    if len(notes) != EXPECTED_METADATA_OBSERVATIONS:
        failures.append(
            f"catalog: {len(notes)} metadata-measurement observations, "
            f"{EXPECTED_METADATA_OBSERVATIONS} declared in this script - if the upstream "
            f"catalog changed, decide what the new number means and declare it")

    for n in notes:
        print(f"note: {n}")
    for f in failures:
        print(f"FAIL: {f}")

    if failures:
        print(f"\ncheck_catalog: {len(failures)} failure(s) over {len(entries)} entries")
        return 1
    print(f"check_catalog: OK ({len(entries)} entries, {len(notes)} note(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
