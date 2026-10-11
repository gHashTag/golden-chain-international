# Company facts - the single source of truth

Status: authoritative. Last verified: 2026-10-09; sections 1, 3, 6, 7 and History
updated 2026-10-11. Maintained by the founder.

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
| Scott Olsen | External collaborator. Principal Investigator on the 2026 DARPA proposal (section 5), submitted through his own company, Wisdom Traditions Center, LLC (Florida) | Not a shareholder. Not a funder: he said he is not in a position to fund the process (2026-09-09) | Correspondence, 2026-04-17 to 2026-09-17 |

Team size: one founder and no employees, as recorded in audit entry W-INTL-25.

**Full names only.** Always write a person's full name, for the founder
**Dmitrii Vasilev**; never "Dmitrii" or "Dima" alone, in any document, email or
message. The arXiv author "D. Vasilev" of arXiv:2607.09485 (hep-th, Ievlev /
Vasilev / Yung) is an unrelated namesake: Dmitrii Vasilev's own papers are the ones listed under
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
| Equity | **No investors.** The founder, Dmitrii Vasilev, holds 100% of the equity | Founder, 2026-10-11 |

If an investor or adviser also does work for the company, that work goes in a
separate advisor agreement. It is never added to the investment terms.

### 3.1 Equity is not the token

Each row is a fact with its source. Where something is not yet a fact, the row
says "not established".

| Item | Fact | Source |
|---|---|---|
| Who holds equity | Nobody but the founder, Dmitrii Vasilev. There are no investors | Founder, 2026-10-11 (the row above) |
| What equity carries | Equity carries no tokens and no token rights: no right to emission, to a pool, or to network payouts. Tokens are a separate incentive | Section 6, "Relation to equity" (Founder, 2026-10-09); `WHITE-PAPER.md` v0.9, section 7, legal posture (2026-10-10) |
| Money and the token | No investment money buys, supports or lists the token. There are no investors (above), no token sale is planned or authorised (section 6), and the project initiates no listing | Founder, 2026-10-11; section 6, "Token sale" (Founder, 2026-10-09); `WHITE-PAPER.md` v0.9, principle D9 (2026-10-10) |
| How anyone else gets $TRI | The token is not sold. Contributors and developers earn $TRI only as payment for verified work, through bounties and fees designed by the founder, never by minting | Founder, 2026-10-11; section 6, "Token sale" (Founder, 2026-10-09) |
| The five kinds of payment | BOUNTY, EXECUTOR_FEE, PROVIDER_FEE, VERIFIER_FEE and AUTHOR_ROYALTY. Each is payment for work, never a share of company profit, and each is tied to a verified receipt. A disagreeing receipt is slashed | Owner decision, 2026-10-10, on gHashTag/t27 issue 8613 (https://github.com/gHashTag/t27/issues/8613#issuecomment-6098242581); gHashTag/t27 `specs/verified/payout.t27` (a72281956, 2026-10-10) and `specs/network/pool.t27` (49461b70e, 2026-10-10) |
| Credits are non-transferable | Network credits are non-transferable until written counsel review opens a value gate, and are minted only on the chain of record | gHashTag/t27 issue 8613, the same comment; `specs/network/pool.t27` (49461b70e, 2026-10-10) |
| No token allocation | Neither the company nor the founder holds a token allocation: no founder pool, no investor pool, no insider reserve, no airdrop | `WHITE-PAPER.md` v0.9, principle D7 (2026-10-10); section 6, "Deployed token" (ledger row E22) |
| Who may mint | The founder alone (section 6, "Issuing authority"). No investor, equity holder, contributor or company may mint | Founder, 2026-10-11 |
| Chain of record | TON is the only chain of record of $TRI. gHashTag/t27 `specs/trinet/tri-bridge.t27` makes TON the chain of record and the only minter; other chains hold TRI only by lock-and-mint. Its claim status is DESIGN: no contract, vault, key or bridged token exists yet | Founder, 2026-10-11; `specs/trinet/tri-bridge.t27` (5fc049a2c, 2026-10-10), owner decision of 2026-10-09 |
| How the mint authority is bound on chain | Which key mints, and how the cap and the halving schedule bind it on TON: **not established** | - |
| The Base Sepolia testnet token | **Retired.** The TriToken contract on Base Sepolia (section 6) is a retired testnet experiment. It is not $TRI, and its supply is not $TRI supply. Its renounced ownership is a historical fact about that contract only: it does not bear on TON as the only chain of record, or on the founder's issuing authority. This answers gHashTag/t27 issue 8618 | Founder, 2026-10-11 |
| Value gates | Every value gate needs written counsel review first: a sale, a listing, transferable credits, a mainnet deployment. No counsel is engaged yet, so no value gate is open | Section 6; `FINANCE_AND_COMPLIANCE.md` sections 3 and 6 (2026-10-09); `WHITE-PAPER.md` v0.9, principle D6 (2026-10-10) |
| Counsel review of a single issuer | **Not established.** No counsel has reviewed the founder's sole issuing authority | - |
| Price of one unit of work | **Not established.** Pricing by measured work units is open as gHashTag/t27 issue 8619 | gHashTag/t27 issue 8619 |

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
| Base Sepolia TriToken (retired) | **A retired testnet experiment. It is not $TRI, and its supply is not $TRI supply.** A historical fact about that contract only: its constructor mints the entire supply to MiningPool and renounces ownership in the same transaction. There is no founder, treasury or liquidity allocation | Founder, 2026-10-11; `paper/evidence_ledger.md` row E22 |
| Supply lock (retired contract only) | Historical, about the retired Base Sepolia contract above, not about $TRI. **100% of the supply is locked in MiningPool, by design, to keep the token out of securities-offering territory.** MiningPool holds 7,625,597,484,987 TRI, the full total supply. Ownership of both TriToken and MiningPool is renounced, so no key can mint, move or reallocate tokens. A token leaves the pool only as a reward for a verified compute proof from a registered chip, on a four-year halving curve set by EmissionController | Founder, 2026-10-09; ledger rows E22, E23; `plan/launch_readiness.md` |
| What the lock does not cover | $TRI is earned only by verified work in the founder's game: bounties, fees and royalties. Only the founder, Dmitrii Vasilev (gHashTag), mints, on TON, the chain of record | Founder, 2026-10-11 |
| Superseded token | TrinityToken on Ethereum Sepolia, from February 2026, carried a founder and treasury split. It is superseded and must not be cited as current | Audit addendum |
| Token sale | **None planned or authorised.** A public sale requires legal review first, and then a row in this file | Founder, 2026-10-09 |
| Relation to equity | Tokens are a separate incentive. Holding equity, or a SAFE, gives no right to tokens | Founder, 2026-10-09 |
| Issuing authority | **The sole authority to issue (mint) $TRI is Dmitrii Vasilev (GitHub gHashTag).** No other person, company or investor may mint. Contributors and developers earn $TRI only as payment for verified work, through bounties and fees designed by the founder, never by minting. $TRI's only chain of record is TON (gHashTag/t27 `specs/trinet/tri-bridge.t27`). The Base Sepolia contract above is a retired testnet experiment and is not $TRI, so its renounced ownership does not bear on this authority | Founder, 2026-10-11 |

Some token configurations in other repositories carry a founder allocation or a
sale. They are not adopted, and they must not be cited.

## 7. Wrong statements already made - do not repeat

| Wrong statement | Where it appeared | Correct statement |
|---|---|---|
| "my co-founder" | Outbound email, 2026-09-03 | There is no co-founder. The sole founder is Dmitrii Vasilev |
| "founder from Brazil" | An introduction email, 2026-10-08 | The founder is based in Thailand |
| "establishing the legal vessel at ADGM and relocating to Abu Dhabi" | `paper/hub71_form_answers.md`, an application that was not selected | No ADGM entity exists. The text is a historical record |
| "UAE ADGM / DIFC Foundation" as the planned legal vessel | This repository's README and description, until 2026-10-09 | See section 2 |
| That a business angel holds 0.5 percent of the equity under a SAFE, or that the company has any investor | This file until 2026-10-11; `README.md`, `GREEN-PAPER.md` v0.1, `WHITE-PAPER.md` v0.9 and `FINANCE_AND_COMPLIANCE.md` until the same date | There are no investors. The founder, Dmitrii Vasilev, holds 100% of the equity (Founder, 2026-10-11) |

## History

| Period | Statement that was then current | Superseded by |
|---|---|---|
| 2026-07-02 to 2026-10-09 | Planned legal vessel: UAE ADGM / DIFC Foundation, with Armenia as backup | Section 2, 2026-10-09 |
| 2026-07-29 to 2026-08-24 | Hub71 Cohort 20 application in preparation, closing 21 August 2026 | Section 5: not selected |
| 2026-10-09 to 2026-10-11 | A verbal equity arrangement was recorded in section 3 | Withdrawn by the founder on 2026-10-11; section 3 (Founder, 2026-10-11) |
| 2026-10-09 to 2026-10-11 | Section 6 described the TriToken contract on Base Sepolia as the deployed token, and how it related to the founder's issuing authority was not established | Section 6, "Base Sepolia TriToken (retired)": a retired testnet experiment, not $TRI (Founder, 2026-10-11) |
| 2026-10-09 to 2026-10-11 | Section 6, "What the lock does not cover": the founder, the company and any investor receive tokens only the way anyone else does, by earning them through the pool (the retired contract's MiningPool); selling compute hardware with a promise of token income, selling or pre-selling tokens, listing them on an exchange, or marketing them as an investment would each change the legal analysis and need legal review first (Founder, 2026-10-09) | Section 6, "What the lock does not cover" (Founder, 2026-10-11). The legal-review red lines stand in `FINANCE_AND_COMPLIANCE.md` section 3 |
