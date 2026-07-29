# Weakness Audit Addendum: W-INTL-16 .. W-INTL-25

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

## W-INTL-18  A fabrication date appears in a public roadmap without funding

Severity: high. The link goes into the application.

A public repository status table carries a fabrication date, and a roadmap phase
is built on returned dies. The funding position behind that date has changed.

Action: remove the date, restate the phase without one, and tag every dependent
claim as an open conjecture per rule 10. Rule 10 would have caught this had it
been applied outside this repository.

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

1. W-INTL-17  blocks the economics entirely
2. W-INTL-23  largest credibility gain, hardware already present
3. W-INTL-18  one line, public, in the submission path
4. W-INTL-25  requires a third party, so start earliest

W-INTL-16 was third in this order and is now closed; see its entry above.
