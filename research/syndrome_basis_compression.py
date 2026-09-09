#!/usr/bin/env python3
"""Exact basis coordinates for the BCH syndrome helper.

Status: [measured] finite software control for the repository's six-block
BCH(127,57,11) chain.  The helper stores 22 GF(2^7) syndromes per block,
which is 154 emitted bits although the binary parity-check map has rank
n-k = 70.  This module derives a deterministic column basis for that map,
encodes each attainable syndrome as 70 basis coordinates, and reconstructs
the original 154-bit syndrome before decoding.

[proved] The rank and the lossless reconstruction are properties of the
finite binary linear map built from the repository's syndrome function.
[open conjecture] This is not a security proof, a leakage theorem, a deployed
wire format, a side-channel result, an area/timing result, or an FPGA result.
The compression is an engineering reproduction of the familiar syndrome
construction; it is not claimed as new cryptographic prior art.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from key_generator_e2e import (  # noqa: E402
    BLOCKS,
    N,
    T,
    decode_block,
    enrol,
    regenerate,
    syndromes,
)

SYNDROME_BITS = 2 * T * 7
TRIALS = 64
SEED = 20260820


def _syndrome_to_int(values: list[int]) -> int:
    if len(values) != 2 * T or any(not 0 <= value < 128 for value in values):
        raise AssertionError("invalid BCH syndrome vector")
    text = "".join(f"{value:07b}" for value in values)
    return int(text, 2)


def _int_to_syndrome(value: int) -> list[int]:
    if value < 0 or value.bit_length() > SYNDROME_BITS:
        raise AssertionError("syndrome integer is outside its fixed width")
    text = f"{value:0{SYNDROME_BITS}b}"
    return [int(text[offset:offset + 7], 2)
            for offset in range(0, SYNDROME_BITS, 7)]


def _one_hot_syndrome(position: int) -> int:
    if not 0 <= position < N:
        raise AssertionError("response position outside BCH block")
    bits = [0] * N
    bits[position] = 1
    return _syndrome_to_int(syndromes(bits))


def _build_basis() -> tuple[list[int], dict[int, tuple[int, int]]]:
    """Return independent columns and a reduction table over GF(2)."""
    columns: list[int] = []
    reduced: dict[int, tuple[int, int]] = {}
    for position in range(N):
        vector = _one_hot_syndrome(position)
        coordinates = 1 << len(columns)
        for pivot in sorted(reduced, reverse=True):
            if (vector >> pivot) & 1:
                old_vector, old_coordinates = reduced[pivot]
                vector ^= old_vector
                coordinates ^= old_coordinates
        if vector:
            pivot = vector.bit_length() - 1
            reduced[pivot] = (vector, coordinates)
            columns.append(_one_hot_syndrome(position))
    return columns, reduced


BASIS_COLUMNS, REDUCED_BASIS = _build_basis()
RANK = len(BASIS_COLUMNS)


def coordinates_for(values: list[int]) -> int:
    """Map an attainable 154-bit syndrome to its 70-bit basis coordinates."""
    vector = _syndrome_to_int(values)
    coordinates = 0
    for pivot in sorted(REDUCED_BASIS, reverse=True):
        if (vector >> pivot) & 1:
            old_vector, old_coordinates = REDUCED_BASIS[pivot]
            vector ^= old_vector
            coordinates ^= old_coordinates
    if vector:
        raise AssertionError("syndrome is outside the BCH parity-check image")
    if coordinates.bit_length() > RANK:
        raise AssertionError("coordinate width exceeded the measured rank")
    return coordinates


def syndrome_for_coordinates(coordinates: int) -> list[int]:
    """Reconstruct the fixed-width syndrome from its basis coordinates."""
    if coordinates < 0 or coordinates.bit_length() > RANK:
        raise AssertionError("coordinate integer outside the rank-sized space")
    vector = 0
    for index, column in enumerate(BASIS_COLUMNS):
        if (coordinates >> index) & 1:
            vector ^= column
    return _int_to_syndrome(vector)


def pack_helper(helper: list[list[int]]) -> bytes:
    """Pack six 70-bit coordinate words with no per-block padding."""
    if len(helper) != BLOCKS:
        raise AssertionError("unexpected number of BCH blocks")
    words = [coordinates_for(block) for block in helper]
    bit_string = "".join(f"{word:0{RANK}b}" for word in words)
    return int(bit_string, 2).to_bytes((len(bit_string) + 7) // 8, "big")


def unpack_helper(data: bytes) -> list[list[int]]:
    """Unpack the canonical 420-bit helper; only leading byte padding is allowed."""
    expected_bits = BLOCKS * RANK
    expected_bytes = (expected_bits + 7) // 8
    if len(data) != expected_bytes:
        raise AssertionError("unexpected compressed helper byte length")
    value = int.from_bytes(data, "big")
    if value.bit_length() > expected_bits:
        raise AssertionError("non-zero padding bits in compressed helper")
    text = f"{value:0{expected_bits}b}"
    return [syndrome_for_coordinates(
        int(text[offset:offset + RANK], 2)
    ) for offset in range(0, expected_bits, RANK)]


def run() -> dict[str, int | float]:
    if RANK != N - 57:
        raise AssertionError(f"unexpected BCH parity-check rank: {RANK}")
    raw_bits = BLOCKS * SYNDROME_BITS
    compressed_bits = BLOCKS * RANK
    rng = random.Random(SEED)
    exact_round_trips = 0
    decode_agreements = 0
    coordinate_mutations = 0
    for _ in range(TRIALS):
        enrolled, helper = enrol(rng, 0.35)
        packed = pack_helper(helper)
        restored = unpack_helper(packed)
        if restored != helper:
            raise AssertionError("basis compression changed a syndrome helper")
        exact_round_trips += 1
        noisy = regenerate(rng, enrolled, 0.02)
        full_recovered = [decode_block(block, expected)
                          for block, expected in zip(noisy, helper)]
        compressed_recovered = [decode_block(block, expected)
                               for block, expected in zip(noisy, restored)]
        if compressed_recovered != full_recovered:
            raise AssertionError("compressed and full helpers changed decoder output")
        decode_agreements += 1
        # Every coordinate is independent by construction: flipping one must
        # produce a different reconstructed syndrome, not a silent alias.
        words = [coordinates_for(block) for block in helper]
        for block_index in range(BLOCKS):
            for coordinate_index in range(RANK):
                altered = words[:]
                altered[block_index] ^= 1 << coordinate_index
                altered_helper = [syndrome_for_coordinates(word) for word in altered]
                if altered_helper == helper:
                    raise AssertionError("a coordinate mutation aliased the helper")
                coordinate_mutations += 1
    return {
        "seed": SEED,
        "trials": TRIALS,
        "rank_per_block": RANK,
        "raw_syndrome_bits": raw_bits,
        "compressed_coordinate_bits": compressed_bits,
        "raw_wire_bytes": (raw_bits + 7) // 8,
        "compressed_wire_bytes": (compressed_bits + 7) // 8,
        "semantic_bits_saved": raw_bits - compressed_bits,
        "wire_bytes_saved": (raw_bits + 7) // 8 - (compressed_bits + 7) // 8,
        "semantic_reduction_percent": 100.0 * (raw_bits - compressed_bits) / raw_bits,
        "exact_round_trips": exact_round_trips,
        "decode_agreements": decode_agreements,
        "coordinate_mutations": coordinate_mutations,
    }


def main() -> None:
    result = run()
    print("BCH syndrome basis compression control [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[proved] The derived rank-sized coordinates reconstruct every sampled syndrome exactly.")
    print("[open conjecture] No leakage, security, hardware, or deployed wire-format claim is made.")


if __name__ == "__main__":
    main()
