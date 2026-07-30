#!/usr/bin/env python3
"""The aging mitigation, realised in standard cells, and what it would cost.

The design carries an aging-resistant oscillator because a conventional ring-oscillator
bank loses a third of its response bits over ten years and this construction absorbs 9.2
percent. The factor in the budget - 1.857 - is a transistor-width ratio taken from the
custom cell in Rahman et al., and it is the one number in the recommendation with neither
a measurement nor a synthesis behind it. W-INTL-167 also records that it is a ratio of
widths applied to an area.

There is a realisation of the same mechanism in this library that needs no custom cell.

**What the mechanism is.** Their ARO adds two transistors per stage: one to stop
oscillation, and one to hold the inverter input at VDD - VT while idle so the pMOS never
sees a zero. The second is the one that matters - NBTI on a pMOS is driven by a gate at
zero, and an idle conventional ring leaves half its nodes there. Not running it is not
resting it.

**The standard-cell form.** Build the ring out of two-input NANDs with the enable on the
spare input instead of inverters. With the enable high each stage is an inverter and the
ring oscillates. With the enable low **every** output is driven to VDD, so every pMOS gate
in the ring sits at one, which is the recovery condition rather than the stress condition.
That is the same mechanism as their Mc transistor, reaching it through a cell the library
already has.

**And in this library it is free.** sky130_fd_sc_hd__nand2_1 and sky130_fd_sc_hd__inv_1
occupy the same area. Not similar - the same number, read from the liberty below rather
than transcribed.

**What this does not establish.** The 7.73 percent ten-year figure belongs to their
circuit, measured in their simulation. A NAND ring shares the mechanism and has no
published flip rate. So this file does not change the budget: the conservative 1.857 stays
until someone puts a number on this arrangement. What it records is that the mitigation is
probably free rather than costing 0.08 of a tile, and exactly what would have to be shown.
"""

import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I

LIBERTY = "/tmp/sky130.lib"
CELLS = ("sky130_fd_sc_hd__inv_1", "sky130_fd_sc_hd__nand2_1",
         "sky130_fd_sc_hd__einvn_1")


def cell_areas(path=LIBERTY):
    """Areas straight from the liberty, so the comparison is executed and not quoted."""
    try:
        text = open(path, errors="ignore").read()
    except OSError:
        return None
    out = {}
    for m in re.finditer(r'cell \("([^"]+)"\)\s*\{', text):
        if m.group(1) not in CELLS:
            continue
        seg = text[m.end():m.end() + 3000]
        a = re.search(r"\barea\s*:\s*([0-9.]+)\s*;", seg)
        if a:
            out[m.group(1)] = float(a.group(1))
    return out


def budget(factor):
    osc = 35 * I.INVERTERS_PER_OSCILLATOR * I.INVERTER_AREA * factor
    cells = (I.decoder_area(7, 11) + I.SLLC_AREA[11]
             + I.COUNTERMEASURE_AREA["spongent_permutation"] + osc)
    return osc, cells, I.tiles(cells)


if __name__ == "__main__":
    areas = cell_areas()
    if areas is None or len(areas) < 2:
        print(f"liberty not found at {LIBERTY}; nothing measured, nothing claimed")
        sys.exit(0)

    inv = areas["sky130_fd_sc_hd__inv_1"]
    nand = areas["sky130_fd_sc_hd__nand2_1"]
    einvn = areas.get("sky130_fd_sc_hd__einvn_1")

    print("1. the cells, read from the liberty")
    for name in CELLS:
        if name in areas:
            print(f"   {name:32s} {areas[name]:8.4f} um^2")
    print(f"   the borrowed inverter figure this project uses is "
          f"{I.INVERTER_AREA:.4f}, within "
          f"{abs(I.INVERTER_AREA - inv) / inv:.2%} of the library's own")

    print("\n2. a NAND ring costs what an inverter ring costs")
    print(f"   nand2_1 / inv_1 = {nand / inv:.4f}")
    print(f"   the tristate inverter, for contrast, is {einvn / inv:.3f} - it stops the")
    print(f"   oscillation but leaves the node floating, which is not the mechanism")

    print("\n3. what each arrangement would put in the budget")
    print(f"   {'arrangement':>34} {'factor':>7} {'oscillators':>12} {'cells':>8} "
          f"{'tiles':>7}")
    for label, factor in (("conventional inverter ring", 1.0),
                          ("NAND ring, same library cell", nand / inv),
                          ("their ARO, by transistor width", I.AGING_RESISTANT_FACTOR)):
        osc, cells, tiles = budget(factor)
        print(f"   {label:>34} {factor:7.3f} {osc:12.0f} {cells:8.0f} {tiles:7.2f}")

    print("\n4. the budget does not move")
    print("   The 7.73 percent ten-year figure is theirs, for their cell, in their")
    print("   simulation. A NAND ring shares the mechanism and has no published flip")
    print("   rate, so adopting it would trade a measured number for an argued one. The")
    print("   conservative factor stays in the budget.")
    print("   What would settle it: a ten-year flip rate for a NAND-gated ring held high")
    print("   while idle - simulated or measured - at which point the mitigation costs")
    print(f"   nothing instead of {budget(I.AGING_RESISTANT_FACTOR)[2] - budget(1.0)[2]:.2f}"
          f" of a tile.")
