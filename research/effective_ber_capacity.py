#!/usr/bin/env python3
"""Measure the loss from replacing per-position BERs by one effective BER.

Status: [measured] numerical control; [open conjecture] for any downstream coding
benefit.  The current design and the comparison rows report one average BER, but
selection produces a heterogeneous population of channels.  This file keeps the
parallel-channel capacity and the scalar-BER proxy side by side, so the proxy is not
read as an achievable bound.

The calculation is deliberately independent of theory_bounds.py: it samples explicit
per-position crossover probabilities, evaluates each binary symmetric channel, and
compares that sum with the channel obtained after averaging the probabilities.  It does
not claim a new converse or a code-performance result.

Literature context:
- https://arxiv.org/abs/2502.03221 (converse bounds; prior art, not a new result here)
- https://past.date-conference.com/proceedings-archive/2018/pdf/0479.pdf (the DATE row
  whose helper-data and BER comparison motivated the audit)
"""

import math


SOURCE_URLS = (
    "https://arxiv.org/abs/2502.03221",
    "https://past.date-conference.com/proceedings-archive/2018/pdf/0479.pdf",
)


def binary_entropy(p):
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def parallel_capacity(crossovers):
    """Capacity sum in bits for independent BSCs, one bit per position."""
    return sum(1.0 - binary_entropy(p) for p in crossovers)


def scalar_capacity(crossovers):
    """Capacity after collapsing the population to its arithmetic mean BER."""
    values = tuple(crossovers)
    return len(values) * (1.0 - binary_entropy(sum(values) / len(values)))


def capacity_gap(crossovers):
    exact = parallel_capacity(crossovers)
    proxy = scalar_capacity(crossovers)
    return {"exact": exact, "proxy": proxy, "gap": exact - proxy}


def _assert_controls():
    # Homogeneous channels have no Jensen gap.
    homogeneous = (0.06,) * 1000
    same = capacity_gap(homogeneous)
    assert abs(same["gap"]) < 1e-12

    # A selected population with the same mean BER can have different capacity.
    # The two mixtures are deliberately mean-matched: the scalar report cannot tell
    # them apart, while the explicit channels can.
    mild = (0.03,) * 500 + (0.09,) * 500
    split = (0.001,) * 500 + (0.119,) * 500
    a = capacity_gap(mild)
    b = capacity_gap(split)
    assert abs(sum(mild) / len(mild) - sum(split) / len(split)) < 1e-15
    assert abs(a["proxy"] - b["proxy"]) < 1e-12
    assert a["gap"] > 0.0 and b["gap"] > a["gap"]

    # The current raw-error operating point is also a concrete check: a 20/80
    # population with mean 0.06 is not equivalent to a homogeneous 0.06 channel.
    selected_like = (0.01,) * 400 + (0.09333333333333334,) * 600
    current = capacity_gap(selected_like)
    assert abs(sum(selected_like) / len(selected_like) - 0.06) < 1e-12
    assert current["gap"] > 1.0


def main():
    _assert_controls()
    cases = {
        "homogeneous_6pct": (0.06,) * 1000,
        "mean_matched_mild": (0.03,) * 500 + (0.09,) * 500,
        "mean_matched_split": (0.001,) * 500 + (0.119,) * 500,
        "selected_like_mean_6pct": (0.01,) * 400 + (0.09333333333333334,) * 600,
    }
    print("Effective-BER capacity audit [measured]")
    print("case                         mean BER  exact bits  scalar bits  gap bits")
    for name, crossovers in cases.items():
        result = capacity_gap(crossovers)
        mean = sum(crossovers) / len(crossovers)
        print(f"{name:28s} {mean:9.6f} {result['exact']:11.6f} "
              f"{result['proxy']:11.6f} {result['gap']:9.6f}")
    print("[open conjecture] translating the capacity gap into finite-length BCH or "
          "convolutional-code performance needs a decoder experiment")


if __name__ == "__main__":
    main()
