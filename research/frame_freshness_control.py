#!/usr/bin/env python3
"""Finite freshness control around the keyed candidate helper frame.

Status: [measured] software/protocol-boundary control only.  W-INTL-267 checked
keyed acceptance and mutation rejection, but deliberately left replay/freshness
open.  This file adds a strict monotone sequence rule without calling it a
deployed protocol or a security result.

[proved] For the fixed byte layout, test key, and finite verifier state, a valid
sequence is accepted once, an exact replay and a lower sequence are rejected,
and a sequence mutation without a recomputed tag is rejected before the inner
parser is reached.
[open conjecture] The public key is test data, the tag is truncated, and no claim
is made about key management, rollback-resistant storage, distributed ordering,
loss recovery, active attackers, leakage, timing, area, FPGA behavior, or G16.
"""

from __future__ import annotations

import hashlib
import hmac
import random
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from framed_helper_contract import frame, parse  # noqa: E402
from key_generator_e2e import BLOCKS, enrol  # noqa: E402
from syndrome_basis_compression import pack_helper  # noqa: E402

SEED = 20260901
TRIALS = 64
TAG_BYTES = 16
SEQUENCE_BYTES = 8
DOMAIN = b"gci/helper-frame/freshness/v1"
TEST_KEY = b"gci-public-fixture-key-v1"
WRONG_KEY = b"gci-public-fixture-key-v2"
MAX_SEQUENCE = (1 << (8 * SEQUENCE_BYTES)) - 1


def _payload(rng) -> bytes:
    _, helper = enrol(rng, 0.35)
    return pack_helper(helper)


def authenticate(packet: bytes, sequence: int, key: bytes = TEST_KEY) -> bytes:
    """Return sequence || packet || tag for the finite test protocol."""
    if not packet:
        raise AssertionError("empty inner frame")
    if not isinstance(sequence, int) or not 0 <= sequence <= MAX_SEQUENCE:
        raise AssertionError("sequence outside the fixed unsigned range")
    body = struct.pack(">Q", sequence) + packet
    tag = hmac.new(key, DOMAIN + body, hashlib.sha256).digest()[:TAG_BYTES]
    return body + tag


def verify(authenticated: bytes, key: bytes = TEST_KEY) -> tuple[int, bytes]:
    """Verify the tag and canonical inner frame, returning sequence and payload."""
    minimum = SEQUENCE_BYTES + TAG_BYTES + 1
    if len(authenticated) < minimum:
        raise AssertionError("freshness frame is truncated")
    body, got = authenticated[:-TAG_BYTES], authenticated[-TAG_BYTES:]
    expected = hmac.new(key, DOMAIN + body, hashlib.sha256).digest()[:TAG_BYTES]
    if not hmac.compare_digest(got, expected):
        raise AssertionError("freshness frame tag mismatch")
    sequence = struct.unpack(">Q", body[:SEQUENCE_BYTES])[0]
    payload = parse(body[SEQUENCE_BYTES:])
    return sequence, payload


class FreshnessVerifier:
    """A strict monotone verifier whose state is explicit and finite."""

    def __init__(self) -> None:
        self.last_sequence = -1

    def accept(self, authenticated: bytes, key: bytes = TEST_KEY) -> bytes:
        sequence, payload = verify(authenticated, key)
        if sequence <= self.last_sequence:
            raise AssertionError("stale or replayed sequence")
        self.last_sequence = sequence
        return payload


def run() -> dict[str, int]:
    rng = random.Random(SEED)
    stream_accepted = replay_rejected = stale_rejected = 0
    sequence_mutation_rejected = wrong_key_rejected = truncated_rejected = 0

    for index in range(TRIALS):
        payload = _payload(rng)
        packet = frame(payload)
        verifier = FreshnessVerifier()
        authenticated = authenticate(packet, index + 1)
        if verifier.accept(authenticated) != payload:
            raise AssertionError("fresh authenticated frame failed canonical acceptance")
        stream_accepted += 1

        try:
            verifier.accept(authenticated)
        except AssertionError:
            replay_rejected += 1
        else:
            raise AssertionError("exact replay was accepted")

        # A distinct valid tag for a lower sequence is an out-of-order/stale case,
        # not merely a byte mutation.  It must be rejected by verifier state.
        stale = authenticate(packet, index)
        try:
            verifier.accept(stale)
        except AssertionError:
            stale_rejected += 1
        else:
            raise AssertionError("lower sequence was accepted")

        # Changing the sequence without recomputing the tag must fail authentication.
        mutated = bytearray(authenticated)
        mutated[SEQUENCE_BYTES - 1] ^= 1
        try:
            verifier.accept(bytes(mutated))
        except AssertionError:
            sequence_mutation_rejected += 1
        else:
            raise AssertionError("sequence mutation bypassed the tag")

        try:
            verifier.accept(authenticate(packet, index + 1, WRONG_KEY), WRONG_KEY)
        except AssertionError:
            wrong_key_rejected += 1
        else:
            raise AssertionError("wrong key was accepted")

        try:
            verifier.accept(authenticated[:-1])
        except AssertionError:
            truncated_rejected += 1
        else:
            raise AssertionError("truncated frame was accepted")

    return {
        "seed": SEED,
        "blocks": BLOCKS,
        "trials": TRIALS,
        "tag_bytes": TAG_BYTES,
        "sequence_bytes": SEQUENCE_BYTES,
        "stream_accepted": stream_accepted,
        "replay_rejected": replay_rejected,
        "stale_rejected": stale_rejected,
        "sequence_mutation_rejected": sequence_mutation_rejected,
        "wrong_key_rejected": wrong_key_rejected,
        "truncated_rejected": truncated_rejected,
    }


def main() -> None:
    result = run()
    print("Freshness and replay control [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[proved] The finite verifier accepts increasing sequences once and rejects replayed or stale sequences.")
    print("[open conjecture] This is not a deployed freshness protocol or a security proof.")


if __name__ == "__main__":
    main()
