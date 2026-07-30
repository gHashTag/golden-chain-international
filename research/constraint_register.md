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
