# Company facts - the single source of truth

Status: authoritative. Last verified: 2026-10-09. Maintained by the founder.

This file is the one place where facts about the company itself are recorded:
who the people are and what roles they hold, who owns what, the legal form, the
funding, and the outcome of every programme the company has applied to.

**Every other text must agree with this file.** That covers documents in this
repository, applications, decks, emails, posts, and anything an agent writes.
When another text disagrees, this file wins and the other text is corrected. If
this file is wrong, correct it here first, in a pull request that names where
the new fact comes from. Only after that may other texts change.

## Rules for anyone writing about the company, human or agent

1. **State only what is recorded here.** If a fact you need is not in this
   file, write "not established". Do not infer it, round it, or carry it over
   from an older document.
2. **Every fact carries a source and a date.** A statement with no source does
   not belong in this file.
3. **Private terms stay out of this public repository.** That means investment
   amounts, valuation caps, tax numbers, addresses, phone numbers and
   citizenship. The founder holds them off-repo. Where one matters, this file
   says so and gives no value.
4. **Supersede, do not delete.** When a fact stops being true, move it to the
   History section with the date it stopped being true.
5. **Correct a known-wrong statement wherever it appears.** Section 7 lists
   wrong statements that have already reached outside readers. Never repeat
   them.

---

## 1. People and roles

| Person | Role | Is not | Source |
|---|---|---|---|
| Dmitrii Vasilev | Sole founder. Author of TRI-27 / t27, GoldenFloat and the Golden Ruler numeric format catalog. The only decision-maker. Based in Thailand. ORCID 0009-0008-4294-6159, admin@t27.ai | - | Founder, 2026-10-09 |
| Dmitrii Fedorov | Business angel: an investor in the company (section 3). Makes introductions to investors and partners | Not a co-founder. Not an employee. Not a director. Holds no control rights | Founder, 2026-10-09 |
| Scott Olsen | External collaborator. Principal Investigator on the 2026 DARPA proposal (section 5), submitted through his own company, Wisdom Traditions Center, LLC (Florida) | Not a shareholder. Not a funder: he said he is not in a position to fund the process (2026-09-09) | Correspondence, 2026-04-17 to 2026-09-17 |

Team size: one founder and no employees, as recorded in audit entry W-INTL-25.

**Two people named Dmitrii.** The founder and the business angel share a first
name. Always write the full name, **Dmitrii Vasilev** or **Dmitrii Fedorov**;
never "Dmitrii" or "Dima" alone, in any document, email or message. The arXiv
author "D. Vasilev" of arXiv:2607.09485 (hep-th, Ievlev / Vasilev / Yung) is an
unrelated namesake: Dmitrii Vasilev's own papers are the ones listed under
ORCID 0009-0008-4294-6159.

## 2. Legal form

| Item | State as of 2026-10-09 | Source |
|---|---|---|
| Incorporated entity | **None.** The work is carried out by the founder personally, under the Trinity S3AI / gHashTag name | Founder |
| Planned entity | A company registered in the founder's name. The founder holds 100% of the common stock at formation. The planned vehicle is a **Delaware C-corporation**: the standard YC SAFE form is written for one, and it can register for US grants (EIN, SAM.gov UEI). Not yet filed | Founder, 2026-10-09 |
| ADGM / DIFC foundation | **Not pursued now.** ADGM's amendments of 2026-05-01 bar foundations used for non-profit purposes. Minimum initial assets are USD 50,000, in fiat only. The Hub71 route it was meant to serve closed on 2026-08-24 | Founder, 2026-10-09 |
| Armenia backup | Not pursued | Founder, 2026-10-09 |

Do not write "ADGM-registered", "UAE entity", "Abu Dhabi company" or
"relocating to Abu Dhabi". None of these is true.

## 3. Ownership and investment

| Item | Fact | Source |
|---|---|---|
| Founder | 100% of the equity before investment | Founder, 2026-10-09 |
| Dmitrii Fedorov | **0.5% (one half of one percent)** of the company's equity, in exchange for a cash investment. Agreed verbally and confirmed by the founder on 2026-10-09. "0.5" always means 0.5 percent, never 50 percent | Founder, 2026-10-09 |
| Instrument | YC **post-money SAFE**, valuation cap only. Signed once the company exists. The cap is set so that the investment converts to exactly 0.5%: cap = investment / 0.005. The amount and the cap are held off-repo | Founder, 2026-10-09 |
| Control | **None.** No board seat. No votes before conversion. No veto. No rights beyond the standard form. The founder's principle: investor control over a solo founder hinders development | Founder, 2026-10-09 |
| Token rights | **None.** The SAFE covers equity only. Tokens are a separate incentive and are not part of the investment | Founder, 2026-10-09 |
| Payment | Paid into the company's own bank account, never to the founder personally | Founder, 2026-10-09 |
| Paperwork status | Agreed; not yet signed, because no company exists yet | Founder, 2026-10-09 |

If an investor or adviser also does work for the company, that work goes in a
separate advisor agreement. It is never added to the investment terms.

## 4. Funding and revenue

| Item | State as of 2026-10-09 | Source |
|---|---|---|
| Equity funding received into a company | None. No company account exists yet | Section 2 |
| Grants awarded | None | Section 5 |
| Revenue | Not established in this file. Claim revenue only after a source row is added here | - |

## 5. Programmes and applications

| Programme | Submitted | Outcome | Source |
|---|---|---|---|
| Hub71 Access Programme, Cohort 20 (Abu Dhabi) | Before the 21 August 2026 deadline | **Not selected**, notified 2026-08-24 | Hub71 email |
| DARPA DSO, CLARA programme, full proposal FP-067 | 2026-04-17. Proposing organisation: Wisdom Traditions Center, LLC. PI: Scott Olsen | **Returned 2026-08-08 as non-conforming.** Two required forms were missing: the Streamlined Cost Buildup Workbook and the Common Forms for Current and Pending. The proposal was not evaluated technically | DARPA email |

Registration lesson from the DARPA attempt. Submitting a proposal needs a
DARPA BAA portal account. Receiving an award needs a SAM.gov registration of
type "All Awards", not "Federal Assistance".

## 6. Token

| Item | Fact | Source |
|---|---|---|
| Deployed token | TriToken on Base Sepolia, a testnet. Its constructor mints the entire supply to MiningPool and renounces ownership in the same transaction. There is no founder, investor, treasury or liquidity allocation | `paper/evidence_ledger.md` row E22 |
| Supply lock | **100% of the supply is locked in MiningPool, by design, to keep the token out of securities-offering territory.** MiningPool holds 7,625,597,484,987 TRI, the full total supply. Ownership of both TriToken and MiningPool is renounced, so no key can mint, move or reallocate tokens. A token leaves the pool only as a reward for a verified compute proof from a registered chip, on a four-year halving curve set by EmissionController | Founder, 2026-10-09; ledger rows E22, E23; `plan/launch_readiness.md` |
| What the lock does not cover | The founder, the company and any investor receive tokens only the way anyone else does: by earning them through the pool. Selling compute hardware with a promise of token income, selling or pre-selling tokens, listing them on an exchange, or marketing them as an investment would each change the legal analysis. Each needs legal review first, and then a row in this file | Founder, 2026-10-09 |
| Superseded token | TrinityToken on Ethereum Sepolia, from February 2026, carried a founder and treasury split. It is superseded and must not be cited as current | Audit addendum |
| Token sale | **None planned or authorised.** A public sale requires legal review first, and then a row in this file | Founder, 2026-10-09 |
| Relation to equity | Tokens are a separate incentive. Holding equity, or a SAFE, gives no right to tokens | Founder, 2026-10-09 |

Some token configurations in other repositories carry a founder allocation or a
sale. They are not adopted, and they must not be cited.

## 7. Wrong statements already made - do not repeat

| Wrong statement | Where it appeared | Correct statement |
|---|---|---|
| "my co-founder Dmitrii Fedorov" | Outbound email, 2026-09-03 | Fedorov is a business angel. The sole founder is Dmitrii Vasilev |
| "founder from Brazil" | Investor introduction, 2026-10-08 | The founder is based in Thailand |
| "establishing the legal vessel at ADGM and relocating to Abu Dhabi" | `paper/hub71_form_answers.md`, an application that was not selected | No ADGM entity exists. The text is a historical record |
| "UAE ADGM / DIFC Foundation" as the planned legal vessel | This repository's README and description, until 2026-10-09 | See section 2 |
| "0.5" read as 50 percent | Risk of misreading | 0.5 percent |

## History

| Period | Statement that was then current | Superseded by |
|---|---|---|
| 2026-07-02 to 2026-10-09 | Planned legal vessel: UAE ADGM / DIFC Foundation, with Armenia as backup | Section 2, 2026-10-09 |
| 2026-07-29 to 2026-08-24 | Hub71 Cohort 20 application in preparation, closing 21 August 2026 | Section 5: not selected |
