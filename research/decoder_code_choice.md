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
