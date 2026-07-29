# Evidence Ledger

Status: Wave-intl-2 draft
Scope: every externally visible claim made by Trinity / TRI-NET / Golden Chain,
mapped to the artefact that supports it and the level at which it is verified.

Purpose. A reviewer should not have to trust a summary. Each row states what is
claimed, where the evidence lives, and what would falsify it. Rows that cannot
be supported are listed as such rather than omitted.

Verification levels, in decreasing strength:

  hw          measured on physical hardware, artefact recorded
  test        passing automated test, reproducible from the repository
  sim         simulation or model only, not run on hardware
  written     specified or implemented but not executed in its target context
  conjecture  [Open conjecture] per hard rule 10, falsification path stated

---

## 1. Mesh and radio

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E1 | Authenticated encryption runs on the node CPU | hw | 534,604-byte static ARM binary, sha256 recorded, exit code 0, 2026-07-01 | rebuild from source produces a different hash, or a non-zero exit on device |
| E2 | Radio front end tunes to 5.8 GHz | hw | LO 5.8 GHz, FFT peak +0.999 MHz, 30.72 MHz sample rate, 65,536 samples | re-run of the capture fails to place the tone within tolerance |
| E3 | Signal is 108.6 dB over the noise floor | hw, loopback only | digital loopback capture | any restatement of this figure as an over-the-air result is a claim error, not a measurement error |
| E4 | Three mesh nodes are physically connected | hw | assembled and powered, 2026-07-04 | photograph or inventory showing fewer than three |
| E5 | Multi-hop IP routing with link-cost metric | sim | Rust unit tests | not yet falsifiable on hardware; run M2 on device |
| E6 | Throughput sustained across two hops | sim | not run | run M3 with bench attenuators |
| E7 | Three-node triangle shares one uplink | sim | not run | this is the P2 gate; run M4 |
| E8 | Mesh self-heals within a measured time | undefined | no definition landed | define the metric before claiming it |
| E9 | Nothing has been transmitted over the air | hw, negative | regulatory status recorded | any RF emission without amplifier and licence would contradict this |

## 2. Compute

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E10 | Inference core runs at 309 MHz on Artix-7 | refuted | as stated. No timing report exists; 309 is one of three clock values swept in a performance model, and the project's own synthesis notes record that place and route was not run and that there is no Fmax data | already falsified on 2026-07-29; see audit W-INTL-29. A real Fmax requires place and route, which is blocked on toolchain |
| E11 | Three compute boards connected over USB | hw | inventory | fewer than three enumerated |
| E12 | Quantisation-aware training pipeline for 1.58-bit weights | test | training runs reproducible from repository | a run that does not converge to the reported metric |
| E13 | Five public submissions to a constrained-budget compression challenge, three of them withdrawn by the author on stated technical grounds | written, external, third-party visible | pull requests on the challenge repository, with the withdrawal reasoning in their comment threads; the leading entry was retracted by the author together with the argument for why its measurement was invalid | any of the submissions or their closing comments being absent from the public record. The earlier form of this row asserted a Top-5 placement at 0.9650 bits per byte; the artefact search found no such score in the submission history and it was removed. See audit W-INTL-28 |
| E14 | Multiplier-free ternary tile, zero DSP | test, independently reproduced | RTL plus self-checking testbench; reproduced from a clean checkout on 2026-07-29: the testbench compiles and runs to 206 tests, 206 pass, 0 fail, measured lane density 1563/3200; separately, Xilinx-targeted synthesis of the tile emits no DSP primitive of any kind, only LUT, CARRY4, FDCE and MUXF cells | any synthesis report allocating a DSP, or any vector mismatch. Neither occurred when the check was run |
| E15 | End-to-end language model inference | not built | no attention, no key-value cache, no normalisation or quantisation units | this row exists to prevent comparison against full-system baselines |
| E16 | Throughput and power figures for the compute node | not measured | ceiling estimated from memory bandwidth only | measure on device; the estimate must not be quoted as a benchmark |

## 3. Numeric foundation

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E17 | GoldenFloat format family published | written, external | arXiv:2606.05017 | withdrawal of the preprint |
| E18 | Numeric format catalog published | written, external | arXiv:2606.09686 | withdrawal of the preprint |
| E19 | Catalog size is 83 formats in 13 families | written, external | arXiv:2606.09686v2 of 2026-06-22 states 83 in title and abstract; SSOT specs/numeric/formats_catalog.t27 in gHashTag/t27 counts 83 records with no duplicate ids; public READMEs of gHashTag/trinity-fpga and gHashTag/t27 both state 83; the superseded count 84 survives only inside the two published errata, which is where it belongs | a direct count of the SSOT returning a number other than 83, or any public artefact outside an erratum asserting a different size |
| E20 | Energy advantage over a general-purpose baseline | modelled, artefact not located | the row names naive and honest calculations published side by side, honest figure 4x to 8x with 95 percent CI [3, 10]. A search on 2026-07-29 did not find either calculation in any reachable repository. The figure may be sound; what is missing is the working | a measured end-to-end comparison falling outside the interval, or the calculations not being produced. This is now the only externally quoted number in the application with no locatable derivation |

## 4. Economics

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E21 | Four proof types settle through one contract with seven checks | not built | the named artefact is contract source, and no such source was found. The only Solidity contract under this account is a token; a search for any contract named for rewards, proofs or settlement returns nothing, and the one rewards script calls claimVested on that token, which is a vesting withdrawal and not a proof settlement | already falsified unless the source is produced. See audit W-INTL-30 |
| E22 | No premine, no venture allocation, no treasury | refuted | the contract source settles it. TrinityToken.sol fixes the split in hardcoded constants: founder 20 percent, node rewards 40, community 20, treasury 10, liquidity 10, of a 10,460,353,203 token supply, with founder tokens vesting over 48 months behind a 12 month cliff and treasury over 60 months behind a 6 month cliff. The Sepolia deployment record assigns all five to the deployer's address | already falsified. Not resolvable by pointing at a different instrument, because no other contract exists under this account. See audit W-INTL-30 |
| E23 | Contracts deployed to testnet | confirmed, third-party verifiable | token deployed to Sepolia, chain id 11155111, address 0xef368e29FA3aB2eaf02BccD05438ED3bafE9f469, recorded 2026-02-16 in deploy/contracts/deployment-sepolia.json in gHashTag/trinity; a second record exists for a local chain | the address returning no code on Sepolia. Note that this row and E22 describe the same artefact and disagree; see W-INTL-30 |
| E24 | Mainnet settlement operates | conjecture | blocked: settlement requires device signatures that do not yet exist | see audit W-INTL-17; falsified or resolved by a transitional signing mode |
| E25 | Three proof types operate today | written, software-signed | node daemon | the contract does not accept software signatures; see W-INTL-17 |

## 5. Attestation

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E26 | Attestation is rooted in the device, not a vendor enclave | written | mesh node part carries a bitstream signature scheme | demonstration that the trust path depends on a third-party enclave |
| E27 | Compute boards are a bench tier, not the trust anchor | written, by design | documented separation | any settlement path accepting a signature from the bench tier |
| E28 | Hardware class can be proven by response deadline | refuted | a native optimised software implementation completes the sequential work faster than the target device | already falsified; retained so the idea is not reintroduced |
| E29 | Hardware class can be narrowed by parallel-width challenge | partial | model | separation holds against a general-purpose processor and fails against a many-lane accelerator |
| E30 | Correctness is enforced economically | modelled | re-execution of a sampled fraction with stake forfeiture; operating point 1 percent sampling at 100x stake | a parameter set where the expected value of cheating is positive |

---

## Summary

  written       7 rows   (of which 3 external, 1 software-signed, 1 by design)
  hw            6 rows   (of which 1 loopback only, 1 negative)
  refuted       3 rows
  sim           3 rows
  modelled      2 rows
  not built     2 rows
  test          2 rows   (1 of them independently reproduced by execution)
  confirmed     1 row    (third-party verifiable on a public chain)
  conjecture    1 row
  not measured  1 row
  undefined     1 row
  partial       1 row
  total        30 rows

The economics section is the weakest part of this table and was the last to be
checked. Of its five rows, one is confirmed on a public chain, one is refuted by
the contract that confirms it, one is not built, one is a conjecture that depends
on the one that is not built, and one describes a daemon rather than a settlement.
That section should be rewritten as a design before it is shown to anyone who
reads token structures professionally.

Movement since the first draft of this ledger. E10 from hardware to refuted, its
named artefact having turned out not to exist. E13 rewritten entirely: the score
it asserted was not in the submission history, and what the search did find - a
record of submissions withdrawn by their own author on stated technical grounds -
is both true and more useful. E19 from inconsistent to verified. E14 strengthened,
having been reproduced by execution rather than read.

Three rows moved down, two moved up, and one changed into a different claim. A
ledger that only ever moves upward is not being checked.

The counts above are derived from the table by parsing the level column, not
written by hand. A ledger whose own arithmetic does not reconcile has no claim
on a reviewer's trust.

## Verification pass, 2026-07-29

Rows were tested against live artefacts rather than against the documents that
assert them. Method and outcome are recorded so the pass can be repeated.

Confirmed, and stronger than the row claimed:

- E1. The authenticated-encryption smoke test has two independent on-device runs,
  2026-07-01 on a P201Mini and 2026-07-04 on board-1, each with its own binary
  hash and RC=0, recorded in smoke/M1_RESULTS.md in gHashTag/tri-net. Two runs on
  two boards is reproduction, not a single lucky success.
- E2, E3. LO 5.8 GHz, FFT peak +0.999 MHz and SNR 108.6 dB are recorded in
  tri-net at radio/README.md and repeated in its README and ROADMAP. The source
  repository already marks the figure as digital loopback and not over the air,
  and links its own regulatory-status note. The caveat is upstream of this ledger.
- E5 to E8. The sim and undefined levels assigned here match the status table
  published in tri-net independently, including M5 being undefined.
- Absence of unsafe Rust. The crate carries forbid(unsafe_code); the only two
  textual occurrences of the word are comments explaining that fact.

Weakened or contradicted:

- E13. See audit W-INTL-28. No artefact supports the stated placement or score.
- E4. The evidence recorded upstream for three connected boards is an operator
  confirmation rather than a photograph or an inventory artefact. That is the
  weakest evidence type in an otherwise artefact-backed table and should be
  upgraded before submission.

Reproduced by execution rather than by reading:

- E14, vector count. The ternary tile testbench was compiled and run from a clean
  checkout on 2026-07-29. It reports 206 tests, 206 pass, 0 fail, and a measured
  active-lane density of 1563 out of 3200. The figure of 206 is therefore not an
  assertion in a document; it is what the testbench prints when anyone runs it.
- E14, zero DSP. The tile was synthesised against a Xilinx target in the same
  pass. The resulting cell list contains BUFG, CARRY4, FDCE, IBUF, INV, LUT2 to
  LUT6, MUXF7, MUXF8 and OBUF, and no DSP primitive of any kind. The claim holds
  under an independent synthesis, not only under the project's own assertion.
- Incidental. That synthesis emits 441 LUTs for the tile, where the project's
  performance model estimates about 380. The model is optimistic by roughly a
  sixth. This does not affect any claim made externally, but the estimate should
  be corrected before it is used in a projection.
- E19, by direct count rather than by citation. The single source of truth
  specs/numeric/formats_catalog.t27 was fetched and counted on 2026-07-29: 83
  catalog records, and 13 distinct clusters whose members sum to exactly 83.
  GoldenFloat 22, HistoricalVendor 10, PositUnumIII 8, IntegerFixed 8,
  MlLowPrecision 7, Ieee754Binary 5, Theoretical 4, Lns 4, CompressionTrick 4,
  Microscaling 3, Ieee754Decimal 3, ExtendedFloat 3, QuantTuned 2. Both published
  numbers hold.
- A note on method, since this ledger asks others to check it. The first count of
  clusters run here returned 12, not 13. The pattern used had truncated
  Ieee754Binary and Ieee754Decimal to a common prefix and merged two clusters into
  one. The instrument was wrong, not the claim. It is recorded because a checker
  who makes the same mistake will otherwise conclude that the catalog is
  misdescribed.

Not confirmed: 4,463 lines of Rust. The public mesh repository contains 6,181
lines under src and 18,708 in total, so the figure matches nothing currently
visible and is presumed to be a stale count of a repository that is not public.

Refuted: see E10 and audit W-INTL-29.

Two rows are deliberately negative (E15, E16) and one is deliberately refuted
(E28). A ledger that contains only supporting rows is a marketing document.
