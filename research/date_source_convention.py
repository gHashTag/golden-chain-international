#!/usr/bin/env python3
"""Re-read the DATE 2018 table instead of assigning its helper bits to a mask.

The previous model treated the DATE row's 288 helper bits as one compressed
selection mask and therefore left two symmetric mask fractions.  The cited
paper's Table 1 separates that row into a 256-bit reliability mask and a
32-bit BCH syndrome.  The paper also states that a one in its mask codeword
means that the corresponding SRAM cell is reliable and selected for key
generation.  This script keeps that source convention explicit and checks the
arithmetic.

The source has a wording mismatch worth preserving rather than smoothing:
the introduction calls 288 bits the result of bit selection with lossless
compression, while Table 1 labels 288 as the Dark-bit row and labels the
lossless row 276.  The table's selected-versus-rejected convention is resolved;
the provenance of the introductory 288-bit sentence remains [open conjecture].

Source:
https://past.date-conference.com/proceedings-archive/2018/pdf/0479.pdf

Status: [measured] from the cited table and [proved] for the arithmetic below.
This is a source-reading correction, not a claim about Golden Chain's
construction or a new security bound.
"""

import math


SOURCE_URL = (
    "https://past.date-conference.com/proceedings-archive/2018/pdf/0479.pdf"
)
# This is a source-table input, not a recommendation-derived quantity.  Keep
# the provenance in the identifier so the stale-literal guard does not confuse
# the cited row with a design output.
DATE_TABLE_ROW_POSITIONS = 1060
TABLE_MASK_BITS = 256
TABLE_SYNDROME_BITS = 32
TABLE_TOTAL_HELPER_BITS = 288


def binary_entropy(fraction):
    """Entropy of a Bernoulli mask, in bits per position."""
    if fraction <= 0.0 or fraction >= 1.0:
        return 0.0
    return -(
        fraction * math.log2(fraction)
        + (1.0 - fraction) * math.log2(1.0 - fraction)
    )


def source_row():
    """Return the Table 1 decomposition and the resolved selected fraction."""
    selected_fraction = TABLE_MASK_BITS / DATE_TABLE_ROW_POSITIONS
    rejected_fraction = 1.0 - selected_fraction
    return {
        "raw_positions": DATE_TABLE_ROW_POSITIONS,
        "mask_bits": TABLE_MASK_BITS,
        "syndrome_bits": TABLE_SYNDROME_BITS,
        "total_helper_bits": TABLE_TOTAL_HELPER_BITS,
        "selected_fraction": selected_fraction,
        "rejected_fraction": rejected_fraction,
        "mask_entropy_floor": DATE_TABLE_ROW_POSITIONS * binary_entropy(selected_fraction),
    }


def _assert_controls(row):
    """Controls that must fail if the source split or convention is changed."""
    assert row["mask_bits"] + row["syndrome_bits"] == row["total_helper_bits"]
    assert row["raw_positions"] == 1060
    assert row["mask_bits"] == 256
    assert row["syndrome_bits"] == 32
    assert abs(row["selected_fraction"] - (256.0 / 1060.0)) < 1e-15
    assert abs(row["rejected_fraction"] - (804.0 / 1060.0)) < 1e-15
    assert row["selected_fraction"] < 0.5 < row["rejected_fraction"]
    # 288 is the total row, not n*h(f).  This catches the interpretation made
    # by date_helper_ambiguity.py without erasing that earlier reproducibility
    # check or pretending that the source's mask is an iid Bernoulli draw.
    assert abs(row["mask_entropy_floor"] - 845.3939027097364) < 1e-9
    assert abs(row["mask_entropy_floor"] - row["total_helper_bits"]) > 500.0


if __name__ == "__main__":
    row = source_row()
    _assert_controls(row)
    print(
        "DATE source convention: mask codeword 1 marks a reliable SRAM cell "
        "selected for key generation"
    )
    print(
        f"Table 1 helper split: mask {row['mask_bits']} + syndrome "
        f"{row['syndrome_bits']} = {row['total_helper_bits']} bits"
    )
    print(
        f"selected raw fraction: {row['selected_fraction']:.9f} "
        f"({row['mask_bits']} of {row['raw_positions']})"
    )
    print(f"rejected raw fraction: {row['rejected_fraction']:.9f}")
    print(
        f"iid-mask entropy at that fraction: "
        f"{row['mask_entropy_floor']:.6f} bits; not the {row['total_helper_bits']}-bit total"
    )
    print(
        "[open conjecture] the introduction's separate 288-bit wording needs "
        "source-level reconciliation with Table 1"
    )
