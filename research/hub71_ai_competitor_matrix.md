# Hub71+ AI Competitor Matrix

Status: Wave-intl-2 draft
Scope: the AI-infrastructure landscape this application competes in. The mesh
and decentralised-infrastructure competitor work lives in the mesh repository;
this file covers the compute and verification axes that an AI track will weigh.

Figures marked [PUB] are taken from the cited publication. Figures marked [EST]
are derived from device data and design structure, not measured. No [EST] figure
may be presented as a result.

---

## 1. Low-precision inference accelerators

| System | Platform | Decode throughput | Power | Per watt | Source |
|---|---|---|---|---|---|
| Reference edge accelerator v1 | AMD Kria KV260, Zynq UltraScale+ XCK26 | 9.51 tok/s [PUB] | under 7 W | 1.36 | arXiv:2504.16266 |
| Reference edge accelerator v2 | same board | 25 tok/s [PUB] | 5 W | 5.00 | arXiv:2510.15926 |
| High-end FPGA, small model | datacentre-class board | 16,300 tok/s [PUB] | 46 W | 354 | TerEffic, 2025 |
| High-end FPGA, larger model | same, with high-bandwidth memory | 727 tok/s [PUB] | 46 W | 15.8 | TerEffic, 2025 |
| Dedicated silicon | custom die | not comparable | 4.69 mW [PUB] | n/a | ISSCC 2025 |
| Trinity, one node | mature-node bench board | 13.7 tok/s [EST] ceiling | 6 W [EST] | 2.29 | this work |

Reading. On throughput per watt Trinity is below the current edge state of the
art by more than a factor of two, and the figure quoted is a memory-bandwidth
ceiling rather than a benchmark, so a measured result will be lower.

The application must not claim an efficiency advantage. The numbers do not
support it and the comparison is public.

## 2. Where the contest actually is

The reference edge accelerator states its own limitation plainly: its decode
gap is architectural rather than algorithmic, arising from external memory
bandwidth, and the remedy it proposes is a higher-bandwidth platform - a
high-bandwidth-memory FPGA or custom silicon.

Verified against the source on 2026-07-29. The v1 paper attributes its decode
throughput gap to the board's limited external memory bandwidth and states that
"this limitation is architectural rather than algorithmic" (arXiv:2504.16266),
proposing HBM-enabled FPGAs or custom ASICs as the scaling path. The 9.51 tok/s
figure appears in the contributions list and the evaluation section of the same
paper, not only in the abstract, where the rounded form 9 tok/s is used. The v2
figures of 25 tok/s under 5 W are confirmed in arXiv:2510.15926.

This matters because the argument of this section rests on the cited work
diagnosing the bottleneck itself. That diagnosis is quoted, not inferred.

That remedy costs roughly forty times the board price, an order of magnitude
more power, and a process node that a buyer concerned with supply-chain
independence may not be able to obtain.

Modelling confirms the shape of the problem. On a mature-node board the compute
ceiling is reached far later than the memory ceiling: roughly 1 TOPS of logic
against a 13.7 tok/s bandwidth limit for a mid-size model. A single node
saturates memory long before it saturates logic.

If decode is bandwidth-bound per node, aggregate bandwidth scales with node
count. That is what a mesh is for. It is not an accessory to the compute story;
it is the architectural response to the bottleneck the field has already named.

Stated honestly: per watt and per unit cost, an array of mature-node boards does
not beat one modern edge board. It differs on a separate axis - every node is
obtainable under any export regime, and capacity grows by adding nodes rather
than by acquiring restricted parts.

## 3. Verification of remote compute

| Approach | Root of trust | Consequence for a supply-chain-independent buyer |
|---|---|---|
| Trusted execution environment | processor vendor enclave | reintroduces dependence on the vendor whose supply the buyer is trying to reduce |
| Succinct cryptographic proof | mathematics | strongest guarantee, high proving cost, immature for general workloads |
| Device identity registry | hardware fingerprint plus secret | practical, and the level at which physical-infrastructure networks actually operate |
| Economic assurance | stake and sampled re-execution | cheap to verify, expensive to defeat, no cryptographic absolutes |

The dominant deployed answer is the first row. Its structural cost is the point
of this application: proving where a computation ran currently requires trusting
the same small set of vendors that the buyer is trying to depend on less.

Trinity's position is the third and fourth rows combined, on parts that carry no
such vendor dependence. As far as this research found, that combination is not
occupied.

Honest boundary. This is assurance, not proof. On the parts in question a
cryptographically unbreakable attestation is not achievable - see the audit
addendum. The correct phrase is economically secure attestation, and the
economic parameters are published: sampled re-execution at 1 percent with stake
set at 100 times the unit reward makes cheating unprofitable at any horizon.

## 4. Decentralised compute networks

Structural comparison only; no throughput figures are asserted for third
parties.

| Dimension | Typical decentralised compute network | This work |
|---|---|---|
| Hardware | general-purpose accelerators, operator-supplied | purpose-built node, mesh radio plus inference in one enclosure |
| Attestation | device identification through vendor serials and capability benchmarks | device secret plus sampled re-execution |
| Failure mode addressed | operator misrepresenting hardware | operator misrepresenting work performed |
| Connectivity assumption | node has an internet connection | node provides connectivity to others |
| Token allocation | commonly includes founder, investor and treasury allocation | none of the three |

The connectivity row is the differentiator most likely to be missed. Every
comparable network assumes its nodes are already connected. This one is the
connection.

## 5. Adjacent field: constrained-budget model compression

Added 2026-07-29 after checking the field directly rather than citing it.

The OpenAI Parameter Golf challenge asks for the best language model inside a
16 MB artefact trained in under ten minutes on eight accelerators, scored by
tokenizer-agnostic bits per byte on a fixed validation set. Lower is better. It is
the closest public benchmark to the low-precision compression thesis argued here.

| Entry | Score, bits per byte | Note |
|---|---|---|
| Best entry on the live leaderboard | 1.0565 | the bar the field currently clears |
| Best ternary entry, third-party | 1.1565 | 74M ternary model, published record directory |
| Same author, binary, unconstrained | 1.1239 | outside the compute limit, listed as non-record |
| Stated baseline | 1.2244 | reference point published with the challenge |

Two things follow, and both matter more than the table.

A third party has already published a ternary entry in this challenge. The
ternary-under-a-parameter-budget position is occupied, by someone else, with a
public artefact and a reproducible record directory. Any claim to novelty in that
specific framing should be checked against that entry first.

The gap between the ternary entry and the leaderboard leader is about 0.1 bits
per byte. That is the honest size of the penalty currently paid for ternary
weights in this setting - not a fatal gap, and not a free lunch either. It is a
better number to quote than any internal estimate, because a reviewer can check
it in one click.

This section asserts no figure for this project. Nothing here was produced by it.

## 6. What to claim, and what not to

Claim:
- six devices assembled, with cryptography and radio verified on-device
- an attestation route that does not require a vendor enclave
- an economic assurance model with published parameters
- an allocation structure with no founder, investor or treasury share
- an honest energy figure with its interval, shown beside the naive calculation

Do not claim:
- superiority in throughput per watt
- proof, in the cryptographic sense, that work ran on specific hardware
- an operating mesh, until the three-node gate has been run
- any comparison against a full inference system, until one exists
