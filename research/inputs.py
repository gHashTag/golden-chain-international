"""Every measured or borrowed input, declared once.

Written after W-INTL-99, where a utilisation factor was measured, recorded, applied in one
document and then absent from every figure computed in the next. Nothing was overwritten
and no step was wrong: the value simply did not make the journey between files. An audit
then found each of these quantities living in three to seven places.

The fix for that is not vigilance. It is that the number appears once and everything else
imports it.

Every entry below carries where it came from, because a constant without a provenance is
the thing that drifts. Three categories:

  measured here  - synthesis or simulation in this repository, reproducible by
                   research/rtl/measure_all.sh
  measured there - somebody else's measurement, with the conditions it was taken under
  specified      - a published specification rather than a measurement
"""

# ── the toolchain ───────────────────────────────────────────────────────────
# Every area here is a synthesis result, and a synthesis result is a property of the
# tool as much as of the circuit. The first run of verify_inputs.py on a machine that
# was not this one reported all twenty-two areas as mismatches, by up to seven percent
# in both directions, because the runner's yosys was a different version. Nothing was
# wrong with the circuits and nothing was wrong with the declarations; the toolchain had
# never been declared, so "these figures reproduce" silently meant "on this laptop".
#
# Declared here so that a version difference reports itself as a version difference
# instead of as twenty-two wrong numbers.
TOOLCHAIN = {"yosys": "0.65"}

# Which declared areas move between yosys versions, measured rather than assumed. Under
# 0.67+111, nineteen of the twenty-two reproduce exactly and these three differ by at
# most 0.259 percent - all of them the shared-multiplier solver, which is the design's
# only stage with resource sharing and therefore the only one where the mapper has
# choices to make differently.
#
# Named individually so that a tolerance applies where it is earned and nowhere else: a
# blanket tolerance would have let the other nineteen drift silently.
VERSION_SENSITIVE = {("decoder_serial", 7, 7), ("decoder_serial", 7, 11),
                     ("decoder_serial", 7, 13), ("decoder_serial", 7, 21)}

# ── the shuttle ─────────────────────────────────────────────────────────────
TILE_AREA = 18_032        # specified: one Tiny Tapeout tile, 161 x 112 micrometres
TILE_LIMIT = 16           # specified: largest submission is 8x2 tiles

# measured there: the published PUF tile declares 1x2 tiles, 36,064 um^2, and holds
# 20,900 um^2 of standard cells. Same flow, same process. Cell area is not die area and
# this is the factor between them.
# units: standard-cell area / die area, both square micrometres
UTILISATION = 20_900 / 36_064

# ── the oscillator ──────────────────────────────────────────────────────────
# measured there: the same published tile, 6,730 um^2 of ring oscillators across 1,792
# inverters. Cross-checked against the library everything else here is measured on:
# sky130_fd_sc_hd__inv_1 is 3.7522 um^2 and this figure is 3.7556, a ratio of 1.0009. The
# published tile's oscillators are built from drive-1 inverters and nothing was lost in
# the borrowing. Forty loops of budgets rested on that and it had never been checked. Seven inverters per oscillator is that design's choice; Mansouri and Dubrova
# call ten to twenty typical, and W-INTL-92 shows tripling it changes no fit verdict.
# units: square micrometres / inverters, giving square micrometres per inverter
INVERTER_AREA = 6_730 / 1_792
INVERTERS_PER_OSCILLATOR = 7

# estimated here, and labelled as an estimate rather than a measurement. W-INTL-154 makes
# an aging-resistant oscillator a requirement rather than an option: a conventional bank
# loses a third of its bits over ten years and the design tolerates 9.2 percent.
#
# The aging-resistant design in Rahman et al. is a conventional ring with two extra nMOS
# transistors per stage - one to stop oscillation, one to hold the inverter input at
# VDD - VT while idle so the pMOS never sees a zero. Their sizes are stated: inverters at
# Wn = 0.12u with Wp = 2.5 Wn, and gates of 0.12u and 0.24u for the two additions. By
# transistor width that is (0.42 + 0.36) / 0.42.
#
# Two approximations stacked, both stated: transistor width is not layout area, and the
# base figure it multiplies is itself an inverter count from a published tile.
#
# Bracketed against the library rather than left unbounded. A tristate inverter is an
# inverter with two extra series devices, which is the same device count the ARO adds
# though not the same placement: sky130_fd_sc_hd__einvn_0 is 1.333 times inv_1 and
# einvn_1 is 1.666. So the layout cost of two added devices in this library sits between
# 1.33 and 1.67, and the 1.857 in use is conservative by eleven to forty percent. The
# ratio is kept rather than replaced, because a tristate inverter is an analogue and not
# the circuit; what the bracket buys is knowing which way the estimate errs. A layout
# would settle it.
# units: transistor width / transistor width - and it multiplies an AREA, which is the
# mismatch W-INTL-167 names. Widths and laid-out areas do not scale together, which is
# why the library bracket below disagrees with it. Kept because it is the conservative
# end; adopting the area-grounded 1.67 would shrink the budget, and the convenient
# direction is not the one to move in on an unmeasured quantity.
AGING_RESISTANT_FACTOR = (0.12 + 0.30 + 0.12 + 0.24) / (0.12 + 0.30)

OSCILLATOR_AREA = (INVERTERS_PER_OSCILLATOR * INVERTER_AREA
                   * AGING_RESISTANT_FACTOR)

# ── the source ──────────────────────────────────────────────────────────────
# measured there: Wilde, Hiller and Pehl from Maiti's dataset - 512 ring oscillators on
# each of 193 Xilinx Spartan-3E parts at room temperature, paired disjointly with
# immediate neighbours, giving 241.0 bits of min-entropy in 256 response bits. The same
# paper shows this figure swinging widely with pairing distance, so it carries its
# arrangement with it. It is the tightest input in this work.
#
# It is measured on UNSELECTED positions, and the design selects. Reliable-bit
# selection discards the positions whose difference is closest to zero, which are the
# positions least committed to a value - so the survivors are more biased than the
# population and this density does not describe them. Delvaux et al. state it in their
# abstract, "we disprove the intuitive assumption that bit selection schemes have no
# leakage", and name global thresholding as the scheme that amplifies bias the most.
# research/selection_entropy.py computes the amplification in this project's own source
# model: at the twenty percent the design discards, 0.9414 becomes 0.9293.
MIN_ENTROPY_BITS = 241.0
MIN_ENTROPY_OVER = 256
# units: bits of min-entropy / response bits
MIN_ENTROPY_DENSITY = MIN_ENTROPY_BITS / MIN_ENTROPY_OVER

# the fraction of positions the recommendation discards: 477 raw, 381 selected. The
# density above applies before this and not after it.
# units: positions / positions
#
# The fraction is not a free parameter. Enrolment ranks by how lopsided a majority vote
# was, so the attainable fractions are the discrete vote margins, and the deepest is the
# share of positions that never voted unanimously. At twenty-five reads that floor is
# 54.4 percent kept; forty percent, which the previous loop specified, is not reachable by
# this mechanism at any read count near it - discarding further means tie-breaking at
# random among positions the vote cannot separate, which buys nothing. W-INTL-188.
#
# So the read count is the parameter and the fraction follows from it. Twenty-five reads,
# keep the positions that were not unanimous: 54.4 percent, 701 raw positions for 381
# selected, and a ten-year effective rate of 0.0064 against 0.0442 tolerated - a margin of
# 6.9 where nine reads give 2.4.
#
# That quantisation is a property of ranking by a vote of sign bits, and W-INTL-189 shows
# it is avoidable: this project's characterisation structure emits frequency counts, and
# ranking by the averaged difference is continuous, tracks the ideal bound, and gives
# 0.0039 at the same 54.4 percent - a margin of 11.3 rather than 6.9, at the same area.
# The positions and the area below are unchanged because the count-based ranking is a
# provisioning-flow choice, not a die-area one; what it costs is that the part must expose
# counts during enrolment and disable that interface afterwards.
SELECTION_LOSS = 1 - 381 / 701

# ── the requirement ─────────────────────────────────────────────────────────
KEY_BITS = 128            # specified: the key the registry needs
TARGET_FAILURE = 1e-6     # specified: word error probability the application allows

# A design rule rather than a measurement, and the reason is written here because the
# number is a judgement. The aging input - 7.73 percent ten-year flip rate for an
# aging-resistant bank - is the least trustworthy figure in this work: simulated, at 90 nm,
# for a cell this design does not use. A construction that meets the requirement with two
# percent to spare on that figure is not meeting it.
#
# So a candidate must absorb at least this multiple of the published rate. At 1.25,
# BCH(127,78,7) in two blocks is excluded - it is 26 percent smaller and absorbs 8.4
# percent against 7.73 published - and BCH(127,57,11) in three blocks is admitted at 10.9.
#
# The cost is 0.9 of a tile out of 12.5 spare. Area stopped binding four loops ago and the
# aging input did not, which is the whole of the argument. W-INTL-196.
AGING_HEADROOM = 1.25
# Vestigial as of W-INTL-193: it feeds only cheapest(), which is kept solely as the
# guard on the utilisation factor and is no longer the source of any recommended
# figure. Left declared rather than deleted so that the guard keeps its provenance.
RAW_BUDGET = 3000         # a design choice, not a constraint: how many response bits the
                          # analysis is willing to spend, which sets the block count

# ── decoders ────────────────────────────────────────────────────────────────
# measured here, keyed by (field bits, correction strength). Every entry decoded correctly
# end to end before its area was quoted - injected errors located exactly, every weight
# from one to t, in every field. Reproduce with research/rtl/measure_all.sh.
DECODER_AREA = {
    (7, 7):   27_857,   # tables 6,708 + parallel solver 21,149
    (7, 11):  42_069,   # tables 11,021 + parallel solver 31,048
    (7, 13):  50_143,   # tables 13,448 + parallel solver 36,695
    (7, 21):  79_787,   # tables 22,215 + parallel solver 57,571
    (7, 23):  86_896,
    (7, 27): 102_267,
    (7, 31): 116_194,
    (8, 18):  90_254,
    (8, 30): 147_563,
    (8, 31): 152_170,
    (8, 42): 206_630,
    (8, 43): 211_985,
    (8, 45): 222_024,
    (8, 47): 231_431,
    (8, 55): 268_820,
    (9, 54): 304_465,
}

# measured here, same convention but with the shared-multiplier solver in place of the
# replicated one. The recommendation is built from this table, not the one above.
#
# The two were mixed for one loop: 24,659 and 28,958 were entered into DECODER_AREA,
# whose verifier measures the parallel solver, so the declaration named one circuit and
# the verifier synthesised another. Both numbers were right and neither described what
# the dictionary said it described. scripts/verify_inputs.py checks this table too now,
# which is what found it.
DECODER_AREA_SERIAL = {
    (7, 7):   16_333,   # tables 6,708 + serial solver 9,625 - the recommendation
    (7, 11):  24_659,   # tables 11,021 + serial solver 13,638 - the recommendation
    (7, 13):  28_958,   # tables 13,448 + serial solver 15,510
    (7, 21):  44_346,   # tables 22,215 + serial solver 22,131
}


def decoder_area(m, t):
    """The area the design would pay: the shared-multiplier solver where measured."""
    return DECODER_AREA_SERIAL.get((m, t), DECODER_AREA.get((m, t)))


# measured here: the two SLLC stages, the systematic encoder and the unmask, keyed by
# correction strength because the generator's degree is n-k and so is the register's.
#
# This was a bare literal in one script for five loops - 4,745 - and it was the figure
# for BCH(127,29,21), whose generator has degree 98. The recommendation is
# BCH(127,57,11), degree 70. The budget had been paying for the wrong encoder since the
# code changed, and paying too much, so the error was in the conservative direction and
# would not have shown up as a fit failure.
#
# The encoder is now generated from the code parameters by gen_sllc.py rather than
# transcribed, and checked against a software polynomial division on 24 random
# information words before its area is quoted - it had no testbench at all. The
# generated t=21 encoder reproduces the hand-written file it replaces to within one
# square micrometre, which is what makes the replacement safe to make.
SLLC_AREA = {7: 2_158, 11: 3_176, 21: 4_746}

# measured here: the characterisation structure's readout for a 272-oscillator bank, and
# the smaller variant. The oscillators themselves are not synthesised - a ring oscillator
# is a physical structure, not a logic cell - and are scaled from INVERTER_AREA above.
CHARACTERISER_AREA = {272: 5_223, 64: 3_435}

# measured here: the helper-data manipulation countermeasure. SPONGENT-88/80/8's
# permutation, one round per clock. This replaces a figure borrowed from the thesis - 85
# slices on a Spartan-3E - which was the last number in this project taken from a paper
# rather than measured on the right library. Diffusion verified before the area was quoted:
# one input bit changes a mean of 46.5 of 88 output bits, and two injected faults fail it.
COUNTERMEASURE_AREA = {"spongent_round": 2_215, "spongent_permutation": 6_215}

# measured here: the key-equation solver with its multipliers shared rather than
# replicated. The parallel form instantiates 3(t+1) general multipliers - 66 at t=21 - and
# was 78 percent of the decoder while the decoder was 87 percent of the design. Sharing two
# multipliers across about 1,850 cycles costs 185 microseconds once at power-up and saves
# 62 percent of the solver. Verified differentially against the parallel solver on every
# error weight, and an injected fault in the serial version alone fails all 42 cases.
SOLVER_AREA = {"parallel_t21_m7": 57_571, "serial_t21_m7": 22_131}

# a requirement on the provisioning flow, not an implementation detail. Reliable-bit
# selection ranks positions by repeated reads, and the ranking quality is what sets the
# effective error rate: one read makes selection counterproductive, nine gives 0.0133
# effective from 0.0600 raw, twenty-five gives 0.0104. Twenty-five is the figure the
# budget uses, because nine leaves a margin of 1.10 at ten years - see W-INTL-185.
ENROLMENT_READS = 25

# ── the source, over time ───────────────────────────────────────────────────
# measured here, in the sense that 0.06 is the fresh-device figure this project has used
# throughout and every effective rate is computed from it. It lived as a literal in four
# files until W-INTL-198, which is the arrangement this file exists to prevent - and it
# was invisible to the input-coverage sweep for exactly as long, because a literal is not
# a declared input.
RAW_NOISE_BER = 0.06

# measured there: Rahman, Forte, Fahrny and Tehranipoor, DATE 2014. Response-bit flip
# rates at ten years - HSPICE Monte Carlo, 100 chip instances, 90 nm, 64 oscillators,
# 23 percent activation time. Simulation rather than silicon, and not this process. The
# conventional figure was written out in two files and the resistant one in one.
AGED_FLIP_CONVENTIONAL = 0.3241
AGED_FLIP_RESISTANT = 0.0773

# ── debiasing ───────────────────────────────────────────────────────────────
# measured there: Maes, van der Leest, van der Sluis and Willems, Table 2, overhead at
# bias 40/35/30/25 percent. Computed for a 1,000-bit output; the dependence runs through
# an inverse binomial, so these are the published values and the constraint is
# reimplemented in key_generator_e2e.py rather than these being rescaled.
# units: raw bits in / retained bits out
DEBIAS_OVERHEAD = {
    "CVN":      {40: 4.40, 35: 4.40, 30: 5.30, 25: 5.30},
    "2O-VN":    {40: 2.31, 35: 2.45, 30: 2.66, 25: 2.99},
    "2P-TO-VN": {40: 1.58, 35: 1.73, 30: 1.96, 25: 2.32},
}
# e-2O-VN has overhead 1.00 and is the only reusable method, and W-INTL-71 shows it is
# not constructible here at any entropy density - the inner repetition code it needs
# cannot carry the information the key requires. Recorded as absent rather than as a
# number.
REUSABLE_DEBIASING_AVAILABLE = False


def tiles(cell_area):
    """Die area in tiles. Cell area is not die area; see UTILISATION."""
    return cell_area / UTILISATION / TILE_AREA


def fits(cell_area):
    return tiles(cell_area) <= TILE_LIMIT
