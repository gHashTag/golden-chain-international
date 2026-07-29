# Verifiability per Dollar, Computed

Status: first computation, 2026-07-29. Closes the arithmetic half of audit entry
W-INTL-37, which recorded that this metric had been named as the organising idea
of the thesis across three predecessor review passes and never once computed.

The result is not flattering in the direction that was probably hoped for, and it
is useful in a direction that was not.

---

## 1. Why a single number is not available

The metric as usually stated - verification obtained per unit of spend - needs a
unit of work that both systems perform. The two systems being compared do not
perform comparable work. A Zynq-7020 node and a confidential cloud instance differ
by orders of magnitude in throughput, and any ratio built across that gap says
more about the gap than about verification.

So the honest move is to compute what can be computed, name the unit each time,
and refuse the composite. Three quantities below are real. The fourth is the one
everyone wants and it is not available yet.

## 2. Cost of an attested node-hour

Inputs, with sources and their weaknesses stated.

| Input | Value | Source | Weakness |
|---|---|---|---|
| Node hardware | 439 to 859 USD | public listing range for the board used | a listing range, not a purchase invoice; quantity pricing unknown |
| Amortisation | 3 years, 26,280 hours | assumption | no field data on service life |
| Power draw | 6 W | [EST] from device data, not measured | measurement outstanding, see ledger E16 |
| Energy price | 0.10 USD per kWh | mid industrial rate | varies by more than 2x across candidate regions |

Taking the midpoint of the hardware range, 649 USD:

    amortisation   649 / 26,280           = 0.0247 USD per hour
    energy         0.006 kWh x 0.10       = 0.0006 USD per hour
    ------------------------------------------------------------
    attested node-hour                     = 0.0253 USD per hour

At the ends of the hardware range this is 0.0173 to 0.0333 USD per hour. Every
figure in the table above can move it, and the power figure is an estimate rather
than a measurement, so treat the result as a first significant figure: about three
US cents per node-hour.

## 3. Cost of the sampling overhead

The published assurance parameters are one percent sampled re-execution with stake
set at one hundred times the unit reward.

Re-execution is a direct cost and it is small: the network performs 1.01 units of
work per unit settled, so the overhead is one percent of the figure above, about
0.00025 USD per hour. It is not the interesting term.

Stake is not a cost, it is locked capital. Its cost is the return foregone on it.
For a unit reward r the stake is 100r, so at an annual opportunity cost c the
carrying cost per unit is 100rc divided by the number of units the stake covers
per year. Without a settled unit reward this cannot be reduced to a number, and no
document defines r. That is the second open item this computation exposes: the
assurance parameters are published in ratios but never grounded in a price.

## 4. Cost of the attestation premium in the alternative

Confidential computing is billed as a premium over ordinary instances. Published
on-demand rates for an Intel TDX confidential VM are 0.0033982 USD per vCPU-hour
and 0.0004555 USD per GiB-hour. For a small four-vCPU, sixteen-GiB instance:

    vCPU premium   4 x 0.0033982          = 0.0136 USD per hour
    memory premium 16 x 0.0004555         = 0.0073 USD per hour
    ------------------------------------------------------------
    attestation premium                    = 0.0209 USD per hour

This is the premium alone. The underlying instance is charged separately.

## 5. The one comparison that survives

Owning and running an attested node costs about 0.025 USD per hour. Paying the
attestation premium on a small confidential cloud instance costs about 0.021 USD
per hour, on top of the instance itself.

So the price of the attestation property alone, rented, is within the same order
as the price of owning the whole device that provides it. That is the defensible
statement, and it is narrower than the metric it replaces.

Three qualifications, all of which matter more than the ratio.

The node is not doing the cloud instance's work. On throughput the comparison is
lost by a wide margin, and section 1 of the competitor matrix says so with
measured figures.

The node delivers a second service the instance does not: it carries mesh
connectivity. Per dollar it provides transport as well as attestation, which is
the actual architectural argument and is not captured by any per-hour figure.

The attestation the node provides is currently weaker than the one it is compared
against. Per audit W-INTL-34, the deployed registry accepts a self-declared key,
so the device-identity property is not yet enforced. A comparison of prices for a
property that one side does not yet deliver is a comparison of intentions. This
section should be re-run once the identity gate exists.

## 6. What would make the composite metric available

A unit of verified work, defined once and used everywhere: one settled proof of a
named type, with its compute content stated. A price for that unit, which is the
missing r above. Then verification per dollar is units settled divided by total
cost including the carrying cost of stake, and it can be compared against the
premium a buyer pays to obtain the same assurance from a vendor enclave.

Until the unit and its price exist, the metric should be described as the
organising idea it is, and not quoted as though a number stood behind it.
