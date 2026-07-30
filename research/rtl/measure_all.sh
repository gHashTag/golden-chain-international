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
LIB="${1:-/tmp/sky130.lib}"
cd "$(dirname "$0")"

if [ ! -f "$LIB" ]; then
    echo "liberty file not found: $LIB" >&2
    echo "areas below would be meaningless without it; stopping" >&2
    exit 1
fi

fail=0

run_tb () {   # name, output-regex, iverilog args...
    local name="$1"; shift
    local bin; bin="$(mktemp -t tb)"
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
run_tb "Reed-Muller decoder R(1,6)" rm_area_probe.v tb_rm.v
run_tb "characterisation readout" ro_characteriser.v tb_ro_char.v

if [ "$fail" -ne 0 ]; then
    echo
    echo "a testbench failed; areas are not printed" >&2
    exit 1
fi

echo
echo "== areas, SkyWater typical corner, one tile = 18,032 um^2 =="
echo
echo "  the chosen construction, BCH(127,22,23) over GF(2^7):"
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
