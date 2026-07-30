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

# ── the shuttle ─────────────────────────────────────────────────────────────
TILE_AREA = 18_032        # specified: one Tiny Tapeout tile, 161 x 112 micrometres
TILE_LIMIT = 16           # specified: largest submission is 8x2 tiles

# measured there: the published PUF tile declares 1x2 tiles, 36,064 um^2, and holds
# 20,900 um^2 of standard cells. Same flow, same process. Cell area is not die area and
# this is the factor between them.
UTILISATION = 20_900 / 36_064

# ── the oscillator ──────────────────────────────────────────────────────────
# measured there: the same published tile, 6,730 um^2 of ring oscillators across 1,792
# inverters. Seven inverters per oscillator is that design's choice; Mansouri and Dubrova
# call ten to twenty typical, and W-INTL-92 shows tripling it changes no fit verdict.
INVERTER_AREA = 6_730 / 1_792
INVERTERS_PER_OSCILLATOR = 7
OSCILLATOR_AREA = INVERTERS_PER_OSCILLATOR * INVERTER_AREA

# ── the source ──────────────────────────────────────────────────────────────
# measured there: Wilde, Hiller and Pehl from Maiti's dataset - 512 ring oscillators on
# each of 193 Xilinx Spartan-3E parts at room temperature, paired disjointly with
# immediate neighbours, giving 241.0 bits of min-entropy in 256 response bits. The same
# paper shows this figure swinging widely with pairing distance, so it carries its
# arrangement with it. It is the tightest input in this work.
MIN_ENTROPY_BITS = 241.0
MIN_ENTROPY_OVER = 256
MIN_ENTROPY_DENSITY = MIN_ENTROPY_BITS / MIN_ENTROPY_OVER

# ── the requirement ─────────────────────────────────────────────────────────
KEY_BITS = 128            # specified: the key the registry needs
TARGET_FAILURE = 1e-6     # specified: word error probability the application allows
RAW_BUDGET = 3000         # a design choice, not a constraint: how many response bits the
                          # analysis is willing to spend, which sets the block count

# ── decoders ────────────────────────────────────────────────────────────────
# measured here, keyed by (field bits, correction strength). Every entry decoded correctly
# end to end before its area was quoted - injected errors located exactly, every weight
# from one to t, in every field. Reproduce with research/rtl/measure_all.sh.
DECODER_AREA = {
    (7, 21):  79_787,
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
# effective from 0.0600 raw, twenty-five gives 0.0104. Nine is the figure the budget uses.
ENROLMENT_READS = 9

# ── debiasing ───────────────────────────────────────────────────────────────
# measured there: Maes, van der Leest, van der Sluis and Willems, Table 2, overhead at
# bias 40/35/30/25 percent. Computed for a 1,000-bit output; the dependence runs through
# an inverse binomial, so these are the published values and the constraint is
# reimplemented in key_generator_e2e.py rather than these being rescaled.
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
