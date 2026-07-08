# Tax close calendar — a controller COORDINATION checklist (not tax advice)

> **Last reviewed:** 2026-07-06. Owned by `controller` (+ `audit-prep-specialist` for evidence, `financial-modeler` for the ASC 740 provision mechanics in [`tax-provision-asc740.md`](tax-provision-asc740.md)).
>
> **SCOPE — READ THIS FIRST.** This is a **coordination checklist**: what the controller tracks, gathers, and hands to the tax function so nothing is missed and no filing is late. It is **NOT tax advice and NOT a determination of any filing obligation, nexus, rate, due date, taxability, or election.** Cadences and dates below are *typical U.S. patterns that change* — with weekend/holiday shifts, jurisdiction-specific rules, entity-type differences, and annual IRS/state updates. **Every date and every determination must be confirmed against the current authority (IRS, the specific state/local agency) and routed to a licensed CPA / tax advisor.** Treat this file as a tickler, not a tax opinion. When book-vs-tax mechanics matter, cross-read [`tax-provision-asc740.md`](tax-provision-asc740.md) (ASC 740) and [`accrual-and-cutoff-discipline.md`](accrual-and-cutoff-discipline.md).

The controller does not *file* most of these — but the controller is the choke point that assembles the numbers and evidence the tax function and external preparers need. A missed sales-tax return or a late 1099 batch is usually a *coordination* failure (someone didn't hand off the data on time), not a tax-technical one. This checklist keeps the coordination honest.

---

## 1. Recurring cadences to track (confirm each date with the agency / advisor)

| Obligation | Typical cadence | What the controller coordinates | Route determination to |
|---|---|---|---|
| **Sales & use tax** | Monthly / quarterly / annually — **cadence is assigned per jurisdiction by filing volume** | Pull taxable vs. exempt sales by jurisdiction; reconcile collected liability to the GL; confirm nexus footprint hasn't changed (new state, marketplace, remote employees) | State/local DOR + tax advisor (nexus, taxability, rate) |
| **Use tax self-assessment** | With the sales-tax return | Flag purchases where no sales tax was charged but the item is taxable | Tax advisor |
| **Payroll tax deposits** | Per IRS schedule (semi-weekly / monthly) — usually run by the payroll provider | Confirm the provider deposited; reconcile payroll-tax liability to the GL each close | Payroll provider + tax advisor |
| **Federal & state income tax — estimated payments** | Quarterly (calendar-year C-corp: ~Apr / Jun / Sep / Dec 15; individuals/pass-throughs differ) | Provide the forecast taxable income / book-to-tax the estimate is built on; confirm the payment was made | Tax advisor (amount, safe-harbor) |
| **Income tax provision (ASC 740)** | Quarterly (interim AETR) + annual | Deliver the trial balance, permanent/temporary difference support, deferred rollforward inputs, and the schedules below | Tax advisor / provision preparer |
| **Franchise / margin / gross-receipts tax** | Annual (some quarterly) — state-specific | Gather the base (net worth, margin, or receipts) the state uses | State DOR + tax advisor |
| **Property tax (business personal property)** | Annual rendition + payment (dates vary by county) | Provide the fixed-asset listing (ties to the depreciation schedule) at the assessment date | County assessor + tax advisor |
| **1099 information returns** | Annual — see §2 | Validate vendor W-9s / TINs through the year; classify reportable payments | Tax advisor (reportability) |
| **W-2 / payroll year-end** | Annual — see §2 | Reconcile W-2 totals to the payroll GL and the 941s | Payroll provider + tax advisor |

**Nexus is the silent risk.** A remote hire, a new warehouse, crossing an economic-nexus sales threshold, or a marketplace-facilitator change can create a *new* filing obligation mid-year. The controller's job is to **flag the trigger event**; whether it creates nexus is a determination for the tax advisor.

---

## 2. Year-end information-return timing (1099 / W-2) — confirm current-year dates

These are the classic "January surprises." **Confirm the exact due dates with the IRS/SSA for the specific year** (weekend/holiday shifts move them):

- **W-9 collection is a year-round control, not a January scramble.** Every new vendor gets a W-9 *before* first payment; a missing/invalid TIN is what causes B-notices and backup-withholding exposure. The controller keeps the vendor master clean all year so the year-end batch is mechanical.
- **1099-NEC** (non-employee compensation) is generally due to **both** the recipient and the IRS by **~Jan 31** — the tightest deadline, with little slack for corrections.
- **1099-MISC / other 1099s** — recipient copy generally ~Jan 31; IRS copy later (paper vs. e-file dates differ). **Confirm.**
- **W-2 / W-3** — to employees and the SSA generally by **~Jan 31**.
- **E-file thresholds have tightened** — the aggregate-return count that forces e-filing has dropped in recent years. Confirm whether the entity is over the current threshold; if so, paper filing is not an option.
- Reconcile the 1099 batch to the AP subledger and the W-2 batch to the payroll GL / 941s **before** transmitting. A number that doesn't tie to the GL is the tell.

---

## 3. ASC 740 (income-tax provision) touchpoints the controller feeds

The controller doesn't compute the provision, but supplies its inputs. See [`tax-provision-asc740.md`](tax-provision-asc740.md) for the mechanics. Hand off, each quarter/year:

- **Book income** — the reconciled trial balance / pre-tax income by legal entity.
- **Permanent differences** — non-deductible items (certain M&E, fines/penalties, some stock comp), tax-exempt income.
- **Temporary differences** — the book-vs-tax timing items that create deferreds. **The close schedules feed these directly:**
  - **Depreciation** — book straight-line (from [`../skills/close-schedules/`](../skills/close-schedules/SKILL.md)) vs. **tax MACRS/bonus/§179**. The difference is a temporary difference and a deferred-tax item. The engine produces the *book* side only.
  - **Deferred revenue** — book ASC 606 recognition vs. tax timing (advance-payment rules) can diverge.
  - **Prepaids, accruals, reserves/allowances, R&D capitalization (§174)** — common temporary differences.
- **Deferred rollforward inputs**, valuation-allowance evidence, uncertain-tax-position (FIN 48) support.
- **The interim AETR** estimate for quarterly provisions.

**The controller's line is bright:** deliver *reconciled book numbers + the schedules + the difference candidates*; the **classification of a difference as permanent vs. temporary, the tax method, the rate, and the valuation-allowance judgment are the tax advisor's determination.**

---

## 4. Estimated-payment coordination

- Build the estimate off a **documented forecast of taxable income** (not book income — the advisor adjusts for book-to-tax). The controller supplies the forecast and the book base; the advisor sets the payment amount and the safe-harbor strategy.
- Track the four quarterly due dates as hard tickler items; confirm each payment cleared and hit the right agency and period.
- A large true-up at year-end is usually a signal the forecast drifted — feed actuals back so the next year's estimates are better (this is the FP&A reforecast loop, applied to tax).

---

## 5. How this ties to the close

- **Reconcile before you file.** Every tax liability account (sales tax payable, payroll tax payable, income tax payable) is reconciled in the same close ([`reconciliation-summary`](../skills/reconciliation-summary/SKILL.md)) before any return is cut. A return built on an unreconciled liability is describing noise.
- **The fixed-asset schedule is shared evidence.** The depreciation rollforward supports both the book balance sheet *and* the property-tax rendition *and* the book side of the tax-depreciation difference — produce it once, use it three ways.
- **Materiality still applies** to *coordination effort*, but **not** to filing obligations: a small sales-tax return is still late if it's late. Don't suppress a filing because the dollars are immaterial.
- **Audit trail.** Who pulled the data, when, what period, which agency, confirmation number. A tax coordination log with no signatures is informal (finance CLAUDE.md §3 #6).

---

## 6. What this file is not

Not a tax-filing schedule you can rely on as-is, not legal or tax advice, and not a substitute for a licensed preparer. Dates, thresholds, cadences, nexus, taxability, and elections **change and are jurisdiction- and entity-specific** — confirm every one against current authority and route determinations to a CPA / tax advisor. This is a controller's coordination tickler, cross-checked against general U.S. practice; it earns its keep by making sure the right data reaches the right person on time, not by deciding the tax answer.
