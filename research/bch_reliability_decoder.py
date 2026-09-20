#!/usr/bin/env python3
"""Finite BCH experiment with reliability-aware Chase candidates.

Status: [measured] deterministic Monte Carlo under an independent, heterogeneous
BSC model for the repository's recommended BCH(127,57,11) construction.  The
algebraic decoder is the actual binary BCH code: its generator is built from the
GF(2^7) cyclotomic cosets, and Berlekamp--Massey plus a Chien search corrects up
to t errors.  The soft variant keeps the six least reliable positions and tries
the received word plus every one-bit flip in that list.  It selects the valid
codeword with the best per-position likelihood.

This is not a BCH hardware result, an area result, or a claim about helper-data
binding.  [open conjecture] The experiment only measures whether a small
reliability-aware list can recover some words that hard algebraic decoding leaves
uncorrected.  The retention cost of reliability metadata, a larger list, and an
RTL implementation remain open.

Prior art is explicit: Maringer et al. model unequal PUF-bit reliabilities as a
Varying Binary Symmetric Channel (VBSC), and study its capacity:
https://arxiv.org/abs/2112.02198.  This file is a finite-code
reproduction/control, not a new channel theorem.
"""

from __future__ import annotations

import itertools
import math
import random


M = 7
REDUCTION = 0x09
N = (1 << M) - 1
T = 11
K = 57
TRIALS = 1000
RELIABILITY_LIST = 6


def _field():
    mask = (1 << M) - 1

    def multiply(a: int, b: int) -> int:
        result = 0
        for _ in range(M):
            if b & 1:
                result ^= a
            b >>= 1
            a = (
                ((a << 1) ^ REDUCTION) & mask
                if a & (1 << (M - 1))
                else (a << 1) & mask
            )
        return result

    def power(a: int, exponent: int) -> int:
        result = 1
        while exponent:
            if exponent & 1:
                result = multiply(result, a)
            a = multiply(a, a)
            exponent >>= 1
        return result

    return multiply, power


GF_MUL, GF_POW = _field()
ALPHA = [GF_POW(2, exponent) for exponent in range(N)]


def _generator_polynomial() -> list[int]:
    """Build the binary narrow-sense BCH generator for roots alpha^1..alpha^22."""
    seen: set[int] = set()
    polynomial = [1]  # low coefficient first
    for root_exponent in range(1, 2 * T + 1):
        if root_exponent in seen:
            continue
        coset: list[int] = []
        exponent = root_exponent
        while exponent not in coset:
            coset.append(exponent)
            seen.add(exponent)
            exponent = (2 * exponent) % N
        for exponent in coset:
            root = ALPHA[exponent]
            product = [0] * (len(polynomial) + 1)
            for index, coefficient in enumerate(polynomial):
                product[index] ^= GF_MUL(coefficient, root)
                product[index + 1] ^= coefficient
            polynomial = product
    if len(polynomial) - 1 != N - K or set(polynomial) != {0, 1}:
        raise AssertionError("generator is not the expected binary BCH polynomial")
    return polynomial


GENERATOR = _generator_polynomial()


def _evaluate(polynomial: list[int], point: int) -> int:
    value = 0
    for coefficient in reversed(polynomial):
        value = GF_MUL(value, point) ^ coefficient
    return value


def _syndromes(word: list[int]) -> list[int]:
    result = []
    for power in range(1, 2 * T + 1):
        syndrome = 0
        for position, bit in enumerate(word):
            if bit:
                syndrome ^= ALPHA[(position * power) % N]
        result.append(syndrome)
    return result


def _berlekamp_massey(syndromes: list[int]) -> tuple[list[int], int]:
    locator = [1]
    previous = [1]
    degree = 0
    shift = 1
    previous_discrepancy = 1
    for index, syndrome in enumerate(syndromes):
        discrepancy = syndrome
        for term in range(1, degree + 1):
            if term < len(locator):
                discrepancy ^= GF_MUL(locator[term], syndromes[index - term])
        if discrepancy == 0:
            shift += 1
            continue
        old_locator = locator[:]
        scale = GF_MUL(
            discrepancy, GF_POW(previous_discrepancy, (1 << M) - 2)
        )
        if len(locator) < len(previous) + shift:
            locator.extend([0] * (len(previous) + shift - len(locator)))
        for term, coefficient in enumerate(previous):
            locator[term + shift] ^= GF_MUL(scale, coefficient)
        if 2 * degree <= index:
            degree = index + 1 - degree
            previous = old_locator
            previous_discrepancy = discrepancy
            shift = 1
        else:
            shift += 1
    return locator, degree


def algebraic_decode(received: list[int]) -> list[int] | None:
    """Decode one word with the actual BCH(127,57,11) algebraic path."""
    syndromes = _syndromes(received)
    if not any(syndromes):
        return received[:]
    locator, degree = _berlekamp_massey(syndromes)
    if degree > T:
        return None
    roots = [
        position
        for position in range(N)
        if _evaluate(locator, ALPHA[(-position) % N]) == 0
    ]
    if len(roots) != degree:
        return None
    corrected = received[:]
    for position in roots:
        corrected[position] ^= 1
    return corrected if not any(_syndromes(corrected)) else None


def _encode(message: list[int]) -> list[int]:
    """Generate a valid codeword as a message polynomial times g(x)."""
    word = [0] * N
    for position, bit in enumerate(message):
        if bit:
            for offset, coefficient in enumerate(GENERATOR):
                word[position + offset] ^= coefficient
    return word


def chase_decode(received: list[int], crossover: list[float]) -> list[int] | None:
    """Try one-bit changes at the least reliable positions, then score valid words."""
    order = sorted(
        range(N), key=lambda position: crossover[position], reverse=True
    )[:RELIABILITY_LIST]
    best = None
    best_score = float("inf")
    for flips in itertools.chain(
        ((),), ((position,) for position in order)
    ):
        candidate = received[:]
        for position in flips:
            candidate[position] ^= 1
        decoded = algebraic_decode(candidate)
        if decoded is None:
            continue
        score = sum(
            -math.log(probability if decoded[position] != received[position]
                     else 1.0 - probability)
            for position, probability in enumerate(crossover)
        )
        if score < best_score:
            best_score = score
            best = decoded
    return best


def _run_case(
    name: str, groups: list[tuple[int, float]], seed: int
) -> tuple[int, int, int, int]:
    crossover = [
        probability
        for count, probability in groups
        for _ in range(count)
    ]
    if len(crossover) != N:
        raise AssertionError("case does not cover all 127 codeword positions")
    if abs(sum(crossover) / N - 0.06) > 1e-12:
        raise AssertionError("cases must have the same mean BER")

    random_source = random.Random(seed)
    hard_failures = 0
    chase_failures = 0
    hard_declines = 0
    chase_declines = 0
    for _ in range(TRIALS):
        transmitted = _encode(
            [random_source.randrange(2) for _ in range(K)]
        )
        received = [
            bit ^ int(random_source.random() < probability)
            for bit, probability in zip(transmitted, crossover)
        ]
        hard = algebraic_decode(received)
        if hard != transmitted:
            hard_failures += 1
        if hard is None:
            hard_declines += 1
        soft = chase_decode(received, crossover)
        if soft != transmitted:
            chase_failures += 1
        if soft is None:
            chase_declines += 1
    print(
        f"{name:12s} mean_ber=0.060000 frames={TRIALS} "
        f"hard_failures={hard_failures:3d} "
        f"chase_failures={chase_failures:3d} "
        f"hard_declines={hard_declines:3d} "
        f"chase_declines={chase_declines:3d}"
    )
    return hard_failures, chase_failures, hard_declines, chase_declines


def _controls() -> None:
    if len(GENERATOR) - 1 != N - K:
        raise AssertionError("generator degree control failed")
    for errors in range(T + 1):
        source = [0] * N
        for position in random.Random(9000 + errors).sample(range(N), errors):
            source[position] = 1
        if algebraic_decode(source) != [0] * N:
            raise AssertionError(f"algebraic correction failed at weight {errors}")

    cases = {
        "homogeneous": [(N, 0.06)],
        "mild": [(42, 0.01), (43, 0.06), (42, 0.11)],
        "split": [(42, 0.001), (43, 0.06), (42, 0.119)],
    }
    results = {
        name: _run_case(name, groups, 20260817 + index)
        for index, (name, groups) in enumerate(cases.items())
    }
    if any(soft > hard for hard, soft, _, _ in results.values()):
        raise AssertionError("reliability list worsened a deterministic case")
    if not results["mild"][1] < results["mild"][0]:
        raise AssertionError("mild heterogeneous control shows no soft improvement")
    if not results["split"][1] < results["split"][0]:
        raise AssertionError("split heterogeneous control shows no soft improvement")


def main() -> None:
    _controls()
    print(
        "[measured] The one-bit reliability list changes finite BCH decoding "
        "at the same mean BER; this is not a hardware or helper-data result."
    )
    print(
        "[open conjecture] Metadata retention cost, larger Chase lists, "
        "and an RTL implementation remain unmeasured."
    )


if __name__ == "__main__":
    main()
