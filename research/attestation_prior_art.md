# Attestation Prior Art

Status: written 2026-07-30. Prompted by a gap this project's own code now states
explicitly: `ChipRegistryV2` proves that whoever registered a chip identifier held
the key it derives from, and cannot prove the key lives on a die rather than in a
file. That is the hard part of the thesis, and it has a literature.

**How these sources were read, stated because the audit requires it.** Search-level
summaries and abstracts, not full texts. Two of the closest papers returned 403 to
an unauthenticated fetch. So what follows is a map of where the answers live and
what they appear to say, not a reading of the arguments. Anything acted on should
be read properly first, and the entries below say which ones matter enough to
warrant that.

---

## 1. The gap, restated precisely

The project's attestation argument is that proving where a computation ran should
not require a trusted execution environment from a processor vendor, because that
reintroduces the dependence the buyer is trying to reduce. That argument is sound
and is the strongest thing the application says.

What it needs in order to work is a way to bind a signing key to a specific
physical device without a vendor enclave. The gate written this week binds a key
to an identity and closes four replay paths. It does not bind the key to silicon.
An operator who extracts a key once can register from anywhere thereafter.

## 2. What the literature does about it

Three families, and the project has been reaching for the weakest one.

**Keys derived from a physical function rather than stored.** The recurring answer
is not to protect a stored key but to have no stored key: the signing key is
reconstructed from a physically unclonable function at the moment it is used, so
there is nothing at rest to extract. This is the direct answer to the question the
gate cannot answer, and it changes the attack from "read the flash once" to
"possess the device and elicit its response every time". For this project it also
happens to be the reading of `ChipRegistry`'s own documentation, which says the
identifier is derived from an on-die function - the design already assumes this
family and the implementation does not yet reach it.

**Attestation read-only memory paired with that key.** Several schemes add a small
immutable region holding the attestation routine, specifically for devices whose
application code lives in external non-volatile memory that an attacker can read
or rewrite. That is exactly the situation on both parts here: the bitstream and
the root filesystem sit in external flash. A key derived from a physical function
is worth little if the code that uses it can be replaced, which is the failure
mode this addresses and which nothing in the current design does.

**Software-only attestation resting on timing or on memory scarcity.** The
literature names this family and characterises it as depending on stringent time
constraints or on the absence of free space in which to hide malicious code. This
is the family the project already tried: audit entry W-INTL-21 records that a
response-deadline challenge was tested and refuted, because an optimised software
implementation completed the dependent work faster than the target device. The
literature's framing explains why that outcome was likely rather than unlucky -
the whole family rests on an assumption about the adversary's hardware, and that
assumption fails the moment the adversary has better hardware.

## 3. What follows for this project

**The refutation in W-INTL-21 was a category result, not a bad day.** Timing-based
software attestation is a known family with a known dependency, and testing it
against a faster software implementation is the standard way it fails. That entry
should say so, because "we tried a thing and it did not work" reads as weaker than
"we tested the software-only family against its known dependency and confirmed it
does not hold for our device class".

**The identity roadmap has a shape, and it is not the one being built.** In
increasing strength: a signature over a bound message, which now exists; a key
reconstructed from a physical function rather than stored, which the documentation
already assumes and the hardware may support; and an immutable attestation routine
so that the code using the key cannot be swapped. The third matters most on parts
whose code lives in external flash, which is both of these.

**One honest boundary does not move.** None of this reaches the guarantee a vendor
enclave offers, and the application should keep saying so. What it reaches is
assurance whose cost to defeat is physical possession of a device rather than a
one-time key extraction, and that is a materially different proposition from what
is deployed today.

## 4. What to read properly before acting

In order of how much a decision would rest on them:

1. The lightweight remote attestation scheme combining a physical function with
   hash-based signatures for low-end devices, in Future Generation Computer
   Systems, 2023. Closest match to the device class here, and the source of the
   attestation-ROM pairing.
2. The survey of hardware approaches to remote attestation, arXiv:2005.12453.
   Establishes where these families sit relative to each other and to trusted
   platform modules.
3. Work on publicly verifiable attestation. The project's thesis is that a third
   party should be able to check, not merely the operator, and that constraint
   rules out schemes whose verification is private.

## 5. Availability on the parts in hand, checked 2026-07-30

The strong family is not available. Neither part has a hardened physical function:
Zynq UltraScale+ devices do, Zynq-7000 and the 7-Series do not, and on those
families such a function must be built in fabric. Fabric lives in the bitstream,
and the bitstream on these parts carries an unpatchable published break to its
encryption on one and a published bypass of its authentication on the other. A
fabric-built function on either can therefore be read out, or the code consuming it
replaced.

The consequence is recorded as audit entry W-INTL-46 and it is the reason this
research mattered. The project holds two constraints at once - identity rooted in
the device, and hardware obtainable under any export regime - and on commodity
parts they conflict. The part that offers the function today is a recent
advanced-node device, which is the class the thesis argues a supply-chain-independent
buyer cannot count on. The two constraints meet at exactly one point, a custom die
on a mature node.

Confirmed against the manuals on 2026-07-30, for each part rather than for one and
its family. UG470 for the bench tier and UG585 for the mesh tier, the latter being
1843 pages and 3.2 megabytes of extracted text. The three phrasings return zero
occurrences in both.

What both manuals do offer is a key at rest - in fuses or in battery-backed memory
- which is the family the literature specifically argues against, since a key at
rest is a key that can be extracted. And the layer protecting that storage on these
parts is the bitstream path, which carries an unpatchable published break on one
and a published authentication bypass on the other. So the parts do not merely lack
the strong option; the option they do offer has its protective layer already broken
in this setting.

## 6. What this does not license

It does not license claiming a physical-function-based identity in any external
document. Nothing of that kind is implemented, the parts' capability for it has
not been established here, and the two published attacks recorded in W-INTL-19
apply to the bitstream path on both tiers regardless. The finding is that a
credible path exists and is documented in the literature, and that the project has
been attempting the weakest of the three families available to it.
