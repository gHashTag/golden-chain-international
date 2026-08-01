#!/usr/bin/env python3
"""Every model in research/ must still run.

W-INTL-202: code_choice_model.py had not run since the decoder areas were re-keyed from
strings to (field bits, correction strength) tuples. Its construction table kept the old
strings, so it raised a KeyError on the first row - and nothing noticed for the whole
interval, because no check ran the models.

The checks in this repository verify that documents agree with the model and that
declared inputs are read. None of them executed the files that do the reasoning. That is
the same shape as the reproduction script that had only ever run on one machine: an
artefact nobody executes rots quietly, and the rot is invisible from every green run.

This runs each one and fails on a non-zero exit. It does not check the output - a model
whose numbers are wrong is a different problem, and one the figure checks already cover
for the numbers that reach a document. This covers the cheaper failure: the file no longer
runs at all.

Exit code 1 if any model fails. Intended to run in CI.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS = ROOT / "research"


# Models excluded, with the reason, because an exclusion nobody can see is a gap nobody
# knows about. quantiser_emulation_check.py needs torch: hundreds of megabytes on every
# CI run for one peripheral model that is not part of the identity-root recommendation.
# It is therefore unchecked here, which is a known gap rather than an unnoticed one, and
# the name is printed on every run so it stays known.
HEAVY = {"quantiser_emulation_check.py": "needs torch, which CI does not install"}

# Models that run and pin no figure, each with the reason. W-INTL-244: this file used to
# hold only the list of models that DO pin one, so a model producing nothing checkable was
# indistinguishable from a model nobody had got to. Four were in that state, and two of
# them were the end-to-end chain and the SLLC generator - the two-witness argument this
# project cites as evidence, corroborated by nothing.
#
# The rule from W-INTL-234 was that a limit on how many figures to pin is a decision about
# which go unpinned. This is that decision, written down.
UNPINNED = {
    "bch_code_search.py":
        "enumerates every BCH code over two fields; its output is a search space rather "
        "than a figure, and the code it selects is pinned through selection_with_bch",
    "code_choice_model.py":
        "a construction table superseded by selection_with_bch, kept for the record of "
        "what was compared - W-INTL-202 is it having stopped running unnoticed",
}


# One figure per model, recomputed from research/inputs.py and matched against what the
# model prints. W-INTL-203: running a model proves it does not raise, which is the
# cheapest failure and not the interesting one. A model can run perfectly and print a
# number that stopped being true three loops ago - which is exactly what burn_in.py did
# with its absorbable flip rate, and nothing here would have said so.
#
# Deliberately one figure each. This is not a test suite; it is a tripwire on the number
# each model exists to produce.
def _free_temperature(percent=True):
    """Largest temperature term the recommendation carries without changing."""
    import importlib, math
    I = importlib.import_module("inputs")
    R = importlib.import_module("reliable_bit_selection")
    S = importlib.import_module("selection_with_bch")
    keep = 1.0 - I.SELECTION_LOSS
    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    age = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)

    def code_at(flip):
        drift = math.sqrt(age * age + R.sigma_for_raw_ber(max(flip, 1e-6)) ** 2)
        eff = R.aged_selected_ber(noise, drift, keep, I.ENROLMENT_READS)
        best = S.best_at(keep, eff, S.need_k_at(keep))
        return best[1:5] if best else None

    at_zero, lo, hi = code_at(0.0), 0.0, 0.5
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if code_at(mid) == at_zero else (lo, mid)
    return lo * 100 if percent else lo


def _worst_corner_cost(): 
    """Extra tiles at the worst chip with the two drifts fully correlated. W-INTL-236."""
    import importlib, math
    I = importlib.import_module("inputs")
    R = importlib.import_module("reliable_bit_selection")
    S = importlib.import_module("selection_with_bch")
    AM = importlib.import_module("aging_margin")
    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    age = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    tol = AM.tolerated_ber()

    def cheapest(drift):
        best = None
        for keep in (1.0 - I.SELECTION_LOSS, 0.40, 0.326, 0.20, 0.10):
            eff = R.aged_selected_ber(noise, drift, keep, I.ENROLMENT_READS)
            if eff > tol:
                continue
            found = S.best_at(keep, eff, S.need_k_at(keep))
            if found is None:
                continue
            _, n, k, t, blocks, _, raw = found
            osc = max(S.floor_ent(I.KEY_BITS), S._r(raw))
            tiles = I.tiles(I.decoder_area(7, t) + I.SLLC_AREA[t]
                            + osc * I.OSCILLATOR_AREA
                            + I.COUNTERMEASURE_AREA["spongent_permutation"])
            best = tiles if best is None or tiles < best else best
        return best

    temp = R.sigma_for_raw_ber(I.TEMPERATURE_FLIP_WORST)
    return cheapest(age + temp) - cheapest(age)


def _tiles_at_worst():
    """Tiles the budget needs at the worst-chip temperature term. W-INTL-235."""
    import importlib, math
    I = importlib.import_module("inputs")
    R = importlib.import_module("reliable_bit_selection")
    S = importlib.import_module("selection_with_bch")
    keep = 1.0 - I.SELECTION_LOSS
    drift = math.sqrt(R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT) ** 2
                      + R.sigma_for_raw_ber(I.TEMPERATURE_FLIP_WORST) ** 2)
    eff = R.aged_selected_ber(R.sigma_for_raw_ber(I.RAW_NOISE_BER), drift, keep,
                              I.ENROLMENT_READS)
    best = S.best_at(keep, eff, S.need_k_at(keep))
    _, n, k, t, blocks, _, raw = best
    osc = max(S.floor_ent(I.KEY_BITS), S._r(raw))
    return I.tiles(I.decoder_area(7, t) + I.SLLC_AREA[t] + osc * I.OSCILLATOR_AREA
                   + I.COUNTERMEASURE_AREA["spongent_permutation"])


def _word_failure_at(ber):
    """Word failure of the recommendation at this raw bit error rate. W-INTL-244."""
    import importlib
    C = importlib.import_module("check_figures_reproduce")
    _, n, _, t, blocks, _, _, _ = C.recommendation()
    return C.word_failure(n, t, blocks, ber)


def _burn_in_half():
    """The selected error rate with half the ten-year drift applied before enrolment."""
    import importlib
    I = importlib.import_module("inputs")
    R = importlib.import_module("reliable_bit_selection")
    # The rescaling written out here rather than obtained by calling the function under
    # test. The first version called aged_selected_ber_with_burn_in, so a control that
    # broke that function moved both sides together and the tripwire stayed green - the
    # same defect as the min-entropy tripwire in W-INTL-224, in the loop that cites it.
    import math
    sig_n = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    sig_a = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    scale = math.sqrt(1.0 + sig_a * sig_a * 0.5)
    return R.aged_selected_ber(sig_n / scale, sig_a * math.sqrt(0.5) / scale,
                               1.0 - I.SELECTION_LOSS, I.ENROLMENT_READS)


def _pointer_oscillators():
    """Oscillators the pointer family needs at the current recommendation. W-INTL-228.

    Was the literal 56, which was its count under the three-block construction. A
    tripwire holding a figure that the recommendation determines goes stale exactly when
    the thing it guards does.
    """
    import importlib
    P = importlib.import_module("pointer_vs_linear")
    return P.pairs_for(P.CODE[0] * P.BLOCKS * P.IBS_BLOCK)


def _k_total(I):
    """Bits of k the recommendation carries, recomputed here on an independent path."""
    import importlib
    SE = importlib.import_module("selection_entropy")
    rho = SE.density_for_bias(
        SE.selected_bias(SE.mean_for_density(SE.working_density()), I.SELECTION_LOSS)[0])
    return -(-int(I.KEY_BITS / rho) // 57) * 57


def _density_floor(I, R):
    """The declared min-entropy density below which the key stops fitting the code.

    Independent of research/borrowed_margins.py on purpose: it is the figure that model
    exists to print, and a tripwire that imports its subject checks nothing.
    """
    import importlib
    SE = importlib.import_module("selection_entropy")
    keep = 1.0 - I.SELECTION_LOSS
    lo, hi = 0.5, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        after = SE.density_for_bias(SE.selected_bias(SE.mean_for_density(mid), 1 - keep)[0])
        if I.KEY_BITS / after <= _k_total(I):
            hi = mid
        else:
            lo = mid
    return hi


def _expected():
    import importlib, math, sys as _sys
    _sys.path.insert(0, str(MODELS))
    I = importlib.import_module("inputs")
    R = importlib.import_module("reliable_bit_selection")
    _sys.path.insert(0, str(ROOT / "scripts"))
    C = importlib.import_module("check_figures_reproduce")

    absorbable = C.absorbable_flip() * 100
    return {
        "aging_margin.py": (
            r"survives an unselected ten-year flip rate up to ([\d.]+)%", absorbable, 0.06),
        "burn_in.py": [
            (r"sigma at ([\d.]+)% \(what the construction absorbs\)", absorbable, 0.06),
            # The widening arm at half the drift before enrolment - W-INTL-234. Bound
            # because the row it checks was unbound for as long as it took to notice.
            (r"\n\s+50%\s+[\d.]+\s+([\d.]+)\s", _burn_in_half(), 5e-6),
        ],
        # Recomputed here through selection_entropy rather than imported from the model,
        # so the tripwire is an independent path. The first version of this entry copied
        # the model's own floor - KEY_BITS/k with no selection term - and so agreed with
        # a figure that was wrong by 0.13.
        "borrowed_margins.py": (
            r"tightest: min-entropy density at ([\d.]+) times",
            I.MIN_ENTROPY_DENSITY / _density_floor(I, R), 0.02),
        "min_entropy_from_shannon.py": (
            r"min-entropy, same fitted model\s+[\d.]+\s+([\d.]+)",
            I.MIN_ENTROPY_DENSITY, 0.0005),
        # W-INTL-235. The free-headroom figure, recomputed here rather than obtained from
        # the model, because a tripwire calling its own subject is what W-INTL-234 caught.
        "environmental_margin.py": [
            (r"absorbs a temperature term up to ([\d.]+)% without", _free_temperature(), 0.2),
            # And the worst-chip row, because the free-headroom figure does not depend on
            # TEMPERATURE_FLIP_WORST at all - a control on that input left the check green,
            # which is the unbound-table gap of W-INTL-234 in the loop that recorded it.
            (r"\n\s+11\.00%\s+[\d.]+\s+no\s+\S+ x \d+\s+\d+\s+([\d.]+)",
             _tiles_at_worst(), 0.02),
        ],
        # W-INTL-236. The worst corner with the fraction free, recomputed here on an
        # independent path rather than by calling budget_audit.
        "budget_audit.py": (
            r"the worst corner costs ([\d.]+) of a tile", _worst_corner_cost(), 0.01),
        # W-INTL-237. Two figures: the two-condition rate the lever is worth, and the
        # agreement between this Monte Carlo and the closed-form model at the case they
        # share - which is the only model-against-model cross-check in this project and
        # would be worth nothing unbound.
        "multi_condition_enrolment.py": [
            (r"and two give ([\d.]+), a factor", 0.00636, 5e-5),
            (r"apart by ([\d.]+) standard errors", 1.1, 0.6),
        ],
        # W-INTL-238. The two-level density and the gap to the single-bias derivation.
        # The gap is the figure that matters: it is the claim that the derivation
        # sixty-eight documents rest on is sound, and it is worth nothing unbound.
        "entropy_second_opinion.py": [
            (r"two levels \(this file\)\s+([\d.]+)", 0.5917, 0.0005),
            (r"difference \+([\d.]+) per bit", 0.0028, 0.0005),
        ],
        # W-INTL-239. The recommendation's margin against the ordering ceiling and the
        # block count where the accounting stops being sound - the second is what the
        # file exists to say, and it would be unbound without an entry of its own.
        "ordering_ceiling.py": [
            (r"the recommendation stands at ([\d.]+), which", 1.177, 0.002),
            (r"accounting stops being sound at (\d+) blocks", 10, 0),
        ],
        # W-INTL-240. Both extrapolations, because they straddle the claim and the whole
        # content of that file is that they disagree. Kept bound after W-INTL-241 settled
        # the question exactly: the Monte Carlo is superseded and its figures still have
        # to be the figures it produced, or the record of why it was superseded rots.
        "ordering_achievable.py": [
            (r"carried at constant ratio\s+([\d.]+)", 199.8, 1.0),
            (r"carried at constant deficit\s+([\d.]+)", 217.7, 1.0),
        ],
        # W-INTL-241. The exact figure and the crossing, which is the number that moved -
        # four blocks against the ceiling, two against what the ordering achieves.
        "ordering_exact.py": [
            (r"stops being sound at (\d+) blocks", 8, 0),
            (r"so the margin runs [\d.]+ to (\d+\.\d+)\.", 1.069, 0.003),
        ],
        # W-INTL-244. The two-witness argument: the chain's own Monte Carlo against the
        # binomial model it is supposed to corroborate. Both figures at the same operating
        # point, and the model column recomputed here from the recommendation rather than
        # read from the model that prints it.
        "key_generator_e2e.py": [
            (r"\n\s+0\.06\s+\d+\s+([\d.]+)\s", 0.403, 0.02),
            (r"\n\s+0\.06\s+\d+\s+[\d.]+\s+([\d.]+)", _word_failure_at(0.06), 0.002),
        ],
        "sllc_key_generator.py": (
            r"\n\s+0\.04\s+\d+\s+\d+/\d+\s+([\d.e-]+)", _word_failure_at(0.04), 0.002),
        "nand_ring.py": (
            r"nand2_1 / inv_1 = ([\d.]+)", 1.0, 0.001),
        "selection_with_bch.py": (
            r"best: BCH\(127,(\d+),\d+\)", float(C.recommendation()[2]), 0.5),
        "selection_entropy.py": (
            r"measured density ([\d.]+) bits per position", I.MIN_ENTROPY_DENSITY, 0.0005),
        "reliable_bit_selection.py": (
            r"noise sigma [\d.]+ gives raw ber ([\d.]+)", 0.15, 0.001),
        "pointer_vs_linear.py": (
            r"pointer family is ([\d.]+) of a tile ahead",
            C.recommendation()[0] - I.tiles(
                I.decoder_area(7, 11) + I.POINTER_AREA["ibs_select_block4"]
                + I.COUNTERMEASURE_AREA["spongent_permutation"]
                + _pointer_oscillators() * I.OSCILLATOR_AREA), 0.02),
    }


def main():
    # --only <name> runs a single model. Each control re-ran all twelve, four minutes
    # each, and three controls took the job to eighteen minutes - W-INTL-211.
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    # Discovery, not enumeration - W-INTL-243 is this check's sibling learning the same
    # lesson one loop earlier. Every model with a main block must pin a figure or be
    # listed in UNPINNED with the reason.
    with_main = {p.name for p in MODELS.glob("*.py")
                 if not p.name.startswith("_") and "__main__" in p.read_text()}
    unlisted = sorted(with_main - set(_expected()) - set(UNPINNED) - set(HEAVY))
    stale_unpinned = sorted(set(UNPINNED) - with_main)

    files = sorted(p for p in MODELS.glob("*.py")
                   if not p.name.startswith("_") and p.name not in HEAVY
                   and (only is None or p.name == only))
    if not files:
        print("FAIL: no models found, so this check read nothing", file=sys.stderr)
        return 1

    import re

    expected = _expected()
    failures = []
    checked = 0
    for path in files:
        result = subprocess.run([sys.executable, str(path)],
                                capture_output=True, text=True, cwd=ROOT)
        if result.returncode != 0:
            last = (result.stderr or result.stdout).strip().splitlines()[-1:]
            failures.append(f"{path.name}: {last[0] if last else 'non-zero exit'}")
            continue
        if path.name not in expected:
            continue
        # One entry may carry several figures. It was one apiece - "deliberately one
        # figure each; this is not a test suite" - and that held while each model printed
        # one thing worth pinning. W-INTL-234 added a burn-in table to burn_in.py whose
        # rows no check could see, because the slot for that file was already taken by
        # the absorbable flip rate. A tripwire per model is a rule about how many, and the
        # figure that matters is not always the first one written.
        entries = expected[path.name]
        if isinstance(entries, tuple) and entries and isinstance(entries[0], str):
            entries = [entries]
        for pattern, want, tol in entries:
            m = re.search(pattern, result.stdout)
            if not m:
                failures.append(f"{path.name}: prints no figure matching {pattern!r}")
                continue
            checked += 1
            got = float(m.group(1))
            if abs(got - want) > tol:
                failures.append(
                    f"{path.name}: prints {got:g} where inputs give {want:.4g} "
                    f"(tolerance {tol})")

    for name in unlisted:
        failures.append(f"{name} runs and pins no figure, and UNPINNED does not say why")
    for name in stale_unpinned:
        failures.append(f"UNPINNED names {name}, which research/ no longer defines")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_models_run: {len(failures)} of {len(files)} models do not run")
        return 1
    want = len(expected) if only is None else (1 if only in expected else 0)
    if checked < want:
        print(f"FAIL: {checked} of {len(expected)} declared model figures were checked")
        return 1
    skipped = ", ".join(f"{n} ({why})" for n, why in sorted(HEAVY.items()))
    if only is None:
        for name, why in sorted(UNPINNED.items()):
            print(f"  runs and pins nothing: {name} - {why}")
    print(f"check_models_run: OK ({len(files)} models run, {checked} figures verified"
          + (f"; not run: {skipped})" if skipped else ")"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
