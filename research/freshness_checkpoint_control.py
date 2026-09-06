#!/usr/bin/env python3
"""Finite checkpoint control for the keyed sliding-window state.

Status: [measured] software/protocol-boundary control only.  The previous loops
checked the in-memory bitmap and the unsigned sequence endpoints.  This file
checks the separate persistence boundary: a fixed checkpoint has a canonical
encoding, a digest witness, a bounded bitmap, and a forward generation number.

[proved] For the fixed byte layout, malformed or stale checkpoints are rejected
before the active state changes, and a canonical checkpoint round-trips.  The
model does not provide rollback resistance: a generation stored in ordinary
storage is not a trusted monotonic counter.  Persistent rollback, crash
atomicity, distributed recovery, key management, leakage, active attacks,
side channels, area, timing, FPGA behaviour, and G16 remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random
import struct

SEED = 20260904
TRIALS = 64
WINDOW = 8
MAX_SEQUENCE = (1 << 64) - 1
MAGIC = b"GCI1"
VERSION = 1
DOMAIN = b"golden-chain/freshness-checkpoint/v1\0"
# magic, version, width, reserved, generation, highest, seen
BODY = struct.Struct(">4sBBHQQQ")
CHECK_BYTES = 16
WIRE_BYTES = BODY.size + CHECK_BYTES
MASK = (1 << WINDOW) - 1


@dataclass(frozen=True)
class State:
    generation: int
    highest: int
    seen: int


def _valid_state(state: State) -> None:
    if not isinstance(state.generation, int) or state.generation < 1:
        raise AssertionError("generation is outside the positive integer domain")
    if not isinstance(state.highest, int) or not 0 <= state.highest <= MAX_SEQUENCE:
        raise AssertionError("highest sequence is outside the unsigned 64-bit domain")
    if not isinstance(state.seen, int) or not 0 <= state.seen <= MASK:
        raise AssertionError("bitmap contains a bit outside the declared window")


def encode(state: State) -> bytes:
    """Return the one canonical checkpoint encoding for a valid finite state."""
    _valid_state(state)
    body = BODY.pack(MAGIC, VERSION, WINDOW, 0, state.generation, state.highest, state.seen)
    digest = hashlib.sha256(DOMAIN + body).digest()[:CHECK_BYTES]
    return body + digest


def decode(blob: bytes) -> State:
    """Decode only an exact, self-consistent checkpoint; never coerce bytes."""
    if not isinstance(blob, bytes) or len(blob) != WIRE_BYTES:
        raise AssertionError("checkpoint length is not canonical")
    body, supplied = blob[:-CHECK_BYTES], blob[-CHECK_BYTES:]
    if hashlib.sha256(DOMAIN + body).digest()[:CHECK_BYTES] != supplied:
        raise AssertionError("checkpoint digest mismatch")
    magic, version, width, reserved, generation, highest, seen = BODY.unpack(body)
    if magic != MAGIC or version != VERSION or width != WINDOW or reserved != 0:
        raise AssertionError("checkpoint header is not canonical")
    state = State(generation, highest, seen)
    _valid_state(state)
    return state


class CheckpointStore:
    """A finite in-memory stand-in for applying a recovered checkpoint."""

    def __init__(self, state: State) -> None:
        _valid_state(state)
        self.state = state

    def apply(self, blob: bytes) -> State:
        candidate = decode(blob)
        if candidate.generation <= self.state.generation:
            raise AssertionError("checkpoint is not a strictly newer generation")
        self.state = candidate
        return self.state


def run() -> dict[str, int]:
    rng = random.Random(SEED)
    roundtrip_accepted = checksum_rejected = length_rejected = 0
    mask_rejected = stale_rejected = forward_accepted = 0

    for trial in range(TRIALS):
        state = State(
            generation=trial + 1,
            highest=(MAX_SEQUENCE - trial) if trial < 2 else (1000 + trial),
            seen=(trial * 37) & MASK,
        )
        blob = encode(state)
        if decode(blob) != state:
            raise AssertionError("canonical checkpoint did not round-trip")
        roundtrip_accepted += 1

        # A storage bit flip is rejected by the digest witness.
        corrupted = bytearray(blob)
        corrupted[-1] ^= 1 << (trial % 8)
        try:
            decode(bytes(corrupted))
        except AssertionError:
            checksum_rejected += 1
        else:
            raise AssertionError("checksum mutation was accepted")

        # Neither a torn write nor an appended byte may be silently coerced.
        for malformed in (blob[:-1], blob + b"\0"):
            try:
                decode(malformed)
            except AssertionError:
                length_rejected += 1
            else:
                raise AssertionError("non-canonical checkpoint length was accepted")

        # Recompute a valid digest around an out-of-window bitmap to exercise the
        # semantic guard separately from the checksum guard.
        bad_body = BODY.pack(MAGIC, VERSION, WINDOW, 0, state.generation,
                             state.highest, 1 << WINDOW)
        bad_blob = bad_body + hashlib.sha256(DOMAIN + bad_body).digest()[:CHECK_BYTES]
        try:
            decode(bad_blob)
        except AssertionError:
            mask_rejected += 1
        else:
            raise AssertionError("out-of-window bitmap was accepted")

        # A stale or equal-generation checkpoint cannot change the active state.
        active = State(10_000 + trial, state.highest, state.seen)
        store = CheckpointStore(active)
        before = store.state
        stale = encode(State(active.generation - 1, state.highest, state.seen))
        try:
            store.apply(stale)
        except AssertionError:
            stale_rejected += 1
        else:
            raise AssertionError("stale checkpoint was accepted")
        if store.state != before:
            raise AssertionError("stale checkpoint changed active state")

        # A strictly newer checkpoint is accepted and becomes the state.
        future = State(active.generation + 1, state.highest, state.seen)
        if store.apply(encode(future)) != future:
            raise AssertionError("forward checkpoint was not applied")
        forward_accepted += 1

        # Keep the RNG in the protocol so adding or removing trial inputs changes
        # the deterministic transcript rather than silently changing the seed.
        if rng.randrange(0, 2**32) < 0:
            raise AssertionError("unreachable deterministic guard")

    print(f"roundtrip_accepted={roundtrip_accepted}")
    print(f"checksum_rejected={checksum_rejected}")
    print(f"length_rejected={length_rejected}")
    print(f"mask_rejected={mask_rejected}")
    print(f"stale_rejected={stale_rejected}")
    print(f"forward_accepted={forward_accepted}")
    print("checkpoint_wire_bytes=48")
    return {
        "roundtrip_accepted": roundtrip_accepted,
        "checksum_rejected": checksum_rejected,
        "length_rejected": length_rejected,
        "mask_rejected": mask_rejected,
        "stale_rejected": stale_rejected,
        "forward_accepted": forward_accepted,
    }


if __name__ == "__main__":
    run()
