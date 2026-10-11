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

# The catalog size is not a constant. It was 83 when arXiv:2606.09686v2 was published
# on 2026-06-22 and the SSOT has grown since; the documents of this repository were
# moved to a dated-observation wording on 2026-09-04, and this file was not moved with
# them, so the check went on comparing a living number against a published one and
# failed for twenty-six formats that are simply new. W-INTL-276.
#
# What is worth checking is therefore not the size but whether the size still matches
# the last count somebody recorded. The declaration below is an observation with a date
# and a commit behind it, not a quotation from a preprint, and check_count_declaration
# refuses to let it drift away from the E19 row of the evidence ledger - which is the
# defect this replaces: a document and its checker were updated separately.
CATALOG_COUNT = 109
CATALOG_COUNT_DATE = "2026-09-05"
CATALOG_COUNT_COMMIT = "10889fc7"
LEDGER = "paper/evidence_ledger.md"

# The metadata-measurement check observes an artefact in another repository, which this
# project cannot edit. That is a real reason for a note rather than a failure - and a note
# nobody counts is the pattern this project has now promoted away four times. So the
# outstanding observations are declared instead: the check passes while they match and
# fails when they move, which is the part that needs a human either way.
#
# Declared as the set of entries rather than as how many there are. A count alone passes
# when one entry stops asserting a measurement and another starts, which is two changes
# a reader would want to see and no signal at all.
EXPECTED_METADATA_OBSERVATIONS = {"gf16", "tnf4", "tnf8", "tnf16", "tnf32", "tnf64"}
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

# And the same mistake returned through a cluster already on the whitelist. The
# GoldenFloat cluster grew from 22 entries to 48, and eighteen of the new ones carry an
# exponent counted in trits rather than in bits: the catalog says so in the field it
# provides for saying so - "e is 7 balanced-ternary TRITS not bits". A field of Et trits
# takes 3^Et values, so the offset that centres it is (3^Et - 1)/2, which is exactly what
# those entries store; 2^(e-1)-1 is not defined for a trit field. The whitelist let them
# through because it selects on cluster, and a cluster is not a layout. W-INTL-276.
TRIT_EXPONENT = re.compile(r"\btrits?\b", re.I)


def exponent_radix(e):
    """2 for a bit exponent, 3 for one the catalog declares in trits."""
    return 3 if TRIT_EXPONENT.search(e.get("standard", "")) else 2


def expected_bias(radix, ndigits):
    if radix == 3:
        return (3 ** ndigits - 1) // 2, f"(3^{ndigits}-1)/2"
    return 2 ** (ndigits - 1) - 1, f"2^({ndigits}-1)-1"


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
    # The ternary offset has the same problem at width: (3^391-1)/2 does not fit either.
    # Accepted in the form the generator would write it, before any entry needs it.
    m = re.fullmatch(r"\(?3\^(\d+)-1\)?/2", raw)
    if m:
        return (3 ** int(m.group(1)) - 1) // 2
    return int(raw)


def check_field_rule(entries):
    """The bias must be the offset that centres the exponent field, in the radix the
    entry declares that field in: 2^(e-1)-1 for bits, (3^e-1)/2 for trits."""
    for e in entries:
        if not uses_fixed_fields(e):
            continue
        try:
            ndigits, bias = int(e["e"]), parse_bias(e["bias"])
        except (KeyError, ValueError):
            continue
        radix = exponent_radix(e)
        expected, rule = expected_bias(radix, ndigits)
        if bias != expected:
            shown = expected if expected < 10 ** 12 else rule
            unit = "trits" if radix == 3 else "bits"
            failures.append(
                f"{e.get('id', '?')}: bias {bias} does not satisfy the field rule "
                f"{rule} for an exponent of {ndigits} {unit}; expected {shown}"
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
    seen = set()
    for e in entries:
        blob = " ".join(e.get(k, "") for k in ("standard", "use_case", "name"))
        hit = MEASUREMENT_IN_METADATA.search(blob)
        if hit:
            seen.add(e.get("id", "?"))
            notes.append(
                f"{e.get('id', '?')}: metadata asserts a measurement "
                f"({hit.group(0)!r}); a result belongs in a document with an "
                f"artefact, not in a catalog field"
            )
    appeared = sorted(seen - EXPECTED_METADATA_OBSERVATIONS)
    gone = sorted(EXPECTED_METADATA_OBSERVATIONS - seen)
    if appeared or gone:
        failures.append(
            "catalog: the entries asserting a measurement in metadata have moved"
            + (f"; newly asserting: {appeared}" if appeared else "")
            + (f"; no longer asserting: {gone}" if gone else "")
            + " - decide what the change means and declare the new set in this script"
        )


def check_counts(entries):
    if len(entries) != CATALOG_COUNT:
        failures.append(
            f"catalog holds {len(entries)} formats; the last count recorded here is "
            f"{CATALOG_COUNT}, taken on {CATALOG_COUNT_DATE} at {DEFAULT_REPO} "
            f"{CATALOG_COUNT_COMMIT}. The size is a live invariant of the source of "
            f"truth, so this is not a defect in the catalog: count it, then record the "
            f"number, the date and the commit here and in the E19 row of {LEDGER}"
        )
    clusters = collections.Counter(e.get("cluster", "?") for e in entries)
    if len(clusters) != EXPECTED_CLUSTERS:
        failures.append(
            f"catalog holds {len(clusters)} clusters, external documents quote {EXPECTED_CLUSTERS}"
        )
    dupes = [i for i, c in collections.Counter(e.get("id") for e in entries).items() if c > 1]
    if dupes:
        failures.append(f"duplicate catalog ids: {dupes}")


def check_count_declaration():
    """The declaration above and the E19 row of the ledger have to name the same count.

    Both were correct and disagreed with each other for six days: the ledger moved to a
    dated observation of 109 on 2026-09-04 and this file kept the published 83, so a
    reader could have read either number as current. Nothing else in this file compares
    the project against itself, which is how that survived. W-INTL-276."""
    path = pathlib.Path(__file__).resolve().parent.parent / LEDGER
    try:
        text = path.read_text()
    except OSError:
        notes.append(
            f"{LEDGER} not readable from here, so the count declaration was not "
            f"cross-checked against it"
        )
        return
    row = [ln for ln in text.splitlines() if ln.startswith("| E19 ")]
    if not row:
        failures.append(f"{LEDGER}: no E19 row, so the catalog count has no ledger entry")
        return
    line = row[0]
    missing = [s for s in (str(CATALOG_COUNT), CATALOG_COUNT_DATE) if s not in line]
    if missing:
        failures.append(
            f"{LEDGER} E19 does not carry {missing} while this script declares a count of "
            f"{CATALOG_COUNT} taken on {CATALOG_COUNT_DATE} - one of the two was updated "
            f"without the other"
        )


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
    check_count_declaration()

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
