#!/usr/bin/env python3
"""Finite rollback-anchor control around the two-slot checkpoint journal.

W-INTL-272 can recover an older valid slot when a newer slot is torn or corrupt,
but it cannot tell that both slots have been restored to an older valid image.
This control adds a separate monotone anchor to the finite model. Recovery accepts
only a journal generation equal to the trusted anchor generation; anchor updates
are strictly increasing and canonical bytes are checked before state changes.

[measured] This is a software model with injected faults. It does not establish
that ordinary storage, a filesystem, a device, or a deployment supplies a
monotone anchor, crash atomicity, rollback resistance, or a security property.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct

from checkpoint_journal_recovery import SLOT_BYTES, Slot, State, _slot_bytes, recover as recover_journal

SEED = 20260906
TRIALS = 64
ANCHOR_MAGIC = b"GA01"
ANCHOR_VERSION = 1
ANCHOR_DOMAIN = b"golden-chain/rollback-anchor/v1\0"
ANCHOR = struct.Struct(">4sBBH Q 16s")
ANCHOR_BYTES = ANCHOR.size


@dataclass(frozen=True)
class AnchorState:
    generation: int


def encode_anchor(state: AnchorState) -> bytes:
    if not isinstance(state.generation, int) or isinstance(state.generation, bool):
        raise AssertionError("generation must be an integer")
    if not 0 <= state.generation < 1 << 64:
        raise AssertionError("generation outside unsigned 64-bit domain")
    body = ANCHOR.pack(ANCHOR_MAGIC, ANCHOR_VERSION, 0, 0, state.generation, b"\0" * 16)
    tag = hashlib.sha256(ANCHOR_DOMAIN + body[:-16]).digest()[:16]
    return body[:-16] + tag


def decode_anchor(blob: bytes) -> AnchorState:
    if not isinstance(blob, bytes) or len(blob) != ANCHOR_BYTES:
        raise AssertionError("anchor length")
    magic, version, reserved, pad, generation, supplied = ANCHOR.unpack(blob)
    if (magic, version, reserved, pad) != (ANCHOR_MAGIC, ANCHOR_VERSION, 0, 0):
        raise AssertionError("anchor header")
    expected = hashlib.sha256(ANCHOR_DOMAIN + blob[:-16]).digest()[:16]
    if supplied != expected:
        raise AssertionError("anchor digest")
    return AnchorState(generation)


def update_anchor(current: bytes, candidate: bytes) -> bytes:
    old = decode_anchor(current)
    new = decode_anchor(candidate)
    if new.generation <= old.generation:
        raise AssertionError("anchor is not strictly newer")
    return candidate


def recover_with_anchor(slots: tuple[bytes, bytes], anchor: bytes) -> State:
    trusted = decode_anchor(anchor)
    state = recover_journal(slots)
    if state.generation != trusted.generation:
        raise AssertionError("journal is not at the anchored generation")
    return state


def _mutate(blob: bytes, offset: int) -> bytes:
    out = bytearray(blob)
    out[offset % len(out)] ^= 1 << (offset % 8)
    return bytes(out)


def run() -> dict[str, int]:
    forward = rollback_rejected = tamper_rejected = stale_update_rejected = 0
    anchor_roundtrips = length_rejected = state_unchanged = 0
    for trial in range(TRIALS):
        old = State(100 + trial * 2, 1000 + trial, trial & 0xFF)
        new = State(old.generation + 1, old.highest + 1, ((trial + 3) * 17) & 0xFF)
        old_slots = (_slot_bytes(Slot(0, old)), _slot_bytes(Slot(1, old)))
        new_slots = (_slot_bytes(Slot(0, old)), _slot_bytes(Slot(1, new)))
        old_anchor = encode_anchor(AnchorState(old.generation))
        new_anchor = encode_anchor(AnchorState(new.generation))
        if decode_anchor(new_anchor) != AnchorState(new.generation):
            raise AssertionError("anchor did not round-trip")
        anchor_roundtrips += 1

        if recover_with_anchor(new_slots, new_anchor) != new:
            raise AssertionError("new journal was rejected by matching anchor")
        forward += 1

        # Both valid journal slots have rolled back, while the independent anchor
        # retains the newer generation. The stale image must not be accepted.
        try:
            recover_with_anchor(old_slots, new_anchor)
        except AssertionError:
            rollback_rejected += 1
        else:
            raise AssertionError("both-slot rollback was accepted")

        try:
            recover_with_anchor(new_slots, _mutate(new_anchor, 5))
        except AssertionError:
            tamper_rejected += 1
        else:
            raise AssertionError("tampered anchor was accepted")

        for candidate in (old_anchor, new_anchor):
            try:
                update_anchor(new_anchor, candidate)
            except AssertionError:
                stale_update_rejected += 1
            else:
                raise AssertionError("stale or equal anchor update was accepted")

        try:
            decode_anchor(new_anchor[:-1])
        except AssertionError:
            length_rejected += 1
        else:
            raise AssertionError("truncated anchor was accepted")

        before = new
        after = recover_with_anchor(new_slots, new_anchor)
        if after != before:
            raise AssertionError("successful recovery changed the candidate state")
        state_unchanged += 1

    print(f"forward_anchor_accept={forward}")
    print(f"both_slot_rollback_rejected={rollback_rejected}")
    print(f"tampered_anchor_rejected={tamper_rejected}")
    print(f"stale_anchor_update_rejected={stale_update_rejected}")
    print(f"anchor_roundtrip={anchor_roundtrips}")
    print(f"anchor_length_rejected={length_rejected}")
    print(f"state_unchanged_on_success={state_unchanged}")
    print(f"anchor_wire_bytes={ANCHOR_BYTES}")
    print(f"journal_slot_wire_bytes={SLOT_BYTES}")
    return {
        "forward_anchor_accept": forward,
        "both_slot_rollback_rejected": rollback_rejected,
        "tampered_anchor_rejected": tamper_rejected,
        "stale_anchor_update_rejected": stale_update_rejected,
        "anchor_roundtrip": anchor_roundtrips,
        "anchor_length_rejected": length_rejected,
        "state_unchanged_on_success": state_unchanged,
    }


if __name__ == "__main__":
    run()
