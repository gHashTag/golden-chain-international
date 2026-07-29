# Evidence Ledger

Status: Wave-intl-2 draft
Scope: every externally visible claim made by Trinity / TRI-NET / Golden Chain,
mapped to the artefact that supports it and the level at which it is verified.

Purpose. A reviewer should not have to trust a summary. Each row states what is
claimed, where the evidence lives, and what would falsify it. Rows that cannot
be supported are listed as such rather than omitted.

Verification levels. Every level used in the table below is defined here; an
earlier version of this legend listed five while the table used twelve, which
left a reader meeting terms that were never explained.

Supporting, in decreasing strength:

  hw            measured on physical hardware, artefact recorded
  confirmed     verifiable by a third party without the applicant's cooperation
  test          passing automated test, reproducible from the repository
  written       specified or implemented but not executed in its target context
  modelled      derived from a model whose assumptions are stated
  sim           simulation only, not run on hardware

Non-supporting, and deliberately kept in the table:

  not built     the thing described does not exist yet
  not measured  it exists but the quoted figure was estimated, not measured
  partial       holds under some conditions and fails under others, both named
  undefined     the claim has no metric, so it cannot yet be true or false
  conjecture    [Open conjecture] per hard rule 10, falsification path stated
  refuted       the falsification test written into the row was run, and the
                claim failed it

Qualifiers may follow a level after a comma - "hw, loopback only", "hw, negative",
"test, independently reproduced" - and narrow it rather than change it.

A row may carry only the level its artefact supports. Where the two disagreed,
the level was lowered rather than the artefact restated.

---

## 1. Mesh and radio

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E1 | Authenticated encryption runs on the node CPU | hw, reproduced | two on-device runs on two different boards: 2026-07-01 on a P201Mini with a 534,604-byte static ARM binary, and 2026-07-04 on board-1 with its own binary. Each has its sha256 recorded and exited zero | rebuild from source produces a different hash, or a non-zero exit on device. A single passing run would not have been enough for this level |
| E2 | Radio front end tunes to 5.8 GHz | hw | LO 5.8 GHz, FFT peak +0.999 MHz, 30.72 MHz sample rate, 65,536 samples | re-run of the capture fails to place the tone within tolerance |
| E3 | Signal is 108.6 dB over the noise floor | hw, loopback only | digital loopback capture | any restatement of this figure as an over-the-air result is a claim error, not a measurement error |
| E4 | Three mesh nodes are physically connected | written | the upstream status table records this as hardware, but the evidence it cites is an operator confirmation dated 2026-07-04, not a photograph, an inventory record or a device enumeration. An operator confirmation is the applicant asserting it, which is what every other row in this table avoids | a photograph or inventory showing fewer than three. Upgrades to hw the moment a dated photograph with the three boards visible exists, which is five minutes of work |
| E5 | Multi-hop IP routing with link-cost metric | sim | Rust unit tests | not yet falsifiable on hardware; run M2 on device |
| E6 | Throughput sustained across two hops | sim | not run | run M3 with bench attenuators |
| E7 | Three-node triangle shares one uplink | sim | not run | this is the P2 gate; run M4 |
| E8 | Mesh self-heals within a measured time | undefined | no definition landed | define the metric before claiming it |
| E9 | Nothing has been transmitted over the air | hw, negative | regulatory status recorded | any RF emission without amplifier and licence would contradict this |

## 2. Compute

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E10 | Inference core runs at 309 MHz on Artix-7 | refuted | re-examined 2026-07-29 with a wider search. Timing data does exist, contrary to an earlier pass here: a synthesis target table records the ternary module at 4,267 LUT, 2,449 FF, zero DSP and an Fmax of at least 92 MHz, marked measured, and a separate hardware debug report records a place-and-route result of 239.46 MHz for a trivial counter design on a 50 MHz part. Neither is 309 MHz, and neither is the inference core. The measured figure for the relevant module is at least 92 MHz | already falsified. The refutation is now stronger than when it rested on absence: a measured number for the module exists and it is far below the claim. Publishing 309 would require a timing report for that core |
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
| E20 | Energy advantage over a general-purpose baseline | modelled, naive side not singular | the naive figure has been stated as at least four different values across this project's own documents: 49x in the predecessor weakness registry, 20x from dividing 1 pJ per multiply-accumulate by 0.05 pJ per add, 10 to 20x in that same document's opening, and 20 to 30x from a second pair of figures in it. The honest figure of 4x to 8x with 95 percent CI [3, 10] is therefore quoted against a baseline that has no single value, and its own derivation was not found by a search across the account under five formulations | a measured end-to-end comparison falling outside the interval. Hard rule 7 asks the naive and honest calculations to be paired, which requires the naive one to be singular first |

## 4. Economics

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E21 | Proof types settle through one contract with a fixed check sequence | confirmed, with two checks vacuous | MiningPool.sol, deployed to Base Sepolia at 0xAe28EDd6c13fd8B3b5C217fd705488B30683c45E. The era match, nullifier replay guard, register cap and non-zero reward checks are real and enforced. Two are not: the chip-registration check passes for any self-declared key because ChipRegistry has no gate, and the zero-knowledge register cannot verify because JobProver's verifying key is a labelled placeholder | any settlement path bypassing a working check. The two vacuous checks are recorded in audit W-INTL-34 rather than counted as passing |
| E22 | No premine, no venture allocation, no treasury | confirmed, third-party verifiable | TriToken.sol mints its entire supply to MiningPool in the constructor and renounces ownership in the same transaction. There is no allocation mechanism to a founder, investor, treasury or liquidity address, and supply cannot be inflated afterwards. Deployed at 0x7D3ECaB5c467bd86050f9160B15c002a57249c59 | any allocation found in the deployed bytecode. An earlier and superseded token of the same project, TrinityToken on Ethereum Sepolia, does carry a founder and treasury split; it is not this instrument. See audit W-INTL-30 |
| E23 | Contracts deployed to testnet | confirmed, third-party verifiable | five contracts on Base Sepolia, chain id 84532, deployed 2026-05-18 across seven transactions in blocks 41,674,689 to 41,674,694: TriToken, MiningPool, EmissionController, ChipRegistry and JobProver, each with its address and deploy transaction recorded | any of the addresses returning no code on Base Sepolia |
| E24 | Mainnet settlement operates | conjecture | blocked: settlement requires device signatures that do not yet exist | see audit W-INTL-17; falsified or resolved by a transitional signing mode |
| E25 | Three proof types operate today | written, software-signed | node daemon | the contract does not accept software signatures; see W-INTL-17 |

## 5. Attestation

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E26 | Attestation is rooted in the device, not a vendor enclave | not built | two separate findings put this below conjecture. The mesh node's signature scheme has a published bypass whose fix status on the deployed boot loader is unchecked (W-INTL-19), and the deployed ChipRegistry accepts any self-declared key with no signature or challenge, so device identity is currently a bookkeeping entry rather than a hardware property (W-INTL-34). The design is coherent; nothing enforcing it is running | a working off-chain challenge and response, plus a patched boot loader, would move this to written. It should not be described as implemented before then |
| E27 | Compute boards are a bench tier, not the trust anchor | written, by design | documented separation | any settlement path accepting a signature from the bench tier |
| E28 | Hardware class can be proven by response deadline | refuted | a native optimised software implementation completes the sequential work faster than the target device | already falsified; retained so the idea is not reintroduced |
| E29 | Hardware class can be narrowed by parallel-width challenge | partial | model | separation holds against a general-purpose processor and fails against a many-lane accelerator |
| E30 | Correctness is enforced economically | modelled | re-execution of a sampled fraction with stake forfeiture; operating point 1 percent sampling at 100x stake | a parameter set where the expected value of cheating is positive |

---

## Summary

  written       7 rows   (of which 3 external, 1 software-signed)
  hw            5 rows   (of which 1 reproduced, 1 loopback only, 1 negative)
  confirmed     3 rows   (all three third-party verifiable on a public chain)
  sim           3 rows
  conjecture    2 rows
  modelled      2 rows
  refuted       2 rows
  test          2 rows   (1 of them independently reproduced by execution)
  not built     1 row
  not measured  1 row
  partial       1 row
  undefined     1 row
  total        30 rows

The economics section is the weakest part of this table and was the last to be
checked. Of its five rows, one is confirmed on a public chain, one is refuted by
the contract that confirms it, one is not built, one is a conjecture that depends
on the one that is not built, and one describes a daemon rather than a settlement.
That section should be rewritten as a design before it is shown to anyone who
reads token structures professionally.

Movement since the first draft. E10 from hardware to refuted, its named artefact
having turned out not to exist. E13 rewritten: the score it asserted was not in
the submission history, and the withdrawal record that was there is both true and
more useful. E14 strengthened by reproduction. E19 from inconsistent to verified.
E26 from written to conjecture, the attestation root having a published bypass
whose fix status is unchecked.

E21, E22 and E23 moved up, and that movement was a correction of this ledger
rather than of the project. All three had been downgraded on 2026-07-29 on the
finding that no settlement contract existed. It does exist, deployed, with
addresses; the search that concluded otherwise looked in one repository and used
the wrong names. The rows are now the strongest in the table, and the audit entry
that caused the error records how it happened.

The lesson is recorded rather than quietly fixed: absence reported from a failed
search is a claim like any other, and this ledger made it three times before
checking it.

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

Confirmed on re-examination: 4,463 lines of Rust. An earlier pass here reported
that the figure matched nothing visible, having counted raw lines including blanks
and generated code. Counted the way such a figure is normally stated - source
lines under src, excluding blank and comment-only lines - the mesh repository
gives 4,370. The claim is sound and the earlier check used the wrong instrument;
see audit W-INTL-32.

Refuted: see E10 and audit W-INTL-29. Note that the earlier form of that finding
claimed no timing data existed at all. It does; the wider search found it. The
conclusion survived the correction and improved, because a measured 92 MHz for the
module refutes 309 more firmly than an absent report ever did.

Two rows are deliberately negative (E15, E16) and one is deliberately refuted
(E28). A ledger that contains only supporting rows is a marketing document.
