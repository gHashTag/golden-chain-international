#!/usr/bin/env python3
"""Every declared decoder area must have a testbench that exercises its code.

This project's rule, stated in measure_all.sh's own header, is that no area is quoted for
a circuit that has not decoded correctly. W-INTL-215 found three declared areas -
GF(2^8) at t=30, t=47 and t=55 - with no end-to-end testbench at all. They were
re-synthesised by the verifier and offered to the search as candidates, so a code the
search could have recommended had never decoded anything.

All three pass; the gap was in the coverage, not the circuits. This makes the invariant a
check rather than a habit: for every key in DECODER_AREA there is an end-to-end entry in
measure_all.sh, for every key in DECODER_AREA_SERIAL a differential entry, and for every
key in SLLC_AREA a masking-stage entry.

Exit code 1 on any declared code without a testbench.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))
import inputs as I                                                    # noqa: E402

SCRIPT = ROOT / "research" / "rtl" / "measure_all.sh"


def main():
    sh = SCRIPT.read_text()
    e2e = {(int(m.group(1)), int(m.group(2)))
           for m in re.finditer(r"-DMVAL=(\d+)\s+-DTVAL=(\d+)", sh)}
    diff = {(int(m.group(2)), int(m.group(1)))
            for m in re.finditer(r"-DTVAL=(\d+)\s+-DMVAL=(\d+)[^\n]*bm_serial", sh)}
    sllc = {int(m.group(1)) for m in re.finditer(r"sllc127t(\d+)\.v", sh)}

    failures = []
    for key in sorted(I.DECODER_AREA):
        if key not in e2e:
            failures.append(f"GF(2^{key[0]}) t={key[1]} has a declared area and no "
                            f"end-to-end testbench")
    for key in sorted(I.DECODER_AREA_SERIAL):
        if key not in diff:
            failures.append(f"GF(2^{key[0]}) t={key[1]} has a declared shared-solver "
                            f"area and no differential testbench")
    for t in sorted(I.SLLC_AREA):
        if t not in sllc:
            failures.append(f"the masking stage for t={t} has a declared area and no "
                            f"testbench")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_testbench_coverage: {len(failures)} declared areas have no "
              f"testbench")
        return 1
    total = len(I.DECODER_AREA) + len(I.DECODER_AREA_SERIAL) + len(I.SLLC_AREA)
    if total == 0:
        print("FAIL: no declared areas found, so this check read nothing")
        return 1
    print(f"check_testbench_coverage: OK ({total} declared codes, each with a testbench)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
