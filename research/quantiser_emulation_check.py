#!/usr/bin/env python3
"""Separate emulation error from format error in the 8-bit ablation.

Audit entry W-INTL-40 observes that the ablation's arms are not
implementation-symmetric: the reference arm casts to a native 8-bit float type,
while the project's own arm is a hand-rolled emulation carrying two defects.

  1. On saturation the exponent is clamped while the mantissa is computed from
     the unclamped exponent, so the result is neither the input nor the saturated
     representable value.
  2. There are no subnormals: magnitudes below the smallest normal are flushed to
     zero, where the reference format represents them.

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


def gf8_saturation_fixed(w):
    """Defect 1 repaired: saturate to the representable maximum instead of
    reconstructing from a mismatched mantissa."""
    MX, B, EM, MV, ms = 31.0, 3, 7, 2.0 ** (1 - 3 - 4), 16.0
    s = scale_rows(w, MX)
    ws = w / s
    sg = torch.sign(ws)
    a = torch.abs(ws).clamp(min=MV)
    e = torch.floor(torch.log2(a))
    ef = e + B
    in_range = (ef >= 1) & (ef <= EM - 1)
    ff = a / (2.0 ** e)
    normal = sg * (1 + torch.round((ff - 1) * ms) / ms) * (2.0 ** (e))
    max_repr = (1 + (ms - 1) / ms) * (2.0 ** (EM - 1 - B))
    sim = torch.where(in_range, normal, sg * max_repr)
    sim = torch.where(torch.abs(ws) < MV, torch.zeros_like(sim), sim)
    return torch.clamp(sim, -max_repr, max_repr) * s


def gf8_both_fixed(w):
    """Defects 1 and 2 repaired: saturation as above, plus subnormals - values
    below the smallest normal are quantised on the subnormal grid instead of
    being flushed to zero."""
    MX, B, EM, MV, ms = 31.0, 3, 7, 2.0 ** (1 - 3 - 4), 16.0
    s = scale_rows(w, MX)
    ws = w / s
    sg = torch.sign(ws)
    a = torch.abs(ws)
    e = torch.floor(torch.log2(a.clamp(min=1e-30)))
    ef = e + B
    ff = a / (2.0 ** e)
    normal = sg * (1 + torch.round((ff - 1) * ms) / ms) * (2.0 ** e)
    max_repr = (1 + (ms - 1) / ms) * (2.0 ** (EM - 1 - B))
    sub_step = MV / ms
    subnormal = sg * torch.round(a / sub_step) * sub_step
    sim = torch.where(ef < 1, subnormal,
                      torch.where(ef > EM - 1, sg * max_repr, normal))
    return torch.clamp(sim, -max_repr, max_repr) * s


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
        "GF8, saturation fixed": gf8_saturation_fixed,
        "GF8, saturation + subnormals": gf8_both_fixed,
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
