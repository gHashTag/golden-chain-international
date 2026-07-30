#!/usr/bin/env python3
"""Structural checks over the Wave-intl-2 documents.

These exist because every one of them corresponds to a defect that was found by
hand during the verification passes of 2026-07-29, and that a person rereading a
long document will miss again. Each check is cheap and deterministic.

  1. The ledger's summary block reconciles with its own table.
  2. Every verification level used in the table is defined in the legend.
  3. Claims in the application whose ledger row carries a non-supporting level
     are reported, so the two documents cannot drift apart silently.
  4. Placeholders standing for facts only the applicant holds are reported if
     they are still in the body that would be submitted.
  5. Figures that must be identical everywhere are checked across all four
     documents, because a figure cited two ways is how the catalog count went
     wrong.
  6. Internal file references resolve, unless the line naming them says they do
     not exist - the documents deliberately name unwritten files in order to stop
     promising them.
  7. Structural checks on the audit: entries in numeric order, each with a
     severity line, and a status table listing every entry.
  8. Structural checks on the competitor matrix: every quantitative row carries a
     provenance marker, and every [PUB] row names a citation that can be chased.
  9. Percentages stated in a table row must be derivable from two other numbers in
     that row. Added 2026-07-30 after a decoder-share column was found high by a
     consistent factor of about 1.72 across all four of its rows, against a
     denominator that could not be reconstructed from the document. The two columns
     beside it were correct. Nothing in this file recomputed a derived column, so
     nothing noticed for as long as the table stood. Mark a row whose percentage
     genuinely comes from outside its table with `<!-- derived:external -->`.

A note on testing this file. Negative controls must be written with the same care
as the checks. Two of them here failed to fire not because a check was weak but
because the control was: hard-wrapped documents defeat line-based editing, so a
planted fault applied with sed silently did nothing. Plant faults with a
whitespace-insensitive edit, or the test proves only that the test is broken.

Exit code 1 on any failure. Intended to run in CI.
"""

import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "paper" / "evidence_ledger.md"
APPLICATION = ROOT / "paper" / "hub71_form_answers.md"
AUDIT = ROOT / "audits" / "gc_intl_v2_weakness_audit_addendum.md"
MATRIX = ROOT / "research" / "hub71_ai_competitor_matrix.md"
README = ROOT / "README.md"
CHECKLIST = ROOT / "plan" / "submission_checklist.md"

# Placeholders that must never reach a submitted form. Each stands for a fact
# only the applicant holds; none may be invented to make a check pass.
PLACEHOLDERS = ("[PROGRAMME]", "[MONTH]", "[TEAM]", "[ASK]", "[HIRING]",
                "[CLAIM-HELD]", "[CLAIM-PULLED]", "[UNVERIFIED]", "TODO", "TBD")

# Figures that must carry one value everywhere they appear. The pattern is
# matched across all four documents; a second distinct value is a defect,
# because that is how the catalog count came to be cited three ways.
# Figures that must carry one value everywhere. Each pattern CAPTURES the number
# from its surrounding context rather than matching a known value, so a wrong
# value is detected rather than silently skipped. An earlier version keyed on the
# value itself and could not fail - see the inert-pattern guard below.
SHARED_FIGURES = {
    "attestation binary size": r"([\d,]+)-byte static ARM binary",
    "radio SNR":               r"([\d.]+) dB over the noise floor",
    "catalog size":            r"(\d+)[- ]format numeric catalog|catalog (?:size is |of )(\d+) formats?|(\d+) formats in 13",
    "catalog families":        r"(\d+) (?:families|clusters)",
    "tile vectors":            r"(\d+) of \d+ self-checking vectors|runs to (\d+) tests, \d+ pass|(\d+) of 206",
    "cohort deadline":         r"closes \*{0,2}(\d+ August 2026)|Cohort 20 closes \*{0,2}(\d+ August 2026)",
    "leaderboard best":        r"best entry[^.]{0,30}?([\d.]+) bits per byte|Best entry on the live leaderboard \| ([\d.]+)",
}

NON_SUPPORTING = (
    "not built",
    "not measured",
    "partial",
    "undefined",
    "conjecture",
    "refuted",
)

# Topic -> (phrases that indicate the application makes the claim, ledger row).
# Kept explicit rather than inferred: a wrong mapping is worse than none.
TOPICS = {
    "crypto on device": (["X25519", "ChaCha20"], "E1"),
    "radio front end": (["5.8 GHz", "108.6"], "E3"),
    "three mesh nodes": (["Three nodes assembled"], "E4"),
    "ternary tile": (["ternary tile"], "E14"),
    "numeric catalog": (["83-format", "83 formats"], "E19"),
    "energy multiplier": (["4x to 8x"], "E20"),
    "settlement contract": (["MiningPool"], "E21"),
    "allocation": (["renounces ownership"], "E22"),
    "deployment": (["Base Sepolia"], "E23"),
    "attestation root": (["Attestation is designed"], "E26"),
}

failures = []
notes = []


def parse_rows(text):
    rows = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*(E\d+)\s*\|([^|]*)\|([^|]*)\|", line)
        if m:
            rows[m.group(1)] = m.group(3).strip()
    return rows


def check_summary_reconciles(text, rows):
    counts = collections.Counter(v.split(",")[0].strip() for v in rows.values())
    total = sum(counts.values())
    stated = re.search(r"^\s*total\s+(\d+) rows", text, re.M)
    if not stated:
        failures.append("ledger: no total line found in the summary block")
        return
    if int(stated.group(1)) != total:
        failures.append(
            f"ledger: summary claims {stated.group(1)} rows, table has {total}"
        )
    for level, n in counts.items():
        pat = rf"^\s*{re.escape(level)}\s+(\d+) rows?"
        m = re.search(pat, text, re.M)
        if not m:
            failures.append(f"ledger: level '{level}' counted {n} but absent from summary")
        elif int(m.group(1)) != n:
            failures.append(
                f"ledger: summary says {m.group(1)} rows of '{level}', table has {n}"
            )


def check_legend_covers_levels(text, rows):
    try:
        legend = text.split("Verification levels.")[1].split("---")[0]
    except IndexError:
        failures.append("ledger: legend block not found")
        return
    for level in {v.split(",")[0].strip() for v in rows.values()}:
        if level not in legend:
            failures.append(f"ledger: level '{level}' used in the table but not defined")


def check_application_against_ledger(app_text, rows):
    submitted = app_text.split("# NOT FOR SUBMISSION")[0]
    for topic, (phrases, row_id) in TOPICS.items():
        if row_id not in rows:
            failures.append(f"cross-check: ledger row {row_id} for '{topic}' is missing")
            continue
        if not any(p.lower() in submitted.lower() for p in phrases):
            continue
        level = rows[row_id]
        if any(level.startswith(w) for w in NON_SUPPORTING):
            notes.append(
                f"cross-check: '{topic}' appears in the application while {row_id} "
                f"is '{level.split(',')[0]}' - confirm the wording concedes it"
            )


def check_no_placeholders_in_submitted(app_text):
    submitted = app_text.split("# NOT FOR SUBMISSION")[0]
    # The comment header is working material too; it is stripped before sending.
    body = "\n".join(l for l in submitted.splitlines() if not l.startswith("#"))
    found = collections.Counter()
    for line_no, line in enumerate(body.splitlines(), 1):
        for token in PLACEHOLDERS:
            if token in line:
                found[token] += 1
    for token, n in sorted(found.items()):
        notes.append(
            f"placeholder: {token} appears {n} time(s) in application body - "
            f"must be resolved or cut before the form is filled in"
        )


def check_figures_agree(docs):
    for name, pattern in SHARED_FIGURES.items():
        seen = collections.defaultdict(set)
        for path, text in docs:
            # Documents are hard-wrapped, so a phrase can straddle a newline.
            # Collapse whitespace before matching or every multi-word pattern
            # silently misses the wrapped occurrences.
            flat = re.sub(r"\s+", " ", text)
            for hit in re.findall(pattern, flat):
                value = next((g for g in hit if g), None) if isinstance(hit, tuple) else hit
                if value:
                    seen[value].add(path.name)
        docs_seen = set().union(*seen.values()) if seen else set()
        if seen and len(docs_seen) == 1:
            # Found in one document only: nothing to cross-check against, so a
            # pass here means nothing. Say so rather than report a clean run.
            notes.append(
                f"figure '{name}': found only in {sorted(docs_seen)[0]} - "
                f"not cross-checked, since one document cannot disagree with itself"
            )
        if not seen:
            # A pattern that matches nothing cannot fail, so it is not a check.
            # This is the broken-ruler case: the instrument, not the claim, is
            # what went wrong, and it must be loud rather than silent.
            failures.append(
                f"figure '{name}': pattern matched nothing in any document - "
                f"the check is inert and must be fixed or removed"
            )
            continue
        if len(seen) > 1:
            detail = "; ".join(f"{v!r} in {sorted(f)}" for v, f in seen.items())
            failures.append(f"figure '{name}' stated more than one way: {detail}")


ACKNOWLEDGED = ("not written", "does not exist", "never written", "dangling")


def check_audit_structure(audit_text):
    entries = re.findall(r"^## W-INTL-(\d+)\b(.*)$", audit_text, re.M)
    if not entries:
        failures.append("audit: no entries parsed")
        return
    numbers = [int(n) for n, _ in entries]
    if numbers != sorted(numbers):
        out_of_place = [n for n, s in zip(numbers, sorted(numbers)) if n != s]
        failures.append(
            f"audit: entries out of numeric order, first divergence at {out_of_place[:3]}"
        )
    if len(numbers) != len(set(numbers)):
        dupes = [n for n, c in collections.Counter(numbers).items() if c > 1]
        failures.append(f"audit: duplicate entry numbers {dupes}")

    # Every entry must state a severity, since the file ranks by it.
    blocks = re.split(r"(?m)^(?=## W-INTL-)", audit_text)
    for block in blocks:
        m = re.match(r"## W-INTL-(\d+)", block)
        if m and not re.search(r"^Severity", block, re.M):
            failures.append(f"audit: W-INTL-{m.group(1)} has no severity line")

    # The status table at the end must account for every entry.
    listed = set(re.findall(r"^\| W-INTL-(\d+)", audit_text, re.M))
    ranges = re.findall(r"^\| W-INTL-(\d+) \.\. W-INTL-(\d+)", audit_text, re.M)
    for lo, hi in ranges:
        listed |= {str(i) for i in range(int(lo), int(hi) + 1)}
    missing = sorted(set(str(n) for n in numbers) - listed, key=int)
    if missing:
        notes.append(
            "audit: status table does not list W-INTL-" + ", W-INTL-".join(missing)
        )


def check_matrix_markers(matrix_text):
    """Rows in the competitor tables quote figures for third parties and for this
    project. Each such figure must carry a provenance marker, and a [PUB] marker
    must name a source that can be chased. An unmarked figure in a comparison
    table is how a competitor came to be understated by a fifth."""
    markers = ("[PUB]", "[EST]", "[UNVERIFIED]")
    in_table = False
    for line in matrix_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if set("".join(cells)) <= set("-: "):
            in_table = True          # separator row: the table has begun
            continue
        if not in_table:
            continue
        # A throughput or power figure is a cell holding a number with a unit.
        quantitative = [c for c in cells
                        if re.search(r"\d", c) and re.search(r"tok/s|\bW\b|mW|bits per byte|percent", c)]
        if not quantitative:
            continue
        if not any(m in stripped for m in markers):
            notes.append(
                f"matrix: quantitative row without a provenance marker: "
                f"{cells[0][:44]!r}"
            )
        if "[PUB]" in stripped and not re.search(r"arXiv:\d|ISSCC|TerEffic|\d{4}", stripped):
            notes.append(
                f"matrix: [PUB] row without a chaseable citation: {cells[0][:44]!r}"
            )


DERIVED_EXEMPT = "derived:external"


def check_derived_percentages(docs):
    """A percentage in a table row is a claim about two other numbers in that row.

    For each row containing 'N percent' or 'N%', look for an ordered pair of the
    row's other numeric cells whose ratio rounds to N. If no pair does, the figure
    came from somewhere the reader cannot see, and that is either a labelling
    omission or an arithmetic error. It was an arithmetic error the one time this
    was checked by hand.
    """
    for path, text in docs:
        for line in text.splitlines():
            if not line.startswith("|") or DERIVED_EXEMPT in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            pcts, plain = [], []
            for cell in cells:
                m = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*(?:percent|%)", cell)
                if m:
                    pcts.append(float(m.group(1)))
                    continue
                n = re.fullmatch(r"([0-9][0-9,]*(?:\.[0-9]+)?)", cell)
                if n:
                    plain.append(float(n.group(1).replace(",", "")))
            if not pcts or len(plain) < 2:
                continue
            for pct in pcts:
                found = False
                for a in plain:
                    for b in plain:
                        if b and abs(100.0 * a / b - pct) <= 1.0:
                            found = True
                if not found:
                    failures.append(
                        f"{path.name}: '{pct:g} percent' in a row whose other "
                        f"numbers {[int(v) if v.is_integer() else v for v in plain]} "
                        f"produce no such ratio"
                    )


def check_references_resolve(paths):
    """A reference to a file that does not exist is a defect unless the same
    line says so. Documents here deliberately name unwritten files in order to
    stop promising them, and flagging that as a fault would train the reader to
    ignore the checker."""
    for path in paths:
        text = path.read_text()
        for line in text.splitlines():
            for ref in set(re.findall(r"`([a-z]+/[a-z0-9_]+\.md)`", line)):
                if (ROOT / ref).exists():
                    continue
                if any(a in line.lower() for a in ACKNOWLEDGED):
                    continue
                notes.append(f"reference: {path.name} points at missing {ref}")


def main():
    if not LEDGER.exists() or not APPLICATION.exists():
        print("check_consistency: expected documents not found", file=sys.stderr)
        return 1

    ledger_text = LEDGER.read_text()
    rows = parse_rows(ledger_text)
    if not rows:
        failures.append("ledger: no claim rows parsed")

    app_text = APPLICATION.read_text()
    docs = [(p, p.read_text())
            for p in (LEDGER, APPLICATION, AUDIT, MATRIX, README, CHECKLIST)
            if p.exists()]

    check_summary_reconciles(ledger_text, rows)
    check_legend_covers_levels(ledger_text, rows)
    check_application_against_ledger(app_text, rows)
    check_no_placeholders_in_submitted(app_text)
    check_figures_agree(docs)
    if AUDIT.exists():
        check_audit_structure(AUDIT.read_text())
    if MATRIX.exists():
        check_matrix_markers(MATRIX.read_text())
    check_references_resolve([p for p, _ in docs])
    research = sorted((ROOT / "research").glob("*.md")) if (ROOT / "research").exists() else []
    check_derived_percentages(docs + [(p, p.read_text()) for p in research])

    for note in notes:
        print(f"note: {note}")
    for failure in failures:
        print(f"FAIL: {failure}")

    if failures:
        print(f"\ncheck_consistency: {len(failures)} failure(s)")
        return 1
    print(f"check_consistency: OK ({len(rows)} rows, {len(notes)} note(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
