# Accrual & Cutoff Discipline at Financial Close

*Practitioner synthesis for controllers, close accountants, and FP&A. Research date: 2026-06-04. Confidence tags inline: `[high]` = ≥2 independent authoritative sources or the codification itself; `[med]` = single authoritative source; `[unverified — training knowledge]`.*

## Method note

Searched six sub-topic clusters via WebSearch: accrual recognition + reversing entries; cutoff testing assertions; accrual/provision/reserve under ASC 450; channel stuffing + FOB cutoff; GR/IR (goods-received-not-invoiced); and controller reconciliation/roll-forward discipline. Two confirmatory passes ran on the FASB conceptual framework (CON 6 / CON 8) and on ASC 606 control-transfer mechanics, plus the SEC's position on the word "reserve." Source quality skewed strong: primary or near-primary anchors include the **FASB ASC PDF for Concepts Statement No. 8**, **Deloitte DART** and **PwC Viewpoint** roadmaps on ASC 450 and ASC 606, **SEC EDGAR** correspondence on "reserve" terminology, and audit-assertion references (AccountingInsights, Aurora Financials, maxwellcpareview). Practitioner corroboration came from FinQuery, AccountingTools, Corporate Finance Institute, PLANERGY, and ERP-vendor GR/IR docs. **Blocked:** `accountinginsights.org` returned HTTP 403 on WebFetch — that cutoff-assertion content is cited from the search excerpt, not the fetched page (flagged `[med]` where load-bearing). I could not open the gated DART/Viewpoint full text (subscription walls); their ASC 450/606 claims are corroborated by the search excerpts plus a second independent source and tagged accordingly. No IIA or AU-C 501 primary text was directly retrieved; assertion-framework claims rest on audit-firm/CPA-review secondary sources.

---

## 1. What makes a *proper* accrual

An accrual records an economic event in the period it occurs, independent of cash movement — the core of accrual-basis accounting and the matching principle in the FASB conceptual framework, which calls for expenses to be recognized in the same period as the revenue they help generate `[high]` (FASB CON 8/CON 6; AccountingTools; FinQuery). FASB describes accrual as "the accounting process of recognizing… amounts expected to be received or paid, usually in cash, in the future" `[med]` (FASB conceptual framework excerpt).

**The two recognition gates for an expense accrual** (mirroring the ASC 450 loss-contingency logic for estimated items, and simply "incurred" for known liabilities):

1. **The obligating event has occurred on or before period end** — the goods were received, the service was performed, the employee earned the wage. This is the substance test: an obligation exists at the balance-sheet date `[high]`.
2. **The amount is reasonably estimable** — you can put a defensible number on it `[high]` (ASC 450-20 recognition logic; Lexology/Deloitte roadmap excerpts).

If both hold → accrue. If the obligation exists but you have the *actual* invoice, it's not an accrual, it's a payable. If neither the event nor a reliable estimate exists, you do nothing (possibly disclose, if it's a contingency — see §4).

**Journal-entry shape.** A classic expense accrual is `Dr Expense / Cr Accrued liability` at period end `[high]` (Ramp; FinQuery). An accrued-revenue entry is `Dr Accrued/Unbilled receivable / Cr Revenue` `[high]`.

**True accrual vs. unreversed estimate — the distinction practitioners must hold.**

- A **true (reversing) accrual** is a temporary placeholder for something that will be settled and separately recorded shortly — e.g. received-not-invoiced goods, where the vendor invoice *will* arrive next period. You book it at period end and **reverse it on day one of the next period**; the actual invoice then posts normally with no double-count `[high]` (AccountingVerse; Wafeq; Study.com). The reversal is the *exact opposite* of the original entry.
- An **unreversed estimate** is a standing balance you re-measure each period rather than back out — e.g. a warranty provision or an allowance for doubtful accounts. You don't reverse it; you *roll it forward* and true it up (see §4 and §6).

> **Decision rule — does this accrual reverse?** If the same item will be re-recorded next period from a source document (invoice, payroll run), it's a reversing accrual → set the auto-reversal flag. If it's a re-estimated standing balance, it does **not** reverse → it goes on the roll-forward.

A common error mode is leaving a reversing accrual *unreversed* (double-counting the expense when the invoice lands) or, conversely, auto-reversing a standing estimate that should have been rolled forward (understating the liability).

---

## 2. Cutoff — the concept

**Cutoff** is the assertion that transactions are recorded in the *correct accounting period* — the period in which the obligating/earning event actually occurred `[high]` (AccountingInsights `[med]`, 403-blocked; Aurora Financials; KPM). It is the temporal edge of two financial-statement assertions:

- **Completeness** — everything that *belongs* in the period is recorded (nothing left out / pushed forward). The classic understatement risk for expenses and liabilities `[high]`.
- **Occurrence (existence/validity)** — everything recorded *actually happened* in the period (nothing pulled forward / fabricated). The classic overstatement risk for revenue `[high]` (maxwellcpareview; AccountingInsights excerpt).

**Revenue cutoff** turns on *when control transfers* under ASC 606 — for point-in-time sales of goods, the indicators in ASC 606-10-25-30 (title, physical possession, risks/rewards, acceptance, right to payment). Shipping terms are the practical proxy: **FOB shipping point** → control/title passes at the dock at pickup → revenue recognized at shipment; **FOB destination** → control passes on delivery → revenue recognized at delivery `[high]` (Deloitte DART excerpt; RevenueHub; GAAPdynamics). A sale shipped FOB destination on Dec 31 that arrives Jan 3 belongs to the **next** period.

**Expense cutoff** turns on *when goods/services are received* — the receiving-report date and the service-performance date, not the invoice date and not the payment date `[high]`.

**The classic year-end cutoff window** is the last few days of the closing period and the first few days of the next — auditors deliberately examine "the last few transactions of the audit period and the first few of the next period" `[high]` (Aurora Financials; maxwellcpareview).

---

## 3. Cutoff testing — how it's done and what an error looks like

Cutoff testing **traces source documents around the period boundary to the period in which they were recorded**, in both directions:

- **Revenue:** pull sales invoices and **shipping documents (bills of lading)** dated just before and just after year-end; compare the shipping-doc date to the GL posting date. Goods that left the dock (FOB shipping point) on Dec 30 must be in December revenue; goods shipped Jan 2 must not be `[high]` (Aurora Financials; maxwellcpareview; KPM).
- **Expenses/purchases:** pull **receiving reports** and vendor invoices around the boundary; goods received before cutoff must hit the period's payables/accruals even if the invoice hasn't arrived (the GR/IR accrual — §5) `[high]`.

**Directionality matters** (this is the practitioner subtlety): test **occurrence** by starting *from the books* and vouching back to a real shipment/receipt (catches pulled-forward / fictitious entries → overstatement). Test **completeness** by starting *from real-world evidence* (shipping log, receiving log) and tracing *into* the books (catches omissions → understatement) `[high]` (LegalClarity completeness; AccountingInsights excerpt).

**What a cutoff error looks like:**
- A December GL revenue entry whose bill of lading is dated January → **revenue overstatement** (occurrence failure).
- A receiving report dated Dec 28 with no corresponding accrual or payable → **expense/liability understatement** (completeness failure).
- A pattern of large sales clustered in the final days, reversing as returns early next period → **channel-stuffing red flag** (§5).

---

## 4. Accrual vs. provision vs. reserve — the terminology practitioners blur

These three words are used loosely, and even the codification uses them interchangeably for recorded loss contingencies `[high]` (Lexology/Deloitte roadmap). Sharper working definitions:

| Term | What it really is | Trigger / standard | Reverses? |
|---|---|---|---|
| **Accrual** | A known/estimable liability for goods or services already **received** (or revenue already earned). | Matching principle; obligation exists + estimable. | Usually a **reversing** accrual (true-ups via invoice). |
| **Provision** | An estimated liability for a **contingent** future outflow — warranty, restructuring, litigation, environmental. | **ASC 450-20**: accrue when loss is **probable** *and* **reasonably estimable**. | No — **rolled forward** and re-measured. |
| **Reserve** | Ambiguous. Most often a **contra-asset valuation account** (allowance for doubtful accounts, inventory reserve); sometimes an **appropriation of equity**. | Valuation/measurement, not a liability. | No — re-estimated each period. |

**ASC 450 thresholds (the load-bearing detail).** A loss contingency is *accrued* only when (1) it is **probable** a loss was incurred and (2) the amount is **reasonably estimable** `[high]` (ASC 450-20; PwC Viewpoint 23.4; Deloitte DART excerpts). "Probable" is read in practice as **significantly more than 50% / "likely"** — the codification assigns *no explicit percentage* `[high]`. If a loss is only **reasonably possible**, you **disclose but do not accrue**; if **remote**, generally nothing `[high]`. When a range is estimable but no point in it is better than another, **accrue the minimum** of the range `[high]` (ASC 450-20-30; the FASB Interpretation logic).

> **Decision tree — accrual vs. provision vs. prepaid vs. nothing**
> - Have goods/services been **received** (or revenue **earned**) by period end, amount known/estimable? → **Accrue** (`Dr Expense / Cr Accrued liability`; reverse next period).
> - Is it a **contingent** future loss (warranty, suit, restructuring)?
>   - **Probable AND estimable?** → **Provision / accrue per ASC 450** (no reversal; roll forward).
>   - **Reasonably possible**, or probable but **not estimable**? → **Disclose only**, no accrual.
>   - **Remote?** → **Nothing** (generally no disclosure).
> - Have you **paid in advance** for a future benefit not yet consumed? → **Prepaid asset** (deferral), amortize as consumed — *not* an accrual.
> - Is it a **valuation** of an existing asset (uncollectible AR, slow inventory)? → **Reserve / allowance** (contra-asset), re-estimate each period.

**On "reserve" specifically:** the SEC and the accounting profession have **discouraged the word "reserve"** because it is "not defined in any existing authoritative pronouncement" and misleads readers into thinking cash was set aside; the preferred term is **allowance** (e.g., *Allowance for Doubtful Accounts*) `[high]` (SEC EDGAR correspondence; AccountingCoach; AccountingTools). Controllers should treat "reserve" as a colloquialism and name the account by what it does.

---

## 5. Common cutoff errors

**Revenue (overstatement / occurrence) — the high-fraud-risk side:**
- **Holding the books open** ("keeping the period open") — recording early-January shipments as December revenue to hit a target `[high]`.
- **Channel stuffing** — shipping distributors more than they can sell near period end and booking the revenue now; often paired with **side agreements / extended return rights** that mean control never really transferred. The SEC has pursued this as revenue-recognition fraud; the tell is a late-period sales spike followed by early-next-period returns/credit notes `[high]` (CFI; Lexology; AccountingTools; Eduyush).
- **FOB term misapplication** — booking FOB-destination sales at shipment, or ignoring shipping terms entirely, so control-transfer timing is wrong `[high]`.

**Expense (understatement / completeness):**
- **Failing to accrue received-not-invoiced (GR/IR / GRNI)** — goods received before cutoff with the invoice still in transit. The valid treatment: accrue when the **receipt evidence is valid and the supplier liability is real**, even without the invoice; GR/IR is a temporary accrued liability that **reverses** when the AP voucher is matched `[high]` (PLANERGY; LegalClarity; ERP/Cetec docs). A stale, unreconciled GR/IR balance is a classic audit finding.
- **"Period 13" / soft-close adjustments** — using a special adjustment period to slip late entries; legitimate for true-ups, but a dumping ground for missed accruals and a cutoff-manipulation vector `[unverified — training knowledge]` (term is common ERP practice; not independently sourced this pass).
- **Capitalizing what should be expensed at cutoff** — pushing period-end repairs/supplies into fixed assets or inventory to defer expense and lift current income `[unverified — training knowledge]`.

---

## 6. How cutoff ties to the controller's reconciliation discipline

**Reconcile before you narrate.** A cutoff/accrual figure is only as trustworthy as the reconciliation behind it. The controllership sequence:

1. **Subledger-to-GL tie-out.** Each control account (AP, AR, inventory, fixed assets) must agree to its subledger; differences become *defined reconciling items* with explanations, not plugs `[high]` (Equility; Numeric; Dokka). Align scope/date → extract reports → quantify variance → classify reconciling items → certify with evidence.
2. **Accrual roll-forward.** Standing estimates (provisions, allowances, non-reversing accruals) are proven on a **roll-forward**: *opening balance + additions − releases/utilization = closing balance*, "starting with what you proved last month and explaining the movement" `[high]` (Numeric; Equility). Estimates must be **revisited when the actual invoice arrives** so books and ledger converge — the true-up discipline that keeps an estimate honest.
3. **Review / sign-off with segregation of duties.** The **preparer proposes, a separate reviewer approves/posts** — the preparer should not be able to both set subledger posting rules and approve JEs to control accounts `[high]` (Equility; Xenett). Certification = reviewer sign-off + attached supporting reports + retained audit trail (preparer/reviewer, date/time) `[high]`.

> **Cutoff governance rule:** no accrual or revenue cutoff entry is "done" until (a) it traces to a source document on the correct side of the boundary, (b) the affected control account ties to its subledger, (c) reversing items carry the auto-reversal flag and standing items sit on the roll-forward, and (d) a second person has signed off. Narrate the variance to FP&A *after* that, not before.

---

## Sources

- [FASB Concepts Statement No. 8 (ASC PDF)](https://asc.fasb.org/layoutComponents/getPdf?isSitesBucket=false&fileName=GUID-A28CBB4E-D14E-450F-A22D-5E6299E45A8B.pdf)
- [FASB Conceptual Framework (ICJCE mirror)](https://www.icjce.es/images/pdfs/TECNICA/C04%20-%20FASB/C42%20-%20FASB%20Statements/FASB%20Conceptual%20Framework.pdf)
- [PwC Viewpoint 23.4 Contingencies (ASC 450)](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/financial_statement_/financial_statement___18_US/chapter_23_commitmen_US/234_contingencies_US.html)
- [Deloitte DART — ASC 450 Loss Contingencies, Recognition](https://dart.deloitte.com/USDART/home/codification/liabilities/asc450-10/deloitte-s-roadmap-contingencies-loss-recoveries/chapter-2-loss-contingencies-commitments/2-3-recognition)
- [Deloitte DART — ASC 606 Revenue Recognized at a Point in Time](https://dart.deloitte.com/USDART/home/codification/revenue/asc606-10/roadmap-revenue-recognition/chapter-8-step-5-determine-when/8-6-revenue-recognized-a-point)
- [Lexology — Roadmap to accrual & disclosure under ASC 450](https://www.lexology.com/library/detail.aspx?g=c9a5dfb8-05c6-4757-a32d-e7a87251df2f)
- [RevenueHub — Revenue Recognition for Shipping Agreements](https://www.revenuehub.org/article/revenue-recognition-for-shipping-agreements)
- [GAAP Dynamics — ASC 606 Control / Revenue Recognition Criteria](https://www.gaapdynamics.com/dont-be-a-control-freak-revenue-recognition-criteria-asc-606/)
- [AccountingInsights — Cutoff Assertion in Auditing](https://accountinginsights.org/cutoff-assertion-in-auditing-key-transactions-risks-and-auditor-duties/) (HTTP 403 on fetch — cited from search excerpt)
- [Aurora Financials — Audit Cut-Off Testing](https://aurorafinancials.com/how-to-perfect-your-audit-cut-off-testing-expert-tips-that-work/)
- [maxwellcpareview — Auditing Revenue and Expenses](https://maxwellcpareview.com/cpa-articles/auditing-revenue-and-expenses)
- [LegalClarity — Testing the Completeness Assertion](https://legalclarity.org/how-auditors-test-the-completeness-assertion-2/)
- [KPM — Cutoff Rules When Reporting Revenue & Expenses](https://www.kpmcpa.com/cutoff-rules-when-reporting-revenue-expenses/)
- [AccountingVerse — Reversing Entries](https://www.accountingverse.com/accounting-basics/reversing-entries.html)
- [Wafeq — Reversing Entries](https://www.wafeq.com/en/learn-accounting/double-entry-accounting/reversing-entries)
- [Ramp — Accrued Expense Journal Entry](https://ramp.com/blog/accrued-expense-journal-entry)
- [FinQuery — Accrual Accounting Explained](https://finquery.com/blog/accrual-accounting-explained/)
- [Corporate Finance Institute — Channel Stuffing](https://corporatefinanceinstitute.com/resources/management/channel-stuffing/)
- [Lexology — Revenue Recognition Frauds: Channel Stuffing](https://www.lexology.com/library/detail.aspx?g=66b4261e-982f-4d2a-93d1-40ba30c4be67)
- [AccountingTools — Channel Stuffing](https://www.accountingtools.com/articles/channel-stuffing)
- [PLANERGY — GRNI Reconciliation](https://planergy.com/blog/grni-reconciliation-process-benefits/)
- [LegalClarity — Goods Received Not Invoiced: Accruals & Clearing](https://legalclarity.org/goods-received-not-invoiced-accruals-and-clearing-entries/)
- [Equility — GL to Subledger Reconciliation](https://www.equilityhq.com/blog/general-ledger-to-subledger-reconciliation-key-differences-significance)
- [Numeric — Balance Sheet Reconciliation](https://www.numeric.io/blog/balance-sheet-reconciliation)
- [SEC EDGAR — Letter re: "reserve" terminology](https://www.sec.gov/Archives/edgar/data/935007/000119312506126091/filename1.htm)
- [AccountingCoach — Reserve vs. Allowance](https://www.accountingcoach.com/blog/reserve-allowance)
