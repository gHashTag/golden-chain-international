# Decomposed Plan

Status: written 2026-07-29, replacing the plan referenced but never landed as
`wave_intl_1_decomposed_plan.md`. See the note at the end on why the numbering
changed.

Each gate states the work, the check that closes it, and who can do it. A gate
that cannot be checked is not a gate.

---

## Gates that are closed

| # | Gate | Check that closed it |
|---|---|---|
| G1 | Hard-rules gate passes in CI | a run of the workflow returns success; three consecutive runs have |
| G2 | Ledger arithmetic reconciles | counts derived by parsing the level column match the table row for row |
| G3 | Catalog size and family count settled | direct count of the single source of truth: 83 records, 13 clusters summing to 83 |
| G4 | Competitor figures verified at source | 9.51 tok/s found in the contributions and evaluation sections of the cited paper, not only its abstract; 25 tok/s under 5 W confirmed in the second |
| G5 | Ternary tile reproduced | testbench compiled and run: 206 of 206 pass; synthesis emits no DSP primitive |
| G6 | Submission target and deadline established | Cohort 20 closes 21 August 2026; Hub71+ AI is an ecosystem, not a track |
| G7 | Allocation stated rather than denied | contract read; split published with the comparison that survives it |
| G8 | Stale contradictions marked | banners on three archived issue bodies that asserted the opposite of the current status |

## Gates that are open, and can be closed without the applicant

| # | Gate | Check that will close it | Blocked on |
|---|---|---|---|
| G9 | Energy figure sourced or dropped | the honest derivation exists in the repository, or the number is gone from every external document | half resolved 2026-07-29. The naive side was found: a document dividing 1 pJ per multiply-accumulate by 0.05 pJ per add to reach 20x, while also stating 10 to 20x and 20 to 30x elsewhere in the same file. The honest side that reduces this to 4x to 8x was not found. The pairing hard rule 7 requires is currently one-sided, with only the overclaiming half written down |
| G10 | Settlement layer described consistently | no external document describes the four-proof economics as implemented | nothing |
| G11 | Silicon vocabulary split | no external document uses an unqualified "silicon" to span shuttle tile and custom die | nothing |
| G12 | Public cross-references resolve | every link in the README returns content to an anonymous reader | publishing or replacing two repositories |

## Gates that need the applicant

| # | Gate | Check | Needed |
|---|---|---|---|
| G13 | Host programme chosen | one programme named, and the answers aligned to its form | a decision |
| G14 | Application facts complete | no placeholder markers remain in the answers file | relocation month, team, funding ask, named hiring plan |
| G15 | Evidence upgraded where weakest | the three-board row rests on a dated artefact rather than an operator confirmation | one photograph |

## The gate that changes the category

| # | Gate | Check | Note |
|---|---|---|---|
| G16 | Three-node shared uplink demonstrated | the demonstration runs on the assembled hardware and the result is recorded with a date | this is the only remaining item that changes what kind of application this is, rather than how it is worded. The hardware is on the bench |

---

## Order

G9 and G10 first, because they are the last two places where a document says
something the artefacts do not support, and both are closable by the person
holding this file.

G13 next, because the choice of programme determines which narrative leads and
therefore what the remaining prose should say. Writing the prose before the choice
wastes the writing.

G16 whenever the bench is free. It is worth more than the rest of this list
combined, and the deadline no longer forces a choice between doing it and
submitting on time.

G14 and G15 last, because they are quick once the rest is settled.

---

## Note on the numbering

The repository README referred to a fifteen-gate roadmap in a file named
`wave_intl_1_decomposed_plan.md`. That file was never written, and neither were
the other four Wave-intl-1 deliverables. The Russian-language origin repository
they were to be derived from returns 404 to an external reader, so there was
nothing to translate.

This plan is written directly and is not a reconstruction of the one that was
promised. It does not claim to be. The gate numbers here are its own.

The same applies to `audits/gc_intl_v1_weakness_audit.md`, which the Wave-intl-2
addendum names as the document it extends. That file does not exist, so the
addendum extends nothing and its numbering starts at 16 for historical reasons
only. Rather than invent fifteen findings to fill the gap, the addendum has been
marked to say so.
