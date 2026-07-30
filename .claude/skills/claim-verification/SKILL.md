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

## "Reproducible" means reproducible somewhere else

A script written so that anyone could reproduce every figure in one command failed all twenty-one of
its checks the first time it ran on a Linux machine - a BSD-only spelling of mktemp that GNU
coreutils rejects. Nothing was wrong with what it tested. It had simply only ever run on the machine
that wrote it, for eighty loops, and had no way to say so.

The first run on foreign ground is the measurement. Until then, "reproducible" is a property of your
laptop.

## A rule enforced by memory is a rule that has already failed twice

A project rule - no area is quoted for a circuit that has not been exercised - had a script behind
it that ran when somebody remembered. In five loops it was violated twice: once by a testbench that
existed but was not wired into the script, once by a component that had no testbench at all.

The rule was good and the enforcement was a habit. Move the part that a machine can run to where the
machine runs it, even when that means splitting the tool so the cheap half can go first. Half a
guard on every change beats a whole guard on the changes you remember.

## When a model says a mechanism is limited, check what your own hardware already emits

A model concluded that a ranking step could only reach certain discrete operating points, because it
assumed the ranking saw one bit per measurement. The project's own instrument - built four loops
earlier, for an unrelated reason - emits a full count per measurement, which makes the ranking
continuous and an order of magnitude better.

The limit was real for the assumed architecture and absent from the built one. Nobody had compared
the two, because the model and the instrument lived in different files and were written for
different questions.

So when a model reports a mechanism's limit, go and read what the mechanism actually produces in your
own tree before designing around the limit. And when the answer improves things, look immediately for
what it costs elsewhere - here, exposing counts is precisely what the instrument's own header says a
part holding a secret must never do.

## Quantisation by arithmetic is obvious; quantisation by architecture hides

Five continuous-looking parameters, four quantised by arithmetic - integers, odd counts, pair counts,
powers of two - all four handled correctly without anyone thinking about it, because integers are
visibly integers.

The fifth was quantised by a choice of architecture, and it looked perfectly continuous in the model
for five loops. That is the kind to hunt: a parameter whose granularity comes from *which component
does the work*, not from the algebra.

## Ask whether the mechanism can reach the operating point you chose

A design specified "keep the most reliable forty percent". The mechanism that does the keeping ranks
by a majority vote over N reads, so the fractions it can produce are the discrete vote margins - and
the deepest is the share that never voted unanimously. Forty percent was not among them at any read
count in range. Everything below that floor is tie-breaking at random among positions the ranking
cannot separate.

A continuous parameter in a model is often quantised by the thing that implements it. Before adopting
an operating point, enumerate what the mechanism can actually produce and pick from that list - and
notice which quantity is really the free one. Here it was the read count, with the fraction following
from it, and stating it the other way round specified a design that cannot be built.

The good news is that writing the achievable counterpart of a bound is what surfaced this, one loop
after adopting the unreachable point. Sibling functions earn their keep immediately.

## A bound should carry its direction in its name

A function returning the error rate under *perfect* ranking was called `selected_ber`, with the
optimism documented in its docstring and measured separately in the same file. Two loops later
another analysis called it and reported the result as the design's actual rate. The real figure was a
tenth of the way from that number to failure.

Downstream reads the name and the number, never the docstring. `selected_ber_ideal` would have made
the caller ask where the achievable one lives.

Name bounds as bounds - `_ideal`, `_bound`, `_optimistic` - and when you write one, write the
achievable counterpart next to it even if nothing calls it yet.

## An artefact that records what to revisit is not a revisit

A register gained a column naming, for each constraint, the decisions taken against it - precisely so
that a constraint moving would point at the work to redo. It was then carried for six loops without
anyone reading it, and the first sweep found a safety margin of 1.10 where the documents claimed
comfort.

The same shape had already happened twice in the same project: a register that went stale for three
loops, and advisory notes nobody read for dozens. Writing down what to check is the easy half and it
feels like the whole thing.

If a document exists to trigger periodic work, the trigger has to live somewhere that fires - a
checklist step, a check that fails, a scheduled sweep with an owner. A column that waits to be read
will be read the loop after it mattered.

## One bad comparison is not a general law

A single failing run - every figure out by a few percent - produced the conclusion "these numbers are
toolchain-dependent by up to seven percent". Measured against a current build instead of a
years-old distribution package, nineteen of twenty-two were *identical* and the rest differed by a
quarter of a percent.

The first conclusion was true of the comparison that produced it and false as a general claim, and
the gap between those cost a check that was fifty times looser than it needed to be.

When one comparison surprises you, get a second before generalising - and when you do generalise,
name the comparison the number came from, so the next person can see how narrow it was.

## Turn "it should be fine" into the number it would have to beat

An argument said a cheaper component shares the mechanism of an expensive one, so it should satisfy
the constraint. That is unfalsifiable as stated, and it was pointing in the direction the design
wanted.

Working out where the requirement sits between the two known arrangements turned it into: the cheap
one qualifies only if it captures 96.4 percent of the expensive one's benefit. Same evidence, and now
someone can test it.

A mechanism argument is a hypothesis. The useful form of it is the threshold that would confirm or
kill it, stated before anyone runs the experiment.

## A control must not share a surface with its subject

A control fed a checker a fake commit message naming a nonexistent issue number, expecting the check
to object. It did not - because the probe number was written as a literal in the workflow file, and
the workflow file was part of the diff the check reads. The check found the number it was told to
look for, in the instructions telling it to look.

The control was right about the check and wrong about the world: writing the probe put the probe's
evidence into the evidence.

Before trusting a control, ask what the subject can see. If it reads files, your control's text is a
file. If it reads a directory, your scratch copy is in that directory. Assemble probe values at run
time rather than writing them down, and keep the control's working material outside whatever the
subject scans.

## An observation about something you do not control is still a number you can pin

A check watched an artefact in another repository, so a failure would have demanded a fix nobody on
this side could make. It emitted a note instead - and the note was read past on every run for as long
as it existed.

The third option is a declared count: state how many outstanding observations there are, check it
every run, pass while it matches and fail when it moves. That is exactly when a human is needed, and
it needs no authority over the thing being watched.

## "Skips rather than failing" in a docstring is a defect describing itself

A checker fetched its input from elsewhere and, when the fetch failed, printed "skipped" and returned
success - with the docstring praising this so the build would not depend on another repository.

A green tick that read nothing is the thing to hunt, and here it was announced in the file's own
documentation and survived every reading of that file. Make the skip something a caller asks for
explicitly, and let the default be failure. If a build genuinely must not depend on a fetch, that is a
decision to write at the call site where someone can see it, not a default buried in a library.

## Check the checker's inputs, not just its logic

A reference-resolving check was given six documents and not the research directory - so the file
carrying most of a project's reasoning, which names a script on nearly every page, had never had one
reference checked. Its pattern was also restricted to the one file extension those documents almost
never reference.

The logic was correct. The inputs were wrong, and nothing in a passing run distinguishes "checked and
clean" from "checked the wrong thing". When you audit a check, read what it is *given* and what it
*matches* before reading what it does - and write a control that breaks a real instance in a real
file, because a control on a file the check never opens passes for the same reason the check does.

## A control can test nothing, and it looks exactly like a check that does not work

Python's import cache is keyed on a source file's modification time and size. Swap a value for one of
the same length within the same second - `0.65` for `0.23`, `24,659` for `24,700` - and the mutated
run reads the *original* value. The control reports no failure, and the honest reading of that, "the
check is broken", is wrong.

Equal-length swaps are what a careful person writes. So run controls through a harness that verifies
the anchor exists, disables bytecode caching, restores by content and verifies the restoration by
hash - and give the harness a self-test that reproduces the hazard, so its reason is demonstrated
rather than remembered.

The general form: when a negative result surprises you, suspect the instrument before the subject.
A control that does not fire is a claim about your test rig first and about the code second.

## A default that fills in a missing measurement is worse than a crash

A budget line read `TABLE.get(key, max(TABLE.values()))`. It let a search recommend a construction
whose component had never been measured, substituting the largest measured one - silently, with no
marker in the output.

A missing measurement should stop the search, not be estimated by the nearest number to hand.
`dict.get` with a default is where that happens most often, because it reads as defensive
programming. In a costing model it is the opposite: it converts "we do not know" into a number that
looks like the others.

## A measurement carries its instrument, including the version of the program

A body of work recorded the conditions behind every borrowed number - pairing distance, temperature,
duty cycle, process node - and never recorded which build of the synthesis tool produced its own. The
first run on another machine reported every declared figure as wrong, by a few percent in both
directions, because a different release maps to different cells.

Nothing was wrong with the circuits. "These figures reproduce" had silently meant "on this laptop".

Declare the tool version next to the numbers it produced, and have the checker verify it *before*
comparing anything - so a version difference arrives as one accurate sentence instead of twenty-two
false ones.

## A regex over prose finds the first thing shaped like the answer

Binding a figure with the pattern "to N of sixteen" reported 15, because "13 to 15 of sixteen"
appeared earlier in the file than the sentence being checked. The check was right to fire and wrong
about what it had found.

Anchor a prose pattern on the sentence that makes the claim, not on the units it ends in. Units
repeat; claims do not. And when a binding fails, read what it matched before believing what it says -
the failure may be in the pattern rather than in the document.

## The cheapest version of a mechanism may already be in the library

A design carried an extra cost to satisfy a constraint, taken from a paper's custom cell. The
mechanism that cell implements - hold this node away from the stress state while idle - turned out to
be exactly what a two-input gate already in the standard-cell library does, at identical area.

Before costing a mechanism from someone's transistor-level design, ask what the mechanism *is* in one
sentence, then look for that sentence in the cell library you are already using. But do not take the
saving on an argument: the published number belongs to the published circuit, and swapping the
circuit means the number has to be re-established. Record the option and what would settle it.

## Count by execution, not by appearance

A script's testbench count was taken by matching lines in its source and came out one too high - the
function definition line matched the same pattern as the calls. The script's own counter, incremented
inside the function, was right.

Pattern-matching over source counts what looks like the thing. A counter inside the thing counts what
ran. When both are available, the second is the measurement and the first is a guess that happens to
be usually correct - and when they disagree, that disagreement is worth more than either number.

## Bind prose figures to the model, and put a floor under how many are bound

A document row carrying an externally visible claim held sixteen numbers, four checked and twelve
written. Binding eleven more of them to the model that produces them found three stale claims on the
first run - including one describing a constraint as unchecked in the same paragraph that described
the design built to satisfy it. Prose does not notice when it contradicts itself.

Two cautions came with it. Do not bind constants that came from outside: asserting that an input
equals itself is coverage counted for its own sake. And put a floor under the count of bindings,
because the list can shrink silently, and a number that stops being checked returns to being a
sentence without anyone deciding that it should.

## The error rate tracks whether a number is executed

After two errors in the same class, every division in six models was read expecting to find more.
Five were clean; the sixth failed on a display column, not a result.

Both errors that mattered had been in prose and in a comparison written for a report - places with
no compiler, no import graph and no test. The executed parts had been kept honest by being executed.

So the response to finding an arithmetic error is not to read the arithmetic more carefully. It is
to ask which numbers in the work are never run, and move them into something that runs. Reading
harder scales with attention; a number that is computed on every check does not need any.

## A module that computes on import cannot be cross-checked

Two files reported two values for the same quantity, and nothing compared them - because importing
one of them executed three tables of output. Anything that wants to call a function in it has to run
the whole program first, so nothing ever did.

Put the driver under a main guard from the start. The cost is one line and the benefit is that the
module becomes an importable definition rather than a script, which is the difference between a
figure that can be cross-checked and a figure that has to be trusted.

## When a disposition fails twice, replace it with a check that runs

A rule that said "be careful where the answer is convenient" was in the skill file when the same
error was made again, three loops later. The rule was right and unusable: it names a mood.

The replacement is a script that requires every ratio in the inputs file to declare its numerator
and denominator units, and fails otherwise. It cannot tell whether the units are correct - it forces
the claim into the open, which was enough to surface a width ratio being applied to an area.

The general move: when you catch yourself writing the same lesson a second time, stop writing
lessons. Ask what mechanical artefact would have made that instance impossible to commit, and build
that instead. A disposition scales with attention; a check does not need any.

## Sweep the assumption you cannot verify, and quote the arm that is not convenient

A calculation rested on an unverified step about how a quantity scales with time. Rather than pick
the plausible value, both plausible forms were computed - and one of them made the answer twice as
favourable.

Report both, and state the requirement against the *unfavourable* arm. The favourable one is a
sensitivity, not a result. If the conclusion survives the unfavourable arm you have something; if it
only survives the favourable one you have a question, and saying so is the finding.

## Take a ratio in the units the mechanism operates in

A requirement was expressed as "the residual may be 28 percent of the ten-year value", computed from
the two flip rates. The flip rate is a saturating function of the parameter that actually
accumulates, so in that parameter the residual was 18.3 percent - and the error ran in the direction
that made the requirement look reachable.

When a model carries a parameter and you observe a saturating function of it, the parameter is the
unit for every ratio, every margin and every "fraction remaining". The observable is for reporting.

This is the mechanical form of "verify twice where the answer is convenient", written after that
disposition failed to prevent the same error three loops later. A rule you have recorded is not a
rule you have applied; a rule that names the specific check is easier to apply than one that names a
mood.

## A summary saying there is nothing to read is not evidence there is nothing to read

A fetched summary reported that a paper contained no discussion of the topic being searched for, and
listed the absent subtopics. The PDF had twenty-one mentions of it, a subsection with that heading,
and the measured result the next day's work was built on.

A wrong quotation gets caught by the next reader. A wrong "there is nothing here" ends the search -
and it is the cheapest claim in the world to check, because the file is already on disk. Grep before
accepting an absence, always.

## Bracket an estimate you cannot replace

One figure in a design had neither a measurement nor a synthesis behind it, and the thing it
estimated could not be measured with the tools at hand. Instead of leaving it unbounded, it was
bracketed against the nearest measurable analogue - which showed the estimate was conservative by
eleven to forty percent.

The bracket did not produce a better number and was not meant to. It produced the *direction of the
error*, which is what separates an approximation you can build on from one you can only hope about.
When you cannot measure the thing, measure something that brackets it and say which side you are on.

## The unchecked step is likeliest where the unchecked answer is convenient

A published figure appeared to kill a design. The write-up argued that the figure's operating point
did not match this one, so it was probably pessimistic here - and the source contradicted that
directly, in a passage sitting in the same extracted file.

The argument was not checked because it was the answer the design wanted. Nothing else in that
session went unverified.

So: when a step would rescue your conclusion, that is the step to verify twice, and the cheapest
check is usually to search the source you already have for the thing you are about to assert.

## A figure from a paper carries the operating point it was measured at

A published ten-year degradation figure looked like it killed a design outright. It was measured at
23 percent activation time; the design in question runs its source once at power-up, orders of
magnitude below that, and the paper says explicitly that lower activation reduces the number.

The figure was neither wrong nor applicable. What it establishes is the shape and the direction, and
what it cannot establish is the value here - which the paper's own sweep would have given, for the
other device.

Take the conditions with the number, every time, and say plainly which of them your case matches.
The useful output is often not a verdict but a requirement: "the ten-year flip rate must be at or
below 9.2 percent" is checkable by whoever picks the part, and "the paper says 32 percent" is not.

## Ranking by a signal buys little when the perturbation is as large as the signal

Selecting the most reliable positions cut a noise-driven error rate by a factor of eight and an
aging-driven one by a tenth of that. Same mechanism, same selection, wildly different return -
because the noise was a fifth of the manufacturing spread and the ten-year aging differential was
larger than it.

Before assuming a mitigation transfers to a new perturbation, compare the perturbation to the
quantity the mitigation sorts by. If they are the same size, the sort is close to random.

## Watch a new check run where it will live, not only where you wrote it

A check was replayed against its motivating failure locally, kept with its scope written down, and
wired into CI. Its first CI run printed "nothing to check" and exited zero: the runner's shallow
checkout of a merge commit made the range collapse, so the step passed green having read nothing.

A check has two places it can be inert - the logic and the harness that invokes it - and only the
first is testable from your shell. Read the first run's log, not the status dot, and make an empty
input a failure rather than a polite exit. "Nothing to check" is a result a green tick cannot
distinguish from "checked and fine".

## Run a new check against the failure that motivated it, before trusting it

A check was written to close a specific past failure. Run against the two commits that produced
that failure, it passed both - the thing that went missing was not the thing the check looks at.

Without that step it would have gone into CI looking like coverage, and the next loop would have
recorded the class as closed. A check that cannot see its own motivating case is worse than none,
because it converts an open problem into a solved-looking one.

So: replay the historical failure through the new check first. If it does not fire, either
reformulate it or keep it with its scope written down - and find the real fix elsewhere.

## A heuristic arm in a verification tool is worse than an absent one

One arm of that check needed a list of verbs to tell "I changed X" from "X is where this lives".
It would have worked often and failed quietly the rest of the time.

An absent check leaves you looking. A heuristic one stops you looking and reports a number. Cut the
arm rather than shipping partial coverage that reads as full.

## Never put a destructive command inside a test control

A control committed and reset to clean up after itself, and the reset deleted the untracked file
being tested - the work of the previous half hour.

Controls run on the thing you are least willing to lose, which is exactly when a hard reset, a
checkout of a modified file, or a branch delete is the wrong instrument. Substitute in memory,
copy to a scratch path, restore from a backup you made first. The one-line version: never let a
cleanup step outrank the thing it is cleaning up after.

## An anchored edit must assert its anchor

Two loops of edits were reported as made and were never in the file: a string replacement whose
anchor did not exist returns the string unchanged, so the edit "succeeded", the commit message
described the rows, and the diff did not contain them.

Assert the anchor before replacing, every time. A silent no-op is worse than an error, because the
error stops you and the no-op writes a commit message about work that does not exist.

The deeper gap: checks compare documents against each other and against the model, and nothing
compares a commit message against its diff. Until something does, the assert is the only guard.

## An advisory that never escalates gets read as furniture

The same failure was reported by a check on both occasions, as a *note* rather than a failure, in a
list that grew by two entries a loop for four loops. It was true, it was visible, and it was
scrolled past every time.

If a note is still true after two runs, it is not a note. Either promote it to a failure or delete
it - a permanent advisory trains you to skip the section it lives in, which costs more than the
thing it was warning about.

## A check pinned to an old model is worse than no check

A script recomputed a headline from the design as it stood eight loops earlier. The document stated
that figure, the script recomputed that figure, and they agreed - because both were anchored to the
same superseded construction. The check reported green while the document described a design that
had been replaced four times.

No check leaves a document unverified, which you know. A stale check tells you it is verified.

When the thing under test moves, the check moves with it or it stops being one. Ask, of every green
check: what operating point is this computing, and is it the one we are in.

## A check that runs inside the assumption it is testing proves nothing

A model asserted that a position's reliability says nothing about its value, "checked below rather
than assumed". The check sampled from a distribution whose symmetry was what made the claim true. It
reported the expected answer because the sampler had been told to produce it.

The tell is that the check and the assumption share a parameter. Before trusting one, ask which
input would have to be wrong for the check to fail - and if the answer is "the one the assumption
sets", the check is decoration.

The fix is to vary that parameter to its measured value rather than its convenient one. Here the
measured source had a bias of 0.5207 and the model used 0.5000, and the difference was a live defect
in the design of the previous loop.

## Record the condition a later decision might change, not the one that already burned you

A measured input was recorded with the arrangement it was taken under, because an earlier loop had
been caught by that. It was not recorded as measured before a filtering step the design later added,
because at the time there was no filtering step.

Provenance notes capture the conditions someone thought to write down. The conditions that matter
are the ones a future decision changes. When you add a stage that transforms the data an input
describes, go back and ask what the input still describes.

## "Gates green" is a claim about which gates

A loop reported gates green having run the fast check and not the slow one. The slow one was the
only one that would have fired, and it fired a loop later on work already merged.

Name the gates you ran, in the report and in the commit. A summary that says "green" without a list
is a summary of the checks you remembered.

## When a constraint moves, revisit the decisions that were taken against it

Sixty percent of a design came off in two loops, and neither change needed a new technique, a new
source, or a new constraint. Both were decisions that had been correct at the operating point where
they were made, in a design whose operating point had since moved.

A register of constraints does not catch this. It records what each constraint is and whether it
binds; it does not record which decisions rested on it. So when a constraint changes - and in this
work several changed completely - nothing points at what to redo.

Keep, for each constraint, the list of decisions taken against it. When the constraint moves, that
list is the work queue. Without it the decisions stay correct-as-of-a-date and nobody notices the
date.

## Your measured set encodes the operating point you had when you built it

A search over measured candidates kept returning the same answer, and the answer was the best of the
wrong candidates: every measured option had been chosen when a constraint was five times tighter, so
the set contained nothing suited to the current operating point.

The search was not wrong and neither were the measurements. The candidate set was a fossil.

So when the operating point moves, ask what the *candidate set* was assembled for before trusting a
search over it - and expect that the right answer is something you have not measured, precisely
because you had no reason to measure it before.

## Sharing pays only when the replicated unit is expensive

One component compressed by 62 percent when its replicated multipliers were shared. The same trade
applied to the next component made it 47 percent larger.

The difference is not how much of each is logic - the component that failed was 65 percent logic and
the one that succeeded was 84, which looks like the same story. The difference is what was being
replicated. The successful case replicated *general* multipliers, so sharing removed sixty-four of
sixty-six identical units. The failing case replicated *constant* multipliers - fixed XOR trees, cheap
- and replaced them with one general multiplier plus the addressing to index twenty-two entries,
which cost more than the arithmetic it removed.

So before serialising, compare the cost of one replicated unit against the shared unit plus its
addressing. Replicating something cheap is already the efficient arrangement, and the logic share
will not tell you which case you are in.

## Write down why you expect a result before measuring it

The header for the failing optimisation predicted a smaller saving, for exactly the right reason - a
general multiplier costs more than the constant one it replaces - and got the sign wrong.

Because the reason was written before the measurement, the negative result was immediately
interpretable: the stated mechanism was correct and its magnitude had been underestimated. Without
it, a 47 percent increase would have looked like a bug in the implementation, and the natural next
move would have been to debug a correct circuit.

## Act on the observation you just wrote down

One loop after recording that the largest component had absorbed no optimisation while the smallest
had absorbed six loops of it, acting on that observation removed thirty-nine percent of the design in
a single change.

Nothing new was learned. The technique had been named in the component's own header from the first
loop, and the property that made it free had been sitting in the constraint register marked slack.
Both were written down and neither was used.

So when a loop produces an observation about where the effort should go, the next loop is that -
not the next item on the list that was drawn up before the observation. An insight recorded and not
acted on is indistinguishable from one never had.

## Verify a rewrite differentially against the version it replaces

A rewritten module was checked by feeding both it and the original the same inputs and requiring the
outputs to match, rather than by re-deriving the expected answers.

That is cheaper and stronger. Cheaper because the reference already exists; stronger because the
reference has itself been verified against constructed cases and against injected faults, so the
differential test inherits all of it. It also caught a pipelining error on the first run - products
reflecting the previous cycle's operands - that reading the code would not have shown.

Keep the original in the tree afterwards. It is the test.

## Sort the budget by share before deciding where to work

A design's cost was assembled across twenty sections and never shown as one sorted table. Assembling
it took one command and showed that one component was 87 percent of the total and another, which had
absorbed six loops of optimisation, was 1.2 percent.

The work was not wasted - the small term was where the *constraints* lived, and those decided the
large one. But effort went to refining the small term while the large one sat unexamined until an
outside source forced it.

So sort by share early and re-sort whenever a component is added. Where the constraints are and where
the cost is are different questions, and only one of them is answered by the thing you happen to be
measuring.

## Decline a measured advantage when it buys an attack surface, and say so plainly

An alternative came out 0.32 of a tile cheaper, measured, with its datapath implemented and verified.
It was declined: it needs a random number source the incumbent does not, and the literature records
an attack on its helper data that was demonstrated on exactly this project's source type.

Write that down as a recommendation against the arithmetic rather than burying the measurement. A
reader who sees only the conclusion cannot tell whether the alternative was measured or dismissed,
and a later loop will re-derive it.

## Two tools disagreeing is a better check than reading more carefully

A register named `within` - a SystemVerilog sequence keyword - was accepted by the synthesiser as an
identifier and rejected by the simulator. The synthesiser reported a plausible area for a module the
simulator would not compile.

Nothing was published, because the rule here is that no area is quoted for a circuit that has not
passed a testbench. But the near-miss has the same shape as a path tracer that walked through cells it
did not recognise and returned a number that looked like a depth.

A tool that partly does not understand its input returns a plausible answer rather than an error.
Running a second tool with different strictness over the same source costs nothing and catches the
class.

## Test the property the component is for, not the property it is named after

A cryptographic primitive was implemented to price a countermeasure. Verifying it against the
standard was impossible - no test vectors in hand - so the temptation was to report the area with a
caveat and move on.

The property the countermeasure actually relies on is diffusion, not standards compliance, and that
is measurable directly: one input bit changing about half the output bits. Measuring it turned a
caveat into a result, and two injected faults confirmed the measurement could fail.

So when you cannot verify a component against its specification, find the property the design
depends on and test that instead. Then say precisely what is verified and what is not - here, a
permutation of the specified structure and cost with the required diffusion, not a permutation
checked to be the standard one.

## A control can rule out a design you were considering

The control that used an identity S-box changed exactly one output bit. That is not just a failing
test - it is the reason a linear mixer cannot do this job, since an attacker learns the key change
exactly and compensates. An LFSR-based mixer had looked like a cheaper route to the same diffusion.

Negative controls are usually read as confirming the check works. Some of them also answer a design
question, and it is worth asking of each one what it rules out beyond itself.

## Resolve the bound another agent stated for itself, and reuse its instrument

A parallel agent on the same prompt reached a conclusion and named its own limit precisely: only
one pairing was measured, and a stronger one could reverse it. Testing exactly that reversed it.

Two things made this cheap. Its bound was stated in a form that said what experiment would settle
it. And its model was already validated against a large sample, so reusing it rather than building
another meant the two results were comparable and the validation was inherited.

So when another agent - or an earlier loop - leaves an explicit bound, treat it as the highest-value
next experiment, and reuse the instrument rather than writing a second one. A second instrument
gives you two numbers to reconcile; the same instrument gives you an answer.

## Check another agent's arithmetic against its own stated conditions

A figure in a parallel agent's comparison was correct for four percent and quoted at six, which
changed a loss into a tie. Its mechanism measurements were all sound; one number had travelled from
a different operating point.

Neither agent would have caught it alone, because each reads its own figures as familiar. The check
that found it was mechanical: take each quoted number, find the condition it was derived under, and
confirm that condition is the one it is being quoted for.

That is worth doing to your own figures too, and it is easier on someone else's - which is the
argument for the parallel arrangement, against which the branch collisions are the argument.

## The taxonomy's top level is the one that matters, and it is usually one sentence

The map of framings turned out to be a single sentence in a chapter conclusion: there are two main
families, and every option examined across twelve loops was in one of them. Not a subtle
distinction buried in an appendix - the top-level split, stated plainly, in a document already
cited three loops running.

So when reading for the field's taxonomy, read the conclusions of the survey chapters first and
look specifically for how many families there are. Everything below that level is optimisation;
that level is scope.

And when you find the other family, look for its failure mode rather than its advantage. Here the
second family gets zero leakage for free and has a machine-learning attack on its helper data that
was demonstrated on exactly this project's source type. A family that is better on your binding
constraint usually pays somewhere you were not measuring.

## Find the field's comparison table before optimising, not after

Three loops running, a single table in a document already cited removed a constraint that had been
treated as a fact of the problem: first that helper data must leak, then that the leakage makes
source entropy critical, then that all errors must be corrected rather than avoided.

Each cost one hour to read and each invalidated the framing of several loops of careful work. The
measurements survived every time; the claim to have found the best design did not, because the
work compared options within a framing and never compared framings.

So the first hour of any optimisation goes to finding where the field compares whole approaches -
a survey table, a thesis chapter, a related-work section with numbers. Not to check your approach
is on the list, but to see what the other rows do not have to pay for.

## An open question may have a generic answer that makes the question unnecessary

A claim was chased for four loops: whether one construction resists a particular attack. The
answer, in the same document, was that a cheap generic countermeasure exists which makes the
attack ineffective against any construction.

Verification would have settled which option was safe. The countermeasure settles that the choice
does not matter, and it converts a research question into a missing component - which is a much
better kind of open item, because it can be built.

When a question about which option is safe stays open, look for whether the field has stopped
asking it. Sometimes the answer is a component nobody in your design has.

## Read the taxonomy before optimising within one branch of it

Twelve loops of code selection took a leakage term as a fact of the problem. One table in one
chapter listed four standard constructions with their leakage, and the oldest of them - published
in 1999, the most widely deployed in the field - does not have that term at all.

The work inside the branch was correct. All of it was conditional on a choice made early, and the
document that would have shown the choice existed was a comparison table in the standard reference
for the area.

So before optimising within an approach, find the field's own taxonomy of approaches and read the
row your choice sits in alongside the others. It is usually one table, it is usually in the
literature you have already cited, and it costs an hour against loops of conditional conclusions.

## When a constraint dissolves, say which conclusions were conditional on it rather than wrong

Removing one term withdrew six loops of sensitivity analysis, three reversals of priority, and the
figure that had been called the tightest in the work. None of it was mistaken. All of it was
conditional on a construction chosen without asking whether its leakage was avoidable.

Report that distinction explicitly. A reader who is told the conclusions were wrong will distrust
the measurements; a reader who is told they were conditional knows exactly what still holds and
what to re-derive.

## Implementing a scheme to test one claim checks several others for free

A construction was implemented to settle whether one property held. Building it confirmed three
more things that had been assumed: a code parameter, arrived at from the generator polynomial
rather than from the coset sizes that had produced it before; a structural property the scheme
requires, which had been taken on faith; and the agreement of a software model with the hardware,
since both now compute the same quantity the same way rather than sharing a transcribed number.

An implementation is a bundle of checks. When a claim is cheap to settle by building the thing,
build it and then list what else the build just verified - those are free and they are the ones
nobody would have thought to test.

## Say "out of scope" rather than "open" when a question cannot arise

An open item was recorded as undone for a loop: whether a scheme composes with a concatenated
code. It turned out the recommendation uses a single code, so the question arises only for an
alternative that a different constraint already rules out.

That is not an open question, and filing it as one invites a loop of work on an unreachable
branch. Distinguish what is unanswered from what cannot arise, and say which - the first is a
task and the second is a note.

## Ask whether a binding constraint is a property of the problem or of your choice

A bound had governed every design decision for six loops, sourced from the field's own design
rule and correctly applied. Chasing an unrelated question turned up a construction that does not
have it at all - the redundancy is masked with fresh source bits and the leakage is zero by
construction.

The bound was real. It was a property of the schemes in use, not of the task, and nobody had
asked which.

So for each binding constraint, write down whether it follows from the problem statement or from
the approach. If from the approach, the question "what would have to change for this not to bind"
has an answer, and it is worth an hour before another loop of optimising against it.

## Chasing one unverified claim is how you find the constraint you did not know about

The most consequential finding in many loops came from pursuing a single second-hand citation to
its source. The source did not settle that question and its neighbouring chapter overturned a
different one.

Unverified claims are worth chasing beyond their own value. The path to a primary source runs
through the literature that cites it, and that literature is selected for relevance to your
problem - which is exactly where an unasked question is likely to be sitting.

## Declare each input once, with its provenance and its category

An audit found every measured quantity in a long analysis living in three to seven files.
Each is a place where drift starts, and the rule that a hand-carried number will eventually
not be carried is not fixed by being careful about carrying it.

One module, one declaration per input, everything else importing. Two details make it worth
more than a tidy-up. Each entry carries where it came from, because a constant without a
provenance is exactly the thing that drifts. And each is labelled by category - measured here
and reproducible, measured elsewhere with the conditions stated, or a published specification -
because those three deserve different amounts of trust and look identical as numbers.

A by-product: writing the derivation instead of the result caught a rounding. A factor
recorded as 0.58 is 0.5795 when computed from the two measurements it comes from.

## A guard looser than the pattern it protects reports failures for prose

A check tested whether a phrase appeared anywhere in a document before comparing the figure
beside it. It then failed on a paragraph *about* the check, which quoted the phrase while
describing a failure message.

Guard on the pattern that extracts the value, not on prose that mentions the subject - and
where a document genuinely must state a figure, say so explicitly rather than inferring it
from whether the words are present.

## Checks that compare documents cannot catch a shared omission

Every check in a long analysis compared documents with each other, and a missing factor survived
eighteen loops because the prose and the script agreed - they were wrong together, sharing the
same missing step. Agreement between two derived artefacts is not evidence when both derive the
same way.

The check that closes this recomputes the headline from raw inputs and compares against what the
documents say. One direction catches a document drifting from the computation; the other catches
the computation drifting from its inputs. Build at least one check that crosses from
computation to prose rather than prose to prose.

## A correction is applied to the sentence in front of you

A figure was corrected in a document and two earlier sentences in the same paragraph kept the old
value. Nothing about the edit was wrong; it simply addressed the sentence being read.

So after correcting a number, search the whole corpus for the old value before moving on - and
prefer a form where the number appears once and everything else refers to it.

## Corroboration by two secondary sources is not verification

A claim was traced to two independent papers that both assert it and both cite the same primary,
which is behind a paywall. That is better than one source and it is not verification: two
summaries of the same paper can be wrong the same way, and neither author was writing to defend
that particular sentence.

Record the distinction explicitly - located, corroborated, verified - and say which one a claim
has reached. The useful by-product is that chasing corroboration often surfaces the *distinction*
the claim turns on, which is more actionable than the claim: here, that the vulnerability divides
by construction rather than by code family.

## A register of constraints does not check the arithmetic inside its own rows

One loop after writing a constraint register with a status column, the row marked binding for
area turned out to have been computed wrong for seventeen loops: cell area had been divided by
die area with no utilisation factor, making every figure optimistic by 1.7.

The register was right that the constraint binds and right about its source. It said nothing
about whether the number under it was correct, because that is not what a register does.

So a register makes the missing constraints visible and does not audit the present ones. After
writing one, recompute each binding row from its definition rather than reading it.

## A number carried between documents by hand will eventually not be carried

A utilisation factor was measured, recorded and applied in the first document of this work.
When the analysis moved to a second document, that one started from the raw cell areas rather
than from the first document's conclusions, and the factor was simply absent from everything
after.

Nothing was overwritten and no step was wrong. The value just did not make the journey.

So when analysis moves to a new file, carry the derived quantities as code or as an explicit
import rather than by re-deriving from the raw inputs - and when re-deriving is unavoidable,
list what the earlier document applied that the new one must too.

## Slack results in a row are not evidence the next check will be slack

Three constraints were checked across two loops and all three came back with orders of
magnitude to spare. I wrote that this was not evidence the next would be slack, which was
right, and then drew the wrong conclusion from it anyway: I kept looking for the next
constraint.

What bit was one already in the list, with the wrong arithmetic under it. A run of clean
results shifts attention outward, to the unchecked, when the same run is equally a reason to
re-examine the checked.

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
