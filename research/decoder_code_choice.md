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
against 4.82 - and tolerates entropy density down to 0.7485 against 0.8706. It costs error
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

---

## 53. A check that compares a document against a computation

Every check in this project until now compares documents with each other. That is why
W-INTL-99 survived eighteen loops: the prose said 4.92 tiles, the script computed 4.92 tiles,
and both were wrong together because they shared the same missing step. Cross-document
agreement cannot catch a shared omission.

`scripts/check_figures_reproduce.py` recomputes the headline from its inputs - cell areas,
oscillator floor, utilisation, tile size - and fails if a document disagrees. It is in CI.

Three negative controls, and all three fire:

- dropping the utilisation factor, which is the historical fault, makes the seven and eight
  percent columns fit again and the check says so by name
- changing a decoder area by ten percent makes the recomputed figure disagree with the ledger
- changing the ledger's figure while leaving the inputs alone does the same in the other
  direction

A fourth control did not fire, and the reason is worth more than the control. I copied the
script to a temporary directory to inject the fault, which moved the repository root two
levels up, so the ledger comparison silently did nothing and the run printed a clean pass.
`check_consistency.py` carries a warning about exactly this in its header - negative controls
must be written with the same care as the checks - and it was written after two controls
failed the same way. It caught me a third time.

## 54. Stale figures found in the ledger while debugging

The ledger's headline had been corrected to 8.49 tiles and two earlier sentences in the same
row still carried 4.92 and 5.34 - the pre-correction values W-INTL-99 invalidated. One
sentence was updated and the others were not.

Found by accident, while looking at what the new check's regular expression matched. The
check would not have caught it: it verifies one figure, and the stale ones sit in different
sentences. Corrected, and it is a reminder that a correction applied to a document is applied
to the sentence you are looking at.

## 55. Every binding row, re-derived rather than re-read

The rule from W-INTL-99 was that a register records which constraints exist and does not check
the arithmetic under them. Applied to the remaining five arithmetic rows, for BCH(127,29,21)
over 23 blocks:

| Row | Derivation | Result |
|---|---|---|
<!-- derived:external --> | leakage | rho*n - (n-k) = 0.9414 x 2921 - 2254 | 496 against 128 needed |
<!-- derived:external --> | error target | per block 7.39e-09 at four percent, over 23 blocks | 1.7e-07 against 1e-06 |
<!-- derived:external --> | area | (79,787 + 341 x 26.3) / 0.58 / 18,032 | 8.49 of 16 tiles |
<!-- derived:external --> | entropy density | 1 - (29 - 128/23)/127 | 0.8155, margin 0.1259 |
<!-- derived:external --> | oscillator floor | log2(341!) against 2254 + 128 | 2,383 against 2,382 |

All five reproduce. Only the area row had been wrong, and it is now the one with a check
behind it.

One detail the re-derivation sharpened: this code fails at five percent, not just above it -
8.16e-06 against a target of 1e-06. The recommendation is four percent or below, and five
percent requires moving to BCH(127,22,23). The documents said that; the derivation confirms
the boundary is at four rather than near five.

## 56. Helper-data manipulation: the distinction is code-offset against syndrome

The register put this first among unchecked items and section 52 left it located but
unverified, with Becker's text behind a 403.

A second search over the literature returns a specific and consistent account, and it
identifies the distinction that matters. The repetition code is vulnerable; other linear block
codes including BCH, Reed-Muller and single parity check are affected by the same problem; and
**linear BCH with syndrome decoding is the case proven immune**. An error pattern was found
against the [16,5,8] Reed-Muller code by exhaustively testing all 2^16 possibilities.

So the dividing line is not the code family, it is the construction. A BCH code used in a
code-offset scheme is affected; BCH with syndrome-based helper data is not. This project uses
syndrome-based helper data, so it lands on the immune side of a line a code-offset design with
the same code would land on the wrong side of.

Status, stated exactly. Two independent secondary sources now say this - Gao et al. in their
own words, and this account - and both attribute it to Becker. The primary is still unread.
That is corroboration rather than verification, and the difference is that corroboration can
be wrong in the same way twice.

One consequence for the record. The Reed-Muller construction this document recommended for
two loops before the leakage bound withdrew it is the *named example* of the attack working.
It was inadmissible on leakage and vulnerable to helper-data manipulation, and the leakage
bound happened to catch it first. Being wrong for a reason you did not find is not the same as
being right.

---

## 57. One declaration per input

The audit prompted by W-INTL-99 found each measured quantity living in three to seven
files: the tile area declared three times, the utilisation three times, the entropy density
three times, the key length four, the decoder table three. Each of those is a place where
drift can start, and the rule that came out of the last loop - a number carried by hand
will eventually not be carried - is not fixed by being careful.

`research/inputs.py` now declares each one once, with the measurement it came from and
which of three categories it belongs to: measured here and reproducible by
`measure_all.sh`, measured by somebody else with the conditions stated, or a published
specification. `code_choice_model.py`, `bch_code_search.py` and
`scripts/check_figures_reproduce.py` import rather than redeclare, and all three still
agree.

One small improvement fell out. The utilisation had been written by hand as 0.58; computed
from the two numbers it comes from - 20,900 square micrometres of cells in 36,064 of tile -
it is 0.5795. The tile figure is unchanged at 8.49, and the constant now carries its own
derivation instead of a rounding of it.

## 58. Extending the check found a live error immediately

The check from section 53 verified one figure. Extended to the entropy-density floor and
the oscillator floor, it failed at once:

    FAIL: evidence_ledger.md: oscillator floor says 360, recomputing from inputs gives 341

The floor of 360 belongs to BCH(127,22,23). The recommendation moved to BCH(127,29,21) six
loops ago, whose leakage is 2,254 rather than 2,415 and whose floor is therefore 341. The
number did not follow the recommendation.

Corrected. Two things about it. The error had been in the ledger through every loop since
the recommendation changed, and no amount of reading would have found it - the figure is
plausible, sits in a sentence about a different code's properties, and is the *right* answer
to a question nobody was asking any more. And the check only caught it once its pattern
matched the prose: my first pattern looked for "the floor being N oscillators" where the
text says "oscillator floor is N oscillators", and it silently matched nothing. A check
whose pattern does not fire is a check that passes.

## 59. The end-to-end chain had been validating the wrong construction

`key_generator_e2e.py` was still built around BCH(127,22,23). The recommendation moved to
BCH(127,29,21) in loop 61, and the chain kept validating the older one for six loops -
including the Monte Carlo that gave the failure model its second witness.

The same drift as W-INTL-99, in a third place. Nothing in the file was wrong; it simply
described a construction the rest of the analysis had stopped recommending.

Repointed and re-run. The agreement holds on the new construction: at four percent bit error
rate the model predicts 1.7e-07 and 300 trials show none; at six percent 1.58e-04 against
none in 300; at eight percent 0.0107 predicted against 0.015 observed in 200. Keys round-trip
at zero and two percent noise at two bias levels.

So the model still has a second witness, and it is now a witness to the construction actually
being recommended.

Three instances of one drift class in a single loop - a factor lost between documents, a floor
that did not follow its code, and a chain validating a superseded design - and all three were
found by building the instrument rather than by looking harder. That is the argument for the
instrument.

One more, and it happened while writing this section. The extended check failed on the
paragraph above, because its guard tested whether the phrase "oscillator floor is" appeared
anywhere in a document and this section quotes that phrase while describing the failure
message. A guard looser than the pattern it protects reports failures for prose rather than
for arithmetic. Corrected by distinguishing the document that must state a figure from ones
that merely may, and both controls still fire - a wrong figure and a missing one. Eighth time
one of these checks has caught something in my own writing, and the first time it caught the
text describing itself.

---

## 59b. Every declared area re-synthesised

`scripts/verify_inputs.py` regenerates each decoder from `gen_bch_decoder.py`, synthesises both
halves against the same library, and compares the sum against what `inputs.py` declares. All
thirteen reproduce to within a square micrometre.

That closes the last hand-carried link. Until now the declarations said they were measured here
and reproducible, and nothing checked that a figure transcribed six loops ago still describes the
design rather than the design as it stood then.

## 60. The leakage bound is avoidable, and the paper saying so turned up while chasing a different question

Going after Becker's text - the last inherited claim in this work - led to Hiller's
dissertation, which cites it and is open access. Chapter 5 answers a question nobody here had
asked.

Read directly, not from an abstract. The chapter opens: previous work on secure key derivation
with PUFs is either able to achieve zero leakage or helper data capacity, and Systematic Low
Leakage Coding is the first practical approach to combine zero leakage with a helper data size
close to capacity. It later states that SLLC is currently the only deterministic scheme that
achieves the secret key and the helper data capacity, and also inherently ensures information
theoretic security.

The construction is simple enough to state. The response splits into an information part and a
mask. Redundancy is computed from the information part with a systematic encoder, and the
helper data is that redundancy exclusive-ored with the mask - **fresh PUF bits**. The thesis
gives the algebraic core as an upper triangular full-rank matrix and concludes that the mutual
information between secret and helper data is zero: no information leaks due to the structure
of the algebraic core.

**So the n-k leakage bound is a property of the constructions this project chose, not of the
problem.** Every code decision here since loop 53 rests on

    k_total >= 128 + n_total * (1 - rho)

and under SLLC there is no leakage term at all. The requirement is on entropy alone, because
the first k corrected bits are the key:

    k_total >= 128 / rho = 136

## 61. What that does to the numbers

The recommendation does not change yet, and almost everything else does.

| | Under the leakage bound | Under SLLC |
|---|---|---|
<!-- derived:external --> | blocks for BCH(127,29,21) | 23 | 5 |
<!-- derived:external --> | raw response bits | 2,921 | **635** |
<!-- derived:external --> | oscillators | 341 | 37 |
<!-- derived:external --> | tiles | 8.49 | **7.73** |

A factor of 4.6 in raw response bits. The area gain is modest because the decoder dominates,
but raw width is what the debiasing overhead multiplies and what the oscillator count follows,
so it is the more consequential number.

And it readmits what the leakage bound eliminated:

| Construction | Blocks | Raw bits | Oscillators | Tiles | Failure at 4 percent |
|---|---|---|---|---|---|
<!-- derived:external --> | rep[5] + RM[32,6,16] | 23 | 3,680 | 87 | **0.49** | 0 |
<!-- derived:external --> | rep[3] + RM[64,7,32] | 20 | 3,840 | 89 | 0.66 | 0 |
<!-- derived:external --> | BCH(127,29,21) | 5 | 635 | 37 | 7.73 | 3.7e-08 |

The concatenated Reed-Muller construction, withdrawn in loop 53 for negative residual entropy,
is admissible under SLLC and would be **the cheapest by a factor of twelve**.

The reason not to build it has changed rather than gone away. It is no longer leakage; it is
that Reed-Muller is corroborated as vulnerable to helper-data manipulation, and SLLC does not
address that - zero leakage is a statement about a passive adversary, and manipulation is an
active one. So the recommendation stands on the security property whose reasoning is still only
corroborated, which makes reading Becker's text more urgent rather than less.

## 62. Status of this finding, stated exactly

The primary source is read: chapter 5 of the dissertation, quoted above, not an abstract or a
summary.

The consequence for this project is **my derivation, not the thesis's**. The thesis does not
discuss this construction, these codes, or this tile budget. What I have done is take its stated
property - no leakage - and replace one term in an inequality. That is a small step and it is
still a step somebody else has not checked, and it overturns six loops of conclusions, which is
exactly the combination that has been wrong before in this work.

Three things I have not done. Verified that SLLC composes with a concatenated code, which needs
a systematic encoder for the concatenation rather than for each part. Checked what SLLC costs in
gates - the thesis has an implementation section and I have not measured it here. And checked
whether the mask bits being response bits changes the error-correction requirement; I believe
they do not, since the mask's errors land in the redundancy positions and the codeword still has
n error-prone positions, but that is a belief and it is load-bearing.

Until those are done this is a finding, not a decision. The numbers above are what would follow
if it holds.

---

## 63. SLLC implemented, tested, and measured: the finding becomes a decision

W-INTL-110 listed three things undone, all load-bearing. Two are now tests rather than beliefs
and the third is scoped out.

**Does the mask being response bits change the error-correction requirement?** No, and it is now
measured rather than reasoned. SLLC is implemented in full: the generator polynomial computed from
cyclotomic cosets, systematic encoding by long division, enrolment producing helper data as
redundancy exclusive-ored with fresh response bits, reconstruction unmasking and decoding.

Three things fell out of building it. The generator has degree 98, so k = 29 - a third
independent confirmation of the parameter table, arrived at from the generator rather than from
coset sizes. A systematic codeword has all syndromes zero and its first k bits equal the
information bits, which is the property SLLC requires and which had been assumed. And recovery
succeeds at every error rate tested, with the observed failures tracking the same binomial model
over n positions:

| Bit error rate | Trials | Recovered | Model |
|---|---|---|---|
<!-- derived:external --> | 0.00 | 30 | 30/30 | 0 |
<!-- derived:external --> | 0.02 | 60 | 60/60 | 6.9e-14 |
<!-- derived:external --> | 0.04 | 200 | 200/200 | 3.7e-08 |
<!-- derived:external --> | 0.08 | 120 | 120/120 | 2.3e-03 |

635 raw response bits over five blocks, against 2,921 over twenty-three under the leakage bound.

**What does SLLC cost in gates?** Measured on the same library. The systematic encoder is a
linear feedback shift register of degree 98 with fifty taps, at 3,887 square micrometres, and it
is needed at enrolment only. Reconstruction adds nothing but an exclusive-or of 98 bits, at 858.
Both on die is 4,745 - six percent of the decoder.

**Does SLLC compose with a concatenated code?** Not answered, and not needed. The recommendation
is a single BCH code, so the question does not arise for it; it arises only for the Reed-Muller
alternative, which helper-data manipulation rules out independently. Recorded as out of scope
rather than as open, which is a different thing.

## 64. The payoff is not area, it is that one constraint dissolves

The area gain is small. Without debiasing the budget moves from 8.49 tiles to 8.18 - three
percent, because the decoder dominates and SLLC adds six percent of one.

The gain is elsewhere:

| Construction | Debiasing | Raw bits | Reuse | Disjoint |
|---|---|---|---|---|
<!-- derived:external --> | leakage bound | none | 2,921 | 8.49 | 22.33 does not fit |
<!-- derived:external --> | leakage bound | 2O-VN | 6,368 | 9.45 | 39.68 does not fit |
<!-- derived:external --> | SLLC | none | 635 | 8.18 | 11.28 |
<!-- derived:external --> | SLLC | 2O-VN | 1,384 | 8.23 | **15.05** |

**Under SLLC every combination fits, including debiasing with two oscillators per response bit.**

That dissolves W-INTL-67, which found that debiasing turned the oscillator arrangement from a
factor-of-two question about area into a question of fitting at all, and W-INTL-68, which
concluded from the whole method table that oscillator reuse was a requirement rather than an
optimisation. Both were correct under the leakage bound. Under SLLC the arrangement is a
preference again.

The register's fifth row - bias and debiasing, binding conditionally - moves to slack. That is
two binding constraints removed by one construction: the leakage term itself, and the
arrangement question that the leakage term's raw-width penalty created.

So the finding is a decision for the recommended construction. SLLC should be used, at six
percent more decoder area, for 4.6 times fewer response bits and one fewer binding constraint.

---

## 65. The leakage bound, confirmed first-hand, and an escape I never considered

Going back into the dissertation for the helper-data manipulation question turned up chapter 4,
which contains a first-hand comparison of the four state-of-the-art constructions. Two things
follow, and the first is reassuring.

**The syndrome construction leaks n-k.** Table 4.2 gives the mutual information between secret
and helper data for a nearly perfect PUF as n-k for the syndrome construction. That is the bound
every code decision here has rested on since loop 53, sourced second-hand from Gao et al. and now
confirmed in the primary literature. It was right.

**And Fuzzy Commitment has zero leakage, and has since 1999.** The same table gives its rank loss
as zero and its leakage as below epsilon-nought. So SLLC is not the only escape from the bound, and
last loop over-credited it as the discovery.

| Scheme | Helper bits | Leaks | Needs a random number |
|---|---|---|---|
<!-- derived:external --> | Syndrome | n-k | n-k | no |
<!-- derived:external --> | Fuzzy Commitment | n | about 0 | yes |
<!-- derived:external --> | SLLC | n-k | 0 | no |

SLLC is best on paper - zero leakage at the smallest possible helper data, with no random number.
But Fuzzy Commitment is the most widely deployed scheme in the field, it has been available for
the whole life of this problem, and this project never considered it. Twelve loops of analysis
took the leakage term as given when the oldest construction in the table does not have it.

The thesis also places SLLC exactly, which is worth recording because it makes the idea less
surprising and more trustworthy. The Parity Construction stores the parities of the response with
a systematic code and leaks 2k-n. **SLLC is that construction with the parities masked by fresh
response bits.** It is not a new mechanism bolted on; it is the one scheme in the table repaired.

## 66. Under zero leakage the entropy density stops mattering

Rebuilt with the leakage term removed - the requirement becoming k_total >= 128/rho, met by
adding blocks:

```
                  4%     5%     6%     7%     8%     9%    10%
  rho 1.00    8.18  8.87 10.36 10.36 11.74     -     -
  rho 0.94    8.18  8.88 10.37 10.37 11.75     -     -   <- measured
  rho 0.90    8.18  8.88 10.37 10.37 11.75     -     -
  rho 0.80    8.19  8.89 10.38 10.38 11.75     -     -
  rho 0.70    8.20  8.89 10.39 10.39 11.77     -     -
  rho 0.60    8.20  8.90 10.40 10.40 11.78     -     -
  rho 0.50    8.21  8.91 10.41 10.41 11.80     -     -
```

**The entropy density stops being a constraint.** Halving it, from 1.00 to 0.50, moves the budget
by three hundredths of a tile. The cliff at 0.7986 that W-INTL-86 located, the margin of 0.0065
that W-INTL-72 called the tightest number in the work, the flat band and its edge in W-INTL-82 and
W-INTL-84, the reversal of priority in W-INTL-85 - all of it was a property of the syndrome
construction's leakage term.

The reason is simple once the term is gone. A lower entropy density needs more blocks, and blocks
are processed sequentially by the same decoder, so more of them cost nothing in area. Only the
oscillator count grows and that is a small term. Under the leakage bound each extra block also
added n-k bits of leakage, which is what made the density bind.

So the error rate is now the only binding input. Eight percent fits at 11.75 tiles and nine does
not, at every entropy density from a half upwards.

Six loops of sensitivity analysis, three reversals of priority, and a register row marked as the
tightest figure in the work - all correct, all conditional on a construction chosen in loop 53
without asking whether its leakage was avoidable. That question took one hour when it was finally
asked.

---

## 67. You do not have to correct the errors. You can skip them.

Chapter 6 of the dissertation contains the comparison table this analysis has been
reconstructing for twelve loops. Every row is for an SRAM PUF at **fifteen percent** average bit
error probability, a 128-bit key and a key error rate of one in a million:

| Scheme | PUF response bits | Helper data bits | Slices |
|---|---|---|---|
<!-- derived:external --> | Code-Offset Golay | 3,696 | 3,824 | 907 or more |
<!-- derived:external --> | Code-Offset RM-GMC | 1,536 | 13,952 | 237 |
<!-- derived:external --> | C-IBS RM | 2,304 | 9,216 | 250 |
<!-- derived:external --> | DSC convolutional | 1,224 | 2,176 | 262 |
<!-- derived:external --> | compressed DSC convolutional | 1,224 | 1,224 | 272 |
<!-- derived:external --> | **compressed DSC Seesaw** | **974** | **1,108** | 249 |

This project, at less than half that error rate, needed 2,921 response bits under the syndrome
construction and 635 under SLLC - and concluded that nine percent and above was impossible.

**Differential Sequence Coding reaches fifteen percent with 974 bits because it does not correct
the errors.** It indexes the reliable bits and skips the rest, storing compressed pointers to
them as helper data. The thesis states the arithmetic directly: the target bit error probability
is reached with a maximum of 0.027 by indexing on average 32.6 percent of the available PUF bits.
Fifteen percent raw becomes 2.7 percent effective, and then a modest code suffices.

Every construction evaluated here assumed all n positions must be corrected. **That assumption
is the error-rate constraint** - the one input still binding after SLLC removed the leakage term -
and it was a choice, not a requirement.

One thing already right: reliable-bit selection needs per-bit reliability, which means repeated
measurements at enrolment. The characterisation structure built in section 20 emits raw frequency
counts per oscillator rather than response bits, precisely so that any downstream decision could
be made off the die. Reliability selection is such a decision, and the instrument for it already
exists.

## 68. The helper-data manipulation question had a generic answer all along

W-INTL-105 has been open for four loops as corroborated but unverified: whether syndrome-based BCH
is immune to helper-data manipulation, resting on a second-hand summary of a paper behind a
paywall. The recommendation was standing on it.

Chapter 6 answers a different and better question. From the implementation section: the helper
data is hashed onto the output of the decoder to prevent helper-data manipulation attacks, using
SPONGENT as a lightweight hash, so that 88 key bits are affected by each helper data bit and the
key is corrupted as soon as the helper data is manipulated. Chapter 4 gives the same
countermeasure generically as **K = S xor f(W)** - hash the helper data and fold it into the key.

**So the code choice never turned on manipulation immunity.** There is a generic countermeasure,
it is a lightweight hash, it is independent of the code, and it was in the same document as
everything else this project has been reading for three loops.

That closes the last inherited claim, and it closes it better than verifying Becker would have.
Verification would have told me whether one construction is immune. This tells me the question
does not need to be asked, provided the helper data is hashed into the key - which it currently is
not, in any design considered here.

## 69. Three loops running, the primary literature has removed a constraint I treated as fixed

Worth stating plainly, because the pattern is now the finding.

Loop 69 found that the leakage term was a property of the construction chosen, not of the problem.
Loop 71 found that the oldest construction in the field never had that term, and that removing it
makes the entropy density - the figure called the tightest in this work - stop mattering. This
loop finds that the error rate, the last binding input, rests on the assumption that all errors
must be corrected, and that the standard alternative does not make it.

Each was one table or one section in a document already cited. Twelve loops of careful
measurement, three reversals of priority, a constraint register, and four instruments that check
each other - all of it operating inside a framing that a comparison table would have shown was one
of several.

The measurements survive. Thirteen decoders are still correctly measured, the checks still run,
and the end-to-end chain still agrees with the model. What does not survive is any claim that the
analysis found the best construction, because it never compared framings - only codes within one.

---

## 70. There are two families and this session only looked at one

Recorded as W-INTL-121, and to be read alongside W-INTL-118, produced in parallel by the cloud
routine, which measures the selection mechanism at this project's own error rate and finds that it
transfers while its advantage does not.

Chapter 3 of the dissertation is the map of framings this analysis never had. Its conclusion is
one sentence: there are two main families of syndrome coding schemes for PUFs, linear approaches
and pointer-based approaches.

Every construction evaluated across twelve loops - Fuzzy Commitment, Code-Offset, Syndrome,
Parity, SLLC - is in the **linear** family. The pointer-based family was never examined.

What is in it, from section 3.4:

**Index-Based Syndrome Coding.** The response is divided into blocks and, within each block, the
bit that matches the intended codeword bit with highest probability is indexed; the pointer goes
into the helper data. Two properties follow, and the thesis states both. It performs error
reduction by selecting response bits of higher than average reliability. And **for i.i.d. PUF
bits the pointers are uncorrelated with the code sequence, so no information leaks through the
helper data**.

So the pointer family gets zero leakage by construction - not by masking as SLLC does, nor by a
random number as Fuzzy Commitment does, but because a pointer to a reliable bit says nothing
about the bit's value.

**Complementary IBS**, Hiller's own earlier work, fixes IBS's inefficiency: IBS ignores the
majority of response bits, so C-IBS adds an intermediate encoding step to use more of them.

**Maximum-Likelihood Symbol Recovery** indexes an entire response block rather than single bits,
and the thesis says it is **especially suited for PUFs with bit error probabilities greater than
twenty percent**. This project concluded nine percent was impossible.

And the counterweight, which the same section supplies and which matters here more than
anywhere. The output bits of a ring-oscillator sum-PUF are not fully independent, and IBS helper
data can be attacked with machine learning on that basis. So the pointer family is not simply
better: it trades a leakage-and-correction problem for a modelling problem, and this project's
source is the type where that attack was demonstrated.

That is the honest shape of the finding. Not that twelve loops backed the wrong family, but that
they backed one of two without knowing there were two, and the second has a different failure
mode that happens to be aimed at ring oscillators.

## 71. The countermeasure is implemented and tested

W-INTL-116 and W-INTL-120, and now closed by W-INTL-122, turned four loops of an open security question into a missing component: fold the
helper data into the key, K = S xor f(W), so that touching the helper data corrupts the key.
Absent from every design here.

Present now, in `research/sllc_key_generator.py`, and tested on the property it exists for:

| Check | Result |
|---|---|
<!-- derived:external --> | honest reconstruction at two percent noise recovers the key | 60/60 |
<!-- derived:external --> | one flipped helper-data bit changes the key | 60/60 |

The second line is the point. A manipulated helper data must not yield the enrolled key whatever
the decoder does with it, and folding the helper data into the key achieves that without
depending on the code at all.

Cost, from the thesis rather than measured here: SPONGENT in its smallest configuration returning
an 88-bit hash takes 85 slices on a Spartan-3E with 117 registers and 153 lookup tables. Not
synthesised on this library, so it is a borrowed figure and labelled as one - but it is a
lightweight hash and the decoder it sits beside is 249 slices in the same table, so the order of
magnitude is settled even if the number is not.

---

## 72. Selection paired with BCH, which is the bound the parallel routine left open

W-INTL-118, written in parallel by the cloud routine, measured reliable-bit selection against
repetition and stated its own bound explicitly: the source pairs selection with a convolutional
code, only repetition was measured, and a stronger inner code could reverse the conclusion.

Paired with the BCH codes whose decoders are measured here, reusing the routine's selection model
rather than rebuilding it - that model is already validated against a 120,000-position sample to
within half a thousandth:

| Raw error rate | Ranking | Fraction kept | Effective | Code | Raw positions | Tiles |
|---|---|---|---|---|---|---|
<!-- derived:external --> | 6 percent | 9 reads | 80 percent | 0.0133 | BCH(127,29,21) | 794 | 8.19 |
<!-- derived:external --> | 10 percent | 9 reads | 80 percent | 0.0466 | BCH(127,29,21) | 794 | 8.19 |
<!-- derived:external --> | 15 percent | 9 reads | 40 percent | 0.0374 | BCH(127,29,21) | 1,588 | 8.23 |

**Nine enrolment reads, one code, and about 8.2 tiles at every error rate from six to fifteen
percent.** Without selection: 10.37 tiles at six percent, 26.33 at ten which does not fit, and
nothing fits at fifteen.

So the reversal the routine predicted happens. Its conclusion was correct for repetition and does
not hold for BCH.

Two things this does not do. It does not use perfect ranking - the figures above are from a finite
enrolment budget, which is the routine's own W-INTL-119 caveat honoured rather than discarded. And
at one enrolment read selection makes things **worse**: 0.0823 effective against 0.0600 raw at six
percent, because ranking on a single noisy measurement selects for what the noise did rather than
for what the device is.

## 73. A correction to the parallel routine's comparison

W-INTL-118 compares selection plus repetition at 1,211 to 1,765 response bits against SLLC needing
635 at the same rate. The 635 is five blocks of BCH(127,29,21), and at six percent raw that
construction gives a word failure rate of 3.44e-05 against a target of one in a million. It does
not meet the target there - 635 is the figure for four percent, where that code tolerates up to
4.42 percent.

SLLC at six percent needs the next stronger code, BCH(127,15,27), at ten blocks and 1,270 response
bits.

So the comparison is 1,211 to 1,765 against 1,270 - roughly a tie rather than a loss - and
selection paired with BCH needs 794, which wins outright.

The routine's mechanism measurements stand: the selection model, the 0.150 to 0.0066 figure, the
agreement with a 120,000-position sample, and the enrolment-cost curve are all used above. What
was wrong was one figure carried across from a different operating point, which is the same class
as W-INTL-107 and W-INTL-99 - a number that did not follow the condition it was computed under.

Worth noting how it was found: two agents on the same prompt, one checking the other's arithmetic
against its own stated conditions. Neither would have caught it alone, because each was reading
its own figure as familiar.

## 74. What is left

With selection the error rate stops constraining the design and only sets how many raw positions
must be available - 794 at six percent, 1,588 at fifteen. Oscillators are cheap, so the whole map
that took six loops collapses to one answer of about 8.2 tiles.

That leaves, from the register: the pointer-based family still unexamined as a whole (W-INTL-121),
the SPONGENT cost still borrowed rather than measured, and the enrolment procedure - nine reads per
position - now a stated requirement on the provisioning flow rather than an implementation detail.

---

## 75. The countermeasure's cost, measured rather than borrowed

The helper-data manipulation countermeasure was the last figure in this project taken from a paper
rather than measured here - 85 slices on a Spartan-3E, a different technology on a different
process. It is now load-bearing, since it is what makes the code choice independent of manipulation,
so the borrowed number was the wrong thing to leave in place.

SPONGENT-88/80/8's permutation implemented and measured on this library: the round function 2,215
square micrometres, the full permutation with its state and round counter 6,215. That is 7.8 percent
of the decoder, against SLLC's 6.0, and it moves the budget from 8.19 tiles to 8.79 at six percent
raw error, or 8.23 to 8.83 at fifteen.

What is verified and what is not, stated because the distinction is the whole value of measuring it
here. The S-box and the bit permutation are each checked bijective at generation. The testbench
measures avalanche - the property the countermeasure actually relies on - and one input bit changes
a mean of 46.5 of 88 output bits over 24 trials, range 36 to 52, against an ideal of 44. Two
injected faults fail it: two rounds instead of forty-five gives a mean of 6.2, and an identity
S-box gives exactly 1.

There are no official test vectors in hand, so this is not verified to *be* SPONGENT rather than a
SPONGENT-shaped permutation of the same structure and cost. The area figure is what it is measured
for, and it is measured on the right library for the first time.

The identity-S-box control is worth keeping for a second reason. Exactly one output bit changes,
which is the concrete form of why a linear diffusion function will not serve: an attacker who flips
a helper-data bit learns the key change exactly and can compensate. Earlier in this work an
LFSR-based mixer looked like a cheaper way to get the same diffusion. It would have been cheaper and
useless, and the control says so in one number.

## 76. The enrolment procedure is a requirement now, not an implementation detail

Reliable-bit selection needs to know which positions are reliable, and it learns that by reading
each position several times at enrolment. The figures in section 72 use nine reads, and the number
is not incidental: at one read selection makes the error rate worse than not selecting, at nine it
gives 0.0133 effective from 0.0600 raw, and at twenty-five 0.0104.

So nine reads per position is a constraint on the provisioning flow, and it has not appeared in any
document in this project. Stated here:

**Enrolment requires reading every candidate position at least nine times, at the operating
temperature, before the reliable subset is chosen.** Fewer reads do not degrade the design
gracefully - at one read the selection is counterproductive.

Two consequences worth naming. Provisioning time is nine sweeps of the oscillator bank rather than
one, which at the characterisation structure's 448 cycles per sweep is negligible in absolute terms
but is a step the flow must contain. And the reads must be at the temperature the device will
operate at, or the reliability ranking is of the wrong quantity - which is the same point the
literature makes about pairs whose ordering reverses as the die warms.

---

## 77. The pointer family, costed against the linear one

W-INTL-121 has been the only open critical entry: the field has two families and this work examined
one. Costed now, for the same code and key.

Index-Based Syndrome Coding removes helper-data leakage differently from SLLC. SLLC masks the
redundancy with fresh response bits; IBS makes the helper data a pointer to a position, and for
i.i.d. bits a pointer says nothing about the value it points at. Both give zero leakage; the
question is what each costs.

| Scheme | Positions | Oscillators | Extra logic | Helper bits | Tiles |
|---|---|---|---|---|---|
<!-- derived:external --> | SLLC | 635 | 41 | 4,745 | 490 | 8.79 |
<!-- derived:external --> | IBS, block of 4 | 2,540 | 72 | **581** | 1,270 | **8.47** |
<!-- derived:external --> | IBS, block of 8 | 5,080 | 102 | 623 | 1,905 | 8.55 |

The pointer datapath is eight times smaller than the masking machinery - one counter, one comparator
and a register against a degree-98 encoder - and pays for it in positions, needing four times as
many. Net, the pointer family comes out 0.32 of a tile ahead.

**And it should still not be used here.** IBS needs a random codeword to point at, so it needs a
random number source that SLLC does not. And the literature records that ring-oscillator sum-PUF
outputs are not fully independent and that IBS helper data can be attacked with machine learning on
exactly that basis. So the trade is 0.32 of a tile against a new attack surface aimed at this
project's source type.

That is a recommendation rather than a finding, and it is the first time in this work that a
measured advantage has been declined. Worth stating plainly because the arithmetic says otherwise.

## 78. What the 8.79 tiles are made of

The budget has been assembled across twenty sections and never shown as one table. Every component
measured on this library:

| Component | Area | Share |
|---|---|---|
<!-- derived:external --> | BCH(127,29,21) decoder, three stages | 79,787 | 86.9 percent |
<!-- derived:external --> | SPONGENT permutation, the manipulation countermeasure | 6,215 | 6.8 percent |
<!-- derived:external --> <!-- derived:external --> | SLLC encoder and unmask | 4,745 | 5.2 percent |
<!-- derived:external --> | 41 ring oscillators at 26.3 square micrometres | 1,077 | 1.2 percent |
| **cell area** | **91,824** | |
| die area at 57.95 percent utilisation | 158,446 | |
| **tiles of sixteen** | **8.79** | |

One thing falls out of seeing it in one place. **The decoder is 87 percent of the design and the
oscillators are 1.2 percent.** Six loops went into the oscillator side of the budget - the
arrangement question, the entropy floor, the debiasing overhead, the pairing scheme - and all of it
was optimising a term worth about a hundredth of the total.

Those loops were not wasted, because the oscillator side is where the *constraints* lived: the
entropy density and the error rate decided which code was admissible, and the code is 87 percent of
the area. But the effort went into refining a small term while the large one was settled early and
revisited only when a paper forced it. Sorting the budget by share is a cheap thing to do and it
would have said so at any point.

---

## 79. Sharing the multipliers, which is where the 87 percent was

Section 78 observed that the decoder is 87 percent of the design and that six loops had gone into
the 1.2 percent. This acts on that.

The key-equation solver instantiates 3(t+1) general multipliers - 66 at t=21 - and is 57,571 of the
decoder's 79,787 square micrometres. That count is right for a communications decoder, which needs a
codeword per symbol time. A key generator runs once at power-up and may take as long as it likes.

Rewritten with two multipliers shared across cycles instead of sixty-six in parallel:

| Form | Multipliers | Area | Cycles |
|---|---|---|---|
<!-- derived:external --> | parallel | 66 | 57,571 | one per iteration |
<!-- derived:external --> | serial | 2 | **22,131** | about 1,850 in total |

Sixty-two percent of the solver, for 185 microseconds once at power-up on a ten megahertz clock.

Verified differentially rather than against a re-derived expectation: the same syndromes into both
solvers, and the locator and its degree must match. Every error weight from one to twenty-one, two
patterns each, forty-two cases, all matching. An injected fault in the serial version alone - the
length condition weakened - fails all forty-two.

Two implementation notes worth keeping. The first version registered the multiplier operands and
used the product in the same cycle, so every product reflected the previous cycle's operands; the
differential test caught it immediately, which a same-cycle inspection would not have. And the
update now lands in a shadow array committed in one step, so that the discrepancy phase reads a
consistent locator rather than one being rewritten underneath it.

## 80. The budget after it

| Component | Parallel | Serial |
|---|---|---|
<!-- derived:external --> | decoder, three stages | 79,786 | 44,346 |
<!-- derived:external --> | SLLC encoder and unmask | 4,745 | 4,745 |
<!-- derived:external --> | SPONGENT permutation | 6,215 | 6,215 |
<!-- derived:external --> | 41 ring oscillators | 1,077 | 1,077 |
<!-- derived:external --> | cell area | 91,823 | 56,383 |
| **tiles of sixteen** | **8.79** | **5.40** |

**3.39 tiles, thirty-nine percent of the design, from one change to the component that was
eighty-seven percent of it.**

That is the largest single reduction in this work, and it came from sorting the budget by share one
loop ago rather than from any new measurement or paper. The technique was available from the start:
the solver's own header has said since it was written that a systolic reformulation exists and that
timing is not closed, and the observation that latency is free here has been in the constraint
register as slack since power and timing were checked. Nothing was learned this loop that was not
already written down; what changed was looking at which term was large.

---

## 81. The same trade applied to the Chien search, and it loses

Section 79 took thirty-nine percent off the design by sharing the solver's multipliers. The obvious
next step was the table stages, now half the decoder at 22,215 square micrometres - the syndrome bank
13,258 and the Chien search 8,906.

Implemented, verified differentially against the parallel Chien on six locators, an injected fault
failing all six, and measured: **13,129 square micrometres against 8,906. Forty-seven percent
larger.**

The reason is exact.

| Form | Multipliers | Kind | Logic |
|---|---|---|---|
<!-- derived:external --> | parallel | 22 | constant, fixed XOR trees | 5,823, about 265 each |
<!-- derived:external --> | serial | 1 | general, both operands variable | about 10,050 including addressing |

Removing twenty-one cheap units saves about 5,550. The shared general unit, plus the addressing to
read and write an indexed array of twenty-two entries, costs about 10,050. The trade loses by 4,223.

The solver was the opposite case. Its replicated units were *general* multipliers - the same kind as
the shared one - so sharing removed sixty-four of sixty-six at no change in unit cost, and the
addressing it added was cheaper than the arithmetic it removed.

**So the predictor is not the logic share.** The Chien search is 65 percent logic and does not
compress; the solver was 84 percent logic and compressed by 62. What decides it is whether the
replicated unit costs more than the shared unit plus its addressing. Replicating something cheap is
already the efficient arrangement.

The same reasoning rules out the syndrome bank without implementing it: forty-two constant
multipliers, cheaper still per unit, and serialising would additionally require storing the received
word - another 127 flip-flops - because the parallel accumulators consume the input stream
simultaneously and a shared one would have to re-read it. Recorded as excluded by argument rather
than left as an open option.

The decoder therefore stands at 44,346 square micrometres and the design at 5.40 tiles. The table
stages are at their floor for this technique.

My own header for the serial Chien predicted a smaller saving than the solver's, for the right
reason - a general multiplier costs more than the constant one it replaces. It predicted the sign
wrong. Writing the reason down before measuring made the negative result immediately interpretable
rather than confusing, which is most of what that habit is for.

---

## 82. The code was chosen before selection existed

Reliable-bit selection arrived in loop 74 and made the effective error rate 0.0127 where the raw rate
is six percent. The code was chosen in loop 61 against the raw rate. It was never revisited.

BCH(127,29,21) tolerates 4.42 percent and is being asked to survive 1.27. Re-searched at the rate
that actually applies:

| Code | t | Blocks | Selected bits | Word failure | Measured before |
|---|---|---|---|---|---|
<!-- derived:external --> | BCH(127,57,11) | 11 | 3 | 381 | 2.94e-07 | no |
<!-- derived:external --> | BCH(127,50,13) | 13 | 3 | 381 | 3.44e-09 | no |
<!-- derived:external --> | BCH(127,43,14) | 14 | 4 | 508 | 4.42e-10 | no |
<!-- derived:external --> | BCH(127,29,21) | 21 | 5 | 635 | 0 | yes |

Every code that fits the operating point was unmeasured, and every measured code at n=127 has t of
21 or more - all chosen when high error tolerance was needed. The measured set was built for an
operating point that no longer applies, so the search could only return the best of the wrong
candidates.

Generated, verified end to end and differentially, and measured:

| Construction | Decoder | Raw positions | Oscillators | Cell area | Tiles |
|---|---|---|---|---|---|
<!-- derived:external --> | BCH(127,29,21), 5 blocks | 44,346 | 794 | 41 | 56,383 | 5.40 |
<!-- derived:external --> | BCH(127,50,13), 3 blocks | 28,958 | 477 | 35 | 40,838 | 3.91 |
<!-- derived:external --> | **BCH(127,57,11), 3 blocks** | **24,659** | **477** | 35 | **36,539** | **3.50** |

Leakage checked first, since the code changed: k total is 57 times 3, which is 171 against the 136
required.

## 83. Two loops, two revisits, and the same shape

| Loop | Change | Tiles |
|---|---|---|
<!-- derived:external --> | 76 | as it stood | 8.79 |
<!-- derived:external --> | 77 | shared the solver's multipliers | 5.40 |
<!-- derived:external --> | 79 | re-chose the code at the operating point | 3.50 |

**Sixty percent of the design removed in two loops, and neither required a new measurement technique,
a new paper, or a new constraint.** Both were decisions correct at the operating point where they were
made, in a design whose operating point had since moved - the solver's multiplier count assumed a
throughput requirement this has never had, and the code assumed an error rate that selection had since
reduced by a factor of five.

The constraint register was supposed to catch this and could not. It records what each constraint is
and whether it binds; it does not record which decisions were taken against which constraint. When a
constraint moves, nothing points at the decisions that rested on it.

---

## 84. Selection was assumed to be free in entropy, and the check ran inside the assumption

Reliable-bit selection publishes which positions were kept. The file that introduced it states
why that is safe:

> The reliability of a position is |d|, and it is independent of the bit value sign(d) because the
> distribution of d is symmetric. That independence is the whole reason pointers to reliable
> positions can be published: they say which positions are stable, not what they hold. It is a
> property of this source, and it is checked below rather than assumed.

It is not checked. Every sampler in that file draws `d = rng.gauss(0, 1)` - mean zero, bias exactly
one half - and the check reports a value share of 0.5000 because the sampler was told to produce
one. The symmetry that makes the independence true is a parameter of the model, and the check runs
inside it. This is the broken-ruler error at the level of a source model rather than a signal.

The measured source is not symmetric. The entropy input is 241.0 bits in 256 positions, which is a
bias of 0.5207. And the survey this project deferred reading for five loops states the consequence
in its abstract:

> We disprove the intuitive assumption that bit selection schemes have no leakage.

Their section VII treats four selection schemes. The one used here, global thresholding, is the
worst of the four on exactly this axis - "the larger Loss, the more bias amplification. Global
thresholding amplifies bias the most" - and the pointer family costed in section 77 is the one that
does not: "IBS and C-IBS do not amplify bias [...] Rather the opposite: they remove all bias."

### How much

Computed in this project's own source model, in closed form and by two samplers - one ranking by the
true reliability, one by the nine-read majority vote the design actually performs:

| Discarded | Threshold | Bias | Sampled | Vote-ranked | Density |
|---|---|---|---|---|---|
<!-- derived:external --> | 0% | 0.0000 | 0.5207 | 0.5209 | 0.5226 | 0.9414 |
<!-- derived:external --> | **20%** | 0.2537 | **0.5251** | 0.5247 | 0.5249 | **0.9293** |
<!-- derived:external --> | 40% | 0.5251 | 0.5301 | 0.5306 | 0.5247 | 0.9157 |
<!-- derived:external --> | 67.4% | 0.9835 | 0.5392 | 0.5423 | 0.5236 | 0.8911 |
<!-- derived:external --> | 90% | 1.6471 | 0.5534 | 0.5556 | 0.8535 | 0.8535 |

The **density after selection is 0.9113** at the 45.6 percent the design now discards, against 0.9414
before it. The requirement rises from 136.0 bits of k to 137.7, against 171 carried. The
recommendation survives with thirty-three bits of margin.

The vote-ranked column stops tracking the closed form beyond about a third discarded, and the reason
is worth keeping: nine reads give five distinct reliability levels, so once the split-vote positions
are gone the ranking is arbitrary and discarding more neither improves the error rate nor amplifies
the bias further. The coarseness that caps the benefit also caps the cost.

### The design one loop ago did not survive it

| Design | k | 20% | 67.4% | 80% | 90% |
|---|---|---|---|---|---|
<!-- derived:external --> | BCH(127,29,21) x 5 (loop 78) | 145 | +7.3 | +1.4 | FAILS | FAILS |
<!-- derived:external --> | BCH(127,57,11) x 3 (loop 79) | 171 | +33.3 | +27.4 | +24.6 | +21.0 |

Margin in bits of k. The previous design fails the leakage bound at the deeper selection fractions
the analysis was itself quoting, and had 1.4 bits of margin at the fraction borrowed from the
literature. It was never noticed because the source model had no bias to amplify.

The re-choice in section 82 took the leakage margin from nine bits to thirty-three as a side effect
of choosing for area. That is luck, not method, and it is the second time in three loops that a
constraint was met by an accident of a decision taken for another reason.

`scripts/check_figures_reproduce.py` now recomputes the post-selection density from inputs and fails
if the recommendation's k does not cover it.

## 85. Two numbers in the right place in the wrong dictionary

The re-choice in section 82 entered 24,659 and 28,958 into `DECODER_AREA`. Both were measured
correctly. Neither belonged there: every other entry in that dictionary is the table stages plus the
*replicated* solver, and these two were the table stages plus the *shared* one. The verifier
synthesises what the dictionary says it holds, so it measured 42,069 against a declared 24,659 and
reported a mismatch of seventeen thousand square micrometres in a figure that was not wrong.

The gate caught it. It caught it one loop late, because the previous loop reported gates green
having run `check_consistency` and not `verify_inputs` - the slowest of the three, and the only one
that would have fired. A gate that is not run is not a gate, and "gates green" is a claim about which
gates.

Fixed by naming the two conventions rather than merging them: `DECODER_AREA` holds the replicated
solver, `DECODER_AREA_SERIAL` holds the shared one, `decoder_area(m, t)` returns what the design
would actually pay, and the verifier now checks both tables. It also counted twenty declared areas
where it used to say fifteen, having only ever counted the first table.

`measure_all.sh` had drifted the same way. It is the script that exists so every quoted figure can be
reproduced in one run, and it did not build the recommendation: no end-to-end decode at t=11 or
t=13, and no differential test of the shared solver against the replicated one, though the testbench
for it has been in the repository since loop 77. Three testbench entries and five area probes added;
all seventeen pass, and the two figures the headline rests on now come out of the same run as the
rest.

Still open, and named rather than fixed: `check_figures_reproduce.py` recomputes its headline from
`cheapest(RHO, 0.04)` - a construction with no SLLC, no selection and a three-thousand-bit raw
budget. That is the design as it stood eight loops ago. The ledger states 8.49 tiles and the check
recomputes 8.49 tiles, and they agree because both are anchored to the same superseded operating
point. The check written to stop documents drifting from the model is itself pinned to an old model.
The new selection-entropy guard in the same file is anchored to the current one, which is the shape
the rest of it should take.

## 86. The masking stage was sized for the code it was written for

SLLC was implemented in loop 63 for BCH(127,29,21). Its systematic encoder is a shift register whose
degree is n-k, so for that code it is 98 stages and forty-nine taps, transcribed by hand. The
recommendation has been BCH(127,57,11) since loop 79, whose generator has degree 70.

The budget has been paying for a 98-stage encoder to protect a code that needs 70. The error is in
the conservative direction, which is why nothing caught it: an overestimate cannot fail a fit check.

Two other things were wrong with the same component. It had no testbench - the area had been quoted
for five loops in a project whose rule is that no area is quoted for a circuit that has not been
exercised, and whose measure_all.sh refuses to print areas when a testbench fails. And the number
was a bare literal in one analysis script, in a project that moved every other input into inputs.py
after W-INTL-99 for precisely this reason.

`gen_sllc.py` now computes the generator polynomial from the cyclotomic cosets of alpha^1..alpha^2t,
the same machinery `gen_bch_decoder.py` uses for its constants, so the taps are a consequence of the
code rather than a transcription of it. Two independent confirmations that it is right: the degrees
it produces are 70, 77 and 98 for t of 11, 13 and 21, which are exactly the n-k of the codes used
throughout; and its t=21 output reproduces the hand-written file to within one square micrometre.

| Stage | BCH(127,57,11) | BCH(127,29,21) |
|---|---|---|
<!-- derived:external --> | systematic encoder | 2,562 | 3,887 |
<!-- derived:external --> | unmask | 613 | 858 |
<!-- derived:external --> | **total** | **3,176** | **4,746** |

The design goes from 3.50 tiles to **3.35**. Cell area 34,970: decoder 24,659, SLLC 3,176,
countermeasure 6,215, oscillators 920.

## 87. The check that pinned a document to a model eight loops old

`check_figures_reproduce.py` existed because prose and script had once been wrong together, sharing
a missing step. It recomputed the headline from `cheapest(RHO, 0.04)`: no SLLC, no selection, a
three-thousand-bit raw budget - the design as it stood in loop 61. The ledger stated 8.49 tiles and
the check recomputed 8.49 tiles, and they agreed because both were anchored to the same superseded
construction.

That is worse than having no check. No check leaves a document unverified; this one reported green
while the document described a design that had been replaced four times.

Repointed. The headline now comes from what the recommendation is: selection at the design's
fraction, the post-selection density, SLLC sized to the code's own generator, the countermeasure,
and the shared-multiplier solver. `cheapest()` is kept for one job - it is the arrangement in which
the utilisation factor was dropped, so it still guards that - and is no longer the source of any
figure a document has to match.

Ledger row E31 rewritten to the construction that exists, with the movement recorded: 8.79 tiles,
then 5.40 by sharing multipliers, then 3.50 by re-choosing the code, then 3.35 by sizing the encoder
to its own code. **Sixty-two percent removed in four loops, none of it by a new technique or a new
source.** Every step revisited a decision that had been correct at the operating point where it was
made.

## 88. Two loops of status rows that were never written

Loops 79 and 80 both added rows to the audit's status table with a string replacement whose anchor
was not in the file. `str.replace` returns the string unchanged when it finds nothing, so both edits
reported success, both commit messages described the rows, and neither row existed.

`check_consistency` said so both times - as a note rather than a failure, in a list that grew by two
entries a loop for four loops. It was read as furniture.

Twenty-seven entries added to the status table. Every anchored replacement this loop asserts its
anchor first. The general shape is that a silent no-op is worse than an error, because the commit
message then describes work the diff does not contain; and this project's three checks compare
documents against each other and against the model, but nothing compares a commit message against
its diff.

## 89. Two advisories promoted, and one control that had to be redone

The two notes `check_consistency` had been printing for dozens of loops are gone, not by
suppression. Both were true, both were read as furniture, and neither could be discharged by a
check that only knows how to say the same sentence again.

**The concession cross-check.** The application claims attestation is rooted in the device while
ledger row E26 is `not built`, and the note asked someone to confirm the wording concedes it. The
wording does concede it, plainly - "the architecture is settled; the enforcement is not built". That
is a confirmation that happens once and then has to be recorded somewhere a check can read. The
application now carries `<!-- concedes: E26 -->` at the paragraph that makes the concession, and its
absence is a failure.

**The placeholder count.** `[MONTH]` is a fact only the applicant holds, and the note said so every
run. What it could not express is the distinction that matters: an accounted-for placeholder in a
draft is a state of the work, and the same placeholder in a document declared ready is a defect. The
file now declares which it is. While it says draft, an accounted placeholder passes and an
unaccounted one fails; when it says ready, every placeholder fails.

Four controls, each run and each firing: the concession marker removed, the document marked ready
with a placeholder present, no submission marker at all, and the accounting line for a live
placeholder deleted.

## 90. The check written for W-INTL-149 could not have caught W-INTL-149

`check_commit_claims.py` compares a commit message against its diff, which is the gap W-INTL-149
fell through: nothing in this repository compared a claim against the change supposed to have made
it true.

Run against the two commits that lost their status rows, it passes both. The audit *entries* landed
and only the *table rows* did not, so the numbers do appear in the diff. That was found by running
it against the historical case before trusting it, which is the only reason it is not sitting in CI
right now looking like coverage.

The check is kept, with its scope stated: it catches a commit naming an audit entry that nothing in
the diff mentions, and that arm has a control that fires. The actual fix for W-INTL-149 is the
promotion in section 89 - the check that *did* detect the loss reported it as a note.

A second arm was written and cut. Matching file paths in the message against changed files needed a
list of verbs to distinguish "I changed X" from "X is where this lives", and a verb list is a
heuristic that reports coverage it does not have. In a verification tool that is worse than an
absent check: an absent check leaves you looking, and a heuristic one stops you.

The first version of that control committed and reset to clean up, and the reset deleted the file
being tested. The rewritten control substitutes the message in memory and touches no git state.

## 91. The pointer family re-costed, and the axis that was supposed to matter is inert

Section 77 costed IBS against SLLC at 0.32 of a tile ahead and declined it. Two things have changed:
the design has moved three times, so those absolute figures describe nothing that exists; and
W-INTL-144 established that global thresholding amplifies bias where the pointer family does not -
"IBS and C-IBS do not amplify bias [...] Rather the opposite: they remove all bias."

| Construction | Positions | Osc | Extra logic | Cells | Tiles | k needed | carried |
|---|---|---|---|---|---|---|---|
<!-- derived:external --> | SLLC + thresholding, 80% kept | 477 | 35 | 3,176 | 34,970 | **3.35** | 137.7 | 171 |
<!-- derived:external --> | IBS, block of 4, deficit is bias | 1,524 | 56 | 581 | 32,927 | **3.15** | 128.0 | 171 |
<!-- derived:external --> | IBS, block of 4, deficit is correlation | 1,524 | 56 | 581 | 32,927 | **3.15** | 136.0 | 171 |

The pointer family is 0.20 of a tile ahead, down from 0.32, and **the entropy axis does not enter
the comparison at all**. It feeds the requirement on k, and the code carries 171 against a
requirement of at most 137.7 in every arm. The axis that was expected to decide the question turns
out to bear on a constraint that is slack.

The reason the range is quoted at all is a trap worth naming. The measured entropy deficit is
attributed entirely to bias in `selection_entropy.py`, because that maximises the amplification and
is the pessimistic reading *for thresholding*. Attributing it entirely to bias again here would make
IBS appear to recover the whole deficit, which is the optimistic reading of the same unknown. One
assumption cannot be pessimistic in one comparison and optimistic in the next.

Declined again, for the reason it was declined before: IBS needs a random number source SLLC does
not, and its helper data is attackable by machine learning on exactly the correlation this source is
reported to have. Nothing measured this loop touches that argument.

## 92. Aging, which was the last unchecked constraint that could break the design

Every error-rate figure in this work has been a fresh-device figure. The register named that and left
it. Checked now, from the primary source, and it is the first constraint here that the recommendation
fails.

Rahman, Forte, Fahrny and Tehranipoor, DATE 2014:

> After 10 years, the average error in response of the ARO-PUF is 7.73%, whereas it is 32.41% in the
> conventional RO-PUF.

and on the mechanism:

> The frequency degradation in 10 years is about 1.8%

Those two figures together are the finding. The *common* drift is 1.8 percent and it flips nothing -
a response bit is a comparison between two oscillators, and a drift they share cancels. What flips
bits is the *differential*: the two oscillators of a pair age at different rates because they carry
different duty cycles, and after ten years that differential exceeds the manufacturing difference for
a third of the pairs.

Carried into this project's own source model, calibrated so the unselected rate reproduces the
published figure - the aging term is another Gaussian perturbation of the difference, adding in
quadrature with read noise:

| Oscillator | Age | Kept | Effective BER | Code tolerates | |
|---|---|---|---|---|---|
<!-- derived:external --> | conventional | fresh | 80% | 0.0076 | 0.0442 | fits |
<!-- derived:external --> | conventional | 10 years | 100% | 0.3251 | 0.0442 | FAILS |
<!-- derived:external --> | conventional | 10 years | 80% | **0.2888** | 0.0442 | **FAILS** |
<!-- derived:external --> | aging-resistant | 10 years | 80% | 0.0334 | 0.0442 | fits |

Off by six and a half times, not marginally. **The requirement, as a number rather than an
assumption: the unselected ten-year flip rate must be at or below 9.2 percent.** Published:
32.4 conventional, 7.7 aging-resistant.

### The condition that decides it is not in the source

Both figures are taken at 23 percent activation time - the fraction of wall-clock time the
oscillators run. This design runs its bank once at power-up for a few thousand cycles, so its
activation time is orders below one percent. The paper says outright that "the activation time of a
PUF in security applications should be much less than 23% used earlier" and that lower activation
reduces the error, and its Table I gives that sweep - 7.81, 7.03, 7.01 percent at 23, 10, 5 and 1
percent activation - **for the aging-resistant variant only**.

So the number this design would actually see is not in the paper. What is in the paper is that the
figure moves the right way and that the design's own duty cycle is at the favourable extreme of a
range the paper did not measure for the relevant device.

### What selection buys, and why less than expected

| Oscillator | Unselected | 80% kept | 32.6% kept |
|---|---|---|---|
<!-- derived:external --> | conventional | 0.3251 | 0.2888 | 0.1861 |
<!-- derived:external --> | aging-resistant | 0.0965 | 0.0334 | 0.0001 |

Selection ranks by the manufacturing difference, which is exactly what an aging differential has to
exceed, so it helps here for the same reason it helps against noise. It helps far less on the
conventional bank because the ten-year differential is comparable to the manufacturing spread
itself - **ranking by a signal buys little when the perturbation is as large as the signal**. And
heavier selection cannot rescue it: at 32.6 percent kept the conventional bank still sits at 0.186.

### What it changes

The oscillator arrangement stops being a detail. Until now the bank was specified by count and
length, both driven by entropy; it now carries a reliability requirement that the count and length
do not determine. One enrolment per device, recorded for loops as *binding as policy* with no cost
attached, now has one - the ten-year figure is what that policy buys, and re-enrolment is the other
way to meet the requirement.

## 93. Process corners, half closed by argument and half named

Every area and delay figure is at `sky130_fd_sc_hd__tt_025C_1v80`. The register named the corner
question as unchecked.

Half closes without measuring. Area does not vary with corner - the same cells occupy the same space
at every process condition - and area is what binds here. What varies is timing and power, and both
have an order of magnitude of slack against a design that runs a few thousand cycles once at
power-up.

The other half stays open, named precisely: the slow-corner liberty
`sky130_fd_sc_hd__ss_100C_1v60` is not present in this environment, so no derate has been measured.
An argument that a constraint is slack by a factor of ten is not a measurement of it, and this
project's rule is to say which one a row is.

## 94. Two CI steps that could not tell a clean scan from an empty one

W-INTL-153 was a CI step that passed green having read nothing. The same question asked of the rest
of the workflow found two more that could not answer it.

The banned-vocabulary scan greps a list of directories with errors suppressed; if a path is renamed
away, the scan reports no hits in exactly the way a clean scan does. The non-ASCII scan has the same
shape over `paper/`. Both now count what they matched and fail below a floor, and both print the
count on success - 72 files and 3 respectively.

Neither was inert today. The point is that neither could have told anyone if it were.

## 95. Two corrections to the aging finding, from a passage already on disk

The finding stands and two of the sentences supporting it were wrong. Both were available in the
paper this project had already downloaded and extracted, and both were written anyway.

**The 1.8 percent was not a common drift.** Section 92 read "The frequency degradation in 10 years
is about 1.8%" as a drift shared by both oscillators of a pair, and therefore cancelling. The
sentence continues: "in our proposed ARO whereas it is about 14.4% for a conventional RO." It is the
aging-resistant device's own degradation, against 14.4 percent for the conventional one. The
conclusion did not rest on it - the modelled quantities are the flip rates - but the mechanism
paragraph asserted something the source does not say.

**Low duty cycle is not a defence.** Section 92 argued that the published figures are taken at 23
percent activation time, that this design runs its bank once at power-up, and that the conventional
number was therefore probably pessimistic here. The paper contradicts it directly:

> In all cases, when the conventional RO-PUF is put in the oscillating (AC stress) or non-oscillating
> mode (DC stress) when it is not used, it will experience significant amount of aging

An idle conventional ring oscillator sits with its inverter inputs at a constant value. That is DC
stress, and it is the worst case for NBTI on the pMOS - **not running it is not resting it**. The
aging-resistant design's entire mechanism is a transistor that holds those inputs at VDD - VT while
idle so the pMOS never sees a zero, which is also why the activation-time sweep in their Table I is
given for that device and not for the conventional one.

The argument was not merely unsupported; it ran the wrong way, and the hope it expressed was the
reason it was not checked harder. Both passages sat in `/tmp/aro.txt` when it was written.

## 96. The aging-resistant oscillator, costed and adopted

W-INTL-154 left the design failing its only failing constraint with the fix named but not costed.
Costed now, from the transistor sizes the paper states: inverters at Wn = 0.12u with Wp = 2.5 Wn,
and two added nMOS gates of 0.12u and 0.24u per stage.

By transistor width that is (0.42 + 0.36) / 0.42 = **1.86 times** a conventional stage.

| | Conventional | Aging-resistant |
|---|---|---|
<!-- derived:external --> | oscillator area, each | 26.3 | 48.8 |
<!-- derived:external --> | bank of 35 | 920 | 1,709 |
<!-- derived:external --> | cell area | 34,970 | 35,759 |
<!-- derived:external --> | tiles of sixteen | 3.35 | **3.42** |
<!-- derived:external --> | ten-year flip rate, unselected | 32.4% | 7.7% |
<!-- derived:external --> | effective error at ten years, 80% kept | 0.2888 | 0.0334 |
<!-- derived:external --> | against a code tolerating | 0.0442 | 0.0442 |

**Seven hundredths of a tile buys the only constraint the design was failing.** Adopted: the
recommendation is now an aging-resistant bank, and `inputs.py` carries the factor with its
derivation.

Two approximations are stacked in that factor and both are stated rather than buried. Transistor
width is not layout area. And the base figure it multiplies is itself an inverter count from a
published tile rather than a layout of this oscillator. It is the right order and it is not a
measurement; a layout would settle it, and the ledger's falsifier now says so.

What makes this cheap is a fact established four loops ago for an unrelated reason: the oscillators
are 2.6 percent of the design. The entropy work drove the bank from 341 oscillators to 35, and a
1.86 times multiplier on 2.6 percent is not a decision anyone needs to agonise over. A constraint
that would have been expensive at the old operating point is nearly free at this one.

## 97. A borrowed input checked against the library, forty loops late

`INVERTER_AREA` comes from a published Tiny Tapeout PUF tile: 6,730 square micrometres of ring
oscillators across 1,792 inverters, so 3.7556 each. Every oscillator budget in this project has been
built on it and nobody had ever checked it against the standard-cell library that everything else
here is measured on.

`sky130_fd_sc_hd__inv_1` is **3.7522** square micrometres. The ratio is 1.0009.

The published tile's oscillators are built from drive-1 inverters, and nothing was lost in the
borrowing. That is a clean result and it took one grep of a file that had been on disk for forty
loops. The reason to record it is not the confirmation - it is that a borrowed number sat under
every budget for forty loops with a one-command check available and unrun.

## 98. The aging factor, bracketed against the library

The aging-resistant oscillator's 1.86 factor came from the transistor widths the paper states. It is
the one number in the recommendation with neither a measurement nor a synthesis behind it.

It can be bracketed without being replaced. A tristate inverter is an inverter with two extra series
devices - the same device count the ARO adds, though not the same placement:

| Cell | Area | Ratio to `inv_1` |
|---|---|---|
<!-- derived:external --> | `sky130_fd_sc_hd__inv_1` | 3.75 | 1.000 |
<!-- derived:external --> | `sky130_fd_sc_hd__einvn_0` | 5.00 | 1.333 |
<!-- derived:external --> | `sky130_fd_sc_hd__einvn_1` | 6.25 | 1.666 |
<!-- derived:external --> | in use, from transistor widths | - | **1.857** |

So two added devices in this library cost between 1.33 and 1.67 in laid-out area, and the figure in
use is conservative by eleven to forty percent.

The ratio is kept rather than replaced. A tristate inverter is an analogue, not the circuit - its
enable devices sit in the output stacks where the ARO's second device is a pull-up on the input node.
What the bracket buys is not a better number but knowing **which way the estimate errs**, which is
the difference between an unbounded approximation and a conservative one.

## 99. A second source on aging, pointing the other way, and what it adds

The ten-year requirement rests on one paper: simulation, 90 nm, HSPICE Monte Carlo. A second source
was sought for exactly that reason.

He, Li, Yu and Yang, "ASCH-PUF" (IEEE JSSC), report **silicon** measurements under accelerated aging:
96 hours at 150 °C and 1.4 V, "resulting in equivalent effects of several years' aging under nominal
conditions". Their device is a subthreshold inverter array rather than a ring-oscillator bank, so it
does not refute the RO figure - but their result has a different shape. Aging shows up as an
increase in the *masking ratio*, which is their name for reliable-bit selection: for their D-ASCH
scheme the ratio "at the start of aging is 24% and maintained below 26% throughout the aging
experiment".

Two percentage points of extra selection over several equivalent years, measured, against a third of
all bits flipping over ten, simulated. Different devices, and ring oscillators are the ones the
literature singles out as aging-sensitive - so the two are not in contradiction. What the second
source establishes is that the catastrophic figure is a property of the conventional ring oscillator
specifically, and not a general fact about PUFs that this project should have expected.

### The lever it hands over: burn-in before enrolment

The same paper: "S-ASCH benefits from having a burn-in process prior to enrollment", because "if the
enrollment is run after some time of accelerated aging, the masking ratio will not have such an
aggressive increase".

That is a requirement on the provisioning flow, not on the die - the same class as the nine enrolment
reads. NBTI damage accumulates fast and then slows, so enrolling *after* a burn-in means the enrolled
values already describe an aged device and only the remainder has to be survived.

Quantified against this design: the construction absorbs a post-enrolment flip rate of 9.2 percent,
and the conventional ten-year figure is 32.41. **Burn-in before enrolment must leave at most 28
percent of the ten-year degradation still to come.** Whether a practical burn-in does that is not
answerable from either source, and it is now a stated number rather than a hope.

It is a second, independent route to the same requirement, and it costs no area at all - which
matters because the route already adopted, the aging-resistant oscillator, rests on the one estimate
in the design that has no measurement behind it.

## 100. The summariser said the paper had no aging content, and it has twenty-one mentions

The fetch of the ASCH paper returned: "this paper contains no discussion of PUF aging, NBTI effects,
bit error rate degradation over time, or lifetime stability measurements", with a list of absent
topics and a note that it would not fabricate numbers.

Extracted and grepped, the same PDF has twenty-one occurrences of "aging", two of "NBTI", a
subsection headed "D. Aging", and the burn-in result above.

Third time in this project a fetched summary has been wrong about a source, and the first time it
was wrong by asserting *absence*. A claim that something is not in a document is exactly the claim a
summariser is worst placed to make and a reader is cheapest to check - one grep. The rule this
project already had, read the primary source, needs the corollary: a summary saying there is nothing
to read is not evidence there is nothing to read.

## 101. Burn-in costed, and it is not the free route it was recorded as

Section 99 took a lever from a silicon source - enrol after a burn-in, and the required masking ratio
does not climb aggressively - and recorded it as a second route to the ten-year aging requirement at
no area cost, needing "at most 28 percent of the degradation still to come".

Both halves of that sentence were wrong.

**The 28 percent was in the wrong units.** It compared flip rates: 9.2 percent absorbed against 32.41
at ten years. The quantity that accumulates under an aging law is the degradation, and what the
source model carries is sigma, the width of the aging differential. In sigma the requirement is
0.2974 against 1.6215 - **18.3 percent**. Flip rate is a saturating function of sigma, so a ratio
taken in flip rates flatters the requirement, and the direction of the error was the convenient one
again.

**And "no area cost" was not the cost that mattered.** Burn-in costs service life before enrolment.
Under a power law in time with the exponent swept across its published range:

| NBTI exponent n | Burn-in, equivalent years | Share of a ten-year life |
|---|---|---|
<!-- derived:external --> | 0.16 | 2.82 | 28% |
<!-- derived:external --> | 0.20 | 3.63 | 36% |
<!-- derived:external --> | 0.25 | 4.45 | 44% |
<!-- derived:external --> | 0.30 | 5.09 | 51% |
<!-- derived:external --> | 0.50 | 6.67 | 67% |

Between a quarter and two thirds of the part's service life has to happen before it is enrolled. At
the one acceleration figure available - 96 hours at 150 °C and 1.4 V for "several years" of nominal
aging - that is roughly **54 to 320 hours of oven per part**, days each, and a provisioning step that
has to be qualified rather than merely scheduled.

**So burn-in cannot replace the aging-resistant oscillator.** It survives as a supplement: applied to
a bank that already meets the requirement it widens the margin rather than creating it. The design is
back to one route, and that route rests on the one estimate with no measurement behind it - which is
now the sharpest thing to fix in this work.

Three assumptions are named in the file rather than buried. The power law itself is standard. The
exponent is technology-dependent, which is why it is swept. And the load-bearing one, unverified by
any source read here: that the *differential* between two oscillators inherits the time dependence of
the degradation. If the differential grows faster or slower than the common part, every number in the
table moves.

## 102. The same error twice in three loops, in the same direction

W-INTL-159 recorded an argument that ran the wrong way and was not checked because it was the answer
the design wanted. The 28 percent is the same failure three loops later: a ratio taken in whichever
units were nearest to hand, where the units that were nearest to hand happened to make the
requirement look reachable.

The skill rule written after the first instance - verify twice where the answer is convenient - was
in the file when the second one was written. A rule you have recorded is not a rule you have applied.

What would have caught it is narrower and more mechanical than a disposition: **a ratio between two
quantities must be taken in the units the mechanism operates in**, and when a model carries a
parameter that the observable is a saturating function of, the parameter is the unit. Flip rate is
what you measure. Sigma is what accumulates.

## 103. Every ratio in the inputs now says what it divides by what

W-INTL-166 found the same units error twice in three loops, and the disposition written after the
first instance was in the skill file when the second was made. So it is mechanised.

`scripts/check_units.py` requires every ratio in `research/inputs.py` to carry a `units:` line naming
numerator and denominator, and fails otherwise. It cannot verify that the units are *right*. What it
does is force the claim into the open, and on its first run six of six ratios were undeclared.

Writing them out found one that is wrong:

| Quantity | Units | |
|---|---|---|
| `UTILISATION` | cell area / die area | consistent |
| `INVERTER_AREA` | square micrometres / inverters | consistent |
| `MIN_ENTROPY_DENSITY` | entropy bits / response bits | consistent |
| `SELECTION_LOSS` | positions / positions | consistent |
| `DEBIAS_OVERHEAD` | raw bits in / retained bits out | consistent |
| `AGING_RESISTANT_FACTOR` | **transistor width / transistor width** | **multiplies an area** |

The aging factor is a ratio of transistor widths applied to an area. Widths and laid-out areas do not
scale together, which is exactly why the library bracket - 1.33 to 1.67 for two added devices - sits
below the 1.857 the width calculation gives.

It is kept anyway, and the reason is worth stating because it cuts against the usual instinct.
Adopting the area-grounded 1.67 would shrink the budget; the width figure is the conservative end of
a quantity with no measurement behind it; and on an unmeasured quantity the convenient direction is
not the one to move in. The units line now says so at the point of definition, where the next person
to read it will be deciding exactly that.

## 104. The burn-in assumption swept rather than assumed

The burn-in numbers rest on one unverified step: that the *differential* between two oscillators
inherits the time dependence of the degradation. It is now swept rather than asserted, with the
differential taken as `t^(k*n)`:

| NBTI exponent n | k = 1.0 | k = 0.5 | share, k=1 | share, k=0.5 |
|---|---|---|---|---|
<!-- derived:external --> | 0.16 | 2.82 | 0.79 | 28% | 8% |
<!-- derived:external --> | 0.25 | 4.45 | 1.98 | 44% | 20% |
<!-- derived:external --> | 0.50 | 6.67 | 4.45 | 67% | 44% |

k = 0.5 is what a trap-counting picture gives: a Poisson number of trapped charges has a standard
deviation going as the square root of its mean, so the spread grows more slowly than the mean and
more of it lands early. Under that arm burn-in needs eight to forty-five percent of the service life
rather than a quarter to two thirds.

The literature searched supports the direction - aging-induced threshold-voltage variability grows
with stress and correlates with gate-oxide area - and no source read here gives the functional form.
So both arms are reported and **the requirement is quoted against k = 1**, which is the arm that is
not convenient. Even at the most favourable corner of the favourable arm, burn-in is eight percent of
the service life before enrolment, so the conclusion of the previous loop stands: it supplements the
aging-resistant oscillator and does not replace it.

## 105. Every division in the models, read once

The units check covers `inputs.py`. The two errors that motivated it lived elsewhere - one in prose,
one in a model - so every division in the six research models was read.

| File | Divisions | Verdict |
|---|---|---|
<!-- derived:external --> | `selection_entropy.py` | 8 | probabilities over probabilities, key bits over density; consistent |
<!-- derived:external --> | `aging_margin.py` | 0 | nothing to check |
<!-- derived:external --> | `pointer_vs_linear.py` | 4 | positions over a fraction, key bits over density; consistent |
<!-- derived:external --> | `burn_in.py` | 6 | sigma over sigma, and one flip-rate ratio printed to name the previous error; consistent |
<!-- derived:external --> | `reliable_bit_selection.py` | 8 | integration steps and entropy per selected bit; consistent |
<!-- derived:external --> | `selection_with_bch.py` | 5 | **one defect** |

The defect: the search table displayed the post-selection density as `KEY / need_k`, where `need_k`
is the *ceiled* integer number of bits the key requires. Round-tripping a ceiling through a division
gives 0.9275 where the density is 0.9293. Two files reported two densities for one operating point,
and neither was wrong on its own terms - one printed a density and the other printed the density
implied by a rounded requirement, under the same column heading.

Small, and the same shape as the errors that were not small: a quantity recomputed locally instead of
imported, in units that were nearly right.

Fixed the way this project keeps arriving at: one definition, imported. `density_at()` is now the
only place the number is computed, and the sweep moved under a main guard so a checker can import the
module without executing three tables - a module that computes on import cannot be cross-checked
against, which is part of how the split survived.

And cross-checked rather than trusted. `check_figures_reproduce.py` now compares what the two models
report and fails on any disagreement, because one definition imported can be undone by anyone who
finds it convenient to recompute locally. The control - reintroducing the round-trip - fires.

## 106. What the sweep says about where errors live

Five of six models were clean, and the sixth failed on a display column rather than on a result. That
is worth stating because the instinct after two units errors was that the models were riddled with
them.

The two that mattered were in prose and in a comparison written for a report - places with no
compiler, no import graph and no test. The models are the part of this work that gets executed, and
execution is what has been keeping them honest.

So the useful generalisation is not "audit the arithmetic". It is that **the error rate tracks
whether a number is executed**, and the defence is to move numbers into code that runs rather than to
read prose more carefully. The units check does that for the inputs; the cross-model check does it
for a figure that two files were free to disagree about; the parts still unprotected are the ones
that appear only in sentences.

## 107. The ledger's area row, bound to the model that produces it

W-INTL-170 said the error rate tracks whether a number is executed. The row carrying this project's
externally visible area claim held sixteen numbers, of which four were recomputed by a check and the
rest were sentences. Fifteen are now recomputed from `research/inputs.py` on every run: cell area,
utilisation, the four component areas, raw and selected positions, k carried and k required, the
measured density, the aging factor and its cost in tiles, and two counts describing the apparatus.

Binding them found three stale claims in the row immediately, none of which any existing check could
see:

| Claim | Said | Is |
|---|---|---|
<!-- derived:external --> | cost of the aging-resistant oscillator | 0.07 of a tile | **0.08** |
<!-- derived:external --> | testbenches in `measure_all.sh` | nineteen | **twenty-one** |
<!-- derived:external --> | oscillator aging | "named as unchecked" | checked, binding, and met |

The third is the one that matters. The row still described aging as an open question two loops after
it became the constraint that drove the oscillator choice, in the same paragraph that described the
oscillators as aging-resistant. Prose does not notice when it contradicts itself.

The figures deliberately left unbound are the external ones - the literature's flip rates, the
process node, the key length. Binding those would assert that a constant equals itself, which is the
failure mode of coverage counted for its own sake.

## 108. The count that caught itself

The testbench count was bound by counting `run_tb` lines in the script. That regex returned
twenty-two where the script's own counter reports twenty-one, because the function *definition*
line - `run_tb () {` - also begins with `run_tb `.

Two independent counts of the same thing disagreed, and the disagreement was the whole value: the
first number to distrust is the one you obtained by pattern-matching over source, and the check
against it is the artefact's own report of what it did. The script prints "21 testbenches ran"
because it increments a counter inside the function, which is the count that reflects execution
rather than appearance.

A floor was added with it. The check fails if fewer than fifteen figures bind, because a list of
bindings can shrink silently and a number that stops being checked goes back to being a sentence
without anyone deciding that it should.

## 109. The aging mitigation, realised in a cell the library already has

The design carries an aging-resistant oscillator because a conventional bank loses a third of its
response bits over ten years and this construction absorbs 9.2 percent. The factor in the budget,
1.857, is a transistor-width ratio from a custom cell, and it is the one number in the recommendation
with neither a measurement nor a synthesis behind it.

The mechanism does not need a custom cell. Their ARO adds two transistors per stage: one to stop the
oscillation, one to hold the inverter input at VDD - VT while idle so the pMOS never sees a zero. The
second is the one that matters, because NBTI on a pMOS is driven by a gate at zero and an idle
conventional ring leaves half its nodes there.

**Build the ring from two-input NANDs with the enable on the spare input.** With the enable high each
stage is an inverter and the ring oscillates. With the enable low every output is driven to VDD, so
every pMOS gate in the ring sits at one - the recovery condition rather than the stress condition.
Same mechanism, through a cell that already exists.

And in this library it is free:

| Cell | Area |
|---|---|
<!-- derived:external --> | `sky130_fd_sc_hd__inv_1` | 3.7536 |
<!-- derived:external --> | `sky130_fd_sc_hd__nand2_1` | **3.7536** |
<!-- derived:external --> | `sky130_fd_sc_hd__einvn_1` | 6.2560 |

Not similar - the same number, read from the liberty at run time rather than transcribed. The
tristate inverter is there for contrast: it stops the oscillation and leaves the node floating, which
is not the mechanism.

| Arrangement | Factor | Oscillators | Cells | Tiles |
|---|---|---|---|---|
<!-- derived:external --> | conventional inverter ring | 1.000 | 920 | 34,970 | 3.35 |
<!-- derived:external --> | NAND ring, same library cell | 1.000 | 920 | 34,970 | 3.35 |
<!-- derived:external --> | their ARO, by transistor width | 1.857 | 1,709 | 35,759 | 3.42 |

**The budget does not move.** The 7.73 percent ten-year figure is theirs, for their cell, in their
simulation. A NAND ring shares the mechanism and has no published flip rate, so adopting it would
trade a measured number for an argued one - and the argued one is the convenient one. The
conservative factor stays.

What would settle it is narrow and worth stating: a ten-year flip rate for a NAND-gated ring held
high while idle, simulated or measured. At that point the mitigation costs nothing instead of 0.08 of
a tile, and the last unmeasured estimate in the recommendation disappears with it.

## 110. The register bound, and the synthesis half in CI

Two pieces of apparatus, both continuing W-INTL-170.

**The constraint register.** Seven more figures recompute from the model on every run - k carried,
both densities, the aging factor, its cost in tiles, and the tiles before and after. The register is
where a constraint's *status* is written, which is exactly where the contradiction W-INTL-171 found
lives: a document describing a constraint as unchecked in the same paragraph as the design built to
satisfy it. Twenty-two prose figures are now bound across the two documents, with a floor under the
count.

One pattern had to be anchored on its sentence rather than its units: `to ([\d.]+) of sixteen` matched
"13 to 15 of sixteen" elsewhere in the file first, and reported 15 against a recomputed 3.42. A
regex over prose finds the first thing shaped like the answer, not the answer.

**The synthesis half of `measure_all.sh`, in CI.** This was named and not done for three loops. It
needs the standard-cell liberty, which is 12.8 MB of PDK and not in this repository; the job fetches
it from the cell library mirror, caches it, verifies the header names the corner it asked for, and
fails if the fetch fails - a synthesis check that silently skips is the failure mode of W-INTL-153.
Then `verify_inputs.py` re-synthesises all twenty-two declared areas.

That closes the last gap between "the figures are reproducible" and "the figures are reproduced".
Every area this project quotes is now re-synthesised on every pull request, and every testbench that
guards it runs alongside.

## 111. The areas reproduce on one laptop, and the first foreign run said so

The synthesis job's first run reported **all twenty-two declared areas as mismatches**, by up to seven
percent in both directions - the decoder at t=21 out by 3,230 square micrometres, SPONGENT out by 227
the other way.

Nothing is wrong with the circuits and nothing is wrong with the declarations. The runner's yosys is
a different version from the one every figure here was measured with, and a synthesis area is a
property of the tool as much as of the circuit: a different release maps to different cells.

So "every figure in this project reproduces" has silently meant "on this laptop, with this build of
yosys" for the whole of the work. The liberty was declared, measured, cross-checked and carried in
`inputs.py`. The tool that reads it was never mentioned.

That is the same shape as W-INTL-158 one level deeper. There, a script had only ever run on the
machine that wrote it. Here the *numbers* had only ever been produced by one build of one tool, and
the first execution on foreign ground was again the measurement.

Two fixes. `research/inputs.py` declares the toolchain, and `verify_inputs.py` checks it before
comparing anything - so a version difference now reports itself as a version difference rather than
as twenty-two wrong numbers. And CI installs the pinned build rather than the distribution's,
cached, so the comparison is against the tool the figures were taken with.

CI cannot install the declared build without a blind search through 737 MB release tarballs, so it
compares with a fifteen percent tolerance instead - wider than the measured cross-version spread of
7.3 percent and far tighter than the seventy percent convention error this check was created to
catch. Exact comparison stays where the declared build is.

Two smaller things fell out of doing it. A control that mutates a file and restores it by copy left
the checker reading a stale `__pycache__`, so a run reported the mutated value after the restore -
which means a control can lie in the direction of the thing it was testing. And the version gate is
worth more than the fix: its output is one accurate sentence where the same condition previously
arrived as twenty-two wrong numbers.

The general form is worth keeping: **a measurement carries its instrument**. This project has been
careful to record the conditions of every borrowed number - the pairing distance, the temperature,
the activation time, the process node - and did not record the version of the program that produced
its own.

## 112. A control that tests nothing, and the reason nobody would guess it

The previous loop noticed in passing that a control which mutates a file and restores it by copy left
a checker reading a stale bytecode cache. Chased down, the mechanism is precise and worse than it
looked.

Python's import cache is keyed on the source file's **modification time and size**. Swap a value for
one of the same length, within the same second, and the interpreter reuses the cached bytecode - so
the mutated run reads the *original* value. Reproduced rather than asserted:

```
equal length       mutated to 0.23     the run saw 0.65     -> MUTATION INVISIBLE
different length   mutated to 0.6500   the run saw 0.6500   -> mutation visible
```

The consequence is the inverse of what the last loop guessed. The danger is not that a control
reports a failure after restoring; it is that **a control reports no failure at all** - and the honest
conclusion from a control that does not fire is that the check is broken, which would be wrong. An
equal-length swap is exactly what a careful person writes: `0.65` for `0.23`, `24,659` for `24,700`,
`0.9293` for `0.9500`.

Three of this project's controls were equal-length swaps on Python files. Re-run through a harness
that disables bytecode caching, all of them fire.

`scripts/control.py` is that harness. It verifies the anchor exists before mutating - a replacement
whose anchor is absent returns the input unchanged, which is W-INTL-149 in a different costume - runs
the check with bytecode caching off, restores by content, and verifies the restoration by hash rather
than by assuming the copy worked. Its `--self-test` reproduces the stale-cache case, so the reason
the harness exists is demonstrated on every run rather than believed.

Five controls now run in CI: the self-test, and one for each of the four checks that can be broken by
a single edit.

## 113. The control found a second defect on its way in

Running the zero-selection control through the harness made `check_figures_reproduce.py` crash rather
than report, with a `KeyError` on the SLLC area table.

The cause was worth more than the crash. Without selection the search chooses a different code -
BCH(127,8,31) - and the budget line was written as `I.SLLC_AREA.get(t, max(I.SLLC_AREA.values()))`.
That default silently lets the search **recommend a construction whose masking stage has never been
measured**, using the largest measured one as a stand-in. It happened not to matter, because the code
the search actually returns is measured. It would have mattered the moment the operating point moved
again, which in this work is roughly every third loop.

Codes without a measured masking stage are now skipped outright. A recommendation has to be measured
end to end, and a default that fills in a missing measurement is the opposite of that.

An exception is also not a diagnosis: the control now produces `selection is computing no bias
amplification`, which names the broken thing.

## 114. The oldest check had never been tested, and two of its nine parts could not fail

`check_consistency.py` has run on every loop for longer than anything else here. It has nine internal
checks and not one of them had a control. Written now, one per check, through the harness from the
previous loop.

Seven fire on the first attempt. Two did not, for the same reason and a different one.

**`check_matrix_markers` could not fail.** It appends to `notes`, and notes do not fail a run. The
check exists because a competitor was once understated by a fifth for want of a provenance marker,
and for its whole life it has been unable to stop that happening again. Promoted; the control -
removing the marker from a real quantitative row - now fires with
`quantitative row without a provenance marker: 'Reference edge accelerator v1'`.

That is the third instance of the same pattern in one file, after the two promoted in W-INTL-150. A
note is where a check goes when nobody decides whether it is a rule.

**`check_references_resolve` was worse: wrong file type and wrong file set.** Its pattern matched
backticked `` `dir/file.md` `` only, which is the kind of reference these documents almost never
make, while every document points constantly at `.py`, `.sh` and `.v` files - the ledger explicitly
tells a reader to go and read them. And the list of documents it was given contained the ledger, the
application, the audit, the matrix, the README and a checklist. **Not the research documents.** So
the file carrying most of this project's reasoning, which names a script on nearly every page, had
never had a single reference checked.

Widened to the file types actually used, given the research documents, and promoted from a note to a
failure. One subtlety kept it honest: the audit cites
`paper3-rossiya30-troica/research/weak_spots_registry.md`, a path in another repository that contains
a string looking exactly like a local `research/...` file. The pattern is anchored on a repository
top-level directory preceded by a non-path character so that case does not fire, and there is a
control asserting it does not.

Scanned with the widened pattern, every reference in every document resolves. The check was broken;
the documents were not.

## 115. What "the checks pass" was worth before this loop

Nine internal checks, two of which could never fail and one of which was reading the wrong files.
Every loop for eighty-odd loops printed `check_consistency: OK` and meant less than it appeared to,
by an amount nobody could have stated.

The pattern across the last three loops is one thing said three ways: a check that has never failed
is a check nobody has tested, and the way you test it is to break the thing it guards and watch. Ten
controls now run in CI - the harness self-test and nine deliberate breakages - and each names the
check it exercises.

The remaining untested surface is written down rather than left implicit: `check_catalog` has four
internal checks and no controls, and `check_commit_claims` has one arm with a control that is not in
CI.

## 116. The catalog checker, and the fourth silent-skip in the same codebase

`check_catalog.py` has four internal checks and had no controls. All four have them now, and getting
there found two defects of a kind this project has been finding for four loops running.

**It skipped silently.** Its own docstring says so approvingly: "If neither a path nor the CLI is
available it skips rather than failing, so it can sit in CI without making the build depend on
another repository being reachable." That is a green tick that read nothing - the failure mode of
W-INTL-153, sitting in this file the whole time and *documented as a feature*. Skipping is now
something a caller asks for with `--allow-missing`, and a missing catalog otherwise fails.

**Its metadata check could not fail.** `check_no_measurements_in_metadata` appends to notes, and it
is the check written for W-INTL-41 - an entry marked verified that asserted an FPGA frequency in a
metadata field. The check written to stop that recurring could not stop anything. Fourth instance of
this pattern.

Here the note had a real justification the earlier three did not: the catalog is in another
repository that this project cannot edit, so a failure would demand a fix nobody here can make. The
resolution is neither a note nor a bare failure but a declared count - one outstanding observation,
`EXPECTED_METADATA_OBSERVATIONS = 1`, checked on every run. It passes while the number matches and
fails when it moves, which is exactly when a human is needed. **An observation about something you do
not control is still a number you can pin.**

An unreadable catalog path also used to raise a `FileNotFoundError`. A traceback is not a diagnosis,
and "the catalog says something wrong" and "you gave me a path that is not there" are different
problems for whoever is reading.

## 117. The last check without a control

`check_commit_claims.py` had one arm and no way to control it: its only input is the commit message,
and a message cannot be mutated by editing a file. A `--message-file` override now substitutes the
message while leaving the diff alone, which is the smallest thing that makes the check testable.

That completes the sweep. Every check in this repository now has at least one control, and every
control runs in CI: the harness self-test, nine breakages against `check_consistency` and
`check_figures_reproduce`, four against the catalog, and one against the commit-claims check.

The tally for four loops of this work is worth stating plainly, because it is the argument for having
done it. Of the checks this project trusted, **one could not see its own motivating failure, four
could not fail at all, one was reading the wrong files, one skipped silently while documenting the
skip as a feature, and one had no controls of any kind.** None of that was visible from a green run.

## 118. The control that landed inside the thing it was checking

The commit-claims control passed in CI, which for a control means it failed: the check it was meant to
break reported OK.

The probe message named a nonexistent entry number, written as a literal in the workflow file. The
workflow file is part of the diff the check reads. So the check looked for a line mentioning that
number, found one - its own instructions - and correctly reported no problem.

Writing this section repeated the mistake: describing the control with the number spelled out put the
number back into a document the check reads, and the second CI run failed the same way for a
different file. The number is generated at run time now, from a clock, and no document here contains
it - including this one, which is why it is described rather than quoted.

The control was not wrong about the check. It was wrong about the world: **writing the probe put the
probe's evidence into the evidence**.

This is the third distinct way a control in this project has managed to test nothing - after an
anchor that was not present, and a mutation the interpreter could not see. The pattern underneath all
three: a control is an experiment, and an experiment that shares any surface with its subject is not
measuring what it thinks it is. Here the shared surface was the file itself.

## 119. The toolchain spread, measured instead of assumed

W-INTL-175 concluded that synthesis areas are toolchain-dependent by up to seven percent, from a run
where all twenty-two mismatched. That run used the distribution's yosys, which is several years
behind. Under the pinned modern build the picture is different and much better:

| Entry | yosys 0.65 | yosys 0.67+111 | Delta | Relative |
|---|---|---|---|---|
<!-- derived:external --> | nineteen of twenty-two | - | **0** | 0.000% |
<!-- derived:external --> | GF(2^7) t=11, shared solver | 24,659 | 24,614 | -45 | 0.182% |
<!-- derived:external --> | GF(2^7) t=13, shared solver | 28,958 | 29,015 | +57 | 0.197% |
<!-- derived:external --> | GF(2^7) t=21, shared solver | 44,346 | 44,231 | -115 | **0.259%** |

**Nineteen of twenty-two reproduce exactly, and the three that move are all the shared-multiplier
solver** - the one circuit in this design with resource sharing for the mapper to exploit
differently. That is a satisfying place for the only version sensitivity to sit: the circuit that
exists because two multipliers are used where sixty-six were, and whose whole point is that the
mapper has choices.

So the seven percent was a statement about a stale tool, not about version drift. The CI tolerance
goes from fifteen percent to **one**, against a measured worst case of 0.26. That is close enough to
exact that the CI check is now worth what the local one is: a convention error of the kind it was
built for - 24,659 against 42,069 - is seventy percent, three hundred times the noise.

The earlier figure is corrected rather than quietly replaced. "Toolchain-dependent by up to seven
percent" was true of the comparison that produced it and false as a general claim, and the difference
between those two is the whole of what this project keeps learning.

## 120. What the free aging mitigation has to prove

Section 109 found that a NAND-gated ring gives the aging-resistant mechanism at zero area cost in
this library, and declined to bank it because the ten-year flip rate belongs to the paper's custom
cell. That left the question open. It can be made precise.

In the source model the three arrangements sit at:

| Arrangement | Ten-year flip rate | sigma |
|---|---|---|
<!-- derived:external --> | conventional ring | 32.41% | 1.6215 |
<!-- derived:external --> | required by this construction | 9.20% | 0.2974 |
<!-- derived:external --> | the paper's aging-resistant cell | 7.73% | 0.2477 |

The requirement sits between the two, and **much closer to the aging-resistant end**. A NAND ring may
sit 3.6 percent of the way from the ARO back toward a conventional ring - so it has to capture **at
least 96.4 percent of the ARO's benefit**.

That is a far tighter condition than "shares the mechanism, so it should be fine", which is what the
argument amounted to. The mechanisms are not identical: the ARO holds the inverter input at
VDD - VT with a dedicated transistor, while a NAND holds its output at VDD, and the paper's cell also
stops the oscillation with a second device where the NAND does both jobs with one gate. Whether those
differences cost more or less than 3.6 percent of the benefit is not answerable from the mechanism.

The useful output is the number, not the verdict: **a NAND-gated ring qualifies if its ten-year
unselected flip rate is at or below 9.2 percent**, and the margin between that and the ARO's 7.73 is
one and a half points. Anyone simulating it now knows what counts as a pass.

## 121. The decisions column swept, and the thinnest number in this work

The register has carried a column naming, for each constraint, the decisions taken against it. It has
never been swept. Swept now, constraint by constraint: has this constraint moved since those
decisions were taken, and were they revisited.

Six of eight are clean. Word failure moved and the code was re-chosen. Helper-data leakage no longer
applies. The oscillator entropy floor has not moved. One enrolment per device acquired a cost and it
was analysed. Throughput was slack and then used. Sixteen tiles went from binding to slack with 12.5
tiles spare - and nothing should move with it, because the decisions taken against it (sharing the
solver's multipliers, leaving the Chien search parallel, the field) each won on their own terms and
would win again.

**The raw error rate row was not clean, and what it hid is the thinnest number in this project.**

Its decisions were the selection fraction, the number of enrolment reads and the code. The constraint
moved when aging entered: what matters at ten years is the aged rate, not the fresh one. The code was
revisited. The fraction and the read count were not.

Worse, the aging analysis computed the aged rate with `selected_ber`, which is the **perfect-ranking
bound** - the file that defines it says so in its docstring. Enrolment cannot rank perfectly; it ranks
by a majority vote over a handful of reads. Recomputed against what nine reads actually achieve:

| Kept | Ideal ranking | 9 reads | 25 reads | Tolerated |
|---|---|---|---|---|
<!-- derived:external --> | 80% | 0.0337 | **0.0403** | 0.0376 | 0.0442 |
<!-- derived:external --> | 60% | 0.0065 | 0.0183 | 0.0089 | 0.0442 |
<!-- derived:external --> | 40% | 0.0004 | 0.0177 | **0.0058** | 0.0442 |
<!-- derived:external --> | 32.6% | 0.0001 | 0.0172 | 0.0064 | 0.0442 |

At the design's eighty percent and nine reads, the ten-year effective rate is **0.0403 against 0.0442
tolerated - a margin of 1.10**. The figure the aging work reported, 0.0334, was the perfect-ranking
bound and the achievable number is a tenth of the way from it to failure.

And the lever is not the one the fraction column suggests. Deeper selection with nine reads plateaus
at about 0.017, because past a third discarded **the ranking is the limit, not the fraction** - nine
reads give five distinct reliability levels and cannot separate what is left. The two have to move
together.

Adopted: keep forty percent, read twenty-five times. Ten-year effective rate **0.0058, a margin of
7.6**, for 953 raw positions instead of 477, forty-five oscillators instead of thirty-five, and 0.05
of a tile. The reads cost provisioning time and no area at all.

| | Before | After |
|---|---|---|
<!-- derived:external --> | kept | 80% | 40% |
<!-- derived:external --> | enrolment reads | 9 | 25 |
<!-- derived:external --> | ten-year effective rate | 0.0403 | 0.0058 |
<!-- derived:external --> | margin against 0.0442 | 1.10 | 7.6 |
<!-- derived:external --> | raw positions | 477 | 953 |
<!-- derived:external --> | tiles of sixteen | 3.42 | 3.47 |

A thirteenth thing failed, in CI rather than locally: one of the controls carried the old value as
its anchor, and the harness refused to run it - "the control's anchor is not in research/inputs.py,
so nothing would be broken". Before the harness existed that control would have mutated nothing,
found no failure, and reported that the check does not work. A stale control is the most expensive
kind of stale thing, because it reads as evidence.

Twelve bound figures across the ledger and the register failed the moment the inputs changed, and
each named itself. That is the three loops of binding prose to the model paying for themselves in one
edit.

## 122. What the sweep was actually for

The column was added six loops ago as "the change not made", with a note that the next loop was a
better place to make it. It was then carried, unswept, for six loops - which is the same shape as the
constraint register itself going stale for three, and the notes nobody read for dozens.

**An artefact that records what to revisit is not a revisit.** The sweep took one pass and found a
margin of 1.10 where the documents claimed comfort, in the row whose constraint had moved most
recently and most consequentially.

The generalisation for the skill file is narrower than "sweep your registers". It is that a bound
computed from an *optimistic* model - here perfect ranking, explicitly labelled as a bound in the
file that defines it - will be quoted downstream as if it were the achievable figure, because
downstream reads the number and not the docstring. A bound should carry its direction in its name.

## 123. The bound gets a name and a sibling, and the sibling contradicts last loop

`selected_ber` is renamed `selected_ber_ideal`, and `selected_ber_achievable(sigma, fraction, reads)`
is written beside it. The rename is W-INTL-186's own prescription applied to the function that
motivated it: the docstring said "optimistic bound" for six loops and downstream read the name.

Writing the sibling immediately contradicted the operating point adopted last loop.

**The selection fraction is not a free parameter.** Enrolment ranks by how lopsided a majority vote
was, so the attainable fractions are the discrete vote margins - and the deepest is the share of
positions that never voted unanimously. Everything below that floor is tie-breaking at random among
positions the vote cannot separate, which buys nothing at all:

| Reads | Deepest attainable keep | Ten-year effective rate | Margin | Raw positions |
|---|---|---|---|---|
<!-- derived:external --> | 9 | 64.8% | 0.0186 | 2.4 | 588 |
<!-- derived:external --> | **25** | **54.4%** | **0.0064** | **6.9** | **701** |
<!-- derived:external --> | 49 | 48.8% | 0.0032 | 13.9 | 781 |
<!-- derived:external --> | 99 | 43.8% | 0.0015 | 29.0 | 871 |

Last loop specified "keep forty percent, read twenty-five times". Forty percent is **not reachable**
at twenty-five reads, or at ninety-nine. The right form of the same decision is: **the read count is
the parameter and the fraction follows from it.**

Adopted: twenty-five reads, keep the positions that were not unanimous - 54.4 percent, 701 raw for
381 selected, ten-year effective rate 0.0064 against 0.0442, a margin of 6.9. That is very close to
what last loop claimed, and reached by a mechanism that exists. It is also cheaper than the
unreachable version: 701 raw positions rather than 953, thirty-eight oscillators rather than
forty-five, 3.44 tiles rather than 3.47.

The conclusion held and the specification did not, which is the distinction this whole apparatus is
for. A design that says "keep the most reliable forty percent" and a mechanism that can only keep
54.4 or 48.8 are not the same design, and only one of them can be built.

## 124. What else quotes a bound

The other models were read for the same defect. `code_choice_model.py` uses the n-k leakage bound and
an ordering bound on oscillator entropy, both labelled as bounds in the prose that quotes them and
both used as upper limits on what is claimed, which is the direction a bound is safe in.
`pointer_vs_linear.py` quotes a range rather than a point precisely to avoid it. `burn_in.py` sweeps
its unverifiable assumption and reports against the unfavourable arm.

So one instance, not a pattern - but the one instance sat under the design's tightest constraint for
five loops, and it took writing the sibling function to find that the operating point it justified
was unreachable.

## 125. The ranking was quantised because the model assumed the wrong instrument

Section 123 established that the selection fraction is quantised by the vote margin, and that below
the unanimous-vote floor further selection buys nothing. That is true of ranking by a vote of sign
bits. It is not true of this design.

`ro_characteriser.v` emits **one frequency count per oscillator per sweep**. Its header says why: so
that pairing, thresholds and every derived quantity are computed off the die and can be recomputed
when the question changes. The enrolment model, meanwhile, ranks by `abs(votes - reads/2)` - it
assumes enrolment sees only response bits.

The instrument this project built produces the very quantity the enrolment model assumes is
unavailable.

Ranking by the averaged difference instead - error falling as sigma over the square root of the read
count - is continuous rather than quantised, and tracks the ideal bound:

| Kept | Ideal | Vote, 25 reads | Counts, 25 reads | Counts, 9 reads |
|---|---|---|---|---|
<!-- derived:external --> | 80% | 0.0337 | 0.0371 | 0.0357 | 0.0380 |
<!-- derived:external --> | **54.4%** | 0.0035 | **0.0057** | **0.0039** | 0.0052 |
<!-- derived:external --> | 40% | 0.0004 | 0.0062 | **0.0005** | 0.0007 |
<!-- derived:external --> | 32.6% | 0.0001 | 0.0077 | 0.0002 | 0.0002 |

At the design's operating point the ten-year margin goes from 6.9 to **11.3 at no area cost**, and
deeper fractions become reachable: 40 percent, unattainable by any vote, gives 0.0005 and a margin
above eighty.

**The positions and the area are unchanged**, because this is a provisioning-flow choice rather than
a die-area one. What it costs is stated rather than hidden: the part must expose frequency counts
during enrolment, and `ro_characteriser.v` says in its own header that raw counts are exactly what an
attacker wants and exactly what a key generator must never expose. So count-based ranking requires
that interface to be disabled after enrolment - a security-relevant property of the shipped part, not
a modelling convenience.

## 126. The parameter sweep that produced it

Section 123's lesson - ask whether the mechanism can reach the operating point - was applied to every
other continuous-looking parameter in the design.

| Parameter | Quantised by | Handled |
|---|---|---|
<!-- derived:external --> | number of blocks | integer by construction | yes |
<!-- derived:external --> | oscillator length | must be odd for a ring to invert | yes, at seven |
<!-- derived:external --> | oscillator count | pairs go as R(R-1)/2, so positions jump | yes, the search takes the ceiling |
<!-- derived:external --> | gate window | a power of two by construction | yes, unswept and slack |
<!-- derived:external --> | **selection fraction** | **the ranking mechanism** | **no - and the mechanism was the wrong one** |

Four of five were already handled, mostly because integers are obviously integers. The one that was
not is the one whose quantisation came from a *choice of architecture* rather than from arithmetic -
and an architectural quantisation looks continuous in the model right up until someone asks which
instrument does the ranking.

## 127. Renaming made the defect legible and nobody fixed the callers

`selected_ber` became `selected_ber_ideal` last loop so that a caller who wanted the achievable figure
would notice. Every caller still called the bound: the aging analysis, the code search, and the CI
figure check, all now reading `R.selected_ber_ideal(...)` in plain sight.

A rename converts an invisible defect into a visible one. It does not convert it into a fixed one,
and a line that reads `_ideal` is only conspicuous to someone already asking the question.

All three now use the achievable rate. That needed one more thing first: the count-ranked estimator
was a Monte Carlo, and a check that moves by a thousandth between runs teaches people to re-run it
until it passes. So `selected_ber_counts_exact` derives it in closed form - the conditioning is
standard, `d | v` is Gaussian given the enrolment estimate - and it agrees with the sampler to within
a tenth of a thousandth while being deterministic.

Writing it caught its own arithmetic error on the way: the first version integrated the wrong tail
and made the error rate **rise** with deeper selection. The sign of the slope is what caught it, not
the magnitude, which is the kind of check worth having on any new estimator.

### What it changes

| | Vote-ranked | Count-ranked |
|---|---|---|
<!-- derived:external --> | ten-year effective rate at 54.4% kept | 0.0064 | **0.0040** |
<!-- derived:external --> | margin against 0.0442 | 6.9 | **11.1** |
<!-- derived:external --> | absorbable unselected ten-year flip rate | 9.2% | **15.5%** |
<!-- derived:external --> | a NAND ring must capture | 96.4% of the ARO benefit | **79.4%** |

The last row is the one that matters beyond this file. The threshold the free aging mitigation has to
clear was 96.4 percent of a custom cell's benefit; it is now 79.4, because better ranking left more
room for the oscillator to be worse. **The requirement on a component moved because a decision about
provisioning moved** - which is the constraint-and-decision coupling this project keeps rediscovering,
running in the pleasant direction for once.

## 128. The control that changed nothing

Setting the enrolment read count to one and running the figure check produced **no failure**. The
design depends on that number - it is the difference between a ten-year margin of 11.1 and one of
2.2 - and no bound figure referred to it, so the check could not see it move.

Two figures now do: the ten-year margin, and the unselected flip rate the construction absorbs. Both
recompute from inputs including the read count, and the control fires with `ten-year margin says
11.1, recomputing from inputs gives 2.192`.

The general shape is worth keeping. Twenty-two bound figures made the documents hard to falsify, and
a parameter with no figure attached to it was invisible to all of them. **Coverage of a document is
not coverage of a model**: the question is not how many numbers are checked but which inputs can
change without any of them moving.

## 129. Every input perturbed, and the acceptance criterion came from the superseded code

W-INTL-192 found one input no check could see. Rather than guess at others, every scalar in
`inputs.py` was multiplied and divided and the checks re-run. Two were blind, and the second was not
a blind input at all.

**`TARGET_FAILURE` was declared and unread.** The word error probability the entire error-correction
design exists to meet lived in `inputs.py`, was imported by one file outside the recommendation path,
and was written as the literal `1e-6` in seven other places. That is the pattern `inputs.py` was
created to prevent, in the file that prevents it, applied to the requirement rather than to a
measurement.

**And the tolerated bit error rate was a stale literal from a superseded code.** `0.0442` appeared in
three files as "what the code tolerates". It is not an input - it is a consequence of the code and the
target - and it belonged to BCH(127,29,21) in five blocks, which tolerates 0.0483 and was replaced
four loops ago.

The recommendation, BCH(127,57,11) in three blocks, tolerates **0.0143**. At 0.0442 its word failure
is 0.0322 - thirty thousand times the target. So every aging verdict computed against that literal
was measured against a bar three times too low.

| | Against the stale literal | Against the derived tolerance |
|---|---|---|
<!-- derived:external --> | tolerated bit error rate | 0.0442 | **0.0143** |
<!-- derived:external --> | ten-year margin at 54.4% kept | 11.1 | **3.6** |
<!-- derived:external --> | absorbable unselected flip rate | 15.5% | **10.9%** |
<!-- derived:external --> | a NAND ring must capture | 79.4% of the ARO benefit | **92.0%** |

**The design still fits** - 0.0040 against 0.0143 - and the aging-resistant bank still clears the
requirement at 7.73 against 10.9. The conclusions survive; three loops of margin figures did not.

The tolerance is now derived from the recommendation on every run, so it moves when the code moves.

## 130. The sweep is a check now

`scripts/check_input_coverage.py` perturbs every declared scalar by a factor of four in each direction
and fails if no check notices. It runs in CI.

Two details earned themselves immediately. The perturbation has to be **large**: a half-step landed
inside a bound figure's tolerance and reported a covered input as blind, and the question is whether a
check is sensitive to an input at all, not whether it resolves small changes. And `RAW_BUDGET` is
listed as deliberately unread, with the reason - it feeds only the vestigial guard kept for the
utilisation factor. **An allow-list with reasons is the difference between a known gap and an
unnoticed one.**

The generalisation this project has been circling for four loops now has its mechanical form. Binding
figures to a model makes documents hard to falsify. Perturbing inputs asks the complementary
question - *which inputs can move without any bound figure moving* - and only the second one finds a
constant that nothing reads.

## 131. The check that made the fast job slow

`check_input_coverage` went into the document job and took it from twelve seconds to **ten minutes
and forty-four**. Thirteen inputs, each perturbed and each re-running two checks, one of which
re-derives the recommendation from scratch.

It is the right check in the wrong place. Every unrelated documentation change now waited on a
sensitivity sweep, and the reliable consequence of that is somebody eventually removing the sweep
rather than waiting for it. Split into its own job, where it runs beside the two synthesis jobs that
already take six minutes and blocks nothing that finishes in twelve seconds.

The general point is about how checks get abandoned. A check is not just correct or incorrect; it has
a cost, and the cost lands on whoever is doing something unrelated. A ten-minute gate on a
one-line documentation fix is a gate with a short life expectancy, however sound it is.
