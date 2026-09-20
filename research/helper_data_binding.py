#!/usr/bin/env python3
"""Measure helper-data binding on the repository's finite BCH key chain.

Status: [measured] deterministic software control for BCH(127,57,11), not an
implementation or a security proof.  The construction uses syndrome helper data
and derives K = S xor H(W), where S is a digest of the recovered response and W
is the exact helper-data byte string.  The control compares that bound key with
an intentionally unbound digest under helper-data mutation.

[open conjecture] This does not model a physical active attacker, helper-data
encoding outside the syndrome representation, leakage, side channels, hardware,
or a proof against all decoder manipulation strategies.

The construction is a finite-code control.  The unequal-reliability channel and
finite BCH experiments remain prior-art/reproduction lines; this file measures
the missing key-equation binding path rather than a new channel theorem.
"""

from __future__ import annotations

import hashlib
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from key_generator_e2e import (  # noqa: E402
    N,
    T,
    BLOCKS,
    decode_block,
    enrol,
    key_of,
    regenerate,
    syndromes,
)

TRIALS = 64
TAMPERS_PER_TRIAL = 32
BER = 0.02
BIAS = 0.35
KEY_BYTES = 16


def _helper_bytes(helper: list[list[int]]) -> bytes:
    """Canonical big-endian packing of GF(2^7) syndrome symbols."""
    symbols = [symbol for block in helper for symbol in block]
    if len(symbols) != BLOCKS * 2 * T:
        raise AssertionError("unexpected syndrome-helper length")
    bits = "".join(f"{symbol:07b}" for symbol in symbols)
    return int(bits, 2).to_bytes((len(bits) + 7) // 8, "big")


def _xor(a: bytes, b: bytes) -> bytes:
    if len(a) != len(b):
        raise AssertionError("key operands must have equal length")
    return bytes(x ^ y for x, y in zip(a, b))


def bound_key(response: list[list[int]], helper: list[list[int]]) -> bytes:
    """K = S xor H(W), with S a response digest and W canonical helper bytes."""
    secret = key_of(response)
    helper_digest = hashlib.sha256(_helper_bytes(helper)).digest()[:KEY_BYTES]
    return _xor(secret, helper_digest)


def unbound_key(response: list[list[int]]) -> bytes:
    """Control key that ignores helper data entirely."""
    return key_of(response)


def _flip_helper(helper: list[list[int]], bit_index: int) -> list[list[int]]:
    clone = [row[:] for row in helper]
    symbol_index, offset = divmod(bit_index, 7)
    block, position = divmod(symbol_index, 2 * T)
    # The packed representation is big-endian within each 7-bit symbol.  Flip a
    # symbol bit directly; every value remains a valid GF(2^7) element.
    clone[block][position] ^= 1 << (6 - offset)
    return clone


def _decode(noisy: list[list[int]], helper: list[list[int]]) -> list[list[int]] | None:
    recovered: list[list[int]] = []
    for block, enrolled in zip(noisy, helper):
        out = decode_block(block, enrolled)
        if out is None:
            return None
        recovered.append(out)
    return recovered


def run() -> dict[str, int | float]:
    rng = random.Random(20260819)
    clean_bound_matches = 0
    clean_unbound_matches = 0
    tampered_bound_matches = 0
    tampered_unbound_matches = 0
    direct_bound_matches = 0
    direct_unbound_matches = 0
    tampered_decode_success = 0
    tampered_trials = 0
    for _ in range(TRIALS):
        enrolled, helper = enrol(rng, BIAS)
        noisy = regenerate(rng, enrolled, BER)
        recovered = _decode(noisy, helper)
        if recovered is None:
            raise AssertionError("clean finite-chain control failed to decode")
        expected_bound = bound_key(enrolled, helper)
        expected_unbound = unbound_key(enrolled)
        if bound_key(recovered, helper) == expected_bound:
            clean_bound_matches += 1
        if unbound_key(recovered) == expected_unbound:
            clean_unbound_matches += 1

        # Flip a deterministic spread of every helper symbol's bit positions.
        helper_bits = BLOCKS * 2 * T * 7
        for sample in range(TAMPERS_PER_TRIAL):
            bit = (sample * 97 + 11 * _) % helper_bits
            altered = _flip_helper(helper, bit)
            tampered_trials += 1
            # Hold the recovered response fixed to isolate the key equation from
            # decoder behaviour.  An unbound key is invariant by construction;
            # the bound equation must change when W changes.
            if bound_key(recovered, altered) == expected_bound:
                direct_bound_matches += 1
            if unbound_key(recovered) == expected_unbound:
                direct_unbound_matches += 1
            altered_recovered = _decode(noisy, altered)
            if altered_recovered is not None:
                tampered_decode_success += 1
                if bound_key(altered_recovered, altered) == expected_bound:
                    tampered_bound_matches += 1
                if unbound_key(altered_recovered) == expected_unbound:
                    tampered_unbound_matches += 1

    if clean_bound_matches != TRIALS or clean_unbound_matches != TRIALS:
        raise AssertionError("clean key binding control did not round-trip")
    if tampered_bound_matches != 0:
        raise AssertionError("a tampered helper produced the enrolled bound key")
    if direct_bound_matches != 0 or direct_unbound_matches != tampered_trials:
        raise AssertionError("direct key-equation binding control failed")
    return {
        "trials": TRIALS,
        "tampered_trials": tampered_trials,
        "tampered_decode_success": tampered_decode_success,
        "clean_bound_matches": clean_bound_matches,
        "clean_unbound_matches": clean_unbound_matches,
        "tampered_bound_matches": tampered_bound_matches,
        "tampered_unbound_matches": tampered_unbound_matches,
        "direct_bound_matches": direct_bound_matches,
        "direct_unbound_matches": direct_unbound_matches,
        "ber": BER,
        "bias": BIAS,
        "helper_bits": BLOCKS * 2 * T * 7,
    }


def main() -> None:
    result = run()
    print("Helper-data binding control [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[measured] Clean K = S xor H(W) round-trips; no sampled one-bit helper mutation reproduced the enrolled bound key.")
    print("[open conjecture] This finite control does not establish security, hardware cost, leakage, or a deployed helper-data encoding.")


if __name__ == "__main__":
    main()
