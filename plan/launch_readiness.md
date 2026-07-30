# Launch Readiness

Status: written 2026-07-30. What is deployed today is a testnet bring-up. This
sets out what separates it from a production launch, in the order the gaps have
to be closed, and it starts with one that was found by reading the deployed
contracts rather than by consulting a checklist.

---

## 1. What is deployed today, and what that means

Five contracts on Base Sepolia, chain id 84532. A testnet. The tokens have no
value, the chain is disposable, and a deployment there commits nothing. That is
the correct place for the work to be, and it should be described that way.

Two facts about the current deployment matter more than its existence. Nothing
has ever used it: the registry and the prover show zero transactions 72 days
after deployment. And none of the five is source-verified on the explorer, so
nobody outside the project can confirm the bytecode was built from the published
source. `scripts/verify_contracts.sh` closes the second down to one command.

## 2. The blocker, found in the contracts rather than in a checklist

MiningPool is `Ownable` and exposes `setChipRegistry`, which replaces the registry
deciding which chips may claim rewards. MiningPool holds the entire token supply.
TriToken renounces ownership in its constructor.

The deployment script renounces MiningPool's ownership too, explicitly, on the
line after the token is deployed. So there is no owner and no administrative key
anywhere in the deployed set.

That is not the reassurance it first appears to be. The registry can never be
replaced, and the registry currently accepts any self-declared key (audit
W-INTL-34). This deployment therefore has a permanently unfixable identity gate:
nothing can repair it, nothing can pause it, and no key exists that could.

For this deployment that is acceptable, because it is a testnet and it has never
been used. Treat it as disposable, which is what a testnet is for.

For a value-bearing deployment it is the central design question, and it is worth
stating plainly. Renouncing everything at deployment is the strongest possible
statement about supply and the weakest possible position on defects, because it
forecloses every response to one. The defensible sequence is to renounce late
rather than early: hold administrative functions in a multi-signature wallet
behind a timelock while the system is being exercised, and give them up once it
has been. That reaches the same end state, and keeps the ability to fix a defect
during precisely the window in which defects are found.

## 3. What a production launch requires, mapped to what exists

Ordered by what blocks what, not by importance in the abstract.

**Custody before anything else.** Administrative functions on a value-bearing
contract belong to a multi-signature wallet with named signers, behind a timelock
where the action can change who gets paid, so the change is visible before it
takes effect. Neither exists in the current set - not because the keys are held
badly but because they were given up at deployment, which is the other way to
have no custody policy.

**Identity has a hardware floor, and the current parts are below it.** Per audit
W-INTL-46, the scheme the attestation literature recommends - a key reconstructed
from a physical function rather than stored - needs a hardened function neither
part has. Built in fabric it lives in a bitstream with a published break on one
part and a published authentication bypass on the other. So no arrangement of
contracts closes identity on this hardware, and the custom die is where it closes
rather than a later ambition. That does not block anything below; it means identity
should be described as asserted until the die exists.

**The identity gate has to be real.** MiningPool's chip check currently passes for
any key someone previously registered, because ChipRegistry has no signature
check. A drafted gate exists in audit W-INTL-34; it is a specification and has not
been written, tested or reviewed. Until it is, the economic security of the
network rests on the nullifier and the register cap alone, which is worth saying
out loud.

**The prover has to verify.** JobProver carries a placeholder verifying key with
its first constants set to 1 and 2, labelled as such in the source. It cannot
verify a proof. No external party should be invited to submit one until a real
trusted setup output replaces it.

**Test coverage, then tools, then an external audit, in that order.** The
prevailing guidance is high unit and integration coverage first, then static
analysis and fuzzing, and only then a third-party audit - because an audit spent
finding what a fuzzer would have found is an audit wasted. For contracts holding
supply this is not optional and it is the long pole in any realistic schedule.

**Rehearse the deployment against a fork.** Fork mainnet, run the deployment
script, trace the transactions, and confirm the resulting state matches what was
intended, before anything is sent for real. The circular constructor arrangement
here - MiningPool deployed against TriToken's predicted address, TriToken then
receiving MiningPool's - is exactly the kind of thing that must be rehearsed
rather than reasoned about.

**Stage the exposure.** Caps, allowlists or a restricted first cohort, so that
production behaviour can be compared against expectation while the amount at risk
is small. A network paying operators has a natural staging axis: a small number of
known operators first.

**Have the incident plan before you need it.** A pause path, a documented
response, and a decision made in advance about who can invoke it. Designed at
build time, not after.

## 4. Sequence

1. Write down the ownership schedule for the next deployment: what is held, by
   whom, behind what delay, and on what condition it is given up. The current
   arrangement - everything renounced at deployment - was almost certainly
   inherited from the script rather than chosen, and should not be repeated by
   default.
2. Write the ChipRegistry gate. Have it reviewed by someone who did not write it.
3. Replace the JobProver verifying key, or remove that register from the
   published set until it is real.
4. Submit one proof end to end on the testnet. Nothing has ever exercised this
   path, so no claim about it has been tested at all.
5. Bring coverage up, run static analysis and fuzzing, fix what they find.
6. External audit.
7. Fork rehearsal of the exact deployment.
8. Mainnet with a staged cohort and a published incident plan.

Steps 1 through 4 are the project's own work and are not blocked on funding. Step
6 is where the money and the calendar go.

## 5. What to say in the meantime

That the contracts are deployed to a public testnet, unexercised, and not yet
audited; that the economics are implemented and the identity gate is not; and
that mainnet is gated on an audit rather than on a date. Every part of that is
checkable, which is the point.

The temptation is to describe the testnet deployment as a launch. It is not one,
a reviewer will establish that in about a minute from the transaction count, and
the honest description is more useful anyway: five contracts written, deployed and
waiting on an identity gate and an audit is a clear statement of where the work
actually is.
