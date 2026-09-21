#!/usr/bin/env python3
"""Re-read the 2018 DATE helper-data row through the selection-mask bound.

The source row reports 1,060 raw SRAM response bits and 288 helper-data bits after
bit selection and lossless compression, for a 128-bit key at an average BER of
10.22 percent and word failure below 1e-6. The number 288 is compatible with the
entropy of a selection mask, but entropy alone does not identify whether the
selected fraction is the small retained set or its large complement.

For a mask with n positions and retained fraction f, the asymptotic lower bound is
n*h(f), where h is binary entropy. Since h(f) = h(1-f), one helper-data total has
two symmetric solutions. This file computes both, checks the symmetry numerically,
and keeps the interpretation open until the paper's encoding convention is read.

Source:
https://past.date-conference.com/proceedings-archive/2018/pdf/0479.pdf

Status: [measured] from the cited row and [open conjecture] for which branch the
source implementation uses. The calculation is a consistency check, not a claim
about the source's internal encoding.
"""

import math


def binary_entropy(f):
    """Entropy of a Bernoulli selection mask, in bits per position."""
    if f <= 0.0 or f >= 1.0:
        return 0.0
    return -(f * math.log2(f) + (1.0 - f) * math.log2(1.0 - f))


def low_branch_for_entropy(target):
    """Return f in [0, 1/2] with h(f) = target by bisection."""
    if not 0.0 <= target <= 1.0:
        raise ValueError("binary entropy target must be in [0, 1]")
    lo, hi = 0.0, 0.5
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if binary_entropy(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def row_interpretations(n=1060, helper_bits=288):
    """Return both mask-fraction solutions and their recomputed helper totals."""
    target = helper_bits / n
    low = low_branch_for_entropy(target)
    high = 1.0 - low
    return {
        "n": n,
        "helper_bits": helper_bits,
        "entropy_per_position": target,
        "low_fraction": low,
        "high_fraction": high,
        "low_total": n * binary_entropy(low),
        "high_total": n * binary_entropy(high),
    }


def _assert_controls(result):
    """Numerical controls that must fail if the mask calculation is changed."""
    low = result["low_fraction"]
    high = result["high_fraction"]
    assert 0.0 < low < 0.5 < high < 1.0
    assert abs((low + high) - 1.0) < 1e-12
    assert abs(result["low_total"] - result["helper_bits"]) < 1e-9
    assert abs(result["high_total"] - result["helper_bits"]) < 1e-9
    assert abs(binary_entropy(low) - binary_entropy(high)) < 1e-12


if __name__ == "__main__":
    row = row_interpretations()
    _assert_controls(row)
    print("DATE row: 1,060 raw positions and 288 compressed helper bits")
    print(f"entropy per position: {row['entropy_per_position']:.9f} bits")
    print(f"low retained-fraction branch:  {row['low_fraction']:.6f} "
          f"({row['low_fraction'] * row['n']:.1f} positions)")
    print(f"high retained-fraction branch: {row['high_fraction']:.6f} "
          f"({row['high_fraction'] * row['n']:.1f} positions)")
    print(f"recomputed helper total: {row['low_total']:.6f} bits on both branches")
    print("[open conjecture] the cited source must be read to identify which branch "
          "its selection convention uses")
