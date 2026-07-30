---
name: claim-verification
description: Verify claims in documents against live artefacts before they go to an outside reader. Use when auditing an application, a whitepaper, a status table or a claims ledger, or whenever a document asserts a number, a measurement or the existence of a thing. Encodes nine correction-driven rules from an audit in which half the errors found were in the checking rather than in the claims.
---

# Claim Verification

A document is checked by reaching the artefact behind each claim, not by reading
the claim more carefully. This skill is the residue of an audit that ran to
forty-five findings, of which nine were retractions of its own conclusions. The
rules below each exist because one of those nine happened.

## The first move, always

Open the source, not the record that summarises it. Findings came repeatedly from
reading code where a document had already stated a conclusion:

- A status table said an FPGA ran at a given frequency, `verified`, citing a file.
  The file did not exist. A similarly named one held software benchmarks.
- A contract's identity check was described externally as device identity. The
  contract accepted any self-declared value.
- A published ablation reported a format losing a comparison. The quantiser it
  exercised mixed two format conventions in one function and saturated every row.

Run things where you can. Compiling a testbench, executing a test suite,
synthesising a module and comparing quantisers each settled a question that
reading could not.

## Absence is a claim and needs a method

Five findings were false negatives from a single failed search. Wrong directory;
a settlement contract named `MiningPool` rather than anything containing
"settlement"; a repository name searched for when the content was a directory
inside another repository.

**Never write "X does not exist" from one query.** Search under several phrasings,
in several places, and record in the finding how the search was run so a reader
can judge whether it could have found the thing. Where that record is missing,
write "not found by this method" rather than "absent".

## "This value is wrong" is also a claim and also needs a method

One retraction: two catalog entries were reported as carrying a corrupted bias.
They carried `2^194-1` and `2^390-1`, written as expressions because the values
exceed a 64-bit integer. The check had extracted the bias with a digits-only
pattern and kept the leading `2`.

**A pattern that cannot represent the value's format will always report it as
malformed.** State how the value was read.

## Check the instrument before blaming the subject

Roughly half of all corrections were the tool:

- A consistency check keyed each figure on its known value, so a wrong value did
  not match the pattern at all and the check passed. A check that cannot fail is
  not a check.
- Patterns broke on hard-wrapped text, so multi-word phrases straddling a newline
  were invisible. Normalise whitespace before matching.
- A field rule applied outside its domain flagged thirty-six correct entries -
  vendor formats with their own bias conventions, tapered formats without fixed
  fields, decimal formats with a different convention, composite and logarithmic
  rows with no bias at all. **Apply rules by whitelist, not by exception.** Noise
  trains a reader to ignore the checker.
- Negative controls applied with `sed` to hard-wrapped text silently did nothing,
  so two controls "passed" while testing nothing. **Plant faults
  whitespace-insensitively, or the test only proves the test is broken.**

Every check needs a negative control that fires. Every check that finds nothing
should say whether it could have found something.

## Reach the primary source, and record how far you got

Search summaries and abstracts are a map, not a reading. Say which you did. Two
conclusions here were reached at search depth and marked as such; when one was
later confirmed against the vendor manual it did not merely confirm - it refined.

The manual said a factory identifier is "most often unique. However, up to 32
devices within the family can contain the same DNA value", and separately that a
wider identifier "is always unique" but reachable only over a debug port, not from
inside the device. The search-depth version had one identifier where there are two,
and missed that the unique one is unreachable by the thing that needs it.

So a primary source is not a formality. Reaching it changed what the finding meant.

A negative result from a primary source is worth stating precisely: a term searched
under three phrasings across a whole document with zero occurrences is a much
stronger statement than "I could not find it", and it is the form to use.

**Confirm for the artefact, not for its family.** A conclusion about a capability
was checked against the manual for one part and applied to a second by family
inference. The second part was the one the argument actually rested on. Checking it
directly took one download and it held - but the inference was the weakest link in
the chain while it stood, and it stood in a document presented as verified. Where a
claim concerns a specific thing, reach the document for that thing.

## Findings in either direction count the same

Two retractions ran in the project's favour, one of them large: a format reported
as losing a benchmark turned out to beat the reference once its quantiser was
implemented correctly. Both were written up at the same length as the findings
against. An audit that only ever moves one way is not measuring.

Correspondingly: record what the subject gets right. A status table that marked a
projection as an open conjecture two rows below an overstated measurement had the
discipline; it simply had not applied it to that row. That is worth saying.

## Grade evidence explicitly, and let the grade fall

Give every claim a level and define every level in use. A legend that named five
levels while the table used twelve left readers meeting undefined terms.

Levels that earn their keep, in decreasing strength: measured on hardware with a
recorded artefact; verifiable by a third party without the author's cooperation;
passing a reproducible test; specified but not executed in its target context;
derived from a model whose assumptions are stated; simulation only.

Levels for what does not support a claim, kept in the table rather than omitted:
not built; not measured; partial, with both conditions named; undefined, meaning
the claim has no metric yet; open conjecture with a falsification path; refuted,
meaning the row's own falsification test was run and the claim failed it.

**A row may carry only the level its artefact supports.** Where the two disagree,
lower the level rather than restate the artefact.

## Derive counts, never write them

A summary claimed twenty-nine rows against thirty present, with three categories
missing and three counts each inflated by one. Parse the table and generate the
summary. The same defect recurred two iterations later and a script caught it
within seconds.

## Retract in place

Keep a withdrawn finding, marked, with the reason and the method error that
produced it. Deleting it hides that a decision was made on it. Two entries here
were acted on before being retracted, and the record of that is the useful part.

## Distinguish deployed from working, and specified from written

A deployment is not an operation: five contracts held bytecode and had zero
transactions seventy-two days later, so nothing had ever exercised the settlement
path. Two of the five were scaffolds - one with a placeholder verifying key, one
with no gate at all.

Ask of every asserted capability: does the thing exist, is it enforced, has it ever
run. Those are three separate questions and documents routinely answer the first
and imply the other two.

## What not to do

Do not invent facts only the subject holds. Leave named placeholders where a
month, a figure or a name belongs, and add a check that fails if a placeholder
reaches a submitted document.

Do not soften a claim that failed. Remove it, and put in its place whatever is both
true and useful - in one case a record of publicly withdrawn submissions proved a
stronger credential than the score it replaced.

Do not treat a checker's clean run as evidence until its negative controls fire.
