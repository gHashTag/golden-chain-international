# Does a Usable Identity Root Fit on a Tile

Status: written 2026-07-30. Answers the question left open by audit W-INTL-47,
which found that the primitive has been fabricated on the process this project
already uses but at eight bits of response, and did not establish whether a usable
one fits in the area a shuttle allows.

Every cell area below is an estimate. The conclusion should be confirmed by
synthesis, not by this document.

---

## 1. The numbers that are not estimates

A Tiny Tapeout 1x1 tile is about 161 by 112 micrometres, so 18,032 square
micrometres. The largest block a submission may take is 8x2, sixteen tiles, about
288,512 square micrometres.

The existing eight-bit implementation declares 1x2 tiles. That is 36,064 square
micrometres for eight response bits, or about 4,508 per bit.

## 2. Why naive scaling fails

At 4,508 square micrometres per response bit, a 128-bit response needs about
577,000 - thirty-two tiles against a limit of sixteen. It does not fit, and this is
the number that matters if the architecture is taken as given.

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

| Assumption | Raw bits | Oscillators | Estimated area | Tiles |
|---|---|---|---|---|
| optimistic, 2x | 256 | 128 | 52,600 | 2.9 |
| typical, 3x | 384 | 256 | 66,700 | 3.7 |
| conservative, 4x | 512 | 256 | 73,700 | 4.1 |

At sixty percent utilisation, and with a decoder budgeted at roughly three thousand
gates.

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

Whether three thousand gates is the right decoder budget. Published designs correct
on the order of seventeen errors in a three-hundred-bit codeword; matching a
measured error rate may need more.

Every one of those is a measurement rather than a question of principle, and the
first step for all three is the same: put a characterisation structure on a tile and
read it out across temperature.
