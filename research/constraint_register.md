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
| 2 | Word failure rate at or below one in a million | the application's own requirement | **binding** - cliff at eight to nine percent bit error rate |
| 3 | Sixteen tiles, 288,512 square micrometres | Tiny Tapeout specification | **binding** - excludes the whole n=511 family; the expensive cells reach 84 percent |
| 4 | Min-entropy per response bit | Wilde, Hiller and Pehl, measured on FPGAs | **binding** - cliff at 0.7986, and the tightest input in the work |
| 5 | Response bias, and whether debiasing is needed | Maes et al. and Gao et al. | **binding conditionally** - decides whether oscillator reuse is a requirement |
| 6 | Oscillator entropy floor, log2(R!) above leakage plus 128 | derived here | **binding** - sets 360 to 380 oscillators, and was wrong once (W-INTL-77) |
| 7 | One enrolment per device | Maes et al., verified here on this construction | **binding as policy** - written into the registry contract |
| 8 | Supply current, 20 mA for a 0.1 volt drop | Tiny Tapeout specification | slack - 384 to 471 MHz against a clock of tens of MHz |
| 9 | Logic depth and achievable clock | measured here | slack - 168 to 350 MHz mapped |
| 10 | Interconnect capacitance | estimated here | slack - a 1.4 to 1.6 times correction to power, which does not bind |
| 11 | Oscillator length, seven against ten to twenty inverters | Mansouri and Dubrova | slack - nineteen percent of area, no fit verdict changes |

Six binding, one binding as policy, four slack.

## Not checked

These are named because naming them is the whole value of the register. Each is a
constraint someone could reasonably expect to have been considered, and none has been.

| Constraint | Why it might matter | Named in |
|---|---|---|
| **Helper-data manipulation by an active adversary** | Gao et al. state plainly that not all codes and decoding strategies guarantee security of the derived key, and that resistance to helper-data manipulation must be evaluated alongside overhead. This project uses syndrome-based helper data, which they chose partly for that reason - but the argument was never checked here, only inherited | Gao et al.; Becker, on robust fuzzy extractors |
| **Aging of the oscillators** | the literature reports ring-oscillator PUFs as resilient to temperature but *less* resilient to aging. Every error-rate figure here is a fresh-device figure | Mansouri and Dubrova, and the configurable-RO literature |
| **Synchroniser metastability in the characteriser** | the characterisation structure samples free-running oscillators through two flip-flops. Two stages is conventional and the mean time between failures has not been computed for this process and clock | nothing - this is an omission of my own |
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
