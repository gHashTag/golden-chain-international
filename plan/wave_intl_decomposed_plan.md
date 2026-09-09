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
| G3 | Catalog size and family count settled | direct count of the single source of truth: 83 records, 13 clusters summing to 83 at the 2026-07-29 count recorded in the ledger appendix; the count is a live invariant that has grown since (109 records at origin/master, 2026-09-05), so no document states it as a fixed current figure |
| G4 | Competitor figures verified at source | 9.51 tok/s found in the contributions and evaluation sections of the cited paper, not only its abstract; 25 tok/s under 5 W confirmed in the second |
| G5 | Ternary tile reproduced | testbench compiled and run: 206 of 206 pass; synthesis emits no DSP primitive |
| G6 | Submission target and deadline established | Cohort 20 closes 21 August 2026; Hub71+ AI is an ecosystem, not a track |
| G7 | Allocation stated rather than denied | contract read; split published with the comparison that survives it |
| G8 | Stale contradictions marked | banners on three archived issue bodies that asserted the opposite of the current status |

## Gates that are open, and can be closed without the applicant

| # | Gate | Check that will close it | Blocked on |
|---|---|---|---|
| G9 | Energy figure sourced or dropped | the honest derivation exists in the repository, or the number is gone from every external document | half resolved 2026-07-29. The naive side was found: a document dividing 1 pJ per multiply-accumulate by 0.05 pJ per add to reach 20x, while also stating 10 to 20x and 20 to 30x elsewhere in the same file. The honest side that reduces this to 4x to 8x was not found. The pairing hard rule 7 requires is currently one-sided, with only the overclaiming half written down |
| G19 | A bound exists, not only measurements | at least one converse bound on response positions, proved and controlled in CI | CLOSED 2026-08-13. research/theory_bounds.py: four theorems with controls, floor at 179 positions set by the measured min-entropy density. Prior art cited, arXiv:2502.03221, so this is a reproduction in this project's model and not a contribution. See W-INTL-251 to W-INTL-254 |
| G20 | Comparisons re-read as implementation figures | no document reads an effective-bit-error-rate comparison as a statement about what is achievable | open 2026-08-13. Theorem 4 shows the summary is lossy by 11 to 17 percent through Jensen; W-INTL-118 and the dissertation table both use it. Nothing external states it yet, so this is a discipline gate rather than a correction. See W-INTL-252. W-INTL-256 recorded the entropy-only ambiguity; W-INTL-257 resolves the DATE Table 1 row as 256 selected-mask bits plus 32 syndrome bits, while the introduction's separate 288-bit wording remains open. |
| G21 | Positioned against the literature, not the vendors | the comparison axis is one the field publishes | CLOSED 2026-08-13. Eleven commercial PUF lines surveyed and none publishes response bits paired with helper data at a stated word error rate; four academic figures do and are recorded. See W-INTL-255 |
| G17 | Reliable-bit selection evaluated or dropped | the alternative framing has a measured response-bit count at this project's error rate, not a quoted one | closed 2026-07-30. research/reliable_bit_selection.py measures it: the mechanism transfers, the advantage does not. 1,211 to 1,765 response bits at six percent raw against 635 under SLLC, and thirty-one enrolment reads per position against one. Bounded to repetition as the inner code; a convolutional pairing was not measured. See W-INTL-118, W-INTL-119 |
| G18 | Helper data folded into the key | K = S xor f(W) present in the key derivation | partly closed by W-INTL-262 as a finite software control; the deployed encoding, leakage, attacker model, and hardware integration remain open |
| G10 | Settlement layer described consistently | no external document describes the four-proof economics as implemented | CLOSED 2026-07-29. Four places corrected: the solution paragraph, the business model, the traction list and the host-programme note. The traction line claiming settlement contracts written and deployed was the sharpest and is gone |
| G11 | Silicon vocabulary split | no external document uses an unqualified "silicon" to span shuttle tile and custom die | CLOSED 2026-07-29. The application now defines both terms and states that the shuttle tile is submitted and awaiting fabrication while the custom die is neither funded nor existing |
| G12 | Public cross-references resolve | every link in the README returns content to an anonymous reader | CLOSED 2026-07-29. All four remaining repository links return HTTP 200 to a logged-out request. The private preprint repository is now cited by arXiv identifier, which resolves for anyone, and the derivation claim resting on a non-public origin is withdrawn from Scope |

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


## Wave-intl-261 bounded follow-up

| Item | Result | Remaining boundary |
|---|---|---|
| Reliability metadata precision before the BCH list | [measured] one bit per response position (127 metadata bits per 127-bit word) reaches the same finite failure counts as 2, 3, and 8 bits in the two heterogeneous controls | [open conjecture] helper-data encoding, binding, larger lists, area, timing, and G16 hardware |

The result is a finite-code control, not a claim that a deployed helper-data protocol needs exactly one bit.

## Wave-intl-262 bounded follow-up

| Item | Result | Remaining boundary |
|---|---|---|
| Helper-data binding in the key equation | [measured] `K = S xor H(W)` round-trips 64/64 clean trials; under 2,048 direct one-bit helper mutations the bound key changes in 2,048/2,048 samples while the unbound control remains unchanged | [open conjecture] security proof, leakage, helper-data encoding policy, adversarial decoder strategy, area, timing, and G16 hardware |

The script is a finite control of the key equation, not evidence that a deployed PUF construction is secure.


## Wave-intl-263 bounded follow-up

| Item | Result | Remaining boundary |
|---|---|---|
| Rank-sized syndrome helper coordinates | [measured] binary elimination over the repository's BCH(127,57,11) syndrome map gives rank 70 per block; six blocks reconstruct exactly from 420 semantic coordinate bits, with 64/64 decoder agreement and 26,880 independent coordinate mutations | [open conjecture] this is not a leakage theorem or a deployed wire format; adversarial decoding, side channels, area, timing, FPGA integration, and G16 hardware remain open |

The 504-bit semantic reduction is a storage representation fact. It must not be presented as a security gain, because the literature treats syndrome rank and public helper-data leakage as separate questions.

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


## Wave-intl-264 bounded follow-up

| Item | Result | Remaining boundary |
|---|---|---|
| Exact membership of the BCH syndrome helper image | [measured] rank-70 elimination accepts 384/384 helpers from deterministic enrolment, rejects 256/256 random 154-bit ambient words, and reports 212/256 one-symbol-bit perturbations outside the image while 44/256 remain valid | [open conjecture] the exact 2^-84 image fraction is not a leakage/security bound; helper encoding, active attacks, area, timing, FPGA integration, and G16 hardware remain open |

This is a finite representation and integrity-precheck control. A decoder's refusal is not used as the membership oracle, and the nearby perturbation control is reported with both outcomes rather than being forced into “invalid”.


## Wave-intl-265 bounded follow-up

| Item | Result | Remaining boundary |
|---|---|---|
| Canonical packed helper-data boundary | [measured] six rank-70 coordinate words occupy 420 semantic bits in 53 bytes with four padding bits; 64/64 canonical round-trips pass, 256/256 padding-bit mutations reject, and 64/64 payload mutations remain syntactically accepted while changing the expanded helper | [open conjecture] authenticated framing, helper-data integrity, leakage, active attacks, area, timing, FPGA integration, and G16 hardware |

This result narrows the interface boundary rather than proposing a deployed wire format: exact syndrome-image membership catches ambient-word errors before compression, while a full coordinate payload needs a separate integrity mechanism.


## Wave-intl-266 bounded follow-up

| Item | Result | Remaining boundary |
|---|---|---|
| Versioned helper-frame parser boundary | [measured] `research/framed_helper_contract.py` accepts 64/64 canonical frames and rejects 64/64 truncations, extensions, wrong-version frames, wrong-format frames, and payload mutations; `scripts/check_models_run.py` pins all six counts | [open conjecture] the digest is not a keyed authenticator; robust fuzzy-extractor security, leakage, active attacks, deployment, area, timing, FPGA integration, and G16 hardware remain open |

This is a parser and framing control, not an authenticated wire format. The literature search found direct prior art for robust helper-data tamper detection and public-helper-data leakage, so the implementation is positioned as a bounded interface result and not as a security novelty.
