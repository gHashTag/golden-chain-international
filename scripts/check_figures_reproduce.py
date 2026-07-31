#!/usr/bin/env python3
"""The load-bearing figures in the documents must be reproducible by running the model.

Written after W-INTL-99, where a utilisation factor was measured, recorded and applied in
one document and then absent from every figure computed in the next. Nothing was
overwritten and no step was wrong; the value simply did not make the journey between
files, and eighteen loops of tile counts were optimistic by 1.7 as a result.

The existing checks compare documents against each other. This one compares a document
against a computation, which is the only thing that would have caught it: the prose said
4.92 tiles, the script computed 4.92 tiles, and both were wrong together because they
shared the same missing step.

So this recomputes each headline from its definition - cell area, oscillator floor,
utilisation, tile size - and fails if a document disagrees. Anything added here must be
recomputed from inputs, not read from another file.

Exit code 1 on any mismatch. Intended to run in CI.
"""

import pathlib
import re
import sys
from math import comb, lgamma

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "research"))
import inputs as I

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "paper" / "evidence_ledger.md"
REGISTER = ROOT / "research" / "constraint_register.md"

# ── inputs ──────────────────────────────────────────────────────────────────
# Imported rather than redeclared. Every one of these used to be written out here as
# well as in two other scripts, which is the arrangement W-INTL-99 came out of: a
# quantity living in several files is a quantity that will eventually disagree with
# itself. research/inputs.py carries each with the measurement it came from.
TILE = I.TILE_AREA
TILE_LIMIT = I.TILE_LIMIT
UTILISATION = I.UTILISATION
OSC = I.OSCILLATOR_AREA
INVERTERS = I.INVERTERS_PER_OSCILLATOR
import selection_entropy as _SE
# Two names, because they are two quantities and the last three corrections in this
# project were all one quantity wearing another's name. RHO is what the source paper
# measured; RHO_SIZED is that figure derated by DENSITY_HEADROOM, and only the sizing
# path uses it. A document stating the measurement is checked against RHO, and the
# vestigial utilisation guard keeps RHO because it is about area, not margin.
RHO = I.MIN_ENTROPY_DENSITY
RHO_SIZED = _SE.working_density()   # W-INTL-228
SE_SIZED_DENSITY = _SE.density_for_bias(
    _SE.selected_bias(_SE.mean_for_density(RHO_SIZED), I.SELECTION_LOSS)[0])
KEY_BITS = I.KEY_BITS
DECODER = I.DECODER_AREA
LN2 = 0.6931471805599453

failures = []


def bch_parameters(m):
    n = (1 << m) - 1
    coset = {}
    for i in range(1, n):
        if i in coset:
            continue
        c, x = set(), i
        while x not in c:
            c.add(x)
            x = (2 * x) % n
        for e in c:
            coset[e] = frozenset(c)
    seen, best = set(), {}
    for d in range(1, n):
        if d in coset:
            seen |= coset[d]
        if d % 2 == 0:
            t, k = d // 2, n - len(seen)
            if k > 0 and (k not in best or t > best[k]):
                best[k] = t
    return sorted((t, k) for k, t in best.items())


def word_failure(n, t, blocks, p):
    per = sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(t + 1, n + 1))
    return 1 - (1 - per) ** blocks


def oscillator_floor(leakage):
    x = 2
    while lgamma(x + 1) / LN2 < leakage + KEY_BITS:
        x += 1
    return x


def cheapest(rho, ber, raw_budget=3000):
    """Cheapest measured code meeting both constraints, in tiles of die area."""
    best = None
    for m in (7, 8, 9):
        n = (1 << m) - 1
        blocks = raw_budget // n
        for t, k in bch_parameters(m):
            if (m, t) not in DECODER:
                continue
            if blocks * (k - n * (1 - rho)) < KEY_BITS:      # leakage
                continue
            if word_failure(n, t, blocks, ber) > I.TARGET_FAILURE:  # error target
                continue
            leakage = n * blocks - k * blocks
            cells = DECODER[(m, t)] + oscillator_floor(leakage) * OSC
            tiles = cells / UTILISATION / TILE                # die, not cell, area
            if tiles > TILE_LIMIT:
                continue
            if best is None or tiles < best[0]:
                best = (tiles, n, k, t)
    return best


def check(text, name, label, pattern, expected, tol, required=True):
    """Compare a figure stated in prose against one recomputed from inputs.

    `required` distinguishes the document that must state the figure from ones that
    merely may. The first version guarded on whether a phrase appeared anywhere in the
    text, which fired on a paragraph *about* the check that quoted the phrase without a
    number - a check whose guard is looser than its pattern reports failures for prose
    rather than for arithmetic.
    """
    m = re.search(pattern, text)
    if not m:
        if required:
            failures.append(f"{name}: no figure found for {label} (pattern {pattern!r})")
        return
    got = float(m.group(1))
    if abs(got - expected) > tol:
        failures.append(
            f"{name}: {label} says {got:g}, recomputing from inputs gives "
            f"{expected:.2f} (tolerance {tol})"
        )


def rho_floor(n, k, blocks):
    """Lowest min-entropy density at which this construction still yields a key."""
    return 1 - (k - KEY_BITS / blocks) / n


def max_ber(n, t, blocks):
    lo, hi = 0.0, 0.5
    for _ in range(50):
        mid = (lo + hi) / 2
        if word_failure(n, t, blocks, mid) <= I.TARGET_FAILURE:
            lo = mid
        else:
            hi = mid
    return lo


def recommendation():
    """The construction this project actually recommends, recomputed from inputs.

    W-INTL-147: the headline used to come from cheapest(RHO, 0.04) - no SLLC, no
    selection, a three-thousand-bit raw budget - which is the design as it stood eight
    loops ago. The ledger stated 8.49 tiles and this file recomputed 8.49 tiles, and
    they agreed because both were anchored to the same superseded operating point. A
    check that pins a document to a stale model is worse than no check: it reports green
    while the document is wrong.

    This recomputes what the recommendation is: reliable-bit selection at the design's
    fraction, the post-selection density, SLLC sized to the code's own generator degree,
    the manipulation countermeasure, and the shared-multiplier solver.
    """
    import reliable_bit_selection as R
    import selection_entropy as SE

    fraction = 1.0 - I.SELECTION_LOSS
    # Sized against the derated density, reported at the measured one. The construction
    # has to survive the borrowed figure being wrong (W-INTL-228); the number a document
    # states as "the post-selection density" is what the measurement predicts, and that is
    # 0.9113 whatever margin the sizing carries.
    need_k = KEY_BITS / SE.density_for_bias(
        SE.selected_bias(SE.mean_for_density(RHO_SIZED), I.SELECTION_LOSS)[0])
    rho_sel = SE.density_for_bias(
        SE.selected_bias(SE.mean_for_density(RHO), I.SELECTION_LOSS)[0])
    sigma = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    # The achievable rate, not the bound - see W-INTL-191. Deterministic, so the check
    # does not move between runs.
    eff = R.selected_ber_counts_exact(sigma, fraction, I.ENROLMENT_READS)

    candidates = []
    for m in (7, 8):
        n = (1 << m) - 1
        for t, k in bch_parameters(m):
            area = I.decoder_area(m, t)
            if area is None:
                continue
            blocks = -(-int(need_k) // k)
            if word_failure(n, t, blocks, eff) > I.TARGET_FAILURE:
                continue
            if k * blocks < need_k:
                continue

            selected = n * blocks
            raw = int(-(-selected // fraction) + 1e-9)   # ceil, without the
            # truncation that made this 478 where the design says 477
            osc = max(oscillator_floor(0), pairs_for(raw))
            if t not in I.SLLC_AREA:
                # The masking encoder's degree is n-k, so its area is a property of the
                # code. Substituting the largest measured one - which this line used to
                # do - lets the search recommend a construction whose masking stage has
                # never been measured. A recommendation has to be measured end to end.
                continue
            cells = (area + I.SLLC_AREA[t]
                     + I.COUNTERMEASURE_AREA["spongent_permutation"] + osc * OSC)
            tiles = cells / UTILISATION / TILE
            candidates.append((tiles, n, k, t, blocks, raw, osc, rho_sel))

    # The aging-headroom rule is applied after sorting rather than inside the loop. It
    # costs a bisection over a numerical integral per candidate, and evaluating it for
    # every code in two fields took this check from twelve seconds to eighty-six. Sorted
    # by area and walked in order, it is evaluated for one or two.
    for cand in sorted(candidates):
        # One implementation, in research/aging_margin.py, imported here. It lived only
        # in this file, which is why the search model did not have the rule at all and
        # went on recommending the code the rule excludes - W-INTL-205.
        import aging_margin as AM
        if AM.meets_aging_headroom(cand[3], cand[2], cand[4]):
            return cand
    return None


def pairs_for(positions):
    """Oscillators needed to yield this many distinct pairs."""
    x = 2
    while x * (x - 1) // 2 < positions:
        x += 1
    return x


def check_selection_entropy():
    """The leakage bound must be checked against the density of the SELECTED bits.

    RHO is measured on unselected positions and the design discards a fifth of them.
    Selection keeps the positions furthest from the decision boundary, which are the
    positions most committed to a value, so the survivors are more biased than the
    population - Delvaux et al. name global thresholding as the scheme that amplifies
    bias the most, and this project's own source model reproduces it.

    The check is here rather than in a document because it is what would have caught
    the previous design: BCH(127,29,21) in five blocks carried 145 bits of k, and at
    the deeper selection fractions the analysis was quoting, 145 is not enough.

    All three ways it can fail were exercised before it was committed: no amplification
    (W-INTL-144), a document figure that disagrees, and a k that does not cover the
    requirement, which reproduces the previous design's failure.
    """
    import selection_entropy as SE

    mu = SE.mean_for_density(RHO)
    bias, _ = SE.selected_bias(mu, I.SELECTION_LOSS)
    rho_selected = SE.density_for_bias(bias)
    if rho_selected >= RHO:
        failures.append(
            "selection entropy: selection is computing no bias amplification, which "
            "means the source model has lost its offset - see W-INTL-144"
        )
        return None
    k_total = 57 * 3                      # the recommendation, BCH(127,57,11) x 3
    required = KEY_BITS / rho_selected
    if k_total < required:
        failures.append(
            f"selection entropy: the recommendation carries {k_total} bits of k and "
            f"needs {required:.1f} at the post-selection density {rho_selected:.4f}"
        )
    doc = ROOT / "research" / "decoder_code_choice.md"
    if doc.exists():
        check(doc.read_text(), "decoder_code_choice.md",
              "min-entropy density after selection",
              r"density after selection is ([0-9]\.[0-9]+)", rho_selected, 0.002)

    # Every model that reports this density must report the same one. The search table
    # used to display it by inverting a ceiled integer - KEY / need_k - which gave 0.9275
    # where the density is 0.9293, so two files reported two densities for one operating
    # point and neither was wrong on its own terms. Cross-checked here rather than
    # trusted, because the fix (one definition, imported) can be undone by anyone who
    # finds it convenient to recompute locally.
    import selection_with_bch as SW
    other = SW.density_at(1.0 - I.SELECTION_LOSS)
    if abs(other - rho_selected) > 1e-9:
        failures.append(
            f"selection entropy: selection_with_bch reports a post-selection density of "
            f"{other:.6f} where selection_entropy gives {rho_selected:.6f}")
    return rho_selected


def tolerated_ber():
    """The bit error rate the recommendation's code survives at the declared target.

    Written as the literal 0.0442 in three places until W-INTL-193. It is not an input:
    it is what BCH(127,57,11) in three blocks tolerates at a word failure of one in a
    million, so it moves when the code moves or when the target moves, and a literal does
    not.
    """
    rec = recommendation()
    if rec is None:
        return 0.0
    _, n, k, t, blocks, _, _, _ = rec
    return max_ber(n, t, blocks)


def aged_margin():
    """How much room the construction has at ten years on an aging-resistant bank."""
    import reliable_bit_selection as R
    from math import sqrt
    keep = 1.0 - I.SELECTION_LOSS
    sig = sqrt(R.sigma_for_raw_ber(I.RAW_NOISE_BER) ** 2 + R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT) ** 2)
    return tolerated_ber() / R.selected_ber_counts_exact(sig, keep, I.ENROLMENT_READS)


def absorbable_flip():
    """The unselected ten-year flip rate the construction still survives."""
    import reliable_bit_selection as R
    from math import sqrt
    keep = 1.0 - I.SELECTION_LOSS
    base = R.sigma_for_raw_ber(I.RAW_NOISE_BER) ** 2
    lo, hi = 0.0, 0.99
    for _ in range(60):
        mid = (lo + hi) / 2
        sig = sqrt(base + R.sigma_for_raw_ber(max(mid, 1e-6)) ** 2)
        if R.selected_ber_counts_exact(sig, keep, I.ENROLMENT_READS) <= tolerated_ber():
            lo = mid
        else:
            hi = mid
    return lo


_ABSORB_CACHE = {}


def absorbable_flip_for(t, k, blocks):
    """The unselected ten-year flip rate a candidate construction still survives.

    Memoised and coarse on purpose. It is a filter inside a search over every code in two
    fields, so calling it uncached with a forty-step bisection over a four-thousand-point
    integral turned a twelve-second check into one that does not finish - which is the
    W-INTL-195 lesson arriving inside a single script rather than across two CI jobs.
    Twenty steps resolve to a millionth, which is far finer than the input it filters on.
    """
    key = (t, k, blocks)
    if key in _ABSORB_CACHE:
        return _ABSORB_CACHE[key]
    import reliable_bit_selection as R
    from math import sqrt
    keep = 1.0 - I.SELECTION_LOSS
    tol = max_ber(127, t, blocks)
    base = R.sigma_for_raw_ber(I.RAW_NOISE_BER) ** 2
    lo, hi = 0.0, 0.99
    for _ in range(20):
        mid = (lo + hi) / 2
        sig = sqrt(base + R.sigma_for_raw_ber(max(mid, 1e-6)) ** 2)
        if R.selected_ber_counts_exact(sig, keep, I.ENROLMENT_READS, steps=600) <= tol:
            lo = mid
        else:
            hi = mid
    _ABSORB_CACHE[key] = lo
    return lo


def check_ledger_figures(rec):
    """Bind the numbers in the ledger's area row to the model that produces them.

    W-INTL-170: the error rate tracks whether a number is executed, and both errors that
    mattered lived in prose. The ledger row that carries this project's externally visible
    area claim held sixteen numbers, of which four were recomputed by this file and twelve
    were sentences.

    Each entry below is recomputed from research/inputs.py. Figures that are external -
    the literature's aging rates, the process node, the key length - are deliberately not
    here; they are inputs, not derivations, and binding them would only assert that a
    constant equals itself.
    """
    if rec is None:
        return 0
    tiles, n, k, t, blocks, raw, osc, rho_sel = rec
    decoder = I.decoder_area(7, t)
    sllc = I.SLLC_AREA[t]   # guaranteed present: recommendation() skips codes without it
    counter = I.COUNTERMEASURE_AREA["spongent_permutation"]
    osc_area = osc * OSC
    cells = decoder + sllc + counter + osc_area
    conventional_osc = osc * INVERTERS * I.INVERTER_AREA
    delta_tiles = (cells / UTILISATION / TILE) - (
        (decoder + sllc + counter + conventional_osc) / UTILISATION / TILE)

    bound = [
        ("cell area",            r"from ([\d,]+) square micrometres of standard cells", cells, 1),
        ("tile utilisation",     r"measured (\d+) percent tile utilisation", UTILISATION * 100, 0.5),
        ("decoder area",         r"decoder ([\d,]+),", decoder, 1),
        ("SLLC area",            r"SLLC stages ([\d,]+),", sllc, 1),
        ("countermeasure area",  r"countermeasure ([\d,]+),", counter, 1),
        ("oscillator area",      r"oscillators ([\d,]+)\.", osc_area, 1),
        ("raw positions",        r"([\d,]+) raw positions", raw, 0),
        ("selected positions",   r"([\d,]+) selected, \d+ oscillators", n * blocks, 0),
        ("k carried",            r"carries ([\d,]+) bits of k", k * blocks, 0),
        ("k required at the measured density",
         r"against the ([\d.]+) the key needs", KEY_BITS / rho_sel, 0.05),
        # W-INTL-228: the design is sized against the derated density, so the number
        # it is actually built to is the second one, and a ledger stating only the
        # first would describe a construction with 88 spare bits of k for no reason.
        ("k required at the derated density",
         r"and the ([\d.]+) it needs once the borrowed figure is derated",
         KEY_BITS / SE_SIZED_DENSITY, 0.05),
        ("measured density",     r"the measured ([\d.]+) - selection amplif", RHO, 0.0005),
        ("aging factor",         r"above the estimated ([\d.]+) times", I.AGING_RESISTANT_FACTOR, 0.005),
        ("aging cost in tiles",  r"per stage and ([\d.]+) of a tile", delta_tiles, 0.005),
        # The read count had no bound figure, so a control that set it to one changed
        # nothing a check could see - W-INTL-192. These two depend on it.
        ("ten-year margin",      r"a ten-year margin of ([\d.]+)", aged_margin(), 0.15),
        # The conventional bank's flip rate was declared and unread - the design uses the
        # aging-resistant bank, so nothing in the recommendation path touches it, and the
        # coverage sweep said so the moment it became a declared input. It is the figure
        # the whole aging argument is against, so the ledger states it and this binds it.
        ("conventional flip rate",
         r"loses ([\d.]+) percent of its response bits over ten years",
         I.AGED_FLIP_CONVENTIONAL * 100, 0.05),
        ("absorbable flip rate", r"flip rate exceeds ([\d.]+) percent unselected",
         absorbable_flip() * 100, 0.15),
    ]
    # Two counts that describe the apparatus rather than the design, and were both
    # stale in prose: the testbench count and the number of declared areas. Counted from
    # the artefacts rather than remembered.
    # The obvious regex counts the function definition too - "run_tb () {" starts with
    # "run_tb " - and reported twenty-two where the script runs twenty-one. Caught by the
    # script's own count disagreeing with it, which is the point of counting twice.
    tb_count = len(re.findall(r'(?m)^run_tb "',
                              (ROOT / "research" / "rtl" / "measure_all.sh").read_text()))
    declared = (len(I.DECODER_AREA) + len(I.DECODER_AREA_SERIAL)
                + len(I.SLLC_AREA) + len(I.COUNTERMEASURE_AREA)
                + len(I.POINTER_AREA) + len(I.SOLVER_AREA)
                + len(I.CHARACTERISER_AREA))
    WORDS = {19: "nineteen", 20: "twenty", 21: "twenty-one", 22: "twenty-two",
             23: "twenty-three", 24: "twenty-four", 25: "twenty-five",
             26: "twenty-six", 27: "twenty-seven", 28: "twenty-eight",
             29: "twenty-nine", 30: "thirty", 31: "thirty-one",
             32: "thirty-two", 33: "thirty-three"}
    bound += [
        ("testbench count", r"measure_all\.sh runs ([a-z-]+) testbenches",
         WORDS.get(tb_count, str(tb_count)), None),
        ("declared areas", r"re-synthesised by scripts/verify_inputs\.py - ([a-z-]+) of them",
         WORDS.get(declared, str(declared)), None),
    ]

    text = LEDGER.read_text() if LEDGER.exists() else ""
    if not text:
        failures.append("evidence_ledger.md missing, so no ledger figure was bound")
        return 0
    flat = re.sub(r"\s+", " ", text)
    for label, pattern, expected, tol in bound:
        m = re.search(pattern, flat)
        if not m:
            failures.append(f"evidence_ledger.md: no figure found for {label} "
                            f"(pattern {pattern!r})")
            continue
        if tol is None:                      # a word rather than a number
            if m.group(1) != expected:
                failures.append(
                    f"evidence_ledger.md: {label} says '{m.group(1)}', counting the "
                    f"artefact gives '{expected}'")
            continue
        got = float(m.group(1).replace(",", ""))
        if abs(got - expected) > tol:
            failures.append(
                f"evidence_ledger.md: {label} says {got:g}, recomputing from inputs "
                f"gives {expected:.4g} (tolerance {tol})")
    return len(bound)


def check_register_figures(rec):
    """The constraint register carries the same numbers as the ledger, in sentences.

    It is the document where a constraint's *status* is recorded, and W-INTL-171 found
    the failure that costs: the ledger described aging as unchecked two loops after it
    became binding, in the same paragraph as the design built to satisfy it. The register
    is where that class of contradiction lives, so its figures are bound too.
    """
    if rec is None or not REGISTER.exists():
        return 0
    tiles, n, k, t, blocks, raw, osc, rho_sel = rec
    conventional = (I.decoder_area(7, t) + I.SLLC_AREA[t]
                    + I.COUNTERMEASURE_AREA["spongent_permutation"]
                    + osc * INVERTERS * I.INVERTER_AREA)
    bound = [
        ("k carried", r"construction meets at (\d+)", k * blocks, 0),
        ("post-selection density", r"which is ([\d.]+) rather than 0\.9414",
         rho_sel, 0.0005),
        ("measured density", r"rather than (0\.9414)", RHO, 0.0005),
        ("aging factor", r"([\d.]+) times the area by transistor width",
         I.AGING_RESISTANT_FACTOR, 0.005),
        ("aging cost in tiles", r"transistor width, ([\d.]+) of a tile",
         tiles - I.tiles(conventional), 0.005),
        ("tiles before", r"taking the design from ([\d.]+) to", I.tiles(conventional), 0.005),
        # Anchored on the sentence rather than on "of sixteen", which also appears
        # in "13 to 15 of sixteen" elsewhere in the file and matched first.
        ("tiles after", r"taking the design from [\d.]+ to ([\d.]+) of sixteen",
         tiles, 0.005),
    ]
    flat = re.sub(r"\s+", " ", REGISTER.read_text())
    for label, pattern, expected, tol in bound:
        m = re.search(pattern, flat)
        if not m:
            failures.append(f"constraint_register.md: no figure found for {label} "
                            f"(pattern {pattern!r})")
            continue
        got = float(m.group(1))
        if abs(got - expected) > tol:
            failures.append(
                f"constraint_register.md: {label} says {got:g}, recomputing from inputs "
                f"gives {expected:.4g} (tolerance {tol})")
    return len(bound)


def check_borrowed_table():
    """Bind the borrowed-margin tables in decoder_code_choice.md to the model.

    Both tables were exempted from the consistency rule with `derived:external`, which says
    the figures come from outside that document - true, and it left them bound to nothing.
    W-INTL-224 is what that costs: the margin column read 1.26 for an interval after the
    model that produced it was corrected to 1.13, and no check could have said so.

    Returns the number of figures bound.
    """
    import importlib
    sys.path.insert(0, str(ROOT / "research"))
    BM = importlib.import_module("borrowed_margins")
    path = ROOT / "research" / "decoder_code_choice.md"
    if not path.exists():
        return 0
    text = path.read_text()
    bound = 0

    for name, value, limit_fn, direction, _ in BM.ROWS:
        row = re.search(rf"\| {re.escape(name)} \| ([\d.]+) \| ([\d.]+) (above|below) \| "
                        rf"\*\*([\d.]+)x\*\*", text)
        if not row:
            failures.append(f"decoder_code_choice.md: no margin row for {name}")
            continue
        limit = limit_fn()
        margin = (value / limit) if direction == "below" else (limit / value)
        # A prose figure is rounded, and how far it may sit from the model is set by how
        # many decimals it was printed to - not by a tolerance picked to make it pass.
        def rounding_tol(text):
            frac = text.split(".")[1] if "." in text else ""
            return 0.5 * 10 ** -len(frac)

        for got, want, what in ((row.group(1), value, "value"),
                                (row.group(2), limit, "limit"),
                                (row.group(4), margin, "margin")):
            bound += 1
            tol, got = rounding_tol(got), float(got)
            if abs(got - want) > tol:
                failures.append(f"decoder_code_choice.md: {name} {what} reads {got:g}, "
                                f"the model gives {want:.4g}")
        if row.group(3) != direction:
            failures.append(f"decoder_code_choice.md: {name} row says {row.group(3)}, "
                            f"the model says {direction}")

    # The joint table. Each cell is a claim about whether any selection fraction works.
    joint_rows = 0
    for density in BM.JOINT_DENSITY:
        # Anchored to the line start, past any derivation marker: the margin table also
        # carries 0.9414, in a row of three cells, and an unanchored search finds it first.
        row = re.search(rf"^(?:<!-- \S+ --> )?\| {density:.4f} \| (.+?) \|\s*$",
                        text, re.M)
        if not row:
            continue                      # not every swept row is quoted in the document
        joint_rows += 1
        cells = [c.strip() for c in row.group(1).split("|")]
        if len(cells) != len(BM.JOINT_FLIP):
            failures.append(f"decoder_code_choice.md: joint row {density} has "
                            f"{len(cells)} cells, the model sweeps {len(BM.JOINT_FLIP)}")
            continue
        for cell, flip in zip(cells, BM.JOINT_FLIP):
            bound += 1
            keep = BM.largest_retained(density, flip)
            want = "---" if keep is None else f"{keep:.0%}"
            if cell != want:
                failures.append(f"decoder_code_choice.md: joint cell ({density}, {flip}) "
                                f"reads {cell}, the model gives {want}")
    if joint_rows == 0:
        failures.append("decoder_code_choice.md: the joint table matched no rows, so this "
                        "half of the check read nothing")
    return bound


def main():
    check_selection_entropy()

    # The headline: the construction recommended now, not the one recommended in loop 61.
    rec = recommendation()
    if rec is None:
        failures.append("model: nothing fits at the recommended operating point")
    else:
        tiles, n, k, t, blocks, raw, osc, rho_sel = rec
        docs = [(LEDGER, "evidence_ledger.md"),
                (ROOT / "research" / "decoder_code_choice.md", "decoder_code_choice.md")]
        for path, name in docs:
            if not path.exists():
                continue
            text = path.read_text()
            required = (name == "evidence_ledger.md")
            check(text, name, "tiles of sixteen at the recommendation",
                  r"([0-9]+\.[0-9]+) of the sixteen tiles", tiles, 0.02, required)
            check(text, name, "entropy density floor of the recommendation",
                  r"entropy density down to ([0-9]\.[0-9]+)", KEY_BITS / (k * blocks),
                  0.002, required)
            check(text, name, "oscillator floor",
                  r"oscillator floor is ([0-9]+) oscillators", osc, 0, required)

    n_bound = (check_ledger_figures(rec) + check_register_figures(rec)
               + check_borrowed_table())
    if n_bound < 25:
        failures.append(
            f"only {n_bound} ledger figures were bound; the list has shrunk, which is "
            f"how a number goes back to being a sentence")

    at_measured = cheapest(RHO, 0.04)
    if at_measured is None:
        failures.append("model: no code fits at the measured entropy and 4 percent")
    else:
        # cheapest() is kept for one job only: it is the arrangement in which the
        # utilisation factor was dropped, so it still guards that. It is no longer the
        # source of any figure a document has to match.
        # The high error-rate columns must be absent, which is what W-INTL-99 restored.
        for ber in (0.07, 0.08):
            if cheapest(RHO, ber) is not None:
                failures.append(
                    f"model: something fits at {ber:.0%} error rate, which contradicts "
                    f"W-INTL-99 - check the utilisation factor"
                )

    if REGISTER.exists():
        reg = REGISTER.read_text()
        if "58 percent" not in reg:
            failures.append("constraint_register.md: no utilisation figure in the area row")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"\ncheck_figures_reproduce: {len(failures)} failure(s)")
        return 1
    tiles, n, k, t, blocks, raw, osc, rho_sel = rec
    print(f"check_figures_reproduce: OK "
          f"(recommendation BCH({n},{k},{t}) x {blocks} at {tiles:.2f} of {TILE_LIMIT} "
          f"tiles, {raw} raw positions, {osc} oscillators, "
          f"post-selection density {rho_sel:.4f}; "
          f"{n_bound} prose figures bound)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
