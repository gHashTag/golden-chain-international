#!/usr/bin/env python3
"""Enrolling at two temperatures answers the temperature term for no area at all.

W-INTL-237, and it comes from the last unaudited input. `ENROLMENT_READS = 25` is declared
as a requirement on the provisioning flow, and `constraint_register.md` adds a condition
nobody followed up: the reads are taken "at the operating temperature". A part is enrolled
once, at manufacture, at one temperature, and then operates across a range - so the phrase
is either a requirement the flow cannot meet or a lever nobody pulled.

It is a lever.

Twenty-five reads reduce the *read noise* in the enrolment estimate by twenty-five. They do
nothing whatever to the temperature drift, because more reads at one temperature say
nothing about behaviour at another - which is why `aged_selected_ber` averages only the
noise. But reads at a SECOND temperature say exactly that, and reliable-bit selection is a
ranking: rank on the worst of the two conditions instead of on one, and the positions that
survive are the ones that are stable across both.

That is the only lever found in this work that attacks the environmental residual directly.
Everything else - a longer code, more blocks, a deeper fraction - answers a worse error rate
after the fact.

What it is worth
----------------
At the worst chip in the measurement this project borrows, one-temperature enrolment fails
at the declared selection fraction and two-temperature enrolment passes, by a factor of
3.8 in the error rate. The construction does not change, the oscillator count does not
change, and the area does not change. The alternative found in W-INTL-236 - selecting
harder - costs 0.25 of a tile, 5,715 raw positions and 108 oscillators. This costs a
second enrolment pass.

What it assumes
---------------
That the temperature drift is REPEATABLE: that a position which moves one way at 70 degrees
moves that way every time it reaches 70 degrees. That is what makes the second enrolment
informative rather than a second noisy sample, and it is the same property that makes the
drift a drift rather than noise, so it is consistent with how the term is modelled
throughout. A non-repeatable component would not be reduced by this and would not be a
drift.

And that the second condition is at or beyond the operating extreme. Selecting on the
extreme is conservative for anything in between, which is why it is the extreme that is
enrolled.

Monte Carlo, with a fixed seed, so the figures do not move between runs - a check that
moves by a thousandth teaches people to re-run it, which is why every other model here is
closed form. Two dimensions of drift and an order statistic over two conditions do not have
one.

Usage: multi_condition_enrolment.py    prints the comparison
"""

import math
import random
import sys
from statistics import NormalDist

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import aging_margin as AM
import inputs as I
import reliable_bit_selection as R

ND = NormalDist()
SAMPLES = 400_000
SEED = 12345


def selected_ber(temperature_sigma, keep, conditions, samples=SAMPLES, seed=SEED):
    """Error at the operating extreme, ranking on `conditions` enrolment temperatures.

    conditions=1 ranks on the nominal enrolment alone, which is what the design does.
    conditions=2 ranks on the smaller of the two magnitudes, nominal and extreme.
    """
    rng = random.Random(seed)
    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    aging = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    tau = noise / math.sqrt(I.ENROLMENT_READS)

    rows = []
    for _ in range(samples):
        d = rng.gauss(0.0, 1.0)
        drift = rng.gauss(0.0, temperature_sigma)
        nominal = d + rng.gauss(0.0, tau)
        extreme = d + drift + rng.gauss(0.0, tau)
        score = min(abs(nominal), abs(extreme)) if conditions == 2 else abs(nominal)
        rows.append((score, d, drift, nominal))

    rows.sort(key=lambda row: -row[0])
    kept = rows[:int(samples * keep)]
    wrong = 0
    for _, d, drift, nominal in kept:
        regenerated = (d + drift + rng.gauss(0.0, aging) + rng.gauss(0.0, noise))
        if (regenerated >= 0.0) != (nominal >= 0.0):
            wrong += 1
    return wrong / len(kept)


def selected_ber_conditional(temperature_sigma, keep, samples=1_600_000, seed=SEED):
    """The same quantity, estimated without tossing the coin. W-INTL-247.

    `selected_ber` above draws the regeneration noise and counts whether the bit flipped.
    At an error rate near 0.0037 that Bernoulli draw is almost all of the variance: the
    standard error is 3.5 percent of the value at four hundred thousand samples, so the
    comparison it feeds could resolve differences above ten percent - and the modelling
    error W-INTL-232 corrected was eight.

    A check that would not have caught the last defect is worth knowing about before the
    next, so this estimator accumulates the CONDITIONAL probability of a flip for each kept
    position instead of a zero or a one. Everything the closed form assumes is still
    simulated - the finite-sample ranking, the drift, the enrolment noise - and only the
    last coin toss is replaced by its expectation, which is what makes it a variance
    reduction rather than a different question.

    Halves the standard error at the same cost, and four times the samples halves it again:
    2.5 percent resolution in under three seconds, against the eight percent that matters.

    Stratifying the difference d does not help - the variance lives in the drift and in the
    spread of the conditional probabilities, not in d - and that was measured rather than
    assumed.
    """
    rng = random.Random(seed)
    noise = R.sigma_for_raw_ber(I.RAW_NOISE_BER)
    aging = R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT)
    tau = noise / math.sqrt(I.ENROLMENT_READS)
    drift_sigma = math.sqrt(aging * aging + temperature_sigma * temperature_sigma)

    rows = []
    for _ in range(samples):
        d = rng.gauss(0.0, 1.0)
        drift = rng.gauss(0.0, drift_sigma)
        nominal = d + rng.gauss(0.0, tau)
        rows.append((abs(nominal), d + drift, nominal))

    rows.sort(key=lambda row: -row[0])
    kept = rows[:int(samples * keep)]
    values = [ND.cdf(-(aged if nominal >= 0.0 else -aged) / noise)
              for _, aged, nominal in kept]
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return mean, math.sqrt(variance / len(values))


if __name__ == "__main__":
    tol = AM.tolerated_ber()
    keep = 1.0 - I.SELECTION_LOSS
    print(f"tolerated selected error rate {tol:.5f}, {SAMPLES:,} samples, seed {SEED}\n")
    print(f"{'temperature':>12} {'kept':>7} {'one condition':>14} {'two conditions':>15} "
          f"{'verdict':>16}")
    for flip in (I.TEMPERATURE_FLIP_TYPICAL, I.TEMPERATURE_FLIP_WORST):
        sigma = R.sigma_for_raw_ber(flip)
        for fraction in (keep, 0.326, 0.20):
            one = selected_ber(sigma, fraction, 1)
            two = selected_ber(sigma, fraction, 2)
            verdict = ("both meet" if max(one, two) <= tol
                       else "two only" if two <= tol else "neither")
            print(f"{flip:>12.2%} {fraction:>7.1%} {one:>14.5f} {two:>15.5f} "
                  f"{verdict:>16}")

    # The one-condition arm is the closed-form model's own case, so the two must agree.
    # They do, to within sampling error, which is the only place in this project where two
    # independent implementations of the same quantity meet - every other cross-check
    # compares a document against a model rather than a model against a model.
    sigma = R.sigma_for_raw_ber(I.TEMPERATURE_FLIP_WORST)
    from math import sqrt as _sqrt
    closed = R.aged_selected_ber(
        R.sigma_for_raw_ber(I.RAW_NOISE_BER),
        _sqrt(R.sigma_for_raw_ber(I.AGED_FLIP_RESISTANT) ** 2 + sigma * sigma),
        keep, I.ENROLMENT_READS)
    mc = selected_ber(sigma, keep, 1)
    band = _sqrt(mc * (1 - mc) / (SAMPLES * keep))
    print(f"\nagreement with the closed form at one condition: Monte Carlo {mc:.5f}, "
          f"closed form {closed:.5f},")
    print(f"apart by {abs(mc - closed) / band:.1f} standard errors of the sampling")

    one = selected_ber(sigma, keep, 1)
    two = selected_ber(sigma, keep, 2)
    print(f"\nat the worst chip and the declared fraction, one condition gives {one:.5f}")
    print(f"and two give {two:.5f}, a factor of {one / two:.1f}, which is the difference")
    print("between missing the target and meeting it with the construction unchanged.")
    print("\nW-INTL-236 answers the same corner by selecting harder: 0.25 of a tile,")
    print("5,715 raw positions, 108 oscillators. This answers it with a second enrolment")
    print("pass and no area. Both are recorded; neither is adopted, because the borrowed")
    print("11 percent is from a different circuit over a narrower span and what settles")
    print("it is the same temperature sweep either way.")
