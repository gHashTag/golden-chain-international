#!/usr/bin/env python3
"""Finite generation-transition guard for the paired journal bundle.

W-INTL-274 binds a journal, an independent anchor, and a commit record, but a
complete older bundle is still a valid parser input. This control adds the local
transition rule used by a caller: a candidate bundle must be exactly one
monotone generation beyond the active bundle. Replay, stale candidates,
skipped generations, and ambiguous same-generation candidates fail closed.

[measured] This is a pure software transition check over canonical bytes. It is
not a persistent counter, a transaction, a crash-consistency result, a storage
durability result, a rollback-resistant deployment, or a security proof.
"""

from __future__ import annotations

from dataclasses import dataclass

from checkpoint_journal_recovery import Slot, State, _slot_bytes
from paired_anchor_commit_control import Bundle, make_bundle, recover_bundle

SEED = 20260908
TRIALS = 64


@dataclass(frozen=True)
class TransitionResult:
    state: State
    bundle: Bundle


def _state_for(generation: int, trial: int, salt: int = 0) -> State:
    return State(
        generation=generation,
        highest=10_000 + trial * 7 + salt,
        seen=(trial * 29 + salt) & 0xFF,
    )


def _bundle(previous: State, current: State) -> Bundle:
    journal = (_slot_bytes(Slot(0, previous)), _slot_bytes(Slot(1, current)))
    return make_bundle(journal, current)


def apply_transition(active: Bundle, candidate: Bundle) -> TransitionResult:
    """Apply one adjacent generation without mutating either input bundle."""
    active_state = recover_bundle(active)
    candidate_state = recover_bundle(candidate)
    if candidate_state.generation != active_state.generation + 1:
        raise AssertionError("candidate is not the adjacent next generation")
    return TransitionResult(candidate_state, candidate)


def run() -> dict[str, int]:
    adjacent_accepted = replay_rejected = stale_rejected = 0
    skip_rejected = ambiguous_rejected = 0
    tampered_rejected = length_rejected = 0
    rejected_state_unchanged = 0

    for trial in range(TRIALS):
        base = _state_for(100 + trial * 3, trial)
        current = _state_for(base.generation + 1, trial, 1)
        next_state = _state_for(current.generation + 1, trial, 2)
        stale = _state_for(base.generation, trial, 3)
        skipped = _state_for(current.generation + 2, trial, 4)
        alternate = _state_for(current.generation, trial, 5)

        active = _bundle(base, current)
        adjacent = _bundle(current, next_state)
        replay = active
        stale_bundle = _bundle(base, stale)
        skipped_bundle = _bundle(current, skipped)

        applied = apply_transition(active, adjacent)
        if applied.state != next_state or applied.bundle != adjacent:
            raise AssertionError("adjacent generation was not applied exactly")
        adjacent_accepted += 1

        for candidate, counter in (
            (replay, "replay"),
            (stale_bundle, "stale"),
            (skipped_bundle, "skip"),
        ):
            before = recover_bundle(active)
            try:
                apply_transition(active, candidate)
            except AssertionError:
                if recover_bundle(active) != before:
                    raise AssertionError(f"{counter} rejection changed active state")
                rejected_state_unchanged += 1
                if counter == "replay":
                    replay_rejected += 1
                elif counter == "stale":
                    stale_rejected += 1
                else:
                    skip_rejected += 1
            else:
                raise AssertionError(f"{counter} candidate was accepted")

        # Both slots are valid but carry different states at one generation.
        # The inherited journal parser rejects this ambiguity before transition.
        ambiguous_journal = (
            _slot_bytes(Slot(0, current)),
            _slot_bytes(Slot(1, alternate)),
        )
        ambiguous = make_bundle(ambiguous_journal, alternate)
        try:
            apply_transition(active, ambiguous)
        except AssertionError:
            ambiguous_rejected += 1
            rejected_state_unchanged += 1
        else:
            raise AssertionError("ambiguous same-generation bundle was accepted")

        # A self-consistent candidate with a modified commit record must still
        # fail before the generation rule can be considered.
        tampered = bytearray(adjacent.commit)
        tampered[7] ^= 1 << (trial % 8)
        tampered_bundle = Bundle(adjacent.journal, adjacent.anchor, bytes(tampered))
        try:
            apply_transition(active, tampered_bundle)
        except AssertionError:
            tampered_rejected += 1
            rejected_state_unchanged += 1
        else:
            raise AssertionError("tampered candidate was accepted")

        for malformed in (
            Bundle(adjacent.journal, adjacent.anchor, adjacent.commit[:-1]),
            Bundle(adjacent.journal, adjacent.anchor, adjacent.commit + b"\0"),
        ):
            try:
                apply_transition(active, malformed)
            except AssertionError:
                length_rejected += 1
                rejected_state_unchanged += 1
            else:
                raise AssertionError("malformed candidate was accepted")

    print(f"adjacent_accepted={adjacent_accepted}")
    print(f"replay_rejected={replay_rejected}")
    print(f"stale_rejected={stale_rejected}")
    print(f"skip_rejected={skip_rejected}")
    print(f"ambiguous_rejected={ambiguous_rejected}")
    print(f"tampered_rejected={tampered_rejected}")
    print(f"length_rejected={length_rejected}")
    print(f"rejected_state_unchanged={rejected_state_unchanged}")
    return {
        "adjacent_accepted": adjacent_accepted,
        "replay_rejected": replay_rejected,
        "stale_rejected": stale_rejected,
        "skip_rejected": skip_rejected,
        "ambiguous_rejected": ambiguous_rejected,
        "tampered_rejected": tampered_rejected,
        "length_rejected": length_rejected,
        "rejected_state_unchanged": rejected_state_unchanged,
    }


if __name__ == "__main__":
    run()
