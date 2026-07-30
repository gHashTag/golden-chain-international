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

## An estimate that extrapolates from a neighbour inherits its assumptions

The rule that produced the largest correction so far. Two of a decoder's three stages
were measured; the third was budgeted as comparable to them, and measured nearly three
times larger. The two measured stages multiply by compile-time constants, which fold
into XOR trees. The third multiplies two runtime values. The estimate had silently
assumed the same kind of arithmetic.

So when sizing an unbuilt block from a built one, name the property being carried
across and check that it holds. "Similar block, similar area" is not a measurement; it
is a claim about what the blocks have in common, and that claim is the thing to test.

## Check the configuration is admissible before measuring it carefully

The strongest form of the rule below, and it cost five loops. An error-correcting code
was sized repeatedly, with increasing precision, and never once checked against the
error rate it had to survive. It does not survive it. The measurements were correct and
the configuration was inadmissible, which no amount of measurement precision reveals.

So for anything being characterised, write down its requirement first and check the
candidate meets it. A careful measurement of an inadmissible configuration reads
exactly like a useful result, and the more careful the measurement, the more convincing
the wrong answer.

## A ratio between two parts is not a ratio between two designs

Reported a factor of 19.5 between two options, then found it was 4.4 once the rest of
each design was counted - the smaller part paid for itself by making a different part
six times larger. The direction of the conclusion held; the number did not, and it had
already gone into a merged document and a pull request by then.

Before quoting a ratio, name what is inside each side of it. If the two sides are
subsystems rather than whole designs, say so in the same sentence as the number.

## Combinatorial counts are usually not entropy counts

A bank of R elements compared pairwise offers R(R-1)/2 pairs, and that was used as a
count of independent bits. Comparison is transitive, so R elements carry an ordering:
log2(R!) bits, not R(R-1)/2. At R=614 that is 4,807 against 188,191, a factor of 39.

The flaw was not that the pairs might be correlated on some particular process - it was
that they are provably dependent for every process. When a count of configurations is
being used as a count of information, look for the structure that makes configurations
predictable from each other, and expect to find one.

## Before sizing the thing, check it is the right thing

Stronger than the rule above, and it arrived immediately after it. The measurement was
correct and the subject was wrong: an area budget built around one error-correcting
code, when the standard reference on that exact problem discards that code on area
grounds and recommends another that measures nineteen times smaller.

A well-verified measurement of the wrong configuration reads exactly like a
well-verified measurement. Nothing internal to it signals the error - the testbenches
pass, the negative controls fail, the numbers reconcile. The only thing that catches it
is reading what the field already decided, and reading the paper rather than its
abstract: the sentence that mattered here was a parenthetical explaining why they did
not implement the obvious choice.

So for any block being sized, ask first whether the literature has already chosen
differently, and go looking for the reason rather than the recommendation.

## A derived column is a claim, and unchecked claims drift

A percentage column in a research table was high by a consistent factor of about 1.72
across all four of its rows, against a denominator that could not be reconstructed from
the document. The two columns beside it were correct and self-consistent.

The consistency checker verified ledger counts against the ledger table and quoted
figures against their sources, and did not verify that a derived column followed from
its neighbours. Anything computed from other numbers in the same document should be
recomputed by whatever checks that document, or it will drift and nothing will notice.

## Enumerate, then filter, then fetch

When an index cannot be trusted, the replacement is not a better query - it is a
listing. File trees pulled through the API for six repositories came to just over
forty thousand paths; filtering those by name for the subject, then fetching the
handful of candidates, found a model the index had never surfaced under five
different phrasings.

The order matters. Enumerate first, because a listing is complete in a way a query
is not. Filter on paths, because names are cheap and contents are not. Fetch last,
and only the candidates.

This also gives absence a form worth stating: not "five searches returned nothing"
but "forty thousand paths were listed, filtered on these terms, and the candidates
read." The second is a claim someone else can repeat.

## When the index fails, fetch the files

An account-wide code search returned nothing for a phrase that was demonstrably
present in a file in that account - the phrase had been read directly minutes
earlier. The index did not cover it.

So a search that returns nothing has two readings, and they are not
distinguishable from the result: the thing is absent, or the instrument does not
reach it. **Before reporting absence from an index, confirm the index can find
something you know is there.** If it cannot, enumerate and fetch instead - fifteen
files fetched and grepped locally took one command and gave an answer the index
could not.

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

## Audit the sections nobody audits

Verification concentrates where numbers are, so the sections that carry
architecture rather than figures get read and not checked. Three findings arrived in
one pass over the two sections of an application that had never been examined - after
forty-odd passes over the rest.

They were: a hardware component asserted in the product description that the
project's own working notes say is not fitted; a statement that two radios have never
been powered simultaneously, which meant no two-party radio test had ever been
possible and made a set of simulation-level rows unrunnable rather than merely
unrun; and a market claim of a single supplier in a market with at least four,
addressed to a committee that buys in that market.

None of the three needed a tool. Two came from grepping the subject's own working
files for the component names in its own prose. The third came from one search.

**Take the prose apart into claims and check each one, especially where there is no
number to attract attention.** A sentence describing what a thing is made of is as
checkable as a measurement, and it is checked far less often.

Note also where the subject is more honest internally than externally. In all three
cases the working notes were candid - GPS marked as unavailable, the single-radio
limitation written down by its own author, a rate constant labelled a guess. The
defect was in what reached the outside, not in what was known.

## Ask how far away, not only whether

A conclusion that a capability is unreachable on current hardware was correct and
incomplete. It said the fix required a funded custom fabrication run. Checking the
open process the project already used showed the primitive had been fabricated there
already, at the scale of a shuttle tile, in a programme the subject had already
submitted to. The blocker was real; the distance was wrong by an order of magnitude
in cost and schedule.

**A finding of the form "X is impossible here" should always be followed by "and
what is the cheapest thing that makes it possible".** The second question changes
what the finding means to whoever has to act on it, and it is often answerable from
public artefacts.

When the answer arrives, carry the limitations across with the same weight as the
opportunity - here, eight bits of response, no measured uniqueness or reliability,
and drift with temperature that the author documents. A nearer path reported without
its limits is worse than no path, because it will be planned against.

## Do the arithmetic before accepting a limit

A finding said a capability would not fit in the available area, scaled from a
published implementation. Scaling was the wrong operation: the implementation
replicated shared apparatus once per output bit. Sharing it moved the answer from
thirty-two units of area to three, against a limit of sixteen.

**When a limit is asserted, find out whether it is dimensional or architectural.**
Those need different answers and get confused constantly. Public artefacts usually
carry enough to tell them apart - here a configuration file declaring tile count and
a README describing the block structure were sufficient.

Label every estimate as an estimate, and say what would settle it. An area budget
built from cell-area guesses is a decision aid, not a result; the thing that settles
it is synthesis.

Then go and settle it. Naming what would replace an estimate is the easy half; the
estimates here were replaced by cloning the published design and running it through
a synthesiser against the real cell library, which took one download and one command.
The measured numbers came out within a few percent of the guesses and the conclusion
did not move - which is worth recording precisely because most checks in this work
found errors. A check that confirms is still a check, and reporting the agreement is
what makes the disagreements credible.

Keep track of which inputs remain unmeasured after the pass, and then measure that
one too. Here one survived a pass - roughly half the total by the estimate's own
reckoning - and measuring it moved the answer by nearly a factor of two, because the
estimate had been low. The inputs that survive a measurement pass are selected for
being hard to measure, which is exactly why they are where the error lives.

When measuring something you have to build, build only the part you can build
correctly, and say which part that is. Two of three decoder stages were written and
synthesised; the third was left out rather than written unverified in one pass and
reported as measured. A measured lower bound with a named gap is worth more than a
complete number nobody should trust.

Sweep the parameter rather than picking one. Measuring the decoder at four correction
strengths showed the area is linear in it, which turned a single number into a
relationship - and the relationship revealed that the unmeasured physical error rate
sizes the largest block on the chip. A single point would have hidden that.

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

## Revise on the same evidence you would have demanded

An entry was lowered from high to medium after inspecting one repository, where the
status table turned out to be careful. It was the wrong repository: a second one
carried a dated fabrication commitment in a public README, which is exactly what the
entry had originally alleged. The revision was right about the file and wrong about
the subject.

**A downgrade needs the same coverage a finding does.** It is easy to be strict when
raising a concern and loose when withdrawing one, because withdrawal feels like
humility. It is not - an entry revised on partial inspection is not revised, it is
guessed at with more confidence.

That entry went on to be rated high, medium, high, and medium again. The final
lowering is the only one that stands, because it came from fetching fifteen files and
searching them rather than from inspecting one and generalising. Two lessons sit in
the oscillation. A rating that moves on each new sample is telling you the sample is
too small, not that the subject is ambiguous. And when the systematic pass finally
runs, it can settle a finding in the same direction an unjustified guess had gone -
which does not retroactively justify the guess.

**A repeated correction is a finding about method, not about the subject.** The same
error - inspect one, conclude about all - appeared as a family inference about a chip,
as a downgrade on one repository, and as an absence reported from one query. Three
different clothes, one mistake. When a class of error recurs, stop fixing instances
and write the rule.

Watch for verbs that survive a correction. Here the distinction between "produced"
and "settled" had been carefully drawn and defended twice, and both sides of it were
wrong: stub code that compiles is neither. Getting a distinction right does not make
either of its terms true.

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
