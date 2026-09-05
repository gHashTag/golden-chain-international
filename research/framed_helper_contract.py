#!/usr/bin/env python3
"""Finite control for a versioned, length-delimited helper frame.

Status: [measured] software/protocol-boundary control only.  This is deliberately
separate from W-INTL-262's key binding and W-INTL-265's packed-coordinate boundary:
it checks that a candidate frame is canonical before any authentication step.

[proved] A frame with a fixed magic, version, format identifier, payload length,
and domain-separated digest has one canonical parse. Truncation, extension,
wrong version, wrong format, and payload changes are rejected by this finite
parser/digest control.
[open conjecture] This is not a security proof, a collision-resistance claim, a
deployed protocol, a leakage bound, or an active-attacker result. The digest is
a deterministic integrity witness for the software control, not an authenticated
keyed tag.
"""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from syndrome_basis_compression import pack_helper  # noqa: E402
from key_generator_e2e import BLOCKS, enrol  # noqa: E402

SEED = 20260823
VERSION = 1
FORMAT_ID = b"BCH127-R70"
MAGIC = b"GCH1"
TAG_BYTES = 16
TRIALS = 64


def _payload(rng) -> bytes:
    _, helper = enrol(rng, 0.35)
    return pack_helper(helper)


def frame(payload: bytes, *, version: int = VERSION, format_id: bytes = FORMAT_ID) -> bytes:
    if not payload or len(payload) > 0xFFFF:
        raise AssertionError("payload length outside the fixed frame")
    if len(format_id) > 0xFF:
        raise AssertionError("format identifier too long")
    header = MAGIC + bytes([version, len(format_id)]) + format_id + struct.pack(">H", len(payload))
    digest = hashlib.sha256(b"gci/helper-frame/v1/" + header + payload).digest()[:TAG_BYTES]
    return header + payload + digest


def parse(packet: bytes, *, version: int = VERSION, format_id: bytes = FORMAT_ID) -> bytes:
    minimum = len(MAGIC) + 2 + len(format_id) + 2 + TAG_BYTES
    if len(packet) < minimum:
        raise AssertionError("frame is truncated")
    if packet[:4] != MAGIC:
        raise AssertionError("frame magic mismatch")
    got_version = packet[4]
    if got_version != version:
        raise AssertionError("frame version mismatch")
    id_len = packet[5]
    cursor = 6
    if id_len != len(format_id) or packet[cursor:cursor + id_len] != format_id:
        raise AssertionError("frame format identifier mismatch")
    cursor += id_len
    payload_len = struct.unpack(">H", packet[cursor:cursor + 2])[0]
    cursor += 2
    end = cursor + payload_len
    if end + TAG_BYTES != len(packet):
        raise AssertionError("frame length is not canonical")
    payload = packet[cursor:end]
    tag = packet[end:]
    expected = hashlib.sha256(b"gci/helper-frame/v1/" + packet[:cursor] + payload).digest()[:TAG_BYTES]
    if tag != expected:
        raise AssertionError("frame integrity witness mismatch")
    return payload


def run() -> dict[str, int]:
    import random
    rng = random.Random(SEED)
    accepted = truncated = extended = wrong_version = wrong_format = payload_mutated = 0
    for _ in range(TRIALS):
        payload = _payload(rng)
        packet = frame(payload)
        if parse(packet) != payload:
            raise AssertionError("canonical frame failed round-trip")
        accepted += 1
        for candidate, bucket in ((packet[:-1], "truncated"),
                                  (packet + b"x", "extended"),
                                  (frame(payload, version=2), "wrong_version"),
                                  (frame(payload, format_id=b"BCH127-R70X"), "wrong_format")):
            try:
                parse(candidate)
            except AssertionError:
                if bucket == "truncated": truncated += 1
                elif bucket == "extended": extended += 1
                elif bucket == "wrong_version": wrong_version += 1
                else: wrong_format += 1
            else:
                raise AssertionError(f"{bucket} mutation was accepted")
        mutated = bytearray(packet)
        payload_offset = len(MAGIC) + 2 + len(FORMAT_ID) + 2
        mutated[payload_offset] ^= 1
        try:
            parse(bytes(mutated))
        except AssertionError:
            payload_mutated += 1
        else:
            raise AssertionError("payload mutation bypassed the integrity witness")
    return {"seed": SEED, "blocks": BLOCKS, "trials": TRIALS,
            "canonical_accepted": accepted, "truncated_rejected": truncated,
            "extended_rejected": extended, "wrong_version_rejected": wrong_version,
            "wrong_format_rejected": wrong_format,
            "payload_mutation_rejected": payload_mutated,
            "tag_bytes": TAG_BYTES}


def main() -> None:
    result = run()
    print("Versioned helper frame contract [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[proved] The parser enforces a canonical length-delimited frame before any authentication step.")
    print("[open conjecture] The digest is not a keyed authenticator or a security proof.")


if __name__ == "__main__":
    main()
