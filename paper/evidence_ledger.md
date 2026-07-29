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
| E10 | Inference core runs at 309 MHz on Artix-7 | hw | bench board, timing report | a timing report below the stated frequency |
| E11 | Three compute boards connected over USB | hw | inventory | fewer than three enumerated |
| E12 | Quantisation-aware training pipeline for 1.58-bit weights | test | training runs reproducible from repository | a run that does not converge to the reported metric |
| E13 | Top-5 placement at 0.9650 bits per byte | hw, third-party | public leaderboard entry | leaderboard record showing otherwise |
| E14 | Multiplier-free ternary tile, zero DSP | test | RTL plus self-checking testbench, 206 directed and random vectors against a golden model | any synthesis report allocating a DSP, or any vector mismatch |
| E15 | End-to-end language model inference | not built | no attention, no key-value cache, no normalisation or quantisation units | this row exists to prevent comparison against full-system baselines |
| E16 | Throughput and power figures for the compute node | not measured | ceiling estimated from memory bandwidth only | measure on device; the estimate must not be quoted as a benchmark |

## 3. Numeric foundation

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E17 | GoldenFloat format family published | written, external | arXiv:2606.05017 | withdrawal of the preprint |
| E18 | Numeric format catalog published | written, external | arXiv:2606.09686 | withdrawal of the preprint |
| E19 | Catalog size | inconsistent | cited as three different counts across three public repositories | reconcile against the preprint before submission; see audit W-INTL-16 |
| E20 | Energy advantage over a general-purpose baseline | modelled | naive and honest calculations published side by side; honest figure 4x to 8x, 95% CI [3, 10] | a measured end-to-end comparison falling outside the interval |

## 4. Economics

| # | Claim | Level | Artefact | Falsified by |
|---|---|---|---|---|
| E21 | Four proof types settle through one contract with seven checks | written | contract source | a settlement path that bypasses any check |
| E22 | No premine, no venture allocation, no treasury | written | contract source, deployable and auditable | any allocation found in the deployed bytecode |
| E23 | Contracts deployed to testnet | written | testnet deployment | absence of the deployment |
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

  hw          9 rows
  test        3 rows
  written     9 rows
  sim         3 rows
  conjecture  1 row
  refuted     1 row
  not built   2 rows
  inconsistent 1 row

Two rows are deliberately negative (E15, E16) and one is deliberately refuted
(E28). A ledger that contains only supporting rows is a marketing document.
