#!/usr/bin/env bash
# Every synthesis figure this project quotes, in one run.
#
# The areas were gathered over six loops as individual yosys invocations, typed
# into documents by hand. That makes them unreproducible in practice: nobody can
# check them without reconstructing six sessions of shell history, and a change of
# library or tool version would go unnoticed until it contradicted something.
#
# This runs every probe and prints the table. It also runs the testbenches first,
# because this project's rule is that no area is quoted for a circuit that has not
# decoded correctly, and a script that prints areas without checking that rule
# would quietly break it.
#
# Usage:  ./measure_all.sh [path-to-liberty]
# Default liberty is /tmp/sky130.lib, the SkyWater standard cells at the typical
# corner. Exit code 1 if any testbench fails.

set -u
cd "$(dirname "$0")"

# --verify-only runs the testbenches and stops. The synthesis half needs a standard-cell
# liberty, which is 13 MB of PDK and is not in this repository; the verification half
# needs only iverilog, so it is the half that can run in CI. Splitting them is what makes
# "every quoted figure comes from a circuit that was exercised" enforceable by a machine
# rather than by whoever remembered to run this.
VERIFY_ONLY=0
if [ "${1:-}" = "--verify-only" ]; then
    VERIFY_ONLY=1
    shift
fi

LIB="${1:-/tmp/sky130.lib}"

if [ "$VERIFY_ONLY" -eq 0 ] && [ ! -f "$LIB" ]; then
    echo "liberty file not found: $LIB" >&2
    echo "areas below would be meaningless without it; stopping" >&2
    echo "run with --verify-only to check the testbenches without synthesising" >&2
    exit 1
fi

fail=0
ran=0

run_tb () {   # name, output-regex, iverilog args...
    local name="$1"; shift
    # "mktemp -t tb" is a BSD spelling; GNU coreutils rejects a template with no X's.
    # This script had never run anywhere but a Mac, which is how a reproduction script
    # goes eighty loops without being reproducible - see W-INTL-158.
    local bin; bin="$(mktemp "${TMPDIR:-/tmp}/tb.XXXXXX")"
    ran=$((ran + 1))
    if ! iverilog -g2012 -o "$bin" "$@" 2>/dev/null; then
        echo "  FAIL  $name (did not compile)"; fail=1; return
    fi
    if "$bin" 2>/dev/null | grep -q '^PASS'; then
        echo "  ok    $name"
    else
        echo "  FAIL  $name"; fail=1
    fi
    rm -f "$bin"
}

area () {     # label, top, params..., files...
    local label="$1" top="$2" params="$3"; shift 3
    local script="read_verilog -sv $*; "
    for p in $params; do script+="chparam -set ${p%=*} ${p#*=} $top; "; done
    script+="hierarchy -top $top; synth -top $top -flatten; "
    script+="dfflibmap -liberty $LIB; abc -liberty $LIB; opt_clean; stat -liberty $LIB"
    local a
    a=$(yosys -p "$script" 2>/dev/null | grep "Chip area for module" | grep -o '[0-9.]*$')
    if [ -z "$a" ]; then
        printf "  %-44s %14s\n" "$label" "SYNTH FAILED"; fail=1
    else
        printf "  %-44s %14.0f  %6.2f tiles\n" "$label" "$a" "$(echo "$a/18032" | bc -l)"
    fi
}

echo "== verification: nothing below is quoted for a circuit that fails here =="
run_tb "key-equation solver, GF(2^8) t=18" \
    -DTVAL=18 -DMVAL=8 -DREDVAL="8'h1D" bm_area_probe.v tb_bm.v
run_tb "key-equation solver, GF(2^7) t=27" \
    -DTVAL=27 -DMVAL=7 -DREDVAL="7'h09" bm_area_probe.v tb_bm.v
run_tb "full decode end to end, GF(2^8) t=18" \
    -DMVAL=8 -DTVAL=18 -DREDVAL="8'h1D" -DTOPNAME=bch255_tables \
    bch255_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^7) t=27" \
    -DMVAL=7 -DTVAL=27 -DREDVAL="7'h09" -DTOPNAME=bch127_tables \
    bch127_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^7) t=23" \
    -DMVAL=7 -DTVAL=23 -DREDVAL="7'h09" -DTOPNAME=bch127t23_tables \
    bch127t23_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^8) t=42" \
    -DMVAL=8 -DTVAL=42 -DREDVAL="8'h1D" -DTOPNAME=bch255t42_tables \
    bch255t42_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^9) t=54" \
    -DMVAL=9 -DTVAL=54 -DREDVAL="9'h011" -DTOPNAME=bch511t54_tables \
    bch511t54_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^7) t=31" \
    -DMVAL=7 -DTVAL=31 -DREDVAL="7'h09" -DTOPNAME=bch127t31_tables \
    bch127t31_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^8) t=43" \
    -DMVAL=8 -DTVAL=43 -DREDVAL="8'h1D" -DTOPNAME=bch255t43_tables \
    bch255t43_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^8) t=45" \
    -DMVAL=8 -DTVAL=45 -DREDVAL="8'h1D" -DTOPNAME=bch255t45_tables \
    bch255t45_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^7) t=21" \
    -DMVAL=7 -DTVAL=21 -DREDVAL="7'h09" -DTOPNAME=bch127t21_tables \
    bch127t21_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^8) t=31" \
    -DMVAL=8 -DTVAL=31 -DREDVAL="8'h1D" -DTOPNAME=bch255t31_tables \
    bch255t31_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^7) t=7" \
    -DMVAL=7 -DTVAL=7 -DREDVAL="7'h09" -DTOPNAME=bch127t7_tables \
    bch127t7_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "shared-multiplier solver vs replicated, GF(2^7) t=7" \
    -DTVAL=7 -DMVAL=7 -DREDVAL="7'h09" bm_serial.v bm_area_probe.v tb_bm_diff.v
run_tb "SLLC encoder vs polynomial division, BCH(127,78,7)" \
    sllc127t7.v tb_sllc127t7.v
run_tb "full decode end to end, GF(2^7) t=11" \
    -DMVAL=7 -DTVAL=11 -DREDVAL="7'h09" -DTOPNAME=bch127t11_tables \
    bch127t11_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "full decode end to end, GF(2^7) t=13" \
    -DMVAL=7 -DTVAL=13 -DREDVAL="7'h09" -DTOPNAME=bch127t13_tables \
    bch127t13_tables.v bm_area_probe.v tb_bch_e2e.v
run_tb "shared-multiplier solver vs replicated, GF(2^7) t=11" \
    -DTVAL=11 -DMVAL=7 -DREDVAL="7'h09" bm_serial.v bm_area_probe.v tb_bm_diff.v
run_tb "shared-multiplier solver vs replicated, GF(2^7) t=13" \
    -DTVAL=13 -DMVAL=7 -DREDVAL="7'h09" bm_serial.v bm_area_probe.v tb_bm_diff.v
run_tb "shared-multiplier solver vs replicated, GF(2^7) t=21" \
    -DTVAL=21 -DMVAL=7 -DREDVAL="7'h09" bm_serial.v bm_area_probe.v tb_bm_diff.v
run_tb "SLLC encoder vs polynomial division, BCH(127,57,11)" \
    sllc127t11.v tb_sllc127t11.v
run_tb "SLLC encoder vs polynomial division, BCH(127,29,21)" \
    sllc127t21.v tb_sllc127t21.v
run_tb "Reed-Muller decoder R(1,6)" rm_area_probe.v tb_rm.v
run_tb "characterisation readout" ro_characteriser.v tb_ro_char.v

# The count is checked, not just the failures. A run that compiles nothing and reports
# nothing looks identical to a clean one otherwise - the shape of W-INTL-153.
if [ "$ran" -lt 20 ]; then
    echo
    echo "only $ran testbenches ran; expected the full set" >&2
    exit 1
fi

if [ "$fail" -ne 0 ]; then
    echo
    echo "a testbench failed; areas are not printed" >&2
    exit 1
fi

echo
echo "  $ran testbenches ran, $fail failed"

if [ "$VERIFY_ONLY" -eq 1 ]; then
    echo "  --verify-only: stopping before synthesis"
    exit 0
fi

echo
echo "== areas, SkyWater typical corner, one tile = 18,032 um^2 =="
echo
echo "  the recommendation, BCH(127,57,11) with the shared-multiplier solver:"
area "syndrome bank + Chien search" bch127t11_tables "" bch127t11_tables.v
area "key-equation solver, shared" bm_serial "T=11 M=7 RED=9" bm_serial.v bm_area_probe.v
echo
echo "  and the next code up, BCH(127,50,13):"
area "syndrome bank + Chien search" bch127t13_tables "" bch127t13_tables.v
area "key-equation solver, shared" bm_serial "T=13 M=7 RED=9" bm_serial.v bm_area_probe.v
echo
echo "  the construction it replaced, BCH(127,29,21), both solvers:"
area "key-equation solver, shared" bm_serial "T=21 M=7 RED=9" bm_serial.v bm_area_probe.v
echo
echo "  the cheapest build if the error rate holds at four percent, BCH(127,29,21):"
area "syndrome bank + Chien search" bch127t21_tables "" bch127t21_tables.v
area "key-equation solver" bm_area_probe "T=21 M=7 RED=9" bm_area_probe.v
echo
echo "  and its GF(2^8) counterpart, BCH(255,55,31):"
area "syndrome bank + Chien search" bch255t31_tables "" bch255t31_tables.v
area "key-equation solver" bm_area_probe "T=31 M=8 RED=29" bm_area_probe.v
echo
echo "  the construction for a five percent error rate, BCH(127,22,23):"
area "syndrome bank + Chien search" bch127t23_tables "" bch127t23_tables.v
area "key-equation solver" bm_area_probe "T=23 M=7 RED=9" bm_area_probe.v
echo
echo "  the construction it replaced, BCH(127,15,27):"
area "syndrome bank + Chien search" bch127_tables "" bch127_tables.v
area "key-equation solver" bm_area_probe "T=27 M=7 RED=9" bm_area_probe.v
echo
echo "  the fallback if both error rate and entropy come in poor, BCH(255,47,42):"
area "syndrome bank + Chien search" bch255t42_tables "" bch255t42_tables.v
area "key-equation solver" bm_area_probe "T=42 M=8 RED=29" bm_area_probe.v
echo
echo "  measured to test whether the flat band is an artefact of a sparse set:"
area "BCH(127,8,31)  syndrome + Chien" bch127t31_tables "" bch127t31_tables.v
area "BCH(127,8,31)  solver" bm_area_probe "T=31 M=7 RED=9" bm_area_probe.v
area "BCH(255,45,43) syndrome + Chien" bch255t43_tables "" bch255t43_tables.v
area "BCH(255,45,43) solver" bm_area_probe "T=43 M=8 RED=29" bm_area_probe.v
area "BCH(255,37,45) syndrome + Chien" bch255t45_tables "" bch255t45_tables.v
area "BCH(255,37,45) solver" bm_area_probe "T=45 M=8 RED=29" bm_area_probe.v
echo
echo "  rejected: BCH(511,139,54), decoder alone exceeds the whole budget"
area "syndrome bank + Chien search" bch511t54_tables "" bch511t54_tables.v
area "key-equation solver" bm_area_probe "T=54 M=9 RED=17" bm_area_probe.v
echo
echo "  the code it replaced, BCH(255,131) t=18 over GF(2^8):"
area "syndrome bank + Chien search" bch255_tables "" bch255_tables.v
area "key-equation solver" bm_area_probe "T=18 M=8 RED=29" bm_area_probe.v
echo
echo "  the construction withdrawn for negative residual entropy:"
area "R(1,6) + repetition decoders" rm_area_probe "M=6 R=3" rm_area_probe.v
area "R(1,5) + repetition decoders" rm_area_probe "M=5 R=3" rm_area_probe.v
echo
echo "  the SLLC stages, keyed by the generator degree which is n-k:"
area "encoder, BCH(127,57,11), degree 70" sllc127t11_encoder "" sllc127t11.v
area "unmask,  BCH(127,57,11)" sllc127t11_unmask "" sllc127t11.v
area "encoder, BCH(127,29,21), degree 98" sllc127t21_encoder "" sllc127t21.v
area "unmask,  BCH(127,29,21)" sllc127t21_unmask "" sllc127t21.v
echo
echo "  the instrument:"
area "characterisation readout, 272 oscillators" ro_characteriser \
     "NRO=272 CW=20 GATE=16" ro_characteriser.v
area "characterisation readout, 64 oscillators" ro_characteriser \
     "NRO=64 CW=20 GATE=16" ro_characteriser.v
echo
echo "  oscillator area is not synthesised: a ring oscillator is a physical"
echo "  structure, not a logic cell. It is scaled from the measured inverter area"
echo "  in the published tile, 6,730 um^2 across 1,792 inverters, seven per"
echo "  oscillator - so 26.3 um^2 each, and 7,151 for a bank of 272."
