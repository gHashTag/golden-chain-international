#!/usr/bin/env python3
"""Measure how reliability metadata precision affects finite BCH decoding.

Status: [measured] deterministic finite-code experiment; [open conjecture] for helper-data
binding, hardware cost, and deployment.  W-INTL-260 measured a one-bit reliability-aware
Chase list using the exact per-position crossover probabilities.  This non-duplicating
follow-up varies only the retained reliability metadata: zero, one, two, three, or eight
bits per response position, then quantises the same known channel probabilities before
running the same one-bit candidate list on BCH(127,57,11).

The unequal-reliability channel model is prior art, not a claim here:
https://arxiv.org/abs/2112.02198
The reliability-aware decoder is a finite-code reproduction/control, not a new channel
bound.  Metadata bits are counted as an experimental input, not a helper-data construction.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bch_reliability_decoder import (  # noqa: E402
    K,
    N,
    _encode,
    algebraic_decode,
    chase_decode,
)


FRAMES = 200

CASES = {
    "homogeneous": [(N, 0.06)],
    "mild": [(42, 0.01), (43, 0.06), (42, 0.11)],
    "split": [(42, 0.001), (43, 0.06), (42, 0.119)],
}


def expand(groups: list[tuple[int, float]]) -> list[float]:
    values = [p for count, p in groups for _ in range(count)]
    if len(values) != N or abs(sum(values) / N - 0.06) > 1e-12:
        raise AssertionError("case must contain 127 positions at mean BER 0.06")
    return values


def quantise(values: list[float], bits: int) -> list[float]:
    """Uniformly quantise known reliabilities; zero bits means one scalar level."""
    levels = 1 << bits
    if bits == 0:
        return [0.06] * len(values)
    lo, hi = min(values), max(values)
    if hi == lo:
        return values[:]
    step = (hi - lo) / (levels - 1)
    return [lo + round((value - lo) / step) * step for value in values]


def run_case(values: list[float], bits: int, seed: int) -> tuple[int, int]:
    estimated = quantise(values, bits)
    rng = random.Random(seed)
    hard_failures = 0
    chase_failures = 0
    for _ in range(FRAMES):
        transmitted = _encode([rng.randrange(2) for _ in range(K)])
        received = [
            bit ^ int(rng.random() < probability)
            for bit, probability in zip(transmitted, values)
        ]
        hard = algebraic_decode(received)
        if hard != transmitted:
            hard_failures += 1
        soft = chase_decode(received, estimated)
        if soft != transmitted:
            chase_failures += 1
    return hard_failures, chase_failures


def _controls() -> dict[str, dict[int, tuple[int, int]]]:
    results: dict[str, dict[int, tuple[int, int]]] = {}
    for index, (name, groups) in enumerate(CASES.items()):
        values = expand(groups)
        by_bits = {
            bits: run_case(values, bits, 20260818 + 100 * index)
            for bits in (0, 1, 2, 3, 8)
        }
        # A homogeneous channel has no information to preserve: all quantisers are the
        # same scalar channel.  This is the control that catches a metadata-only effect.
        if name == "homogeneous" and len({pair[1] for pair in by_bits.values()}) != 1:
            raise AssertionError("homogeneous metadata control changed the decoder")
        # The finest quantiser has at least as much resolution as the one-bit metadata
        # path in this deterministic experiment.  This is a finite control, not a proof.
        if by_bits[8][1] > by_bits[1][1]:
            raise AssertionError("more metadata bits worsened the deterministic control")
        results[name] = by_bits
    # The selected-like cases must retain a measurable reduction over zero metadata; if
    # this fails, the experiment has not established a precision/cost trade-off.
    for name in ("mild", "split"):
        if results[name][3][1] >= results[name][0][1]:
            raise AssertionError(f"three metadata bits did not improve {name}")
    return results


def main() -> None:
    results = _controls()
    print("Reliability metadata precision audit [measured]")
    print("case        bits/pos  metadata_bits  mean_ber  frames  hard_failures  chase_failures")
    for name, by_bits in results.items():
        for bits in (0, 1, 2, 3, 8):
            hard, chase = by_bits[bits]
            print(f"{name:11s} {bits:8d} {bits*N:14d} 0.060000 {FRAMES:7d} "
                  f"{hard:13d} {chase:14d}")
    print("[measured] Metadata precision changes the finite BCH outcome at fixed mean BER; "
          "the table is a deterministic control, not a hardware result.")
    print("[open conjecture] Helper-data binding, metadata encoding, larger lists, and "
          "FPGA cost remain unmeasured.")


if __name__ == "__main__":
    main()
