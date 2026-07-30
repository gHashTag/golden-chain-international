# Does a Usable Identity Root Fit on a Tile

Status: written 2026-07-30. Answers the question left open by audit W-INTL-47,
which found that the primitive has been fabricated on the process this project
already uses but at eight bits of response, and did not establish whether a usable
one fits in the area a shuttle allows.

Confirmed by synthesis on 2026-07-30, three times. First the published oscillator
implementation, then two of the decoder's three stages, then the third stage and an
alternative code. Every area below is now measured.

Each pass moved the answer, and the third moved it furthest. The decoder estimate was
low twice over, and then the code the decoder was sized for turned out to be the wrong
code - see `decoder_code_choice.md`, which this section now defers to.

---

## 1. Measured

A Tiny Tapeout 1x1 tile is about 161 by 112 micrometres, so 18,032 square
micrometres. The largest block a submission may take is 8x2, sixteen tiles, about
288,512 square micrometres.

Synthesis of the published eight-bit implementation:

| Quantity | Measured |
|---|---|
| Cells | 3,784 |
| Total cell area | 20,900 um^2, for eight response bits |
| Ring oscillators | 6,730 um^2 across 1,792 inverters |
| Flip-flops | 5,930 um^2 across 296 |
| Remaining logic | 8,240 um^2 - multiplexers, arbiters, counters, replicated eight times |
| Declared footprint | 1x2 tiles, 36,064 um^2, so 58 percent utilisation |

The 1,792 inverters are exactly eight blocks by thirty-two oscillators by seven
inverters, which confirms the architecture reading this document was built on.

An aside worth recording because most checks in this work have found errors. The
estimates this document previously used were close: an inverter assumed at 3.75
against 3.756 measured, a flip-flop at 22.0 against 20.03, utilisation assumed at
60 percent against 58 measured. The conclusion did not move. That is not a reason to
trust the next set of estimates, but it is worth saying when it happens.

## 2. Why naive scaling fails

Taking the declared footprint of 4,508 square micrometres per response bit, a
128-bit response needs about 577,000 - thirty-two tiles against a limit of sixteen.
It does not fit, and this is the number that matters if the architecture is taken as
given.

It should not be taken as given. The existing design instantiates a complete
measurement chain per response bit: thirty-two ring oscillators, two sixteen-to-one
multiplexers, two sixteen-bit counters and an arbiter, replicated eight times. The
oscillators are the entropy and have to be physically distinct. The counters, the
multiplexers and the arbiter are measurement apparatus and do not.

## 3. Trading time for area

Share one comparison chain and drive it sequentially. The oscillators stay
distinct; the counters and arbiter are used once per response bit rather than once
per design. A bank of n oscillators offers n(n-1)/2 distinct pairs, so 128
oscillators offer 8,128 - far more than any key needs, and the constraint moves from
oscillator count to how many pairs are independent enough to count as entropy.

## 4. A correction to the first attempt at this

The first version of this calculation assumed the error correction could run in
software on the processing system, using public helper data, leaving only the
oscillators and their readout on the tile. That is wrong, and the literature is
explicit: the post-processing belongs on the same integrated circuit, because a raw
response that leaves the die can be captured, and capturing it defeats the entire
point of a key that is never stored.

So the decoder is inside the area budget. It is also the largest single item in it.

## 5. The budget, with the decoder inside

A fuzzy extractor loses entropy to its helper data, so the raw response must be
larger than the key. Taking a 128-bit key and three multipliers for raw width:

Recomputed on measured cell areas and the measured 58 percent utilisation:

| Assumption | Raw bits | Oscillators | Area | Tiles |
|---|---|---|---|---|
| optimistic, 2x | 256 | 128 | 51,500 | 2.9 |
| typical, 3x | 384 | 256 | 65,600 | 3.6 |
| conservative, 4x | 512 | 256 | 70,000 | 3.9 |

Every input measured except the decoder, budgeted at roughly three thousand gates.
That single estimate is now the largest source of uncertainty in the table and the
only thing left to settle.

## 6. Answer

Superseded twice; see section 7 and `decoder_code_choice.md`. On the code this
document was written around it is four to nine tiles of the sixteen available, and on
the code the literature recommends the decoder falls to a quarter of one. It fits
either way. What remains open is the oscillator count, not the area.

The blocker is architectural rather than dimensional. The existing implementation
does not scale because it replicates apparatus that should be shared, not because
the process or the shuttle is too small. That is a much better position than
W-INTL-47 left open, and it is worth stating carefully rather than enthusiastically.

## 7. What this does not settle

Whether the oscillator pairs are independent enough to yield the assumed entropy on
this process. Nobody knows: the existing implementation's uniqueness, reliability
and entropy are unmeasured and its author is crowdsourcing measurements.

Whether the design holds across temperature. The author documents responses
changing until the part warms. Error correction exists to absorb that, but the code
parameters depend on the error rate, and the error rate is what nobody has measured.

Whether the decoder budget was right. It was not, and this is now measured.

A decoder was written for BCH(255,131) over GF(2^8) with the primitive polynomial
0x11D. All three stages are now measured - the syndrome bank, the Chien search and the
key-equation solver, the last of them verified against constructed error patterns
before any area was quoted from it.

| t | Syndrome + Chien | Solver | Decoder | Tiles |
|---|---|---|---|---|
| 4 | 5,694 | 17,503 | 23,197 | 1.3 |
| 8 | 10,475 | 31,620 | 42,095 | 2.3 |
| 12 | 15,350 | 45,878 | 61,228 | 3.4 |
| 18 | 22,668 | 66,847 | 89,515 | 5.0 |

The solver had been budgeted as comparable to the two stages beside it. It is nearly
three times larger, because those two multiply by compile-time constants and fold into
XOR trees while it multiplies two runtime values, about 3(t+1) times. The estimate
assumed one kind of arithmetic and got another.

Full budget with all three stages measured, everything else as in section 5:

| t | Decoder | Total | Tiles | Decoder share |
|---|---|---|---|---|
| 4 | 23,197 | 65,979 | 3.7 | 35 percent |
| 8 | 42,095 | 91,802 | 5.1 | 46 percent |
| 12 | 61,228 | 117,995 | 6.5 | 52 percent |
| 18 | 89,515 | 156,880 | 8.7 | 57 percent |

The decoder-share column in the version of this table that stood before today did not
follow from the two columns beside it - it read 36, 51, 61 and 69 percent where its own
figures give 21, 30, 35 and 40, high by a consistent factor of about 1.72 against a
denominator that cannot be reconstructed. The column above is computed from the two
beside it.

So on this code the answer is four to nine tiles rather than five to seven, and at
t=18 it takes 8.7 of the 16 a submission may use.

And the code is the wrong code. The standard reference on area-efficient helper data
extraction discards BCH before implementing it, on exactly these grounds, and its
recommended construction - a short repetition code concatenated with a first-order
Reed-Muller code - measures 4,596 square micrometres against 89,515 on this same
library, a quarter of one tile. That is a factor of 19.5, and it is set out with its
verification and its one significant catch in `decoder_code_choice.md`. The catch is
that the raw response width the construction needs is tied to a measured error rate,
and this project's error rate is unmeasured, so the saving is real and the count it
depends on is not yet known.

It still fits in sixteen. The margin is smaller than this document previously said,
and the reason is worth stating plainly: the correction strength drives everything,
and the correction strength is set by the oscillator error rate, which is the one
thing nobody has measured. At t=4 the decoder is a third of the budget; at t=18 it
is two thirds. Characterising the error rate is therefore not the first step because
it is tidy - it is the first step because it sizes the largest block on the tile.

Every one of those is a measurement rather than a question of principle, and the
first step for all three is the same: put a characterisation structure on a tile and
read it out across temperature.
