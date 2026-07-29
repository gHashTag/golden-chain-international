#!/usr/bin/env python3
"""Separate emulation error from format error in the 8-bit ablation.

Audit entry W-INTL-40 observes that the ablation's arms are not
implementation-symmetric: the reference arm casts to a native 8-bit float type,
while the project's own arm is a hand-rolled emulation carrying two defects.

  1. The per-row scaling target is 31, while the largest value the format can
     represent is 15.5. Every row's extreme values therefore saturate by
     construction, before any quantisation error is considered.
  2. On saturation the exponent is clamped while the mantissa is computed from
     the unclamped exponent, so the result is neither the input nor the saturated
     representable value.
  3. There are no subnormals: magnitudes below the smallest normal are flushed to
     zero. The MV constant in the ablation is exactly the smallest subnormal of
     the format its other constants describe, so the format was designed with
     them and the implementation drops them.

This script measures how much of the reported gap those two defects account for.
It does not re-run training. It quantises the same tensors through four paths and
compares reconstruction error, which is the quantity training amplifies.

Run: python3 research/quantiser_emulation_check.py
"""

import numpy as np
import torch

SEED = 42
ROWS, COLS = 512, 512


def scale_rows(w, fmt_max):
    """Per-row absolute-maximum scaling, identical to the ablation."""
    s = (w.abs().amax(dim=-1, keepdim=True) / fmt_max).clamp(min=1e-12)
    return s


def fp8_native(w):
    """Reference arm, exactly as the ablation runs it."""
    s = scale_rows(w, 448.0)
    return (w / s).to(torch.float8_e4m3fn).to(w.dtype) * s


def gf8_as_written(w):
    """The project's arm, transcribed from the ablation source without change."""
    MX, B, EM, MV, ms = 31.0, 3, 7, 2.0 ** (1 - 3 - 4), 16.0
    s = scale_rows(w, MX)
    ws = w / s
    sg = torch.sign(ws)
    a = torch.abs(ws).clamp(min=MV)
    e = torch.floor(torch.log2(a))
    ff = a / (2.0 ** e)
    ef = torch.clamp(e + B, 1, EM - 1)          # exponent clamped ...
    sim = sg * (1 + torch.round((ff - 1) * ms) / ms) * (2.0 ** (ef - B))
    #        ... while ff came from the unclamped e. That is defect 1.
    sim = torch.where(torch.abs(ws) < MV, torch.zeros_like(sim), sim)  # defect 2
    return torch.clamp(sim, -MX, MX) * s


# Format geometry derived from the constants in the ablation rather than assumed.
# Bias 3, exponent field 1..6 normal, 4 mantissa bits. The largest representable
# value is therefore (1 + 15/16) * 2^3 = 15.5, and the smallest subnormal is
# 2^-2 / 16 = 2^-6 - which is exactly the MV constant the ablation uses, so the
# format was designed with subnormals and the implementation drops them.
GF8_B, GF8_EM, GF8_MS = 3, 7, 16.0
GF8_MAX = (1 + (GF8_MS - 1) / GF8_MS) * 2.0 ** ((GF8_EM - 1) - GF8_B)   # 15.5
GF8_MIN_NORMAL = 2.0 ** (1 - GF8_B)                                     # 0.25
GF8_SUB_STEP = GF8_MIN_NORMAL / GF8_MS                                  # 2^-6


def gf8_scale_fixed(w):
    """Defect 3 repaired only: scale rows to the value the format can actually
    represent, 15.5, instead of 31. Everything else as written."""
    s = scale_rows(w, GF8_MAX)
    ws = w / s
    sg = torch.sign(ws)
    a = torch.abs(ws).clamp(min=GF8_SUB_STEP)
    e = torch.floor(torch.log2(a))
    ff = a / (2.0 ** e)
    ef = torch.clamp(e + GF8_B, 1, GF8_EM - 1)
    sim = sg * (1 + torch.round((ff - 1) * GF8_MS) / GF8_MS) * (2.0 ** (ef - GF8_B))
    sim = torch.where(torch.abs(ws) < GF8_SUB_STEP, torch.zeros_like(sim), sim)
    return torch.clamp(sim, -GF8_MAX, GF8_MAX) * s


def gf8_correct(w):
    """A correct implementation of the format the constants describe: right
    scaling target, saturation to the representable maximum, and subnormals."""
    s = scale_rows(w, GF8_MAX)
    ws = w / s
    sg = torch.sign(ws)
    a = torch.abs(ws)

    e = torch.floor(torch.log2(a.clamp(min=1e-30)))
    ff = a / (2.0 ** e)
    normal = (1 + torch.round((ff - 1) * GF8_MS) / GF8_MS) * (2.0 ** e)
    subnormal = torch.round(a / GF8_SUB_STEP) * GF8_SUB_STEP

    out = torch.where(a < GF8_MIN_NORMAL, subnormal, normal)
    out = torch.where(a > GF8_MAX, torch.full_like(a, GF8_MAX), out)
    return sg * out * s


def error(w, q):
    d = (q - w).float()
    return {
        "rmse": float(torch.sqrt((d ** 2).mean())),
        "max_abs": float(d.abs().max()),
        "zeroed": float((q == 0).float().mean() - (w == 0).float().mean()),
    }


def main():
    torch.manual_seed(SEED)
    cases = {
        "normal(0,1)": torch.randn(ROWS, COLS),
        "normal, heavy tail": torch.randn(ROWS, COLS) * (1 + 3 * torch.rand(ROWS, 1)),
        "trained-like (t-dist)": torch.distributions.StudentT(3.0).sample((ROWS, COLS)),
    }
    paths = {
        "FP8 native (reference arm)": fp8_native,
        "GF8 as written (project arm)": gf8_as_written,
        "GF8, scaling target fixed": gf8_scale_fixed,
        "GF8, correct implementation": gf8_correct,
    }

    print(f"{ROWS}x{COLS} tensors, seed {SEED}, per-row absmax scaling\n")
    for cname, w in cases.items():
        print(f"== {cname} ==")
        base = None
        for pname, fn in paths.items():
            e = error(w, fn(w))
            if "as written" in pname:
                base = e["rmse"]
            share = ""
            if base and "GF8" in pname and "as written" not in pname:
                share = f"   ({100 * (1 - e['rmse'] / base):+.1f}% vs as-written)"
            print(f"  {pname:32s} rmse={e['rmse']:.5f}  "
                  f"maxerr={e['max_abs']:.4f}  extra-zeros={e['zeroed']:.4%}{share}")
        print()


if __name__ == "__main__":
    main()
