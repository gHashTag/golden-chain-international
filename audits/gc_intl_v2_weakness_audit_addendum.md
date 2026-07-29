# Weakness Audit Addendum: W-INTL-16 .. W-INTL-37

Entries are in numeric order. They were not until 2026-07-29: 26 and 27 had been
appended where they were written rather than where they belong, which put 19
through 25 after them.

Status: Wave-intl-2. The predecessor this extends is
`paper3-rossiya30-troica/research/weak_spots_registry.md` in gHashTag/trinity-papers-ru,
a Russian-language registry running W1 to W18. That is why the numbering here
starts at 16. An earlier version of this header said the predecessor had never
been written; that was wrong, and W-INTL-32 records why the search missed it.

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

## W-INTL-17  Settlement requires device signatures that do not exist  [RESTATED 2026-07-29]

Severity: still critical, but the object of the finding was wrong and is corrected
here. This entry and W-INTL-30 were carrying two accounts of one thing, which the
audit is not allowed to do.

The correction. This entry says the settlement contract requires device
signatures. W-INTL-30 established that no settlement contract exists in source.
Both cannot be true of one object. What is true: the requirement lives in a design
note, not in code. So the blockage described below is a property of the design, and
the design is not yet implemented - which makes this entry a constraint on work not
started rather than a bug in work delivered. The severity stays critical because
the constraint is real and shapes what can be built; the framing changes because a
reviewer told that a contract requires something will look for the contract.

The design note requires device signatures and a unique hardware fingerprint
among its checks, and states that any reward path settling without a valid device
signature is a protocol violation. Together
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

## W-INTL-19  Both tiers have published bitstream attacks, and the difference between them is not the one stated  [REVISED 2026-07-29]

Severity: raised from medium to high. The entry as originally written drew a
distinction that the literature does not support, and the distinction was
load-bearing for the attestation claim.

What was written. The bench-tier part has a published full break of its bitstream
encryption, and unlike its system-on-chip siblings carries no public-key
signature scheme. That much is correct: the break is STARBLEED, Ender, Moradi and
Paar, USENIX Security 2020, "The Unpatchable Silicon: A Full Break of the
Bitstream Encryption of Xilinx 7-Series FPGAs". Artix-7 is a 7-Series part, the
attack is low-cost, and the vendor's own position is that it cannot be patched in
silicon.

What was wrong. The implication that the mesh tier is unaffected. Zynq-7000
contains 7-Series programmable logic. The vendor advisory did claim resistance,
on the grounds that authentication in the boot process runs before configuration
is used. That claim has since been broken in public: Ravi and others, USENIX WOOT
2024, "Achilles Heel in Secure Boot: Breaking RSA Authentication and Bitstream
Recovery from Zynq-7000 SoC", also IACR eprint 2023/1913. They report a flaw in
the first-stage boot loader that bypasses RSA authentication outright, and the
first practical STARBLEED recovery of a decrypted bitstream from an AES-256
encrypted boot image on Zynq-7000.

The real difference, and it does survive. The bench-tier break is in silicon and
unpatchable; the mesh-tier bypass is in first-stage boot loader software and is
fixable by changing that software. So the tiers are not equivalent, but the
separation rests on patchability rather than on one part being sound. That is a
weaker and more defensible statement than the one it replaces.

Action.

1. State the mesh-tier position accurately wherever the trust anchor is
   described. A part with a signature scheme that has a published, fixable bypass
   is not the same as a part with an intact one, and a security-literate reviewer
   will know the difference.
2. Establish whether the deployed first-stage boot loader carries the fix. This is
   checkable and has not been checked. Until it is, the attestation root is
   [Open conjecture] per hard rule 10.
3. Keep the tier separation, but justify it by patchability rather than by
   presence or absence of a scheme.

Closes when the boot loader is confirmed patched and the external description
matches. Never let a settlement path accept a bench-tier signature regardless.

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

## W-INTL-26  Two of six public cross-references are unreachable to a reviewer  [CLOSED 2026-07-29]

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

Closed. Every repository link in the README now returns HTTP 200 to a logged-out
request, checked that way rather than from an authenticated session. The private
preprint repository is cited by its arXiv identifier instead, which resolves for
anyone. The Scope claim that this edition derives from a Russian-language origin
is withdrawn: the origin is not public, so the derivation cannot be checked, and
an unverifiable provenance claim is worse than none.

Reopens if any README link stops resolving anonymously.

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

## W-INTL-28  A leaderboard placement is asserted that no artefact supports

Severity: critical, and higher than anything else in this file. It is the one
claim in the application that an AI-track reviewer can check in about a minute,
and the check is the first one such a reviewer would run.

The claim. Top-5 placement in OpenAI's Parameter Golf at 0.9650 bits per byte.

What was checked on 2026-07-29, and what was found.

- The live leaderboard in openai/parameter-golf lists its best entry at 1.0565
  bits per byte. Lower is better on this metric. A score of 0.9650 would not be a
  top-five placement; it would lead the board by a wide margin.
- The string 0.9650 does not appear in that leaderboard.
- No entry on that leaderboard is attributed to this author, this project, or any
  of the account names associated with it.
- The local checkout of the challenge is a fork. A fork is not a submission.
- The one record directory in that checkout concerning ternary models is authored
  by a different person and reports 1.1565 bits per byte for its best valid
  ternary result, not 0.9650.
- The only places the value 0.9650 was found anywhere in the account are two
  documents in gHashTag/trinity-fpga, neither about this challenge: a training
  loss in a report where the same table annotates the run as having been made
  worse by refinement, and an arithmetic coincidence in an unrelated document,
  where 94 divided by pi to the fourth power evaluates to 0.9650. Neither is a
  bits-per-byte score, and a training loss and a compression metric are not
  interchangeable.

Artefact search completed 2026-07-29 with account access. Five submissions to the
challenge exist and were found. None of them reports 0.9650.

| Submission | Reported score | State |
|---|---|---|
| Trinity v7+skip | 0.22311 | closed by the author |
| Trinity SLOT v3 + Pre-Quant TTT | 0.65802 | closed by the author |
| SP8192 + NN base + byte-PPM mixer | 0.99145 | closed by the author |
| Trinity Ternary CPU v3, non-record | 1.5042 | open, and below the baseline |
| Canonical top-stack reproduction | 1.05985 | open, and a reproduction of another entry |

So the claim is settled on its own terms: there is a real submission history, it
does not contain 0.9650, and it does not contain a top-five placement.

The reason the three strongest numbers are closed is the important part, and it
runs the other way from what an auditor usually finds. Each was withdrawn by the
author, with a stated technical reason: the first for violating the full-vocabulary
normalisation condition, the second and third in light of a public discussion about
per-byte versus per-token measurement bases. On the first, the author added a
retroactive note observing that a score that far below the Shannon-floor estimate
for the corpus is by itself proof that the metric was not measuring real lossless
compression. That is an author supplying the mathematical argument against their own
leading record and then acting on it.

Two consequences follow.

First, by the author's own published reasoning, any score materially below about
1.0 bits per byte on this corpus should be treated as an artefact of a broken
measurement rather than as a result. 0.9650 is below 1.0. The claim should not be
reinstated even if a run log turns up showing that number; what would need to turn
up is a run log plus a demonstration that the measurement condition holds.

Second, and this is the actionable part: the withdrawal history is a stronger
credential than the score ever was. A committee that reads applications all day
sees claimed records constantly and almost never sees someone retract their own
number-one result on a public leaderboard, in public, with the reasoning attached.
That is precisely the disposition this evidence ledger is meant to demonstrate, and
unlike the score, it is fully documented and checkable. It belongs in the
application. The score does not.

Why it is rated above W-INTL-17. W-INTL-17 is an unbuilt thing honestly described.
This is a built-sounding thing that a reviewer will try to verify and, on the
evidence available, will fail to verify. The asymmetry matters: an application
that under-claims survives scrutiny, and one superlative that does not check out
puts every other figure in the document under suspicion, including the ones that
are solid - and E1 through E3 are solid.

Action, revised after the artefact search.

1. Remove the score claim permanently rather than pending an artefact. The search
   is complete and the account's own submission history settles it.
2. Replace it with the withdrawal record, which is verifiable and stronger:
   submissions made to a public challenge, three of them retracted by the author
   on stated technical grounds, including a leading record retracted with the
   argument for why the measurement was invalid.
3. Leave the compute story resting on the ternary tile and the numeric catalog.
   Both have artefacts, and the tile has now been reproduced by execution.

Closes when the score appears in no external document and the withdrawal record
appears in the application.

## W-INTL-29  A modelling parameter was published as a hardware measurement

Severity: critical. Same class as W-INTL-28 and found the same way, but this one
is settled rather than merely unsupported.

The claim. An inference core running at 309 MHz on Artix-7, recorded at the
strongest evidence level available, with a timing report named as its artefact.

What was found on 2026-07-29.

- The project's own comparison document states, in its list of honest
  limitations, that all cell counts come from yosys and not from a vendor flow,
  and that there is no timing or Fmax data.
- The synthesis bench notes record place and route as blocked on a toolchain
  problem, list extracting Fmax from a timing report as an outstanding task that
  blocks completion, and instruct the author to document honestly that place and
  route was not run.
- The number 309 appears in the performance model as one of three clock values
  swept for a projection, alongside 50 and 150. The same model uses 150 MHz, not
  309, when it states a compute ceiling.
- Synthesis without place and route cannot produce an Fmax. The named artefact
  therefore cannot exist in the state the repositories describe.

The finding is not that the number is implausible. It is that a swept parameter
in a projection was promoted to a measurement, and an artefact was named for it
that the project's own notes say does not exist.

What makes this worse than an ordinary overstatement: the underlying documents
are honest. The performance model marks every projected figure as an estimate and
states in its own output that the throughput figure is a ceiling and not a
benchmark. The overstatement was introduced downstream of careful work.

Action. Taken in part: the figure has been removed from the application, and the
ledger row is now recorded as refuted with the reason. Remaining: either complete
place and route and publish a real Fmax, or state a clock only as a projection
with its assumption attached. Closes when no external document states a frequency
without saying whether it was measured or assumed.

Counterweight, recorded here because the same pass produced it. The ternary tile
claim was tested by execution rather than by reading, and it held: the testbench
runs to 206 of 206 passing, and an independent Xilinx-targeted synthesis emits no
DSP primitive. That claim is now stronger than it was, by the same method that
refuted the frequency. The method is not biased toward negative findings.

## W-INTL-30  Two tokens exist and the superseded one is easier to find  [CORRECTED 2026-07-29]

Severity: medium. The original entry rated this critical and was substantially
wrong. The correction is recorded in full because the error is instructive.

What this entry claimed. That the allocation claim - no premine, no venture
allocation, no treasury - was refuted by a deployed contract carrying a 20 percent
founder share and a 10 percent treasury share, and that no settlement contract
existed to point at instead.

What is actually true. The claim holds, of the instrument it describes.
gHashTag/trinity-contracts is public and contains TriToken, MiningPool,
EmissionController, ChipRegistry and JobProver, all deployed to Base Sepolia on
2026-05-18 with addresses and deploy transactions recorded. TriToken mints its
entire supply to MiningPool in the constructor and renounces ownership in the same
transaction: there is no allocation mechanism to any founder, investor, treasury
or liquidity address, and the supply cannot be inflated afterwards. That is a
stronger form of the claim than the one the application was making.

How the error happened, since the method is the point of this file. The search
that concluded absence was `deploy/contracts/src` in one repository plus a code
search for contracts named for rewards, proofs or settlement. The first is the
wrong directory and the second returned nothing because the settlement contract is
called MiningPool. Absence was then reported with confidence, and two ledger rows
were downgraded on it. The repository was linked from the mesh roadmap the whole
time. Concluding absence from a failed search is the exact failure this audit
exists to catch, and it went uncaught for three passes.

What survives, and it is real. Two tokens exist under this project. The superseded
one, TrinityToken on Ethereum Sepolia from February 2026, does carry a founder and
treasury split, and it is still public. A reviewer searching for the project's
token may find that one first and conclude the allocation claim is false, exactly
as this audit did. The risk is not that the claim is wrong; it is that the
disproof is easier to find than the proof.

Action.

1. Name the instrument explicitly wherever the economics are described - contract
   names, chain, addresses - so the right artefact is the one a reader reaches.
2. Say plainly that the February token is superseded. Pointing at it is cheaper
   than being shown it.
3. Consider marking the old repository's contract directory as superseded, since
   a deprecation note costs nothing and removes the ambiguity at source.

Closes when the application names the deployed instrument by address and the
superseded one is labelled as such.

## W-INTL-31  The register bank admits twenty-seven proof types, not four

Severity: low, but it is a discrepancy between a contract and every document
describing it.

MiningPool defines MAX_REGISTER as 26, so proof types 0 to 26 are accepted, and
the named constants visible include a zero-knowledge job register and a Bittensor
register. Every external document describes four proof types: transport,
coverage, sensing and inference.

Both may be true - four registers used out of a bank of twenty-seven - but no
document says so, and a reader who opens the contract finds a wider surface than
the prose implies.

Action: state which registers are in use and that the bank is larger. Closes when
the mapping from the four named arms to their register indices is written down.

## W-INTL-32  Four claims in this audit were false, all from the same method error

Severity: high, and it is a finding about this document rather than about the
project.

On 2026-07-29 four separate conclusions in this audit turned out to be wrong. Each
was an assertion of absence, and each came from a search that failed rather than
from a thing that was missing.

| Claim made here | What is actually true |
|---|---|
| No settlement contract exists | gHashTag/trinity-contracts holds MiningPool, EmissionController, ChipRegistry, JobProver and TriToken, deployed to Base Sepolia with recorded addresses |
| The allocation claim is refuted by a deployed token | TriToken mints its whole supply to MiningPool and renounces ownership; the token that carries a founder split is a superseded one |
| The figure of 4,463 lines of Rust matches nothing visible | tri-net's src directory is 4,370 lines once blanks and comment-only lines are excluded, which is the convention such a figure normally uses |
| The v1 weakness audit was never written | it exists as a Russian-language registry of W1 to W18 in gHashTag/trinity-papers-ru |

The common shape. In every case a search was run, returned nothing, and the
nothing was reported as a fact. The searches failed for ordinary reasons: the
wrong directory, a contract named MiningPool rather than anything containing the
word settlement, a line count taken raw when the claim used source lines, and a
repository name searched for when the content was a directory inside another
repository.

Why it matters more than the individual corrections. This audit's authority rests
on the idea that a claim without a locatable artefact should be distrusted. That
principle is sound, but it silently assumes the search was competent. Four times
it was not, and the resulting false negatives were stated with the same confidence
as the true ones. A reader had no way to tell which was which.

Standing rule adopted from this. An assertion of absence must record how the
search was run, so a reader can judge whether it was capable of finding the thing.
Where that record is missing from an earlier entry, the entry states absence
weakly - not found by this method - rather than as fact.

Directly affected and already corrected: W-INTL-30, and ledger rows E21, E22, E23.
Re-examined since: W-INTL-29, whose absence claim was too strong and is corrected
above; the finding survived and improved. Still resting on absence: E20 on the
energy derivation, searched across the account under five formulations on
2026-07-29 with no result. That is recorded as not found by this method rather
than as fact.

## Predecessor registry, and what it already knew

Located 2026-07-29 in gHashTag/trinity-papers-ru, at
`paper3-rossiya30-troica/research/weak_spots_registry.md`. It is Russian-language
and runs W1 to W28, not W1 to W15 as the numbering here assumed. Several of its
entries anticipate findings this addendum arrived at independently, which is worth
recording because it means the project had already identified them and this
document duplicated the work.

| Predecessor | Says | Relation to this addendum |
|---|---|---|
| W1 | silicon not measured; all energy-efficiency figures are projections | anticipates E16 and E20 |
| W3 | advantage over posit and MX formats not proven | carried forward as W-INTL-36, where a measurement now runs against it |
| W6 | export control and foreign fabrication left unsaid | anticipates W-INTL-24 and the shuttle-tile question in W-INTL-18 |
| W15 | single author, bus factor not addressed | is W-INTL-25 |
| W16, W21, W26 | verifiability-per-dollar not operationalised in numbers | carried forward as W-INTL-37 |
| W17 | competitive landscape not shown | answered by the competitor matrix |
| W20 | reproducibility without an artefact protocol | answered in part: two claims are now reproducible by command |
| W25 | verifiable arithmetic is not verifiable inference - hallucination and adversarial behaviour sit above the arithmetic | carried forward and answered as W-INTL-33 |
| W28 | ternary energy efficiency is a 49x projection with no mechanism | see below |

Two consequences.

W25 has been carried into the international edition and answered as W-INTL-33. It
was a threat to the thesis rather than to a claim, and it deserved an answer
rather than a hedge.

W28 changes the energy picture. The naive energy figure has now been stated as at
least four different values across the project's own documents: 49x in this
registry, 20x from a picojoule division, 10 to 20x in the same document's opening,
and 20 to 30x from a second pair of figures in it. The honest figure of 4x to 8x
is quoted against a naive number that does not have one value. Hard rule 7 asks
for the naive and honest calculations to be paired; pairing requires the naive one
to be singular first.

## W-INTL-33  Verifiable arithmetic is not verifiable inference  [ANSWERED 2026-07-29]

Severity when opened: the highest in either registry, because it threatens the
thesis rather than a claim. Carried forward from the predecessor registry, entry
W25, where it had been raised and left unanswered.

The objection. Proving that arithmetic executed correctly says nothing about
whether the model's output is true. Hallucination and adversarial behaviour sit
above the arithmetic, so an application selling verifiable AI compute may be
selling a guarantee that does not reach the thing a buyer cares about.

The objection is correct, and the answer is not to deny it.

Answer, part one: concede the scope. Execution verification does not make output
true, unbiased or non-hallucinated. Those are properties of the model and are
addressed by evaluation. Any document of ours implying otherwise is wrong and
should be corrected.

Answer, part two: the conceded part is not where the money is. An operator paid to
run inference gains nothing by faking a matrix multiply - it is expensive to fake
and cheap to check. The profitable attacks are at the edges: substitute a smaller
model and bill for the larger, tamper with the input, alter the sampling policy,
or return a cached answer without computing. The zero-knowledge literature on
verifiable inference makes this point against itself, noting that proving the
forward pass over an unverified model identity and unverified input establishes
very little. See the survey literature on zero-knowledge verifiable machine
learning and the recent work on agent-execution transcripts, IACR eprint 2026/199.

Answer, part three: that is the gap this design addresses, and it addresses it
without a vendor enclave. Device identity binds the work to a specific piece of
hardware. A nullifier makes each claim single-use. Sampled re-execution with stake
forfeiture makes substitution unprofitable rather than impossible. The result is
assurance with published parameters, not a cryptographic absolute.

Why this strengthens rather than weakens the position. The field's own critique of
zero-knowledge inference is that the hard cryptography is aimed at the attack
nobody is running, while identity and input integrity - the attacks that pay - are
left assumed. A design that starts from identity and economics is aimed at the
right target, and can say so with a citation rather than an assertion.

Residual, addressed 2026-07-29. Sampled re-execution assumes the work can be
re-run and compared. That assumption holds for three of the four arms and not for
the fourth, and the honest design consequence is to say so rather than to average
over it.

Transport, coverage and sensing are deterministic given their recorded inputs. A
packet count, a position and time, a spectrum snapshot: re-execution is a
comparison of recorded values against a re-derivation, and a mismatch is
unambiguous. Sampled re-execution works for these as written.

Inference is not deterministic in general. Temperature, sampling policy, batching
order and hardware reduction order all move the output. Comparing two runs
bit-for-bit will fail for honest operators, and comparing them loosely will pass
for dishonest ones. Three routes exist and the choice has to be made explicitly:

1. Pin determinism in the job specification. Temperature zero, a fixed seed, a
   fixed batch shape, a named reduction order. The job becomes reproducible by
   construction and re-execution compares exactly. The cost is that the network
   can only settle work whose caller accepts those constraints.
2. Compare distributions rather than tokens. Re-run and check that the returned
   logits lie within a tolerance of the re-derived ones. This admits sampling but
   requires the operator to return logits, and the tolerance becomes a parameter
   an adversary will probe.
3. Do not settle inference by re-execution at all. Use it for the three
   deterministic arms and settle inference against a different mechanism, which is
   where a proof system would earn its cost.

Recommendation is the first for now, because it is the only one that can be
specified today without new cryptography, and because a network that settles
deterministic jobs honestly is more useful than one that settles all jobs
ambiguously.

What must not happen is the current state: an economic assurance model quoted with
its sampling rate and stake multiple, applied to four arms, one of which cannot be
compared. The parameters are meaningless for that arm until the comparison rule
exists.

## W-INTL-34  Two of the five deployed contracts are scaffolds, and one of them is the identity root

Severity: high. Deploying scaffolds to a testnet for bring-up is ordinary
engineering. Describing the deployment as implementing device identity is not,
and the application was heading that way.

Found by reading the source on 2026-07-29 rather than the deployment record.

ChipRegistry does not verify anything. `registerChip` is external, has no access
control and no signature check. It takes a 32-byte key, a family in the range one
to three, and a value that must equal the contract's own public constant
PHI_ANCHOR. Anyone who has read the contract can supply all three. The contract's
own comment says the intended gate is an off-chain challenge and response, and
that this minimal registry does not implement it.

The consequence reaches MiningPool. Its settlement path checks that the submitting
chip is registered. That check passes for any key someone previously self-declared,
so it establishes that a registration transaction happened, not that hardware
exists. The device-identity property that the whole attestation argument rests on
is, in the deployed contracts, a bookkeeping entry.

JobProver cannot verify a proof either. Its Groth16 verifying key is a placeholder,
labelled as such in the source, with the first two constants set to 1 and 2. Those
are not the output of a trusted setup. The zero-knowledge proof register is
deployed and inert.

What this does not mean. The settlement logic is real and the checks around these
two - era matching, nullifier replay protection, register caps, supply that cannot
be inflated - work as written. The economics are further along than the audit
previously credited. But two of the five contracts are frames waiting for their
contents, and one of them is the one the thesis leans on.

Action.

1. Say which contracts are functional and which are bring-up scaffolds, in the
   application and in the repository README. A reviewer who opens ChipRegistry
   before being told will conclude something worse than the truth.
2. Do not describe device identity as implemented. It is designed, deployed as an
   interface, and not yet enforced.
3. Write the off-chain challenge and response, or state what gates registration in
   its absence. Until then MiningPool's chip check is a formality and should be
   described as one.

   Drafted gate, offered as a specification rather than as code. A signature check
   with a subtle error is a hole rather than a gate, so this should be reviewed and
   tested before it is written into a contract that holds the supply.

   > registerChip takes an additional signature over a message binding four
   > things: the chip public key, the registrant address, the registry's own
   > address, and a nonce the registry issues and consumes. The contract recovers
   > the signer from that signature and requires it to equal the chip public key
   > being registered. Binding the registrant prevents a captured signature being
   > replayed by a third party; binding the registry address prevents it being
   > replayed onto a different deployment; consuming the nonce prevents it being
   > replayed at all. The phi-anchor equality check is kept but demoted to a
   > format assertion, since a public constant cannot gate anything.
   >
   > This still only proves possession of a private key at registration time. It
   > does not prove the key lives on a die. Proving that needs the challenge to be
   > answered by the hardware under a timing or physical constraint, which is
   > W-INTL-21's territory and remains partial.

   The honest description while this is unbuilt: registration is open, and the
   security of the arms that settle rests on the nullifier, the register cap and
   sampled re-execution, not on chip identity.
4. Replace the placeholder verifying key before any external party is invited to
   submit a zero-knowledge proof.

Closes when each deployed contract is described at the level it actually operates,
and the identity gate either exists or is stated as absent.

## W-INTL-35  The deployed contracts are not source-verified on the explorer

Severity: high for a submission that leads with the economics, and the cheapest
item on this list to fix.

Checked 2026-07-29. The MiningPool address holds contract bytecode, is not an
externally owned account, and holds a balance matching the token's total supply
constant exactly, which corroborates the deployment record. The explorer also
shows the contract source is unverified and invites the creator to publish it.

Why it matters more than it looks. Everything this audit now says about the
economics rests on reading source in one place and a deployment record in another.
Nobody outside the project can confirm that the bytecode at that address was built
from that source. A reviewer who checks - and on a digital-assets track someone
will - finds an unverified contract holding 7.6 trillion tokens. The honest
explanation and the dishonest one look identical from outside.

Action: verify all five contracts on the explorer. The settings are already in
the repository's foundry configuration - solc 0.8.24, optimizer enabled at 200
runs, via_ir off - and the explorer endpoint is configured there too. With a
BASESCAN_API_KEY the command per contract is:

    forge verify-contract --chain base-sepolia \
        --compiler-version 0.8.24 --num-of-optimizations 200 \
        <address> src/<Name>.sol:<Name>

Constructor arguments are needed for TriToken, MiningPool and any contract taking
addresses; they are recoverable from the deploy transactions recorded in
deployments/base-sepolia.md.

This converts every economic claim in the application from trust-us to check-it,
and it is an afternoon.

Closes when each of the five addresses shows verified source matching the
repository.

## W-INTL-36  The format's advantage over established alternatives is not demonstrated, and one measurement runs against it

Severity: high for a submission whose numeric work is its published foundation.
Carried forward from predecessor entry W3, which recorded that advantage over
posit and microscaling formats was unproven. It is worse than unproven: there is
now a measurement pointing the other way.

The evidence, from this project's own ablation. In quantisation-aware training on
a 29.4M-parameter model over 2000 steps, three seeds, disjoint train and
validation shards, with a significance threshold of 0.005 BPB fixed in advance:

| Arm | Median BPB | Delta against FP32 |
|---|---|---|
| FP32 baseline | 2.8279 | - |
| FP8 E4M3 with per-row scaling | 2.8280 | +0.0001, below threshold |
| GoldenFloat 8-bit | 3.0474 | +0.2196, about 44x threshold |
| E2M5 | 3.0944 | +0.2666, about 53x threshold |

An industry-standard 8-bit format is indistinguishable from full precision in this
setting. The project's own 8-bit format is not. The ablation also records the
mechanism hypothesis - that a narrow exponent range restricts weight dynamics
under straight-through estimation, so range matters more than grid density during
training - and marks it as hypothesis rather than result.

Why this is not fatal, and how it should be said. The catalog's stated purpose is
registry filling rather than superiority: a vendor-neutral reference with
bit-exact conformance vectors. That claim is intact and is supported by the
83-format single source of truth. The format family is a separate claim, and on
the one controlled comparison available it loses at 8 bits during training.

The application currently avoids claiming format superiority, which is correct.
The risk is a reviewer inferring it from the prominence the numeric work is given.

Action.

1. Never claim the format beats posit or microscaling formats. On the evidence
   available it does not, at 8 bits, in training.
2. Lead the numeric work as a registry contribution, which is what it is and what
   the preprint says.
3. Publish the negative result rather than leaving it in a research directory. It
   is already written, already controlled, and disclosing it is worth more than
   the claim it costs.
4. If the ternary case is where the advantage lives, run the same ablation there.
   The 8-bit result says nothing about 1.58-bit weights either way.

Closes when the external documents state the registry claim and no superiority
claim, and when a ternary ablation exists or its absence is stated.

## W-INTL-37  The central metric is named but never computed  [PARTLY CLOSED 2026-07-29]

Severity: medium, rising the moment anyone asks for a number.

Carried forward from predecessor entries W16, W21 and W26, which recorded across
two review passes that verifiability-per-dollar is asserted as the organising
metric and never operationalised. Neither this addendum nor the application has
improved on that.

The thesis is that a buyer should be able to obtain verification per unit of
spend, and that this project offers more of it per dollar than a trusted-execution
alternative. No document defines the numerator, the denominator, or a single
worked example.

What would close it, and it is an afternoon of arithmetic rather than research.
Define one unit of verified work - a settled proof of a stated type. Define its
cost - node amortisation, energy, and the sampling overhead at the published one
percent with stake at one hundred times the unit reward. Then state the same for
the alternative being displaced, which is a trusted execution environment on
rented hardware. The comparison does not need to be favourable to be worth
publishing; it needs to exist, because a metric quoted without a number reads as
a slogan and the predecessor registry says so in three separate entries.

Action: compute it once, publish the working, and let the figure be what it is.

Done in part, at research/verifiability_per_dollar.md. What the computation
produced:

- An attested node-hour costs about 0.025 USD, from a hardware listing midpoint
  amortised over three years plus energy at a mid industrial rate. The range
  across the listing is 0.017 to 0.033.
- The attestation premium alone on a small confidential cloud instance is about
  0.021 USD per hour, on top of the instance.
- So the rented price of the attestation property is within the same order as the
  owned price of the whole device providing it. That is the comparison that
  survives, and it is narrower than the metric it replaces.

What the computation could not produce, and this is the finding. The composite
metric needs a unit of verified work priced in currency. No document defines one.
The assurance parameters are published as ratios - one percent sampling, one
hundred times stake - and a ratio cannot be costed. The carrying cost of stake,
which is the only economically significant term in the overhead, therefore has no
value.

Two consequences. The metric must not be quoted as though a number stood behind
it until the unit exists. And the price comparison above compares against an
attestation this project does not yet enforce, per W-INTL-34, so it should be
re-run once the identity gate is real.

Remaining to close: define one unit of verified work with its compute content and
its price.

---

## Priority order

2. W-INTL-29  settled: a projection was published as a measurement
3. W-INTL-28  a reviewer checks it first and, on present evidence, it fails
4. W-INTL-27  everything else is scheduled against it; partly closed, one decision left
5. W-INTL-17  blocks the economics entirely
6. W-INTL-23  largest credibility gain, hardware already present
7. W-INTL-25  requires a third party, so start earliest
8. W-INTL-26  cheap, high visibility, partly closed
9. W-INTL-18  vocabulary discipline, no artefact change required

W-INTL-16 was third in the previous order and is now closed; see its entry above.

## Status at 2026-07-29

| Entry | State |
|---|---|
| W-INTL-16 | closed, verified |
| W-INTL-17 | open, formulation drafted, decision required |
| W-INTL-18 | revised, severity lowered, restated |
| W-INTL-19 | revised, severity raised; both tiers have published attacks |
| W-INTL-20 .. W-INTL-22 | open, unchanged |
| W-INTL-23 | open, hardware present, gate not run |
| W-INTL-24 | open, unchanged |
| W-INTL-25 | open, requires a third party |
| W-INTL-26 | closed, all links resolve anonymously |
| W-INTL-27 | partly closed, host programme still to choose |
| W-INTL-28 | closed by artefact search; score removed, withdrawal record substituted |
| W-INTL-29 | open, critical, refuted as stated; figure removed from the application |
| W-INTL-30 | corrected; the claim holds and this entry was wrong |
| W-INTL-31 | open, low; register bank wider than the prose |
| W-INTL-32 | open, high; four false negatives from failed searches, method rule adopted |
| W-INTL-33 | answered; scope conceded, target defended, one residual open |
| W-INTL-34 | open, high; identity registry and proof verifier are deployed scaffolds |
| W-INTL-35 | open, high, cheap; deployed contracts not source-verified on the explorer |
| W-INTL-36 | open, high; format advantage unproven and one measurement runs against it |
| W-INTL-37 | partly closed; computed as far as the missing unit price allows |
