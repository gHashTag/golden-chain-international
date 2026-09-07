#!/usr/bin/env python3
"""Finite control for a keyed tag around the candidate helper frame.

Status: [measured] software/protocol-boundary control only.  W-INTL-266 checked
canonical parsing and an unkeyed digest witness.  This separate control checks
the missing key-dependent acceptance boundary without changing W-INTL-262's
PUF key equation or claiming a deployed fuzzy extractor.

[proved] For the fixed byte layout and fixed demonstration key, the verifier
accepts the exact authenticated frame and rejects a wrong key, a changed tag,
a changed inner frame, and a tag made under a different domain string.  The
constant-time comparison is a property of this finite verifier, not a theorem
about attacks.
[open conjecture] The demonstration key is public test data, HMAC truncation is
not a security level, and no claim is made about key management, leakage,
replay/freshness, active attackers, deployment, area, timing, FPGA behavior, or
G16 hardware.
"""

from __future__ import annotations

import hashlib
import hmac
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from framed_helper_contract import frame, parse  # noqa: E402
from key_generator_e2e import BLOCKS, enrol  # noqa: E402
from syndrome_basis_compression import pack_helper  # noqa: E402

SEED = 20260824
TRIALS = 64
TAG_BYTES = 16
DOMAIN = b"gci/helper-frame/auth/v1"
ALT_DOMAIN = b"gci/helper-frame/other/v1"
# Public fixture key: this is a test vector, not a credential.
TEST_KEY = b"gci-public-fixture-key-v1"
WRONG_KEY = b"gci-public-fixture-key-v2"


def _payload(rng) -> bytes:
    _, helper = enrol(rng, 0.35)
    return pack_helper(helper)


def authenticate(packet: bytes, key: bytes = TEST_KEY, *, domain: bytes = DOMAIN) -> bytes:
    """Append a truncated HMAC over the already-framed packet."""
    if len(packet) < 1:
        raise AssertionError("empty inner frame")
    tag = hmac.new(key, domain + packet, hashlib.sha256).digest()[:TAG_BYTES]
    return packet + tag


def verify(authenticated: bytes, key: bytes = TEST_KEY, *, domain: bytes = DOMAIN) -> bytes:
    """Verify the keyed tag before delegating to the canonical inner parser."""
    if len(authenticated) <= TAG_BYTES:
        raise AssertionError("authenticated frame is truncated")
    packet, got = authenticated[:-TAG_BYTES], authenticated[-TAG_BYTES:]
    expected = hmac.new(key, domain + packet, hashlib.sha256).digest()[:TAG_BYTES]
    if not hmac.compare_digest(got, expected):
        raise AssertionError("keyed frame tag mismatch")
    # A valid tag must not bypass W-INTL-266's parser contract.
    return parse(packet)


def run() -> dict[str, int]:
    rng = random.Random(SEED)
    accepted = wrong_key_rejected = tag_mutation_rejected = frame_mutation_rejected = 0
    domain_swap_rejected = inner_parser_rejected = 0
    for _ in range(TRIALS):
        payload = _payload(rng)
        packet = frame(payload)
        authenticated = authenticate(packet)
        if verify(authenticated) != payload:
            # Compare the parser's semantic payload, not a hard-coded header offset,
            # so a future framing extension remains a test failure.
            raise AssertionError("authenticated frame failed canonical acceptance")
        accepted += 1

        for candidate, bucket in (
            (authenticate(packet, WRONG_KEY), "wrong-key"),
            (authenticated[:-1] + bytes([authenticated[-1] ^ 1]), "tag"),
            (authenticate(packet[:-1]), "frame"),
            (authenticate(packet, domain=ALT_DOMAIN), "domain"),
        ):
            try:
                verify(candidate)
            except AssertionError:
                if bucket == "wrong-key":
                    wrong_key_rejected += 1
                elif bucket == "tag":
                    tag_mutation_rejected += 1
                elif bucket == "frame":
                    frame_mutation_rejected += 1
                else:
                    domain_swap_rejected += 1
            else:
                raise AssertionError(f"{bucket} mutation was accepted")

        # An authenticated tag cannot make a malformed inner frame parseable when
        # recomputed under the test key.
        malformed = authenticate(packet[:-TAG_BYTES])
        try:
            verify(malformed)
        except AssertionError:
            inner_parser_rejected += 1
        else:
            raise AssertionError("malformed inner frame bypassed parser")

    return {
        "seed": SEED,
        "blocks": BLOCKS,
        "trials": TRIALS,
        "tag_bytes": TAG_BYTES,
        "canonical_accepted": accepted,
        "wrong_key_rejected": wrong_key_rejected,
        "tag_mutation_rejected": tag_mutation_rejected,
        "frame_mutation_rejected": frame_mutation_rejected,
        "domain_swap_rejected": domain_swap_rejected,
        "inner_parser_rejected": inner_parser_rejected,
    }


def main() -> None:
    result = run()
    print("Keyed helper-frame authentication control [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[proved] The fixed test key and domain separate the authenticated frame from the mutation classes.")
    print("[open conjecture] This is not a deployed authenticator, freshness protocol, or security proof.")


if __name__ == "__main__":
    main()
