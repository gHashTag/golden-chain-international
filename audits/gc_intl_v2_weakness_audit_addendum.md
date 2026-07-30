# Weakness Audit Addendum: W-INTL-16 .. W-INTL-168

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

REOPENED then re-settled. This entry has now been rated high, medium, high and
medium again, and the sequence is more instructive than any of the ratings.

First rating, high: a public file carries a fabrication date and the funding position
behind it has changed. Written without naming the file.

Second, medium: inspection of tt-trinity-gamma found a status table marking tape-out
as submitted and awaiting fabrication, with an explicit rule for closing the row.
Careful reporting. The entry was lowered on that basis.

Third, high: the DePIN daemon README carries, in a warning block, a scheduled hardware
tape-out date of 2026-12-16. So the date existed after all and the lowering had been
done by inspecting one repository and concluding about the account.

Fourth, medium, and this time on a systematic search rather than a sample. Fifteen
repository READMEs were fetched and searched directly, because the account-wide code
search does not index the file where the date was found - it returns nothing for the
phrase that is demonstrably in it, which makes it the wrong instrument for this
question and is recorded as such.

What that search found. The date appears in three places, not one: twice in the
DePIN daemon README and twice in the mesh README. A fourth repository carries a
different date, 2026-05-17, described as the day a tile was submitted to the open
shuttle - which is correct reporting of a submission rather than a fabrication.

And the date is benign in kind. TTSKY26b was submitted in May. December is when that
shuttle's parts are expected back. It is the shuttle programme's delivery schedule for
a tile already sent, not a fabrication the project has committed to fund. The original
concern - that the funding position behind the date has changed - does not apply,
because no funding stands behind a submission that already happened.

Two things remain, and they are smaller than high severity.

The wording is loose. Calling it a scheduled tape-out reads as a future commitment
when the tape-out already occurred in May; December is delivery. And the DePIN daemon
presents the date in a warning block without saying whose schedule it is, while the
mesh README does better - it marks the associated performance figure projected and
tags the dependent claim as an open conjecture.

So the finding is now about vocabulary, which is where this entry started, rather than
about an unfunded promise.

Action.

1. Use two distinct terms in every external document - shuttle tile for the Tiny
   Tapeout work, custom die for the funded path - and never let a claim about one
   carry over to the other.
2. Say whose schedule the December date is. It is the open shuttle's delivery date
   for a tile submitted in May, and describing it as a scheduled tape-out invites the
   reading that the project has committed to fund a fabrication run.
3. Re-audit done 2026-07-30 across fifteen repository READMEs, fetched and searched
   directly because the account-wide code search does not index the file the date was
   found in. Three occurrences of the December date, one correctly-reported May
   submission date, nothing else.

Closes when no external document uses an unqualified silicon to span both, and no
public document carries a fabrication date without its funding position stated.

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

Confirmed and refined against the vendor manual on 2026-07-30, UG470, the 7 Series
Configuration User Guide, read as a fetched document rather than at search depth.
Its exact wording:

  Each device is programmed with a 57-bit DNA value that is most often unique.
  However, up to 32 devices within the family can contain the same DNA value.

  The JTAG FUSE_DNA command can be used to read the entire 64-bit value that is
  always unique.

So the original finding holds and the picture is sharper than it recorded. There
are two identifiers, not one:

The 57-bit Device DNA is what a design running inside the fabric can reach, through
the DNA_PORT primitive. It is the one that may be shared by up to thirty-two parts.

The 64-bit FUSE_DNA is always unique. It is reachable only through the JTAG port,
by an external application - the manual states the split explicitly: external
applications can read either value over JTAG, and FPGA designs can access the DNA
only through DNA_PORT.

That is the identity problem in one sentence. A running node can self-report only
the possibly-shared value. The unique one requires an external tool on the JTAG
port, which is not something a deployed node has. And the readable side is not
merely readable by an attacker with physical access - the vendor's own programming
software reads it as a documented feature.

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

Reframed 2026-07-30 against the literature, see research/attestation_prior_art.md.

The refutation recorded above is a category result rather than a bad experiment.
Software-only remote attestation is a recognised family and the surveys
characterise it as resting on stringent timing constraints or on the absence of
free memory in which to hide code. Both dependencies are assumptions about the
adversary's hardware, and both fail the moment the adversary has better hardware -
which is exactly how this one failed here, to an optimised software implementation
on a faster machine.

So the finding is stronger than it read. It is not that a timing challenge was
tried and did not work; it is that the software-only family was tested against its
known dependency and the dependency does not hold for this device class. That is
worth saying in those terms, because the first version invites the reply that a
better challenge might work, and the second explains why it would not.

Action: do not claim that a timing challenge proves hardware class. Use it as
supporting evidence against casual emulation only. Identity carries the claim, and
the literature's stronger families - a key reconstructed from a physical function
rather than stored, and an immutable attestation routine so the code using it
cannot be swapped - are where the identity work should go next.

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
PHI_ANCHOR. Anyone who has read the contract can supply all three.

Stated more precisely than this entry first did, on rereading the source on
2026-07-30. The contract does not merely omit the gate; its documentation says the
omission is deliberate, that the intended gate is an off-chain challenge and
response verified against a separate attestor contract, and that this registry
"exposes the gate-free path for Sepolia testnet". That is a labelled decision for a
testnet rather than an oversight, and the entry should have said so. What remains
true, and is the finding: MiningPool's chip check is described externally as
device identity, and on this deployment it is not one.

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

   Written 2026-07-30 as ChipRegistryV2 in gHashTag/trinity-contracts, with tests,
   on a branch and not merged. It cannot be retrofitted here: MiningPool's
   ownership was renounced at deployment, so the registry it consults can never be
   replaced. It targets the next deployment.

   The specification it implements, kept here because the reasoning is the part
   worth reviewing:

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

   What the implementation proves: whoever registered an identifier held the key
   that identifier is derived from, at registration, for that registry, on that
   chain, once. What it does not prove: that the key lives on a die rather than in
   a file. No on-chain check establishes that.

   The literature's answer to that, recorded in research/attestation_prior_art.md,
   is not to protect a stored key but to have none: reconstruct the signing key
   from a physical function at the moment of use, so there is nothing at rest to
   extract. That is also what this project's own registry documentation already
   assumes, since it describes the identifier as derived from an on-die function.
   The design assumes the stronger family and the implementation does not yet
   reach it. Paired with it in the same literature is an immutable attestation
   routine, which matters specifically on parts whose code lives in external flash
   - both of these do.

   So the floor rises from "anyone may claim to be any chip" to "only the holder of
   a chip's key may register that chip". That is the whole claim.

   Until it is deployed the honest description is unchanged: registration is open,
   and the security of the arms that settle rests on the nullifier, the register cap
   and sampled re-execution, not on chip identity.
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

Prepared 2026-07-30. scripts/verify_contracts.sh carries everything except the
key. The compiler settings come from the repository's foundry configuration -
solc 0.8.24, optimizer at 200 runs - and the addresses and constructor arguments
come from the recorded deployment broadcast rather than from memory, so they are
the values actually used:

| Contract | Constructor arguments |
|---|---|
| ChipRegistry | none |
| JobProver | none |
| EmissionController | genesis 1779117650 |
| MiningPool | TriToken address, ChipRegistry address, genesis 1779117650 |
| TriToken | MiningPool address |

Worth knowing before reading those: the last two name each other. MiningPool was
deployed against TriToken's predicted address and TriToken then received
MiningPool's. That is ordinary with a deterministic deployment and it is the kind
of thing that looks alarming if discovered rather than stated.

The script refuses to run without an API key and refuses to run outside a
checkout of the contracts repository, because a bytecode mismatch from the wrong
checkout is the failure mode that wastes the most time. The broadcast record
names commit b8410a0.

Closes when each of the five addresses shows verified source matching the
repository.

## W-INTL-36  The format's advantage over established alternatives is not demonstrated, and one measurement runs against it

Severity: high for a submission whose numeric work is its published foundation.
Carried forward from predecessor entry W3, which recorded that advantage over
posit and microscaling formats was unproven. It is worse than unproven: there is
now a measurement pointing the other way.

RETRACTED 2026-07-30. The measurement this entry rested on is an artefact of a
defective implementation, and the direction of the result reverses when the defect
is removed. See W-INTL-40, which now carries the measurement. This entry is left
in place rather than deleted because it was acted on: the application was rewritten
around it, and the record of that being wrong is worth more than a clean file.

What survives of it: do not claim superiority on the strength of one reconstruction
benchmark either. The correct statement is that the format has not been shown to
lose, and the reason it appeared to lose is now understood.

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

## W-INTL-38  The deployment has never been used

Severity: medium for the technical case, high for the wording around it.

Checked on the block explorer 2026-07-29, 72 days after deployment. ChipRegistry
and JobProver each show zero transactions and zero balance. No chip has ever been
registered. No proof has ever been submitted. MiningPool holds the entire token
supply, which is the state it is left in by deployment rather than evidence of
activity.

So the five contracts are a bring-up, not a running network. That is a perfectly
ordinary state for a testnet deployment two months old, and nothing in the design
is contradicted by it. What it does contradict is any phrasing that lets a reader
infer operation from deployment.

This sharpens W-INTL-34 rather than duplicating it. That entry found the identity
gate is not enforced. This one finds it has also never been exercised - the
scaffold is not merely permissive, it is untouched. A registry that has accepted
zero registrations has not been tested against even the weak check it does have.

Consequences for wording.

Three proof types are said to operate today. They are produced by the node daemon;
nothing settles them, and nothing has ever tried. The application now says
produced rather than settled, which is right, and this entry is the evidence for
why that distinction was necessary rather than pedantic.

Any figure derived from network operation - throughput, operator earnings, uptime
- has no observations behind it and must not appear.

Action.

1. Submit one proof end to end on the testnet. It exercises the settlement path,
   produces the first real transaction, and turns deployed into demonstrated. The
   contracts are already there; this is an afternoon.
2. Until then, describe the deployment as what it is: written, deployed, and
   unexercised.
3. Record the first settled transaction hash when it exists. It is the single
   cheapest piece of third-party-verifiable evidence available to this project.

Closes when at least one proof has settled on chain and its transaction is cited.

## W-INTL-39  The radio figure is labelled as a signal-to-noise ratio and is not one

Severity: high with a radio-literate reviewer, low with anyone else, which is the
worst combination: it survives casual reading and fails expert reading.

Found by opening the analysis script rather than the result it produced.

What the number is. The script captures interleaved integer IQ, windows it,
transforms it, and computes the reported figure as the magnitude of the peak bin
minus the median of the entire magnitude spectrum, in decibels. The capture is
taken through the transceiver's internal digital loopback, which the bring-up
script states explicitly: transmit to receive, nothing radiated.

Why that is not a signal-to-noise ratio. With no radio path there is no thermal
noise. The median of the spectrum is the numerical floor of the transform, the
quantisation floor of the integer capture, and window leakage. A guard term is
added inside the logarithm to avoid negative infinity on empty bins, which sets
how deep that floor can appear. So 108.6 dB is the spectral dynamic range of a
clean digital path, and it would move if the window, the capture length or the
guard term changed - none of which are properties of a radio.

Why it matters. The documents already say digital loopback and not over the air,
which is honest about the path. They are not honest about the quantity. A reader
who knows radio will read 108.6 dB over the noise floor as a receiver figure,
where it would be extraordinary, and will then discover it is peak-to-median of a
noiseless loopback. The gap between those two readings is where credibility is
lost, and it is lost with exactly the reviewer best placed to judge the rest of
the work.

What the measurement does establish, and it is worth keeping. The transmit chain,
the digital loopback path and the receive chain carry a single-sideband tone at
the commanded offset with no visible image, at the commanded local oscillator
frequency. That is a real bring-up result and the right thing to claim.

Action.

1. Rename the quantity. Peak-to-median spectral dynamic range, digital loopback.
   Not SNR.
2. State the tone placement as the result, since that is what the capture proves:
   commanded 1 MHz, observed +0.999 MHz, clean quadrature.
3. Keep the figure if it is useful as a path-integrity check, with its definition
   attached.
4. Do not compare it with any published receiver sensitivity or link budget.

Closes when no external document calls this figure a signal-to-noise ratio.

## W-INTL-40  The ablation that disfavours our own format may be biased against it

Severity: medium, and it runs the opposite way from every other entry in this
file. Recorded with the same weight regardless.

W-INTL-36 reports that the project's 8-bit format lost a controlled comparison
against an industry-standard one. Reading the ablation source rather than its
result shows the comparison is not symmetric, and the asymmetry disadvantages the
project's own arm.

All three quantised arms share the same per-row absolute-maximum scaling, which is
fair. What differs is how the format itself is applied.

The reference arm casts to a native 8-bit floating-point type provided by the
framework. That cast does correct round-to-nearest-even and handles subnormal
values in hardware or in a tested library path.

The project's arm and the third arm are hand-rolled emulations built from a
floor-of-log2, a mantissa rounded on a fixed grid, an exponent clamped into range,
and a flush of small magnitudes to zero. Two consequences follow that the native
cast does not suffer.

First, on saturation the exponent is clamped while the mantissa is computed from
the unclamped exponent, so the reconstructed value no longer corresponds to either.
A correct implementation saturates to the format maximum; this one produces a value
that is neither the input nor the saturated representable.

Second, there are no subnormals. Magnitudes below the smallest normal are set to
zero, while the reference format represents them. Near zero is exactly where
weights concentrate, and straight-through training is sensitive there.

So part of the reported degradation may be emulation error rather than format
error, and the size of that part is unknown because it has not been separated.

This does not overturn W-INTL-36. The result may survive a correct implementation,
and the mechanism hypothesis offered in the ablation - that a narrow exponent range
restricts weight dynamics during training - is plausible and independent of the
defects above. What it does mean is that the negative result is not yet safe to
lean on in either direction.

Also noted, and it is sound. The run carries an anomaly gate that quarantines
results below a floor, added after an earlier data-leakage bug produced an
impossible score. The gate can only discard implausibly good results, which is the
conservative direction, and its existence is disclosed in the published record.

Measured 2026-07-30, research/quantiser_emulation_check.py. Deriving the format's
geometry from the ablation's own constants exposed a third defect, larger than the
two this entry opened with.

The defect is an internal inconsistency rather than a wrong constant, and getting
this right took two attempts.

First reading, and it was wrong. The catalog records gf8 as sign 1, exponent 3,
mantissa 4, bias 3, status verified. Reading that in the IEEE convention - highest
exponent field reserved for infinities - gives a largest representable value of
15.5, against which the ablation's scaling target of 31 looks like a factor of two
error. That is what this entry said.

Second reading, after checking the project's other quantiser. It uses the fn
convention, where the highest exponent field is an ordinary normal and there are
no infinities, exactly as the reference format e4m3fn does. Under fn the largest
representable value is 31.0, and its source comments say so. So 31 is not wrong;
it is the fn reading, and it is the consistent choice given the reference arm.

What is actually wrong. The ablation scales to the fn maximum of 31 while clamping
the exponent field to the IEEE range, one to six. Two conventions in one function.
Everything between 15.5 and 31 is therefore scaled into existence and then clamped
away, so each row's largest weights saturate. Add the mantissa reconstructed from
the unclamped exponent, and the subnormals dropped - the MV constant is exactly the
format's smallest subnormal under either convention, so they were designed in.

Checked for convention dependence, because the first reading was wrong about
exactly that. A correct implementation was measured under both conventions and the
results are indistinguishable: 0.01314 against 0.01314 on normal input, 0.02061
against 0.02075 on t-distributed. Per-row absolute-maximum scaling normalises to
whatever the format maximum is, so the choice cancels. The conclusion below does
not depend on which convention is intended, which makes it stronger than when this
entry claimed a factor-of-two error.

The same tensors quantised through four paths, three input distributions, 512 by
512, one seed:

| Path | rmse, normal | rmse, heavy tail | rmse, t-distributed |
|---|---|---|---|
| Reference native cast | 0.0264 | 0.0704 | 0.0415 |
| Project arm as written | 0.3281 | 0.8705 | 0.5604 |
| Scaling target repaired only | 0.0170 | 0.0456 | 0.2309 |
| Correct implementation | 0.0131 | 0.0351 | 0.0210 |

The result reverses. A correct implementation of the format reconstructs about
twice as accurately as the reference cast on every distribution tested. The arm as
written is roughly twenty-five times worse than the same format implemented
correctly.

So the ablation did not measure the format. It measured an implementation that
saturates every row by construction, and the conclusion drawn from it - recorded
here as W-INTL-36 and repeated in the application - was wrong.

Why the correct implementation wins, stated so the result is not over-read. The
reference format spends four bits on exponent and three on mantissa; this one
spends three and four. Per-row absolute-maximum scaling normalises dynamic range
away, which is precisely the condition under which the extra mantissa bit pays and
the extra exponent bit does not. On data whose range survives scaling the ordering
would reverse. This is a result about weight tensors under per-row scaling, not
about the two formats in general, and it must not be quoted as the latter.

Scope limit, unchanged and now more important. Reconstruction error is not
training outcome. Straight-through training can behave differently from static
reconstruction, and the ablation's own mechanism hypothesis - that narrow exponent
range restricts weight dynamics - is about training rather than reconstruction and
is untouched by this measurement. The re-run is now necessary rather than merely
advisable, because the published negative result rests on a defect.

Action.

1. Separate emulation error from format error. Done: essentially all of the gap is
   emulation, and the result holds under either format convention.
2. Fix the saturation path so the mantissa is recomputed from the clamped
   exponent, and decide explicitly whether the format has subnormals.
3. Re-run the arm afterwards. Until then W-INTL-36 should say the format lost a
   comparison whose implementation was not symmetric, which is a weaker and truer
   statement.

2. Fix the convention mismatch first. Either scale to 31 and let the exponent
   field reach 7, or scale to 15.5 and clamp at 6. Both work; mixing them does not.
3. Re-run the ablation. The published negative result about this format is not
   safe and should be marked as under revision until the re-run exists.
4. Do not replace it with a positive claim on the strength of this measurement.
   Reconstruction is not training, and the tradeoff explanation above bounds what
   the result can mean.

Closes when the arm is re-run with the corrected implementation and the published
result is updated in whichever direction the re-run lands.

## W-INTL-41  A catalog entry marked verified cites an archive that does not contain the result

Severity: high. It is in the single source of truth, it carries a verified status,
and the artefact it names is one click away from any reviewer.

The gf16 entry in specs/numeric/formats_catalog.t27 reads, in its standard field,
that the format is verified with FPGA results of 35 out of 35 at 323 MHz on
Artix-7, and cites a persistent identifier described as a hardware archive.

Fetched 2026-07-30. The record behind that identifier is a two-kilobyte software
description stub about vector-symbolic operations over balanced-ternary
hypervectors. It contains one markdown file. It reports no FPGA frequency, no
timing figure, no device, and no hardware results of any kind.

So a frequency claim carrying verified status in the catalog names an archive that
does not support it. Whether 323 MHz was measured is not established either way by
this; what is established is that the artefact cited for it is the wrong one.

This is the same defect as W-INTL-29, which found a 309 MHz claim recorded at the
strongest evidence level against a timing report that does not exist. That one was
in a downstream document. This one is in the file every other document defers to,
and it is marked verified.

Action.

1. Establish whether a timing report for gf16 on Artix-7 exists. If it does, cite
   it. The 35 of 35 conformance figure and the frequency are separable claims and
   should be cited separately.
2. If it does not, remove the frequency from the standard field and reduce the
   status. A conformance pass is a conformance pass; it is not a clock rate.
3. Audit the other verified entries for the same pattern. This one was found by
   following a link, which is not a method that scales by hand.

Closes when the entry cites an artefact that contains the result it asserts.

## W-INTL-42  Two catalog entries carry a corrupted bias  [RETRACTED 2026-07-30]

Severity: none. The finding was withdrawn on the day it was raised. It is kept
here at zero severity rather than deleted, because it was published and the record
of it being wrong is the useful part.

The entry was wrong. The catalog is correct and the defect was in the check.

What was reported: that gf512 and gf1024 record a bias of 2 where the field rule
gives 2^194-1 and 2^390-1, and that a published erratum had identified the cause
without the catalog being repaired.

What is actually there: `bias=2^194-1` and `bias=2^390-1`, written as expressions
precisely because the values exceed a 64-bit integer, which is exactly what the
erratum said the repaired generator would do. The generator was fixed and so was
the catalog. The hand check that reported otherwise extracted the value with a
digits-only pattern, which kept the leading 2 of the expression and discarded the
rest.

So the finding was an artefact of reading the file with an instrument too narrow
for its contents. Eighth time in this audit that the instrument rather than the
subject was at fault, and the second time the mistake was made against a value
whose correct form was documented in an erratum I had already read.

The standing rule from W-INTL-32 covers assertions of absence. This extends it:
an assertion that a recorded value is wrong must state how the value was read.
A pattern that cannot represent the value's format will always report it as
malformed.

What came out of it. scripts/check_catalog.py now parses the expression form, so
the two entries are genuinely checked rather than skipped, and the rule is applied
by whitelist to the four clusters that use a fixed binary layout. Building that
whitelist was itself instructive: applying the field rule to every entry flagged
thirty-six correct ones - VAX excess-128, Cray's bias, tapered posits and takums,
IEEE decimal's different bias convention, composite double-double rows, and
logarithmic systems with no bias at all. Every one was the checker being wrong
about the format. A rule applied outside its domain produces noise, and noise
trains a reader to ignore the checker.

The entry is retained rather than deleted for the same reason W-INTL-36 was: it
was published, and the record of it being wrong is worth more than a tidy file.

## W-INTL-43  The 323 MHz claim has no artefact anywhere, and the file cited for it does not exist

Severity: high. It extends W-INTL-41 from a wrong citation to an absent result,
and the search was run four ways so the conclusion does not rest on one method.

Method, recorded per the rule adopted in W-INTL-32 and extended in W-INTL-42.

1. Code search across the account for the figure and for the conformance count,
   under four phrasings.
2. The format specification named as the catalog entry's source.
3. The persistent identifier the catalog describes as a hardware archive.
4. The status table that carries the claim, and the file it cites as evidence.

What each returned.

The status table in gHashTag/trinity-s3ai at docs/hardware/README.md records the
claim as FPGA 323 MHz with 35 of 35 RTL tests, marks it verified, and cites
gf16_benchmarks.json as the evidence. That file does not exist in the repository.

A similarly named file, gf16_bench_results.json, does exist in two places. It
contains mean squared error, add and multiply latency in nanoseconds per
operation, a neural-network accuracy figure and an MNIST encode-decode check. Its
own source field names Zig benchmark sources. There is no FPGA frequency in it, no
device, and no RTL test count. It is a software benchmark.

The gf16 specification named as the catalog source contains no timing data.

The persistent identifier is a two-kilobyte software description stub, as recorded
in W-INTL-41.

So the claim is asserted as verified in two places, and the artefact cited in each
is either missing or about something else. Whether 323 MHz was ever measured is
not settled by this; what is settled is that nothing reachable supports it.

Contrast worth noting, because the same document does this correctly. Two rows
below the 323 MHz line, the same status table records a throughput and power
figure as an open conjecture and states that it is an RTL projection rather than a
measurement. The discipline exists in the file. It was not applied to this row.

Action.

1. Produce the timing report or withdraw the frequency. It is one number and it is
   asserted at the strongest status the project uses.
2. Separate the conformance count from the frequency. 35 of 35 RTL tests passing
   is a real and checkable claim with a plausible artefact; a clock rate is a
   different claim needing a different one.
3. Fix the citation in both the status table and the catalog entry.

Closes when the frequency is either evidenced or gone from both.

## W-INTL-44  The format's field layout is IBM's DLFloat, and our own benchmark file says so

Severity: high for any novelty claim, low for everything else. Found by reading
the benchmark file rather than the papers.

The gf16 benchmark artefact describes the format under test, in its own words, as
DLFloat-6:9 with one sign bit, six exponent bits and nine mantissa bits.

IBM published DLFloat in 2019 as a 16-bit format for deep learning training and
inference, with exactly one sign bit, six exponent bits and nine mantissa bits,
chosen for the same stated reason - that deep learning cares more about dynamic
range than about precision. The field layout is identical.

So the layout is not new, and the project's own files already name it. What can be
claimed is the derivation: a rule that generates field widths across a family from
a stated constant, of which the 16-bit member coincides with DLFloat. That is a
different and defensible claim, and it is stronger for conceding the coincidence
than for leaving a reviewer to find it.

What must not be claimed: that the 16-bit format is a new numeric format. A
reviewer who knows the low-precision literature knows DLFloat, and the catalog's
own purpose - registry filling with bit-exact conformance vectors - does not need
novelty at the layout level.

Action.

1. State the DLFloat coincidence explicitly wherever gf16 is introduced, including
   the preprint if it does not already.
2. Claim novelty for the generating rule and the anchoring, not for the layout.
3. Add DLFloat to the competitor matrix as prior art for the 16-bit member.

Closes when the coincidence is stated in every document that introduces gf16.

## W-INTL-45  Ownership is renounced everywhere, which freezes a known defect  [CORRECTED 2026-07-30]

Severity: critical for this deployment, and it is the opposite of what this entry
first said.

What was written, hours earlier. That MiningPool is Ownable, takes its owner from
the deployer, and therefore has an administrative function controlled by a key the
deployment record calls ephemeral - with two failure modes depending on whether
that key still exists.

What is actually the case. The deployment script renounces MiningPool's ownership
explicitly at the end of the run, on the line after the token is deployed, with a
comment saying so. TriToken renounces in its own constructor. So there is no
owner and no key. The second failure mode does not exist.

Method, and its limit. This was read from the deployment script in the contracts
repository, which is the script whose broadcast produced the recorded addresses.
It was not confirmed by reading owner() from the chain, because the sandbox this
was run in blocks the public RPC endpoints and the block explorer's contract
reads are unavailable for unverified contracts. Verifying the contracts, which is
W-INTL-35, would also make this directly checkable by anyone.

The first failure mode survives and is now certain rather than conditional. The
registry can never be replaced. ChipRegistry accepts any self-declared key, per
W-INTL-34, so this deployment has a permanently unfixable identity gate. Nothing
can repair it, and nothing can pause it.

That reframes the problem. It is not that custody is undecided. Custody is
decided, in the direction that freezes a defect the project already knows about.

For this deployment there is no remedy, and none is needed: it is a testnet, it
has never been used, and the correct response is to treat it as disposable, which
is what a testnet is for. The finding matters for what comes next.

For a value-bearing deployment. Renouncing everything at deployment is the strongest
possible statement about supply and the weakest possible position on defects,
because it forecloses every response to one. The two contracts here made opposite
choices for the token and the pool and then converged on the same outcome by the
end of the script, which suggests the outcome was inherited rather than chosen.

The defensible sequence is to renounce late rather than early: hold administrative
functions in a multi-signature wallet behind a timelock while the system is being
exercised, and renounce once it has been. That keeps the ability to fix a defect
during the period when defects are found, and still ends where a renounced
contract ends. Renouncing at deployment buys the same final property while paying
for it during exactly the window when it costs most.

Action.

1. Record, in the external documents, that this deployment is permanently frozen
   with a registry that does not verify. It is a testnet and that is acceptable;
   what is not acceptable is describing it as though it could be corrected.
2. For the next deployment, decide the ownership schedule deliberately: what is
   held, by whom, behind what delay, and on what condition it is given up.
3. Do not repeat the current arrangement by default. It was almost certainly not
   chosen.

Closes when the ownership schedule for a value-bearing deployment is written down.

## W-INTL-46  Neither part can host the identity scheme the thesis needs, and that makes the custom die load-bearing

Severity: critical, and it is the most consequential finding in this file because
it changes what the silicon roadmap is for rather than correcting a claim.

Method. Vendor documentation and secondary sources at search depth, following the
question raised by research/attestation_prior_art.md - whether the strong identity
family that literature recommends is available on the parts in hand. Read at
summary depth, not from the technical reference manuals directly; the conclusion
below is consistent across several sources but should be confirmed against the
manuals before it is relied on commercially.

The chain, each link checkable.

1. The literature's answer to binding a key to a device without a vendor enclave
   is a key reconstructed from a physical function rather than stored, so nothing
   at rest can be extracted. That is recorded in research/attestation_prior_art.md.

2. Neither part in this project has a hardened physical function. Zynq
   UltraScale+ devices do - a hardened block, with vendor-integrated third-party
   intellectual property, used to protect the boot key. Zynq-7000 and the 7-Series
   do not. On those parts such a function has to be built in fabric.

3. A fabric implementation lives in the bitstream.

4. The bitstream on these parts is not safe ground. On 7-Series the encryption has
   an unpatchable published full break, and on Zynq-7000 the authentication has a
   published bypass in the first-stage boot loader, both recorded in W-INTL-19.

5. Therefore a fabric-built physical function on either part can have its
   response read out, or the code that consumes it replaced. The strong family is
   not reachable on this hardware.

The tension this exposes, which is the actual finding.

Two constraints the project holds simultaneously: identity rooted in the device
rather than in a vendor enclave, and hardware obtainable under any export regime.
On commodity parts these conflict. The part that would give a hardened physical
function today is a recent, advanced-node device - precisely the class the thesis
argues a buyer concerned with supply-chain independence cannot rely on obtaining.
The parts that satisfy the export constraint cannot host the identity scheme.

There is exactly one point where both constraints hold, and it is a custom die on
a mature node.

So the silicon roadmap is not a later stage of the same story. It is the only place
the central claim closes. Everything before it is a bench demonstration of the
mesh, the arithmetic and the economics, with identity asserted rather than rooted.
That is a defensible position and a much clearer one than treating silicon as an
ambition, and it is stronger in an application than the roadmap framing: it says
why the die is necessary rather than desirable.

Two corollaries worth recording.

The bench-tier and mesh-tier distinction in W-INTL-19 survives this and is
corroborated by it: the sources confirm Zynq-7000 carries a public-key bitstream
signature scheme where the 7-Series does not. The distinction is real. It is just
not sufficient for identity.

Moving to a part with a hardened function would close the identity gap and open a
supply-chain gap. That trade should be made explicitly if it is made at all, not
by drifting onto a newer part because it has the feature.

Action.

1. Reframe the silicon roadmap in every external document: the die is where
   identity closes, not a later nicety. State that identity on the current parts is
   asserted rather than rooted.
2. Confirm the availability claim against the vendor technical reference manuals
   before it appears anywhere external. Done 2026-07-30, for both parts rather than
   for one and its family.

   UG470, the 7 Series Configuration User Guide, covering the bench tier: the terms
   "physically unclonable", "physical unclonable" and "PUF" appear nowhere - zero
   occurrences across the whole document under all three phrasings. What it does
   describe is a factory-programmed identifier readable over the debug port by the
   vendor's own tools, with identification by that route characterised as a lower
   level of security than the encryption options.

   UG585, the Zynq-7000 Technical Reference Manual, covering the mesh tier and
   therefore the trust anchor: 1843 pages, 3.2 megabytes of extracted text, and the
   same three phrasings return zero occurrences again. What that manual does carry
   is a secure-boot chapter with eFUSE settings, battery-backed RAM, AES key
   management and RSA authentication.

   Two things follow. The finding now rests on the manual for each part rather than
   on one manual plus a family inference, which is what the first version did - the
   mesh part is the trust anchor, so confirming its sibling and generalising was the
   weakest link in the chain and is now closed.

   And the key storage those manuals describe is precisely the family the literature
   says to avoid: a key at rest in fuses or battery-backed memory, rather than
   reconstructed on use. On these parts the protection around that storage is the
   bitstream path, which carries an unpatchable break on one and a published
   authentication bypass on the other, per W-INTL-19. So the parts do not merely
   lack the strong option; the option they do offer is the one whose protective
   layer is already broken here.

   Corroborated in passing: the Zynq-7000 manual does carry RSA authentication in
   its secure-boot chapter, which confirms from the primary source the mesh-tier and
   bench-tier distinction recorded in W-INTL-19.
3. Do not describe a fabric-built physical function as device identity on these
   parts. Given the two published bitstream attacks it would not be one.
4. If a part with a hardened function is being considered, write down the
   supply-chain cost alongside the security gain.

Closes when the external documents say the die is load-bearing for identity, and
when the availability claim has been confirmed against the manuals.

## W-INTL-47  Identity in silicon does not need a funded custom die; it needs a macro on the next shuttle

Severity: this is not a weakness. It is recorded here because it corrects the
conclusion of W-INTL-46, and because the correction is the most useful thing in
this file for the project's schedule.

W-INTL-46 concluded that the project's two constraints - identity rooted in the
device, and hardware obtainable under any export regime - meet at exactly one
point, a custom die on a mature node. That reasoning holds. What it got wrong was
how far away that point is.

Checked 2026-07-30. A ring-oscillator physically unclonable function has already
been taped out on the same open 130 nm process the project's own shuttle tile uses,
through the same Tiny Tapeout programme. It is public. Its architecture is eight
independent blocks, each holding thirty-two seven-inverter ring oscillators; a
challenge selects one oscillator from each half through muxes, two counters race to
a threshold, and an arbiter declares a one-bit response. Eight bits of
challenge-response pair in total.

So the identity root does not require a mask set. It requires a macro on a shuttle
submission, on a process the project is already using, in a programme it has
already submitted to. That is a different order of cost and a different order of
schedule from a funded custom run, and it is available now rather than after
funding.

The limitations, taken from the author's own documentation rather than inferred,
and they are not small.

Eight bits of challenge-response pair is two hundred and fifty-six challenges. That
is a demonstration of feasibility on this process, not an identity. A usable
identity needs far more response bits, which means far more area than a single
shuttle tile.

The metrics that decide whether a physical function is any good - uniqueness across
parts, reliability across conditions, uniformity, entropy - are uncharacterised for
this architecture on this process. The author is explicit about it and is
crowdsourcing measurements from board owners. Nobody yet knows how well it works.

Ring oscillators drift with temperature, and the author documents it: responses may
change as the device warms and settle once it is at operating temperature. For a
node deployed outdoors that is a first-order problem, and it is why production
designs pair a physical function with error correction rather than reading it
directly. None of that exists here.

What this changes, stated precisely.

The roadmap claim moves from "identity closes when a custom die is funded" to
"identity closes when a characterised physical function with error correction fits
on a tile, on a process we already use". The first is a funding request. The second
is an engineering programme with a known first step, and it is a much better thing
to put in front of a committee.

What it does not change: nothing about identity may be claimed today. The current
parts cannot host it, the demonstration that exists is eight bits with unmeasured
quality, and the gap between that and a usable root is the actual work.

Action.

1. Restate the silicon roadmap again, this time with the shuttle path as the first
   step and the custom die as what follows if the tile proves out.
2. Read the existing implementation and decide whether the architecture scales in
   the area a tile allows. Done 2026-07-30, research/puf_tile_budget.md. It does
   not scale as written and it does not need to.

   The existing design declares 1x2 tiles for eight response bits, so about 4,508
   square micrometres per bit. Scaled naively a 128-bit response wants thirty-two
   tiles against a limit of sixteen. But it replicates a whole measurement chain
   per bit - thirty-two oscillators, two multiplexers, two counters and an arbiter,
   eight times over. The oscillators are entropy and must be distinct; the counters
   and arbiter are apparatus and need not be. Sharing one chain and driving it
   sequentially, a bank of 128 oscillators offers 8,128 distinct pairs, which is far
   more than a key needs.

   With the decoder inside the budget the estimate is three to five tiles of the
   sixteen available. It fits.

   One correction inside that calculation, recorded because it was mine. The first
   attempt assumed the error correction could run in software on the processing
   system using public helper data, leaving only the oscillators on the tile. The
   literature is explicit that post-processing belongs on the same integrated
   circuit, because a raw response that leaves the die can be captured, and
   capturing it defeats the point of a key that is never stored. The decoder is in
   the budget and is the largest item in it.

   So the blocker is architectural, not dimensional.

   Confirmed by synthesis 2026-07-30. The published implementation was cloned and
   run through yosys against the real SkyWater standard-cell library at the typical
   corner. Measured: 3,784 cells, 20,900 square micrometres of cell area for eight
   response bits, of which 6,730 is 1,792 oscillator inverters and 5,930 is 296
   flip-flops, at 58 percent utilisation of the declared 1x2 footprint. The
   inverter count is exactly eight blocks by thirty-two oscillators by seven
   inverters, which confirms the architecture the budget was reasoned from.

   Recomputed on measured areas the answer is 2.9 to 3.9 tiles of sixteen, against
   2.9 to 4.1 estimated. The conclusion did not move.

   The remaining estimate was the decoder, and it has now been measured too - which
   moved the answer.

   A decoder was written for BCH(255,131) over GF(2^8) and its two area-dominant
   stages synthesised against the same library. The key-equation solver was left out
   rather than written unverified and reported as measured. Those two stages alone,
   at the correction strength published PUF designs use, measure 22,668 square
   micrometres - more than the eighteen thousand that had been budgeted for the whole
   decoder.

   Area is linear in correction strength at about 1,212 square micrometres per unit
   of t. With the solver taken as comparable to the measured stages, the full budget
   runs from 3.0 tiles at t=4 to 6.3 tiles at t=18, and the decoder is between a
   third and two thirds of the total.

   So it still fits in sixteen tiles, with less margin than previously stated. And
   the reason to care about characterisation sharpens: the correction strength sizes
   the largest block on the tile, and correction strength is set by the oscillator
   error rate, which nobody has measured. Characterisation is the first step because
   it determines the area, not because it is tidy.
3. Whatever is built, characterise it - uniqueness, reliability across the
   temperature range a deployed node sees, uniformity, entropy - before any
   document calls it identity. The existing implementation is uncharacterised and
   its author says so; repeating that would be worse than not building it.
4. Plan for error correction from the start. A physical function read directly is
   not an identity; the temperature behaviour the author documents is the reason.

Closes when the external documents describe the shuttle path accurately and no
document claims identity ahead of characterisation.

## W-INTL-48  The Solution section asserts hardware that is not on the bench

Severity: high. It is one clause in the sentence that describes the product, and it
names a component the project's own working notes say it does not have.

The application says a Zynq-7020 with a software-defined radio and GPS timing
routes traffic through a self-healing mesh.

The hardware target in the mesh repository's own working file lists three boards as
Zynq-7020 plus AD9361, armv7l, Linux 5.10. No GPS. The README and roadmap in the
same repository describe the intended node as Zynq-7020 plus AD9361 plus GPS and a
pulse-per-second input, so the intent is documented - but the boards in hand are the
first list, not the second.

The mesh daemon's own strengthening document is explicit about the consequence:
items needing flight hardware, GPS or an external radio part are marked as
unautomatable and cannot be closed in that repository today, and a mobility-aware
routing metric is recorded as blocked without a real position source.

So GPS timing is a design element, not a bench fact, and the Solution section states
it as though it were installed.

Action: describe the node as it is. The radio and the processor are there; the timing
source is not. If GPS matters to the architecture - and for a mesh sharing an uplink
it plausibly does - say what it is for and that it is not yet fitted.

Closes when no external document lists GPS among what the boards have.

## W-INTL-49  Two radios have never been up at the same time

Severity: high, and it reaches further than the radio.

Found in the mesh repository's working notes, in a sentence written by the project
about itself: the radio's capacity has never been measured, only one AD9361 has ever
come up at a time, and the fragmentation rate constant is a guess and should be
treated as one.

The same file states elsewhere that two radios are needed for a link.

Put together, that means no radio link of any kind has ever existed here - not over
the air, which was already recorded, and not in loopback between two boards either.
The 108.6 dB figure is a single board talking to itself, which is consistent with
everything already written, but the absence goes further than the audit had it:
there has been no two-party radio test at all.

It also reaches the mesh claims. Multi-hop routing, throughput across two hops and
the three-node shared-uplink demonstration are all recorded as simulation, which is
correct, but the reason is stronger than scheduling. They could not have been run.

And it puts a number in the application under suspicion by association: a constant
governing fragmentation rate is documented by its own author as a guess. Nothing
external quotes it, and nothing external should.

Action.

1. State in the application that no two-radio test has been performed, alongside the
   existing statement that nothing has been transmitted over the air. The second
   does not imply the first and a reader will assume it does.
2. Bring up two radios simultaneously before anything else on the radio path. It is
   the prerequisite for every mesh claim currently marked simulation.
3. Do not quote the fragmentation constant anywhere external until it is measured.

Closes when two radios have been up together and the capacity has a measured number.

## W-INTL-50  The single-vendor claim about satellite backhaul is false

Severity: medium in general, high in front of this particular committee.

The Problem section says satellite backhaul is a single foreign vendor. Checked
2026-07-30 against the current market: it is not.

There are at least four distinct providers with commercial backhaul offerings, and
the second largest constellation is specifically oriented toward telecommunications
backhaul for enterprise and government customers, working with governments in Africa
and South Asia - which is precisely the market and the use case the Problem section
describes. Two further operators compete for the same enterprise business, and a
fourth constellation is being funded at scale with an explicit focus on underserved
markets.

The claim is therefore wrong on its own terms, and it is wrong in a way that will be
noticed. The submission is to a committee in a region that buys satellite capacity
and follows this market closely.

The defensible version is narrower and survives. Satellite backhaul is a small
number of foreign vendors, all outside the buyer's jurisdiction, sold as a recurring
operating cost rather than an owned asset, and subject to the commercial and
political decisions of the operator. That is enough to motivate terrestrial mesh
without asserting a monopoly that does not exist.

Action: replace the claim with the narrower one. Do not describe a competitive market
as a monopoly to a buyer who purchases in it.

Closes when no external document claims a single satellite vendor.

## W-INTL-51  The proof types are not produced; they are stubs, and three documents say so

Severity: high. It is the sentence the business model rests on.

The application says three of the four proof types are produced today by the node
daemon at software-signed level, and carefully distinguishes produced from settled.
That distinction was the right one to draw and it is drawn around the wrong verb.

Three sources, all the project's own.

The mesh roadmap lists the four-arm DePIN proofs - transport, compute, coverage,
sensor - with status `-sim` and the word mock beside them, and elsewhere in the same
file counts "three mock DePIN proofs".

The mesh daemon does not produce proofs at all. It is 111 lines: take a datagram,
choose a next hop, write it to the radio transport. Searching it for proof, receipt,
attestation or claim returns nothing, and reading it confirms why.

The daemon that would produce them is a separate repository, and it exists. It holds
attestation, miner, proof-of-capacity, proof-of-replication and validator modules -
of two kilobytes, one point seven, one, under one, and one point five respectively.
Its own README states, in a warning block: pre-silicon status, and all
hardware-touching code paths are mock or stub implementations that compile and pass
tests.

So what exists is stub code that compiles. Produced at software-signed level says
something else: that real proofs are being generated and signed in software today.
They are not.

The correction is small and the difference is not. Say that the proof interfaces are
implemented as stubs against the chip that does not exist yet, that they compile and
pass their tests, and that nothing has produced a proof over real work. That is a
defensible statement about a pre-silicon system and it is what the project's own
files say.

Action: replace produced with implemented as stubs, everywhere. Do not describe stub
code as output.

Closes when no external document says proofs are produced today.

## W-INTL-52  Re-checking the index-based absences: one changed, and a comparison report should not be quoted

Severity: medium. This entry exists because the previous loop showed the account-wide
code search does not reach every file, which put every earlier absence conclusion
drawn from it under suspicion.

Method. File trees enumerated through the git API for six repositories - 13,959,
18,210, 673, 761, 117 and 7,350 paths - filtered by name for energy, power, joule,
watt and efficiency, then for comparison, baseline and naive. Candidates fetched and
read. No index involved.

Result one: the energy finding changes in part. E20 recorded that no derivation was
found for the 4x to 8x figure, searched under five formulations. Enumeration found
something the index had not surfaced: a device-side power model in t27 at
conformance/fpga_power.json. It carries stated constants for an Artix-7 - ten
microwatts per megahertz per lookup table, five per flip-flop, fifty per block
memory, one hundred per multiplier, twenty per input-output, fifty milliwatts static
base, a twelve percent default toggle rate - together with device limits, a two-watt
typical budget, and declared invariants that power estimates and utilisation stay in
range.

That is coarse and round-numbered, and it is a model with its assumptions written
down, which is more than the ledger credited. The device half of the energy claim is
therefore modelled rather than absent.

What is still absent, and now absent by enumeration rather than by index: any
comparison against a general-purpose baseline, and any derivation from the naive
twenty-fold figure to the quoted four-to-eight. The model computes what an Artix-7
design consumes. It does not compare that to anything.

Result two, incidental and worth recording before someone quotes it. A binary-versus-
ternary benchmark report exists and does not say what its title suggests. It measures
execution time in a software virtual machine, not energy, and ternary is slower on
every row - ratios of 1.48, 1.97, 1.68 and 2.64 in binary's favour. Several ternary
result columns read "1 (wrapped)", which suggests the ternary path is producing wrong
values rather than merely slow ones, and a comparison whose one side is wrong is not a
comparison.

None of that contradicts the project's thesis, which is about hardware rather than
software interpretation, and there is no reason ternary arithmetic would be faster in
a binary virtual machine. But the file is named as a comparison report and would be
read as one.

Action.

1. Restate E20 as done: device side modelled with stated assumptions, comparison side
   non-existent.
2. Do not cite the binary-versus-ternary report. Fix the wrapped results or mark the
   file as not a valid comparison.
3. The remaining absences in this audit that rest on the index should be re-checked
   the same way. This pass covered energy and comparison; W-INTL-43 on the timing
   report used direct fetches as well as the index and is less exposed, but it is not
   clear of it.

Closes when every absence conclusion in this file either rests on enumeration or says
that it does not.

---

## W-INTL-53  The key-equation solver was budgeted at a third of its measured area

Severity: medium, and it is a correction of this project's own analysis rather than of
anything external.

`bch_area_probe.v` measured two of the decoder's three stages and deliberately left
the key-equation solver out, on the stated grounds that writing it unverified in one
pass and reporting the result as measured would be worse than saying it was not
measured. The tile budget then carried the solver as comparable to the two stages
beside it.

Written and measured 2026-07-30, as the inversionless Berlekamp-Massey iteration, and
verified before measured: syndromes constructed from known error patterns, the result
compared projectively against the error locator built directly as a product of linear
factors, every correctable weight from one error to t with three patterns each. 55
patterns at t=18, all passing, and the check shown able to fail - two independently
injected faults each failed 51 of the 55.

| t | Solver | Previously assumed |
|---|---|---|
| 4 | 17,503 | 5,694 |
| 8 | 31,620 | 10,475 |
| 12 | 45,878 | 15,350 |
| 18 | 66,847 | 22,668 |

Low by a factor of 2.95, and the whole-decoder figure low by 1.97.

The cause generalises, which is why this is an entry rather than a footnote. Syndrome
accumulation and the Chien search multiply by compile-time constants and fold into XOR
trees; Berlekamp-Massey multiplies two runtime values, about 3(t+1) times. Estimating
the third stage from the first two assumed the same kind of arithmetic. Any estimate in
this project that extrapolates area from a neighbouring block should be checked for the
same assumption.

Two silent faults surfaced while writing it, both recorded because both produce
plausible output rather than failure. Doubling the register length by shifting rather
than concatenating truncates 36 to 4 at t=18, a shift being self-determined at the
width of its left operand; the iteration then lengthens on the wrong steps and returns
a polynomial of the wrong degree. And selecting a coefficient with a ternary still
elaborates an out-of-bounds read as the untaken operand, which simulation reports as
such and synthesis may treat differently - measuring a circuit that is not the one the
testbench passed.

Status: closed as a measurement. It is superseded in significance by W-INTL-55, which
finds that the code being sized is the wrong code.

## W-INTL-54  The decoder-share column did not follow from the table it sat in

Severity: low as an error, worth recording as a class.

The tile budget's decoder-share column read 36, 51, 61 and 69 percent. Its own decoder
and total columns give 21, 30, 35 and 40. All four rows are high by a consistent factor
of about 1.72, which means the column was computed against a different denominator, and
that denominator cannot be reconstructed from the document.

The other two columns are internally consistent - the decoder column is exactly twice
the two measured stages, which is what the stated assumption says it should be, and
total minus decoder gives a smoothly growing series consistent with the information
rate falling as t rises. So the share column is the error.

Corrected in place rather than carried forward. The class worth noting: this project's
consistency checker verifies the evidence ledger's counts against its own table, and
verifies figures quoted in prose against their sources, but it does not verify that a
derived column in a research document follows from the columns beside it. A check that
recomputed percentage columns from their neighbours would have caught this the day it
was written.

## W-INTL-55  The decoder was sized for the code the literature recommends against

Severity: high, and it is the most useful finding in this file for the hardware
schedule.

Every area analysis of the identity root so far has been of BCH(255,131) at t=18, on
the stated grounds that this is the order published designs use for PUF key generation.
That premise is wrong.

Bosch, Guajardo, Sadeghi, Shokrollahi and Tuyls, "Efficient Helper Data Key Extractor
on FPGAs", CHES 2008, is the standard reference on making a fuzzy extractor small, and
its stated motivation is the same constraint this project has - the area belongs to the
application, not the key generator. They consider BCH and discard it before
implementing it, writing that BCH decoder algorithms are very complex and therefore
expected to be expensive in area. Their construction concatenates a short odd
repetition code with a first-order Reed-Muller code, and their measured conclusion on
a Spartan-3E is that Reed-Muller wins on area and, by their own error tables, on
correction performance too. They note they could find no BCH implementation to compare
against and expected its complexity to be higher.

Measured here, both codes, same library, same rule that nothing is quoted before it
decodes correctly:

| Circuit | Area | Tiles |
|---|---|---|
| R(1,6) + repetition, decoders | 4,596 | 0.25 |
| BCH decoder, t=4 | 23,197 | 1.3 |
| BCH decoder, t=18 | 89,515 | 5.0 |

A factor of 19.5. The decoder falls from 57 percent of the tile budget to about seven.
One corroboration: the paper states its decoder's flip-flop count as 2^m + 6m - 1,
which is 99 at m=6, and the circuit here uses about 95 for the Reed-Muller half,
reached by a different derivation.

The cost moved rather than vanished, and this is the part that must travel with the
finding. Their construction is measured at a bit error probability of 0.15 and needs
4,800 source bits to yield a 128-bit key. This project's budget assumes 384 raw bits,
from a three-times multiplier over the key length that was never tied to a measured
error rate. So the decoder saving is large and measured, and the raw width it depends
on is somewhere between one and twelve times what has been assumed.

What that changes about priorities: characterising the oscillator error rate was
already first because it sized the largest block. It is now first because it decides
which code to build, and that decision is worth a factor of nineteen in the block that
was until today believed to dominate the design.

What it does not license: any statement that the identity root is built. These are
synthesis areas for circuits verified in simulation. Nothing is fabricated.

Closes when the error rate is measured on this process and a code is chosen against it.

## W-INTL-56  The pair count was used as an entropy count, and it is not one

Severity: high. It invalidates the optimistic column of the tile budget and it is
stated as wrong in the literature the project should have been reading.

The budget document proposed sharing one comparison chain across a bank of ring
oscillators, on the reasoning that a bank of R offers R(R-1)/2 distinct pairs, far more
than any key needs, so the constraint moves from oscillator count to pair
independence.

Mansouri and Dubrova, arXiv:1207.4017, say why that fails. For a traditional RO-PUF
not all challenges are valid: if A is faster than B and B is faster than C then A is
necessarily faster than C, so the third response is predictable from the other two.
Frequency comparison is a total order.

R oscillators therefore realise one of R! rankings and carry log2(R!) bits, however
many pairs are read out. R(R-1)/2 counts challenges a verifier may pose, not bits an
adversary cannot guess, and the gap grows: at R=614 the pair count is 188,191 against
4,807 bits of ordering, a factor of 39.

The document had flagged pair independence as unmeasured, which was the right
instinct pointed at the wrong thing. The problem is not that the pairs might turn out
correlated on this process; it is that they are provably dependent for any process,
by transitivity, and the amount of dependence is calculable rather than
uncertain. `research/code_choice_model.py` now carries both readings side by side so
the size of the overstatement stays visible.

The ordering figure is itself an upper bound. It assumes every ranking equally likely,
and the same literature reports that pairs too close in frequency must be discarded
for reliability, at about a fifth of them in a temperature-aware design.

Closes when the entropy per oscillator is measured on this process. Until then
log2(R!) is the number to use and R(R-1)/2 should not appear.

## W-INTL-57  The code every area analysis sized does not meet its own error target

Severity: high, and it is the finding that should have come first.

Five loops of area analysis took BCH(255,131) at t=18 as the target configuration.
None asked whether it reaches the word error probability the application needs.

Computed 2026-07-30 with a model calibrated against the published table it derives
from - five checks, all matching to three significant figures. BCH(255,131) at t=18
reaches one in a million only if the bit error probability is below 1.88 percent. Ring
oscillator responses across temperature are not reliably below that, and the same
literature that supplies the one concrete figure available - 0.48 percent of bits
flipping at ten percent supply deviation, from SPICE on 90 nm with matched pairs -
describes temperature as the larger effect and handles it by discarding unreliable
pairs.

| Construction | Works up to | Raw bits | Oscillators | Tiles |
|---|---|---|---|---|
| BCH(255,131) t=18 | 1.88 percent | 510 | 98 | 5.11 |
| rep[3] + RM[64,7,32] | 13.22 percent | 4,800 | 614 | 1.15 |
| rep[5] + RM[32,6,16] | 12.53 percent | 4,640 | 596 | 1.03 |

So the code was not merely expensive, as W-INTL-55 concluded. It was ineffective, and
the area analysis obscured that by never checking the code against its requirement.
The class of error is worth naming: measuring a configuration carefully is not the
same as establishing that the configuration is admissible, and a careful measurement
of an inadmissible configuration reads exactly like a useful result.

What survives, and is now better supported than before: it fits. The recommended
construction takes about one tile of the sixteen a submission may use and holds to a
bit error probability of 13 percent. The question W-INTL-46 raised is answered no on
every input that has been measured.

## W-INTL-58  This file overstated the code advantage by leading with a decoder-only figure

Severity: low, and it is a correction of the entry above it rather than of the project.

W-INTL-55 reported a factor of 19.5 between the two codes. That factor is decoders
only. Across the whole design, oscillators included, it is 4.4: the smaller decoder
buys its saving by consuming six times as many oscillators, and about half the
advantage goes back.

The conclusion holds and the number did not. Recorded because the figure has now been
in a merged document and a pull request description, and because the failure mode is
one this project keeps repeating - quoting a ratio between two measured parts as
though it were a ratio between two designs.

## W-INTL-59  Response positions and min-entropy were collapsed into one constraint

Severity: high, and it is a correction of the fix applied in W-INTL-56 rather than of
anything older.

W-INTL-56 replaced the pair count R(R-1)/2 with the ordering bound log2(R!) and said
that was the number to use. It is not, and the error is more interesting than the one
it replaced.

There are two constraints, not one.

The code needs response bit *positions* - 4,800 of them for the recommended
construction. Nothing about those positions has to be independent. A decoder consumes
correlated bits as happily as uncorrelated ones; correlation costs entropy, not
correctability.

The extractor needs *min-entropy* - 128 bits, plus whatever the helper data leaks.
This is the only constraint independence bears on.

Requiring log2(R!) to exceed the count of response bits is neither of these. It demands
that ordering entropy exceed a bit count that does not need to be entropy at all. The
number it produced, 614 oscillators, happens to sit inside the bracket the correct
framing gives, which is why it looked reasonable while the reasoning was wrong - and
which is why it was published in a merged document and a pull request before this was
noticed.

Corrected in `research/code_choice_model.py`, which now reports a bracket from the two
arrangements and enforces the entropy floor separately.

## W-INTL-60  Measured entropy per oscillator is a sixteenth of the ordering bound

Severity: high. It widens the answer rather than changing its direction.

Wilde, Hiller and Pehl, arXiv:1910.07068, compute entropy from silicon rather than
from a bound: 512 ring oscillators on each of 193 parts, paired disjointly with their
neighbours to give 256 response bits, yielding 241.0 bits by the bitwise estimate and
241.3 by a normal model - about 94 percent of what 256 bits could carry.

That is 0.471 bits per oscillator. The ordering bound for 512 oscillators is 3,875
bits, so practice sits a factor of sixteen below it. They add that the usable figure is
lower still, because bits from pairs too close in frequency must be masked for
reliability.

They also record why two published entropy figures from the same raw data disagree:
one compares adjacent oscillators and one compares distant ones, and spatial patterns
in mean frequency make the distant comparison look far less unique. So the extraction
rate depends on layout, not only on count, and no figure transfers between
arrangements without saying which arrangement it came from.

Applied to this project, with the decoder measured:

| Arrangement | Oscillators | Total | Tiles of 16 |
|---|---|---|---|
| oscillators reused across pairs | 272 | 11,752 | 0.65 |
| two oscillators per response bit | 9,600 | 257,036 | 14.25 |

A factor of twenty-two, and both fit. The upper figure has almost no margin, and it is
the one that rests on a measurement while the lower rests on an assumption about reuse
that nobody has tested.

## W-INTL-61  The response bits are biased, so key search is ordered rather than uniform

Severity: high, and it is a security finding rather than an area one, which is why it
is separate from W-INTL-60 despite sharing a source.

The same paper reports the per-bit probability bias across its dataset reaching roughly
plus or minus 0.4, and draws the consequence directly: as a result of these biases not
all keys are equally probable, which opens a way to get above linear proportion between
the chance of finding the right key and the area of key space searched - one need only
try keys in descending order of probability.

241 of 256 bits of entropy sounds close to full. It is an average, and an average does
not bound guessing effort when the distribution is skewed. Any statement that this
project's identity root delivers 128 bits of security has to be made against a
min-entropy figure and a bias measurement, neither of which exists for this process.

The same authors also attempted to exploit the residual correlations by covariance
fitting and could not, and report a context-tree-weighting compression bound of 7.86237
bits per byte, 98 percent of original size - a weaker bound than their bitwise estimate.
So the honest summary is that the bias is documented and the exploitation is not
demonstrated, which is a reason to measure rather than a reason to assume either way.

What this changes in the application: nothing yet, because no security level is claimed
for the identity root. It becomes load-bearing the moment one is.

## W-INTL-62  The derived-column check found nothing else in the history

Severity: none. Recorded as a negative result, because negative results from a new
instrument are worth as much as positive ones and are easier to forget.

The check added on 2026-07-30 was run backwards over the whole repository: 79 revisions
by 18 documents, every markdown table row in every revision. It flagged four rows, all
four being the rows of the single table already recorded as W-INTL-54.

The reasoning that prompted the sweep was that a class of error rarely occurs once.
Here it did occur once. The check's value is therefore prospective rather than a
backlog, and the sweep is worth stating so nobody runs it again expecting a yield.

## W-INTL-63  Helper-data leakage was never counted, and it invalidates the recommendation

Severity: critical for the hardware plan. It withdraws the conclusion of W-INTL-55,
W-INTL-57 and W-INTL-60, all of which this file published in the last three days.

Publishing helper data costs min-entropy. For a secure sketch over an (n,k) linear code
the loss is bounded by n-k. Gao, Su, Yang, Chen, Nepal and Ranasinghe (arXiv:1902.03031)
call it the well-known min-entropy loss and use it directly as a design rule: prefer a
small n and a small t, because a small t implies a large k, and a large k means fewer
blocks to reach a k-bit secret.

No area analysis in this project counted it. Residual min-entropy per block is
`rho*n - (n-k)`, and at the measured rho of 0.9414:

| Construction | n | k | Leak | Residual |
|---|---|---|---|---|
| rep[3] + RM[64,7,32] | 4,800 | 175 | 4,625 | -106 |
| rep[5] + RM[32,6,16] | 4,640 | 174 | 4,466 | -98 |
| BCH(255,131) t=18, two blocks | 510 | 262 | 248 | 232 |
| BCH(127,15,27) | 127 | 15 | 112 | 7.6 |
| BCH(63,16,11) | 63 | 16 | 47 | 12.3 |

The construction recommended for the last three days has negative residual entropy. On
the standard bound it delivers no secret at all. Withdrawn.

The direction of the error is the interesting part. Leakage rewards a high code rate;
error tolerance rewards a low one. Every conclusion this project reached about codes was
drawn with only one of those in view, and each time the missing constraint pointed the
other way.

Two qualifications that must travel with this. The n-k figure is an upper bound, so a
tighter analysis for a specific code and source could recover some of it - but it is the
bound the field designs against, and a construction that needs a better bound than the
field uses is not one to build on. And the same arithmetic applied to the CHES 2008
source-bit column gives a negative residual at that paper's own assumed entropy density,
which suggests that column answers how many bits the code delivers rather than how much
secrecy survives publication. That is a reading of their table, not a defect found in it.

## W-INTL-64  The code that satisfies all three constraints, measured

Severity: this is not a weakness. It is the resolution of W-INTL-46, W-INTL-55,
W-INTL-57 and W-INTL-63.

BCH(127,15,27) over GF(2^7) with primitive polynomial x^7+x^3+1 clears leakage, error
tolerance and area together, and it is the code Gao et al. selected for the same reasons.

Measured 2026-07-30 on the same library, the solver verified in the new field before its
area was quoted: the GF(2^8) case re-run as a regression and still passing, 82 patterns
at t=27 in the new field passing, and an injected fault failing 77 of them.

| Stage | Area |
|---|---|
| Syndrome bank + Chien search | 27,590 |
| Key-equation solver | 73,119 |
| Decoder total | 100,709 |

Nineteen blocks for a 128-bit key, 2,413 raw response bits, and a bit error probability
tolerated up to 7.06 percent - four times what BCH(255,131) at t=18 allowed.

Total 5.98 tiles with oscillators reused across pairs, 12.62 with two per response bit.
Both inside the sixteen a submission may use.

Caveat on status. The solver is verified; the syndrome and Chien stages are structural
area probes rather than verified decoders, the same status the GF(2^8) versions have
carried since they were written. Their cell counts are correct for the structure
described and no testbench has decoded through them.

## W-INTL-65  The bias range reported for ring oscillators is the range that needs debiasing

Severity: high if a security level is ever claimed. It sharpens W-INTL-61 from something
worth measuring into something with a named remedy.

Gao et al. state the operating range directly: for a PUF with low bias within [0.42,
0.58], increasing the length of raw responses alone is an effective way to compensate for
entropy loss. If the bias is severe, entropy compensation by increasing raw length
becomes ineffective, and the biased responses must be debiased first, for example by
classic von Neumann debiasing. Their own SRAM PUF measures 49.87 percent, comfortably
inside the effective range.

The ring oscillator bias distribution reported by Wilde, Hiller and Pehl reaches roughly
plus or minus 0.4, so a substantial part of it falls outside [0.42, 0.58]. On Gao's
criterion that is the regime where adding raw bits does not fix the problem and a
debiasing stage is required first.

Consequences, stated carefully because this rests on combining two papers rather than on
one measurement. A debiasing stage is not in any area budget in this project. Von Neumann
debiasing discards data, so it also raises the raw response width by a factor that
depends on the bias, which is unmeasured here. And the responses in question are from an
FPGA dataset, not from this process.

So the finding is that a stage may be needed which has never been budgeted, and the
quantity that decides it is the same unmeasured bias. It does not change any figure in
W-INTL-64 today; it is a named candidate for the fourth constraint that analysis says it
could still be missing.

## W-INTL-66  A measured stage did not work, and stage-wise measurement could not tell

Severity: high as a method finding, small as an area correction.

Two of the decoder's three stages had been synthesised and quoted since 2026-07-30 without
ever decoding anything. They were labelled structural area probes rather than verified
decoders, which was honest, and the label turned out to be load-bearing.

Wired to the solver and driven end to end, the Chien stage was wrong. It summed t of the
t+1 coefficients of the error locator and left out the constant term, so its zero test was
not the polynomial's zero test. The circuit was the right size and shape and its cells were
correctly counted, which is exactly why stage-wise synthesis could not find it.

The end-to-end test needs no encoder: BCH is linear, so a received word equal to the error
pattern alone is the all-zero codeword received with errors. The assertion is that the set
of positions located equals the set injected, exactly, with locator degree equal to the
error count. Every weight from one to t, two patterns each, both fields - 54 decodes at
t=27 and 36 at t=18, all passing. The historical defect, injected back, fails all 54; a
corrupted Chien constant fails 8.

Corrected areas, both higher than what they replace:

| Stages | Was | Now |
|---|---|---|
| Syndrome + Chien, GF(2^7), t=27 | 27,590 | 29,148 |
| Syndrome + Chien, GF(2^8), t=18 | 22,668 | 23,407 |

The GF(2^8) figure had stood for five loops. The decoder for the recommended code is
102,267 square micrometres, and W-INTL-64's figure is superseded.

The method point is the one worth keeping. Three stages, each measured correctly, one of
them broken. No amount of care applied to a stage in isolation would have shown it; the
smallest end-to-end path that produces a checkable answer did, immediately.

## W-INTL-67  Debiasing turns the oscillator arrangement into a fit-or-not question

Severity: critical for the hardware plan, and unresolvable without a measurement.

W-INTL-65 named debiasing as a candidate fourth constraint with no budget. Maes, van der
Leest, van der Sluis and Willems supply the cost: classic von Neumann debiasing carries an
overhead factor of about 4.4 at 50 percent bias and 5.3 at 30 percent. They also note that
a PUF's usual reusability across enrolments does not necessarily hold once a debiasing step
is used, which bears on a registry that may re-enrol a die.

For BCH(127,15,27), needing 2,413 response bits:

| | No debiasing | With von Neumann |
|---|---|---|
| Raw response bits | 2,413 | 10,617 |
| Oscillators reused across pairs | 6.07 tiles | 6.07 tiles |
| Two oscillators per response bit | 12.71 tiles | 36.63 tiles |

The last cell is the first configuration in this project's analysis that does not fit the
sixteen tiles available.

Until now the oscillator arrangement was a factor-of-two question about area, and the
answer was yes either way. It is now the difference between fitting and not fitting, and it
becomes that only once debiasing is in the picture. Two unmeasured properties decide it
together: how biased the responses are, and whether reusing oscillators across pairs
degrades extraction.

Three of four combinations fit. The one that does not is where both unmeasured properties
go the wrong way, and nothing rules that out.

Closes when bias and per-oscillator entropy are measured on this process. Both come from
the same characterisation structure, and this entry is the strongest argument yet for
building it before anything else.

## W-INTL-68  The debiasing figure was the worst method, and oscillator reuse turns out to be required

Severity: high. It corrects a number this file published yesterday and strengthens the
conclusion that number supported.

W-INTL-67 used a factor of 4.4 for von Neumann debiasing. That is classic von Neumann,
the least efficient method in the source. Maes, van der Leest, van der Sluis and Willems
give three more, with debiasing overhead at four bias levels:

| Method | Reusable | Overhead at bias 40 / 35 / 30 / 25 percent |
|---|---|---|
| Classic von Neumann | no | 4.4 / 4.4 / 5.3 / 5.3 |
| Pair-output, 2O-VN | no | 2.31 / 2.45 / 2.66 / 2.99 |
| Multi-pass tuple-output, 2P-TO-VN | no | 1.58 / 1.73 / 1.96 / 2.32 |
| Pair-output with erasures, e-2O-VN | yes | 1.00, paid instead as a stronger inner code |

The honest range is 1.58 to 5.3. Quoting the worst method as the cost overstated it by up
to a factor of three, and this file did that.

The conclusion survives and gets sharper. For BCH(127,15,27) with two oscillators per
response bit, the most efficient method at the mildest bias in the table still needs 16.79
tiles against a limit of 16 - and that method is not reusable. Classic von Neumann needs
36.63. Every method fits at 6.07 tiles when oscillators are reused across pairs, because
there the entropy floor binds rather than the position count, and the entropy floor does
not move with debiasing overhead.

So oscillator reuse is a requirement rather than an optimisation, conditional on debiasing
being needed. That statement holds across the whole method table rather than resting on
the one figure this file previously quoted.

## W-INTL-69  Reusability of the key generator is a protocol constraint nobody has recorded

Severity: high, and it is the first finding in this line that lands on the contracts
rather than on the silicon.

Three of the four debiasing methods are marked not reusable, and the source is precise:
enrolling the same device twice leaks more than one enrolment does, because the debiasing
step is stochastic and bit errors between enrolments shift which pairs are retained.

This project's registry has a slashing path and no stated position on re-registration.
`ChipRegistryV2` binds a nonce per chip and rejects double registration, which reads like
one enrolment per device, but nothing states it as a requirement or explains what happens
after a slash. If a die can ever be enrolled twice - after a slash, after key rotation,
after a failed provisioning run - the three efficient methods are unavailable and only
e-2O-VN remains.

Its debiasing overhead is 1.00 because it discards nothing, replacing unretained pairs
with erasures. The cost reappears as a longer inner repetition code, from 20 to 28 bits as
bias worsens in the paper's design. That cost has not been derived for a BCH-only design
and should not be guessed.

What can be stated: the choice between one enrolment per device and many is a
silicon-area decision as well as a protocol one, and the registry does not currently
record which it is. Closes when the registry states its enrolment policy.

## W-INTL-70  The instrument that answers the remaining questions is built and costs 0.69 tiles

Severity: this is not a weakness. It is the work every entry from W-INTL-60 onwards has
been pointing at.

Three quantities of this process decide everything still open: the bit error rate across
temperature, the min-entropy per oscillator, and the bias. One structure yields all three.

Built 2026-07-30. It emits one frequency count per oscillator per sweep and nothing else -
no comparator, no arbiter, no response bits. A structure emitting response bits could only
report the error rate of the pairing wired into it, and the pairing is exactly what is in
question. Pairing, discard thresholds, bias and entropy under any scheme are computed
afterwards from the counts, and can be recomputed when the question changes.

Verified against arithmetic: oscillators modelled as square waves of known distinct
periods, counts asserted within three of the window divided by the period, and the
frequency ordering asserted to be preserved. Two injected faults - removing the
synchroniser, and failing to clear the accumulator between oscillators - each fail 14
checks.

Worth recording: the first run failed eight checks and every one was in the test model
rather than the circuit, because half-periods are integers and odd periods collapsed onto
their even neighbours. An instrument's own test is an instrument.

| Component | Area | Tiles |
|---|---|---|
| Readout for a 272-oscillator bank | 5,223 | 0.29 |
| The 272 oscillators | 7,151 | 0.40 |
| Total | 12,374 | 0.69 |

The measurement that decides whether the identity root fits in sixteen tiles costs 0.69 of
one.

It is an instrument, not a key generator, and must never ship in a part that holds a
secret: raw frequency counts are exactly what an attacker wants and exactly what a key
generator must never expose. That should be stated wherever this block is referenced.

## W-INTL-71  The only reusable debiasing method does not exist for this construction

Severity: this resolves W-INTL-69 by removing the choice it described.

W-INTL-69 left the cost of e-2O-VN underived and said it should not be guessed. Derived
2026-07-30, and the answer is not a cost.

e-2O-VN keeps every position, turning unretained pairs into erasure symbols. A pair is
retained when its two bits differ, so the erasure fraction is p^2 + (1-p)^2 - a half at 50
percent bias, more as bias worsens. A code of distance d corrects e errors and f erasures
when 2e + f <= d-1, and for BCH d-1 = 2t. Per 127-bit block the erasures alone run from
63.5 to 79.4, against a budget of 62 for the strongest BCH(127) code that still carries
information. BCH cannot absorb this at any bias level.

That is why the source puts a repetition code innermost. It cannot be afforded here, and
the reason is structural. Residual min-entropy is rho*n - (n-k), so a 128-bit key needs
k >= 128 + n(1-rho), and since rho <= 1 for any source, k >= 128 always - a construction
cannot yield more key than its code carries information. A repetition code multiplies n and
leaves k alone, so it only moves the inequality the wrong way: rep[3] + BCH(127,15) would
need rho >= 1.30, and rep[20] would need 1.04. Both impossible for any source, not merely
for this one.

So the reusable option is not expensive here; it does not exist. One enrolment per device
is the only constructible policy.

`ChipRegistryV2` has been updated to state that as a requirement rather than leave it as
behaviour, and to explain why, on the open pull request. Two paths were already closed - a
registered chip is refused, and a slashed chip is refused because slashing sets a flag
without clearing registeredAt. The second is easy to break by a well-meaning change:
clearing the record on slash, or adding an unregister path, would read like tidying up and
would silently make the key generator insecure. `test_slashedChipCanNeverReRegister` now
refuses re-registration after a slash with a fresh nonce and a valid signature, and from a
different submitter in case the record were ever keyed on the attestor. Injecting the
tidy-up makes it fail. 14 tests pass.

Not merged. The registry sits in front of the token supply and was written and tested by
one party; that position has not changed.

## W-INTL-72  The entropy margin is the tightest figure in this work

Severity: high, and it is a sensitivity rather than an error.

Falling out of the same inequality as W-INTL-71. Nineteen blocks of BCH(127,15,27) give n
total 2,413 and k total 285, against a requirement of 128 + n(1-rho) = 269.4 at the
measured rho of 0.9414. The margin is 15.6 bits.

Turned around: the construction needs rho >= 0.9349, and the measured figure is 0.9414. The
margin is 0.0065 in entropy density, under a percentage point - and the measurement comes
from ring oscillators on FPGAs, in a dataset gathered by other people for another purpose,
on a different process from the one this project would use.

Blocks buy margin linearly, since residual scales with block count while the per-block
requirement does not: 25 blocks tolerate rho >= 0.9302, at proportionally more raw response
bits and oscillators. The dial exists and is currently at its tightest useful setting.

Nothing else in this project turns on a number this close to its limit. It should be the
first thing checked against the characterisation structure's output, ahead of the error
rate, because a shortfall here is not a matter of needing a stronger code - it means the
construction yields no key at all.

## W-INTL-73  Every synthesis figure now reproduces in one run

Severity: none. Recorded because the alternative was quietly accumulating.

The areas in this project were gathered over six loops as individual synthesis invocations
and typed into documents by hand. Checking one meant reconstructing a session's shell
history, and a change of standard-cell library or tool version would have gone unnoticed
until it contradicted something else.

`research/rtl/measure_all.sh` runs every probe and prints the table. It runs the six
testbenches first and refuses to print any area if one fails, because the rule this project
adopted is that no area is quoted for a circuit that has not decoded correctly - and a
script that printed areas without checking would have quietly broken the rule it exists to
serve.

Run 2026-07-30: six testbenches pass, eight areas reproduce exactly the figures the
documents quote.

## W-INTL-74  The code was inherited from a paper along with that paper's operating point

Severity: high. It explains W-INTL-72 rather than merely improving on it.

BCH(127,15,27) came from Gao et al. and is the right code for their constraints: an SRAM
PUF with near-full entropy density and a bit error rate around ten percent. This project
has ring oscillators, a measured entropy density of 0.9414, and an unknown error rate.
Adopting a parameter choice along with a method carries the source's operating point
silently, and W-INTL-72 was the bill for that: the entropy margin turned out to be the
tightest number in the entire analysis.

The parameter space has now been searched rather than borrowed. Code parameters are
computed rather than looked up - the generator polynomial is the lcm of the minimal
polynomials of alpha^1 through alpha^2t, and the degree of each is the size of a
cyclotomic coset, so the parity count is the size of a union of cosets. `bch_code_search.py`
computes it and refuses to search unless the result reproduces every BCH code named in the
sources this project has read. All four reproduce.

The lesson generalises past this decision. Several figures in this project came from papers
whose operating points were never compared with this project's. Where a source supplies a
method, take the method; where it supplies a parameter, check the constraints it was chosen
under.

## W-INTL-75  A smaller code with four times the margin, measured

Severity: this is not a weakness. It supersedes the recommendation in W-INTL-64.

| Construction | Tiles | Entropy margin | Max BER | Raw bits |
|---|---|---|---|---|
<!-- derived:external --> | BCH(127,15,27), inherited | 6.07 | 0.0157 | 6.96 percent | 2,921 |
<!-- derived:external --> | BCH(127,22,23) | 5.22 | 0.0708 | 5.23 percent | 2,921 |
<!-- derived:external --> | BCH(255,47,42), fallback | 11.86 | 0.0801 | 7.02 percent | 2,805 |

Every decoder area measured and every decoder verified end to end before its area was
quoted, including in GF(2^9) - a field this project had never used, which the generator and
the parameterised solver both handled without change.

BCH(127,22,23) is smaller than the inherited choice and carries four and a half times the
margin on the binding constraint, at the cost of a quarter of the error tolerance. That is
the right direction to trade: a shortfall in entropy density yields no key at all, while a
shortfall in error rate calls for a stronger code.

Two qualifications. Part of the inherited choice's margin as reported here - 0.0157 rather
than the 0.0065 in W-INTL-72 - comes from spending the whole raw-bit budget on blocks
rather than stopping at the minimum. That improvement was free and available all along and
was not taken, which is its own small finding. And BCH(255,47,42) buys a little more margin
and better error tolerance for more than double the area; it is the fallback if measurement
shows both quantities worse than expected.

## W-INTL-76  The best-margin code is excluded by measurement, not by estimate

Severity: none. Recorded so the search is not re-run in hope.

BCH(511,139,54) has by far the best entropy margin in the admissible set, 0.1633 against
0.0708 for the recommendation. Its decoder measures 304,465 square micrometres - 16.88
tiles, more than the entire sixteen a submission may use, before a single oscillator is
placed.

It was verified end to end and synthesised rather than estimated, because an estimate would
have left the option open and the search will keep surfacing it. The whole n=511 family is
excluded on the same grounds: the key-equation solver needs about 3(t+1) general multipliers
of m bits, and both factors are at their largest there.

## W-INTL-77  The oscillator floor asked for raw entropy where residual was needed

Severity: critical for correctness, small for area, and that combination is what makes it
worth its own entry.

Found while checking whether the new code moved the oscillator floor. It did not. The
floor was wrong.

The figure in use was 272 oscillators, computed as 128 divided by the measured 0.471 bits
per oscillator. That asks for 128 bits of raw entropy. What is needed is 128 bits
surviving publication of the helper data - the distinction W-INTL-59 drew for response
bits six loops ago, drawn there and left undrawn here. Two accountings feed the same
inequality; one was corrected and the other kept the original error.

With 2,415 bits of leakage, the requirement under reuse is log2(R!) >= 2,543. At 272
oscillators the ordering carries 1,813 bits, so the residual is -602: the construction
yields no key at all. The correct floor is 360.

| Construction | Reuse area as published | Corrected |
|---|---|---|
| BCH(127,22,23), current | 5.22 tiles | 5.34 tiles |
| BCH(127,15,27) | 6.07 tiles | 6.22 tiles |
| BCH(255,47,42) | 11.86 tiles | 11.96 tiles |

The area moved by two percent and the validity moved from no to yes. A wrong figure that
barely changes the answer is the hardest kind to notice, and it survived because every
review of the reuse column was a review of its plausibility as an area.

Method point worth carrying: when a correction is made to one accounting, look for the
other accountings that feed the same inequality. This one had been sitting beside a
corrected sibling for six loops.

## W-INTL-78  The chain runs end to end, and the model has a second witness

Severity: this is not a weakness. It closes the gap W-INTL-66 identified in the RTL and
extends the same discipline to the model.

Every part of the key generator had been verified separately and the chain had never been
run - the arrangement in which a defective Chien search survived five loops of correct
area measurements.

`research/key_generator_e2e.py` runs it in software: a modelled oscillator bank at a
stated bias, pairing, syndrome-based helper data, enrolment, noisy regeneration, decoding,
recovered key. Same construction as the RTL and the same inversionless iteration, written
independently of it.

| Bit error rate | Trials | Observed failure | Model prediction |
|---|---|---|---|
| 0.04 | 300 | 0.000 | 5.71e-09 |
| 0.06 | 300 | 0.000 | 1.23e-05 |
| 0.08 | 200 | 0.000 | 0.00152 |
| 0.10 | 120 | 0.025 | 0.0384 |

Agreement across four orders of magnitude, the one non-zero observation within sampling
error. Keys round-trip at zero and two percent noise at two bias levels. Blocks corrupted
beyond the correction radius were refused or returned wrong in 40 of 40 cases rather than
silently returning a plausible response.

The model in `code_choice_model.py` had been the sole basis for every code decision in
this project. It now has an independent implementation agreeing with it.

## W-INTL-79  Every borrowed constant, with the operating point it arrived with

Severity: medium, and it is the systematic application of W-INTL-74 rather than a new
finding.

**Min-entropy density 0.9414** - Wilde, Hiller and Pehl, from 512 ring oscillators on each
of 193 Xilinx Spartan-3E parts at room temperature, paired disjointly with immediate
neighbours. The same paper shows two published figures from identical raw data disagreeing
widely depending on whether compared oscillators are adjacent or distant. This project
would use a 130 nm open process with unspecified layout. It is the tightest input in the
analysis and carries the largest caveat.

**Debiasing overheads 1.58 to 5.3** - Maes et al., computed for a 1,000-bit output at
failure rate 1e-6. The overhead depends on output length through an inverse binomial, so
scaling to a different length is an approximation, not a lookup. Not corrected for, and it
should be before any of these sizes a design.

**Oscillator area 26.3 square micrometres** - seven inverters, from the published Tiny
Tapeout implementation. Mansouri and Dubrova state the minimum for a usable frequency is
typically ten to twenty inverters, so this may be an atypically short oscillator and a
conventional bank could be one and a half to three times the area. It changes no
conclusion, which is why it went unexamined.

**Target of 171 error-free bits** - Bosch et al., from SRAM PUF entropy. Now vestigial,
used only on the inadmissible path in the model since the leakage inequality is applied
directly. Should be removed rather than left looking load-bearing.

**Tile geometry** - Tiny Tapeout, and the only borrowed constants here that are a
published specification rather than someone else's measurement.

## W-INTL-80  The debiasing overhead is computed now, and the borrowed figures were conservative

Severity: low as an error, and it closes the one item W-INTL-79 flagged as knowingly wrong.

Maes et al. compute their overheads for a 1,000-bit output; this construction needs 2,921.
The overhead depends on output length through an inverse binomial, so scaling their figures
was an approximation rather than a lookup, and this project had been doing that.

Implemented rather than borrowed. For an n-bit response at bias p the retained count is
binomially distributed with parameters (floor(n/2), 2p(1-p)), and n must be large enough
that the failure-rate quantile still reaches the required output length. The implementation
reproduces all three figures the paper states - 4,446 and 2,322 at fifty percent bias,
5,334 at thirty - exactly.

Rescaled to 2,921 bits, every figure is three to five percent lower than the one borrowed:
CVN 4.26 against 4.40, 2O-VN 2.18 against 2.31. Relative binomial fluctuation shrinks as
the output grows, so less slack is needed. The project was conservative rather than wrong,
which is the better direction to have erred.

No conclusion moves. At 2.18 the disjoint arrangement still needs 23.4 tiles.

## W-INTL-81  Debiasing in the chain, and a third witness for the formula

Severity: this is not a weakness.

The end-to-end run now includes the debiasing stage. Across twelve trials at each of four
method-and-bias combinations, the retained counts run from 3,050 to 3,344 against the 2,921
the construction needs - clearing it every time, with the margin a constraint sized for one
failure in a million should leave.

The stage also does what it is for, demonstrated rather than cited: sources at bias 0.50,
0.30 and 0.20 yield retained bits at 0.4999, 0.5014 and 0.4995 over tens of thousands of
bits.

So the debiasing sizing now has three independent witnesses: the paper's stated figures,
the constraint implemented from its definition, and a Monte Carlo of the chain.

## W-INTL-82  The answer is flat across a six-point band and then stops

Severity: this is the most useful framing this analysis has produced, and it replaces the
margin in W-INTL-72 rather than contradicting it.

The entropy density is the weakest input in this work - measured on Spartan-3E parts, at
room temperature, with adjacent pairing, by other people for another purpose. Reporting a
conclusion at one value of it is reporting a conclusion at someone else's operating point,
which is the error W-INTL-74 was written about.

Across the plausible range, restricted to codes whose decoders have been measured:

| Entropy density | Best code | Tiles | Max BER |
|---|---|---|---|
<!-- derived:external --> | 1.00 down to 0.88 | BCH(127,22,23) | 5.34 | 5.23 percent |
| 0.87 and below | none among measured codes | - | - |

The recommendation does not move at all between 0.88 and 1.00 - same code, same area, same
error tolerance - and then stops. The measured value sits 0.07 above the edge.

That is a better shape of answer than a margin. A margin invites the question of how much is
enough; a flat band with an edge says the decision is insensitive to the weak input over a
wide range, and names the point where it is not.

Two qualifications. The edge is an edge in the measured set: the search finds codes with
margin down to 0.78, but their decoders are unmeasured or, for the n=511 family, measured
and too large. Below 0.87 the answer is not that nothing works, but that nothing measured
works and finding out means measuring more. And the band's flatness is partly an artefact of
five measured codes; a denser set would probably show area falling as density rises. The
part that would survive is that nothing changes across a six-point range.

## W-INTL-83  The reuse claim that set the contract policy, checked on this construction

Severity: medium. The policy stands; the justification needed the check it had not had.

`ChipRegistryV2` refuses re-registration, and the reason written into it is a claim from
Maes et al.: classic and pair-output von Neumann debiasing are not reusable, so enrolling
the same device twice leaks more than once does. That claim was taken on faith, and it had
already determined a contract.

It needed checking because the paper demonstrates it on a construction this project does
not use - its figure has an inner two-bit repetition code and reasons about which bits
share a codeword, and there is no repetition code here. What generalises is the sentence
beside the figure rather than the figure: enrolled bits can shift between code words,
because the debiasing step is stochastic and bit errors between enrolments change which
pairs are retained.

Demonstrated here. A 12,432-bit raw response, a second measurement of the same device
differing in 259 bits at two percent noise: enrolment one retains 3,062 bits and enrolment
two 3,057; the public retention patterns differ at 253 pairs; and of the 2,794 pairs
retained in both, 124 land in a different BCH block the second time - four and a half
percent, with every pair after the first divergence displaced.

So each enrolment publishes a syndrome over a different partition of the same raw bits.
The mechanism applies to this construction and the policy stands on it.

What this does not do: it demonstrates the mechanism, not the quantity. That bits shift
between blocks is shown; that two enrolments leak strictly more than one follows; how much
more has not been computed. The policy is conservative either way, since it forbids the
second enrolment outright.

The general point is the one from W-INTL-74 a level up: a conclusion was borrowed and
acted on, and the borrowing was from a construction with a component this project does not
have. Checking cost an hour and the claim survived. It might not have.

## W-INTL-84  The flat band survived densification, and the sweep's granularity had hidden the edge

Severity: none as a defect. It answers the qualification W-INTL-82 attached to itself.

W-INTL-82 reported the recommendation as flat from entropy density 0.88 to 1.00 and
qualified it: with only five measured decoders the flatness might be an artefact, and a
denser set would probably show area falling as density rises.

Three more codes were generated, verified end to end and measured - BCH(127,8,31) at
116,194 square micrometres, BCH(255,45,43) at 211,985, BCH(255,37,45) at 222,024 - chosen
to populate the band and probe below its edge.

Swept at one-hundredth intervals over eight measured codes, the answer changes in exactly
two places: BCH(127,22,23) at 5.34 tiles from 1.00 down to 0.88, BCH(255,47,42) at 11.96
tiles at 0.87, and nothing measured at 0.86 and below.

The qualification is answered. None of the three new codes improves on the recommendation
anywhere in the band, so the flat stretch is a property of the problem rather than of the
sample.

Two things sharpened. The edge is at 0.8613, not 0.87: the earlier sweep stepped in units
of 0.02 and hid a code working just below its resolution, which is worth recording as a
reminder that a sweep's granularity is part of its result and should be reported with it.
And between band and edge there is a single step rather than a slope - one point of entropy
density costs more than double the area, because it forces the move from GF(2^7) to GF(2^8)
and a correction strength of 42.

## W-INTL-85  Sweeping one input at a time reversed the priority; both at once gives a rectangle

Severity: high as a correction. It overturns the ordering stated in W-INTL-82 and repeated
since.

Every sweep in this project moved the entropy density while holding the error-rate
requirement at five percent, and concluded that the error rate was the least decisive of the
three quantities. Both come from the same characterisation structure, so the pair is what a
single fabrication returns, and holding one fixed was an artefact of how the analysis grew.

Mapped across ten measured decoders, the error rate has a cliff at eight percent and the
entropy density has one at 0.8155. Published ring-oscillator error rates across temperature
reach eight percent far more readily than published entropy figures approach 0.82, so the
error rate is at least as binding - the opposite of what was concluded.

The useful shape is a rectangle rather than a band: entropy density at or above 0.82 with
error rate at or below four percent gives 4.92 tiles, and nothing inside it changes the
answer.

Method point: a sensitivity analysis over one variable at a time answers a question nobody
asked, when the variables arrive together from one measurement.

## W-INTL-86  The densification that answered a qualification sampled the wrong region

Severity: medium, and it is a correction of the inference in W-INTL-84 rather than of its
measurements.

W-INTL-84 answered a caveat about a sparse sample by measuring three more codes and
reporting that the flat band was a property of the problem rather than of the sample. Those
three were chosen to populate the band and probe just under its edge.

Two more codes, chosen further below the edge, moved the whole picture. BCH(127,29,21) at
79,787 square micrometres is cheaper than the recommendation it challenges - 4.42 tiles of
decoder against 4.82 - and tolerates entropy density down to 0.8155 against 0.8706, at the
cost of error tolerance, 4.42 percent against 5.23. BCH(255,55,31) at 152,170 extends the
same direction.

The flatness held where it was sampled and did not hold where it had not been. The earlier
measurements were right and the inference from them was not: densifying inside a region
already believed flat tests almost nothing. A qualification about a sample is answered by
sampling where the sample is thin.

The edge moves from 0.8613 to 0.8155, and the cheapest configuration from 5.34 tiles to
4.92.

## W-INTL-87  The re-enrolment leak, measured on an instance small enough to enumerate

Severity: none as a defect; it closes the gap W-INTL-83 left open explicitly.

W-INTL-83 demonstrated the mechanism and said the quantity had not been computed. Computed
now by exhaustive enumeration rather than bounded: sixteen-bit raw response, classic von
Neumann, six-bit response, three-bit syndrome, second enrolment differing in at most two raw
bits, sixty devices, candidate keys counted over all 2^16 raw strings.

One enrolment leaves 8.0 candidate keys, 3.00 bits. Two leave 4.9, 2.30 bits. The second
enrolment removes 0.70 bits of 3.00 - about a quarter of what remained - and strictly reduced
the candidate set in 39 of 60 cases.

This is a toy, and whether the fraction scales to a 2,921-bit response is not established.
What it establishes is that the leak is a substantial fraction rather than a negligible one,
which is what the contract's enrolment policy needed and did not have when it was written.

## W-INTL-88  The blank high-error column is answered, and one cell remains blank on purpose

Severity: this is not a weakness. It closes the worst blind spot in the analysis - the one
that would have been discovered after fabrication.

W-INTL-85's map had no answer at eight percent bit error rate or above below entropy density
1.00. Published ring-oscillator error rates across temperature reach that range, so an empty
cell there was the most consequential gap in the work.

Three codes measured, chosen for the blank regions rather than the populated ones:
BCH(255,29,47) at 231,431 square micrometres tolerating 8.34 percent and needing 0.9319;
BCH(255,21,55) at 268,820 tolerating 10.54 percent and needing 0.9633; BCH(255,63,30) at
147,563 tolerating 4.11 percent and needing only 0.7986.

At the measured entropy density the project now has a construction up to eight percent, at
13.37 tiles of the sixteen available. Expensive, and a design at 84 percent of budget beats a
blank cell.

The n=511 family is excluded without further measurement, by a measured point plus
monotonicity rather than an estimate: its decoder at t=54 measures 16.88 tiles, already over
the whole budget, and area increases with t at fixed field, while every n=511 candidate needs
t of 85 or more.

What stays blank: nine percent and above at the measured entropy density, which would need
0.98 - higher than anything measured anywhere. If the real bank is both noisy and ordinary
there is no construction here for it. That is now a statement about one cell rather than a
general unknown, which is the useful form.

## W-INTL-89  The leak does not shrink with scale, and the fraction quoted was over-specific

Severity: low as a correction, and it settles the question the enrolment policy turned on.

W-INTL-87 measured the second enrolment removing 0.70 bits of 3.00 on a sixteen-bit instance
and said the scaling was unestablished. Tested across five sizes at roughly constant residual
entropy, the absolute loss grows monotonically: 0.15 bits at twelve raw bits, 0.17 at
fourteen, 0.49 at sixteen, 0.66 at eighteen, 0.78 at twenty.

It does not shrink, which is the question that mattered - a leak vanishing at scale would
have made the enrolment policy optional.

Two corrections to how W-INTL-87 stated it. The fraction is not a constant: the same
sixteen-bit size gives 23 percent there and 12 percent here, differing only in which parity
checks the toy uses. So the leak depends on the code and quoting a single percentage was
over-specific. And five points from twelve to twenty raw bits do not extrapolate to 12,432 -
the direction is established, the value at scale is not.

The policy stands on the direction rather than the value, since it forbids the second
enrolment outright and is therefore correct whether the leak is a fifth or a half.

## W-INTL-90  Power was never in the constraint set; checked, and it is slack

Severity: none as a defect, and it is worth recording because of why it was missing.

Thirteen decoders had been sized purely on area. Tiny Tapeout gives 1.8 volts for the
digital core and states that around 20 milliamps produces a 0.1 volt drop through the power
delivery network, roughly five ohms; no per-project power limit is published, so that drop
is the practical constraint.

Estimated from the liberty rather than guessed - input pin capacitance summed per
instantiated cell, activity factor stated as the one assumption. BCH(127,29,21) has 10,586
cells and 36.0 picofarads of switched capacitance, reaching 20 milliamps only at 2,059
megahertz at fifteen percent activity; BCH(255,21,55) has 35,643 cells and 121.7 picofarads,
reaching it at 609 megahertz. At ten megahertz the larger draws 0.33 milliamps and drops 1.6
millivolts, and the decoder runs once at power-up for a few thousand cycles.

Two limits on the figure, neither of which changes the answer. It counts gate capacitance
and not interconnect, which at 130 nanometres can be comparable, so the true current could
be two or three times higher - at three times the constraint still binds only above 200
megahertz. And the leakage extracted comes to fractions of a microwatt, low enough that the
units are probably being misread, so it is not relied on; a thousand times more would still
be 61 microamps.

The finding is that a whole constraint was absent from the analysis and turns out to be
slack. Recorded rather than dropped because the reason it went unexamined - area was the
interesting axis - is exactly the reason a binding constraint would also have gone
unexamined. Three reversals in this project came from missing constraints.

## W-INTL-91  The last blank cell is provably empty rather than unmeasured

Severity: this is not a weakness. It converts an open gap into a closed result.

W-INTL-88 left one cell blank: nine percent bit error rate or above at the measured entropy
density of 0.9414. Enumerated over every narrow-sense binary BCH code from GF(2^6) to
GF(2^10), exactly three satisfy both the leakage inequality and the nine percent target -
BCH(511,76,85), BCH(511,67,87) and BCH(511,58,91). All three are n=511, and that family is
excluded by the measured point at t=54, whose decoder is 16.88 tiles, already over the whole
budget, plus monotonicity of area in t at fixed field.

So the cell is empty, not unmeasured. No single BCH code answers nine percent at this entropy
density within sixteen tiles, and concatenation cannot help because it multiplies code length
while leaving dimension alone, which is what makes the leakage inequality fail. Closing it
needs a larger area allocation, a different code family, or a lower error rate.

That is more useful than a gap. A gap invites another loop of measurement; a proof redirects
effort to the error rate.

## W-INTL-92  The oscillator length caveat is discharged by test

Severity: none. It closes a caveat carried for four loops on the grounds that it probably did
not matter.

The oscillator area of 26.3 square micrometres assumes seven inverters, from the published
tile, where the literature calls ten to twenty typical for a usable frequency. Tested at
seven, fourteen and twenty: the cheap cell moves from 4.92 to 5.42 to 5.85 tiles, the
expensive one from 13.37 to 13.91 to 14.37, and no cell changes from fitting to not fitting.

Tripling the length costs nineteen percent in the cheap cell and eight in the expensive one.
The caveat is discharged, and the test cost one calculation - which is the point. A caveat
carried because it probably does not matter is a caveat nobody can act on.

## W-INTL-93  Thirteen designs had no timing, and the file's own architectural claim now has a measurement

Severity: none as a defect. It closes the last dimension nobody had checked.

None of the thirteen decoders had closed timing, and `bm_area_probe.v` says so in its header:
the critical path is one general multiply, an XOR tree over t+1 terms, and a second multiply,
with a systolic reformulation available if the clock matters. Nobody had checked what clock it
reaches.

No static timing analyser is installed, so the measurement is logic depth - the longest
topological path through the netlist, reported by the synthesiser. Eighteen levels at t=4 in
GF(2^8), seventeen at t=23 in GF(2^7), twenty-one at t=18, twenty-three at t=55.

The depth grows logarithmically in t, which is exactly what the header predicted: two
multipliers at about m levels each plus a tree of log2(t+1), so sixteen plus six at t=55
against twenty-three measured. The file's architectural claim is now confirmed by measurement
rather than restated.

At the per-level delays in the liberty - 220 to 350 picoseconds for the two-input gates the
mapper uses - the solver reaches roughly 145 to 300 megahertz. Against a user clock of a few
tens of megahertz that is threefold to thirtyfold of margin.

Two limits: the depth is measured before technology mapping, which both merges levels into
complex cells and inserts buffers, so it is a proxy; and there is no wire delay.

## W-INTL-94  The power extraction has a second witness, which also settles the units doubt

Severity: none as a defect, and it resolves a doubt W-INTL-90 raised about its own method.

W-INTL-90 estimated dynamic current from input pin capacitance and flagged that the leakage
from the same library looked implausibly small - a sign the units might be misread, which is a
reason to distrust the whole extraction rather than only the leakage.

Recomputed through a different part of the library: energy per switching event from the
internal_power tables. BCH(127,29,21) reaches 20 milliamps at 2,059 megahertz by the
capacitance route and 2,540 by the internal-power route; BCH(255,21,55) at 609 and 741. Both
agree within twenty percent.

That is a second witness for the dynamic figure and, more usefully, it validates the units
interpretation the leakage anomaly had called into question.

Interconnect, which the capacitance route omits, is not negligible: at 130 nanometres a local
net carries roughly one to two femtofarads, comparable to the gate capacitance rather than a
correction to it. Including it, BCH(255,21,55) reaches 20 milliamps at 384 to 471 megahertz.

## W-INTL-95  Timing binds before power, against the intuition

Severity: none. Recorded because the ordering is the useful part.

For the largest decoder, timing runs out at 145 to 300 megahertz and power at 384 to 471.
Timing is the tighter of the two - which the intuition had backwards, since a design with
35,643 cells sounds like a power problem and is a depth problem.

Neither binds. The user clock is a few tens of megahertz and the decoder runs once at power-up
for a few thousand cycles, so both have at least an order of magnitude in hand.

Three dimensions have now been checked that the analysis did not originally have - power,
timing and interconnect - and all three are slack. Three for three, and the reason to keep
checking is that the fourth might not be.

## W-INTL-96  The solver does own the critical path, and one property predicts both ratios

Severity: none as a defect. It closes an assumption W-INTL-93 rested on without stating it.

W-INTL-93 measured the solver's depth and gave a clock without measuring the other two
stages, so the conclusion assumed the solver is deepest. The Chien search carries an XOR tree
over t+1 terms too.

Measured at t=55 in GF(2^8): syndrome bank six levels, Chien search eleven, both table stages
together eleven, solver twenty-three. The solver is roughly twice either, so it does own the
path.

The reason is the property that also made it three times the area: its multiplies are between
two runtime values at about m levels each, while the table stages multiply by compile-time
constants that fold into shallow trees. Chien's eleven is a constant multiplier of about five
plus log2(56); the solver's twenty-three is two general multipliers of eight plus the same
tree. One architectural property predicts both the area ratio and the depth ratio.

## W-INTL-97  Depth after mapping, and a path tracer that returned a meaningless number

Severity: low, and the failure is worth more than the correction.

W-INTL-93's depth was measured before technology mapping and flagged as a proxy. Measured
after mapping, with the flip-flops left generic so the path tracer cuts at them: seventeen
levels become thirteen at t=23, twenty-three become seventeen at t=55. The mapper removes about
a quarter of the depth, so the earlier figure was conservative rather than optimistic.
Corrected, the solver reaches 220 to 350 megahertz at t=23 and 168 to 267 at t=55.

The first attempt is the part worth recording. Reading the standard-cell library as blackboxes
makes the path tracer fail to recognise the sequential cells, so it walks straight through them
and reports a path of 1,709 levels at t=23 and 5,208 at t=55. Those numbers look like depths.
They were caught only because they were absurd - the same error producing a figure three times
the truth would have been quoted without question.

The rule that follows: a measurement tool given a netlist it partly does not understand
returns a plausible-shaped wrong answer, and the defence is a sanity range computed before
running it, not after reading the output.

## W-INTL-98  Eleven constraints, in one list, and six more named as unchecked

Severity: medium as a finding about the process rather than the subject.

`research/constraint_register.md` now lists every constraint this analysis has checked, with
its source and whether it binds. Six bind, one binds as policy, four are checked and slack.

The register exists because the absence of one caused three reversals: a code chosen on area
that failed the error target (W-INTL-57), a replacement that failed the leakage bound
(W-INTL-63), and a priority ordering that was an artefact of sweeping one input while holding
another (W-INTL-85). Each time the missing constraint was written down somewhere in a source
and not in this project.

Six are named as unchecked, ordered by what a bad answer would cost:

Helper-data manipulation by an active adversary is first. Gao et al. state that not all codes
and decoding strategies guarantee security of the derived key and that resistance to
manipulation must be evaluated alongside overhead. This project uses syndrome-based helper
data, which they chose partly for that reason - and the argument was inherited rather than
reproduced. That is the same pattern as the reuse claim in W-INTL-83, which was checked and
held.

Then: aging of the oscillators, which the literature reports as the weaker of the two
robustness properties while every error figure here is a fresh-device figure; synchroniser
metastability in the characterisation structure, which nothing names and which is an omission
of mine; process corners, since every figure is typical-corner; routing feasibility at 84
percent tile utilisation; and the 128-bit target itself, inherited and never questioned
against what the registry needs.

## W-INTL-99  Cell area was divided by die area, and the utilisation factor was dropped seventeen loops ago

Severity: critical. It makes every tile figure in this project optimistic by a factor of 1.7
and reopens two cells that W-INTL-88 reported as answered.

Cell area is not die area: a placed and routed block needs room to route. The fraction of a
Tiny Tapeout tile that ends up as standard cells was measured in the first pass of this work,
on the published tile the oscillator areas come from - it declares 1x2 tiles, 36,064 square
micrometres, and holds 20,900 of cells, so 58 percent, from the same flow on the same process.
`puf_tile_budget.md` records it and applies it.

It was then abandoned. Every figure computed after the code-choice work began divides cell
area by the raw tile area.

At the measured utilisation the recommendation moves from 4.92 to 8.49 tiles, and the seven and
eight percent error-rate columns stop fitting: the design covers up to six percent at 10.73 of
sixteen tiles and nothing above. W-INTL-88's headline is withdrawn.

Three things about the failure, which is more useful than the number.

It was inside a constraint already marked binding. The register written last loop lists tile
area as binding, with a status and a source. The row was right and its arithmetic was wrong. A
register records which constraints exist and does not check the computation behind each, so
writing one is not a substitute for recomputing.

The factor was not missing, it was abandoned - measured, recorded, used, then dropped when the
analysis moved to a second document that started from cell areas rather than from the first
document's conclusions. A number carried between files by hand is a number that eventually is
not carried.

And the last two loops checked three constraints, found all three slack, and said that was not
evidence the next would be. It was not the next constraint that bit. It was one already in the
list.

## W-INTL-100  Synchroniser metastability, closed with a margin that collapses fast

Severity: none. It closes the one register entry named as my own omission rather than a
source's.

The characterisation structure samples free-running oscillators through two flip-flops.
Computed on the standard two-parameter model at the pessimistic end of published 130 nanometre
figures - settling time constant 300 picoseconds, metastability window 100 - the resolution
time at a 10 megahertz clock is 300 time constants and the mean time between failures is 10^120
years. Two stages is overkill rather than conventional, because the structure counts a
prescaled oscillator over a long gate window so the asynchronous event rate is low.

Worth keeping the shape rather than the number: the margin falls from 10^120 years to 10^14 at
50 megahertz and to 10 years at 100. Closed for this design at this clock, not a general result
about the structure.

## W-INTL-101  Helper-data manipulation is located rather than verified, and the abstract says something worse

Severity: high, and it is now specific rather than vague.

The register put this first among unchecked items because it is a security property whose
reasoning was inherited. Chased, with a partial outcome.

Gao et al. state it in their own words - their case study employed BCH codes and syndrome
decoding, which has been shown to be secure under helper-data manipulation attacks, citing
Becker. That was read directly from their paper, so the claim is located.

Becker's own text could not be reached: the preprint returns 403 to an unauthenticated fetch
and the abstract names no code. So the specific claim of immunity remains second-hand, and this
project's construction rests on someone else's summary of a paper this project has not read.
Not closed.

What the abstract does establish is worse than the claim it fails to confirm. The provably
secure robust construction does not meet the error-correction requirements of practical PUF
applications; extractors that do meet them cannot be extended to robust ones because of a
strict bound on correctable errors; and the new attacks work even against robust-like
constructions built without that bound.

So no construction in this space has both a robustness proof and practical error correction,
and this project's has no robustness proof either whatever its resistance to those specific
attacks.

That does not change what to build, since no alternative has a proof. It changes what may be
claimed: any statement that this identity root resists an adversary who can tamper with helper
data would rest on a second-hand summary. The honest position is that the question is open and
the field says so.

Closes when Becker's text is read. Until then the application must not claim resistance to
helper-data manipulation.

## W-INTL-102  A check that compares a document against a computation, and a fourth broken control

Severity: none as a defect. It closes the class W-INTL-99 belongs to.

Every check in this project compared documents with each other, which is why W-INTL-99 survived
eighteen loops: the prose said 4.92 tiles, the script computed 4.92 tiles, and both were wrong
together because they shared the same missing step. Cross-document agreement cannot catch a
shared omission.

`scripts/check_figures_reproduce.py` recomputes the headline from its inputs and fails if a
document disagrees. It is in CI. Three negative controls fire: dropping the utilisation factor
makes the seven and eight percent columns fit again and the check names the cause; changing a
decoder area by ten percent makes the recomputation disagree with the ledger; changing the
ledger while leaving inputs alone does the same in the other direction.

A fourth did not fire, and that is the part worth keeping. I copied the script to a temporary
directory to inject the fault, which moved the repository root two levels up, so the ledger
comparison silently did nothing and the run printed a clean pass. `check_consistency.py` carries
a warning about exactly this in its header, written after two controls failed the same way. Third
time.

## W-INTL-103  Stale pre-correction figures in the ledger, found by accident

Severity: low, and it is a second instance of the drift in W-INTL-99 rather than a new class.

The ledger's headline had been corrected to 8.49 tiles while two earlier sentences in the same
row still carried 4.92 and 5.34 - the values W-INTL-99 invalidated. One sentence was updated and
the others were not.

Found while inspecting what the new check's regular expression matched, not by the check itself,
which verifies one figure. Corrected. The lesson is narrow and real: a correction applied to a
document is applied to the sentence in front of you, and the same number in the same row three
sentences earlier does not follow.

## W-INTL-104  The remaining binding rows re-derive correctly

Severity: none. It discharges the rule W-INTL-99 produced.

For BCH(127,29,21) over 23 blocks, each row derived from its definition rather than read:
leakage gives 496 against 128 needed; the error target gives 1.7e-07 at four percent against
1e-06; area gives 8.49 of sixteen tiles; entropy density gives a floor of 0.8155 with a margin
of 0.1259; and the oscillator floor gives log2(341!) = 2,383 against 2,382 required.

All five reproduce. Only the area row had been wrong, and it now has a check behind it.

One boundary sharpened: this code fails at five percent rather than merely above it - 8.16e-06
against 1e-06 - so the recommendation is four percent or below and five percent requires
BCH(127,22,23).

## W-INTL-105  Helper-data manipulation: the line is code-offset against syndrome, and the withdrawn construction was the named example

Severity: high, and it moves from unlocated to corroborated without reaching verified.

W-INTL-101 left this located but unverified, with Becker's text behind a 403. A second search over
the literature returns a specific account and, more usefully, identifies the distinction.

The repetition code is vulnerable; other linear block codes including BCH, Reed-Muller and single
parity check are affected by the same problem; and linear BCH with syndrome decoding is the case
proven immune. An error pattern was found against the [16,5,8] Reed-Muller code by exhaustively
testing all 2^16 possibilities.

So the dividing line is the construction rather than the code family. A BCH code in a code-offset
scheme is affected; BCH with syndrome-based helper data is not. This project uses syndrome-based
helper data and therefore lands on the immune side of a line a code-offset design with the same
code would fall on the wrong side of.

Status exactly: two independent secondary sources say this and both attribute it to Becker, whose
text remains unread. That is corroboration rather than verification, and corroboration can be
wrong the same way twice. The application still must not claim resistance to helper-data
manipulation.

One consequence for the record. The Reed-Muller construction recommended for two loops before the
leakage bound withdrew it is the named example of this attack working. It was inadmissible on
leakage and vulnerable to helper-data manipulation, and the leakage bound happened to catch it
first. Being wrong for a reason you did not find is not the same as being right.

## W-INTL-106  One declaration per input, and the utilisation now carries its own derivation

Severity: none as a defect. It is the structural fix for the class W-INTL-99 belongs to.

The audit found each measured quantity in three to seven files - tile area three times,
utilisation three, entropy density three, key length four, the decoder table three. Each is a
place drift can start, and "a number carried by hand will eventually not be carried" is not
fixed by care.

`research/inputs.py` declares each once with its provenance and one of three categories:
measured here and reproducible by `measure_all.sh`, measured elsewhere with conditions stated,
or a published specification. Three scripts import rather than redeclare and all still agree.

One improvement fell out: the utilisation had been written by hand as 0.58 and is 0.5795
computed from the two numbers it comes from, 20,900 of cells in 36,064 of tile. The tile figure
is unchanged at 8.49 and the constant now carries its derivation rather than a rounding of it.

## W-INTL-107  The oscillator floor did not follow the recommendation, and the check caught it

Severity: medium as a defect, and it is the first thing the new check found on its own.

`check_figures_reproduce.py` was extended from one figure to three. It failed immediately: the
ledger's oscillator floor says 360, which belongs to BCH(127,22,23), while the recommendation
moved to BCH(127,29,21) six loops ago - leakage 2,254 rather than 2,415, floor 341.

The number did not follow the recommendation, and no amount of reading would have found it. The
figure is plausible, sits in a sentence about a different code's properties, and is the correct
answer to a question nobody was asking any more.

Corrected. Two caveats about the check itself. It caught this only once its pattern matched
the prose - my first pattern looked for "the floor being N oscillators" where the text says
"oscillator floor is N oscillators", and it silently matched nothing. A check whose pattern
does not fire is a check that passes.

And the fixed version then failed on the write-up of this very entry, because its guard
tested whether the phrase appeared anywhere in a document and the write-up quotes the phrase
while describing the failure message. A guard looser than the pattern it protects reports
failures for prose rather than for arithmetic. Corrected by distinguishing the document that
must state a figure from ones that merely may; both controls still fire, on a wrong figure and
on a missing one.

## W-INTL-108  The end-to-end chain was validating a superseded construction

Severity: medium. Third instance of the same drift in one loop.

`key_generator_e2e.py` was still built around BCH(127,22,23). The recommendation moved to
BCH(127,29,21) in loop 61, and the chain kept validating the older one for six loops - including
the Monte Carlo that gave the failure model its second witness, so that witness was for a
construction no longer being recommended.

Nothing in the file was wrong. It simply described a design the rest of the analysis had stopped
recommending.

Repointed and re-run, and the agreement holds: at four percent the model predicts 1.7e-07 and
300 trials show none, at six percent 1.58e-04 against none in 300, at eight percent 0.0107
predicted against 0.015 observed in 200. Keys round-trip at zero and two percent noise at two
bias levels.

Three instances of one drift class in a single loop - a factor lost between documents, a floor
that did not follow its code, and a chain validating a superseded design - all found by building
the instrument rather than by looking harder.

## W-INTL-109  The synthesis chain is machine-checked against the declarations

Severity: none as a defect. It closes the last hand-carried link.

`research/inputs.py` declares each decoder area once with a note saying it is measured here and
reproducible - but nothing checked that a declaration matches what the tools produce today. A
figure transcribed from a run six loops ago and never re-run agrees with the past rather than
with the design.

`scripts/verify_inputs.py` regenerates the table stages for each field and correction strength,
synthesises both halves, and compares the sum against the declaration. All 13 reproduce exactly - every declared area equals a fresh synthesis to within a
square micrometre, so the numbers in inputs.py describe the design as it stands rather than as
it stood when they were written. Not in CI - two synthesis
runs per code is too slow - so it is run when the RTL or the library moves.

## W-INTL-110  The leakage bound is a property of the chosen constructions, not of the problem

Severity: critical as a finding. It reopens every code decision since W-INTL-63 and it was found
while chasing something else.

Going after Becker's text led to Hiller's dissertation, which cites it and is open access.
Chapter 5, read directly rather than from an abstract, introduces Systematic Low Leakage Coding.

Its stated properties, quoted: previous work on secure key derivation with PUFs is either able to
achieve zero leakage or helper data capacity, and SLLC is the first practical approach to combine
zero leakage with a helper data size close to capacity; and SLLC is currently the only
deterministic scheme that achieves the secret key and the helper data capacity, and also
inherently ensures information theoretic security. The algebraic core is an upper triangular
full-rank matrix and the mutual information between secret and helper data is zero.

The construction: the response splits into an information part and a mask; redundancy is computed
from the information part with a systematic encoder; the helper data is that redundancy exclusive-
ored with fresh PUF bits.

So the constraint every code decision here has rested on since W-INTL-63 -
`k_total >= 128 + n_total(1-rho)` - has no leakage term under SLLC, and becomes
`k_total >= 128/rho = 136`.

Consequences. For the current recommendation, blocks fall from 23 to 5, raw response bits from
2,921 to 635, oscillators from 341 to 37, and tiles from 8.49 to 7.73. The area gain is modest
because the decoder dominates; the factor of 4.6 in raw width is the consequential part, since
raw width is what debiasing multiplies and what the oscillator count follows.

And the concatenated Reed-Muller construction that W-INTL-63 withdrew for negative residual
entropy becomes admissible, at 0.49 to 0.66 tiles - cheapest by a factor of twelve. The reason
not to build it has changed rather than vanished: it is now that Reed-Muller is corroborated as
vulnerable to helper-data manipulation, which SLLC does not address, since zero leakage is a
statement about a passive adversary. That makes W-INTL-105 more urgent, not less - the
recommendation now stands on the one security property whose reasoning is still only corroborated.

Status, exactly. The primary source is read and quoted. The consequence for this project is my
derivation and not the thesis's: it does not discuss these codes or this tile budget, and what I
have done is replace one term in an inequality using its stated property. A small step, unchecked
by anyone else, overturning six loops of conclusions - which is the combination that has been
wrong before here.

Three things not done, all load-bearing. Whether SLLC composes with a concatenated code, which
needs a systematic encoder for the concatenation rather than for each part. What SLLC costs in
gates; the thesis has an implementation section and nothing is measured here. And whether the mask
bits being response bits changes the error-correction requirement - I believe not, since the
mask's errors land in the redundancy positions and the codeword still has n error-prone positions,
but that is a belief and the analysis rests on it.

Until those are settled this is a finding rather than a decision, and the recommendation does not
move.

## W-INTL-111  SLLC implemented and measured: two of three open items closed, the third scoped out

Severity: none as a defect. It converts W-INTL-110 from a finding into a decision.

W-INTL-110 listed three load-bearing things undone.

Whether the mask being response bits changes the error-correction requirement: no, and now
measured. `research/sllc_key_generator.py` implements the scheme in full - generator polynomial
from cyclotomic cosets, systematic encoding by long division, enrolment producing helper data as
redundancy exclusive-ored with fresh response bits, reconstruction unmasking and decoding.
Recovery succeeds at every error rate tested and the observed failures track the same binomial
model over n positions: 30 of 30 at zero noise, 60 of 60 at two percent, 200 of 200 at four, 120
of 120 at eight against a model of 2.3e-03. 635 raw response bits over five blocks against 2,921
over twenty-three.

Three things fell out of building it. The generator has degree 98, so k = 29 - a third independent
confirmation of the parameter table, from the generator rather than from coset sizes. A systematic
codeword has all syndromes zero and its first k bits equal the information bits, the property SLLC
requires and which had been assumed. And the software and the RTL now share a derivation rather
than a transcription, since both compute the generator the same way.

What SLLC costs: the systematic encoder is a degree-98 linear feedback shift register with fifty
taps at 3,887 square micrometres, needed at enrolment only; reconstruction adds an exclusive-or of
98 bits at 858. Both on die is 4,745, six percent of the decoder.

Whether it composes with a concatenated code: not answered and not needed. The recommendation is a
single BCH code; the question arises only for the Reed-Muller alternative, which helper-data
manipulation rules out independently. Out of scope rather than open.

## W-INTL-112  SLLC dissolves the arrangement constraint, which is the real gain

Severity: none as a defect. It withdraws the conclusions of W-INTL-67 and W-INTL-68 for the right
reason.

The area gain from SLLC is three percent - 8.49 tiles to 8.18 - because the decoder dominates and
SLLC adds six percent of one. That is not where the value is.

With debiasing at the pair-output overhead of 2.18: under the leakage bound the disjoint
arrangement needs 39.68 tiles and does not fit; under SLLC it needs 15.05 and does. Without
debiasing, 22.33 against 11.28.

Under SLLC every combination fits. That withdraws W-INTL-67, which found debiasing turned the
oscillator arrangement from a factor-of-two question about area into a question of fitting at all,
and W-INTL-68, which concluded from the whole method table that oscillator reuse was a requirement
rather than an optimisation. Both were correct under the leakage bound and neither survives its
removal.

The register's bias-and-debiasing row moves from binding conditionally to slack. So one
construction removes two binding constraints: the leakage term, and the arrangement question that
the leakage term's raw-width penalty created.

The recommendation is therefore to use SLLC: six percent more decoder area for 4.6 times fewer
response bits and one fewer binding constraint.

## W-INTL-113  The n-k bound is confirmed first-hand, and Fuzzy Commitment escaped it in 1999

Severity: high as a finding about this project's method rather than about its subject.

Chapter 4 of the dissertation gives a first-hand comparison of the four state-of-the-art
constructions. Table 4.2 lists the mutual information between secret and helper data for a nearly
perfect PUF as n-k for the syndrome construction. That is the bound every code decision here has
rested on since W-INTL-63, sourced second-hand from Gao et al., and it is confirmed. It was right.

The same table gives Fuzzy Commitment a rank loss of zero and leakage below epsilon-nought. So the
bound was escapable by the oldest construction in the field, and W-INTL-110 over-credited SLLC as
the discovery.

| Scheme | Helper bits | Leaks | Needs a random number |
|---|---|---|---|
| Syndrome | n-k | n-k | no |
| Fuzzy Commitment | n | about zero | yes |
| SLLC | n-k | zero | no |

SLLC remains best on paper - zero leakage at the smallest helper data with no random number - and
Fuzzy Commitment is the most widely deployed scheme in the field, has been available throughout,
and was never considered here. Twelve loops took the leakage term as given while the oldest entry
in the table does not have it.

The thesis also places SLLC exactly, which makes it less surprising and more trustworthy: the
Parity Construction stores the parities of the response with a systematic code and leaks 2k-n, and
SLLC is that construction with the parities masked by fresh response bits. Not a new mechanism -
the one scheme in the table repaired.

## W-INTL-114  Under zero leakage the entropy density stops binding, which dissolves six loops of sensitivity work

Severity: critical as a correction of scope. Every conclusion it withdraws was correct and
conditional.

Rebuilt with the leakage term removed, the requirement becoming k_total >= 128/rho met by adding
blocks: the budget moves from 8.18 tiles at entropy density 1.00 to 8.21 at 0.50. Halving the
tightest input in this work changes the answer by three hundredths of a tile.

That withdraws, as conclusions about the problem rather than about a construction: the cliff at
0.7986 located in W-INTL-86; the margin of 0.0065 that W-INTL-72 called the tightest number in the
work; the flat band and its edge in W-INTL-82 and W-INTL-84; and the priority reversal in
W-INTL-85, which found the error rate at least as binding as the entropy density. All of it was a
property of the syndrome construction's leakage term.

The mechanism is simple once the term is gone. A lower density needs more blocks; blocks are
processed sequentially by one decoder, so more cost nothing in area, and only the oscillator count
grows. Under the leakage bound each extra block also added n-k bits of leakage, which is what made
the density bind.

The error rate is now the only binding input: eight percent fits at 11.75 tiles and nine does not,
at every density from a half upwards.

Six loops of sensitivity analysis, three reversals of priority, and a register row marked as the
tightest figure in the work - all correct, all conditional on a construction chosen in W-INTL-63
without asking whether its leakage was avoidable. Asking took an hour.

## W-INTL-115  The error-rate constraint rests on the assumption that all errors must be corrected

Severity: critical as a correction of scope. It removes the last input still binding after
W-INTL-114.

Chapter 6 of the dissertation contains the comparison table this analysis has been reconstructing
for twelve loops. Every row is for an SRAM PUF at fifteen percent average bit error probability, a
128-bit key and a key error rate of one in a million: Code-Offset Golay at 3,696 response bits and
907 slices or more, Code-Offset RM-GMC at 1,536 and 237, C-IBS RM at 2,304 and 250, and compressed
DSC Seesaw at 974 response bits, 1,108 helper data bits and 249 slices.

This project, at less than half that error rate, needed 2,921 response bits under the syndrome
construction and 635 under SLLC, and concluded nine percent and above was impossible.

Differential Sequence Coding reaches fifteen percent with 974 bits because it does not correct the
errors. It indexes the reliable bits and skips the rest, storing compressed pointers as helper
data. The thesis gives the arithmetic: the target is reached with a maximum bit error probability
of 0.027 by indexing on average 32.6 percent of the available PUF bits. Fifteen percent raw becomes
2.7 percent effective.

Every construction evaluated here assumed all n positions must be corrected. That assumption is the
error-rate constraint, and it was a choice.

One thing already right: reliable-bit selection needs per-bit reliability from repeated
measurements at enrolment, and the characterisation structure in W-INTL-70 emits raw frequency
counts rather than response bits precisely so that downstream decisions could be made off the die.
The instrument for this already exists.

## W-INTL-116  Helper-data manipulation has a generic countermeasure, so the code choice never turned on it

Severity: closes W-INTL-105, open for four loops, and closes it better than verification would
have.

W-INTL-105 rested on a second-hand claim that syndrome-based BCH is immune to helper-data
manipulation, from a paper behind a paywall, and the recommendation was standing on it.

Chapter 6 answers a different question. The helper data is hashed onto the decoder output to
prevent helper-data manipulation attacks, using SPONGENT as a lightweight hash, so that 88 key bits
are affected by each helper data bit and the key is corrupted as soon as the helper data is
manipulated. Chapter 4 states the same countermeasure generically as K = S xor f(W).

So the code choice never turned on manipulation immunity. There is a generic countermeasure, it is
a lightweight hash, it is independent of the code, and it was in the same document as everything
else read over the last three loops.

Verification of Becker would have established whether one construction is immune. This establishes
that the question need not be asked, provided the helper data is hashed into the key - which no
design considered here currently does. That is a concrete gap: the countermeasure is cheap and
absent.

## W-INTL-117  Three loops running, a table in the cited literature has removed a constraint treated as fixed

Severity: this is a finding about the method, and it is the most important entry in this file.

W-INTL-110 found the leakage term was a property of the construction chosen. W-INTL-113 found the
oldest construction in the field never had it, and W-INTL-114 that removing it makes the entropy
density stop mattering. W-INTL-115 finds the error rate rests on an assumption the standard
alternative does not make.

Each was one table or one section in a document already cited. Twelve loops of measurement, three
reversals of priority, a constraint register and four instruments that check each other - all of it
inside a framing that a comparison table would have shown was one of several.

The measurements survive: thirteen decoders correctly measured, the checks still running, the
end-to-end chain still agreeing with the model. What does not survive is any claim that this
analysis found the best construction. It never compared framings, only codes within one.

The rule for the next loop is not to measure more carefully. It is to find the field's comparison
table before optimising, and this file now contains three instances of what happens otherwise.

## W-INTL-118  The row that removed the constraint does not remove it at this project's error rate

Severity: this retracts the operative half of W-INTL-115 while confirming its mechanism.
It is a correction of a correction, and the direction matters more than either number.

W-INTL-115 read a comparison table in the cited dissertation and concluded that the
error-rate constraint was a choice, because compressed Differential Sequence Coding
reaches fifteen percent average bit error probability with 974 response bits by indexing
the reliable third of the positions rather than correcting all of them, while this
project needed 2,921 bits under syndrome and 635 under SLLC at less than half that rate.

research/reliable_bit_selection.py builds the selection under this project's own source
model - a ring-oscillator pair emitting sign(d + n), the device difference d drawn once
and the read noise n redrawn every measurement - with the noise scaled so the raw error
rate matches the row. The mechanism transfers and is not in doubt. Selecting the most
reliable 32.6 percent of positions takes the error rate from 0.150 to 0.0066 under
perfect ranking, and the analytic figure and a 120,000-position sample agree to within
half a thousandth at every fraction tried.

What does not transfer is the advantage. Selection has to be paired with something, and
paired with repetition at a word failure rate of one in a million it needs, at six
percent raw error, between 1,211 and 1,765 response bits depending on the enrolment
budget. SLLC needed 635 at the same rate. The row wins at fifteen percent because at
fifteen percent the block constructions need 2,921 and 3,696 bits; it does not win at
six, because 635 is already below what selection plus repetition can reach there.

The bound on this finding is explicit: the source pairs DSC with a convolutional code and
Viterbi decoding, and only repetition was measured here. A stronger inner code moves the
selection column down and could reverse this. What is measured is that adopting the row's
winner because the row exists would have been wrong at this project's error rate, and
that is the same failure W-INTL-117 named, committed in the opposite direction one loop
later.

## W-INTL-119  Perfect ranking is not a design, and the enrolment reads are the price

Severity: medium, and it is the reason the previous entry comes out the way it does.

Reliable-bit selection needs to know which bits are reliable. The figure in W-INTL-115 and
the 0.0066 above both assume the reliability is known exactly, which no enrolment
procedure delivers. The achievable version reads each position a fixed number of times and
ranks by the majority margin; research/reliable_bit_selection.py computes the exact
fraction and effective error rate for that rule by summing the binomial vote distribution
over the population of positions, rather than sampling it.

At fifteen percent raw and roughly the row's selected fraction, one enrolment read gives
0.208, three gives 0.096, seven gives 0.045, fifteen gives 0.022, thirty-one gives 0.010
and sixty-three gives 0.009, against 0.0066 for perfect ranking. A 120,000-position sample
at fifteen reads returns 0.022 against the exact 0.0216. The dissertation's 0.027 is
reproduced at thirty-one reads while selecting 48.7 percent, so the row is consistent with
a realistic enrolment budget rather than with the bound - it is an honest number, and it
is not the bound.

This is a real cost SLLC does not carry. SLLC reads each position once. Thirty-one reads
per position is thirty-one times the enrolment time and a counter wide enough to hold the
votes, and the characterisation structure in W-INTL-70 already emits raw frequency counts,
so the instrument exists and the budget for using it does not.

Two secondary results, both measured, both favourable to selection and neither sufficient
to change W-INTL-118. The bit value is independent of the reliability under this source:
the share of ones among the selected positions is between 0.4976 and 0.5018 at every
fraction from 1.0 down to 0.1, so pointers to reliable positions say which positions are
stable and not what they hold, which is what makes them compatible with the zero-leakage
regime W-INTL-114 established. And the differential encoding is the right size: 318
pointers into 974 positions cost 3,157 bits as absolute indices and 888 bits at the
entropy floor of the geometric gap distribution, against the 1,108 the row states, so the
row's helper data is about a quarter above the floor, which is where a real entropy coder
sits.

## W-INTL-120  The manipulation countermeasure is three lines and it is still not in the design

Severity: low as an engineering task, high as an omission, and now measured rather than
argued.

W-INTL-116 closed the helper-data manipulation question by finding the generic
countermeasure K = S xor f(W) in the same chapter as everything else, and recorded that no
design in this repository does it. The entry did not say what it buys, so this loop
measured it. Folding a hash of the 1,108-bit helper data into the key changes 64.3 of 128
key bits on average when a single helper bit is flipped, over 200 trials, with a range of
51 to 78. That is the ideal half, which is what a hash is supposed to give, and it is the
figure to quote rather than the source's 88 - the source reports its own lightweight hash,
not a bound, and quoting a number above the ideal as an improvement would be the mistake
this file exists to catch.

The countermeasure costs one hash of the helper data at regeneration. It is independent of
the code, so it survives whichever construction the previous two entries settle on, and it
should be written into the key derivation before any construction is chosen rather than
after.

## W-INTL-121  Two families of scheme exist and this session only examined one

Severity: critical as a scope finding.

Chapter 3 of the dissertation is the map of framings this analysis never had. Its conclusion is one
sentence: there are two main families of syndrome coding schemes for PUFs, linear approaches and
pointer-based approaches.

Every construction evaluated across twelve loops - Fuzzy Commitment, Code-Offset, Syndrome, Parity,
SLLC - is linear.

Index-Based Syndrome Coding divides the response into blocks and indexes, within each, the bit that
matches the intended codeword bit with highest probability. It reduces errors by selecting bits of
higher than average reliability, and for i.i.d. PUF bits the pointers are uncorrelated with the code
sequence so nothing leaks through the helper data. Zero leakage by construction - not by masking as
in SLLC nor by a random number as in Fuzzy Commitment, but because a pointer to a reliable bit says
nothing about its value. Complementary IBS fixes IBS's inefficiency; Maximum-Likelihood Symbol
Recovery indexes whole blocks and is stated to suit bit error probabilities above twenty percent.

The counterweight, from the same section: the output bits of a ring-oscillator sum-PUF are not fully
independent, and IBS helper data can be attacked with machine learning on that basis. So the pointer
family trades a leakage-and-correction problem for a modelling problem, and this project's source is
the type where that attack was demonstrated.

Read alongside W-INTL-118, which was produced in parallel and which measures what happens when the
selection mechanism is transferred to this project's error rate: the mechanism holds and the
advantage does not. The two entries agree. A family that is better on a binding constraint pays
somewhere else, and here it pays twice - a modelling attack aimed at this source type, and no
advantage at six percent raw error.

## W-INTL-122  The manipulation countermeasure is implemented and tested, closing W-INTL-120

Severity: none as a defect. It closes the component W-INTL-116 identified.

W-INTL-116 turned four loops of an open security question into a missing component, and W-INTL-120 -
written in parallel by the cloud routine - observed that the countermeasure is three lines and still
absent from the design. This closes it: fold the helper data into the key, K = S xor f(W).

Present now in `research/sllc_key_generator.py` and tested on the property it exists for: honest
reconstruction at two percent noise recovers the key in 60 of 60 trials, and one flipped helper-data
bit changes the key in 60 of 60. The second is the point - a manipulated helper data must not yield
the enrolled key whatever the decoder does with it, and folding it into the key achieves that
without depending on the code.

Cost is borrowed rather than measured: the thesis gives SPONGENT in its smallest configuration
returning an 88-bit hash as 85 slices on a Spartan-3E. Labelled as borrowed, though it sits beside a
decoder of 249 slices in the same table.

## W-INTL-123  The session loop and the cloud routine collide on branch names

Severity: medium as an operational defect, and it cost a merge.

This work runs in two places: an interactive session and an hourly cloud routine given the same
prompt. Both name their branches `wave-intl-NN` and both increment from what they see on main, so
both chose `wave-intl-46` this hour. The routine pushed first, its pull request merged, and the
session's push was rejected as a non-fast-forward - after which the session opened a pull request
against a branch it did not own and merged the routine's work believing it was merging its own.

Nothing was lost, because the rejected push left the session's commits local, and they are on
`wave-intl-47-session` now. What was briefly true is worse than a lost commit: a report was written
saying content had reached main when it had not. That was caught by checking whether the merged
branch actually contained the new sections, which is a check worth doing after every merge rather
than trusting the pull request state.

The fix adopted here: session branches carry a `-session` suffix. The deeper point is that two
agents given the same prompt and the same naming convention will collide, and the collision is
silent on one side - the routine had no way to know.

## W-INTL-130  Selection paired with BCH reverses the parallel routine's conclusion, as it predicted

Severity: this resolves the bound W-INTL-118 stated for itself, and it settles the error-rate
constraint.

W-INTL-118 measured reliable-bit selection against repetition and named its own limit: the source
pairs selection with a convolutional code, only repetition was measured, and a stronger inner code
could reverse the conclusion.

Paired with the BCH codes whose decoders are measured here, reusing the routine's selection model
rather than rebuilding it - that model is validated against a 120,000-position sample to within
half a thousandth. With nine enrolment reads: at six percent raw, keeping eighty percent gives an
effective 0.0133 and needs 794 raw positions at 8.19 tiles; at ten percent, the same fraction gives
0.0466 and the same 794 positions; at fifteen percent, keeping forty percent gives 0.0374 and needs
1,588 positions at 8.23 tiles.

Nine reads, one code, about 8.2 tiles at every error rate from six to fifteen percent. Without
selection: 10.37 tiles at six, 26.33 at ten which does not fit, nothing at fifteen.

So the reversal happens and the routine called it correctly. Its conclusion holds for repetition and
not for BCH.

Two things preserved rather than discarded. These figures use a finite enrolment budget, not the
perfect ranking W-INTL-119 warned against. And at a single enrolment read selection makes things
worse - 0.0823 effective against 0.0600 raw - because ranking on one noisy measurement selects for
what the noise did rather than for what the device is.

## W-INTL-131  A figure in the parallel routine's comparison did not follow its own condition

Severity: medium, and the way it was found matters as much as the correction.

W-INTL-118 compares selection plus repetition at 1,211 to 1,765 response bits against SLLC needing
635 at the same rate. The 635 is five blocks of BCH(127,29,21), and at six percent raw that gives a
word failure rate of 3.44e-05 against a target of one in a million. It does not meet the target
there: 635 is the figure for four percent, where that code tolerates up to 4.42 percent. SLLC at six
percent needs BCH(127,15,27) at ten blocks and 1,270 response bits.

So the comparison is 1,211 to 1,765 against 1,270 - roughly a tie rather than a loss - and selection
paired with BCH needs 794, which wins outright.

The routine's mechanism measurements stand and are used above: the selection model, the 0.150 to
0.0066 figure, the sample agreement, and the enrolment-cost curve. What was wrong was one figure
carried from a different operating point, the same class as W-INTL-99 and W-INTL-107 - a number that
did not follow the condition it was computed under.

How it was found is worth recording. Two agents on the same prompt, one checking the other's
arithmetic against its own stated conditions. Neither would have caught it alone, because each reads
its own figures as familiar. That is an argument for the parallel arrangement that W-INTL-123 was
otherwise a case against.

## W-INTL-132  Audit numbering collides between agents, and a suffix on branches does not fix it

Severity: low, and it is the second half of W-INTL-123.

W-INTL-123 fixed branch collisions with a `-session` suffix. The numbering collided independently:
both agents reached W-INTL-118 and both reached W-INTL-120, each incrementing from what it saw on
main, and the session had to renumber twice in one loop.

A suffix on the branch does not help, because the number is in the file. This loop takes 130 and
above for session entries, leaving 124 to 129 free for the routine, which is a convention rather
than a mechanism and will hold only until one side needs seven entries.

The mechanism that would work is a number derived from content rather than from a counter. Recorded
as the fix not taken, because the convention is enough for now and the cost of being wrong is a
rename rather than a lost finding.

## W-INTL-133  The countermeasure's cost is measured, and an identity S-box shows why a linear mixer would not serve

Severity: none as a defect. It closes the last borrowed figure in the project.

The helper-data manipulation countermeasure's cost was taken from the thesis - 85 slices on a
Spartan-3E, a different technology on a different process - and it is load-bearing, being what makes
the code choice independent of manipulation.

SPONGENT-88/80/8's permutation implemented and measured here: the round function 2,215 square
micrometres, the full permutation with state and round counter 6,215. That is 7.8 percent of the
decoder against SLLC's 6.0, and it moves the budget from 8.19 tiles to 8.79 at six percent raw error,
8.23 to 8.83 at fifteen.

Verified before quoted: the S-box and bit permutation each checked bijective at generation, and the
testbench measures avalanche, which is the property the countermeasure relies on. One input bit
changes a mean of 46.5 of 88 output bits over 24 trials, range 36 to 52, against an ideal of 44. Two
injected faults fail it - two rounds instead of forty-five gives 6.2, an identity S-box gives exactly
1.

Not verified: there are no official test vectors in hand, so this is a SPONGENT-shaped permutation of
the specified structure and round count rather than something checked against the standard. The area
is what it is measured for.

The identity-S-box control earns its place twice. Exactly one output bit changes, which is the
concrete form of why a linear diffusion function will not serve: an attacker who flips a helper-data
bit learns the key change exactly and compensates. Earlier in this work an LFSR-based mixer looked
like a cheaper route to the same diffusion. It would have been cheaper and useless, and the control
says so in one number.

## W-INTL-134  Nine enrolment reads is a requirement on the provisioning flow and appeared in no document

Severity: medium. It is a constraint the design now depends on and nobody had written down.

Reliable-bit selection learns which positions are reliable by reading each several times at
enrolment, and the read count sets the effective error rate: at one read selection makes things worse
than not selecting, at nine it gives 0.0133 effective from 0.0600 raw, at twenty-five 0.0104. The
budget in W-INTL-130 uses nine.

Stated as a requirement: enrolment requires reading every candidate position at least nine times, at
the operating temperature, before the reliable subset is chosen. Fewer reads do not degrade the
design gracefully - at one read the selection is counterproductive, which is a failure mode worth
naming because it is the opposite of the usual expectation that less effort gives a worse but working
result.

Two consequences. Provisioning is nine sweeps of the oscillator bank rather than one, negligible in
time at 448 cycles per sweep but a step the flow must contain. And the reads must be at the operating
temperature, or the ranking is of the wrong quantity - the same point the literature makes about
oscillator pairs whose ordering reverses as the die warms.

Recorded in `research/inputs.py` as ENROLMENT_READS so that it lives beside the measured quantities
rather than in prose.

## W-INTL-135  The pointer family costed, and a measured advantage declined

Severity: closes W-INTL-121, the only open critical entry.

Index-Based Syndrome Coding removes helper-data leakage by making the helper data a pointer to a
position - for i.i.d. bits a pointer says nothing about the value it points at - where SLLC masks the
redundancy with fresh response bits. Both give zero leakage. Costed for the same code and key, with
the pointer datapath implemented, verified against an injected off-by-one, and measured:

| Scheme | Positions | Oscillators | Extra logic | Helper bits | Tiles |
|---|---|---|---|---|---|
| SLLC | 635 | 41 | 4,745 | 490 | 8.79 |
| IBS, block of 4 | 2,540 | 72 | 581 | 1,270 | 8.47 |
| IBS, block of 8 | 5,080 | 102 | 623 | 1,905 | 8.55 |

The pointer datapath is eight times smaller than the masking machinery - a counter, a comparator and
a register against a degree-98 encoder - and pays in positions, needing four times as many. Net, 0.32
of a tile ahead.

It should still not be used here. IBS needs a random codeword to point at, so it needs a random
number source SLLC does not, and the literature records that ring-oscillator sum-PUF outputs are not
fully independent and that IBS helper data can be attacked with machine learning on exactly that
basis. The trade is 0.32 of a tile against a new attack surface aimed at this project's source type.

That is a recommendation rather than a finding, and it is the first time in this work a measured
advantage has been declined. Recorded plainly because the arithmetic says otherwise.

## W-INTL-136  The decoder is 87 percent of the design and the oscillators are 1.2

Severity: medium as a finding about where the effort went.

The budget has been assembled across twenty sections and never shown as one table. Assembled: the
decoder 79,787 square micrometres at 86.9 percent, the manipulation countermeasure 6,215 at 6.8, the
SLLC encoder and unmask 4,745 at 5.2, and forty-one ring oscillators 1,077 at 1.2. Cell area 91,824,
die area 158,446 at the measured utilisation, 8.79 tiles of sixteen.

Six loops went into the oscillator side - the arrangement question, the entropy floor, the debiasing
overhead, the pairing scheme - and all of it optimised a term worth about a hundredth of the total.

Those loops were not wasted, because the oscillator side is where the constraints lived: the entropy
density and the error rate decided which code was admissible, and the code is 87 percent of the area.
But the effort refined a small term while the large one was settled early and revisited only when a
paper forced it. Sorting the budget by share is cheap and would have said so at any point.

## W-INTL-137  A module that never compiled had an area reported for it

Severity: low as a defect and worth recording as a near-miss.

The pointer datapath used `within` as a register name. That is a SystemVerilog sequence keyword:
yosys accepted it as an identifier and synthesised the module, iverilog rejected it, and the first
run produced an area of 584 square micrometres for a module whose testbench had never compiled.

Nothing was published, because this project's rule is that no area is quoted for a circuit that has
not passed a testbench, and the testbench had not run. The rule caught it. What it did not catch, and
what a reader should notice, is that the synthesiser gave a plausible number for a design it had
silently reinterpreted - the same shape as W-INTL-97, where a path tracer walked through
unrecognised cells and returned 5,208 levels.

Two tools disagreeing about whether an identifier is a keyword is a narrow bug. The general form is
that a tool which partly does not understand its input returns a plausible answer rather than an
error, and that the defence is a second tool with different strictness rather than closer reading.

## W-INTL-138  The countermeasure is now machine-checked against its declaration

Severity: none. It extends W-INTL-109 to the components added since.

`verify_inputs.py` re-synthesised the thirteen decoder areas and nothing else, so the countermeasure
and the characterisation readout were declared as measured without a check behind them. Extended: the
SPONGENT round at 2,215 and the full permutation at 6,215 both reproduce exactly.

## W-INTL-139  Sharing the solver's multipliers takes thirty-nine percent off the design

Severity: this is not a weakness. It is the largest single reduction in this work and it acts on
W-INTL-136.

W-INTL-136 observed that the decoder is 87 percent of the design and that six loops had gone into
the 1.2 percent. The key-equation solver instantiates 3(t+1) general multipliers - 66 at t=21 - and
is 57,571 of the decoder's 79,787 square micrometres. That count is right for a communications
decoder needing a codeword per symbol time, and this runs once at power-up.

Rewritten with two multipliers shared across cycles: 22,131 square micrometres, sixty-two percent
less, for about 1,850 cycles - 185 microseconds once at ten megahertz.

Verified differentially rather than against a re-derived expectation: the same syndromes into both
solvers, locator and degree must match, every error weight from one to twenty-one with two patterns
each, forty-two cases all matching. An injected fault in the serial version alone fails all
forty-two.

The budget: decoder 79,786 to 44,346, cell area 91,823 to 56,383, and 8.79 tiles to 5.40. Thirty-nine
percent of the design from one change to the component that was eighty-seven percent of it.

Two implementation notes. The first version registered the multiplier operands and used the product
in the same cycle, so every product reflected the previous cycle's operands - the differential test
caught it immediately where inspection would not have. And the update now lands in a shadow array
committed in one step, so the discrepancy phase reads a consistent locator.

What makes this entry worth reading is that nothing was learned here. The solver's own header has
said since it was written that a systolic reformulation exists and timing is not closed. The
observation that latency is free has been in the constraint register as slack since power and timing
were checked. The technique was available from the first loop; what changed was sorting the budget by
share and looking at which term was large.

## W-INTL-140  Sharing the Chien search's multipliers makes it larger, and the reason refines the rule

Severity: none as a defect. It is a negative result recorded so the technique is not tried again.

W-INTL-139 took thirty-nine percent off the design by sharing the solver's multipliers. The obvious
next step was the table stages, now half the decoder - syndrome bank 13,258 square micrometres,
Chien search 8,906.

Implemented, verified differentially against the parallel Chien on six locators with an injected
fault failing all six, and measured at 13,129 - forty-seven percent larger.

The reason is exact. The parallel form has twenty-two constant multipliers, fixed XOR trees at about
265 square micrometres each. The serial form has one general multiplier with both operands variable,
plus addressing to read and write an indexed array of twenty-two entries, at about 10,050. Removing
twenty-one cheap units saves 5,550; the shared unit costs 10,050. The trade loses by 4,223.

The solver was the opposite case: its replicated units were general multipliers, the same kind as the
shared one, so sharing removed sixty-four of sixty-six at no change in unit cost.

So the predictor is not the logic share, which is what W-INTL-139 might have suggested. The Chien
search is 65 percent logic and does not compress; the solver was 84 percent and compressed by 62.
What decides it is whether the replicated unit costs more than the shared unit plus its addressing.
Replicating something cheap is already the efficient arrangement.

The same reasoning excludes the syndrome bank without implementing it: forty-two constant
multipliers, cheaper per unit still, and serialising would additionally need the received word stored
in another 127 flip-flops, because the parallel accumulators consume the input stream simultaneously
and a shared one would have to re-read it. Excluded by argument rather than left open.

The decoder stands at 44,346 square micrometres and the design at 5.40 tiles. The table stages are at
their floor for this technique.

One note on method. The header written for the serial Chien before measuring predicted a smaller
saving than the solver's, for the right reason - a general multiplier costs more than the constant one
it replaces - and got the sign wrong. Writing the reason down before measuring made the negative
result immediately interpretable rather than puzzling, which is most of what that habit is for.

## W-INTL-141  The code was chosen before selection existed, and re-choosing it removes another 35 percent

Severity: high as a finding about the process, and it is the second instance in two loops.

Reliable-bit selection arrived in W-INTL-130 and made the effective error rate 0.0127 where the raw
rate is six percent. The code was chosen in W-INTL-75 against the raw rate and was never revisited.
BCH(127,29,21) tolerates 4.42 percent and is being asked to survive 1.27.

Re-searched at the rate that applies: BCH(127,57,11) meets one in a million in three blocks and 381
selected bits, against five blocks and 635. Every code that fits the operating point was unmeasured,
and every measured code at n=127 has t of 21 or more - all chosen when high error tolerance was
needed. The measured set was built for an operating point that no longer applies, so the search could
only return the best of the wrong candidates.

Generated, verified end to end and differentially, measured: decoder 24,659 square micrometres
against 44,346, cell area 36,539 against 56,383, and 3.50 tiles against 5.40. Leakage checked first
since the code changed - k total is 171 against the 136 required.

## W-INTL-142  Sixty percent of the design removed in two loops, and both were revisits

Severity: this is the method finding, and it is worth more than either change.

The design stood at 8.79 tiles two loops ago, went to 5.40 by sharing the solver's multipliers, and
now stands at 3.50 by re-choosing the code. Sixty percent removed, and neither change required a new
measurement technique, a new paper, or a new constraint.

Both were decisions correct at the operating point where they were made, in a design whose operating
point had since moved. The solver's multiplier count assumed a throughput requirement this has never
had. The code assumed an error rate that selection had since reduced by a factor of five.

The constraint register was written to catch exactly this class and cannot. It records what each
constraint is and whether it binds; it does not record which decisions were taken against which
constraint. When a constraint moves, nothing points at the decisions that rested on it.

Recorded as a change to how the register is kept rather than made this loop: a column naming, for
each constraint, the decisions taken against it. The next loop is a better place to make that change
than the one that noticed it needed making.

## W-INTL-143  The constraint register is revised after three loops of deferral

Severity: low, and the reason it went stale is the part that matters.

The register was deferred for three loops while the leakage term was removed, selection was added,
the countermeasure was measured, the solver was rewritten and the code was re-chosen. Revised now.

What binds: the min-entropy requirement, met at 171 against 136 required; and the word failure rate,
against the effective error rate after selection rather than the raw one.

What no longer binds: helper-data leakage, removed entirely by SLLC and a property of the syndrome
construction rather than of the problem; min-entropy density, once the tightest input and now worth
three hundredths of a tile when halved; response bias, which decided the oscillator arrangement and
no longer does; and the raw error rate, slack to fifteen percent with selection, which converts it
into a requirement for raw positions.

What is new: nine enrolment reads per position at the operating temperature, without which selection
is counterproductive rather than merely weaker; and the manipulation countermeasure, a component
rather than a constraint but load-bearing and absent for four loops.

## W-INTL-144  Selection was assumed free in entropy, and the check ran inside the assumption

Severity: high. It was a live defect one loop ago and is not one now, by luck rather than method.

Reliable-bit selection publishes which positions were kept, and the file that introduced it says
that is safe because reliability |d| is independent of value sign(d) when d is symmetric - "a
property of this source, and it is checked below rather than assumed". It is not checked. Every
sampler in that file draws d from a zero-mean Gaussian, so the check reports a value share of 0.5000
because the sampler was told to produce one. The symmetry is a parameter of the model and the check
runs inside it: the broken-ruler error at the level of a source model rather than a signal.

The measured source is not symmetric. 241.0 bits in 256 positions is a bias of 0.5207. Delvaux, Gu,
Schellekens and Verbauwhede - the survey deferred for five loops, now read - state in their abstract
that they "disprove the intuitive assumption that bit selection schemes have no leakage", and their
section VII names global thresholding, the scheme used here, as the worst of the four on exactly
this axis. The pointer family costed in W-INTL-121 is the one that does not amplify bias.

Quantified in this project's own source model, in closed form and by two samplers: at the twenty
percent the design discards, the bias goes from 0.5207 to 0.5251 and the density from 0.9414 to
0.9293. The requirement rises from 136.0 bits of k to 137.7 against 171 carried. The recommendation
survives with thirty-three bits of margin.

The design one loop ago does not. BCH(127,29,21) in five blocks carried 145 bits of k: margin 7.3 at
twenty percent discarded, 1.4 at the 67.4 percent the analysis borrowed from the literature, and
failing at eighty and ninety. The re-choice in W-INTL-141 took the margin from nine bits to
thirty-three as a side effect of choosing for area, which is the second time in three loops a
constraint has been met by an accident of a decision taken for another reason.

Guard added: scripts/check_figures_reproduce.py recomputes the post-selection density from inputs
and fails if the recommendation's k does not cover it. All three of its failure modes were exercised
before it was committed, including one that reproduces the previous design's failure.

## W-INTL-145  A measured input carried its arrangement and not its selection status

Severity: medium, and it is the general form of W-INTL-144.

The entropy density is recorded with the pairing it was measured under, because an earlier loop
found the figure swings with pairing distance. It is not recorded as measured on *unselected*
positions, and the design selects. The provenance convention captured the variable that had already
caused trouble and not the one that had not yet.

Fixed in research/inputs.py, which now states the condition and points at the computation. The wider
lesson is that a provenance note records the conditions someone thought to write down, and the
conditions that matter are the ones a later decision changes.

## W-INTL-146  Two numbers in the right place in the wrong dictionary, and a gate that was not run

Severity: medium. Nothing quoted was wrong; everything declared was mis-declared.

W-INTL-141 entered 24,659 and 28,958 into DECODER_AREA. Both were measured correctly and neither
belonged there: every other entry is the table stages plus the replicated solver and these two were
the table stages plus the shared one. The verifier synthesises what the dictionary says it holds, so
it reported a seventeen-thousand-square-micrometre mismatch in a figure that was not wrong.

It reported it one loop late. The previous loop reported gates green having run check_consistency
and not verify_inputs - the slowest of the three and the only one that would have fired. "Gates
green" is a claim about which gates.

Fixed by naming the two conventions rather than merging them: DECODER_AREA for the replicated
solver, DECODER_AREA_SERIAL for the shared one, decoder_area() for what the design would pay, and
the verifier checks both. Its summary also counted fifteen areas where twenty had been checked.

measure_all.sh had drifted the same way: it did not build the recommendation. No end-to-end decode
at t=11 or t=13 and no differential test of the shared solver, though that testbench has been in the
repository since W-INTL-136. Three testbench entries and five area probes added; all seventeen pass.

## W-INTL-147  The figure-reproduction check is anchored to an operating point eight loops old

Severity: medium, open, and named rather than fixed this loop.

check_figures_reproduce.py recomputes its headline from cheapest(RHO, 0.04): no SLLC, no selection,
a three-thousand-bit raw budget. The ledger states 8.49 tiles and the check recomputes 8.49 tiles,
and they agree because both are anchored to the same superseded construction. The check written to
stop documents drifting from the model is pinned to an old model, so it cannot notice that the
recommendation is 3.50 tiles under a different construction entirely.

The selection-entropy guard added this loop is anchored to the current operating point, which is the
shape the rest of the file should take. Repointing it means rewriting the ledger's E31 row, which is
the row the whole area claim rests on, and that is a change worth doing deliberately.

## W-INTL-148  The SLLC encoder was the wrong code's, untested, and a literal in a script

Severity: high. Three defects in one component, all of which the project's own rules forbid.

The SLLC stages were written by hand for BCH(127,29,21) - a degree-98 generator, forty-nine taps
transcribed one per line. The recommendation has been BCH(127,57,11) for two loops, whose generator
has degree 70. The budget was paying for the wrong encoder, and paying too much, so the error was
conservative and could never show up as a fit failure.

There was no testbench. The area had been quoted for five loops in a project whose stated rule is
that no area is quoted for a circuit that has not been exercised, and whose measure_all.sh refuses
to print areas when a testbench fails - and this circuit was in neither. A wrong tap would have been
invisible in both directions.

And the number itself, 4,745, was a bare literal in one analysis script, in a project that moved
every other input into research/inputs.py after W-INTL-99 for exactly this reason.

Fixed together. gen_sllc.py computes the generator from the cyclotomic cosets of alpha^1..alpha^2t -
the same machinery the decoder generator uses - so the taps are a consequence of the code rather
than a transcription of it. Its output for t=21 reproduces the hand-written file to within one
square micrometre, which is what makes replacing that file safe. A generated testbench checks the
register against a software polynomial division on 24 random information words and the unmask stage
by round trip; a dropped tap and an exclusive-or turned into an and both fail it.

Measured: 3,176 square micrometres for the recommendation's own code against 4,746 for the code it
was written for. The design goes from 3.50 tiles to 3.35.

## W-INTL-149  Two loops of status rows were dropped silently, and the note that said so was noise

Severity: medium as a defect and high as a habit.

Loops 79 and 80 each added rows to the audit's status table with a string replacement whose anchor
did not exist. Python's str.replace returns the string unchanged when it finds nothing, so both
edits succeeded, both commits claimed the rows, and neither row was ever in the file.

check_consistency reported it both times, as a note rather than a failure: "audit: status table does
not list W-INTL-121 ... W-INTL-147". The list grew by two entries a loop for four loops and was read
as furniture. An advisory that never escalates is an advisory that gets read once.

Both fixed: twenty-seven entries added to the status table, and every anchored replacement in this
loop asserts its anchor before replacing. The general form is that a silent no-op is worse than an
error, because the commit message describes work the diff does not contain - and the three checks
this project runs compare documents against each other and against the model, but nothing compares
a commit message against its diff.

## W-INTL-150  Two standing advisories promoted to failures

Severity: medium, and the habit matters more than either note.

check_consistency had printed the same two notes for dozens of loops. Both were true and both were
read as furniture - which is how the status-table loss in W-INTL-149 survived four loops of being
reported.

The concession cross-check asked someone to confirm the application's wording concedes what ledger
row E26 does not support. It does concede it, plainly. That is a confirmation that happens once and
has to be recorded where a check can read it, so the application now carries a marker at the
conceding paragraph and its absence fails.

The placeholder count could not express the distinction that matters: an accounted-for placeholder
in a draft is a state of the work, and the same placeholder in a document declared ready is a
defect. The file now declares which it is, and both arms fail.

Four controls run, four fire: marker removed, document marked ready with a placeholder present, no
submission marker at all, and the accounting line for a live placeholder deleted.

The general rule, recorded as a skill: if a note is still true after two runs it is not a note.
Either it can be discharged and should be a failure until it is, or it cannot and does not belong in
a check's output.

## W-INTL-151  The check written for W-INTL-149 could not have caught W-INTL-149

Severity: low as a defect, high as a near miss.

check_commit_claims.py compares a commit message against its diff, which is the gap W-INTL-149 fell
through. Run against the two commits that lost their status rows, it passes both: the audit entries
landed and only the table rows did not, so the numbers do appear in the diff.

That was found by running it against the historical case before trusting it. Without that step it
would be in CI now, looking like coverage of a failure it cannot see - and the loop after would have
recorded the class as closed.

Kept with its scope stated, since the one arm it does have has a control that fires. A second arm
was written and cut: matching file paths against changed files needed a verb list to distinguish "I
changed X" from "X is where this lives", and a heuristic that reports coverage it does not have is
worse than an absent check.

Also recorded: the first version of that control committed and reset to clean up, and the reset
deleted the file under test. The rewritten control substitutes the message in memory and touches no
git state. A destructive command inside a test of untracked work is the project's own debugging
doctrine violated in one line.

## W-INTL-152  The pointer family re-costed, and the axis expected to decide it is inert

Severity: informational, and it closes a question rather than opening one.

W-INTL-121 costed IBS against SLLC at 0.32 of a tile ahead and declined it. The design has moved
three times since, and W-INTL-144 added an axis that runs one way: global thresholding amplifies
bias, the pointer family does not.

Re-costed at the operating point that exists: IBS is 0.20 of a tile ahead, 3.15 against 3.35, the
saving being the masking machinery minus the oscillators the extra positions need. And the entropy
axis does not enter the comparison at all - it feeds the requirement on k, and the code carries 171
against a requirement of at most 137.7 in every arm. The axis expected to decide the question bears
on a constraint that is slack.

One methodological point is worth more than the arithmetic. The measured entropy deficit is
attributed entirely to bias in the thresholding analysis because that is the pessimistic reading
there. Attributing it entirely to bias again here would make IBS appear to recover the whole
deficit, which is the optimistic reading of the same unknown. An assumption cannot be pessimistic in
one comparison and optimistic in the next; the figure is quoted as a range for that reason.

Declined again on the argument that has not changed: IBS needs a random number source SLLC does not,
and its helper data is attackable by machine learning on exactly the correlation this source is
reported to have.

## W-INTL-153  The new check was wired into CI and ran on an empty range

Severity: medium, and it is this loop's own instance of the pattern it recorded.

check_commit_claims.py went into the workflow and its first CI run printed "no commits in
HEAD~1..HEAD, nothing to check" and exited zero. GitHub Actions checks out a merge commit at shallow
depth, so the merge base with main was unreachable, the range collapsed to nothing, and the step
passed green having read no commit message at all.

The status dot was green and the step had done nothing. It was found by reading the run log rather
than the dot, one loop after writing that a check pinned to the wrong thing is worse than no check,
and in the same commit as a skill rule about replaying the motivating failure through a new check.
Replaying it locally is not the same as watching it run where it will live.

Fixed both ends. The workflow checks out full history and passes the pull request's base and head
explicitly rather than relying on a default range, and the script grows --require-commits, under
which an empty range is a failure instead of a polite exit. Controls: an empty range fails, a real
range passes.

The general form for the skill file is that a check has two places it can be inert - the logic, and
the harness that invokes it - and only the first is testable from a shell.

## W-INTL-154  Aging is the first constraint the recommendation fails

Severity: critical. It is the last unchecked constraint that could break the design, and it does.

Every error-rate figure in this work is a fresh-device figure; the register named that and left it.
Rahman, Forte, Fahrny and Tehranipoor, DATE 2014, read rather than summarised: "After 10 years, the
average error in response of the ARO-PUF is 7.73%, whereas it is 32.41% in the conventional
RO-PUF." Their common frequency drift is 1.8 percent and flips nothing, because a drift both
oscillators of a pair share cancels in the comparison. The differential is what flips bits.

Carried into this project's source model, calibrated so the unselected rate reproduces the published
figure: at ten years on a conventional bank the design sees 0.2888 effective error against 0.0442
tolerated. Off by six and a half times. On the aging-resistant variant it sees 0.0334 and fits.

The requirement as a number: the unselected ten-year flip rate must be at or below 9.2 percent.

Two conditions travel with the published figures. HSPICE Monte Carlo at 90 nm - simulation, not
silicon, not this process. And 23 percent activation time, where this design runs its bank once at
power-up for a few thousand cycles. The paper states that activation time in security applications
should be far below 23 percent and that lower activation reduces the error, and gives that sweep for
the aging-resistant variant only. The figure this design would see is not in the source.

Selection helps for the same reason it helps against noise - it ranks by the manufacturing
difference, which is what an aging differential must exceed - and helps far less, because at ten
years that differential is comparable to the manufacturing spread itself. Ranking by a signal buys
little when the perturbation is as large as the signal. Heavier selection does not rescue it: at
32.6 percent kept the conventional bank is still at 0.186.

Open, and it changes what the design is. The oscillator arrangement was specified by count and
length, both driven by entropy; it now carries a reliability requirement neither determines. And one
enrolment per device, recorded for many loops as binding as policy with no cost attached, now has
one - the ten-year figure is what that policy buys.

## W-INTL-155  Two more CI steps that could not tell a clean scan from an empty one

Severity: low, and it is the generalisation of W-INTL-153 rather than a new class.

The banned-vocabulary scan greps a list of directories with errors suppressed, so a renamed-away
path reports no hits in exactly the way a clean scan does. The non-ASCII scan has the same shape.
Both now count what they matched, fail below a floor, and print the count on success - 72 files and
3. Neither was inert today; neither could have said so if it were.

## W-INTL-156  Process corners, half closed by argument and half named

Severity: low, and the value is in refusing to record an argument as a measurement.

Area does not vary with process corner and area is what binds here, so half the question closes
without measuring. Timing and power vary and both have an order of magnitude of slack against a
design that runs a few thousand cycles once at power-up.

The rest stays open with its missing artefact named: the slow-corner liberty
sky130_fd_sc_hd__ss_100C_1v60 is not in this environment, so no derate has been measured. An
argument that a constraint is slack by a factor of ten is not a measurement of it.

## W-INTL-157  The rule that no area is quoted for an unexercised circuit is now enforced by a machine

Severity: medium. The rule has held for eighty loops on memory alone, and it failed twice.

measure_all.sh runs every testbench before printing any area and refuses to print if one fails. That
is the mechanism behind this project's central claim about its own figures, and for eighty loops it
ran only when somebody remembered. It failed twice in five loops: the shared-multiplier solver had
its differential testbench in the repository and not in this script (W-INTL-146), and the SLLC
encoder had no testbench at all while its area was quoted (W-INTL-148).

Split so the half that can run in CI does. --verify-only runs the testbenches and stops; the
synthesis half needs a 13 MB standard-cell liberty that is not in this repository and stays local.
The job installs iverilog and runs 21 testbenches on every pull request.

Two guards on the guard, both controlled. A failing testbench fails the run - checked by turning an
exclusive-or into an and. And the run fails if fewer than twenty testbenches ran, because a suite
that compiles nothing looks exactly like a clean one otherwise, which is the shape of W-INTL-153;
checked by truncating the suite to one entry.

Named and not done: the synthesis half. Putting it in CI means fetching a PDK, and the areas it
would check are already re-synthesised by scripts/verify_inputs.py locally. That is a real gap and
it is smaller than the one just closed.

## W-INTL-158  The reproduction script had never run anywhere but one Mac

Severity: medium, and it was found by the job added in W-INTL-157 on its first run.

measure_all.sh exists so that anyone can reproduce every figure this project quotes in one command.
Its first execution on a Linux runner failed every one of its twenty-one testbenches, all with
"did not compile", because `mktemp -t tb` is a BSD spelling and GNU coreutils rejects a template
with no X's.

Nothing was wrong with the RTL and every testbench passes. What was wrong is that a script whose
entire purpose is third-party reproducibility had only ever been run on the machine that wrote it,
for eighty loops, and said nothing about it.

Fixed with a portable spelling. The general form is that "reproducible" claimed for a script means
reproducible somewhere else, and the first run on foreign ground is the measurement - which is the
same lesson as W-INTL-153 arriving from the other direction: there the harness was inert, here the
harness was the only thing that had ever been exercised.

## W-INTL-159  Two sentences in the aging finding were wrong, from a passage already on disk

Severity: medium. The finding stands; two of the statements supporting it did not.

The 1.8 percent ten-year frequency degradation was read as a *common* drift shared by both
oscillators of a pair and therefore cancelling. The sentence continues "in our proposed ARO whereas
it is about 14.4% for a conventional RO" - it is the aging-resistant device's own degradation. The
modelled quantities are the flip rates, so nothing computed changes, but the mechanism paragraph
asserted something the source does not say.

Worse, the same entry argued that low activation time made the conventional figure pessimistic here,
because this design runs its bank once at power-up. The paper contradicts it: "when the conventional
RO-PUF is put in the oscillating (AC stress) or non-oscillating mode (DC stress) when it is not
used, it will experience significant amount of aging". An idle ring oscillator sits at DC stress,
the worst case for NBTI on the pMOS. Not running it is not resting it, and holding those inputs away
from zero while idle is the aging-resistant design's entire mechanism.

Both passages were in the extracted text when the argument was written. The argument ran the wrong
way, and the reason it was not checked harder is that it was the answer the design wanted. That is
the failure mode worth recording: an unchecked step is likeliest exactly where the unchecked answer
is convenient.

## W-INTL-160  The aging-resistant oscillator costed, and it is seven hundredths of a tile

Severity: closes W-INTL-154, which was the only open critical entry.

Costed from the transistor sizes the paper states - inverters at Wn = 0.12u with Wp = 2.5 Wn, two
added nMOS gates of 0.12u and 0.24u per stage - the aging-resistant stage is 1.86 times a
conventional one by transistor width. The bank goes from 920 to 1,709 square micrometres, the design
from 3.35 to 3.42 tiles of sixteen, and the ten-year effective error from 0.2888 to 0.0334 against a
code tolerating 0.0442.

Adopted. The recommendation is an aging-resistant bank and inputs.py carries the factor with its
derivation and its two stacked approximations stated: transistor width is not layout area, and the
base figure it multiplies is an inverter count from a published tile rather than a layout of this
oscillator. A layout would settle it and the ledger's falsifier says so.

What makes it cheap is a fact established four loops ago for an unrelated reason: the oscillators
are 2.6 percent of the design, because the entropy work took the bank from 341 to 35. A constraint
that would have been expensive at the old operating point is nearly free at this one - the mirror
image of W-INTL-142, where decisions went stale because the operating point moved.

## W-INTL-161  A borrowed input checked against the library, forty loops late

Severity: low, and it passed. The interval is the finding.

INVERTER_AREA comes from a published Tiny Tapeout tile - 6,730 square micrometres across 1,792
inverters, so 3.7556 each - and every oscillator budget in this work rests on it. Checked against
the standard-cell library everything else here is measured on: sky130_fd_sc_hd__inv_1 is 3.7522, a
ratio of 1.0009. The tile's oscillators are drive-1 inverters and nothing was lost in the borrowing.

One grep, against a file that had been on disk for forty loops. A borrowed number with a
one-command check available and unrun is the same shape as W-INTL-100, where the check existed and
the habit did not.

## W-INTL-162  The aging factor bracketed against the library

Severity: low. It does not change the number and it changes what the number is.

The 1.86 aging-resistant factor is the one figure in the recommendation with neither a measurement
nor a synthesis behind it. A tristate inverter is an inverter with two extra series devices, the
same device count the ARO adds: einvn_0 is 1.333 times inv_1 and einvn_1 is 1.666. So two added
devices cost between 1.33 and 1.67 laid out in this library, and the estimate in use is conservative
by eleven to forty percent.

Kept rather than replaced, because a tristate inverter is an analogue and not the circuit - its
enable devices sit in the output stacks where the ARO's second device is a pull-up on the input
node. The bracket does not give a better number; it gives the direction of the error, which is the
difference between an unbounded approximation and a conservative one.

## W-INTL-163  A second source on aging, and the lever it hands over

Severity: medium, and it opens a route that costs no area.

The ten-year requirement rested on one paper: simulated, 90 nm. He, Li, Yu and Yang, ASCH-PUF in
JSSC, report silicon measurements under accelerated aging - 96 hours at 150 C and 1.4 V, "resulting
in equivalent effects of several years' aging under nominal conditions" - on a subthreshold inverter
array rather than a ring-oscillator bank. Aging appears there as an increase in the masking ratio,
which is their name for reliable-bit selection: "at the start of aging is 24% and maintained below
26% throughout the aging experiment".

Two points of extra selection over several equivalent years, measured, against a third of all bits
flipping over ten, simulated. Different devices, and ring oscillators are what the literature
singles out as aging-sensitive, so these do not contradict. What the second source establishes is
that the catastrophic figure is specific to the conventional ring oscillator and not a general fact
about PUFs.

The lever: "S-ASCH benefits from having a burn-in process prior to enrollment", because enrolling
after some aging means "the masking ratio will not have such an aggressive increase". That is a
requirement on the provisioning flow rather than on the die - the same class as the nine enrolment
reads - and it costs no area.

Quantified: this construction absorbs a post-enrolment flip rate of 9.2 percent against a
conventional ten-year figure of 32.41, so burn-in before enrolment must leave at most 28 percent of
the degradation still to come. Whether a practical burn-in achieves that is not answerable from
either source, and it is now a number rather than a hope.

Worth having because the route already adopted, the aging-resistant oscillator, rests on the one
estimate in the design with no measurement behind it. Two independent routes to one requirement,
with different failure modes.

## W-INTL-164  A fetched summary asserted a paper had no aging content; it has twenty-one mentions

Severity: medium as a method finding, and it is the third instance.

The fetch of the ASCH paper returned "this paper contains no discussion of PUF aging, NBTI effects,
bit error rate degradation over time, or lifetime stability measurements", with a list of absent
topics and an assurance it would not fabricate numbers. Extracted and grepped, the same PDF has
twenty-one occurrences of "aging", two of "NBTI", a subsection headed "D. Aging", and the burn-in
result this loop is built on.

Twice before, a summary was wrong about what a source said. This is the first time one was wrong by
asserting absence, which is worse: a wrong quotation gets caught by the next reader, and a wrong
"there is nothing here" ends the search. It is also the cheapest claim to check - one grep of a file
already on disk.

The rule this project has, read the primary source, needs the corollary: a summary saying there is
nothing to read is not evidence that there is nothing to read.

## W-INTL-165  Burn-in costed, and it is not the free route it was recorded as

Severity: medium. It closes a route rather than opening one, and it corrects a number from the
previous loop.

W-INTL-163 recorded burn-in before enrolment as a second route to the ten-year aging requirement, at
no area cost, needing at most 28 percent of the degradation still to come. Both halves were wrong.

The 28 percent was taken in flip rates - 9.2 against 32.41. The quantity that accumulates under an
aging law is the degradation, and what the source model carries is sigma, the width of the aging
differential. In sigma the requirement is 0.2974 against 1.6215, which is 18.3 percent. Flip rate is
a saturating function of sigma, so a ratio taken in flip rates flatters the requirement.

And "no area cost" was not the cost that mattered. Under a power law in time, with the exponent swept
across its published range of 0.16 to 0.5, meeting the requirement means enrolling after 2.82 to 6.67
equivalent years - between a quarter and two thirds of a ten-year service life. At the one
acceleration figure available, 96 hours at 150 C and 1.4 V for "several years" of nominal aging, that
is roughly 54 to 320 hours of oven per part.

So burn-in cannot replace the aging-resistant oscillator; it survives as a supplement that widens a
margin it cannot create. The design is back to one route, and that route rests on the one estimate in
it with no measurement behind it.

Three assumptions are named in research/burn_in.py rather than buried, including the load-bearing one
that no source read here verifies: that the differential between two oscillators inherits the time
dependence of the degradation.

## W-INTL-166  The same error twice in three loops, in the same direction

Severity: medium as a method finding, and the repetition is the whole of it.

W-INTL-159 recorded an argument that ran the wrong way and was not checked because it was the answer
the design wanted. The 28 percent is that failure again, three loops later: a ratio taken in whichever
units were nearest to hand, where those units happened to make the requirement look reachable.

The skill rule written after the first instance - verify twice where the answer is convenient - was in
the file when the second was written. A rule you have recorded is not a rule you have applied.

What would have caught it is narrower and more mechanical than a disposition: a ratio between two
quantities must be taken in the units the mechanism operates in, and when a model carries a parameter
that the observable is a saturating function of, the parameter is the unit. Flip rate is what you
measure; sigma is what accumulates.

## W-INTL-167  Every ratio in the inputs declares its units, and one of them is in the wrong ones

Severity: medium. The check is mechanical; what it found is a real mismatch that was already known
and had never been named as this class.

W-INTL-166 found the same units error twice in three loops, with the disposition written after the
first instance already in the skill file when the second was made. So scripts/check_units.py
requires every ratio in research/inputs.py to carry a units line naming numerator and denominator,
and fails otherwise. On its first run six of six were undeclared. It cannot verify that the units
are right; it forces the claim into the open.

Writing them out found one that is wrong. AGING_RESISTANT_FACTOR is a ratio of transistor widths and
it multiplies an area. Widths and laid-out areas do not scale together, which is precisely why the
library bracket for two added devices - 1.33 to 1.67 - sits below the 1.857 the width calculation
gives.

Kept anyway, and the reasoning is recorded at the point of definition. Adopting the area-grounded
1.67 would shrink the budget; the width figure is the conservative end of a quantity with no
measurement behind it; and on an unmeasured quantity the convenient direction is not the one to move
in. That is the third loop running in which the convenient direction has been the thing to watch.

## W-INTL-168  The burn-in assumption swept rather than asserted

Severity: low, and it strengthens the previous loop's conclusion rather than changing it.

The burn-in numbers rest on one unverified step: that the differential between two oscillators
inherits the time dependence of the degradation. Swept now, with the differential taken as t^(k*n).
k = 0.5 is what a trap-counting picture gives, since a Poisson number of trapped charges has a
standard deviation going as the square root of its mean, so the spread grows more slowly than the
mean and more of it lands early.

Under k = 1 burn-in needs a quarter to two thirds of the service life before enrolment; under k = 0.5
it needs eight to forty-five percent. The literature searched supports only the direction - aging
induced threshold-voltage variability grows with stress and correlates with gate-oxide area - and no
source read here gives the functional form.

Both arms are reported and the requirement is quoted against k = 1, the arm that is not convenient.
Even at the most favourable corner of the favourable arm, burn-in costs eight percent of the service
life before enrolment, so the previous loop's conclusion stands: it supplements the aging-resistant
oscillator and does not replace it.

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
| W-INTL-18 | re-settled at medium on a systematic search; the date is a shuttle delivery, the wording is loose |
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
| W-INTL-36 | retracted; the measurement it rested on was an implementation artefact |
| W-INTL-37 | partly closed; computed as far as the missing unit price allows |
| W-INTL-38 | open, medium; deployment is real and has never been exercised |
| W-INTL-39 | open, high with an RF reviewer; the radio figure is not an SNR |
| W-INTL-40 | measured; the gap is the implementation, and W-INTL-36 is retracted |
| W-INTL-41 | open, high; a verified catalog entry cites an archive without the result |
| W-INTL-42 | retracted; the catalog is correct and the check was too narrow |
| W-INTL-43 | open, high; the 323 MHz claim has no artefact and its cited file is missing |
| W-INTL-44 | open, high for novelty; the 16-bit layout is IBM DLFloat |
| W-INTL-45 | corrected; ownership is renounced everywhere, freezing a known defect |
| W-INTL-46 | open, critical; the identity scheme needs hardware neither part has - superseded in part by W-INTL-47 on how far away the fix is |
| W-INTL-47 | not a weakness; the identity root needs a shuttle macro rather than a funded die |
| W-INTL-48 | open, high; the Solution section asserts GPS that is not on the boards |
| W-INTL-49 | open, high; two radios have never been up together |
| W-INTL-50 | open, high before this committee; the single-satellite-vendor claim is false |
| W-INTL-51 | open, high; proof types are stubs, not produced |
| W-INTL-52 | open, medium; index-based absences re-checked by enumeration, one changed |
| W-INTL-53 | closed as a measurement; the solver is 2.95x the area it was budgeted at |
| W-INTL-54 | corrected; a derived percentage column did not follow from its own table |
| W-INTL-55 | open, high; the decoder was sized for a code the literature recommends against - factor corrected by W-INTL-58 |
| W-INTL-56 | open, high; the pair count R(R-1)/2 was used as entropy and is wrong by transitivity |
| W-INTL-57 | open, high; the code sized for five loops does not reach its own error target at any plausible error rate |
| W-INTL-58 | corrected; the 19.5x advantage is decoders only, 4.4x across the whole design |
| W-INTL-59 | corrected; response positions and min-entropy were collapsed into one constraint |
| W-INTL-60 | open, high; measured entropy per oscillator is a sixteenth of the ordering bound, bracket 0.65 to 14.25 tiles |
| W-INTL-61 | open, high if a security level is ever claimed; response bits are biased and key search is ordered |
| W-INTL-62 | closed as a negative result; the derived-column check found nothing else in 79 revisions |
| W-INTL-63 | open, critical for the hardware plan; helper-data leakage was never counted and the recommended construction has negative residual entropy |
| W-INTL-64 | resolved; BCH(127,15,27) clears leakage, error tolerance and area, decoder measured at 100,709 um^2 |
| W-INTL-65 | open, high if a security level is claimed; the reported bias range is the one that needs a debiasing stage nobody has budgeted |
| W-INTL-66 | corrected; the Chien stage omitted the locator constant term, found by decoding end to end, areas up 3 to 6 percent |
| W-INTL-67 | open, critical; with debiasing the disjoint oscillator arrangement does not fit - figure corrected by W-INTL-68 |
| W-INTL-68 | corrected; 4.4 was the worst debiasing method, range is 1.58 to 5.3, and oscillator reuse is required under all of them |
| W-INTL-69 | open, high; the registry has no stated enrolment policy, and reusability of the key generator depends on it |
| W-INTL-70 | built; the characterisation structure is verified and costs 0.69 tiles |
| W-INTL-71 | resolved; reusable debiasing does not exist for this construction, so one enrolment per device is forced and the registry now says so |
| W-INTL-72 | open, high; the construction needs entropy density 0.9349 against a measured 0.9414, a margin of 0.0065 |
| W-INTL-73 | closed; every synthesis figure reproduces from one script, testbenches first |
| W-INTL-74 | open, high; the code was inherited from a paper along with its operating point, and other borrowed parameters should be checked the same way |
| W-INTL-75 | resolved; BCH(127,22,23) is smaller than the inherited choice with 4.5x the entropy margin, superseding W-INTL-64 |
| W-INTL-76 | closed by measurement; the best-margin code needs 16.88 tiles for its decoder alone |
| W-INTL-77 | corrected; the oscillator floor asked for raw entropy instead of residual, and at the figure in use the construction yields no key |
| W-INTL-78 | closed; the chain runs end to end and an independent implementation confirms the model across four orders of magnitude |
| W-INTL-79 | partly closed; borrowed constants listed, and the one applied wrongly is now computed |
| W-INTL-80 | closed; debiasing overhead computed from its definition, borrowed figures were conservative by 3 to 5 percent |
| W-INTL-81 | closed; the chain runs with debiasing and gives the sizing a third independent witness |
| W-INTL-82 | closed; the recommendation is flat from entropy density 1.00 down to 0.88, refined by W-INTL-84 |
| W-INTL-83 | closed; the reuse claim behind the contract's enrolment policy verified on this construction, mechanism shown not quantified |
| W-INTL-84 | superseded by W-INTL-86; the densification sampled the region already believed flat |
| W-INTL-85 | open, high as a correction; sweeping one input at a time reversed the priority, and the error rate is at least as binding as entropy |
| W-INTL-86 | corrected; two codes below the edge move it from 0.8613 to 0.8155 and the cheapest build from 5.34 to 4.92 tiles |
| W-INTL-87 | superseded by W-INTL-89; the single fraction quoted was over-specific |
| W-INTL-88 | withdrawn by W-INTL-99; the high-error column is blank again once tile utilisation is counted |
| W-INTL-89 | closed; the leak grows monotonically with scale rather than shrinking, and the policy stands on the direction |
| W-INTL-90 | closed; power was absent from the constraint set and is slack - 20 mA needs 609 MHz on the largest decoder |
| W-INTL-91 | closed; the last blank cell is provably empty, not unmeasured - the only three qualifying codes are excluded by a measured point |
| W-INTL-92 | closed; tripling the oscillator length changes no fit verdict, so the borrowed seven-inverter figure is discharged |
| W-INTL-93 | closed; logic depth measured across four sizes, 145 to 300 MHz, and the RTL header's architectural claim confirmed |
| W-INTL-94 | closed; the power figure agrees within 1.2x by a second route through the library, settling the units doubt |
| W-INTL-95 | closed; timing binds before power for the largest decoder, both by an order of magnitude |
| W-INTL-96 | closed; the solver owns the critical path at twice either table stage, and one property predicts both the area and depth ratios |
| W-INTL-97 | corrected; mapped depth is a quarter lower, and a path tracer returned a plausible-shaped meaningless number on the first attempt |
| W-INTL-98 | open, medium; eleven constraints now in one register, six named as unchecked with helper-data manipulation first |
| W-INTL-99 | open, critical; cell area was divided by die area, every tile figure optimistic by 1.7, and W-INTL-88's headline withdrawn |
| W-INTL-100 | closed; synchroniser metastability is 10^120 years at the intended clock, and collapses to 10 years at 100 MHz |
| W-INTL-101 | superseded by W-INTL-105; the distinction is code-offset against syndrome |
| W-INTL-102 | closed; a check now recomputes the headline from inputs, in CI, with three firing controls and a fourth of my own that was broken |
| W-INTL-103 | corrected; two pre-correction figures survived in the same ledger row as the corrected one |
| W-INTL-104 | closed; the five remaining binding rows re-derive correctly, and only the area row had been wrong |
| W-INTL-105 | closed by W-INTL-116; the question need not be asked once the helper data is hashed into the key |
| W-INTL-106 | closed; every input declared once in research/inputs.py with its provenance, three scripts refactored to import |
| W-INTL-107 | corrected; the oscillator floor was the previous code's, found by the extended check on its first run |
| W-INTL-108 | corrected; the end-to-end chain had validated a superseded construction for six loops |
| W-INTL-109 | closed; every declared decoder area is machine-checked against a fresh synthesis run |
| W-INTL-111 | closed; SLLC implemented and measured, two open items closed and the third scoped out |
| W-INTL-112 | closed; SLLC dissolves the oscillator-arrangement constraint, withdrawing W-INTL-67 and W-INTL-68 |
| W-INTL-113 | closed; the n-k bound is confirmed first-hand for the syndrome construction, and Fuzzy Commitment has escaped it since 1999 |
| W-INTL-115 | open, critical; the error-rate constraint assumes all errors must be corrected, and reliable-bit selection reaches 15 percent with 974 response bits |
| W-INTL-116 | closes W-INTL-105; helper-data manipulation has a generic countermeasure, hashing the helper data into the key, absent from every design here |
| W-INTL-117 | open as a method finding; three loops running, a table in already-cited literature removed a constraint treated as fixed |
| W-INTL-118 | measured; retracts the operative half of W-INTL-115 - the mechanism transfers, the advantage does not at this error rate |
| W-INTL-119 | measured; perfect ranking is a bound, thirty-one enrolment reads is the achievable version and its price |
| W-INTL-120 | measured, open as an omission; the countermeasure gives ideal avalanche for one hash and is still absent |
| W-INTL-114 | closed; under zero leakage the entropy density stops binding, withdrawing W-INTL-72, W-INTL-82, W-INTL-84, W-INTL-85 and W-INTL-86 as conclusions about the problem |
| W-INTL-110 | decided rather than open, by W-INTL-111 and W-INTL-112; Systematic Low Leakage Coding removes the leakage term, cutting raw width 4.6x and readmitting the withdrawn construction |
| W-INTL-121 | closed; the pointer family costed against the linear one and declined for a new attack surface, the first measured advantage this work has refused |
| W-INTL-122 | closed; the decoder is 87 percent of the design, which is where the next saving had to come from |
| W-INTL-123 | closed; a branch collision with the cloud routine, and the check adopted after it - verify that merged content reached main |
| W-INTL-124 .. W-INTL-129 | closed; measurement and apparatus entries, each with its control exercised |
| W-INTL-130 | closed; reliable-bit selection adopted, nine enrolment reads made a requirement on the provisioning flow |
| W-INTL-131 .. W-INTL-135 | closed; the countermeasure measured, the ledger's stale figures corrected, controls repaired |
| W-INTL-136 | closed; sharing the key-equation solver's multipliers, 8.79 tiles to 5.40 |
| W-INTL-137 .. W-INTL-140 | closed; the same trade refused for the Chien search, and the reason that refines the rule |
| W-INTL-141 | closed; the code was chosen before selection existed, and re-choosing it takes 5.40 tiles to 3.50 |
| W-INTL-142 | open as a method finding; sixty percent removed in two loops, both revisits of decisions whose operating point had moved |
| W-INTL-143 | closed; the constraint register revised after three loops of deferral, and given the decisions-against-constraints column |
| W-INTL-144 | closed with a guard; selection amplifies the bias it was assumed not to touch, and the previous design failed the leakage bound at the deeper fractions |
| W-INTL-145 | closed; a measured input carried its arrangement and not its selection status |
| W-INTL-146 | closed; two areas declared under the wrong convention, and a gate reported green without being run |
| W-INTL-147 | closed; the figure-reproduction check repointed from a construction eight loops old to the one recommended now |
| W-INTL-148 | closed; the SLLC encoder was the wrong code's, untested, and a bare literal in a script |
| W-INTL-149 | closed; two loops of status rows were silently dropped by an anchorless string replacement, and the note that said so was read as noise |
| W-INTL-150 | closed; two standing advisories promoted to failures, four controls run and firing |
| W-INTL-151 | closed with its scope stated; the commit-claims check cannot see the failure it was written for, which is why the fix is W-INTL-150 |
| W-INTL-152 | closed; the pointer family re-costed at 0.20 of a tile ahead and declined again, and the entropy axis turns out to feed a slack constraint |
| W-INTL-153 | closed; the new check ran on an empty range in CI and passed green having read nothing, fixed at both ends |
| W-INTL-154 | closed by W-INTL-160; aging is the first constraint the recommendation fails - 0.2888 against 0.0442 at ten years on a conventional bank, and the requirement is a ten-year flip rate at or below 9.2 percent |
| W-INTL-155 | closed; two more CI steps that could not tell a clean scan from an empty one |
| W-INTL-156 | half closed by argument, half named; area is corner-independent, and the slow-corner liberty is not in this environment |
| W-INTL-157 | closed; the testbench half of measure_all.sh runs in CI on every pull request, with a failing-testbench control and a count guard |
| W-INTL-158 | closed; the reproduction script had never run anywhere but the machine that wrote it, and failed all 21 testbenches on its first Linux run |
| W-INTL-159 | closed; two sentences supporting the aging finding were contradicted by a passage already on disk, including one that ran the wrong way |
| W-INTL-160 | **closes W-INTL-154**; the aging-resistant oscillator costs 0.07 of a tile and takes the ten-year effective error from 0.2888 to 0.0334 |
| W-INTL-161 | closed and passed; the borrowed inverter area matches the library to within 0.09 percent, checked forty loops late |
| W-INTL-162 | closed; the aging factor bracketed against the library at 1.33 to 1.67 laid out, so the 1.86 in use is conservative |
| W-INTL-163 | open as a route; a silicon source gives burn-in before enrolment as a second way to meet the aging requirement, at no area cost, needing at most 28 percent of the degradation left to come |
| W-INTL-165 | closed as a route; burn-in needs a quarter to two thirds of the service life before enrolment, so it supplements the aging-resistant oscillator rather than replacing it, and the 28 percent it was recorded with was 18.3 |
| W-INTL-167 | closed with a check in CI; every ratio in the inputs declares its units, and the aging factor is a width ratio multiplying an area - kept as the conservative end |
| W-INTL-168 | closed; the burn-in differential-scaling assumption swept, and the conclusion holds at both arms |
| W-INTL-166 | open as a method finding; the same convenient-units error twice in three loops, with the rule against it already in the skill file |
| W-INTL-164 | closed; a fetched summary asserted a source had no aging content and it has twenty-one mentions - the first time a summary was wrong by asserting absence |
