# Research files land here in Wave-intl-1 Phase 3.

`reliability_metadata_cost.py` measures the finite BCH metadata precision/cost control for W-INTL-261.

`paired_anchor_commit_control.py` measures the W-INTL-274 finite update-boundary control:
the journal, anchor, and commit record are checked as one generation-bound bundle.
`generation_transition_control.py` measures the W-INTL-275 finite policy that a
paired bundle must advance exactly one generation; replay, stale, skipped,
ambiguous, tampered, and malformed candidates are rejected without state mutation.
