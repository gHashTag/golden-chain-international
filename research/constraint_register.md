# Constraint Register

Status: written 2026-07-30. Eleven constraints have been checked across this analysis and
they have never appeared in one list. That absence caused three reversals: a code chosen on
area that failed the error target, a replacement that failed the leakage bound, and a
priority ordering that came from sweeping one input while holding another.

The point of the list is the last column. A constraint that is checked and slack is closed;
a constraint nobody has written down is where the next reversal comes from.

---

## Checked

| # | Constraint | Where it comes from | Status |
|---|---|---|---|
| 1 | Helper-data leakage, at most n-k bits | Gao et al., the field's design rule | **binding** - eliminated the concatenated construction outright and sets the entropy floor |
| 2 | Word failure rate at or below one in a million | the application's own requirement | **binding, and the alternative was measured and lost** - reliable-bit selection does reach fifteen percent raw by indexing the reliable third, and the mechanism reproduces under this project's source model, but paired with repetition it needs 1,211 to 1,765 response bits at six percent raw against 635 under SLLC, and it needs thirty-one enrolment reads per position where SLLC needs one. See W-INTL-118 and W-INTL-119, which retract the operative half of W-INTL-115 |
| 3 | Sixteen tiles, 288,512 square micrometres | Tiny Tapeout specification | **binding, and was computed wrong** - cell area was divided by die area with no utilisation factor until W-INTL-99. At the measured 58 percent the design fits to six percent bit error rate and not above |
| 4 | Min-entropy per response bit | Wilde, Hiller and Pehl, measured on FPGAs | slack under zero leakage - halving it moves the budget by three hundredths of a tile, because a lower density needs more blocks and blocks cost no area. It was the tightest input in the work under the syndrome construction; see W-INTL-114 |
| 5 | Response bias, and whether debiasing is needed | Maes et al. and Gao et al. | slack under SLLC - it still sets the raw width, but every arrangement fits either way once the leakage term is gone. It was binding conditionally under the leakage bound; see W-INTL-112 |
| 6 | Oscillator entropy floor, log2(R!) above leakage plus 128 | derived here | **binding** - sets 360 to 380 oscillators, and was wrong once (W-INTL-77) |
| 7 | One enrolment per device | Maes et al., verified here on this construction | **binding as policy** - written into the registry contract |
| 8 | Supply current, 20 mA for a 0.1 volt drop | Tiny Tapeout specification | slack - 384 to 471 MHz against a clock of tens of MHz |
| 9 | Logic depth and achievable clock | measured here | slack - 168 to 350 MHz mapped, solver owns the path |
| 12 | Synchroniser metastability | derived here | slack - 10^120 years at 10 MHz, collapsing to 10 years at 100 |
| 10 | Interconnect capacitance | estimated here | slack - a 1.4 to 1.6 times correction to power, which does not bind |
| 11 | Oscillator length, seven against ten to twenty inverters | Mansouri and Dubrova | slack - nineteen percent of area, no fit verdict changes |

Six binding, one binding as policy, four slack - and one of the binding rows had its arithmetic wrong when this register was written, which is recorded as W-INTL-99. A status column does not check a computation. All five remaining arithmetic rows were re-derived from their definitions in W-INTL-104 and reproduce; the area row now has scripts/check_figures_reproduce.py behind it, which recomputes the headline from inputs and runs in CI.

## Not checked

These are named because naming them is the whole value of the register. Each is a
constraint someone could reasonably expect to have been considered, and none has been.

| Constraint | Why it might matter | Named in |
|---|---|---|
| **Helper-data manipulation by an active adversary** | closed as a question, open as an omission. There is a generic countermeasure - hash the helper data and fold it into the key, K = S xor f(W) - which is code-independent and absent from every design here (W-INTL-116). Measured in W-INTL-120: one flipped helper bit changes 64.3 of 128 key bits, the ideal half, at the cost of one hash. Still not in the design. Formerly: corroborated, not verified. The line is code-offset against syndrome: BCH in a code-offset scheme is affected, BCH with syndrome helper data is the case proven immune, and this project is syndrome-based. Two secondary sources agree and the primary is unread - W-INTL-105. Formerly: Gao et al. assert BCH with syndrome decoding is secure under these attacks, citing Becker; Becker's text returns 403 and its abstract names no code, so the claim is second-hand. The abstract does establish that no construction meeting practical error requirements has a robustness proof - see W-INTL-101 | Gao et al.; Becker |
| **Aging of the oscillators** | the literature reports ring-oscillator PUFs as resilient to temperature but *less* resilient to aging. Every error-rate figure here is a fresh-device figure | Mansouri and Dubrova, and the configurable-RO literature |

| **Process corners** | every area and delay figure is at the typical corner. Timing has an order of magnitude of margin so the slow corner is unlikely to matter, but that is an argument rather than a check | standard practice |
| **Placement and routing at 84 percent utilisation** | the expensive cells fill 13 to 15 of sixteen tiles. Whether that routes is a question no synthesis run answers | standard practice |
| **The 128-bit target itself** | inherited from the sources and never questioned against what the registry actually needs | nothing |

## How to read this

The four slack constraints were each found by asking what had not been written down, and each
took roughly one calculation. Three for three they turned out slack, which is not evidence
that the next one will be - it is evidence that the cost of checking is low.

The unchecked list is ordered roughly by how much a bad answer would cost. Helper-data
manipulation is first because it is a security property, it is named as load-bearing by a
source this project relies on, and the reasoning was inherited rather than reproduced - the
same pattern as the reuse claim in W-INTL-83, which was checked and survived.


---

## Revision, 2026-07-30

The register was written to make unchecked constraints visible and became the most out-of-date
document here: it has been deferred for three loops while the leakage term was removed, reliable-bit
selection was added, the manipulation countermeasure was measured, the solver was rewritten and the
code was re-chosen. Brought up to date, and one lesson recorded about why it went stale.

**What binds now.** Two things. The min-entropy requirement, `k_total >= 128/rho = 136`, which the
recommended construction meets at 171. And the word failure rate, which sets the correction strength
- but only against the *effective* error rate after selection, not the raw one.

**What no longer binds, and why.**

| Row | Was | Now |
|---|---|---|
| helper-data leakage, n-k | binding, eliminated a construction | removed entirely by SLLC; the term is a property of the syndrome construction, not the problem |
| min-entropy per response bit | the tightest input in the work | slack; halving it moves the budget by three hundredths of a tile once the leakage term is gone |
| response bias and debiasing | binding conditionally, decided the oscillator arrangement | slack; every arrangement fits without the leakage term |
| raw bit error rate | binding, cliff at eight to nine percent | slack up to fifteen percent with reliable-bit selection, which converts it into a requirement for raw positions |
| tile area | binding and computed wrong | binding, and now with a check that recomputes it from inputs |

**What is new since the register was written.** Nine enrolment reads per position, at the operating
temperature, without which selection is counterproductive rather than merely weaker. And the
manipulation countermeasure, which is a component rather than a constraint but is load-bearing and was
absent from every design for four loops.

**Why it went stale, which is the part worth keeping.** The register lists constraints and their
status. It does not list *what each decision was made under*. The code was chosen against a six
percent raw error rate; selection then made the effective rate 0.0127 and the code was not revisited
for two loops. The solver's multiplier count was chosen for a communications decoder; the
observation that latency is free here sat in this register marked slack and was not connected to it.

Both losses were the same shape: a decision correct at the operating point where it was made, and an
operating point that moved. A register of constraints does not catch that. What would is a column
recording, for each constraint, which decisions were taken against it - so that when a constraint
moves, the decisions to revisit are named rather than remembered.

Recorded as the change not made, because it is a change to how this file is kept rather than to what
it says, and the next loop is a better place to make it than the one that noticed.

---

## Decisions against constraints, 2026-07-31

The change the previous revision recorded as not made. For each constraint, the decisions that were
taken against it - so that when the constraint moves, what to revisit is named rather than
remembered. The last column is the test: if the constraint changed today, would that decision have
to change with it.

| Constraint | Decisions taken against it | Moves with it |
|---|---|---|
| word failure at 1e-6 | correction strength t; number of blocks; the whole code choice | yes, and it did - the code was chosen against the raw rate and re-chosen two loops after selection changed it |
| min-entropy density | number of blocks; k required; the oscillator floor; whether debiasing is needed | yes - and this loop it moved again, because the density that applies is the one *after* selection, which is 0.9293 rather than 0.9414 |
| helper-data leakage | the construction itself: syndrome over code-offset, then SLLC over syndrome | no longer applies; SLLC removed the term |
| sixteen tiles | every area trade: the solver's multiplier sharing, the Chien search left parallel, the field | yes - and the two largest area wins came from revisiting decisions after this constraint stopped binding |
| raw bit error rate | the selection fraction; the number of enrolment reads; the code | yes - selection converted this constraint into a requirement for raw positions, and every decision above it moved |
| oscillator entropy floor | oscillator count; the pairing arrangement; whether reuse across pairs is allowed | yes, and it was wrong once: the floor was written against raw entropy rather than residual |
| one enrolment per device | the enrolment protocol; the nine-read ranking; the registry contract | policy, not physics - if the contract changes, the ranking quality and the effective error rate change with it |
| throughput and clock | the solver's multiplier count; the serial-vs-parallel choice in every stage | yes - this row was marked slack for eighteen loops before anything was decided differently because of it |

Two entries in that table were written by finding the decision after the constraint had already
moved. The point of keeping the column is that the third one should be found the other way round.
