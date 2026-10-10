# Agent rules

Rules for any agent working in this repository. Each section below is the short
form; the long form of a rule lives in exactly one place, named in its section.

## Company facts: one source of truth

Owner's rule, 2026-10-09: agents must not write things about the company that
are not true. **`FACTS.md` is the single source of truth** for people and
roles, ownership and investment, legal form, funding, programme outcomes and
token policy.

- Before writing any of those facts anywhere - a document here, an application,
  a deck, an email draft, a post, another repository - read `FACTS.md` and use
  its wording.
- A fact that is not in `FACTS.md` is "not established". Do not infer it, and do
  not carry it over from an older document; several older documents here are
  historical records that are now wrong.
- To change a fact, change `FACTS.md` first, in a pull request that names the
  source, and only then the texts that repeat it.
- Never put private terms in this public repository: investment amounts,
  valuation caps, tax numbers, addresses, phone numbers, citizenship.
- Section 7 of `FACTS.md` lists statements already made in error ("co-founder"
  Fedorov, "founder from Brazil", an ADGM entity). Never repeat them.
- The plan built on those facts lives in `FINANCE_AND_COMPLIANCE.md`: how the company is
  formed, what it costs, how the investment is executed, and the token
  compliance position with its red lines. Any outward text about money, a
  deal, the legal form or the token must agree with it. Agreement by each
  stakeholder is recorded in its section 6, by pull request; silence is not
  agreement.

## Own language first

When this project publishes something about itself, it publishes in **this
project's own language and format** -- not translated into somebody else's.

Owner's rule, 2026-09-20: stop writing in other people's languages, we have our
own.

This bites on any file whose only reason to exist is that an outside tool
expects that shape: `llms.txt`, `agents.json`, `ai.txt`, `.well-known/*.json`,
A2A agent cards, `ai-plugin` manifests, OpenAPI stubs, JSON-LD blocks, a README
that restates a spec. The reflex is to write four of them in four foreign
formats, and the reflex is wrong: a project whose claim is "here is a language
worth writing" and which then describes itself in three of other people's
formats has published three documents that are not true of it.

**The move:** find the address the outside world already fetches, then serve our
own language at it. `/llms.txt` at t27.ai **is** a t27 module -- `llms.txt`
requires nothing but text, and every prose line of a `.t27` file is a `;`
comment, so it stays readable to anything that cannot compile it.

**Three qualifications, so the rule stays honest:**

- A format a resolver genuinely parses -- a sitemap, `package.json`, a lockfile
  -- is machinery, not a description. **Generate** it from our own source; never
  hand-write it into a second home for the truth.
- Code against someone else's API uses their types. Prose for a human who has
  never heard of the project uses that human's language.
- If a format demands a claim we cannot back, **publish nothing**. An A2A card
  with no A2A server behind it is a false claim, and a missing file is more
  honest than a lying one.

The test: *is this file the project speaking about itself?* If yes, it speaks
our language. If it is plumbing, it speaks the plumbing's.

**Worked example, compiler-checked rather than asserted:** in `gHashTag/trinity`,
`apps/website/public/t27/files/specs/catalog/onboarding.t27` generates
`/llms.txt` and `/agents.t27` byte-identically, gated in CI as
`check:onboarding`. The generator evaluates the spec's own `test` blocks --
`typecheck.ok` stays true for `assert 1 > 2`, so a compiler saying "this parses"
is not a compiler saying "this is true" -- and re-compiles the rendered document
before writing it.

**The full rule lives in exactly one place: the `own-language-first` skill**
(`~/.claude/skills/own-language-first/SKILL.md`). It carries the consent gate for
documents addressed to other people's agents, the six negative controls, and the
`;`-alone-on-a-line trap that silently discards a `module` declaration. This
section is a pointer, not a copy -- the recorded defect in this codebase family
is the hand-copied rule that only two of its three homes knew about.
