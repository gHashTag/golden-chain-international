# Submission Checklist

Status: current as of 2026-07-29. Supersedes any earlier schedule built on a
2 August deadline.

Every line below is either backed by an artefact that a reviewer can open, or
marked as design, or marked as needing a fact only the applicant holds. Nothing
is listed as ready on the strength of a document asserting it.

---

## 1. The deadline, and what it changes

Cohort 20 closes **21 August 2026**. The programme starts February 2027. Verified
on 2026-07-29 against the Access Programme and Hub71+ Digital Assets pages, which
both state that date. An earlier draft of this repository said 2 August; that was
wrong and cost the plan nineteen days of assumed runway.

Applications arriving after a deadline are rolled into the next cohort rather than
discarded, so the date is a scheduling constraint and not a cliff.

Hub71+ AI is not a track. It is an ecosystem entered by answering an AI question
inside a chosen programme's form. The programme still has to be chosen. See
section 5.

## 2. Ready, with an artefact a reviewer can open

| Item | Artefact | Level |
|---|---|---|
| Authenticated encryption on the node CPU | two on-device runs, 2026-07-01 and 2026-07-04, RC=0, distinct binary hashes | hardware, reproduced |
| 5.8 GHz radio front end | LO, FFT peak and SNR recorded; marked loopback-only at source | hardware, loopback only |
| Three mesh nodes physically connected | assembled and powered | hardware, weak evidence type, see section 4 |
| Three compute boards | inventory | hardware |
| Multiplier-free ternary tile | testbench runs 206 of 206 passing; synthesis emits no DSP primitive | test, reproduced by execution here |
| Numeric catalog | 83 records in 13 clusters, counted directly from the single source of truth | external, published |
| Two preprints | arXiv:2606.05017 and arXiv:2606.09686, the latter at v2 | external, published |
| Token deployed | Sepolia, chain id 11155111, address recorded | confirmed, third-party verifiable |
| Research conduct | five public challenge submissions, three withdrawn by the author on stated technical grounds | external, third-party visible |
| Rust crate carries forbid(unsafe_code) | enforced, and confirmed to have no unsafe block | test |

## 3. Design, and must be described as design

| Item | Why it is not ready |
|---|---|
| Four-proof settlement contract | no source exists; the only contract is the token |
| Nine halvings over forty years | implemented in the chain sources, not in the deployed contract |
| Seven checks | no settlement contract to hold them |
| Multi-hop routing, two-hop throughput, shared uplink | simulation only; hardware for the demonstration is assembled |
| Self-healing convergence | metric undefined; define before claiming |
| Over-the-air operation | nothing has been transmitted; amplifier and licence outstanding |
| End-to-end language model inference | not built; no attention, cache, normalisation or quantisation units |
| Custom die | open item; the Tiny Tapeout shuttle tile is a different thing and must be named differently |

## 4. Removed or corrected during verification, do not reinstate

- **Top-5 placement at 0.9650 bits per byte.** No such score exists in the
  submission history. Replaced by the withdrawal record, which is stronger.
- **309 MHz inference core.** No timing report exists; place and route was not
  run. 309 is a swept parameter in a projection.
- **No premine, no venture allocation, no treasury.** Refuted by the contract:
  founder 20 percent, treasury 10 percent, both vested. Replaced by the honest
  allocation plus the comparison in the competitor matrix.
- **110 test blocks.** The repository's own reproduction command yields 118.
- **4,463 lines of Rust.** Matches nothing visible; the public repository has
  6,181 under src.
- **Energy multiplier 4x to 8x, CI [3, 10].** The figure may be sound but the
  calculation was not found. Either produce the working or drop the number. This
  is the last quoted figure in the application without a locatable derivation.
- **Three connected boards.** Evidence is an operator confirmation, which is the
  weakest type in an otherwise artefact-backed table. A dated photograph with the
  boards and a serial visible would close it in five minutes.

## 5. Needed from the applicant, and only from the applicant

None of these can be produced by reading the repositories.

1. **Host programme.** Access Programme leads with hardware and verifiable
   compute. Hub71+ Digital Assets leads with the settlement layer - and would put
   the allocation table in front of people who read allocation tables for a
   living, which is now defensible but should be a deliberate choice.
2. **Relocation month.** One word, currently a placeholder in the answers file.
3. **Team section.** Not written. Single founder is a scored weakness; see the
   audit entry on it.
4. **Funding ask.** No amount stated anywhere.
5. **Named hiring plan.** The audit requires named roles, not "two engineers".

## 6. Highest-value work still available before the deadline

**Run the three-node demonstration.** The hardware is assembled and the gate has
not been run. It moves the application from assembled and verified component by
component to the network works, and it is the only remaining item that changes the
category of the submission rather than its wording.

**Produce the energy calculation**, or remove the figure. It is one afternoon
either way and it closes the last unsourced number.

**Photograph the three boards.** Five minutes, and it upgrades the weakest
evidence row in the ledger.

## 7. What has been done to the repository

Nine commits on the Wave-intl-2 branch. The hard-rules gate now passes, having
never passed before: the banned-vocabulary step was matching the statement of the
rule it enforces in README.md, and is now exempted by an explicit line sentinel
rather than by dropping README from the scan. A negative control confirms the gate
still catches a planted violation.

The evidence ledger's summary is derived by parsing its own table rather than
written by hand, after it was found to claim 29 rows against 30 present.
