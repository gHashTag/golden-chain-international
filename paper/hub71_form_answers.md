# Hub71+ AI Cohort 20 - form answers
# Golden Chain / Trinity - ASCII-only, hard-rules compliant
# Rules honoured: ASCII only (R1), no state rhetoric (R2), ADGM vessel (R3),
# naive vs honest paired (R7), no hype words (R9), [Open conjecture] tagged (R10).

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

Compute, on hardware. Three Artix-7 boards, a 309 MHz inference core, a
quantisation-aware training pipeline for 1.58-bit weights, and a published
numeric format family. Top-5 in OpenAI's Parameter Golf at 0.9650 bits per byte.

Numeric foundation, published. GoldenFloat (arXiv:2606.05017) and an 83-format
numeric catalog (arXiv:2606.09686), with an open reference implementation.

Economics, written and audited. Four proof types, one settlement contract, seven
checks. No premine, no venture allocation, no treasury. Nine halvings over forty
years.

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
- 110 test blocks, 4,463 lines of Rust, no unsafe code
- Settlement contracts written and deployed to testnet
- Two arXiv preprints; a peer-reviewed track underway
- Apache-2.0 for code, CC-BY 4.0 for text, publicly auditable

## Hub71+ AI question

Is your startup utilizing or building AI solutions as part of its core product
offering? Yes.

Which category best describes your focus? AI infrastructure - verifiable
low-precision inference at the edge and the network that delivers it.

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
