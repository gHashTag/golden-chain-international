#!/usr/bin/env bash
# Verify the five deployed contracts on the Base Sepolia explorer.
#
# This closes audit entry W-INTL-35. The five contracts are deployed and hold
# real bytecode, but none of them is source-verified, so nobody outside the
# project can confirm that the code at those addresses was built from the
# published source. On a digital-assets track someone will look, and an
# unverified contract holding 7.6 trillion tokens reads the same whether the
# explanation is honest or not.
#
# Everything needed is already known and encoded below. The compiler settings
# come from the repository's foundry configuration; the addresses and the
# constructor arguments come from the recorded deployment broadcast, so they are
# the values actually used rather than the values someone remembered.
#
# The one thing missing is an API key, which is yours and is never written down
# here. Export it and run:
#
#     export BASESCAN_API_KEY=...
#     bash scripts/verify_contracts.sh
#
# Run it from a checkout of gHashTag/trinity-contracts, since that is where the
# sources are.

set -euo pipefail

CHAIN="base-sepolia"
SOLC="0.8.24"
OPTIMIZER_RUNS=200

if [ -z "${BASESCAN_API_KEY:-}" ]; then
  echo "error: BASESCAN_API_KEY is not set." >&2
  echo "Get one at https://basescan.org/myapikey and export it before running." >&2
  exit 1
fi

if [ ! -f foundry.toml ]; then
  echo "error: run this from a checkout of gHashTag/trinity-contracts." >&2
  echo "The sources being verified have to be present." >&2
  exit 1
fi

# Address, contract path, and the ABI-encoded constructor arguments as recorded
# in broadcast/DeployAll.s.sol/84532/run-latest.json.
#
# Note the circularity, which is deliberate and worth knowing before reading the
# arguments: MiningPool was deployed against TriToken's predicted address, and
# TriToken then received MiningPool's. Each names the other.
#
# 1779117650 is the genesis timestamp shared by EmissionController and
# MiningPool.

verify() {
  local name="$1" addr="$2" path="$3" ctor="$4"
  echo
  echo "=== $name at $addr ==="
  if [ -n "$ctor" ]; then
    forge verify-contract \
      --chain "$CHAIN" \
      --compiler-version "$SOLC" \
      --num-of-optimizations "$OPTIMIZER_RUNS" \
      --constructor-args "$ctor" \
      --watch \
      "$addr" "$path"
  else
    forge verify-contract \
      --chain "$CHAIN" \
      --compiler-version "$SOLC" \
      --num-of-optimizations "$OPTIMIZER_RUNS" \
      --watch \
      "$addr" "$path"
  fi
}

# No constructor arguments.
verify "ChipRegistry" \
  0xB52F010494f5074F1Ee4EE60e1374c0aF7a29630 \
  src/ChipRegistry.sol:ChipRegistry ""

verify "JobProver" \
  0x4e8971984f7C8eaDFf76F68cF6D6D9134C3dD9F5 \
  src/JobProver.sol:JobProver ""

# uint256 genesisTimestamp
verify "EmissionController" \
  0x5Abb2aB9D97ac56BD7B4c8dF1964C150393b9520 \
  src/EmissionController.sol:EmissionController \
  "$(cast abi-encode 'constructor(uint256)' 1779117650)"

# address triToken, address chipRegistry, uint256 genesis
verify "MiningPool" \
  0xAe28EDd6c13fd8B3b5C217fd705488B30683c45E \
  src/MiningPool.sol:MiningPool \
  "$(cast abi-encode 'constructor(address,address,uint256)' \
      0x7D3ECaB5c467bd86050f9160B15c002a57249c59 \
      0xB52F010494f5074F1Ee4EE60e1374c0aF7a29630 \
      1779117650)"

# address miningPool
verify "TriToken" \
  0x7D3ECaB5c467bd86050f9160B15c002a57249c59 \
  src/TriToken.sol:TriToken \
  "$(cast abi-encode 'constructor(address)' \
      0xAe28EDd6c13fd8B3b5C217fd705488B30683c45E)"

echo
echo "Done. Check each address on https://sepolia.basescan.org and confirm the"
echo "source tab shows the contract rather than an invitation to publish it."
echo
echo "If a verification fails on a bytecode mismatch, the usual cause is that the"
echo "checkout is not at the commit that was deployed. The broadcast record names"
echo "commit b8410a0."
