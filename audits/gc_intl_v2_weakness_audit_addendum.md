# Weakness Audit Addendum: W-INTL-16 .. W-INTL-51

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

REOPENED 2026-07-30, severity back to high. The revision above checked one
repository and generalised.

The DePIN daemon repository's README carries, in a warning block, a scheduled
hardware tape-out date of 2026-12-16, with a performance projection described as
pending that tape-out. That is a dated fabrication commitment in a public README -
which is what this entry originally said and what the revision denied. The revision
was right about tt-trinity-gamma and wrong about the account.

Two things plainly. The revision was made by inspecting one file and concluding about
the whole, which is the error recorded in W-INTL-32 and again in the family-inference
correction inside W-INTL-46. It keeps arriving in different clothes: an entry revised
on partial inspection is not revised, it is guessed at with more confidence.

And the projection beside that date is handled well - labelled projected and pending
tape-out, which is the discipline the account applies unevenly. The problem is the
date, not the number.

Action.

1. Use two distinct terms in every external document - shuttle tile for the Tiny
   Tapeout work, custom die for the funded path - and never let a claim about one
   carry over to the other.
2. Remove the tape-out date from the public README or state the funding position
   beside it. A scheduled fabrication date in a public file is read as a commitment.
3. Re-audit the remaining repositories for dated commitments rather than assuming the
   two inspected so far are representative.

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
| W-INTL-18 | REOPENED; the revision checked the wrong repository, a dated tape-out is public |
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
