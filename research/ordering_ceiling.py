#!/usr/bin/env python3
"""The entropy the per-bit accounting claims, against the ceiling the ordering allows.

W-INTL-239, and it is a second implementation of the entropy available - by combinatorics
rather than by summing per-bit densities. W-INTL-238 re-derived the post-selection density
from a richer source model and confirmed it. This asks a different question: not whether
the density is right, but whether the total the design multiplies out of it can exist.

R oscillators realise one of R! rankings, so R(R-1)/2 pairwise comparisons carry at most
log2(R!) bits however many of them are read. `decoder_code_choice.md` records that bound
and this project uses it in exactly one place: `oscillator_floor` requires log2(R!) to
exceed the KEY size, 128 bits.

That is the weaker of the two conditions available. The construction does not claim 128
bits from the source; it claims that its carried bits hold enough, and the figure it claims
is k x blocks x the post-selection density. Nothing compares THAT against the ceiling.

  blocks  carried     raw   osc   ceiling   present   ratio
       4      228     935    44     180.8     134.3   1.346
       5      285    1169    49     208.6     167.8   1.243
       6      342    1402    54     237.1     201.4   1.177   <- the recommendation
       7      399    1636    58     260.3     235.0   1.108
       8      456    1870    62     284.0     268.6   1.058
       9      513    2103    66     308.1     302.1   1.020
      10      570    2337    69     326.3     335.7   0.972   <- accounting exceeds the ceiling

Two things follow, and the second is the useful one.

The recommendation is sound, at 1.177 - and that is the tightest margin anywhere in this
design. The borrowed-margin sweep's tightest row is the min-entropy density at 1.30, and
this is not in that sweep at all, because it is not a borrowed input. It is a structural
bound, and structural bounds do not appear in a table of things somebody else measured.

And the design is FOUR BLOCKS from the point where its entropy accounting stops being
sound. The ratio falls with block count because raw positions grow linearly while the
oscillators they need grow as their square root, so the per-bit sum outruns log2(R!). Every
correction in the last six loops has added blocks: the density headroom rule took three to
four, and the min-entropy correction took four to six. Two more corrections of that size
reach ten.

At ten blocks nothing fails loudly. `oscillator_floor` still passes, because 326 bits still
exceeds 128. The construction still decodes. What stops being true is the statement that
the carried bits hold the entropy the model says they hold, and no check in this repository
would notice.

What the bound assumes
----------------------
That only the ordering is used, which is what a comparator-based readout does. It is an
upper bound and stays one: the true entropy is lower, because the frequencies are not a
uniformly random permutation. Using it as a ceiling is therefore conservative in the safe
direction - the real margin is smaller than 1.177, not larger.

Usage: ordering_ceiling.py    prints the table and the crossing point
"""

import math
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import inputs as I
import selection_with_bch as S

LN2 = math.log(2.0)


def ordering_bits(oscillators):
    """log2(R!) - every bit the pairwise comparisons of R oscillators can carry."""
    return math.lgamma(oscillators + 1) / LN2


def at_blocks(blocks, k=57, n=127, keep=None):
    """(raw positions, oscillators, ceiling, entropy claimed present) at this block count."""
    if keep is None:
        keep = 1.0 - I.SELECTION_LOSS
    raw = int(n * blocks / keep + 0.999)
    oscillators = max(S.floor_ent(I.KEY_BITS), S._r(raw))
    present = k * blocks * S.density_at(keep)
    return raw, oscillators, ordering_bits(oscillators), present


def crossing_block_count(k=57, n=127, keep=None, limit=40):
    """Fewest blocks at which the per-bit accounting exceeds the ordering ceiling."""
    for blocks in range(2, limit):
        _, _, ceiling, present = at_blocks(blocks, k, n, keep)
        if present > ceiling:
            return blocks
    return None


if __name__ == "__main__":
    import importlib
    sys.path.insert(0, __file__.rsplit("/", 1)[0].rsplit("/", 1)[0] + "/scripts")
    C = importlib.import_module("check_figures_reproduce")
    rec = C.recommendation()
    recommended_blocks = rec[4]

    print("Entropy the per-bit accounting claims, against what the ordering allows.\n")
    print(f"{'blocks':>7} {'carried':>8} {'raw':>7} {'osc':>5} {'ceiling':>9} "
          f"{'present':>9} {'ratio':>7}")
    for blocks in range(4, 14):
        raw, osc, ceiling, present = at_blocks(blocks)
        mark = ("   <- the recommendation" if blocks == recommended_blocks
                else "   <- accounting exceeds the ceiling" if present > ceiling else "")
        print(f"{blocks:>7} {57 * blocks:>8} {raw:>7} {osc:>5} {ceiling:>9.1f} "
              f"{present:>9.1f} {ceiling / present:>7.3f}{mark}")

    raw, osc, ceiling, present = at_blocks(recommended_blocks)
    crossing = crossing_block_count()
    print(f"\nthe recommendation stands at {ceiling / present:.3f}, which is the tightest")
    print("margin anywhere in this design - the borrowed-margin sweep's tightest row is")
    print("1.30, and this bound is not in that sweep because it is not a borrowed input.")
    print(f"\nthe accounting stops being sound at {crossing} blocks, "
          f"{crossing - recommended_blocks} beyond the recommendation.")
    print("Nothing fails loudly there: oscillator_floor still passes, because it compares")
    print(f"the ceiling against the {I.KEY_BITS}-bit key rather than against what the")
    print("construction claims to have. The design has added blocks in each of the last")
    print("two corrections - three to four, then four to six.")
