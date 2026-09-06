#!/usr/bin/env python3
"""Finite two-slot journal recovery control.

This is a bounded software experiment around W-INTL-271's canonical checkpoint.
It models a journal with two complete records: recovery validates both the outer
slot record and the inner checkpoint, then chooses the greatest valid generation.
A torn or corrupted newer slot falls back to the older valid slot; two invalid
slots fail closed; two different valid records at one generation are ambiguous.

[measured] This control does not prove crash atomicity, storage durability,
rollback resistance, authenticated persistence, distributed recovery, or a
security property. It only measures the finite recovery decision for the fixed
record layout and injected faults below.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct

from freshness_checkpoint_control import State, encode as encode_checkpoint, decode as decode_checkpoint

SEED = 20260905
TRIALS = 64
SLOT_MAGIC = b"GJ01"
SLOT_VERSION = 1
SLOT_DOMAIN = b"golden-chain/checkpoint-journal/v1\0"
# magic, version, slot, reserved, generation, highest, seen, inner checkpoint
BODY = struct.Struct(">4sBBHQQQ48s")
CHECK_BYTES = 16
SLOT_BYTES = BODY.size + CHECK_BYTES


@dataclass(frozen=True)
class Slot:
    index: int
    state: State


def _slot_bytes(slot: Slot) -> bytes:
    inner = encode_checkpoint(slot.state)
    body = BODY.pack(SLOT_MAGIC, SLOT_VERSION, slot.index, 0,
                     slot.state.generation, slot.state.highest, slot.state.seen, inner)
    return body + hashlib.sha256(SLOT_DOMAIN + body).digest()[:CHECK_BYTES]


def _read_slot(blob: bytes, expected_index: int) -> State | None:
    if not isinstance(blob, bytes) or len(blob) != SLOT_BYTES:
        return None
    body, supplied = blob[:-CHECK_BYTES], blob[-CHECK_BYTES:]
    if hashlib.sha256(SLOT_DOMAIN + body).digest()[:CHECK_BYTES] != supplied:
        return None
    magic, version, slot, reserved, generation, highest, seen, inner = BODY.unpack(body)
    if (magic, version, slot, reserved) != (SLOT_MAGIC, SLOT_VERSION, expected_index, 0):
        return None
    state = State(generation, highest, seen)
    try:
        if decode_checkpoint(inner) != state:
            return None
    except AssertionError:
        return None
    return state


def recover(slots: tuple[bytes, bytes]) -> State:
    valid = []
    for index, blob in enumerate(slots):
        state = _read_slot(blob, index)
        if state is not None:
            valid.append(state)
    if not valid:
        raise AssertionError("journal has no valid slot")
    newest = max(state.generation for state in valid)
    candidates = [state for state in valid if state.generation == newest]
    if any(state != candidates[0] for state in candidates[1:]):
        raise AssertionError("journal has conflicting records at one generation")
    return candidates[0]


def _mutate(blob: bytes, offset: int) -> bytes:
    out = bytearray(blob)
    out[offset % len(out)] ^= 1 << (offset % 8)
    return bytes(out)


def run() -> dict[str, int]:
    recovered_newest = torn_fallback = corruption_fallback = 0
    both_invalid_rejected = conflict_rejected = length_rejected = 0
    no_mutation_failures = 0
    for trial in range(TRIALS):
        old = State(100 + trial * 2, 1000 + trial, trial & 0xFF)
        new = State(old.generation + 1, old.highest + 1, ((trial + 3) * 17) & 0xFF)
        old_blob, new_blob = _slot_bytes(Slot(0, old)), _slot_bytes(Slot(1, new))
        if recover((old_blob, new_blob)) != new:
            raise AssertionError("valid journal did not select the newest state")
        recovered_newest += 1

        # A torn write leaves the previous complete slot usable.
        before = old
        torn = new_blob[: 1 + (trial % (SLOT_BYTES - 1))]
        try:
            got = recover((old_blob, torn + b"\0" * (SLOT_BYTES - len(torn))))
        except AssertionError:
            raise AssertionError("one valid slot was lost during torn-write recovery")
        if got != before:
            raise AssertionError("torn newer slot did not fall back to old state")
        torn_fallback += 1

        # A same-sized corruption in the newer slot also falls back, without state
        # mutation because recovery returns a new value rather than editing a store.
        if recover((old_blob, _mutate(new_blob, 7))) != old:
            raise AssertionError("corrupt newer slot did not fall back")
        corruption_fallback += 1

        # The parser fails closed when both physical slots are unusable.
        try:
            recover((_mutate(old_blob, 3), _mutate(new_blob, 11)))
        except AssertionError:
            both_invalid_rejected += 1
        else:
            raise AssertionError("two invalid slots were accepted")

        # Two valid but different records at one generation are ambiguous and must
        # not be resolved by an arbitrary slot order.
        left = State(old.generation + 1, old.highest + 1, 1)
        right = State(old.generation + 1, old.highest + 2, 2)
        try:
            recover((_slot_bytes(Slot(0, left)), _slot_bytes(Slot(1, right))))
        except AssertionError:
            conflict_rejected += 1
        else:
            raise AssertionError("same-generation conflict was accepted")

        # Neither truncation nor extension is coerced into a slot record.
        try:
            recover((old_blob[:-1], new_blob + b"\0"))
        except AssertionError:
            length_rejected += 1
        else:
            raise AssertionError("malformed journal was accepted")

        if recover((old_blob, new_blob)) != new:
            no_mutation_failures += 1
    print(f"newest_selected={recovered_newest}")
    print(f"torn_fallback={torn_fallback}")
    print(f"corruption_fallback={corruption_fallback}")
    print(f"both_invalid_rejected={both_invalid_rejected}")
    print(f"conflict_rejected={conflict_rejected}")
    print(f"length_rejected={length_rejected}")
    print(f"state_unchanged_on_recovery={TRIALS - no_mutation_failures}")
    print(f"slot_wire_bytes={SLOT_BYTES}")
    return {
        "newest_selected": recovered_newest,
        "torn_fallback": torn_fallback,
        "corruption_fallback": corruption_fallback,
        "both_invalid_rejected": both_invalid_rejected,
        "conflict_rejected": conflict_rejected,
        "length_rejected": length_rejected,
        "state_unchanged_on_recovery": TRIALS - no_mutation_failures,
    }


if __name__ == "__main__":
    run()
