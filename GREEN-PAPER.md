# GREEN PAPER - The GOLDEN CHAIN and Trinity S3AI

**A consultation on a borderless, ternary, open compute commons**

| | |
|---|---|
| Document | GREEN-PAPER.md |
| Status | CONSULTATION DRAFT v0.1 - comments invited |
| Date | 2026-10-10 |
| Consultation closes | 2026-12-15 (responses processed into White Paper v1.0, due 2027-01-01) |
| Issued by | gHashTag/golden-chain-international (the hub repository of the GOLDEN CHAIN) |
| License | Same as the repository (see LICENSE) |
| Language | English, ASCII. A Russian companion edition is planned; the English text is canonical. |

A green paper invites discussion. It is not a promise, not an offer, and not a
plan that has been agreed by anyone. Every statement of fact in this paper is
either established in FACTS.md of this repository - the single source of truth
for company facts - or it is marked as a question, an intention, or not
established. Where this paper asks a question, the authors genuinely do not
know the answer and want yours.

---

## 1. Why this paper exists

Concentrated AI compute creates concentrated power. The dominant answer today
is a small number of vendors selling sealed accelerators, sealed toolchains,
and sealed models. The alternative tradition - the bazaar tradition of open
source, described by Eric S. Raymond in "The Cathedral and the Bazaar" - built
the software world by a different method: publish everything, let strangers
improve it, let merit route attention.

That method was never seriously applied to compute hardware at network scale.
Hardware has iterated like cathedrals: expensive mask sets, closed bitstreams,
vendor-held keys, and a developer who is a tenant, never a owner.

The GOLDEN CHAIN project family (123 public repositories under one GitHub
account at the time of writing) has spent 2024-2026 building the pieces of a
different starting point:

- a ternary numeric stack - formats GF and TNF with bit-exact conformance
  vectors, verified on a real Artix-7 XC7A200T board through the openXC7 open
  toolchain;
- its own specification language (t27) and compiler, whose rule is that
  hand-written foreign code is debt that only shrinks;
- a token, TriToken, that exists today only on a public testnet, with 100
  percent of supply minted to a mining-pool contract, contract ownership
  renounced, no allocation to any person, and rewards only for verified
  compute proofs on a four-year halving schedule;
- no legal entity, one maintainer, and a growing list of external
  collaborators who showed up because the artefacts are public and checkable.

This paper asks the world a question: can such a stack become a commons - a
TERNARY NETWORK WEB of FPGA, GPU, CPU and NPU boards owned by their operators,
rewarded for verifiable work, governed by rules rather than by people - and
if so, what must be true first?

## 2. What exists today (and what does not)

Established (see FACTS.md in this repository; the evidence ledger,
paper/evidence_ledger.md, is filed with the M0 batch):

- One founder, Dmitrii Vasilev, based in Thailand. No legal entity exists
  yet; a Delaware C-corporation is planned. There are no investors; the
  founder holds 100 percent of the equity.
- The numeric catalogue of the t27 language holds 109 formats in 13 clusters
  and is counted live on every check - never quoted from memory.
- Board-level verification of ternary arithmetic on Artix-7 hardware exists
  and is reproduced by an external collaborator from public artefacts.
- TriToken exists on Base Sepolia (testnet) only. No mainnet token exists.
  Three gates stand before any mainnet move: explorer-verified contract
  sources, a fixed key-acceptance registry, and legal opinions for the United
  States and Thailand.

Not established, and not claimed:

- Any mainnet deployment, any traded token, any income to anyone.
- Hardware-attested compute proofs. Today proofs are software-signed; the
  hardware-binding path is research, not capability.
- Any corporation, foundation, council, or governance body. None exists.
- Compliance "in all countries". Section 6 explains why that formulation is
  dishonest and what we propose instead.

## 3. The proposal, in one page

**Trinity S3AI DNA** is a set of 27 principles arranged in three strands of
nine - Truth, Trade, Trust - each principle typed by a trit: +1 for a duty,
0 for a practice, -1 for a prohibition. The principles are distilled from the
observed practice of the bazaar tradition (including its failures), from the
project's own recorded mistakes and retractions, and from one hard rule given
by the owner on 2026-10-10: there are no chief validators and there can be
none; the system must be able to live without human support.

The **GOLDEN CHAIN** is the mechanism that makes the principles checkable:
a manifest in this hub repository records, for every member repository of the
family, a SHA-256 content anchor - a block in each repository's AGENTS.md
whose hash is recorded here together with the commit that carries it - and
automated checks run in both directions: the hub verifies every spoke, and
each spoke verifies itself against the hub. Removing an anchor is not
impossible; it is *loud*. The honest name for this is tamper-evident, not
tamper-proof, and the manifest says so in its own header.

The **TERNARY NETWORK WEB** is the ambition under consultation: a network in
which operators keep their own boards, execute work described in one spec
language that compiles to FPGA bitstreams and to CPU/NPU code, and earn
rewards against receipts. What is real today is the numeric stack, the
compiler, the board proofs, and a testnet token whose properties (no
allocation, renounced ownership, scheduled emission) are the proposed
economic constitution. What is not real today is the network itself, and this
paper does not pretend otherwise.

## 4. The 27 questions

Answers are requested by 2026-12-15. Each question names its strand. Answer
one or answer all; disagreement is as welcome as agreement.

**Truth strand - about what the system claims:**

1. T1. When a document quotes a live number (a catalogue count, a benchmark),
   must the number be recomputed at publication time, and who arbitrates a
   dispute between two recomputations?
2. T2. What belongs in a public evidence ledger, and what must never be
   written in one (private deal terms, for example)?
3. T3. How should a project publish its own mistakes? Is the retraction-
   beside-the-claim pattern (used in this repository) the right minimum?
4. T4. Should provenance receipts be human-readable, machine-checkable, or
   both - and what is the minimum machine-checkable form for a hardware
   result (which board, which bitstream hash, which vectors, who reran it)?
5. T5. Is a single-maintainer project honest in claiming openness? What
   evidence would convince a skeptic that the bazaar is real and not a
   one-person cathedral with visitors?
6. T6. One public language (English) with translated companion editions - is
   that the right rule for a project that claims to be for all humanity?
7. T7. What claims about ternary arithmetic should be forbidden until
   independently reproduced (energy per operation, "equivalent precision",
   frequency claims)?
8. T8. How much of the compliance position should be public? This
   repository publishes its legal plan and red lines; is that naive or is it
   the point?
9. T9. What is the honest way to present constants (phi, 3^3 = 27) in a
   public technical document so that the mathematics stays clean and the
   framing does not invite dismissal?

**Trade strand - about how value moves:**

10. D1. No allocation, no insider pool, rewards only for verified work: is
    this economically survivable, or does it guarantee that only the already-
    equipped participate? What bootstraps supply before rewards exist?
11. D2. If rewards require verified receipts, and hardware attestation is
    unsolved, is a software-signed proof enough for a zero-value testnet but
    dishonest beyond it? Where exactly is that line?
12. D3. Fixed halving versus any discretionary emission: is a schedule that
    cannot be changed also a schedule that cannot be fixed?
13. D4. Should the network buy only compute, or also review, curation, and
    documentation (the work open source actually runs on)?
14. D5. Red lines - no token sale, no self-initiated listing, no hardware
    marketed with income promises - are quoted verbatim in our finance plan.
    What did we miss?
15. D6. Many stalls, no exclusive vendor: does a commons that runs on one
    vendor's chips (today: one FPGA family, one open toolchain) meet its own
    principle? What is the realistic second silicon target?
16. D7. "Code is a commons, value is a regulated river": jurisdictions
    regulate flows, not source. Where does this doctrine break?
17. D8. How should a network treat an operator who lawfully participates in
    one jurisdiction and is sanctioned by another?
18. D9. If nobody holds the treasury (ownership renounced), what happens
    when the contracts need fixing? Is immutability a duty or a hazard?

**Trust strand - about how the system survives without people:**

19. S1. "No chief validators" - is a validator-less commons achievable, or
    is it a renaming of "the maintainer is the validator until he stops"?
    What is the first mechanism that actually removes a human point of
    control?
20. S2. Two-way content anchoring (hub verifies spokes, spokes verify hub)
    is tamper-evident, not tamper-proof. What external anchor - timestamping,
    mirrors, transparency logs - would you add first, and why?
21. S3. What must be true before the project's repos survive the founder's
    disappearance? (Keys, ownership transfer, funding of CI, documentation
    depth - be specific and unsentimental.)
22. S4. Open source security practice says many eyes make bugs shallow;
    ternary HDL has few eyes anywhere. Until the eyes exist, what formal or
    simulation substitute earns trust?
23. S5. A single GitHub account holds 123 repositories. What is the minimum
    organizational form (not necessarily legal) that makes that acceptable?
24. S6. Secrets never enter the commons; a pushed secret is burned and
    rotated. Is there any case where publishing-then-rotating is not enough?
25. S7. One spec language, many targets, foreign code as shrinking debt:
    pragmatic or self-isolating? Would you join a project whose rule is that
    your favorite language is only ever a compilation target?
26. S8. The bazaar has no borders for source. People and money cross borders
    under law. Is that split coherent, or a lawyer's fantasy?
27. S9. What would make YOU join - with your board, your time, or your
    reputation? Not rhetorically: name the artefact, the proof, or the
    contract that would be sufficient.

## 5. What this paper is not

- Not an offer of securities, tokens, employment, or partnership.
- Not a claim of compliance anywhere. No regulator has been consulted on
  this text.
- Not a prediction that the TERNARY NETWORK WEB will exist.
- Not a document agreed by any stakeholder other than its authors.
  Agreement is recorded, never assumed (FINANCE_AND_COMPLIANCE.md section 6).

## 6. On "compliance in all countries"

The goal as originally stated by the founder was "pass compliance in all
countries". That formulation is not defensible, and this paper does not
repeat it: several jurisdictions ban or restrict precisely the components
this project combines (tokens, borderless networks, strong cryptography,
hardware export). The defensible formulation, on which comment is invited,
is:

> Compliance by design, country by country: the source is open to everyone
> everywhere; participation, rewards, and any future value flow are gated to
> what each jurisdiction's law allows, starting from the jurisdictions where
> the project's people and first users actually are (today: Thailand, the
> United States, the European Union), with written counsel review before any
> gate opens.

## 7. How to respond

- Open an issue in gHashTag/golden-chain-international with the label
  `green-paper` (or any clear title; the label is a convenience).
- Email: admin@t27.ai with "GREEN PAPER" in the subject.
- Answers may be quoted (attributed, unless you ask for anonymity) in the
  White Paper and its revision history. Say so if you do not want that.

## 8. Version history and errata

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-10 | First consultation draft |
| 0.1 erratum | 2026-10-11 | Sections 2 and 5: there are no investors; the founder holds 100 percent of the equity (FACTS.md section 3, founder, 2026-10-11) |

Errata will be recorded in this table and never silently edited; the
repository history is part of the record.

---

*Truth, Trade, Trust - three strands, twenty-seven principles, one trit at a
time.*
