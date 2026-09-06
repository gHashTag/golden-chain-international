#!/usr/bin/env python3
"""Finite sliding-window freshness control for the keyed helper frame.

Status: [measured] software/protocol-boundary control only. W-INTL-268 used a
strictly increasing counter, which rejects legitimate out-of-order delivery and
lost packets. This file adds a bounded bitmap window while keeping the keyed
frame and parser contracts separate.

[proved] For the fixed finite state machine, a valid sequence is accepted once,
a valid unseen sequence inside the window is accepted out of order, a duplicate
or sequence outside the window is rejected, and sequence changes without a new
tag fail before state changes.
[open conjecture] This is not a deployed transport protocol or a security proof.
Rollback-resistant storage, distributed ordering, loss recovery policy, key
management, leakage, active attacks, side channels, area, timing, FPGA behavior,
and G16 remain open.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frame_freshness_control import (  # noqa: E402
    MAX_SEQUENCE,
    SEQUENCE_BYTES,
    TAG_BYTES,
    TEST_KEY,
    authenticate,
    verify,
)
from framed_helper_contract import frame  # noqa: E402
from key_generator_e2e import BLOCKS, enrol  # noqa: E402
from syndrome_basis_compression import pack_helper  # noqa: E402

SEED = 20260902
TRIALS = 64
WINDOW = 8


def _payload(rng) -> bytes:
    _, helper = enrol(rng, 0.35)
    return pack_helper(helper)


class SlidingWindowVerifier:
    """Explicit high-water mark plus a finite bitmap of seen sequences."""

    def __init__(self, width: int = WINDOW) -> None:
        if not isinstance(width, int) or width < 1 or width > 63:
            raise AssertionError("window width outside the fixed implementation range")
        self.width = width
        self.mask = (1 << width) - 1
        self.highest = -1
        self.seen = 0

    def accept(self, authenticated: bytes, key: bytes = TEST_KEY) -> bytes:
        sequence, payload = verify(authenticated, key)
        if self.highest < 0:
            self.highest = sequence
            self.seen = 1
            return payload

        if sequence > self.highest:
            shift = sequence - self.highest
            self.seen = 1 if shift >= self.width else ((self.seen << shift) | 1) & self.mask
            self.highest = sequence
            return payload

        distance = self.highest - sequence
        if distance >= self.width:
            raise AssertionError("sequence is outside the replay window")
        bit = 1 << distance
        if self.seen & bit:
            raise AssertionError("sequence already seen in the replay window")
        self.seen |= bit
        return payload


def run() -> dict[str, int]:
    rng = random.Random(SEED)
    stream_accepted = reordered_accepted = replay_rejected = 0
    stale_rejected = sequence_mutation_rejected = wrong_key_rejected = 0
    truncated_rejected = 0

    for trial in range(TRIALS):
        payload = _payload(rng)
        packet = frame(payload)

        # The ordinary stream remains accepted once, matching the strict-counter control.
        stream = SlidingWindowVerifier()
        if stream.accept(authenticate(packet, trial + 1)) != payload:
            raise AssertionError("fresh in-order frame was not accepted")
        stream_accepted += 1

        # A frame arriving behind the high-water mark is accepted once when it is
        # inside the finite window. The next copy is a distinct replay rejection.
        reordered = SlidingWindowVerifier()
        reordered.accept(authenticate(packet, 100))
        reordered.accept(authenticate(packet, 102))
        if reordered.accept(authenticate(packet, 101)) != payload:
            raise AssertionError("unseen in-window out-of-order frame was rejected")
        reordered_accepted += 1
        try:
            reordered.accept(authenticate(packet, 101))
        except AssertionError:
            replay_rejected += 1
        else:
            raise AssertionError("duplicate in-window frame was accepted")

        # A valid frame eight positions behind the high-water mark is outside a
        # width-eight window and must be rejected as stale.
        stale = SlidingWindowVerifier()
        stale.accept(authenticate(packet, 200))
        try:
            stale.accept(authenticate(packet, 192))
        except AssertionError:
            stale_rejected += 1
        else:
            raise AssertionError("out-of-window frame was accepted")

        # Changing the sequence bytes without recomputing the tag must not alter state.
        mutated = bytearray(authenticate(packet, 300))
        mutated[SEQUENCE_BYTES - 1] ^= 1
        protected = SlidingWindowVerifier()
        try:
            protected.accept(bytes(mutated))
        except AssertionError:
            sequence_mutation_rejected += 1
        else:
            raise AssertionError("sequence mutation bypassed the keyed tag")
        if protected.highest != -1 or protected.seen != 0:
            raise AssertionError("failed authentication changed window state")

        try:
            SlidingWindowVerifier().accept(authenticate(packet, 400, key=b"wrong-fixture-key"), TEST_KEY)
        except AssertionError:
            wrong_key_rejected += 1
        else:
            raise AssertionError("wrong key was accepted")

        try:
            SlidingWindowVerifier().accept(authenticate(packet, MAX_SEQUENCE)[:-1])
        except AssertionError:
            truncated_rejected += 1
        else:
            raise AssertionError("truncated frame was accepted")

    return {
        "seed": SEED,
        "blocks": BLOCKS,
        "trials": TRIALS,
        "window": WINDOW,
        "sequence_bytes": SEQUENCE_BYTES,
        "tag_bytes": TAG_BYTES,
        "stream_accepted": stream_accepted,
        "reordered_accepted": reordered_accepted,
        "replay_rejected": replay_rejected,
        "stale_rejected": stale_rejected,
        "sequence_mutation_rejected": sequence_mutation_rejected,
        "wrong_key_rejected": wrong_key_rejected,
        "truncated_rejected": truncated_rejected,
    }


def main() -> None:
    result = run()
    print("Sliding-window freshness control [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[proved] The finite bitmap window accepts unseen in-window reordering once and rejects duplicates and stale sequences.")
    print("[open conjecture] This is not a deployed transport protocol or a security proof.")


if __name__ == "__main__":
    main()
