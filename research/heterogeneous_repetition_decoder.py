#!/usr/bin/env python3
"""Exact finite-length decoder check for heterogeneous PUF reliabilities.

Status: [measured] exact enumeration under an independent BSC model; [open conjecture]
for transfer to the project's BCH construction.  W-INTL-258 separated parallel-channel
capacity from the scalar effective-BER proxy.  This file closes one narrow remainder:
for a 15-fold repetition word it computes the word-error probability exactly for
(a) hard majority using only the mean BER and (b) a reliability-aware weighted LLR
rule using the per-position BERs.  It is not a BCH or convolutional decoder result.

The Varying Binary Symmetric Channel model and its capacity comparison are prior art:
https://arxiv.org/abs/2112.02198.  The calculation here is a finite repetition-code
reproduction/control, not a new channel theorem.
"""

import math


SOURCE_URLS = ("https://arxiv.org/abs/2112.02198",)
N = 15


def _binomial(n, k, p):
    return math.comb(n, k) * p**k * (1.0 - p)**(n - k)


def hard_majority_error(ps):
    """Exact word error for an odd repetition word and hard majority."""
    # Poisson-binomial dynamic program for the number of flipped positions.
    dist = [1.0] + [0.0] * len(ps)
    for p in ps:
        for k in range(len(ps), 0, -1):
            dist[k] = dist[k] * (1.0 - p) + dist[k - 1] * p
        dist[0] *= 1.0 - p
    return sum(dist[(len(ps) // 2) + 1:])


def _product_ranges(counts):
    values = [[]]
    for count in counts:
        values = [prefix + [k] for prefix in values for k in range(count + 1)]
    return values


def grouped_weighted_error(groups):
    weights = [math.log((1.0 - p) / p) for _, p in groups]
    error = 0.0
    for counts in _product_ranges([count for count, _ in groups]):
        probability = 1.0
        score = 0.0
        for index, ((count, p), flipped) in enumerate(zip(groups, counts)):
            probability *= _binomial(count, flipped, p)
            score += (count - 2 * flipped) * weights[index]
        if score < 0.0:
            error += probability
        elif abs(score) < 1e-15:
            error += 0.5 * probability
    return error


def _assert_controls():
    homogeneous = [(5, 0.06), (5, 0.06), (5, 0.06)]
    flat = [0.06] * N
    assert abs(hard_majority_error(flat) - grouped_weighted_error(homogeneous)) < 1e-12

    mild = [(5, 0.01), (5, 0.06), (5, 0.11)]
    split = [(5, 0.001), (5, 0.06), (5, 0.119)]
    for groups in (mild, split):
        assert abs(sum(count * p for count, p in groups) / N - 0.06) < 1e-12
        # Mean-only majority is the same scalar baseline for both mixtures.
        assert grouped_weighted_error(groups) <= hard_majority_error([0.06] * N)
    assert grouped_weighted_error(split) < grouped_weighted_error(mild)


def main():
    _assert_controls()
    cases = {
        "homogeneous_6pct": [(5, 0.06), (5, 0.06), (5, 0.06)],
        "mild_same_mean": [(5, 0.01), (5, 0.06), (5, 0.11)],
        "split_same_mean": [(5, 0.001), (5, 0.06), (5, 0.119)],
    }
    scalar = hard_majority_error([0.06] * N)
    print("Heterogeneous repetition decoder audit [measured]")
    print("case                 mean BER  scalar majority  weighted LLR  delta")
    for name, groups in cases.items():
        mean = sum(count * p for count, p in groups) / N
        weighted = grouped_weighted_error(groups)
        print(f"{name:20s} {mean:9.6f} {scalar:15.9f} {weighted:13.9f} {scalar-weighted:9.9f}")
    print("[open conjecture] the finite-length effect for the project's BCH construction "
          "still needs a decoder-specific experiment")


if __name__ == "__main__":
    main()
