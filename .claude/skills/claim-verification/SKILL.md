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

## Compute the sanity range before running the tool, not after reading its output

A path tracer given a netlist whose sequential cells it could not recognise walked straight
through them and reported 5,208 levels of logic depth. It was caught only because the number
was absurd. The same misconfiguration producing a figure three times the truth would have
been quoted without question.

So before running a measurement, write down the range the answer must fall in and why - here,
two multipliers plus a tree, so twenty-something. A tool that partly does not understand its
input returns a plausible-shaped wrong answer, and a range computed in advance is the only
thing that catches the plausible ones.

## Keep a register of constraints with their status, not just their values

Eleven constraints had been checked across this work and never appeared in one list. That
absence caused three reversals, each one a constraint written down in a source and not in the
project.

A register with a status column - binds, slack, unchecked - does something a set of findings
cannot: it makes the unchecked ones visible as a list rather than as an absence. Six were
named the moment the register was written, and one of them is a security property whose
reasoning had been inherited rather than reproduced.

Write the register early. The value is not the constraints you have checked; it is the row
you have to leave blank.

## When a method produces one implausible output, distrust the whole extraction

An estimate was built from a standard-cell library, and one number it produced - the leakage -
came out orders of magnitude too small. The dynamic figure from the same extraction was used
anyway, with a note that the leakage looked wrong.

That was the wrong response. An implausible output is evidence about the method, not about one
field. Recomputing through a different part of the same library gave agreement within twenty
percent, which validated the dynamic figure and the units interpretation together.

So when one output of a derivation fails a sanity check, find a second route to a different
output of the same derivation. Either it agrees and the anomaly is local, or it does not and
you have found something larger than the field you noticed.

## Measure the proxy you can when the instrument you want is absent

No static timing analyser was available, so nothing had been checked about timing across
thirteen designs for many loops. Logic depth was available from the synthesiser the whole
time, and depth times a per-level delay from the library brackets the clock well enough to
show the constraint is slack by an order of magnitude.

A proxy with its limits stated beats an unchecked dimension. Name what the proxy omits - here
technology mapping and wire delay - and say what margin would be needed before the omission
matters.

## Check the constraint you never wrote down, and record it even when it is slack

A design had been sized on area across thirteen configurations and nobody had asked about
power. Checked, it turned out slack by two orders of magnitude - and that is worth writing
down rather than dropping, because the reason it went unexamined was that area was the
interesting axis, which is exactly the reason a binding constraint would also have gone
unexamined.

Three reversals in this work came from constraints that were absent rather than wrong. A
constraint found slack costs one calculation and removes a class of future surprise; the
same calculation deferred is how the next reversal arrives.

## Turn a gap into a proof of emptiness where you can

An unanswered cell in a design space was reported as blank for two loops. Enumerating the
candidate space showed exactly three options satisfied the requirements and all three were
already excluded by a measurement plus monotonicity - so the cell is empty, not unmeasured.

A gap invites another loop of searching. A proof of emptiness redirects the effort somewhere
it can succeed. When a gap persists, try to close it by exhausting the candidates rather
than by finding one more candidate.

## Discharge a caveat cheaply rather than carrying it because it probably does not matter

A borrowed constant was flagged as possibly wrong by a factor of three and carried for four
loops with the note that it probably did not change anything. Testing it at three times the
value took one calculation and changed no conclusion.

"Probably does not matter" is a prediction, and an untested prediction in a document is
indistinguishable from an unexamined risk. If the test is cheap, run it and delete the
caveat.

## Spend measurement on the blank cells, not the confident ones

Two loops running, the useful measurements were the ones aimed at regions the analysis had
no answer for. The loop that measured inside a well-covered region learned nothing; the
loops that measured a blank column and a blank edge each moved the result.

Blank cells are also where the cost of being wrong is highest, because a blank discovered
after fabrication is a project without an answer rather than a project with an expensive one.

So when choosing what to measure next, rank candidates by how much of the answer space they
would fill rather than by how interesting they look, and treat regions where you currently
have nothing as the highest priority.

## An excluded option needs a measured point plus monotonicity, not an estimate

A whole family of codes was ruled out without measuring each one: the smallest member had
been measured and already exceeded the entire budget, and the quantity increases with the
parameter that every remaining member has more of.

That is an argument rather than an extrapolation, and it is worth constructing deliberately.
One measurement plus a monotonicity claim excludes an unbounded set; an estimate per member
excludes nothing and invites re-litigation each loop.

## Prefer stating which single cell is empty to stating that something is unknown

A gap reported as "no construction above eight percent error rate at the measured entropy
density, which would need 0.98" is actionable. The same gap reported as "the error rate is
not measured" is not.

Narrow an unknown until it names a cell, a threshold, or a single missing measurement. The
work is the same; what changes is whether the next person can act on it.

## Sweep the variables that arrive together, together

Every sensitivity analysis here moved one input while holding the others at a guessed
value, and the ordering of importance that came out was an artefact of which one was held.
Two of the inputs arrive from the same measurement, so the pair is what a single experiment
returns - and mapping them together reversed the conclusion about which mattered more.

When inputs come from one source, sweep them jointly. A one-at-a-time analysis answers a
question nobody will ever be in a position to ask.

## Answer a sampling qualification by sampling where the sample is thin

A caveat about a sparse sample was answered by measuring three more points - all chosen
inside the region already believed uniform. The uniformity held there, the caveat was
declared closed, and two points from outside that region then moved the whole result.

The measurements were right; the inference was not. Densifying where you are already
confident tests almost nothing. When discharging a caveat about coverage, deliberately
sample the parts you have not looked at, especially the ones you expect to be
uninteresting.

## A sweep's granularity is part of its result

A conclusion was swept in steps of 0.02 and reported an edge at 0.87. Re-swept at 0.01, the
edge was at 0.8613 - a code had been working just below the resolution of the first sweep
and did not appear in it.

Nothing was wrong with either sweep; the first simply could not see what it did not sample.
So report the step size alongside the range, and re-sweep finer near any boundary before
quoting where it is. A boundary found at the resolution of the sweep is a boundary of the
sweep.

## Check a borrowed claim before it becomes a decision, and again after

A claim from a paper was written into a contract as the reason for a policy. It had been
taken on faith, and the paper demonstrates it on a construction with a component this
project does not have.

Checking it cost an hour. The claim survived - the mechanism generalises even though the
example does not - but it might not have, and by then it was already load-bearing in code.

When a borrowed claim is about to determine a decision, verify it on your own
configuration rather than on the source's. And when demonstrating it, be explicit about
whether you have shown the mechanism or measured the quantity: showing that bits move is
not the same as showing how much is lost.

## Answer your own qualifications

A result was published with a caveat that its shape might be an artefact of a sparse
sample. That caveat was honest and it was also a task, and caveats that are never
discharged accumulate into a document nobody can act on.

Densifying the sample took one loop and the shape survived. Track your own qualifications
as work, and close them by test rather than by repetition.

## Report a conclusion over a range of the weakest input, not at a point

The weakest input in a long analysis was a constant measured on someone else's process for
another purpose. Every conclusion had been stated at its value, which is stating a
conclusion at someone else's operating point.

Recomputed across the plausible range, the recommendation turned out not to move at all
over six percentage points, and then to stop entirely. That is a better answer than a
margin: a margin invites the question of how much is enough, while a flat band with a named
edge says the decision is insensitive over a wide range and says exactly where it is not.

So when one input is much weaker than the rest, sweep it and report the shape. And say
whether the edge is an edge in reality or only in what has been measured so far - those are
very different claims and they look identical in a table.

## Implement a borrowed formula rather than scaling its published outputs

Overheads from a paper had been rescaled from the 1,000-bit case it tabulates to a
2,921-bit design. The dependence runs through an inverse binomial, so rescaling was an
approximation dressed as a lookup.

Implementing the constraint took an hour and gave three things a rescaled number cannot:
figures correct for the actual size, a calibration check against every value the paper
states, and the ability to answer the next question without going back to the paper.

When a source tabulates outputs of a formula it also states, implement the formula. The
table is then a test rather than the data.

## When you correct one accounting, find the others feeding the same inequality

A distinction was drawn six loops ago between raw quantity and quantity surviving a
public leak, and the response-bit accounting was fixed. The oscillator accounting fed the
same inequality, sat one column away in the same table, and kept the original error the
whole time - asking for 128 bits of raw entropy where 128 bits of residual were needed.

At the figure in use the residual was negative: the construction yielded no key.

A correction is to a class of reasoning, not to a line. After making one, search for every
other place the same quantity is computed and check each against the corrected form.

## A wrong number that barely changes the answer is the hardest to find

The bad floor moved the area by two percent, so every review of it was a review of whether
the area looked plausible - and it did. What had changed was not the size but whether the
thing worked at all.

So when checking a derived figure, do not ask whether the result looks reasonable. Ask
what the figure is a quantity *of*, and whether that is the quantity the constraint needs.
Plausible magnitude is the disguise, not the evidence.

## Take a source's method, check its parameters

A code was adopted from a paper that chose it well - for a different primitive, a
near-full entropy density and an error rate of ten percent. This project has none of
those. The choice travelled silently with the method, and the bill arrived four loops
later as the tightest margin in the whole analysis.

Searching the space instead found a code that is smaller and carries four and a half times
the margin on the binding constraint.

So when a source supplies a method, take it. When it supplies a parameter, find the
constraints it was chosen under and compare them with yours. Every borrowed constant is a
borrowed operating point.

## Compute the table rather than looking it up, then calibrate on what you already trust

The search needed BCH parameters, and a looked-up table would have been a new unverified
input in the middle of the argument. They are computable: the parity count is the size of a
union of cyclotomic cosets.

Computing them turned a risk into a check, because every code named in the sources already
read becomes a calibration point. All four reproduced, and the script refuses to search if
any disagrees.

Prefer computing a reference table to importing one, and use the values you already trust
as the test rather than as the data.

## Spending a budget you were given is not the same as using the minimum

The inherited construction used the fewest blocks that satisfied the constraint. Using the
whole raw-bit budget instead more than doubled its margin at no cost - the budget was
already allocated and the improvement had been available from the start.

Minimum-to-satisfy is the natural way to size something and it silently discards free
margin. When a resource is already committed, check what the surplus buys before settling
for the smallest configuration that works.

## Push the derivation until the answer stops being a number

An option was left open for two loops as "cost not derived, do not guess". Deriving it
did not produce a cost. Erasures alone exceeded the code's entire correction budget at
every parameter value, and the fix the source used - an inner repetition code - is
excluded by an inequality that holds for any source whatever, because a repetition code
multiplies the code length while leaving its dimension alone.

So the option was not expensive. It did not exist, and two loops of treating it as a live
alternative had been wasted on a branch that was never reachable.

When something is deferred as "expensive, not yet costed", finish the derivation before
planning around it. Sometimes the cost is infinite, and that is a much more useful answer
than a large number - it removes a decision instead of complicating one.

## Find the number closest to its limit and name it

A long analysis accumulates inputs, and attention drifts to whichever one moved last.
Here the moving figure was the error rate and the binding figure was the entropy density:
required 0.9349, measured 0.9414, margin under a percentage point - and measured on
someone else's process for another purpose.

Every other input had margins of two to twenty times. Nobody had asked which was
tightest, because each had been introduced in a different loop and none had been compared
against the others.

So periodically compute the ratio of every input to its limit and report the smallest.
It is usually not the one being discussed, and a shortfall there often means the design
yields nothing rather than yielding less.

## A measurement typed into a document is not reproducible

Eight areas were gathered over six loops as one-off tool invocations and transcribed by
hand. Checking any of them meant reconstructing a session's shell history, and a change
of library or tool version would have gone unnoticed until it contradicted something.

The fix is a script that produces the whole table, and it must enforce the project's own
rules rather than just print - here it runs the testbenches first and refuses to print
any area if one fails, because a script that printed regardless would have quietly broken
the rule it was written to serve.

## Quote the range, not the worst member of a family

A debiasing overhead was reported as 4.4. That is one method of four in the same source,
and the least efficient; the family runs from 1.58 to 5.3. The conclusion happened to
survive - every member still failed the same constraint - but the number was wrong by up
to a factor of three and had already been published.

When a source gives a family of methods, the figure to carry is the range with the method
names attached. If a conclusion holds across the whole range, say so, because that is a
much stronger statement than the same conclusion resting on one member.

## Build the instrument so it does not embed the decision under test

The question was which oscillator pairing to use. A structure that emitted response bits
would have had a pairing wired into it, and could then only report the error rate of that
pairing - measuring through the very decision being evaluated.

Emitting raw counts instead moves every choice off the die: pairing, discard thresholds,
bias and entropy are all computed afterwards, and recomputed when the question changes.
One fabrication answers questions not yet asked.

So when designing a measurement, ask what decision it silently fixes, and push that
decision downstream of the data. And say plainly when the instrument must not ship: raw
measurements are often exactly what an attacker wants.

## Parts measured correctly can still not work together

Three stages of a decoder were synthesised and their areas quoted for five loops. Each
cell count was right. One of the stages did not work - it summed t of the t+1 coefficients
of a polynomial, so its zero test was not that polynomial's zero test. The circuit was the
right size and shape, which is exactly why measuring it in isolation could not tell.

Wiring them together and running one decode found it immediately.

So when parts are measured separately, the number that matters is not any part's - it is
whether the smallest end-to-end path produces a checkable answer. Build that path early,
even a degenerate version: here the all-zero codeword made an encoder unnecessary, because
linearity means a received word equal to the error pattern is already a valid test case.
Look for the degenerate case that removes the machinery you would otherwise have to build
first.

## A label like "not verified" is a debt, and debts come due

The two stages carried an honest note saying they were structural area probes rather than
verified decoders. That note was correct, was written deliberately, and was then quoted
around for five loops as though the caveat neutralised the risk. It did not. One of them
was broken.

Writing down that something is unverified is worth doing and is not a substitute for
verifying it. Track those notes as work items rather than as disclaimers, and treat any
number that rests on one as provisional in the arithmetic, not merely in the prose.

## Enumerate the constraint set before optimising against it

Three loops running, a recommendation was made and withdrawn. Each measurement was
correct and each recommendation was wrong, because the constraint set was incomplete
three times. Area only, so the smallest option won. Then the error target arrived and
killed it. Then the leakage bound arrived and killed the replacement.

Nothing about measuring more carefully would have caught any of it. What caught it was
reading the design rule the field actually uses - which each time was stated plainly in
a paper, as a rule rather than a result, in a sentence that was not the paper's
headline.

So before optimising, write the constraint list down and go looking for the ones not on
it. Ask what the field's own selection rule is and why, because a rule encodes
constraints that results do not. And when a recommendation reverses direction twice,
suspect the list rather than the arithmetic.

## Constraints that pull opposite ways are the ones most often half-counted

Leakage rewards a high code rate. Error tolerance rewards a low one. Every conclusion
this project reached about codes was drawn with one of those in view, and each time the
missing one pointed the other way.

That is not coincidence. When two constraints oppose, optimising against either alone
produces a confident answer at the wrong extreme, and the answer looks better the more
carefully it is computed. Whenever an analysis lands hard at one end of a range, look
for the constraint that would push back.

## Separate what was measured from what was recommended when reporting a reversal

Three recommendations were withdrawn and no measurement was. Saying "the conclusion was
wrong" would have implied the numbers were, and they were not - they were correct
measurements of the wrong configuration, then of a differently wrong one.

When reporting a reversal, say which artefacts survived it. It tells the reader what
they can still rely on, and it keeps the failure located where it belongs: in the
framing, not in the instruments.

## When you fix a conflation, check you have not made another one

The correction that most needs this rule was itself a correction. A pair count was
being used as an entropy count; replacing it with the ordering bound looked like the
fix, and shipped. It was not: the requirement it enforced - that ordering entropy
exceed the number of bits a decoder consumes - was not a requirement at all. Decoders
consume positions and do not care whether they are independent; extractors need
min-entropy and are the only place independence matters. Two constraints, and both
versions of the analysis had one.

The tell was available and ignored: the replacement produced a number inside the range
the correct framing gives, so nothing looked wrong. A plausible number is the normal
appearance of a wrong derivation. After fixing a conflation, write down each constraint
as a separate line with its own units, and check that every quantity appears on the
line where it belongs.

## Prefer a measured rate to a derived bound, and say which arrangement it came from

An ordering bound said 3,875 bits from 512 oscillators. Silicon measured 241. The bound
was correct and useless - a factor of sixteen above what extraction achieves.

Worse, the measured rate does not transfer freely: the same authors show two published
entropy figures from the same raw data disagreeing widely because one compares adjacent
elements and the other distant ones, with layout patterns doing the work. So a measured
rate carries its arrangement with it, and quoting it outside that arrangement is the
same error as quoting a bound.

When both a bound and a measurement exist, report the measurement and name its
conditions. When only a bound exists, say so rather than treating it as a design figure.

## An average entropy figure does not bound guessing effort

241 of 256 bits reads as almost full. The same dataset has per-bit bias reaching plus or
minus 0.4, which means keys are not equiprobable and an attacker searches in descending
order of probability rather than uniformly.

So average entropy sizes a design and does not size an attack. Any security level
claimed in bits needs min-entropy and a bias measurement, and neither follows from an
average. If only the average exists, claim no security level.

## Record negative results from new instruments

A new check was run backwards over 79 revisions of 18 documents on the reasoning that a
class of error rarely occurs once. It found only the one instance already known. That is
worth writing down: it stops the sweep being repeated in hope, and it tells the next
reader that the check earns its place prospectively rather than by clearing a backlog.

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
