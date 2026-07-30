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
