#!/usr/bin/env python3
"""The pointer family against the linear one, re-costed at the operating point that exists.

Section 77 costed Index-Based Syndrome coding against SLLC and found it 0.32 of a tile
ahead, then declined it: IBS needs a random codeword to point at, so it needs a random
number source SLLC does not, and the literature records that ring-oscillator sum-PUF
outputs are not fully independent and that IBS helper data can be attacked with machine
learning on exactly that basis.

Two things have changed since, and only one of them is in the comparison's favour.

The design has moved three times - shared multipliers, a re-chosen code, an encoder sized
to its own generator - so the absolute figures in that table describe nothing that
exists. And W-INTL-144 established that global thresholding, the selection scheme paired
with SLLC here, amplifies the bias already present in the source. Delvaux et al. section
VII.D: "IBS and C-IBS do not amplify bias [...] Rather the opposite: they remove all
bias." The entropy axis did not exist when the comparison was made and it runs one way.

The trap this file is written against is using an assumption in both directions. The
measured entropy deficit - 241.0 bits in 256 positions - is attributed entirely to bias
in selection_entropy.py, because that maximises the amplification and is therefore the
pessimistic reading *for thresholding*. Attributing it entirely to bias again here would
make IBS look like it recovers the whole deficit, which is the optimistic reading of the
same unknown. So IBS is reported as a range: the deficit is bias and IBS removes it, or
the deficit is correlation and IBS removes none of it.
"""

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I
import selection_entropy as SE

CODE = (127, 57, 11)          # the recommendation


def _blocks():
    """Blocks the recommendation carries, derived rather than written down.

    BLOCKS was the literal 3 and went stale the moment the density headroom rule added a
    fourth (W-INTL-228). It compared the pointer family against a construction the project
    had stopped recommending, and would have kept doing so silently - the model runs, the
    table prints, and only the tripwire in check_models_run noticed the tile gap had moved
    from 0.16 to 0.19.

    Fifth model in this project found pinned to a superseded operating point. The rule is
    not "check the constants"; it is that a figure the recommendation determines has to be
    computed from the recommendation.
    """
    rho = SE.density_for_bias(
        SE.selected_bias(SE.mean_for_density(SE.working_density()), I.SELECTION_LOSS)[0])
    return -(-int(I.KEY_BITS / rho) // CODE[1])


BLOCKS = _blocks()
IBS_BLOCK = 4                 # positions per output bit, from the measured datapath
IBS_LOGIC = I.POINTER_AREA["ibs_select_block4"]
COUNTERMEASURE = I.COUNTERMEASURE_AREA["spongent_permutation"]


def pairs_for(positions):
    x = 2
    while x * (x - 1) // 2 < positions:
        x += 1
    return x


def oscillator_floor(bits=128):
    from math import lgamma, log
    x = 2
    while lgamma(x + 1) / log(2) < bits:
        x += 1
    return x


def cost(label, decoder, extra, positions, k_required):
    n, k, t = CODE
    osc = max(oscillator_floor(), pairs_for(positions))
    cells = decoder + extra + COUNTERMEASURE + osc * I.OSCILLATOR_AREA
    return {
        "label": label, "positions": positions, "oscillators": osc,
        "extra": extra, "cells": cells, "tiles": I.tiles(cells),
        "k_required": k_required, "k_carried": k * BLOCKS,
    }


if __name__ == "__main__":
    n, k, t = CODE
    decoder = I.decoder_area(7, t)
    selected = n * BLOCKS
    rho_thresholded = SE.density_for_bias(
        SE.selected_bias(SE.mean_for_density(I.MIN_ENTROPY_DENSITY),
                         I.SELECTION_LOSS)[0])

    rows = [
        cost(f"SLLC + thresholding, {1-I.SELECTION_LOSS:.0%} kept",
             decoder, I.SLLC_AREA[t],
             round(selected / (1 - I.SELECTION_LOSS)),
             I.KEY_BITS / rho_thresholded),
        cost(f"IBS, block of {IBS_BLOCK}, deficit is bias",
             decoder, IBS_LOGIC, selected * IBS_BLOCK, I.KEY_BITS / 1.0),
        cost(f"IBS, block of {IBS_BLOCK}, deficit is correlation",
             decoder, IBS_LOGIC, selected * IBS_BLOCK,
             I.KEY_BITS / I.MIN_ENTROPY_DENSITY),
    ]

    print(f"BCH({n},{k},{t}) in {BLOCKS} blocks, {selected} selected bits, "
          f"decoder {decoder}, countermeasure {COUNTERMEASURE}\n")
    print(f"{'construction':>44} {'positions':>10} {'osc':>5} {'extra':>7} "
          f"{'cells':>8} {'tiles':>7} {'k needed':>9} {'carried':>8}")
    for r in rows:
        print(f"{r['label']:>44} {r['positions']:10d} {r['oscillators']:5d} "
              f"{r['extra']:7d} {r['cells']:8.0f} {r['tiles']:7.2f} "
              f"{r['k_required']:9.1f} {r['k_carried']:8d}")

    linear, ibs_lo, ibs_hi = rows
    print(f"\nthe pointer family is {linear['tiles'] - ibs_lo['tiles']:.2f} of a tile "
          f"ahead, and the entropy axis does not change that -")
    print(f"both IBS rows cost the same area; the range is only in what k the key needs,")
    print(f"and the code carries {linear['k_carried']} either way. The saving is the "
          f"masking machinery")
    print(f"({linear['extra']} against {ibs_lo['extra']}) minus the oscillators the "
          f"extra positions need")
    print(f"({ibs_lo['oscillators']} against {linear['oscillators']}).")
    print(f"\nDeclined again, for the reason it was declined before: IBS needs a random")
    print(f"number source, and its helper data is attackable by machine learning on "
          f"exactly")
    print(f"the correlation this source is reported to have. Nothing measured this loop")
    print(f"touches that argument - the entropy finding makes the arithmetic better and")
    print(f"the attack surface is unchanged.")
