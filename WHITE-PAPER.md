# WHITE PAPER - Trinity S3AI DNA and the GOLDEN CHAIN

**Twenty-seven principles for a borderless ternary compute commons**

| | |
|---|---|
| Document | WHITE-PAPER.md |
| Status | DRAFT v0.9 - not yet the consultation output; v1.0 is due 2027-01-01 and incorporates answers to GREEN-PAPER.md (consultation closes 2026-12-15) |
| Date | 2026-10-10 |
| Issued by | gHashTag/golden-chain-international (hub repository of the GOLDEN CHAIN) |
| Language | English, ASCII. A Russian companion edition follows the same versioning; the English text is canonical. |
| Fact basis | FACTS.md in this repository is the single source of truth for company facts. Nothing here may contradict it; a contradiction is a defect in this paper. |

---

## 1. Abstract

This paper states the constitution of the Trinity S3AI project family as 27
principles in three strands - Truth, Trade, Trust - each principle typed by a
trit: +1 (a duty), 0 (a practice), -1 (a prohibition). It maps those
principles onto the bazaar tradition of open-source production described by
Eric S. Raymond, states honestly where that tradition has never gone, and
defines the mechanisms the project family is building: a content-anchored
manifest of member repositories (the GOLDEN CHAIN), a single specification
language that compiles to FPGA, CPU and NPU targets (t27), a numeric stack
of ternary formats verified on real boards, and a token design whose only
faucet is verified work. The paper also states what does not exist: a
mainnet token, a network, a legal entity, hardware attestation, and
compliance anywhere. Each absence is named because the constitution's first
strand is Truth.

## 2. The 27 principles

Three strands, nine principles each, every principle typed by a trit.
The 3x3x3 structure is a discipline device - it forces each strand to carry
an equal share of duties, practices, and prohibitions - not a claim about
nature. What the trits encode is simple: +1 you must, 0 you measure and
record, -1 you never.

### 2.1 Truth - what the system claims

| # | Trit | Principle |
|---|---|---|
| T1 | +1 | Specs are the single source of truth. Generated code is a shadow of the spec, never a second home for it. |
| T2 | +1 | Every number a document quotes is counted at publication time. A live count, never a remembered one. |
| T3 | +1 | Retract loudly. A wrong claim stays in the record with its retraction beside it; history is never silently edited. |
| T4 | 0 | Provenance is a receipt: which commit, which hash, which date, who reran it. Receipts are written for strangers. |
| T5 | 0 | Label the status of every claim: established, intention, or not established. The third label is respectable. |
| T6 | 0 | The map of the commons is itself data. The manifest of repositories is anchored, versioned, and checked in both directions. |
| T7 | -1 | Never publish what you cannot back. A missing file is more honest than a false one. |
| T8 | -1 | No undocumented human decisions. Agreement is recorded, never assumed; silence is not consent. |
| T9 | -1 | No performance, energy, or precision claim about ternary hardware without a published independent-reproduction path. |

### 2.2 Trade - how value moves

| # | Trit | Principle |
|---|---|---|
| D1 | +1 | Work is the only faucet. Supply enters the system only as rewards for verified work. |
| D2 | +1 | Issuance is by the founder alone, never discretionary in amount: every mint is bounded by the published schedule (cap and halving) and paid only for verified work (bounties and fees), on TON, the single chain of record. Validation stays with the protocol: k-of-n independent operators, one vote per operator. |
| D3 | +1 | Keep the books open. Every reward, every proof, every gate state is public data by default. |
| D4 | 0 | Code is a commons, value is a regulated river. Source obeys no one; flows obey each jurisdiction. |
| D5 | 0 | Many stalls. No exclusive vendor, cloud, or market; concentration is measured and published. |
| D6 | 0 | Red lines are quoted verbatim and gated on written counsel review before any act or text relies on them. |
| D7 | -1 | No allocation. No founder pool, no investor pool, no insider reserve, no airdrop. |
| D8 | -1 | No income promises. Hardware is never marketed with token returns. |
| D9 | -1 | No self-initiated listing; no token sale; the project and its founder do not sell into a market they created. |

### 2.3 Trust - how the system survives people

| # | Trit | Principle |
|---|---|---|
| S1 | +1 | No chief validators. Authority is protocol, not person; every human privilege has a published removal path. |
| S2 | +1 | Ship the bus map. Repositories, documentation, keys, and continuous integration must be able to outlive the founder - and that claim is tested, not asserted. |
| S3 | +1 | Publish the transition from one maintainer to no maintainers, and rehearse it while it is still hypothetical. |
| S4 | 0 | Verification beats trust. Two-direction anchoring, negative controls, mutation tests that must fire. |
| S5 | 0 | Tamper-evident, never tamper-proof. Every integrity mechanism ships with its own defeat analysis. |
| S6 | 0 | Foreign code is debt that only shrinks. The system's own language is its source; other languages are compilation targets. |
| S7 | -1 | Secrets never enter the commons. What was pushed is burned and rotated, never merely deleted. |
| S8 | -1 | No borders in source. No division by nation, color, or race; access to source follows no flag, while participation follows each jurisdiction's law. |
| S9 | -1 | No cathedral exploitation. The commons is never republished sealed, and its artefacts are never sold back to the people who built them. |

## 3. From the bazaar to the hardware bazaar

Raymond's "The Cathedral and the Bazaar" (1997-1999) described why open,
early, frequent release with users treated as co-developers outproduced
sealed corporate development. Its lessons are the ancestors of these
principles. The mapping is honest in both directions: several lessons have
no principle, and the two hardest lessons are stated as open problems
(section 9), not as achievements.

| Raymond's lesson | Principle(s) |
|---|---|
| "Every good work of software starts by scratching a developer's personal itch" | T1 - the specs exist because one person needed the machine to stop lying |
| "Treat your users as co-developers" | S1, S2 - strangers must be able to take over |
| "Release early. Release often. And listen to your customers" | T2, T4 - receipts and live counts are the listening |
| "Given a large enough beta-tester and co-developer base, almost every problem will be characterized quickly" | S4 - but see section 9: the eyes do not exist yet in ternary HDL |
| "If you treat your beta-testers as if they're your most valuable resource, they will become that" | D1 - work is the only faucet; respect priced in receipts |
| "The next best thing to having good ideas is recognizing good ideas from your users" | T5, T8 - claims and agreements are recorded where the system reads them |
| "Often, the most striking and innovative solutions come from realizing that your concept of the problem was wrong" | T3, T7 - retraction is a first-class act |
| "Perfection (in design) is achieved not when there is nothing more to add, but rather when there is nothing left to take away" | S6 - foreign code as debt that only shrinks |
| "Any tool should be useful in the expected way, but a truly great tool lends itself to uses you never expected" | S6 - one language, many targets |

Two lessons the bazaar tradition never solved, stated plainly:

1. **Every bazaar had a seed and a benevolent dictator.** Linux, GNU, the
   BSDs - each began as one person's tree. Raymond documented the bazaar;
   he did not abolish Linus. S1 therefore does not claim the project family
   has no single maintainer today. It has exactly one. The principle claims
   something checkable instead: every human privilege has a published
   removal path, and S3 makes the transition a rehearsal, not a eulogy.
2. **The bazaar ran on cathedral infrastructure.** Compilers, hosting,
   hardware - the open bazaars assembled on donated or corporate ground.
   A hardware bazaar cannot rent that ground; the boards, the toolchain,
   and the reward ledger must themselves be commons. That is why the
   project family builds its own compiler and uses an open FPGA toolchain,
   and why "many stalls" (D5) is measured, not assumed.

## 4. Architecture: the TERNARY NETWORK WEB

The ambition: a network in which operators keep their own FPGA, GPU, CPU
and NPU boards; work is described once in a specification language and
compiled to each target; execution produces receipts; receipts are verified;
verified work is rewarded. Each layer below states what exists, what is
roadmap, and what is undecided.

**Numeric core - exists.** The t27 numeric catalogue holds 109 formats in
13 clusters, counted live on every check. The GF and TNF ternary families
carry bit-exact conformance vectors. Arithmetic cores have been verified at
the board level on an Artix-7 XC7A200T through the openXC7 open toolchain,
and an external collaborator reproduces those results from public artefacts.

**Language and compiler - exists, in migration.** t27 is a specification
language with tests and invariants in the source; t27b, its native backend,
is being rewritten in t27 itself (the self-host epic). The hard rule of the
family: no new hand-written foreign code; foreign code is debt that only
shrinks (S6). One spec, many targets - CPU and FPGA today, NPU as roadmap.

**Open FPGA flow - exists for one silicon family.** Synthesis, place and
route, and bitstream assembly run on open tools for Artix-7. A second
silicon target is an open question (GREEN-PAPER question D6), not a plan.

**Receipts and verification - partial.** Today a receipt is software-signed:
operator identity, work description, result hash, signature. Hardware
binding (the receipt proves which chip ran the work) is research. The
honest line: software-signed receipts are acceptable while nothing of value
moves; the moment value moves, they are not (GREEN-PAPER question D2).

**Reward ledger - exists as design only.** $TRI has one chain of record,
TON (gHashTag/t27 specs/trinet/tri-bridge.t27, a design: no contract,
vault, key or bridged token exists yet). The founder, Dmitrii Vasilev,
alone issues $TRI, and only within the published schedule (cap and
halving) and only as payment for verified work (D2). How the cap and the
halving bind the mint key on chain is not established. The TriToken
contract on Base Sepolia (100 percent of supply minted to a mining-pool
contract, ownership renounced) is a retired testnet experiment: it is not
$TRI, and its supply is not $TRI supply. No mainnet token exists. Three
gates stand before any mainnet move: explorer-verified contract sources;
a fixed key-acceptance registry (today the registry accepts any key - a
known defect with an open issue); and written legal opinions for the
United States and Thailand.

**The GOLDEN CHAIN - lands with this paper (M0, in flight at
publication).** The hub repository (golden-chain-international) is to carry
a manifest: one row per member repository, recording the anchor file, the
commit that carries the anchor, and the SHA-256 of the anchor block - a
marked section of each repository's AGENTS.md. Checks run in both
directions: the hub verifies every spoke at its recorded commit and at
head; each spoke verifies its own row in the hub manifest. Deletion or
alteration is detected, not prevented. Section 9 states how the mechanism
can be defeated; S5 forbids pretending otherwise.

## 5. Economics

The economic constitution is four sentences: no allocation (D7); work is
the only faucet (D1); issuance is by the founder alone, bounded by the
published schedule of cap and halving and paid only for verified work
(D2); the books are open (D3). Everything else -
what work counts, how receipts price, what bootstraps supply before
rewards exist - is explicitly open (GREEN-PAPER questions D1-D9).

The red lines of the finance plan apply verbatim and no paraphrase of them
is authoritative: no token sale or presale; no listing the project itself
initiates; no hardware marketed with a promise of token income; no
marketing that points at token price; the founder and any company do not
sell earned tokens. Each red line requires written counsel review before
anyone acts or writes as if it were allowed.

The doctrine in one line: **code is a commons, value is a regulated
river.** The source is open to everyone everywhere. Participation, rewards,
and any future value flow are gated to what each jurisdiction's law allows,
starting where the project's people and first users are (Thailand, the
United States, the European Union), with written counsel review before any
gate opens. Where the doctrine breaks - and it does break - is an open
question (D7 in the consultation).

## 6. Governance: no chief validators

The rule was given by the owner on 2026-10-10: there are no chief
validators and there can be none; the system must be able to live without
human support. This paper treats that rule as the constitution's hardest
constraint, and it starts by admitting the paradox:

> A system built so far by one maintainer claims it must live without
> maintainers. Until a second person can merge, the claim is a target, not
> a property.

What replaces a chief validator is not another person; it is the
combination of:

1. **Protocol rules fixed in advance** - the issuance schedule (cap and
   halving), reward gates, red lines - published before the first unit
   moves. Issuance has one authority, the founder, and no discretion in
   amount: every mint is bounded by the schedule and paid only for
   verified work (D2), and D9 forbids the sale and listing paths.
   Validation stays with the protocol: k-of-n independent operators, one
   vote per operator.
2. **Two-direction verification** - the hub checks the spokes, the spokes
   check the hub; anyone can rerun both checks from public artefacts (S4).
3. **Recorded agreement** - every human decision that matters is written
   where the system reads it, and silence is never consent (T8).
4. **A published, rehearsed succession path** (S3) - the test of S1 is not
   the absence of people but the presence of a removal path for every
   human privilege, exercised before it is needed.

The known failure modes are published, not hidden: a blockchain halt with
a coordinator's key (Bittensor, 2023) is what a kill switch looks like
when it is called decentralization; a single issuer is a human point of
control, bounded only as far as the schedule binds the mint key on chain,
which is not yet established (D9 question); and a manifest anchored
inside the system it describes is circular until an external anchor -
timestamping, mirrors, a transparency log - breaks the circle. Those are
section 9 items RT-5, RT-3 and RT-4 in the internal red-team audit, and
the consultation asks which external anchor to add first.

## 7. Legal posture

Nothing in this paper is legal advice, and no regulator has seen it.

Facts: no legal entity exists; a Delaware C-corporation is planned. The
founder is in Thailand. There are no investors; the founder holds 100
percent. No token trades; none may be offered; nothing here is an offer. The token exists on a public testnet
where it can carry no value.

Position: compliance by design, country by country, starting from the
jurisdictions where the project's people and first users are. Written
counsel review gates every red line and every mainnet gate. The project
does not claim, and will not claim, compliance "in all countries"; several
jurisdictions restrict exactly what this project combines, and the honest
answer to those jurisdictions is a matter for counsel, not for a slogan.

On sanctions and borders, the split is S8: source has no nationality and
no race; people, money and hardware move under law. Where law requires
screening participants, the network screens participants; it does not
remove the source, because the source is not a person.

## 8. Roadmap

| Milestone | Content | Due |
|---|---|---|
| M0 | Baseline: manifest anchored in the eight core repositories; Green Paper published for consultation; red-team and competitor audits filed | 2026-10-10 (this paper's date) |
| M1 | Consultation runway: answers triaged; browser-verified fact base for load-bearing claims; second maintainer candidate identified (S2 begins) | 2026-12-15 |
| M2 | White Paper v1.0 incorporating consultation answers; anchors extended to the invited family (~55 repositories); coverage metric published | 2027-01-01 |
| M3 | Network pilots: receipt format frozen for software-signed proofs; first external operator runs a paid-in-testnet work unit end to end | Q1 2027 |
| M4 | Compliance: US and Thailand opinions in hand; mainnet gates re-audited; the go/no-go recorded as data | 2027 |
| M5 | Anchors at 100 percent of eligible repositories; succession rehearsal executed and documented | 2027 |

Dates after M2 are intentions (T5), not commitments.

## 9. Risks and open problems

From the internal red-team audit (to be filed as research/redteam.md in
this repository), the ten that bear on this paper, unabridged conclusions
shortened:

1. RT-1 "Compliance in all countries" is falsified by one counterexample.
   This paper therefore never says it.
2. RT-2 Token prose can read as pre-offering disclosure; utility must be
   real before the vocabulary of value appears.
3. RT-3 "Verified compute" is today operator-attested: the registry accepts
   any self-declared key, the verifier key is a labeled placeholder, and
   nothing has ever settled. The papers keep those facts in the same
   sentence as any reward claim.
4. RT-4 The anchor manifest is circular while it lives only in this
   repository; an external anchor (timestamping, transparency log, mirrors)
   must break the circle before M2.
5. RT-5 Governance is a target published as a present property; the
   transition table (one maintainer today, quorum, no indispensable person)
   is the honest answer.
6. RT-6 The bazaar is quoted where its preconditions are absent: the seed
   was a cathedral, iteration costs real hardware, and the eyeballs do not
   exist yet. Cite the mechanics, publish contributor counts.
7. RT-7 The engineering-adoption gap is one-line refutable: no GCC/LLVM
   backend, no debugger story, one chip family on the open flow; roadmap
   rows must carry their evidence level.
8. RT-8 Single points of failure contradict the resilience narrative: one
   account, one founder, no entity. A bus-factor disclosure table is owed.
9. RT-9 Constant-heavy framing taxes the numeric work's credibility; the
   trit typing is serialization, not enforcement, and says so (section 2).
10. RT-10 The consultation's audience and disposition log must exist, and
    silence must never be narrated as consent (T8 applied to ourselves).

## 10. References

- Eric S. Raymond, "The Cathedral and the Bazaar" (1997; book 1999).
- FACTS.md, FINANCE_AND_COMPLIANCE.md - this repository;
  paper/evidence_ledger.md is filed with the M0 batch.
- research/world-practice.md, research/competitors.md, research/redteam.md -
  to be filed in this repository as the M0 audit batch (internal audits,
  [KNOWN]/[UNVERIFIED] tagged).
- The t27 numeric catalogue: gHashTag/t27, specs/numeric/formats_catalog.t27.
- GREEN-PAPER.md - the consultation this paper answers.

## Version history

| Version | Date | Change |
|---|---|---|
| 0.9 | 2026-10-10 | First full draft for internal review; consultation answers pending |
| 0.9 erratum | 2026-10-11 | Section 7: there are no investors; the founder holds 100 percent (FACTS.md section 3, founder, 2026-10-11) |
| 0.9 erratum | 2026-10-11 | Principle D2 rewritten, sections 4, 5 and 6 to match: issuance is by the founder alone, bounded by the published schedule and paid only for verified work, on TON; the TriToken contract on Base Sepolia is a retired testnet experiment, not $TRI (FACTS.md sections 3.1 and 6, founder, 2026-10-11). D2 previously read "Publish the rules of emission before the first unit moves. Halving, not discretion; a schedule, not a decision." |
| 1.0 | planned 2027-01-01 | Incorporates GREEN-PAPER consultation; anchor coverage extended |

---

*Truth, Trade, Trust - three strands, twenty-seven principles, one trit at a
time.*
