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
| Reference edge accelerator v1 | mid-range edge board | 9.51 tok/s [PUB] | under 7 W | 1.36 | arXiv:2504.16266 |
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

## 5. What to claim, and what not to

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
