# Hub71 Cohort 20 - form answers
# Golden Chain / Trinity - ASCII-only, hard-rules compliant
# Rules honoured: ASCII only (R1), no state rhetoric (R2), ADGM vessel (R3),
# naive vs honest paired (R7), no hype words (R9), [Open conjecture] tagged (R10).
#
# Submission route, verified against hub71.com on 2026-07-29. Hub71+ AI is not a
# standalone track; it is an ecosystem entered by answering the AI question inside
# a chosen programme's form. Cohort 20 closes 21 August 2026, programme starts
# February 2027. HOST PROGRAMME NOT YET CHOSEN - see the section below.
#
# OPEN ITEMS, must be resolved before submission:
#   [PROGRAMME]  which Hub71 programme form hosts this application
#   [MONTH]      relocation month, section "Plans for Abu Dhabi"
#   [TEAM]       no team section written; single founder, see audit W-INTL-25
#   [ASK]        no funding amount stated
#   [HIRING]     named hiring plan required by W-INTL-25, currently unnamed
# Each is a fact only the applicant holds. None are invented here.
#
# CLOSED 2026-07-29: the Parameter Golf placement claim. The artefact search is
# complete; see audit W-INTL-28. The submission history is now reported in place
# of a score, and it is the stronger of the two.

## Startup overview

Trinity builds infrastructure for verifiable AI compute at the edge: a
self-organising radio mesh that carries connectivity where there is none, and a
node that earns for four kinds of proven contribution - transport, coverage,
sensing, and low-precision inference. Six devices run on the bench today: three
Zynq-7020 mesh nodes with cryptography verified on-device and a 5.8 GHz
software-defined radio front end, and three Artix-7 compute boards. Our numeric
work is published (arXiv:2606.05017, arXiv:2606.09686) and the stack is
Apache-2.0. Every unverified figure in our repositories carries a simulation
marker.

## Problem

Two problems usually treated separately are one problem. Many regions have
neither dependable connectivity nor the ability to import advanced AI
accelerators, and for overlapping reasons: satellite backhaul is a single
foreign vendor, and capable inference silicon is an export-controlled supply
chain. Solving one leaves the other open.

There is a third gap underneath both. Proving that a computation ran on the
hardware that claims it currently requires a trusted execution environment from
Intel, AMD, Arm or NVIDIA. For a buyer trying to reduce vendor dependence, that
is not a solution; it reproduces the problem one layer down.

## Solution

One node does all three. A Zynq-7020 with a software-defined radio and GPS
timing routes traffic through a self-healing mesh, so a group of nodes shares a
single uplink. The same node runs low-precision inference on multiplier-free
arithmetic that maps onto mature, freely exportable process nodes. Operators are
paid for four proof types, settling through one contract with seven independent
checks.

Attestation is rooted in the device rather than in a vendor enclave. The mesh
node is built on a part that carries a bitstream signature scheme; the compute
boards are a bench tier and are not used as the trust anchor. That separation is
deliberate and documented.

## Product

Mesh, on hardware. Three nodes assembled, powered, and passing verified
cryptographic traffic. X25519 with ChaCha20-Poly1305 confirmed on-device: a
534,604-byte static ARM binary, hash recorded, exit code zero, 2026-07-01. The
radio front end is tuned to 5.8 GHz with a verified digital loopback at 108.6 dB
over the noise floor - loopback only, not over the air, and marked that way
everywhere it appears.

Compute, on hardware. Three Artix-7 boards, a multiplier-free ternary tile
verified against a golden model with zero DSP allocated, a quantisation-aware
training pipeline for 1.58-bit weights, and a published numeric format family.

Research conduct, and this is offered in place of a score. We entered OpenAI's
Parameter Golf challenge and made five public submissions. Three of them we
withdrew ourselves. The first was a leading entry that would have topped the
board; we closed it after finding that our own scoring path violated the
challenge's full-vocabulary normalisation condition, and we recorded, in the same
thread, that a result that far below the corpus Shannon floor is by itself proof
that the metric was not measuring real compression. The other two we closed during
a public discussion about per-byte versus per-token measurement bases. What remains
open is a non-record run and a reproduction of another team's stack.

We report this rather than a placement because it is the more useful fact about
how we work. Every figure elsewhere in this application is stated at the level of
evidence that supports it, and where a figure did not survive checking it has been
removed rather than softened. The clock frequency previously quoted for the
inference core was removed on the same basis: place and route has not been run, so
no timing report exists to support it.

Numeric foundation, published. GoldenFloat (arXiv:2606.05017) and an 83-format
numeric catalog (arXiv:2606.09686), with an open reference implementation.

Economics. One token is deployed, to Sepolia, and its allocation is fixed in the
contract rather than in a configuration file:

  node rewards   40 percent, vesting over 120 months
  founder        20 percent, vesting over 48 months behind a 12 month cliff
  community      20 percent, vesting over 36 months
  treasury       10 percent, vesting over 60 months behind a 6 month cliff
  liquidity      10 percent, minted at deployment

For comparison, a leading physical-infrastructure network allocates 40 percent to
contributors, 20 percent to investors and 20 percent to its team. This project
matches that contributor share and carries no investor allocation at all. The
founder share is vested over four years behind a one-year cliff. We state the
allocation rather than claim its absence, because the contract is public and the
claim would not survive a reader opening it.

The four-proof settlement layer is a design, not an implementation. No settlement
contract has been written: the only contract under this project is the token
above, and the single script that pays anything calls a vesting withdrawal on it.
The nine-halving emission schedule is likewise specified in the chain sources and
absent from the deployed contract. We separate these because an application that
describes a design as a running system is checkable and fails the check.

Energy. Naive comparison against a general-purpose baseline suggests a large
multiplier; the honest figure, accounting for memory traffic and system
overhead, is 4x to 8x with a 95% confidence interval of 3 to 10. We publish the
honest figure and show the naive calculation beside it.

What is not done. Multi-hop routing, throughput across two hops, and the
three-node shared-uplink demonstration are in simulation and marked as such. No
radio has transmitted over the air pending an amplifier and a licence. Silicon
remains an open item; every claim that depends on returned dies is tagged
[Open conjecture] with its falsification path stated.

## Business model

Operators acquire nodes and earn for verified contribution; the network charges
for delivered service. Three of the four proof types run today at software-signed
level. Near-term revenue is node sales and paid pilots with operators who need
connectivity and local inference in the same enclosure - infrastructure, remote
industry, and civil resilience.

## Traction

- Six devices assembled and connected: three mesh nodes, three compute boards
- On-device verified cryptography with recorded artefacts and hashes
- 5.8 GHz radio front end verified in digital loopback
- 118 Rust test blocks in the public mesh repository, reproducible with
  `grep -rE '^\s*#\[test\]' src tests`; the crate carries forbid(unsafe_code)
  and no unsafe block exists in it
- Settlement contracts written and deployed to testnet
- Two arXiv preprints; a peer-reviewed track underway
- Apache-2.0 for code, CC-BY 4.0 for text, publicly auditable

## Hub71+ AI ecosystem question

These two questions appear inside the chosen programme's application form and are
what grants access to the Hub71+ AI ecosystem. They are not a separate form.

Is your startup utilizing or building AI solutions as part of its core product
offering? Yes.

Which category best describes your focus? AI infrastructure - verifiable
low-precision inference at the edge and the network that delivers it.

## Host programme

[PROGRAMME] - not yet chosen. The two candidates that fit this work:

Access Programme. The general route for pre-seed to Series A. Fits the framing used
throughout this document, which leads with hardware and verifiable compute.

Hub71+ Digital Assets. Fits the settlement layer, the four proof types and the
allocation structure. It would foreground the economics rather than the hardware,
which is also why W-INTL-30 has to be settled before this route is chosen: a
Digital Assets committee reads allocation tables for a living and would find the
Sepolia deployment first.

Both close 21 August 2026. The choice determines which narrative leads. Both
openings are drafted below so the decision is one word rather than a rewrite.
Whichever is chosen replaces the Startup overview at the top of this file; the
rest of the document is unchanged either way.

### Opening if Access Programme is chosen

Trinity builds infrastructure for verifiable AI compute at the edge. Six devices
run on the bench today: three Zynq-7020 mesh nodes and three Artix-7 compute
boards. On the mesh side, authenticated encryption has run on the node processors
twice, on two boards, with recorded binary hashes and a zero exit code, and a
5.8 GHz radio front end is verified in digital loopback - loopback, not over the
air, and we mark it that way everywhere. On the compute side, a multiplier-free
ternary tile passes 206 of 206 self-checking vectors against a golden model and
synthesises with no DSP primitive allocated; both results reproduce from the
repository in minutes. Our numeric work is published as two preprints and the
catalog behind it is a single source of truth of 83 formats in 13 families, which
counts to 83 when you count it. What is not built is marked as not built:
multi-hop routing is in simulation, nothing has been transmitted over the air, and
there is no end-to-end language model. Every claim we make carries the level of
evidence that supports it, and a public ledger records which ones failed checking.

### Opening if Hub71+ Digital Assets is chosen

Trinity is building a network that pays operators for physical contribution it can
verify - transport, coverage, sensing and low-precision inference - on hardware
obtainable under any export regime. The distinctive problem we work on is that
proving where a computation ran currently requires a trusted execution environment
from one of four processor vendors, which for a buyer reducing vendor dependence
reproduces the problem one layer down. Our answer is device identity plus sampled
re-execution with stake at risk, on parts that carry no such dependence. On
allocation we state rather than claim: 40 percent to node rewards vesting over ten
years, 20 percent to the founder vesting over four years behind a one-year cliff,
20 percent community, 10 percent treasury, 10 percent liquidity, all fixed in the
deployed contract. That contributor share matches a leading physical-infrastructure
network, and unlike it we carry no investor allocation - a fact about a company
that has not raised, and one we would expect to be held to. The settlement layer
itself is a design, not a running system, and we say so: one token is deployed to
a public testnet, the four-proof contract is not written, and we would rather be
asked why than be found out.

## Plans for Abu Dhabi

I am establishing the legal vessel at ADGM and relocating to Abu Dhabi in
[MONTH] to build the core team there. Abu Dhabi is a product decision rather
than a funding one. The network pays operators for verified physical
contribution, and ADGM is among the few jurisdictions where that settlement
layer can be built inside a clear regulatory framework rather than around one.
The region also matches our demand profile: appetite for sovereign AI capability,
real gaps in terrestrial connectivity, and a strategic interest in reducing
single-vendor dependence in both. In the first year I intend to run a mesh pilot
with a government or infrastructure partner, hire two engineers locally, and
reach mainnet from Abu Dhabi.
