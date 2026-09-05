#!/usr/bin/env python3
"""Finite control for a canonical packed BCH helper candidate.

Status: [measured] software/representation control only.  The existing rank-sized
coordinate representation packs six BCH(127,57,11) helper blocks into 420 semantic
bits and 53 bytes, leaving four leading padding bits.  This module makes that boundary
explicit and measures what it does and does not reject.

[proved] A canonical 53-byte packet has exactly 420 payload bits and four zero padding
bits.  Every 420-bit payload is a valid coordinate word by construction; therefore a
payload mutation can remain a valid packed representation even when it changes the
expanded syndrome helper.
[open conjecture] This is not a deployed wire format, an integrity/authentication
mechanism, a leakage estimate, a security theorem, an active-attacker result, or a
hardware result.  A real protocol would need an authenticated framing and a defined
failure policy.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from key_generator_e2e import BLOCKS, enrol  # noqa: E402
from syndrome_basis_compression import (  # noqa: E402
    RANK,
    pack_helper,
    unpack_helper,
)

SEED = 20260822
TRIALS = 64
RANDOM_PACKETS = 256
PAYLOAD_BITS = BLOCKS * RANK
PACKET_BYTES = (PAYLOAD_BITS + 7) // 8
PADDING_BITS = 8 * PACKET_BYTES - PAYLOAD_BITS


def _mutate_padding(packet: bytes, bit: int) -> bytes:
    """Flip one of the four leading storage bits of the big-endian packet."""
    if not 0 <= bit < PADDING_BITS:
        raise AssertionError("padding bit outside the fixed packet")
    value = int.from_bytes(packet, "big")
    value ^= 1 << (PAYLOAD_BITS + bit)
    return value.to_bytes(PACKET_BYTES, "big")


def _mutate_payload(packet: bytes, bit: int) -> bytes:
    if not 0 <= bit < PAYLOAD_BITS:
        raise AssertionError("payload bit outside the fixed packet")
    value = int.from_bytes(packet, "big")
    value ^= 1 << bit
    return value.to_bytes(PACKET_BYTES, "big")


def _accepted(packet: bytes) -> bool:
    try:
        unpack_helper(packet)
    except AssertionError:
        return False
    return True


def run() -> dict[str, int | float]:
    rng = random.Random(SEED)
    valid_packets = 0
    canonical_round_trips = 0
    padding_rejected = 0
    payload_accepted = 0
    payload_changed = 0
    random_accepted = 0

    packets: list[bytes] = []
    helpers: list[list[list[int]]] = []
    for _ in range(TRIALS):
        _, helper = enrol(rng, 0.35)
        packet = pack_helper(helper)
        if len(packet) != PACKET_BYTES:
            raise AssertionError("canonical packet length changed")
        if int.from_bytes(packet, "big") >> PAYLOAD_BITS:
            raise AssertionError("canonical packet has non-zero padding")
        packets.append(packet)
        helpers.append(helper)
        valid_packets += 1
        restored = unpack_helper(packet)
        if pack_helper(restored) != packet:
            raise AssertionError("canonical packet failed byte-for-byte round-trip")
        canonical_round_trips += 1

    # Every padding bit is outside the semantic coordinate stream and must be rejected.
    for packet in packets:
        for bit in range(PADDING_BITS):
            if _accepted(_mutate_padding(packet, bit)):
                raise AssertionError("non-zero padding was accepted")
            padding_rejected += 1

    # The compressed coordinate space is full by construction.  A payload mutation is
    # therefore accepted, but it must not silently alias the original expanded helper.
    for index, (packet, helper) in enumerate(zip(packets, helpers)):
        bit = (index * 37 + 11) % PAYLOAD_BITS
        mutated = _mutate_payload(packet, bit)
        if not _accepted(mutated):
            raise AssertionError("a legal coordinate payload was rejected")
        payload_accepted += 1
        if unpack_helper(mutated) == helper:
            raise AssertionError("a payload mutation aliased the helper")
        payload_changed += 1

    for _ in range(RANDOM_PACKETS):
        packet = rng.randbytes(PACKET_BYTES)
        if _accepted(packet):
            random_accepted += 1

    return {
        "seed": SEED,
        "blocks": BLOCKS,
        "rank_per_block": RANK,
        "payload_bits": PAYLOAD_BITS,
        "packet_bytes": PACKET_BYTES,
        "padding_bits": PADDING_BITS,
        "valid_packets": valid_packets,
        "canonical_round_trips": canonical_round_trips,
        "padding_mutations": TRIALS * PADDING_BITS,
        "padding_rejected": padding_rejected,
        "payload_mutations": TRIALS,
        "payload_accepted": payload_accepted,
        "payload_changed_helper": payload_changed,
        "random_packets": RANDOM_PACKETS,
        "random_accepted": random_accepted,
        "random_acceptance_percent": 100.0 * random_accepted / RANDOM_PACKETS,
    }


def main() -> None:
    result = run()
    print("Canonical packed helper contract [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[proved] Four zero padding bits are a representational boundary; payload words fill the coordinate space.")
    print("[open conjecture] No deployed wire-format, integrity, leakage, security, or hardware claim is made.")


if __name__ == "__main__":
    main()
