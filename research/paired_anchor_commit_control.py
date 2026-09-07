#!/usr/bin/env python3
"""Finite paired-journal/anchor commit control.

W-INTL-273 checks that a journal and an independent generation anchor agree when
recovery runs, but it does not exercise the update boundary itself.  This control
adds a small commit record binding the canonical journal bytes and anchor bytes
to one generation.  Recovery accepts the old complete bundle or the new complete
bundle, and rejects every one- or two-component crash prefix of the three-component
update.

[measured] This is a software model with injected update-order faults.  It does not
establish a storage transaction, crash atomicity, rollback resistance, durability,
availability, or a security property.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import struct

from checkpoint_journal_recovery import Slot, State, _slot_bytes
from rollback_anchor_control import (
    ANCHOR_BYTES,
    AnchorState,
    decode_anchor,
    encode_anchor,
    recover_with_anchor,
)

SEED = 20260907
TRIALS = 64
COMMIT_MAGIC = b"GC01"
COMMIT_VERSION = 1
COMMIT_DOMAIN = b"golden-chain/paired-anchor-commit/v1\0"
COMMIT_BODY = struct.Struct(">4sBBHQ32s32s")
COMMIT_TAG_BYTES = 16
COMMIT_BYTES = COMMIT_BODY.size + COMMIT_TAG_BYTES


@dataclass(frozen=True)
class Bundle:
    journal: tuple[bytes, bytes]
    anchor: bytes
    commit: bytes


def encode_commit(journal: tuple[bytes, bytes], anchor: bytes,
                  generation: int) -> bytes:
    if len(journal) != 2 or any(not isinstance(slot, bytes) for slot in journal):
        raise AssertionError("journal must contain two byte slots")
    if len(anchor) != ANCHOR_BYTES:
        raise AssertionError("anchor length")
    if not 0 <= generation < 1 << 64:
        raise AssertionError("generation outside unsigned 64-bit domain")
    journal_digest = hashlib.sha256(b"".join(journal)).digest()
    anchor_digest = hashlib.sha256(anchor).digest()
    body = COMMIT_BODY.pack(
        COMMIT_MAGIC, COMMIT_VERSION, 0, 0, generation,
        journal_digest, anchor_digest,
    )
    tag = hashlib.sha256(COMMIT_DOMAIN + body).digest()[:COMMIT_TAG_BYTES]
    return body + tag


def decode_commit(blob: bytes) -> tuple[int, bytes, bytes]:
    if not isinstance(blob, bytes) or len(blob) != COMMIT_BYTES:
        raise AssertionError("commit length")
    body, supplied = blob[:-COMMIT_TAG_BYTES], blob[-COMMIT_TAG_BYTES:]
    if hashlib.sha256(COMMIT_DOMAIN + body).digest()[:COMMIT_TAG_BYTES] != supplied:
        raise AssertionError("commit digest")
    magic, version, reserved, pad, generation, journal_digest, anchor_digest = (
        COMMIT_BODY.unpack(body)
    )
    if (magic, version, reserved, pad) != (COMMIT_MAGIC, COMMIT_VERSION, 0, 0):
        raise AssertionError("commit header")
    return generation, journal_digest, anchor_digest


def make_bundle(journal: tuple[bytes, bytes], state: State) -> Bundle:
    anchor = encode_anchor(AnchorState(state.generation))
    commit = encode_commit(journal, anchor, state.generation)
    return Bundle(journal, anchor, commit)


def recover_bundle(bundle: Bundle) -> State:
    generation, journal_digest, anchor_digest = decode_commit(bundle.commit)
    if hashlib.sha256(b"".join(bundle.journal)).digest() != journal_digest:
        raise AssertionError("commit does not bind journal")
    if hashlib.sha256(bundle.anchor).digest() != anchor_digest:
        raise AssertionError("commit does not bind anchor")
    anchor_state = decode_anchor(bundle.anchor)
    state = recover_with_anchor(bundle.journal, bundle.anchor)
    if state.generation != generation or anchor_state.generation != generation:
        raise AssertionError("bundle generation mismatch")
    return state


def _mutate(blob: bytes, offset: int) -> bytes:
    out = bytearray(blob)
    out[offset % len(out)] ^= 1 << (offset % 8)
    return bytes(out)


def _prefix(old: Bundle, new: Bundle, order: tuple[str, ...],
            count: int) -> Bundle:
    values = {
        "journal": old.journal,
        "anchor": old.anchor,
        "commit": old.commit,
    }
    for name in order[:count]:
        values[name] = getattr(new, name)
    return Bundle(values["journal"], values["anchor"], values["commit"])


def run() -> dict[str, int]:
    old_accept = complete_order_accept = mixed_prefix_rejected = 0
    commit_roundtrips = tampered_commit_rejected = length_rejected = 0
    state_unchanged = 0
    orders = tuple(itertools.permutations(("journal", "anchor", "commit")))

    for trial in range(TRIALS):
        old = State(100 + trial * 2, 1000 + trial, trial & 0xFF)
        new = State(old.generation + 1, old.highest + 1, ((trial + 3) * 17) & 0xFF)
        old_journal = (_slot_bytes(Slot(0, old)), _slot_bytes(Slot(1, old)))
        new_journal = (_slot_bytes(Slot(0, old)), _slot_bytes(Slot(1, new)))
        old_bundle = make_bundle(old_journal, old)
        new_bundle = make_bundle(new_journal, new)

        if decode_commit(new_bundle.commit)[0] != new.generation:
            raise AssertionError("commit did not round-trip")
        commit_roundtrips += 1

        if recover_bundle(old_bundle) != old:
            raise AssertionError("old complete bundle was rejected")
        old_accept += 1
        state_unchanged += 1

        # Every partial order is a mixed-generation state.  The commit record
        # binds both payloads, so none of the 6 * 2 prefixes may be accepted.
        for order in orders:
            for count in (1, 2):
                try:
                    recover_bundle(_prefix(old_bundle, new_bundle, order, count))
                except AssertionError:
                    mixed_prefix_rejected += 1
                else:
                    raise AssertionError(
                        f"mixed prefix accepted for order={order}, count={count}"
                    )

        # Once all three records exist, order no longer matters.
        for order in orders:
            if recover_bundle(_prefix(old_bundle, new_bundle, order, 3)) != new:
                raise AssertionError("complete bundle was rejected")
            complete_order_accept += 1
            state_unchanged += 1

        try:
            recover_bundle(Bundle(new_bundle.journal, new_bundle.anchor,
                                  _mutate(new_bundle.commit, 7)))
        except AssertionError:
            tampered_commit_rejected += 1
        else:
            raise AssertionError("tampered commit was accepted")

        for malformed in (
            Bundle(new_bundle.journal, new_bundle.anchor, new_bundle.commit[:-1]),
            Bundle(new_bundle.journal, new_bundle.anchor,
                   new_bundle.commit + b"\0"),
        ):
            try:
                recover_bundle(malformed)
            except AssertionError:
                length_rejected += 1
            else:
                raise AssertionError("malformed commit length was accepted")

    print(f"old_bundle_accept={old_accept}")
    print(f"complete_order_accept={complete_order_accept}")
    print(f"mixed_prefix_rejected={mixed_prefix_rejected}")
    print(f"commit_roundtrip={commit_roundtrips}")
    print(f"tampered_commit_rejected={tampered_commit_rejected}")
    print(f"length_rejected={length_rejected}")
    print(f"state_unchanged_on_success={state_unchanged}")
    print(f"commit_wire_bytes={COMMIT_BYTES}")
    return {
        "old_bundle_accept": old_accept,
        "complete_order_accept": complete_order_accept,
        "mixed_prefix_rejected": mixed_prefix_rejected,
        "commit_roundtrip": commit_roundtrips,
        "tampered_commit_rejected": tampered_commit_rejected,
        "length_rejected": length_rejected,
        "state_unchanged_on_success": state_unchanged,
    }


if __name__ == "__main__":
    run()
