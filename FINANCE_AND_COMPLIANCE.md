# Finance and compliance plan - for agreement by every stakeholder

Status: **draft v1, open for agreement.** Dated 2026-10-09; sections 2, 3, 5 and 6 revised 2026-10-11. Owner: Dmitrii Vasilev, sole founder.

This document is the plan: how the company is formed, what it costs, and the
position the company takes on token compliance. Section 6 records who has agreed to it.

The facts it builds on are not repeated here. They live in [`FACTS.md`](FACTS.md):

- who the people are;
- what each person holds;
- the legal form;
- the token design.

When this document and `FACTS.md` disagree, `FACTS.md` wins. In that case this
document is corrected.

This is a planning document, not legal or tax advice. Every item marked
**counsel** needs a written answer from a qualified lawyer or accountant before
it is relied on.

## 1. Company formation

**What:** a Delaware C-corporation, held 100% by the founder at formation. See
`FACTS.md` section 2.

**Why Delaware:**
- the standard YC SAFE is written for a Delaware corporation;
- investors expect one;
- it can register for US grants (EIN, SAM.gov UEI, DARPA BAA portal).

**Route:** a formation service that handles the parts a non-US founder needs:

- the state filing;
- the EIN without a US social security number;
- the registered agent;
- founder stock issuance;
- the 83(b) election.

Candidates, with prices as published in 2026; re-check on the provider's own
page before paying:

| Provider | One-time | Includes |
|---|---|---|
| Stripe Atlas (first choice) | USD 500 | State filing fee, EIN, first-year registered agent, founder stock, 83(b) filing support |
| Clerky | USD 499 | YC-style document stack |
| Firstbase | USD 399 | Formation and agent |

**Bank:** Mercury. Thailand is not on Mercury's prohibited-country list as of
2026-10. Approval is case by case, so a second bank is kept as a fallback.

**Recurring costs and deadlines (estimates):**

| Item | Cost per year | Deadline | Note |
|---|---|---|---|
| Registered agent | USD 100 | Annual renewal | After the first year |
| Delaware franchise tax + annual report | from USD 450 | 1 March | Use the assumed par value capital method. Delaware's default notice uses the authorized shares method, which can show a bill of tens of thousands of dollars; recalculate, do not pay it |
| Federal return, Form 1120 with Form 5472 | Accountant, estimate USD 1,000-2,500 | 15 April (extension to 15 October) | Form 5472 is required because a foreign person owns 25% or more. The penalty for a missing form is USD 25,000, even with no income |
| 83(b) election | Included in formation | **30 days after founder stock is issued** | Cannot be filed late |

Estimated total: about USD 500 at formation, then roughly USD 1,500-3,000 a
year before any legal work.

## 2. Investment

There are no investors. The founder holds 100% of the equity (`FACTS.md`
section 3, founder, 2026-10-11). The investment plan this section carried from
2026-10-09 was withdrawn on 2026-10-11; the repository history keeps it. Any
future investment needs a row in `FACTS.md` first.

Work anyone does for the company is not equity. If it is formalised, it goes in
a separate advisor agreement that covers assignment of work product and
confidentiality.

## 3. Token compliance position

The design is recorded in `FACTS.md` section 6 and ledger rows E22-E23:
- 100% of the supply is locked in MiningPool;
- ownership is renounced;
- there is no allocation;
- there is no sale;
- tokens are released only as rewards for verified compute.

On 2026-10-11 the founder decided that the sole authority to issue (mint) $TRI
is his, that TON is its only chain of record, and that the TriToken contract on
Base Sepolia is a retired testnet experiment: it is not $TRI, and its supply is
not $TRI supply (`FACTS.md` sections 3.1 and 6). The design listed above is that
retired contract's. No counsel has reviewed the positions below against it.

The design was chosen to keep the token outside securities-offering rules. The
position in each jurisdiction:

| Jurisdiction | Rule | Position | Open |
|---|---|---|---|
| United States | SEC and CFTC joint interpretation of 2026-03-17 (Commission-level). Solo and pool proof-of-work mining is not an offer or sale of securities: rewards pay for services to the network, not for the managerial efforts of others | The release of TRI only against a verified compute proof is closest to this case | **counsel**: TRI is an ERC-20 reward contract on Base, not native proof-of-work, so the interpretation applies by analogy only |
| European Union | MiCA Article 4(3): Title II does not apply to crypto-assets offered free of charge or created automatically as a reward for maintaining the ledger or validating transactions. Article 4(4): the exemption falls away if the offeror seeks admission to trading on an EU platform | No sale and no listing sought | **counsel**: whether compute rewards fit 4(3), since Base, not TRI, maintains the ledger |
| Thailand (founder's residence) | Emergency Decree on Digital Asset Businesses B.E. 2561 (2018). A public offering of digital tokens needs Thai SEC approval unless it is exempt. Using a token as a means of payment is prohibited. Operating an exchange or brokerage needs a licence | No offering, no payment use, no exchange operated | **counsel**: confirm that reward-only distribution is not an offering |

**Red lines.** Each of these would change the analysis, and none may happen
without counsel's written review and then a row in `FACTS.md`:

- selling or pre-selling tokens;
- a token listing initiated by the company or the founder;
- selling chips or hardware with a promise of token income;
- marketing that points to token price or returns;
- the founder or company earning tokens and selling them.

**Gates before any mainnet deployment:**

1. Verify every contract's source on the block explorer (audit W-INTL-35), so
   that anyone can check the 100% lock.
2. Replace the chip identity check that accepts any key (audit W-INTL-34). The
   testnet deployment has renounced ownership and cannot be repaired, so this
   needs a new deployment.
3. Obtain written legal opinions from US counsel and Thai counsel on the
   positions above.

## 4. The founder's own position in Thailand

These are open, and each one needs **counsel** (Thai tax and immigration):

- the personal tax treatment of income from a foreign company that is brought
  into Thailand by a Thai tax resident;
- whether working on the founder's own foreign company from Thailand needs a
  particular visa or work permit.

No statement on either belongs in any application until the answer is recorded
in `FACTS.md`.

## 5. Decisions and owners

| # | Decision | Owner | State |
|---|---|---|---|
| D1 | Formation provider (Stripe Atlas proposed) | Founder | Open |
| D2 | Bank and fallback bank | Founder | Open |
| D3 | Accountant for Form 1120 / 5472 | Founder | Open |
| D4 | US counsel for the token opinion | Founder | Open, quote to obtain |
| D5 | Thai counsel for section 3 (Thailand) and section 4 | Founder | Open, quote to obtain |
| D6 | Withdrawn 2026-10-11: there are no investors (`FACTS.md` section 3) | Founder | Closed |
| D7 | Withdrawn 2026-10-11, as D6 | Founder | Closed |

## 6. Agreement record

A stakeholder agrees to the sections in their scope. Agreement is recorded here
by pull request, with the date and the channel it was given in. Silence is not
agreement.

| Stakeholder | Role (see `FACTS.md`) | Scope to agree | State |
|---|---|---|---|
| Dmitrii Vasilev | Sole founder | All sections | Author |
| US counsel | To be engaged | Sections 1-3 | Not engaged |
| Thai counsel | To be engaged | Sections 3 and 4 | Not engaged |
| Accountant | To be engaged | Section 1, recurring filings | Not engaged |

## 7. Changing this document

- Change it by pull request that names the reason.
- If a change touches a stakeholder's scope, that stakeholder's agreement in
  section 6 resets to "awaiting reply".
- Facts change in `FACTS.md` first. This document then follows.

## Sources

- SEC and CFTC interpretation, 2026-03-17: summaries by Sidley and Jenner & Block.
- SEC staff statement on proof-of-work mining, 2025-03-20: summary by Dechert.
- MiCA Article 4: Osborne Clarke; Stadler Partner; ESMA Q&A summary by MiCA Crypto Alliance.
- Thailand: Tilleke & Gibbins on ready-to-use utility tokens; Baker McKenzie, Digital Asset Law in Thailand 2025; Chambers Fintech 2026 Thailand.
- Formation and costs: third-party reviews of Stripe Atlas pricing; Delaware franchise tax guides (Otonomos, Rho); Form 5472 guides (Gordon Law).
- Banking: Mercury support page "Prohibited countries".
