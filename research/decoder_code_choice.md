# The Decoder Was Sized Correctly and Chosen Wrongly

Status: written 2026-07-30. Started as one measurement and ended as a different
answer.

The tile budget had one estimated input left: the key-equation solver, the third
stage of the BCH decoder, which `bch_area_probe.v` deliberately left out rather
than write unverified and report as measured. This closes that. It also reports
what closing it turned up, which is larger than the number itself.

Everything below is synthesis against the same SkyWater library at the typical
corner as the earlier stages, and every circuit measured has first decoded
correctly in a testbench that is shown to be capable of failing.

---

## 1. The solver, measured

Written as the inversionless Berlekamp-Massey iteration: inversionless because a
GF(2^8) inverter is expensive and the standard reformulation removes it by carrying
the discrepancy of the last length-changing step as a scale factor instead.

Verified before measured. The testbench builds an error pattern, computes the
syndromes it produces, runs the solver, and compares the result against the error
locator polynomial constructed directly as a product of linear factors, projectively
because the inversionless form returns a scalar multiple rather than the monic
polynomial. Every correctable weight from one error to t, three patterns each, plus
the zero-error case: 55 patterns at t=18, all passing.

Then shown able to fail, because a check that cannot fail is not a check. Two
independent injected faults - the length-update condition weakened from `2L <= r` to
`2L < r`, and the carried scale factor dropped - each failed 51 of the 55 patterns.

| t | Solver alone |
|---|---|
| 4 | 17,503 |
| 8 | 31,620 |
| 12 | 45,878 |
| 18 | 66,847 |

Square micrometres. Linear at about 3,525 per unit of t.

Two silent faults were found while writing it, and both are the kind that produce a
plausible answer rather than an obvious failure. Doubling the register length by
shifting rather than by concatenation truncates 36 to 4 at t=18, because a shift is
self-determined at the width of its left operand; the algorithm then lengthens on the
wrong steps and returns a polynomial of the wrong degree that still looks like a
polynomial. And selecting the zeroth coefficient of x times B with a ternary still
elaborates an out-of-bounds read as the untaken operand, which simulation reports
and synthesis is free to treat differently - a circuit measured that is not the
circuit the testbench passed.

## 2. What that does to the previous estimate

The solver had been budgeted as comparable to the two stages already measured, which
at t=18 meant 22,668. It measures 66,847, so that estimate was low by a factor of
2.95, and the whole-decoder estimate was low by 1.97.

The reason is structural rather than accidental, and it is worth stating because it
predicts the same error elsewhere. Syndrome accumulation and the Chien search
multiply by compile-time constants, which fold into XOR trees. Berlekamp-Massey
multiplies two runtime values, and it needs about 3(t+1) such multipliers. Estimating
the third stage from the first two assumed the arithmetic was the same kind of
arithmetic. It is not, and the ratio between a general GF(2^8) multiplier and a
constant one is roughly the ratio the estimate missed by.

The literature agrees on the count. Sarwate and Shanbhag's reformulated inversionless
architecture is a systolic array of 3t+1 cells, and the conventional form's critical
path is described as two multipliers and 1+log2(t+1) adders - which is exactly the
path in the circuit measured here, since the discrepancy is an inner product computed
in one cycle. So the design measured is the conventional one, its multiplier count is
the standard one, and a systolic reformulation would shorten the path at about the
same area.

Full decoder, all three stages measured:

| t | Syndrome + Chien | Solver | Decoder | Tiles |
|---|---|---|---|---|
| 4 | 5,694 | 17,503 | 23,197 | 1.3 |
| 8 | 10,475 | 31,620 | 42,095 | 2.3 |
| 12 | 15,350 | 45,878 | 61,228 | 3.4 |
| 18 | 22,668 | 66,847 | 89,515 | 5.0 |

## 3. An arithmetic error in the table this replaces

Found while recomputing. The previous budget's decoder-share column does not follow
from the two columns beside it. Its rows read 36, 51, 61 and 69 percent; the same
table's own decoder and total figures give 21, 30, 35 and 40. All four are high by a
consistent factor of about 1.72, which says the column was computed against some
other denominator, and that denominator cannot be reconstructed from the document.

The decoder and total columns are internally consistent - the decoder column is
exactly twice the measured two stages, which is what the stated assumption says it
should be, and total minus decoder gives a smoothly growing series. So the share
column is the error, and it is corrected below rather than carried forward.

## 4. The finding that matters more

The budget had been sizing BCH(255,131) at t=18, on the stated grounds that this is
the order published designs use for PUF key generation. That premise is wrong, and
the source that shows it is wrong is the standard reference on this exact problem.

Bosch, Guajardo, Sadeghi, Shokrollahi and Tuyls, "Efficient Helper Data Key Extractor
on FPGAs", CHES 2008, set out to build a fuzzy extractor as small as possible, with
the stated reason that the area belongs to the application rather than to the key
generator - the same constraint this project has. They consider BCH and discard it
before implementing it, writing that BCH decoder algorithms are very complex and so
expected to be expensive in area. Their construction instead concatenates a short
odd repetition code with a first-order Reed-Muller code, and their measured
conclusion on a Spartan-3E is that Reed-Muller is superior to the alternatives in
area and, by their own error tables, in correction performance too. The whole fuzzy
extractor, including hashing and a doubling allowance for control logic, comes to
under a tenth of a low-end part.

They also state plainly that they could find no BCH implementation to compare
against, and expected its complexity to be higher. This project now has that
comparison, on a real library, in both directions.

## 5. Measured, the same library, the same rules

R(1,6) decoded by majority logic, serialised to one check per cycle: for a
first-order Reed-Muller code the checks for message bit i are exactly the pairs of
positions differing only in bit i, which makes each check one XOR of two bits and the
whole decoder a counter, a tally and two multiplexers. 448 cycles for a full decode.
Key generation runs once at power-up, so cycles are the cheap resource and area is
the dear one, and a serial architecture spends the cheap one.

Verified first, on every error weight the code can correct - zero through fifteen,
four messages each - then shown able to fail on two injected faults: the majority
threshold moved, and the paired position shifted by one bit. 20 and 64 failures
respectively.

| Circuit | Area | Flip-flops | Tiles |
|---|---|---|---|
| R(1,6) + repetition, decoders | 4,596 | 101 | 0.25 |
| R(1,5) + repetition, decoders | 2,883 | 65 | 0.16 |
| BCH decoder, t=4 | 23,197 | - | 1.3 |
| BCH decoder, t=18 | 89,515 | - | 5.0 |

A factor of 19.5 between the code the budget assumed and the code the literature
recommends. Even against BCH at t=4, which does not reach the error probability the
application needs, the factor is 5.

The received word is stored inside the Reed-Muller decoder rather than presented on a
port, because majority-logic decoding needs random access to it and leaving those 64
flip-flops outside would have flattered this design against the BCH stages, which
hold their own state.

One corroboration worth recording. The paper gives its decoder's flip-flop count as
2^m + 6m - 1, which is 99 at m=6. The circuit here uses about 95 for the Reed-Muller
half, reached from a different derivation - the pairs-of-positions identity rather
than their characteristic-vector generator. Two independent routes to the same
neighbourhood is the closest thing to external validation this work has produced.

## 6. What the budget becomes

Correcting only the solver, and keeping every other assumption the previous document
made:

| t | Decoder | Total | Tiles | Decoder share |
|---|---|---|---|---|
| 4 | 23,197 | 65,979 | 3.7 | 35 percent |
| 8 | 42,095 | 91,802 | 5.1 | 46 percent |
| 12 | 61,228 | 117,995 | 6.5 | 52 percent |
| 18 | 89,515 | 156,880 | 8.7 | 57 percent |

So the BCH answer moves from five to seven tiles to between four and nine, and at the
strength the previous document treated as the target it takes 8.7 of the 16 a
submission may use. It still fits. The margin is now under a factor of two, and the
whole of that margin is spent on a code choice the literature had already argued
against in 2008.

With the recommended construction the decoder stops being the constraint. At 4,596
square micrometres it is a quarter of one tile and around seven percent of the
budget, against 57 percent.

## 7. The cost that moved rather than vanished

This is the part that would be dishonest to leave out.

The paper's construction is measured at a bit error probability of 0.15 on SRAM
responses, and at that error rate it needs 4,800 source bits to yield the 171
error-free bits that hash to a 128-bit key. The budget here has been assuming 384 raw
bits, from a three-times multiplier over the key length that was never tied to a
measured error rate.

So the decoder saving is real, large and measured, and the raw-width figure it
depends on is between one and twelve times what the budget assumed. Which of those
holds is set by the oscillator error rate on this process, and that is the same
unmeasured quantity that set the correction strength in the first place. The
uncertainty did not shrink; it moved from a block whose area is now measured to a
block whose count is not.

That strengthens rather than weakens the previous document's conclusion about what to
do first. Characterising the error rate was already the first step because it sized
the largest block. It is now the first step because it sizes the only block left that
is not measured, and because the choice of code - which is the difference between a
quarter of a tile and five tiles - cannot be made without it.

## 8. What this does not license

It does not license saying the identity root is built. Nothing here is fabricated;
these are synthesis areas for circuits that decode correctly in simulation, against a
real library, and that is a different claim from silicon.

It does not license quoting the Reed-Muller figure as the project's decoder cost
without the raw-width caveat in section 7. Two of the three numbers that determine
whether a usable identity root fits on a tile are now measured. The third is a count
of oscillators, it is set by an error rate nobody has measured on this process, and it
is the one that could still make the answer no.

---

## 9. One axis, added 2026-07-30

Section 7 left the comparison in two pieces that could not be added: a measured
decoder area and an unmeasured oscillator count. `code_choice_model.py` puts both on
one axis, the axis being the bit error probability.

Calibration first, because a model of a paper's construction should reproduce the
paper's own numbers. It does, to three significant figures on all five checks: the
source-bit counts for both recommended constructions, both of their word error
probabilities, and a plain BCH row from the earlier table. If those checks fail the
script stops rather than printing.

## 10. The pair count is not an entropy count, and the literature says why

The budget document proposed sharing one comparison chain across a bank of
oscillators, on the reasoning that a bank of R offers R(R-1)/2 distinct pairs, "far
more than any key needs". That reasoning is wrong, and Mansouri and Dubrova state
the reason plainly in arXiv:1207.4017: for a traditional RO-PUF not all challenges
are valid, because if A is faster than B and B is faster than C then A is necessarily
faster than C, so the third response is predictable from the other two.

Frequency comparison is a total order. R oscillators realise one of R! rankings, so
the information available is log2(R!) bits however many pairs are read out. R(R-1)/2
counts challenges a verifier may pose; it does not count bits an adversary cannot
guess, and it exceeds the real figure by a growing margin - at R=614 the pair count is
188,191 against 4,807 bits of ordering.

Corrected, and both readings kept side by side in the script so the size of the
overstatement stays visible. The ordering figure is still an upper bound: it assumes
every ranking equally likely, and the same literature reports that pairs too close in
frequency must be discarded for reliability, costing about a fifth of them in a
temperature-aware design.

## 11. What the axis shows

Oscillator counts from log2(R!), decoder areas measured, one in a million as the
target word error probability:

| Construction | Works up to | Raw bits | Oscillators | Tiles |
|---|---|---|---|---|
| BCH(255,131) t=18 | 1.88 percent | 510 | 98 | 5.11 |
| rep[3] + RM[64,7,32] | 13.22 percent | 4,800 | 614 | 1.15 |
| rep[5] + RM[32,6,16] | 12.53 percent | 4,640 | 596 | 1.03 |

Three things follow, and the first is a correction of section 5.

**The factor of 19.5 was decoders only.** Across the whole design it is 4.4. The
smaller decoder buys its saving by consuming six times as many oscillators, and half
the advantage goes back. The conclusion survives - the recommended construction is
still smaller, and by a factor worth having - but 19.5 was the wrong number to lead
with and this document led with it.

**BCH(255,131) at t=18 does not reach the target at any plausible error rate.** It
needs the bit error probability below 1.88 percent. That is not a statement about
area, and it means every loop that sized this code was sizing a code that does not do
the job. The choice was not expensive; it was ineffective, and the area analysis
obscured that by never asking whether the code met its own requirement.

**It fits, with room, and that is now robust.** The recommended construction takes
about one tile of the sixteen a submission may use, and holds to a bit error
probability of 13 percent - above the range ring-oscillator work reports. The
question W-INTL-46 raised, whether identity in silicon needs a funded die, is answered
no on every input that has been measured.

## 12. What the error rate is likely to be, and why that is still not enough

One concrete figure from the same paper: changing the supply voltage by ten percent
from typical flips 0.48 percent of the output bits, from SPICE on UMC 90 nm with
nominally matched pairs. Their inter-chip uniqueness is 51.35 percent against an
ideal of 50.

If 0.48 percent were the whole story both codes would work and BCH would fit inside
its 1.88 percent margin. It is not the whole story. That figure is voltage only, and
temperature is the larger effect - the same literature describes pairs whose ordering
reverses as the die warms, and handles it by pre-computing which pairs are reliable
across the range and discarding the rest. Nothing in it is a measurement on this
process, at this inverter count, across temperature.

So the axis is built and the point on it is not known. What has changed is that the
measurement now has a decision attached: below about two percent either code works
and the choice is made on area; above it, only the concatenated construction works at
all. That is a cheaper question to answer than the one this analysis started with,
and it is the same characterisation structure that was already the recommended first
step.

---

## 13. The constraint this analysis did not have, added 2026-07-30

Publishing helper data costs min-entropy, and none of the twelve sections above
counted that cost.

For a secure sketch over an (n,k) linear code the loss is bounded by n-k. Gao, Su,
Yang, Chen, Nepal and Ranasinghe (arXiv:1902.03031) call this the well-known
min-entropy loss and use it as the design rule directly: prefer a small n and a small
t, because a small t implies a large k, and a large k means fewer blocks are needed to
reach a k-bit secret.

That rule points the opposite way from everything sections 4 through 12 concluded. Area
favoured the low-rate concatenated construction; leakage forbids it.

Residual min-entropy per block is `rho*n - (n-k)`, with rho the min-entropy per response
bit. At the measured rho of 0.9414:

| Construction | n | k | Leak | Residual |
|---|---|---|---|---|
| rep[3] + RM[64,7,32] | 4,800 | 175 | 4,625 | **-106** |
| rep[5] + RM[32,6,16] | 4,640 | 174 | 4,466 | **-98** |
| BCH(255,131) t=18, x2 | 510 | 262 | 248 | 232 |
| BCH(255,171) t=11 | 255 | 171 | 84 | 156 |
| BCH(127,15,27) | 127 | 15 | 112 | 7.6 |
| BCH(63,16,11) | 63 | 16 | 47 | 12.3 |

The construction recommended in sections 4 through 12 of this document has negative
residual entropy. It is not expensive or marginal; on the standard bound it delivers no
secret at all. That recommendation is withdrawn.

Two things must travel with that. The n-k figure is an upper bound on leakage, so a
tighter analysis for a specific code and source could recover some of it - but n-k is
the bound the literature designs against, and a construction that needs a better bound
than the field uses is not one to build on. And the same arithmetic applied to the CHES
2008 source-bit column gives a negative residual at that paper's own assumed entropy
density, which suggests its column answers a different question - how many bits the code
delivers, not how much secrecy survives publication.

## 14. The code that satisfies all three constraints

Leakage wants a high rate. Error tolerance wants a low one. Area wants both small. Only
one of the codes named in the sources clears all three, and it is the one Gao et al.
chose for the same reasons.

BCH(127,15,27) over GF(2^7), primitive polynomial x^7+x^3+1. Measured on the same
library, the solver verified in the new field before its area was quoted - the GF(2^8)
case re-run as a regression and still passing, 82 patterns at t=27 in the new field
passing, and an injected fault failing 77 of them.

| Stage | Area |
|---|---|
| Syndrome bank + Chien search | 27,590 |
| Key-equation solver | 73,119 |
| Decoder total | **100,709** |

Nineteen blocks for a 128-bit key, 2,413 raw response bits.

| Component | Reuse | Disjoint |
|---|---|---|
| Decoder | 100,709 | 100,709 |
| Oscillators | 272 | 4,826 |
| Total tiles of 16 | **5.98** | **12.62** |

It fits in both readings of the oscillator arrangement, and it tolerates a bit error
probability up to 7.06 percent - four times what BCH(255,131) at t=18 allowed.

## 15. What the three loops on this question actually established

Worth stating plainly, because the direction reversed twice.

The decoder area figures are all correct and all were measured. What changed each time
was which constraint was being applied. Loop one had area only, and picked the smallest
decoder. Loop two added the error target, and found the original code inadmissible.
Loop three added the leakage bound, and found the replacement inadmissible too.

Each measurement survived; each recommendation did not. The pattern is worth naming: a
measurement is about the artefact, a recommendation is about the constraint set, and the
constraint set was incomplete three times running. Nothing about measuring more carefully
would have caught it. Reading the design rule the field uses would have, and that is what
finally did.

The answer now rests on three constraints from three sources, one measured entropy
density, and four synthesis runs. It could still be missing a fourth constraint.

---

## 16. Decoding through the stages, added 2026-07-30

Sections 1 through 15 quoted an area for a syndrome bank and a Chien search that had
never decoded anything. They were called structural area probes, which was honest about
their status, and the status turned out to matter.

Wired to the solver and driven end to end, the Chien stage was wrong. It summed t of the
t+1 coefficients of the error locator, leaving out the constant term, so its zero test
was not the polynomial's zero test. Stage-wise synthesis cannot find that: the circuit is
the right size and shape and its cells are correctly counted. Only decoding through it
does.

The test needs no encoder. BCH is linear, so a received word equal to the error pattern
alone is the all-zero codeword received with errors, and the all-zero word is a codeword.
Errors go in at known positions, the hardware locates them, and the assertion is that the
located set equals the injected set exactly, with the locator degree equal to the error
count.

Every weight from one error to t, two patterns each, in both fields. 54 decodes at t=27
and 36 at t=18, all passing. Two injected faults: the historical defect, which fails all
54; and one corrupted Chien constant, which fails 8.

Corrected areas, and both are higher than the figures they replace:

| Stages | Was | Now | Change |
|---|---|---|---|
| Syndrome + Chien, GF(2^7), t=27 | 27,590 | 29,148 | +5.6 percent |
| Syndrome + Chien, GF(2^8), t=18 | 22,668 | 23,407 | +3.3 percent |

The GF(2^8) figure had stood for five loops. The BCH(127,15,27) decoder is therefore
102,267 square micrometres rather than 100,709, and 5.67 tiles rather than 5.58.

The lesson is about the shape of the check rather than its result. Three stages were each
measured correctly and one of them did not work, and no amount of care applied to a stage
in isolation would have shown it. What showed it was the smallest end-to-end path that
produces a checkable answer.

## 17. The debiasing stage, and the first thing in this analysis that does not fit

W-INTL-65 named a candidate fourth constraint: if the response bias falls outside the
range where adding raw bits compensates, a debiasing stage must come first, and it is in
no budget here.

Maes, van der Leest, van der Sluis and Willems put a number on it. Classic von Neumann
debiasing costs an overhead factor of about 4.4 at 50 percent bias and about 5.3 at 30
percent. They also record that a PUF's usual reusability across enrolments does not
necessarily survive a debiasing step - which bears directly on a registry that may need
to re-enrol a die.

Applied to BCH(127,15,27), which needs 2,413 response bits:

| | No debiasing | With von Neumann |
|---|---|---|
| Raw response bits | 2,413 | 10,617 |
| Oscillators reused across pairs | 6.07 tiles | 6.07 tiles |
| Two oscillators per response bit | 12.71 tiles | **36.63 tiles** |

That last cell is the first configuration in this entire analysis that does not fit the
sixteen tiles a submission may use.

So the oscillator arrangement is no longer a factor-of-two question about area. It is the
difference between fitting and not fitting, and it becomes that only once debiasing is in
the picture. Two unmeasured properties now decide the outcome together: how biased the
responses are, and whether reusing oscillators across pairs degrades extraction.

Three of the four combinations fit. The one that does not is the one where both unmeasured
properties turn out unfavourable, and nothing currently rules that out.

---

## 18. The debiasing figure was the worst case, and the conclusion survives anyway

Section 17 used a factor of 4.4 for von Neumann debiasing. That is classic von Neumann,
which is the least efficient method the source describes. Maes, van der Leest, van der
Sluis and Willems give three more, and their Table 2 lists the debiasing overhead for
each at four bias levels.

| Method | Reusable | Overhead at bias 40 / 35 / 30 / 25 percent |
|---|---|---|
| Classic von Neumann | no | 4.4 / 4.4 / 5.3 / 5.3 |
| Pair-output, 2O-VN | no | 2.31 / 2.45 / 2.66 / 2.99 |
| Multi-pass tuple-output, 2P-TO-VN | no | 1.58 / 1.73 / 1.96 / 2.32 |
| Pair-output with erasures, e-2O-VN | **yes** | 1.00, paid instead as a stronger inner code |

So the honest range is 1.58 to 5.3, not 4.4, and quoting the worst method as the cost
overstated it by up to a factor of three.

The conclusion does not move. Applied to BCH(127,15,27) and its 2,413 response bits,
with two oscillators per response bit:

| Method, best case | Raw bits | Tiles |
|---|---|---|
| 2P-TO-VN at 40 percent bias | 3,813 | 16.79 |
| 2O-VN at 40 percent bias | 5,574 | 21.92 |
| Classic von Neumann | 10,617 | 36.63 |

Sixteen tiles is the limit. The most efficient method in the literature, at the mildest
bias in its table, still does not fit - and that method is not reusable.

Every one of them fits at 6.07 tiles when oscillators are reused across pairs, because
there the binding constraint is the entropy floor rather than the position count, and
the entropy floor does not move with debiasing overhead.

**So oscillator reuse is a requirement rather than an optimisation**, conditional on
debiasing being needed at all. That is a sharper statement than section 17's, and it
holds across the whole method table rather than resting on one figure.

## 19. Reusability is a protocol constraint, not only a silicon one

Three of the four methods are marked not reusable, and the paper is precise about what
that means: enrolling the same device a second time leaks more than one enrolment does,
because the debiasing step is stochastic and bit errors between enrolments shift which
pairs are retained.

This project's registry has a slashing path and no stated position on re-registration. If
a die can ever be enrolled twice - after a slash, after a key rotation, after a failed
provisioning run - then the three efficient methods are unavailable and only e-2O-VN
remains. Its debiasing overhead is 1.00 because it discards nothing, replacing unretained
pairs with erasures; the cost reappears as a longer inner repetition code, which for the
paper's design runs from 20 to 28 bits as bias worsens.

That cost has not been derived for a BCH-only design, and it should not be guessed. What
can be said now is that the choice between one enrolment per device and many is a
silicon-area decision as well as a protocol one, and nothing in the registry currently
records which it is.

## 20. The instrument, built and measured

Everything still open turns on three quantities of this process: the bit error rate
across temperature, the min-entropy per oscillator, and the bias. All three come from one
structure, and it is built.

It emits **one frequency count per oscillator per sweep** and nothing else. No comparator,
no arbiter, no response bits. A structure that emitted response bits could only report the
error rate of the pairing wired into it, and pairing is precisely what is in question - so
the pairing, the threshold for discarding close pairs, the bias and the entropy under any
scheme are all computed afterwards from the counts, and can be recomputed when the
question changes.

Verified against arithmetic: oscillators modelled as square waves of known distinct
periods, counts asserted within three of the window divided by the period, and the
frequency ordering asserted to be preserved - that last being the property the whole
primitive rests on. Two injected faults, removing the synchroniser and failing to clear
the accumulator between oscillators, each fail 14 checks.

The first run failed eight checks and every one was in the test model rather than the
circuit: half-periods are integers, so odd periods collapsed onto their even neighbours.
An instrument's own test is an instrument.

| Component | Area | Tiles |
|---|---|---|
| Readout for a 272-oscillator bank | 5,223 | 0.29 |
| The 272 oscillators | 7,151 | 0.40 |
| **Total** | **12,374** | **0.69** |

The measurement that decides whether the identity root fits in sixteen tiles costs
0.69 of one.

It is an instrument and not a key generator, and it must never ship in a part that holds
a secret: raw frequency counts are exactly what an attacker wants and exactly what a key
generator must never expose.

---

## 21. The reusable debiasing method does not exist for this construction

Section 19 left the cost of e-2O-VN underived and said it should not be guessed. Derived
now, and the answer is not a cost.

e-2O-VN keeps every position: pairs that are not retained become erasure symbols rather
than being discarded. A pair is retained when its two bits differ, so the erasure fraction
is p^2 + (1-p)^2 - a half at 50 percent bias, more as bias worsens.

A code of designed distance d corrects e errors and f erasures when 2e + f <= d-1, and for
BCH d-1 = 2t. Per 127-bit block:

| Bias | Erasure fraction | Erasures per block | Budget needed at 5 percent error rate | Best BCH(127) budget |
|---|---|---|---|---|
<!-- derived:external --> | 50 percent | 0.500 | 63.5 | 69.8 | 62 |
<!-- derived:external --> | 40 percent | 0.520 | 66.0 | 72.1 | 62 |
<!-- derived:external --> | 30 percent | 0.580 | 73.7 | 79.0 | 62 |
<!-- derived:external --> | 25 percent | 0.625 | 79.4 | 84.1 | 62 |

The erasures alone exceed the entire correction budget of the strongest BCH(127) code that
still carries information - t=31, k=8, so 2t = 62. At every bias level. BCH cannot absorb
this on its own, which is exactly why the source's design puts a repetition code innermost:
repetition handles erasures almost free.

But an inner repetition code cannot be afforded here, and the reason is structural rather
than numerical. Residual min-entropy is `rho*n - (n-k)`, so reaching a 128-bit key requires

    k >= 128 + n(1 - rho)

Since rho <= 1 for any source, k >= 128 always - a construction cannot yield more key than
its code carries information. A repetition code multiplies n and leaves k untouched, so it
can only move that inequality the wrong way:

| Construction | n | k | Requirement |
|---|---|---|---|
| rep[1] + BCH(127,15) | 127 | 15 | rho >= 1.89, impossible |
| rep[3] + BCH(127,15) | 381 | 15 | rho >= 1.30, impossible |
| rep[20] + BCH(127,15) | 2,540 | 15 | rho >= 1.04, impossible |

Per block, and no number of blocks helps: from r=3 the per-block residual is already
negative, so adding blocks adds leakage faster than it adds information.

**So e-2O-VN is not unavailable at this entropy density. It is unavailable at any entropy
density, for this construction, because the inner repetition it requires cannot carry the
information the key needs.** The reusable option is not expensive here; it does not exist.

That settles the protocol question in section 19 by removing the choice. One enrolment per
device is the only constructible policy, and the registry has been updated to say so and to
pin it with a test.

## 22. The entropy margin is thinner than anything else in this analysis

Falling out of the same inequality, and worth stating on its own because it is the
tightest number in the whole line of work.

Nineteen blocks of BCH(127,15,27): n total 2,413, k total 285. The requirement is
k >= 128 + n(1-rho), which at the measured rho of 0.9414 is 269.4. The margin is 15.6 bits.

Turned around, the construction needs rho >= 0.9349. The measured value is 0.9414, from
ring oscillators on FPGAs in someone else's dataset. **The margin is 0.0065 in entropy
density**, under a percentage point.

Blocks buy margin linearly, since residual scales with block count while the per-block
requirement does not: at 25 blocks the construction tolerates rho >= 0.9302, at the cost of
proportionally more raw response bits and oscillators. That is a dial worth having and it
is currently set to its tightest useful position.

Nothing else in this analysis turns on a figure this close to its limit, and the figure was
measured on a different process, on FPGAs, by someone measuring something else.

## 23. Every figure, in one run

The areas in this document were gathered over six loops as individual synthesis
invocations and typed in by hand. That makes them unreproducible in practice: checking one
meant reconstructing a session's shell history, and a change of library or tool version
would have gone unnoticed until it contradicted something.

`measure_all.sh` runs every probe and prints the table. It runs the testbenches first and
refuses to print any area if one fails, because this project's rule is that no area is
quoted for a circuit that has not decoded correctly, and a script that printed areas
without checking would quietly break the rule it was written to serve.

Run 2026-07-30: six testbenches pass, and all eight areas reproduce exactly the figures
this document quotes.

---

## 24. The code was inherited from a paper along with that paper's operating point

BCH(127,15,27) came from Gao et al., and it is the right code for their constraints: an
SRAM PUF with near-full entropy density and a bit error rate around ten percent. This
project's constraints are different - ring oscillators, measured entropy density 0.9414,
error rate unknown - and adopting a parameter choice along with a method carries the
source's operating point silently.

W-INTL-72 showed what that cost: the entropy margin was the tightest number in the whole
analysis. So the parameter space was searched rather than borrowed.

Code parameters are computed, not looked up. The generator polynomial of a narrow-sense
binary BCH code is the lcm of the minimal polynomials of alpha^1 through alpha^2t, and the
degree of the minimal polynomial of alpha^i is the size of its cyclotomic coset - so the
parity count is the size of a union of cosets, which is arithmetic. `bch_code_search.py`
computes it and refuses to search unless the result reproduces every BCH code named in the
sources read for this project. All four reproduce.

## 25. A better code exists, and it is smaller

| Construction | Tiles | Entropy margin | Max BER | Raw bits |
|---|---|---|---|---|
<!-- derived:external --> | BCH(127,15,27), the inherited choice | 6.07 | 0.0157 | 6.96 percent | 2,921 |
<!-- derived:external --> | **BCH(127,22,23)** | **5.22** | **0.0708** | 5.23 percent | 2,921 |
<!-- derived:external --> | BCH(255,47,42), fallback | 11.86 | 0.0801 | 7.02 percent | 2,805 |
<!-- derived:external --> | BCH(511,139,54) | rejected | 0.1633 | 5.08 percent | 2,555 |

Every decoder area measured, every decoder verified end to end first - including in
GF(2^9), a field this project had never used, which the generator and the parameterised
solver both handled without change.

**BCH(127,22,23) is smaller than the inherited choice and has four and a half times the
margin on the binding constraint.** It costs a quarter of the error tolerance, which is the
right direction to trade: a shortfall in entropy density yields no key at all, while a
shortfall in error rate calls for a stronger code.

Two honest qualifications. Part of the inherited choice's margin here - 0.0157 rather than
the 0.0065 reported in section 22 - is simply spending the whole raw-bit budget on blocks
rather than stopping at the minimum, which is a free improvement that was available all
along and was not taken. And BCH(255,47,42) buys a little more margin and better error
tolerance for more than double the area, which is the fallback if measurement shows both
quantities worse than expected.

BCH(511,139,54) has by far the best margin and is out on area: its decoder alone measures
304,465 square micrometres, 16.88 tiles, more than the entire sixteen a submission may use
before a single oscillator is placed. That is worth stating as a measurement rather than an
estimate, because the search would otherwise keep recommending it.

## 26. What to measure first, revised

W-INTL-72 changed the priority and this changes it again, in the same direction. The
characterisation structure emits raw counts, so the order of analysis is a choice made
afterwards rather than in silicon. The order should be:

1. **Entropy density per response bit.** It is the binding constraint, a shortfall yields
   no key, and it decides between BCH(127,22,23) at 5.22 tiles and BCH(255,47,42) at 11.86.
2. **Bias.** It decides whether a debiasing stage is needed at all, and with it whether
   oscillator reuse is a requirement rather than a preference.
3. **Bit error rate across temperature.** It is the loosest of the three: every admissible
   code in the search tolerates at least five percent, and a shortfall is answered by a
   stronger code rather than by abandoning the construction.

The error rate has been treated as the headline quantity through six loops of this work. It
is the least decisive of the three.

---

## 27. The chain, run end to end

Every part of this key generator had been verified separately and the chain had never
been run. That is the arrangement in which a Chien search summing t of t+1 coefficients
survived five loops of correct area measurements.

`key_generator_e2e.py` runs it in software: a modelled oscillator bank with a stated
bias, the pairing that turns counts into response bits, syndrome-based helper data,
enrolment, a noisy regeneration, decoding, and the recovered key. Same construction as
the RTL - BCH(127,22,23) over GF(2^7), 23 blocks, 2,921 response bits - and the same
inversionless iteration.

The point is not that the pieces work. It is that `code_choice_model.py` predicts a
failure rate from a binomial tail, and an independent implementation of the actual chain
either agrees or does not.

| Bit error rate | Trials | Observed failure | Model |
|---|---|---|---|
| 0.04 | 300 | 0.000 | 5.71e-09 |
| 0.06 | 300 | 0.000 | 1.23e-05 |
| 0.08 | 200 | 0.000 | 0.00152 |
| 0.10 | 120 | 0.025 | 0.0384 |

Agreement across four orders of magnitude, with the only non-zero observation landing
within sampling error of the prediction. The model now has a second witness.

Two further checks. Keys round-trip at zero noise and at two percent, at bias 0.50 and
0.35, twenty trials each. And blocks corrupted beyond the correction radius - t+6 errors -
were refused or returned a wrong response in 40 of 40 cases, rather than silently
returning a plausible one.

## 28. The oscillator floor asked for the wrong quantity

Found while checking whether the new code moved the floor. It did not; the floor was
wrong.

The figure in use was 272 oscillators, computed as 128 divided by the measured 0.471 bits
per oscillator. That asks for 128 bits of raw entropy. What is needed is 128 bits
surviving publication of the helper data - which is exactly the distinction W-INTL-59
drew for response bits.

It was drawn there and left undrawn here. Two accountings feed the same inequality, one
was corrected six loops ago and the other kept the original error.

With 2,415 bits of leakage, the requirement under reuse is log2(R!) >= 2,543:

| | Oscillators | Ordering entropy | Residual after leakage |
|---|---|---|---|
| floor as used | 272 | 1,813 | **-602** |
| floor correctly stated | 360 | 2,543 | 128 |

At the floor in use the residual is negative and the construction yields no key at all.

Every reuse figure this project has published is affected, and the area consequences are
small because oscillators are cheap:

| Construction | Was | Now |
|---|---|---|
| BCH(127,22,23), current | 5.22 tiles | 5.34 tiles |
| BCH(127,15,27) | 6.07 tiles | 6.22 tiles |
| BCH(255,47,42) | 11.86 tiles | 11.96 tiles |

The area moved by two percent and the validity moved from no to yes, which is the
uncomfortable part: a wrong figure that barely changes the answer is the hardest kind to
notice. Position count is not the binding constraint either way - 77 oscillators supply
the 2,921 positions needed, against 360 for the entropy.

## 29. Every borrowed constant, and the operating point it came with

W-INTL-74 found a code adopted from a paper along with that paper's operating point. The
rule generalises, so here is every constant in this analysis that came from a source
rather than from a measurement of this project.

**Min-entropy density, 0.9414.** Wilde, Hiller and Pehl, from Maiti's dataset: 512 ring
oscillators on each of 193 Xilinx Spartan-3E parts, at room temperature, paired
**disjointly with their immediate neighbours**. The same paper shows two published
figures from the same raw data disagreeing widely because one compares adjacent
oscillators and the other distant ones. This project would use a 130 nm open process
with an unspecified layout, and it is the tightest input in the analysis. Carried with
the largest caveat of anything here.

**Debiasing overheads, 1.58 to 5.3.** Maes, van der Leest, van der Sluis and Willems,
computed for a 1,000-bit output at a failure rate of 1e-6. The overhead depends on the
output length through an inverse binomial, so scaling these to a different length is an
approximation rather than a lookup. Not currently corrected for, and it should be before
any of them is used to size a design.

**Oscillator area, 26.3 square micrometres.** Seven inverters, from the published Tiny
Tapeout implementation, scaled by its measured inverter area. Mansouri and Dubrova state
that the minimum inverter count for a usable oscillation frequency is typically ten to
twenty. So this figure may be for an atypically short oscillator, and a bank built to a
conventional length would be one and a half to three times the area. Since oscillators
are a small part of the budget this does not change any conclusion, which is why it had
not been examined.

**Target of 171 error-free bits.** Bosch et al., derived from SRAM PUF entropy. Now
vestigial: since the leakage inequality is applied directly with a density, this constant
is used only on the inadmissible path in the model. Worth removing rather than leaving as
a number that looks load-bearing.

**Tile geometry, 18,032 square micrometres and a sixteen-tile limit.** Tiny Tapeout, and
the only borrowed constants here that are a published specification rather than a
measurement of something else.

---

## 30. The debiasing overhead, computed rather than borrowed

W-INTL-79 listed the debiasing overheads as the one borrowed constant being applied
knowingly wrong: Maes et al. compute them for a 1,000-bit output, and this construction
needs 2,921. The overhead depends on output length through an inverse binomial, so
scaling the figures was an approximation rather than a lookup.

The constraint is now implemented. For an n-bit response at bias p, the number of bits
retained by von Neumann debiasing is binomially distributed with parameters
(floor(n/2), 2p(1-p)), and n must be large enough that the failure-rate quantile of that
distribution still reaches the required output length.

Calibration first: the implementation reproduces all three figures the paper states -
4,446 and 2,322 at fifty percent bias, and 5,334 at thirty - exactly.

Rescaled to 2,921 response bits:

| Method | Bias | Raw bits needed | Overhead | Figure borrowed until now |
|---|---|---|---|---|
<!-- derived:external --> | CVN | 50 percent | 12,432 | 4.26 | 4.40 |
<!-- derived:external --> | CVN | 30 percent | 14,868 | 5.09 | 5.30 |
<!-- derived:external --> | 2O-VN | 50 percent | 6,376 | 2.18 | 2.31 |
<!-- derived:external --> | 2O-VN | 30 percent | 7,638 | 2.61 | 2.66 |

Every corrected figure is lower than the borrowed one, by three to five percent, because
relative binomial fluctuation shrinks as the output grows and less slack is needed. So the
project has been conservative rather than wrong, which is the better direction to have
erred - and it is now computed rather than approximated.

The conclusion of section 18 is unaffected: at 2.18 the disjoint arrangement still needs
6,368 response bits and 23.4 tiles, well over the sixteen available.

## 31. Debiasing in the chain, and a third witness

The end-to-end run now includes the debiasing stage, so the formula above has an
independent check.

| Method | Bias | Raw needed by formula | Retained over 12 trials |
|---|---|---|---|
<!-- derived:external --> | CVN | 50 percent | 12,432 | 3,050 to 3,163 |
<!-- derived:external --> | CVN | 30 percent | 14,868 | 3,066 to 3,221 |
<!-- derived:external --> | 2O-VN | 50 percent | 6,376 | 3,132 to 3,322 |
<!-- derived:external --> | 2O-VN | 30 percent | 7,638 | 3,056 to 3,344 |

Every trial clears the 2,921 the construction needs, with the margin a constraint sized
for one failure in a million should leave.

And the stage does what it is for. Sources at bias 0.50, 0.30 and 0.20 produce retained
bits at 0.4999, 0.5014 and 0.4995 over tens of thousands of bits - which is the von
Neumann property, demonstrated rather than cited.

## 32. How much the answer depends on the number measured elsewhere

The entropy density is the weakest input in this work: 0.9414, from ring oscillators on
Spartan-3E parts, at room temperature, with adjacent pairing, gathered by other people for
another purpose. Reporting a conclusion at one value of it would be reporting a conclusion
at someone else's operating point, which is the error W-INTL-74 was written about.

So, across the plausible range, restricted to codes whose decoders have been measured:

| Entropy density | Best code | Tiles | Max BER |
|---|---|---|---|
<!-- derived:external --> | 1.00 to 0.88 | BCH(127,22,23) | 5.34 | 5.23 percent |
| 0.87 and below | none among measured codes | - | - |

**The recommendation does not move at all between 0.88 and 1.00** - same code, same area,
same error tolerance - and then stops entirely. The measured value sits 0.07 above the
cliff.

That is a better shape of answer than a margin. A margin invites the question of how much
is enough; a flat band with an edge says the decision is insensitive to the weak input
over a wide range, and names the point where it is not.

Two honest qualifications. The cliff is a cliff in the *measured* set: the search finds
codes with margin down to 0.78, but their decoders are either unmeasured or, for the n=511
family, measured and too large. So below 0.87 the answer is not that nothing works, it is
that nothing that has been measured works, and finding out would mean measuring more.

And the band's flatness is partly an artefact of restricting to five measured codes. With
a denser measured set the area would likely fall somewhat as the density rises. The
important part - that nothing changes across a six-point range - would survive.

---

## 33. The reuse claim, checked on this construction

The registry's enrolment policy rests on a claim taken from Maes et al.: that classic and
pair-output von Neumann debiasing are not reusable, so enrolling the same device twice
leaks more than once does. That claim was written into `ChipRegistryV2` as the reason for
refusing re-registration, and it had not been checked here.

It needed checking, because the paper's demonstration is on a construction this project
does not use. Its figure shows an inner two-bit repetition code and reasons about which
bits land in the same codeword. There is no repetition code here.

What generalises is the sentence beside the figure rather than the figure: enrolled bits
can shift between code words, because the debiasing step is stochastic and bit errors
between enrolments change which pairs are retained.

Demonstrated on this construction. A 12,432-bit raw response, a second measurement of the
same device differing in 259 bits at two percent noise:

- enrolment one retains 3,062 bits, enrolment two retains 3,057
- the public retention patterns differ at 253 pairs
- of the 2,794 pairs retained in both, **124 land in a different BCH block the second
  time** - four and a half percent - and every pair after the first divergence is displaced

So each enrolment publishes a syndrome over a different partition of the same raw bits.
The mechanism the source names does apply here, and the policy written into the contract
stands on it.

One thing this does not do, and the distinction matters. It demonstrates the mechanism,
not the quantity: that bits shift between blocks is shown, that two enrolments leak
strictly more than one follows from it, and how much more has not been computed. The
policy is conservative either way, since it forbids the second enrolment entirely.

## 34. The flat band was not an artefact of a sparse set

Section 32 reported the recommendation as flat from entropy density 0.88 to 1.00, and
qualified it: with only five measured decoders the flatness might be an artefact, and a
denser set would probably show the area falling as density rises.

Three more codes have been generated, verified end to end, and measured, chosen to
populate the band and to probe below its edge:

| Code | Decoder area | Tiles |
|---|---|---|
| BCH(127,8,31) | 116,194 | 6.44 |
| BCH(255,45,43) | 211,985 | 11.76 |
| BCH(255,37,45) | 222,024 | 12.31 |

Swept at one-hundredth intervals across eight measured codes, the answer changes in
exactly two places:

| Entropy density | Best measured code | Tiles | Max BER |
|---|---|---|---|
<!-- derived:external --> | 1.00 down to 0.88 | BCH(127,22,23) | 5.34 | 5.23 percent |
<!-- derived:external --> | 0.87 | BCH(255,47,42) | 11.96 | 7.02 percent |
| 0.86 and below | none measured | - | - |

The qualification is answered: the flatness survived densification. None of the three new
codes improves on BCH(127,22,23) anywhere in the band, so the flat stretch is a property of
the problem rather than of the sample.

Two things sharpened. The edge is at 0.8613 rather than 0.87 - the earlier sweep stepped in
units of 0.02 and hid a code that works just below its resolution, which is a reminder that
a sweep's granularity is part of its result. And between the band and the edge there is a
single step, not a slope: one point of entropy density costs more than double the area,
because it forces the move from GF(2^7) to GF(2^8) and a correction strength of 42.

---

## 35. Two inputs at once, which is what one fabrication answers

Every sweep so far moved the entropy density with the error-rate requirement held at five
percent. Both quantities come from the same characterisation structure, so the pair is
what a single fabrication would return, and holding one fixed while sweeping the other was
an artefact of how the analysis grew rather than a property of the problem.

Cheapest measured code that works, in tiles, across ten measured decoders:

```
             2%     3%     4%     5%     6%     7%     8%   <- bit error rate
rho 1.00   4.92  4.92  4.92  5.34  6.22  7.02  7.02
rho 0.94   4.92  4.92  4.92  5.34  6.22 11.96     -   <- measured entropy
rho 0.90   4.92  4.92  4.92  5.34 11.96 11.96     -
rho 0.88   4.92  4.92  4.92  5.34 11.96 11.96     -
rho 0.86   4.92  4.92  4.92     -     -     -     -
rho 0.82   4.92  4.92  4.92     -     -     -     -
rho 0.81      -     -     -     -     -     -     -
```

This corrects the priority stated three loops ago. That loop concluded the error rate was
the least decisive of the three quantities, and it reached that by sweeping entropy density
while holding the error requirement at five percent. With both moving, the error rate has a
cliff at eight percent among measured codes and entropy has one at 0.8155 - and published
ring-oscillator error rates across temperature reach the first far more readily than
published entropy figures approach the second.

The useful shape: a rectangle. **Entropy density at or above 0.82 and error rate at or
below four percent gives 4.92 tiles**, and nothing inside that rectangle changes the answer.

## 36. The codes that mattered were outside the region I sampled

Last loop this document reported the flat band as a property of the problem rather than of
the sample, having densified from five measured codes to eight. That conclusion was drawn
from three codes chosen to populate the band and probe just under its edge.

Two more codes, chosen further below the edge, moved the whole picture:

| Code | Decoder | Tiles | rho_min | Max BER |
|---|---|---|---|---|
<!-- derived:external --> | BCH(127,29,21) | 79,787 | 4.42 | 0.8155 | 4.42 percent |
<!-- derived:external --> | BCH(255,55,31) | 152,170 | 8.44 | 0.8299 | 4.34 percent |

BCH(127,29,21) is **cheaper than the recommendation it challenges** - 4.42 tiles of decoder
against 4.82 - and tolerates entropy density down to 0.8155 against 0.8706. It costs error
tolerance, 4.42 percent against 5.23.

So the flatness held where I sampled and did not hold where I had not. The correction is
not to the earlier measurement, which was right, but to the inference: densifying inside a
region already believed flat tests almost nothing. A qualification about a sample is
answered by sampling where the sample was thin, not where it was thick.

## 37. What the recommendation is now

It depends on which cell of the map the characterisation lands in, and that is the honest
form of the answer:

- **error rate at or below four percent**: BCH(127,29,21), 4.92 tiles, works down to
  entropy density 0.8155
- **error rate five percent**: BCH(127,22,23), 5.34 tiles, needs 0.8706
- **error rate six to seven percent**: 6.22 to 11.96 tiles depending on entropy
- **error rate at or above eight percent**: no measured code, and the search says codes
  exist but their decoders are unmeasured or too large

The prudent build, before any measurement, is the code that covers the largest rectangle
rather than the one that is cheapest at a guessed operating point. That is BCH(127,29,21)
if the error rate can be held to four percent, and the whole point of the characterisation
structure is that this is a measurement rather than a guess.

## 38. The re-enrolment leak, measured rather than bounded

W-INTL-83 demonstrated the mechanism by which a second enrolment leaks and said explicitly
that the quantity had not been computed. Computed now, on an instance small enough to
enumerate exhaustively rather than bound.

Sixteen-bit raw response, classic von Neumann, six-bit response, three-bit syndrome, second
enrolment differing in at most two raw bits. Sixty devices, candidate keys counted over all
2^16 raw strings:

| | Candidate keys | Entropy |
|---|---|---|
| after one enrolment | 8.0 | 3.00 bits |
| after two enrolments | 4.9 | 2.30 bits |

**The second enrolment removes 0.70 bits of 3.00 - about a quarter of what remained** - and
strictly reduced the candidate set in 39 of 60 cases.

That is a measurement on a toy, and whether the fraction scales to a 2,921-bit response has
not been established. What it establishes is that the leak is a substantial fraction rather
than a negligible one, which is what the contract policy needed and did not have.

---

## 39. The map, filled in where it was blank

Three codes were measured to attack the blank regions rather than the populated ones -
the lesson from section 36. Two aimed at the high error-rate column, which had no answer
below entropy density 1.00, and one below the lower edge.

| Code | Decoder | Tiles | rho_min | Max BER |
|---|---|---|---|---|
<!-- derived:external --> | BCH(255,29,47) | 231,431 | 12.83 | 0.9319 | 8.34 percent |
<!-- derived:external --> | BCH(255,21,55) | 268,820 | 14.91 | 0.9633 | 10.54 percent |
<!-- derived:external --> | BCH(255,63,30) | 147,563 | 8.18 | 0.7986 | 4.11 percent |

Thirteen measured decoders, cheapest that works including its oscillator floor:

```
                  3%     4%     5%     6%     7%     8%     9%    10%
rho 1.00     4.92  4.92  5.34  6.22  7.02  7.02 15.46 15.46
rho 0.98     4.92  4.92  5.34  6.22 11.96 13.37 15.46 15.46
rho 0.96     4.92  4.92  5.34  6.22 11.96 13.37     -     -
rho 0.94     4.92  4.92  5.34  6.22 11.96 13.37     -     -   <- measured entropy
rho 0.92     4.92  4.92  5.34 11.96 11.96     -     -     -
rho 0.90     4.92  4.92  5.34 11.96 11.96     -     -     -
rho 0.86     4.92  4.92     -     -     -     -     -     -
rho 0.82     4.92  4.92     -     -     -     -     -     -
rho 0.80     8.66  8.66     -     -     -     -     -     -
rho 0.79        -     -     -     -     -     -     -     -
```

The blank column is answered where it matters. At the measured entropy density the project
now has a construction up to eight percent bit error rate, where last loop it had nothing
above seven. The cost is steep - 13.37 tiles against 4.92 - but a design that exists at 84
percent of the budget beats a blank cell.

The n=511 family is excluded without measuring it further, and the argument is a measured
point plus monotonicity rather than an estimate: its decoder at t=54 measures 16.88 tiles,
already over the whole budget, and decoder area increases with t at fixed field. Every
n=511 candidate in the search has t of 85 or more.

What remains blank: nine percent and above at the measured entropy density. That needs
0.98, which is above what has been measured anywhere. If the real bank turns out both noisy
and ordinary, there is no construction in this set for it - and that is now a specific
statement about one cell rather than a general unknown.

## 40. The leak fraction does not shrink with scale, and the single number was over-specific

Section 38 reported the second enrolment removing 0.70 bits of 3.00 - about a quarter of
what remained - from a sixteen-bit instance, and said the scaling was unestablished. Tested
across five sizes:

<!-- derived:external -->

| Raw bits | Response | Checks | After one | After two | Lost |
|---|---|---|---|---|---|
| 12 | 4 | 2 | 3.00 | 2.85 | 0.15 |
| 14 | 5 | 2 | 4.00 | 3.83 | 0.17 |
| 16 | 6 | 3 | 4.00 | 3.51 | 0.49 |
| 18 | 7 | 3 | 4.00 | 3.34 | 0.66 |
| 20 | 8 | 4 | 4.00 | 3.22 | 0.78 |

The absolute loss grows monotonically at roughly constant residual entropy - 0.15 bits at
twelve raw bits to 0.78 at twenty. It does not shrink, which is the question that mattered:
a leak that vanished at scale would have made the enrolment policy optional.

Two corrections to how section 38 stated this. The fraction is not a constant: the same
sixteen-bit size gives 23 percent there and 12 percent here, differing only in which parity
checks the toy uses, so the leak depends on the code and a single percentage was
over-specific. And five points spanning twelve to twenty raw bits do not extrapolate to
12,432 - the direction is established, the value at scale is not.

The policy stands on the direction. It forbids the second enrolment outright, so it is
correct whether the leak is a fifth or a half.

---

## 41. Power was never a constraint here, and now that is known rather than assumed

Thirteen decoders had been sized purely on area. Tiny Tapeout's specifications give a
supply of 1.8 volts for the digital core and state that a draw of around 20 milliamps
produces a 0.1 volt drop through the power delivery network - about five ohms. No
per-project power limit is published, so the practical constraint is that drop.

Estimated from the library rather than from a guess: input pin capacitance summed per
instantiated cell out of the liberty, with the activity factor as the single stated
assumption.

| Design | Cells | Switched capacitance | 20 mA reached at 15 percent activity |
|---|---|---|---|
<!-- derived:external --> | BCH(127,29,21) | 10,586 | 36.0 pF | 2,059 MHz |
<!-- derived:external --> | BCH(255,21,55) | 35,643 | 121.7 pF | 609 MHz |

At ten megahertz and fifteen percent activity the larger decoder draws 0.33 milliamps and
drops 1.6 millivolts. The decoder runs once at power-up for a few thousand cycles, so this
is also its whole duty cycle.

Two honest limits on the figure. It counts gate input capacitance and not interconnect,
which at 130 nanometres can be comparable, so the real current could be two or three times
higher. And the leakage extracted from the library comes to fractions of a microwatt, which
is low enough that the units are probably being read wrong - so it is not leaned on. Neither
matters: at three times the estimate the constraint still binds only above 200 megahertz,
and a thousand times the leakage would still be 61 microamps.

So a constraint was missing from the analysis and turns out to be slack. That is worth
recording as a result rather than dropping, because the reason it went unexamined - area was
the interesting axis - is the same reason a binding constraint would have gone unexamined.

## 42. The last blank cell cannot be closed, which is an answer

Section 39 left one cell blank: nine percent bit error rate or above at the measured entropy
density of 0.9414. Enumerated over every narrow-sense binary BCH code from GF(2^6) to
GF(2^10), exactly three satisfy both the leakage inequality and the nine percent target:

| Code | t | Blocks | rho_min | Max BER | Status |
|---|---|---|---|---|---|
<!-- derived:external --> | BCH(511,76,85) | 85 | 5 | 0.9014 | 9.55 percent | excluded |
<!-- derived:external --> | BCH(511,67,87) | 87 | 5 | 0.9190 | 9.85 percent | excluded |
<!-- derived:external --> | BCH(511,58,91) | 91 | 5 | 0.9366 | 10.46 percent | excluded |

All three are n=511, and the family is excluded by the measured point at t=54 - 16.88 tiles
of decoder, already over the whole budget - plus monotonicity of area in t at fixed field.

**So the cell is not unmeasured; it is empty.** No single BCH code answers a nine percent
error rate at this entropy density within sixteen tiles, and concatenation cannot help
because it multiplies the code length while leaving the dimension alone, which is what makes
the leakage inequality fail. Closing that cell would need a larger area allocation, a
different code family, or a lower error rate.

That is a better thing to know than a gap. A gap invites another loop of measurement; a
proof redirects the effort to the error rate, where it belongs.

## 43. The oscillator length does not matter, tested rather than assumed

The oscillator area of 26.3 square micrometres assumes seven inverters, taken from the
published tile, where Mansouri and Dubrova call ten to twenty typical for a usable
frequency. That caveat had been carried for four loops on the grounds that oscillators are
a small part of the budget.

Tested at seven, fourteen and twenty inverters:

| Cell | 7 inverters | 14 inverters | 20 inverters |
|---|---|---|---|
<!-- derived:external --> <!-- derived:external --> | rho 0.94, BER 4 percent | 4.92 | 5.42 | 5.85 |
<!-- derived:external --> <!-- derived:external --> | rho 0.94, BER 8 percent | 13.37 | 13.91 | 14.37 |
<!-- derived:external --> | rho 0.82, BER 4 percent | 4.92 | 5.42 | 5.85 |

Tripling the oscillator length costs nineteen percent in the cheap cell and eight in the
expensive one, and **no cell changes from fitting to not fitting**. The caveat is discharged.

It was reasonable to defer and it is better closed: a caveat carried on the grounds that it
probably does not matter is a caveat nobody can act on, and the test cost one calculation.

---

## 44. Timing, measured for the first time across thirteen designs

None of the thirteen decoders had closed timing, and `bm_area_probe.v` says so in its own
header: the critical path is one general multiply, an XOR tree over t+1 terms, and a second
multiply, with a systolic reformulation available if the clock matters. Nobody had checked
what clock it does reach.

No static timing analyser is installed here, so the measurement is logic depth rather than
delay - the longest topological path through the mapped netlist, which the synthesiser
reports directly:

| Design | Logic depth |
|---|---|
<!-- derived:external --> | solver, GF(2^8), t=4 | 18 |
<!-- derived:external --> <!-- derived:external --> | solver, GF(2^7), t=23 | 17 |
<!-- derived:external --> | solver, GF(2^8), t=18 | 21 |
<!-- derived:external --> <!-- derived:external --> | solver, GF(2^8), t=55 | 23 |

The depth grows logarithmically in t - eighteen at t=4, twenty-three at t=55 - which is what
the header predicted: two multipliers at about m levels each plus a tree of log2(t+1). At
t=55 that is sixteen plus six, and twenty-three is measured. **The file's own architectural
claim is confirmed by measurement rather than restated.**

Converting to a clock needs a per-level delay, taken from the liberty: the median table entry
for the two-input gates the mapper actually uses runs 220 to 350 picoseconds. At those
figures the solver reaches roughly 145 to 300 megahertz, the slowest case being t=55.

Two limits. The depth is measured before technology mapping, and the mapper both merges
levels into complex cells and inserts buffers, so it is a proxy. And there is no wire delay.
Against a Tiny Tapeout user clock of a few tens of megahertz, the margin is three-fold to
thirty-fold either way.

## 45. The power figure has a second witness, and it agrees

Section 41 estimated dynamic current from input pin capacitance and flagged that the
leakage extracted from the same library looked implausibly small - a sign the units might be
misread. That is a reason to distrust the whole extraction, not just the leakage.

Computed a second way, through a different part of the library: energy per switching event
from the internal_power tables, which is a different quantity arrived at by a different
route.

| Design | Capacitance route | Internal-power route | Ratio |
|---|---|---|---|
<!-- derived:external --> | BCH(127,29,21) | 20 mA at 2,059 MHz | 20 mA at 2,540 MHz | 1.2x |
<!-- derived:external --> | BCH(255,21,55) | 20 mA at 609 MHz | 20 mA at 741 MHz | 1.2x |

Agreement within twenty percent. That is a second witness for the dynamic figure and, more
usefully, it validates the units interpretation the leakage anomaly had called into
question.

Interconnect, which the capacitance route omits, is not negligible: at 130 nanometres a local
net carries roughly one to two femtofarads, and with one net per cell output that is
comparable to the gate capacitance rather than a correction to it.

| BCH(255,21,55) | Wire capacitance | Total | 20 mA at |
|---|---|---|---|
<!-- derived:external --> | 1 fF per net | 36 pF | 157 pF | 471 MHz |
<!-- derived:external --> | 2 fF per net | 71 pF | 193 pF | 384 MHz |

## 46. Timing binds before power, and both by an order of magnitude

Putting the two together for the largest decoder: timing runs out at 145 to 300 megahertz,
power at 384 to 471. **Timing is the tighter of the two**, which is worth knowing because
the intuition ran the other way - a design with 35,643 cells sounds like a power problem and
is a depth problem.

Neither binds. A Tiny Tapeout user clock is a few tens of megahertz and the decoder runs once
at power-up for a few thousand cycles, so both constraints have at least an order of
magnitude in hand.

Three dimensions have now been checked that the analysis did not originally have: power,
timing, and interconnect. All three are slack. That is three for three, and the reason to
keep recording them is that the fourth might not be.

---

## 47. The solver does own the critical path, checked rather than assumed

Section 44 measured the solver's depth and concluded 145 to 300 megahertz without measuring
the other two stages. The Chien search carries an XOR tree over t+1 terms too, so the
conclusion rested on an assumption about which stage is deepest.

Measured:

| Stage | Logic depth |
|---|---|
<!-- derived:external --> | syndrome bank, GF(2^8), t=55 | 6 |
<!-- derived:external --> | Chien search, GF(2^8), t=55 | 11 |
<!-- derived:external --> | both table stages together | 11 |
<!-- derived:external --> | key-equation solver, GF(2^8), t=55 | 23 |

The solver is roughly twice either table stage, so it does own the path. The gap is closed
and the conclusion survived.

The reason is the same structural fact that made the solver three times the area: its
multiplies are between two runtime values and take about m levels each, while the table
stages multiply by compile-time constants which fold into shallow XOR trees. The Chien depth
of eleven is a constant multiplier of about five levels plus a tree of log2(56), and the
solver's twenty-three is two general multipliers of eight plus the same tree. **One
architectural property predicts both the area ratio and the depth ratio**, which is the kind
of agreement worth noticing when it happens.

## 48. Depth after mapping, and the earlier figure was conservative

Section 44's depth was measured before technology mapping and flagged as a proxy, because
the mapper both merges levels into complex cells and inserts buffers.

Measured after mapping, with the flip-flops left in their generic form so that the path
tracer cuts at them - reading the standard-cell library as blackboxes makes it walk straight
through the sequential elements and report a meaningless five-thousand-level path, which it
did on the first attempt:

<!-- derived:external -->

| Design | Generic | Mapped |
|---|---|---|
<!-- derived:external --> | solver, GF(2^7), t=23 | 17 | 13 |
<!-- derived:external --> | solver, GF(2^8), t=55 | 23 | 17 |

The mapper removes about a quarter of the depth, so the earlier figure was conservative
rather than optimistic. Corrected, the solver reaches 220 to 350 megahertz at t=23 and 168 to
267 at t=55.

The failed first attempt is worth recording. A path tracer given a netlist whose sequential
cells it cannot recognise returns a number that looks like a depth and is a walk through the
entire design. It did not resemble a plausible answer, which is the only reason it was caught -
the same figure at three times the true value would have been quoted.

## 49. Eleven constraints, in one list at last

Written up as `research/constraint_register.md`. Six constraints bind, one binds as policy,
four are checked and slack, and six more are named as unchecked with the reason each might
matter.

The register exists because the absence of one caused three reversals in this work: a code
chosen on area that failed the error target, a replacement that failed the leakage bound, and
a priority ordering that was an artefact of sweeping one input while holding another fixed.
Each time the missing constraint was written down somewhere in a source and not in this
project.

The most useful entry is the top of the unchecked list. Helper-data manipulation by an active
adversary is a security property, it is named as load-bearing by a source this project relies
on, and the reasoning was inherited rather than reproduced - which is the same pattern as the
reuse claim, checked in section 33 and found to hold. That one held. This one has not been
looked at.

---

## 50. Cell area is not die area, and the factor was dropped seventeen loops ago

Every tile figure in this document divides cell area by the whole area of a tile. Cell area
is not die area: a placed and routed block needs room to route, and the fraction of a tile
that ends up as standard cells is well under one.

That factor was measured in the very first pass of this work, on the published tile the
oscillator areas come from. It declares 1x2 tiles, 36,064 square micrometres, and holds
20,900 square micrometres of cells - **58 percent utilisation**, from the same flow on the
same process. `puf_tile_budget.md` records it and applies it.

It was then dropped. Every figure computed after the code-choice work began - every entry in
`code_choice_model.py`, `bch_code_search.py`, and every version of the map - divides by the
raw tile area. **Every tile count in this analysis has been optimistic by a factor of 1.7.**

Recomputed:

| | As published | At 70 percent | At 58 percent, measured |
|---|---|---|---|
<!-- derived:external --> | rho 0.94, BER 4 percent | 4.92 | 7.03 | **8.49** |
<!-- derived:external --> | rho 0.94, BER 5 percent | 5.34 | 7.63 | 9.21 |
<!-- derived:external --> | rho 0.94, BER 6 percent | 6.22 | 8.89 | 10.73 |
<!-- derived:external --> | rho 0.94, BER 7 percent | 11.96 | does not fit | does not fit |
<!-- derived:external --> | rho 0.94, BER 8 percent | 13.37 | does not fit | does not fit |

So the answer at the measured entropy density is that the design fits up to six percent bit
error rate, at 10.73 of sixteen tiles, and not above. The seven and eight percent columns
were answered in section 39 and are blank again.

Three things about how this happened, because the failure is more interesting than the
number.

**It was inside a constraint already marked binding.** The constraint register written last
loop lists tile area as binding, with a status column and a source. The row was correct and
its arithmetic was wrong. A register records which constraints exist; it does not check the
computation behind each one, and writing one is not a substitute for recomputing.

**The factor was not missing, it was abandoned.** It had been measured, recorded, and used.
The drift happened when the analysis moved from one document to another and the second
started from the cell areas rather than from the first document's conclusions. A number
carried forward by hand between files is a number that will eventually not be carried.

**Three constraints checked in the last two loops all came back slack, and I said that was
not evidence the next would be.** It was not the next constraint that bit. It was one of the
ones already in the list.

## 51. Synchroniser metastability, closed with an enormous margin

The characterisation structure samples free-running oscillators through two flip-flops, and
the register named the mean time between failures as an omission of mine rather than of any
source.

Computed on the standard two-parameter model, at the pessimistic end of published 130
nanometre figures - a settling time constant of 300 picoseconds and a metastability window of
100:

| Clock | Data rate | Resolution time | Time constants | MTBF |
|---|---|---|---|---|
<!-- derived:external --> | 10 MHz | 1 MHz | 90 ns | 300 | 10^120 years |
<!-- derived:external --> | 50 MHz | 5 MHz | 18 ns | 60 | 10^14 years |
<!-- derived:external --> | 100 MHz | 10 MHz | 9 ns | 30 | 10 years |

At the intended clock the margin is beyond meaning, and two stages is overkill rather than
merely conventional. The reason is that the structure is slow by design: it counts a
prescaled oscillator over a long gate window, so the asynchronous event rate is low and a
whole clock period is available to settle.

Worth keeping the third row. The margin collapses from 10^120 years to 10 across one decade
of clock, which is what an exponential does - so this is closed for this design at this clock
and not a general result about the structure.

## 52. Helper-data manipulation: located, not verified, and the abstract says something worse

The register put this first among unchecked items, on the grounds that it is a security
property whose reasoning was inherited. Chased, and the outcome is partial.

Gao et al. state it in their own words: their case study employed BCH codes and syndrome
decoding, which has been shown to be secure under helper-data manipulation attacks, citing
Becker. That sentence was read directly from their paper, so the claim is properly located.

Becker's own text could not be reached - the preprint returns 403 to an unauthenticated
fetch, and the abstract does not name any code. So the specific claim that BCH with syndrome
decoding is immune remains second-hand, and this project's construction rests on somebody
else's summary of a paper this project has not read. That is exactly the pattern the register
flagged, and it is not closed.

What the abstract does establish is less comfortable than the claim it fails to confirm. The
provably secure robust construction does not meet the error-correction requirements of
practical PUF applications; fuzzy extractors that do meet those requirements cannot be
extended to robust ones, because of a strict bound on correctable errors; and the paper's new
attacks work even against robust-like constructions built without that bound.

Read plainly: **no construction in this space has both a robustness proof and practical error
correction.** This project's construction therefore has no robustness proof either, whatever
its resistance to the specific attacks in that paper.

That does not change what to build, since no alternative has a proof either. It changes what
may be claimed. Any statement that this identity root resists an active adversary who can
tamper with helper data would rest on a second-hand summary, and the honest position is that
the question is open and the field says it is open.
