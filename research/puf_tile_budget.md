# Does a Usable Identity Root Fit on a Tile

Status: written 2026-07-30. Answers the question left open by audit W-INTL-47,
which found that the primitive has been fabricated on the process this project
already uses but at eight bits of response, and did not establish whether a usable
one fits in the area a shuttle allows.

Confirmed by synthesis on 2026-07-30. The published implementation was cloned and
run through yosys against the real SkyWater standard-cell library, typical corner,
25 C, 1.8 V. Every cell area below is measured except the error-correction decoder,
which remains an estimate and is flagged where it appears.

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

Three to five tiles of the sixteen available. It fits, with room.

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

Whether three thousand gates is the right decoder budget. It is the one input here
that synthesis has not replaced, and at eighteen thousand square micrometres it is
around half the total. Published designs correct on the order of seventeen errors in
a three-hundred-bit codeword; matching a measured error rate may need more. Writing
and synthesising a decoder would close this the same way the rest closed.

Every one of those is a measurement rather than a question of principle, and the
first step for all three is the same: put a characterisation structure on a tile and
read it out across temperature.
