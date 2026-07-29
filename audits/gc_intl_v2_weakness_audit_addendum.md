# Weakness Audit Addendum: W-INTL-16 .. W-INTL-27

Status: Wave-intl-2 draft, extends `audits/gc_intl_v1_weakness_audit.md`
Rule basis: hard rule 10 - every unproven claim tagged with a falsification path.

Each entry states the weakness, where a reviewer will find it, the severity, and
the action that closes it. Severity is scored by how quickly an external
reviewer encounters it, not by how difficult it is to fix.

---

## W-INTL-16  Numeric catalog cited with three different counts  [CLOSED 2026-07-29]

Severity when opened: high. Found by reading any two public repositories in
sequence. Re-verified on 2026-07-29 and closed: the divergence no longer exists
in any live artefact.

The finding as originally written is superseded. Verification performed:

- arXiv:2606.09686 carries a v2 dated 2026-06-22. The live title and abstract
  read 83 formats spanning 13 families. The v1 count of 84 is superseded.
- The canonical SSOT specs/numeric/formats_catalog.t27 in gHashTag/t27 counts
  83 catalog records with no duplicate ids, and 13 families.
- The public README of gHashTag/trinity-fpga states an 83-entry catalog and
  points at fpga/CATALOG_MATRIX_83.md as the live SSOT.
- The public README of gHashTag/t27 states an 83-format SSOT.
- The README of this repository states an 83-format numeric catalog.
- A code search across the account for the string 84-Format returns exactly two
  files, and both are the published errata that record the correction. That is
  the correct place for a superseded number to survive.

Root cause of the original delta, per the errata: E8M0 block scale was counted
as a standalone format in v1. It is the shared-exponent component of the
Microscaling family, covered by its own conformance pack but not enumerated as
a catalog row. Canonical size is therefore 83.

No action remains. Reopens if a direct count of the SSOT returns a number other
than 83, or if any public artefact outside an erratum asserts a different size.

## W-INTL-17  Settlement requires device signatures that do not exist

Severity: critical. Blocks the entire economic layer, not one component.

The settlement contract requires device signatures and a unique hardware
fingerprint among its checks. A design note states that any reward path
settling without a valid device signature is a protocol violation. Together
these mean that no proof type can settle on mainnet until dies exist - including
the three arms described elsewhere as operating today. Software-signed operation
does not close this: the contract will not accept those signatures.

Action: either (a) introduce a transitional signing mode anchored in the mesh
node's own signature scheme, so three arms settle with valid hardware signatures
and device signatures become a later strengthening, or (b) state plainly that
mainnet is gated on silicon and treat that gate as a funding requirement.

Closes when a settlement path exists that is both accepted by the contract and
executable on present hardware, or when the gate is documented as intentional.

Drafted formulation for option (a), offered so the decision has something concrete
to accept or reject. It is not yet adopted.

> Settlement accepts two signer classes. A class-1 signer is a die-resident key
> and is required for any reward whose proof type asserts a hardware property that
> only a die can hold. A class-2 signer is a mesh-node key held in the node's own
> bitstream signature scheme, is enrolled once against per-device secret material
> rather than a factory serial, and may settle transport, coverage and sensing
> proofs only. Inference proofs remain class-1. The contract records the signer
> class on every settled reward, so the boundary is auditable after the fact and a
> later migration to class-1 does not rewrite history.

Why this shape. It lets the three arms that genuinely run today settle without
asserting anything about silicon, keeps the one arm that does depend on a die
behind the gate, and leaves an on-chain record of which class paid for what. It
also removes the contradiction between the settlement contract and the claim that
three proof types operate today, which is currently the sharpest inconsistency an
external reviewer can find between two of these documents.

The alternative, option (b), is to state that mainnet is gated on silicon and treat
that gate as a funding requirement. That is cheaper to write and harder to sell,
because it moves the entire economic layer behind an unfunded milestone.

## W-INTL-18  Silicon status is two different things under one word  [REVISED 2026-07-29]

Severity: revised down from high to medium, and the finding is restated. The
original wording claimed a public status table carries a dead fabrication date.
Direct inspection on 2026-07-29 does not support that wording.

What the public artefacts actually say. The status table in gHashTag/tt-trinity-gamma
marks GDS / TAPEOUT as submitted and awaiting fabrication, not as fabricated. The
date it carries, 2026-05-17, is labelled as a submission entry, and the file states
in terms that the row moves to complete only once the shuttle confirms fabrication.
That is careful reporting, and the original finding overstated it.

The real exposure is a word collision. Tiny Tapeout on an open multi-project shuttle
and a funded custom die are both called silicon in different documents. A reviewer
who reads a submitted Tiny Tapeout tile as evidence of a funded tape-out will have
been misled by the vocabulary rather than by any single false sentence. The
application text already says silicon remains an open item, which is correct.

Action: use two distinct terms in every external document - shuttle tile for the
Tiny Tapeout work, custom die for the funded path - and never let a claim about one
carry over to the other. Closes when no external document uses an unqualified
silicon to span both.

## W-INTL-26  Two of six public cross-references are unreachable to a reviewer

Severity: high. Costs a reviewer thirty seconds to find and reads as carelessness.

The Cross-references section of the public README listed six repositories. Checked
anonymously on 2026-07-29, which is the view an external reader gets:

- gHashTag/paper3-methodology, tt-trinity-corona, t27, trios-mcp-rag - reachable.
- gHashTag/goldenfloat-preprint - private, returns 404 to an external reader,
  while being cited as the home of arXiv:2606.05017.
- gHashTag/paper3-rossiya30-troica - does not exist, returns 404.

The second of these carries weight beyond a broken link. The Scope section defines
this repository as the international derivative of that Russian-language origin. If
the origin is not public, the derivation cannot be checked, and the four Wave-intl-1
deliverables that were to be derived from it have no source.

Action: taken in part. The README now marks both as unreachable and states that
Wave-intl-1 will be written directly rather than translated. Closes fully when
either the repositories are published under the stated names, or the references are
replaced by artefacts that resolve - the arXiv identifier in place of the preprint
repository, and a plain statement of origin in place of the missing one.

## W-INTL-27  The submission target was misdescribed and the deadline was wrong

Severity: critical for scheduling. Found by reading hub71.com rather than the repository.

Two premises behind this work were wrong, and both were load-bearing.

Hub71+ AI is not a standalone application track. It is a specialist ecosystem
entered by answering an AI question inside whichever programme form is chosen -
Access Programme, Hub71+ Digital Assets, Hub71+ ClimateTech, Hub71+ Life Sciences,
Initiate, SAVI, Sandbox, or ECA Anjal Z. Documents headed as answers to a Hub71+ AI
track therefore describe a form that does not exist on its own. The two AI questions
they contain are real and correctly reproduced; what is missing is the choice of
host programme, which is still open and is a decision for the applicant.

The deadline in the README was 2 August 2026. The Access Programme page and the
Hub71+ Digital Assets page both state 21 August 2026 for Cohort 20, with the
programme starting February 2027. Checked 2026-07-29. Planning built on 2 August
compressed a twenty-three day runway into four.

Action: taken. The README now states the verified deadline and the ecosystem model.
Remaining: choose the host programme, and re-title the answers file once chosen.
Closes when one programme is named and the answers are aligned to that form.

## W-INTL-19  Bench-tier part has no bitstream signature scheme and broken encryption

Severity: medium for the product, high if the bench tier is ever described as a
trust anchor.

The compute boards use a part whose bitstream encryption has a published full
break (USENIX Security 2020) and which, unlike its system-on-chip siblings,
carries no public-key bitstream signature scheme. Design confidentiality on
those boards cannot be assumed under physical access.

Action: keep the documented separation between mesh tier and bench tier explicit
in every external document. Never let a settlement path accept a bench-tier
signature.

Closes when the separation is stated in the whitepaper and enforced in the
contract's accepted-signer set.

## W-INTL-20  Factory device identifiers are not unique

Severity: medium. Matters for resistance to fabricated node identities.

The factory-programmed device identifier on the bench-tier family is documented
by the vendor as potentially shared by up to thirty-two devices, and the
register is readable by anyone with physical access. It is a serial number, not
a secret and not an identity.

Action: never let identity rest on the identifier alone. Identity must come from
per-device secret material. Closes when the enrolment procedure documents this
explicitly.

## W-INTL-21  A response-deadline challenge does not identify hardware class

Severity: medium. Prevents a claim that would not survive review.

Two related ideas were tested and one was refuted.

Sequential deadline: refuted. A native optimised software implementation of a
dependent round chain completes each round faster than the target device does,
across the full clock range considered. A deadline tight enough to exclude
software would exclude the device.

Parallel width: partial. Separation holds against a general-purpose processor
and inverts against a many-lane accelerator, which has more lanes than the
device has challenge engines.

Action: do not claim that a timing challenge proves hardware class. Use it as
supporting evidence against casual emulation only. Identity carries the claim.

## W-INTL-22  No end-to-end inference system exists

Severity: high for any published comparison.

The compute side has one operator. Attention, key-value cache, normalisation
and quantisation units are absent. Comparing a single operator against published
full-system accelerators is not a valid comparison in either direction.

Action: publish no throughput comparison until the pipeline exists. State the
absence in the evidence ledger, which is done. Closes when an end-to-end path
runs and is measured.

## W-INTL-23  The demonstration gate has not been run

Severity: high. This is the largest gap between what is built and what is shown.

The three-node shared-uplink demonstration and the self-healing measurement are
both in simulation. The hardware to run them is assembled.

Action: run it. This is the single change with the largest effect on external
credibility, and the prerequisites are already on the bench.

## W-INTL-24  No emission has occurred and no licence is held

Severity: medium, and rising with any deployment discussion.

All radio work to date is digital loopback. Over-the-air operation requires an
external amplifier chain and regulatory permission, which in the target
jurisdiction is a separate process with its own timeline.

Action: open the regulatory conversation before it is on the critical path.
Raising it unprompted in a review is stronger than being asked.

## W-INTL-25  Single founder, no revenue, no signed operator

Severity: high in any evaluation that scores team and market separately.

Action: a named local hiring plan is mandatory in the application text, not
optional. A letter of intent from one operator converts the submission from a
technology case into a commercial one and is the highest-value item obtainable
before the deadline.

---

## Priority order

1. W-INTL-27  everything else is scheduled against it; partly closed, one decision left
2. W-INTL-17  blocks the economics entirely
3. W-INTL-23  largest credibility gain, hardware already present
4. W-INTL-25  requires a third party, so start earliest
5. W-INTL-26  cheap, high visibility, partly closed
6. W-INTL-18  vocabulary discipline, no artefact change required

W-INTL-16 was third in the previous order and is now closed; see its entry above.

## Status at 2026-07-29

| Entry | State |
|---|---|
| W-INTL-16 | closed, verified |
| W-INTL-17 | open, formulation drafted, decision required |
| W-INTL-18 | revised, severity lowered, restated |
| W-INTL-19 .. W-INTL-22 | open, unchanged |
| W-INTL-23 | open, hardware present, gate not run |
| W-INTL-24 | open, unchanged |
| W-INTL-25 | open, requires a third party |
| W-INTL-26 | partly closed, README corrected |
| W-INTL-27 | partly closed, host programme still to choose |
