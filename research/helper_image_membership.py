#!/usr/bin/env python3
"""Finite-domain control for the BCH syndrome helper.

Status: [measured] software control for the repository's six-block
BCH(127,57,11) chain.  A 22-symbol GF(2^7) helper has 154 emitted bits,
but the syndrome map from 127 response bits has a 70-dimensional binary
image.  This control tests the boundary that follows from that fact: an
enrolled helper is accepted by the rank coordinates, while arbitrary
154-bit words are rejected as non-syndromes.

[proved] The image codimension is 154 - rank, and binary elimination gives
an exact membership decision for the finite map used here.
[open conjecture] Rejection of non-syndromes is not a security claim, a
leakage bound, collision resistance, an active-attacker result, a deployed
wire-format recommendation, or an FPGA area/timing result.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from key_generator_e2e import BLOCKS, N, T, enrol, syndromes  # noqa: E402
from syndrome_basis_compression import (  # noqa: E402
    RANK,
    coordinates_for,
    _int_to_syndrome,
    _syndrome_to_int,
)

SEED = 20260821
VALID_TRIALS = 64
RANDOM_TRIALS = 256
PERTURB_TRIALS = 256
SYNDROME_BITS = 2 * T * 7
CODIMENSION = SYNDROME_BITS - RANK


def _membership(value: int) -> bool:
    """Return whether a fixed-width syndrome integer is in the binary image."""
    if value < 0 or value.bit_length() > SYNDROME_BITS:
        return False
    try:
        coordinates_for(_int_to_syndrome(value))
    except AssertionError:
        return False
    return True


def run() -> dict[str, int | float]:
    rng = random.Random(SEED)
    valid_helpers = 0
    random_rejected = 0
    perturbed_rejected = 0
    perturbed_still_valid = 0
    # Valid helpers come from actual response words, not arbitrary chosen vectors.
    for _ in range(VALID_TRIALS):
        _, helper = enrol(rng, 0.35)
        for block in helper:
            if not _membership(_syndrome_to_int(block)):
                raise AssertionError("an enrolled BCH syndrome was rejected")
            valid_helpers += 1

    for _ in range(RANDOM_TRIALS):
        candidate = rng.getrandbits(SYNDROME_BITS)
        if _membership(candidate):
            raise AssertionError("a random ambient syndrome passed membership")
        random_rejected += 1

    # Flip one symbol bit in a valid helper.  This is not a security experiment;
    # it checks that the precheck distinguishes the finite image from nearby
    # arbitrary words instead of merely recognizing the all-zero case.
    for _ in range(PERTURB_TRIALS):
        _, helper = enrol(rng, 0.35)
        block = helper[rng.randrange(BLOCKS)]
        value = _syndrome_to_int(block)
        bit = rng.randrange(SYNDROME_BITS)
        altered = value ^ (1 << bit)
        if _membership(altered):
            perturbed_still_valid += 1
        else:
            perturbed_rejected += 1

    ambient = 1 << SYNDROME_BITS
    image = 1 << RANK
    return {
        "seed": SEED,
        "blocks": BLOCKS,
        "valid_trials": VALID_TRIALS,
        "valid_helpers_accepted": valid_helpers,
        "random_trials": RANDOM_TRIALS,
        "random_non_syndromes_rejected": random_rejected,
        "perturb_trials": PERTURB_TRIALS,
        "perturbed_non_syndromes_rejected": perturbed_rejected,
        "perturbed_still_valid": perturbed_still_valid,
        "syndrome_bits": SYNDROME_BITS,
        "binary_image_rank": RANK,
        "image_codimension": CODIMENSION,
        "ambient_words": ambient,
        "image_words": image,
        "image_fraction_log2": -CODIMENSION,
    }


def main() -> None:
    result = run()
    print("BCH helper image-membership control [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[proved] Membership is exact for the finite binary syndrome map used by this repository.")
    print("[open conjecture] No security, leakage, deployment, or hardware claim is made.")


if __name__ == "__main__":
    main()
