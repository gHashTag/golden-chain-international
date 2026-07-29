#!/usr/bin/env python3
"""Structural checks over the Wave-intl-2 documents.

These exist because every one of them corresponds to a defect that was found by
hand during the verification passes of 2026-07-29, and that a person rereading a
long document will miss again. Each check is cheap and deterministic.

  1. The ledger's summary block reconciles with its own table.
  2. Every verification level used in the table is defined in the legend.
  3. Claims in the application whose ledger row carries a non-supporting level
     are reported, so the two documents cannot drift apart silently.
  4. Internal file references resolve.

Exit code 1 on any failure. Intended to run in CI.
"""

import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "paper" / "evidence_ledger.md"
APPLICATION = ROOT / "paper" / "hub71_form_answers.md"

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


def check_references_resolve(paths):
    for path in paths:
        for ref in set(re.findall(r"`([a-z]+/[a-z0-9_]+\.md)`", path.read_text())):
            if not (ROOT / ref).exists():
                notes.append(f"reference: {path.name} points at missing {ref}")


def main():
    if not LEDGER.exists() or not APPLICATION.exists():
        print("check_consistency: expected documents not found", file=sys.stderr)
        return 1

    ledger_text = LEDGER.read_text()
    rows = parse_rows(ledger_text)
    if not rows:
        failures.append("ledger: no claim rows parsed")

    check_summary_reconciles(ledger_text, rows)
    check_legend_covers_levels(ledger_text, rows)
    check_application_against_ledger(APPLICATION.read_text(), rows)
    check_references_resolve([LEDGER, APPLICATION])

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
