#!/usr/bin/env python3
"""Finite sequence-domain and wrap boundary control.

Status: [measured] software/protocol-boundary control only. W-INTL-269 covered
ordinary in-window reordering, but did not exercise the unsigned counter's two
endpoints or an attempted rollover.

[proved] In this fixed byte layout, the encoder admits exactly the unsigned
64-bit domain, and a bitmap verifier whose high-water mark is at the maximum
value does not treat sequence zero as a successor.
[open conjecture] This is not a rollover protocol, persistent anti-rollback
storage, or a security proof. Key management, distributed ordering, loss
recovery, leakage, active attacks, side channels, area, timing, FPGA behavior,
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
    TEST_KEY,
    authenticate,
)
from key_generator_e2e import BLOCKS, enrol  # noqa: E402
from framed_helper_contract import frame  # noqa: E402
from sliding_window_freshness import SlidingWindowVerifier  # noqa: E402
from syndrome_basis_compression import pack_helper  # noqa: E402

SEED = 20260903
TRIALS = 64


def _payload(rng) -> bytes:
    _, helper = enrol(rng, 0.35)
    return pack_helper(helper)


def run() -> dict[str, int]:
    rng = random.Random(SEED)
    zero_accepted = max_accepted = overflow_rejected = 0
    negative_rejected = noninteger_rejected = wrap_rejected = 0

    for trial in range(TRIALS):
        payload = _payload(rng)
        packet = frame(payload)

        # Exercise both endpoints as valid encoded values, independently. This
        # is a byte-domain control, not a claim about long-lived deployments.
        zero = SlidingWindowVerifier()
        if zero.accept(authenticate(packet, 0, TEST_KEY)) != payload:
            raise AssertionError("zero sequence failed endpoint acceptance")
        zero_accepted += 1

        maximum = SlidingWindowVerifier()
        if maximum.accept(authenticate(packet, MAX_SEQUENCE, TEST_KEY)) != payload:
            raise AssertionError("maximum sequence failed endpoint acceptance")
        max_accepted += 1

        # Values outside the encoder's unsigned domain must fail before a frame
        # is constructed, rather than being silently truncated or wrapped.
        for value, counter in (
            (MAX_SEQUENCE + 1, "overflow"),
            (-1, "negative"),
            (1.5, "noninteger"),
            ("1", "noninteger"),
        ):
            try:
                authenticate(packet, value, TEST_KEY)
            except AssertionError:
                if counter == "overflow":
                    overflow_rejected += 1
                elif counter == "negative":
                    negative_rejected += 1
                else:
                    noninteger_rejected += 1
            else:
                raise AssertionError(f"{counter} sequence was accepted")

        # A fixed verifier must refuse an apparent rollover from 2^64-1 to 0.
        # Check that the failed successor does not mutate the high-water state.
        wrapped = SlidingWindowVerifier()
        wrapped.accept(authenticate(packet, MAX_SEQUENCE, TEST_KEY))
        before = (wrapped.highest, wrapped.seen)
        try:
            wrapped.accept(authenticate(packet, 0, TEST_KEY))
        except AssertionError:
            wrap_rejected += 1
        else:
            raise AssertionError("sequence zero was accepted after maximum")
        if (wrapped.highest, wrapped.seen) != before:
            raise AssertionError("rejected rollover changed verifier state")

    return {
        "seed": SEED,
        "blocks": BLOCKS,
        "trials": TRIALS,
        "sequence_bytes": SEQUENCE_BYTES,
        "zero_accepted": zero_accepted,
        "max_accepted": max_accepted,
        "overflow_rejected": overflow_rejected,
        "negative_rejected": negative_rejected,
        "noninteger_rejected": noninteger_rejected,
        "wrap_rejected": wrap_rejected,
    }


def main() -> None:
    result = run()
    print("Sequence-domain boundary control [measured]")
    for key, value in result.items():
        print(f"{key}={value}")
    print("[proved] The fixed unsigned domain accepts both endpoints and refuses apparent rollover.")
    print("[open conjecture] This is not a deployed rollover protocol or a security proof.")


if __name__ == "__main__":
    main()
