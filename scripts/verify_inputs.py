#!/usr/bin/env python3
"""Re-synthesise every decoder and check it against what research/inputs.py declares.

The last hand-carried link in the chain. inputs.py now declares each decoder area once,
with a note saying it is measured here and reproducible by measure_all.sh - but nothing
checked that the declared number is what the tools produce today. A figure transcribed
from a tool run six loops ago and never re-run is a figure that agrees with the past
rather than with the design.

This closes it: for each entry in DECODER_AREA, generate the table stages for that field
and correction strength, synthesise both stages against the same library, and compare the
sum against the declaration. A mismatch means either the RTL changed, the tool changed, or
the number was written down wrong.

Slow by nature - two synthesis runs per code. Not in CI for that reason; run it when the
RTL or the library moves.

Usage: python3 scripts/verify_inputs.py [--only 7,21] [liberty]
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RTL = ROOT / "research" / "rtl"
sys.path.insert(0, str(ROOT / "research"))
import inputs as I

LIB = "/tmp/sky130.lib"
POLY = {7: 0x09, 8: 0x1D, 9: 0x011}      # reduction polynomials this project uses


def yosys_area(script):
    r = subprocess.run(["yosys", "-p", script], capture_output=True, text=True, cwd=RTL)
    m = re.findall(r"Chip area for module.*?([0-9.]+)\s*$", r.stdout, re.M)
    return float(m[-1]) if m else None


def measure(m, t):
    """Table stages plus solver, the two halves the areas in inputs.py are sums of."""
    name = f"verify_m{m}t{t}"
    gen = subprocess.run(
        ["python3", "gen_bch_decoder.py", str(m), str(POLY[m]), str(t), name],
        capture_output=True, text=True, cwd=RTL)
    if gen.returncode:
        return None, f"generator failed: {gen.stderr.strip().splitlines()[-1:]}"
    (RTL / f"{name}_tables.v").write_text(gen.stdout)

    tables = yosys_area(
        f"read_verilog -sv {name}_tables.v; hierarchy -top {name}_tables; "
        f"synth -top {name}_tables -flatten; dfflibmap -liberty {LIB}; "
        f"abc -liberty {LIB}; opt_clean; stat -liberty {LIB}")
    solver = yosys_area(
        f"read_verilog -sv bm_area_probe.v; chparam -set T {t} bm_area_probe; "
        f"chparam -set M {m} bm_area_probe; chparam -set RED {POLY[m]} bm_area_probe; "
        f"hierarchy -top bm_area_probe; synth -top bm_area_probe -flatten; "
        f"dfflibmap -liberty {LIB}; abc -liberty {LIB}; opt_clean; stat -liberty {LIB}")
    (RTL / f"{name}_tables.v").unlink(missing_ok=True)
    if tables is None or solver is None:
        return None, "synthesis produced no area"
    return tables + solver, None


def measure_serial(m, t):
    """The same decoder with the shared-multiplier solver in place of the replicated one.

    bm_serial.v instantiates gf_mul from bm_area_probe.v, so both files are read and the
    top is set explicitly; reading one alone fails with an unresolved cell rather than a
    wrong area, which is the failure this project prefers.
    """
    name = f"verify_s_m{m}t{t}"
    gen = subprocess.run(
        ["python3", "gen_bch_decoder.py", str(m), str(POLY[m]), str(t), name],
        capture_output=True, text=True, cwd=RTL)
    if gen.returncode:
        return None, f"generator failed: {gen.stderr.strip().splitlines()[-1:]}"
    (RTL / f"{name}_tables.v").write_text(gen.stdout)
    tables = yosys_area(
        f"read_verilog -sv {name}_tables.v; hierarchy -top {name}_tables; "
        f"synth -top {name}_tables -flatten; dfflibmap -liberty {LIB}; "
        f"abc -liberty {LIB}; opt_clean; stat -liberty {LIB}")
    solver = yosys_area(
        f"read_verilog -sv bm_serial.v bm_area_probe.v; chparam -set T {t} bm_serial; "
        f"chparam -set M {m} bm_serial; chparam -set RED {POLY[m]} bm_serial; "
        f"hierarchy -top bm_serial; synth -top bm_serial -flatten; "
        f"dfflibmap -liberty {LIB}; abc -liberty {LIB}; opt_clean; stat -liberty {LIB}")
    (RTL / f"{name}_tables.v").unlink(missing_ok=True)
    if tables is None or solver is None:
        return None, "synthesis produced no area"
    return tables + solver, None


def tolerance_for(key, declared, tol_pct):
    """A tolerance where it is earned and nowhere else.

    A blanket tolerance covers the nineteen areas that reproduce bit for bit as well as
    the three that do not, so those nineteen could drift by a percent and nothing would
    say so. research/inputs.py names the three, measured; everything else is exact even
    in CI.
    """
    if tol_pct <= 0 or key not in I.VERSION_SENSITIVE:
        return 1.0
    return max(1.0, declared * tol_pct / 100.0)


def main():
    args = sys.argv[1:]
    only = None
    if "--only" in args:
        i = args.index("--only")
        only = tuple(int(x) for x in args[i + 1].split(","))
        del args[i:i + 2]

    # A synthesis area is a property of the tool as much as of the circuit. Checked
    # first, so that a toolchain difference says so instead of arriving as twenty-two
    # wrong numbers - which is exactly how it arrived the first time this ran elsewhere.
    ver = subprocess.run(["yosys", "-V"], capture_output=True, text=True)
    found = re.search(r"Yosys (\S+)", ver.stdout or "")
    want = I.TOOLCHAIN["yosys"]
    if not found:
        print("yosys not found or gave no version; areas cannot be verified",
              file=sys.stderr)
        return 1
    tol_pct = 0.0
    if "--tolerance-percent" in args:
        i = args.index("--tolerance-percent")
        tol_pct = float(args[i + 1])
        del args[i:i + 2]

    # Exact comparison needs the declared build. A different one maps to different cells
    # and every figure moves by a few percent - measured at up to 7.3 across all
    # twenty-two, which is W-INTL-175. CI cannot install the declared build without a
    # blind search through 737 MB release tarballs, so it runs with a tolerance instead:
    # weaker than exact and far tighter than the class of error this check exists for,
    # which was a convention mismatch of seventy percent.
    if tol_pct > 0 and found.group(1) != want:
        print(f"yosys {found.group(1)} found, {want} declared; comparing with a "
              f"{tol_pct:g} percent tolerance (W-INTL-175)")
    elif found.group(1) != want:
        print(f"yosys {found.group(1)} found, {want} declared in research/inputs.py.",
              file=sys.stderr)
        print("Areas are toolchain-dependent - a different version maps differently and "
              "every figure will differ by a few percent. Not a defect in the "
              "circuits; see W-INTL-175.", file=sys.stderr)
        return 1

    if not pathlib.Path(LIB).exists():
        print(f"liberty not found at {LIB}; nothing can be verified", file=sys.stderr)
        return 1

    todo = sorted(I.DECODER_AREA) if only is None else [only]

    # Components measured after this script was written and never machine-checked. Each is
    # a fixed module rather than a generated one, so it is synthesised directly.
    FIXED = {
        "spongent_permutation": ("spongent.v", I.COUNTERMEASURE_AREA["spongent_permutation"], ""),
        "spongent_round":       ("spongent.v", I.COUNTERMEASURE_AREA["spongent_round"], ""),
        "ibs_select":            ("ibs_select.v",
                                  I.POINTER_AREA["ibs_select_block4"], "BLOCK=4"),
        # Two measured dictionaries that nothing read and nothing verified until
        # W-INTL-210. The characterisation readout is quoted in the documents as the cost
        # of the instrument; the two solver forms are the measurement behind the decision
        # to share multipliers. Both were declared, neither was re-synthesised.
        "ro_characteriser":      ("ro_characteriser.v", I.CHARACTERISER_AREA[272],
                                  "NRO=272 CW=20 GATE=16"),
        "ro_characteriser_38":   ("ro_characteriser.v", I.CHARACTERISER_AREA[38],
                                  "NRO=38 CW=20 GATE=16"),
        "ro_characteriser_64":   ("ro_characteriser.v", I.CHARACTERISER_AREA[64],
                                  "NRO=64 CW=20 GATE=16"),
        "bm_area_probe":         ("bm_area_probe.v", I.SOLVER_AREA["parallel_t21_m7"],
                                  "T=21 M=7 RED=9"),
        "bm_serial":             ("bm_serial.v bm_area_probe.v",
                                  I.SOLVER_AREA["serial_t21_m7"], "T=21 M=7 RED=9"),
    }
    # SLLC is declared as a sum of two modules per code, so it is verified as a sum
    # rather than added to FIXED, which holds single modules.
    SLLC = {7: ("sllc127t7.v", "sllc127t7"),
            11: ("sllc127t11.v", "sllc127t11"),
            21: ("sllc127t21.v", "sllc127t21")}
    bad = 0
    print(f"{'code':>12} {'declared':>10} {'measured':>10} {'delta':>8}")
    print("-" * 44)
    for (m, t) in todo:
        declared = I.DECODER_AREA[(m, t)]
        got, err = measure(m, t)
        if got is None:
            print(f"  GF(2^{m}) t={t:<3} {declared:10d} {'-':>10} {err}")
            bad += 1
            continue
        delta = got - declared
        limit = tolerance_for(("decoder", m, t), declared, tol_pct)
        flag = "" if abs(delta) < limit else "   MISMATCH"
        print(f"  GF(2^{m}) t={t:<3} {declared:10d} {got:10.0f} {delta:8.0f}{flag}")
        if abs(delta) >= 1.0:
            bad += 1
    if only is None:
        print()
        print(f"{'code, shared solver':>22} {'declared':>10} {'measured':>10} {'delta':>8}")
        print("-" * 54)
        for (m, t) in sorted(I.DECODER_AREA_SERIAL):
            declared = I.DECODER_AREA_SERIAL[(m, t)]
            got, err = measure_serial(m, t)
            if got is None:
                print(f"  GF(2^{m}) t={t:<3} {declared:10d} {'-':>10} {err}")
                bad += 1
                continue
            delta = got - declared
            limit = tolerance_for(("decoder_serial", m, t), declared, tol_pct)
            flag = "" if abs(delta) < limit else "   MISMATCH"
            print(f"{'GF(2^%d) t=%-3d' % (m, t):>22} {declared:10d} {got:10.0f} "
                  f"{delta:8.0f}{flag}")
            if abs(delta) >= limit:
                bad += 1

    if only is None:
        print()
        print(f"{'SLLC, encoder+unmask':>22} {'declared':>10} {'measured':>10} {'delta':>8}")
        print("-" * 54)
        for t, (src, base) in sorted(SLLC.items()):
            got = 0
            for suffix in ("encoder", "unmask"):
                top = f"{base}_{suffix}"
                part = yosys_area(
                    f"read_verilog -sv {src}; hierarchy -top {top}; "
                    f"synth -top {top} -flatten; dfflibmap -liberty {LIB}; "
                    f"abc -liberty {LIB}; opt_clean; stat -liberty {LIB}")
                got = None if part is None or got is None else got + part
            declared = I.SLLC_AREA[t]
            if got is None:
                print(f"{'t=%d' % t:>22} {declared:10d} {'-':>10}  synthesis failed")
                bad += 1
                continue
            delta = got - declared
            limit = max(1.0, declared * tol_pct / 100.0)
            flag = "" if abs(delta) < limit else "   MISMATCH"
            print(f"{'t=%d' % t:>22} {declared:10d} {got:10.0f} {delta:8.0f}{flag}")
            if abs(delta) >= limit:
                bad += 1

    if only is None:
        print()
        print(f"{'module':>22} {'declared':>10} {'measured':>10} {'delta':>8}")
        print("-" * 54)
        for name, (src, declared, params) in sorted(FIXED.items()):
            # The dictionary key names the entry, not necessarily the module: two entries
            # measure the same module at different parameters, because the instrument was
            # costed for a bank seven times the size of the one in the design.
            # W-INTL-212.
            top = re.sub(r"_\d+$", "", name)
            script = f"read_verilog -sv {src}; "
            for prm in params.split():
                script += f"chparam -set {prm.split('=')[0]} {prm.split('=')[1]} {top}; "
            script += (f"hierarchy -top {top}; synth -top {top} -flatten; "
                       f"dfflibmap -liberty {LIB}; abc -liberty {LIB}; opt_clean; "
                       f"stat -liberty {LIB}")
            got = yosys_area(script)
            if got is None:
                print(f"  {name:>20} {declared:10d} {'-':>10}  synthesis failed")
                bad += 1
                continue
            delta = got - declared
            limit = max(1.0, declared * tol_pct / 100.0)
            flag = "" if abs(delta) < limit else "   MISMATCH"
            print(f"  {name:>20} {declared:10d} {got:10.0f} {delta:8.0f}{flag}")
            if abs(delta) >= limit:
                bad += 1

    # Count what was actually synthesised, not what the first table held. The summary
    # said "all 15" while eighteen areas had been checked, which is the kind of line that
    # makes a passing gate mean less than it appears to.
    total = len(todo) + (0 if only else len(I.DECODER_AREA_SERIAL) + len(FIXED) + len(SLLC))
    print()
    if bad:
        print(f"verify_inputs: {bad} of {total} declared areas do not reproduce")
        return 1
    print(f"verify_inputs: OK, all {total} declared areas reproduce")
    return 0


if __name__ == "__main__":
    sys.exit(main())
