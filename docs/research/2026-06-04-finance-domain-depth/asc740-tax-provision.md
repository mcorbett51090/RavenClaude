# ASC 740 — Income Taxes (the Tax Provision): A Practitioner Synthesis

_Audience: controllers, tax-provision preparers, FP&A modelers. Date: 2026-06-04._

## Method note

This synthesis was built from a WebSearch fan-out across ~9 sub-topic queries (balance-sheet method, valuation allowances, uncertain tax positions, ETR/rate reconciliation, intraperiod allocation, interim reporting under 740-270, GAAP-vs-IFRS divergence, balance-sheet classification, naked credits, and common error modes). Source quality was prioritized as: FASB Codification subsection references → Big-4/large-firm income-tax guides (Deloitte Roadmap on DART, PwC "Income taxes" guide on Viewpoint, KPMG handbook, RSM whitepapers, BDO) → AICPA's _The Tax Adviser_ → corroborating practitioner content (Bloomberg Tax, Moss Adams, Baker Tilly, TaxOps, Forvis Mazars). **Blocked domains:** `dart.deloitte.com` (Deloitte DART), `rsmus.com` PDFs, and `pro.bloombergtax.com` all returned **HTTP 403** to WebFetch, so claims sourced from those are cited from the search-result excerpt and tagged accordingly; the KPMG handbook PDF and PwC Viewpoint pages were reachable. Load-bearing claims are confidence-tagged inline: `[high]` = codification or ≥2 independent authoritative sources; `[med]` = single authoritative source; `[unverified — training knowledge]` = recalled, not re-confirmed this session.

---

## 1. The shape of the provision: current + deferred

The **total income tax provision = current tax expense/benefit + deferred tax expense/benefit** `[high]` (corroborated by Bloomberg Tax, KPMG, RSM excerpts).

- **Current** tax = the tax actually payable/refundable on the **current year's taxable income** as computed on the return basis (book income ± permanent ± temporary differences → taxable income × current statutory rate, less credits).
- **Deferred** tax = the **period change in the net DTA/DTL balance** (including the change in any valuation allowance), measured at enacted rates. Deferred expense is the *plug* that makes total tax expense reflect both periods' economics, not just the cash tax.

A useful identity for modelers: `Deferred expense = (ending net DTL − beginning net DTL) = −(ending net DTA − beginning net DTA)`, adjusted for amounts booked to OCI/equity (intraperiod allocation, §7) and for the deferred-only effect of rate changes and VA changes.

> **Modeler's caution:** the deferred provision is *not* simply "temporary differences × rate." It is the **roll-forward of the deferred balances**. Items that bypass the income statement (OCI, equity, business-combination opening balances, rate-change remeasurement) move the balance without touching tax *expense* from continuing ops — backing them out is where naive three-statement models break.

---

## 2. The balance-sheet (liability) method

ASC 740 uses a **balance-sheet (a.k.a. liability) method**, not an income-statement method `[high]` (KPMG handbook; PwC §4.2; Bloomberg). The mechanic:

1. For each asset/liability, compare its **financial-statement carrying amount** to its **tax basis** in the relevant jurisdiction.
2. The difference is a **temporary difference** if it will produce taxable or deductible amounts when the carrying amount is recovered/settled.
3. Multiply the temporary difference by the **enacted tax rate expected to apply in the period the difference reverses** `[high]` — a **taxable** temporary difference → **DTL**; a **deductible** temporary difference (and carryforwards: NOLs, credits) → **DTA**.
4. Assess the DTA for realizability and record a **valuation allowance** if needed (§5).

**Enacted-rate rule (load-bearing):** deferred taxes are measured at the rate **enacted** under current law for the reversal period — *not* the rate management expects to be enacted, and *not* a "substantively enacted" rate `[high]`. The effect of a rate change is recognized **in the period of enactment**, as a discrete item (§6, §8). This is a hard GAAP/IFRS fork (§9).

---

## 3. Temporary vs. permanent differences

| | **Temporary difference** | **Permanent difference** |
|---|---|---|
| Definition | Book/tax basis differ now but **reverse** over time | Item in book income never in taxable income (or vice versa) — **never reverses** |
| Deferred tax? | **Yes** — creates a DTA or DTL | **No** — no deferred tax |
| Effect on ETR | **None** (reverses; affects timing of cash tax, not the rate) | **Moves the ETR** away from statutory |
| Examples | Depreciation (MACRS vs. book), accruals/reserves not yet deductible (warranty, bad-debt, comp), NOL/credit carryforwards, deferred revenue, capitalized R&D vs. book expense | Tax-exempt municipal interest, §162(m) excess officer comp, 50% of M&E, fines/penalties, certain stock-comp shortfalls, the GILTI/FDII *rate* effects, tax credits (R&D, FTC) |

**Why permanents move the ETR and temporaries don't:** the ETR = total tax expense ÷ pre-tax book income. A temporary difference changes *when* tax is paid but the **total** book tax expense over the item's life equals book pre-tax income × rate, so it nets to zero in the rate reconciliation. A permanent difference changes the **total** tax relative to book income permanently, so it is a standing reconciling item `[high]` (corroborated across The Tax Adviser, Bloomberg, KPMG).

> **Watch item — "permanent component of a temporary difference":** some items (e.g., certain stock comp) have a piece that will *never* be deductible embedded in an item that otherwise reverses. The permanent slice hits the ETR; the temporary slice goes to deferred. The Tax Adviser (Aug 2022) flags this as a recurring mis-classification `[med]`.

---

## 4. The effective tax rate (ETR) and the rate reconciliation

The **rate reconciliation** bridges the **statutory** rate (21% U.S. federal) to the **effective** rate, starting from `pre-tax book income × 21%` and adding/subtracting each driver `[high]`.

Common reconciling items (tax-expense impact and ETR direction):

| Reconciling item | Typical direction on ETR | Why |
|---|---|---|
| **Permanent differences** (nondeductible expense) | ↑ | adds tax with no book offset |
| **Tax-exempt income** (muni interest) | ↓ | book income with no tax |
| **State income taxes** (net of federal benefit) | ↑ | incremental jurisdictional tax |
| **Foreign tax credits (FTC)** | ↓ | credit, not deduction — dollar-for-dollar |
| **R&D credit** | ↓ | credit reduces tax directly |
| **GILTI** | ↑ (net) | inclusion of foreign income; partly offset by §250 deduction + FTC |
| **FDII** | ↓ | deduction lowers effective rate on qualifying export income |
| **Valuation allowance change** | ↑ or ↓ | establishing VA ↑ ETR; releasing VA ↓ ETR — often the single largest swing |
| **Uncertain tax positions (UTP)** | ↑ (build) / ↓ (release) | reserve accruals and reversals |
| **Stock-comp (SBC) windfall/shortfall** | ↓ (windfall) / ↑ (shortfall) | excess tax benefit/deficiency on vesting/exercise runs through tax expense (ASU 2016-09) `[high]` |

**SEC disclosure threshold (post ASU 2023-09):** public business entities must disaggregate any reconciling item ≥ **5%** of `pre-tax income × statutory rate` `[high]` (corroborated by The Tax Adviser Nov 2025 + PwC). FP&A note: this raises the cost of "other" buckets — drivers that used to hide in a catch-all now need standalone disclosure.

> **SBC ETR volatility (load-bearing):** since ASU 2016-09, the windfall/shortfall on stock comp flows through the **income-tax provision** as a discrete item in the period of vest/exercise, tied to the stock price. This makes the ETR **inherently volatile and hard to forecast** — a top cause of "why did our ETR move?" surprises and a recurring interim-modeling error (§8) `[high]`.

---

## 5. Valuation allowances (the realizability gate)

**Rule:** record a VA to reduce a DTA to the amount that is **more likely than not (> 50%)** to be realized `[high]` (ASC 740-10-30; corroborated Bloomberg, PwC §5.2, KPMG). The VA is the central judgment area and the most-second-guessed estimate in the provision.

### The four sources of future taxable income (ASC 740-10-30-18)

A DTA is realizable only to the extent one of these supports it `[high]` (Deloitte §5.3 excerpt; corroborated The Tax Adviser, PwC):

1. **Future reversals of existing taxable temporary differences** (existing DTLs that reverse in the right period/character).
2. **Future taxable income** exclusive of reversing temporary differences and carryforwards (i.e., projected operating income).
3. **Taxable income in prior carryback year(s)**, where carryback is permitted under the tax law.
4. **Tax-planning strategies** — prudent, feasible actions management would take to realize the DTA before it expires.

### Evidence weighting — decision tree

```
Assess all positive AND negative evidence for the DTA (by jurisdiction / tax-paying component)
│
├─ Is there a CUMULATIVE LOSS in recent years (typically 3-yr)?  ── YES ─┐
│                                                                        │  This is SIGNIFICANT NEGATIVE evidence.
│                                                                        │  Objectively-verifiable negative evidence
│                                                                        │  outweighs subjective positive projections.
│                                                                        ▼
│                                          Can positive evidence of the SAME objective weight
│                                          overcome it? (firm backlog, signed contracts,
│                                          reversing DTLs of right character/timing, viable
│                                          tax-planning strategy, carryback capacity)
│                                              │
│                                              ├─ NO  → RECORD FULL VALUATION ALLOWANCE
│                                              │         (most common outcome for cumulative-loss cos.)
│                                              └─ YES → Partial / no VA — document heavily
│
└─ NO cumulative loss ─► Weight evidence; is realization of each DTA piece MLTN (>50%)?
                          ├─ YES for all → No VA
                          └─ NO for some → Partial VA on the unsupported portion
```

**Decision rules baked in:**
- **Objectivity beats optimism.** What has already occurred (verifiable) outweighs projections (not verifiable) `[high]`. "The more negative evidence exists, the more positive evidence is necessary." 
- **Cumulative loss in recent years is negative evidence that is hard to overcome** `[high]` — a near-bright-line trigger reviewers look for first.
- **Naked credits / indefinite-lived DTLs are NOT a valid source.** A DTL on goodwill or an indefinite-lived intangible ("naked credit" / "hanging credit") generally **cannot** be a source of future taxable income, because its reversal is contingent on an indefinite-future sale or impairment — the timing is unknowable, so it can't be scheduled against a finite-lived DTA `[high]` (The Tax Adviser; PwC §10.4/§2.4 excerpts; Forvis Mazars). _Post-2017 nuance: indefinite-lived NOLs (TCJA) can absorb some indefinite-lived DTL reversals, partially relieving the classic naked-credit problem `[med]`._

> **VA release** (going from full VA to none, e.g., after sustained profitability) is a large favorable discrete hit to the ETR and a frequent **earnings-quality flag** — auditors scrutinize the timing closely.

---

## 6. Uncertain tax positions (UTPs) — the two-step model

ASC 740-10 keeps a **two-step** model (legacy FIN 48), assuming the position *will* be examined by an authority with full knowledge `[high]` (Bloomberg, Accounting Insights, KPMG, Deloitte Ch.4 excerpts):

```
STEP 1 — RECOGNITION (ASC 740-10-25)
  Is it MORE LIKELY THAN NOT (>50%) the position will be SUSTAINED on its
  TECHNICAL MERITS, assuming examination by a tax authority with full knowledge?
   │
   ├─ NO  → Recognize NO benefit. Record full liability for the
   │         unrecognized tax benefit (UTB). Stop.
   │
   └─ YES → proceed to Step 2.

STEP 2 — MEASUREMENT (ASC 740-10-30-7)
  Recognize the LARGEST amount of benefit that is > 50% likely (CUMULATIVE
  probability) to be realized on ultimate settlement.
   │
   └─ Build a table of possible outcomes with individual probabilities,
      accumulate from the largest benefit down until cumulative prob > 50%.
      That outcome's benefit is what you recognize; the remainder is the UTB.
```

**Worked logic for Step 2:** if a $100 deduction has outcomes {$100 @ 25%, $80 @ 30%, $60 @ 25%, $0 @ 20%}, cumulative probability reaches >50% at the **$80** level (25%+30%=55%), so recognize **$80** of benefit; the $20 difference is the unrecognized tax benefit `[high]` (method corroborated across sources; figures illustrative).

**Other UTP mechanics:**
- **Interest & penalties:** policy election — classify interest as income tax *or* interest expense; penalties as income tax *or* other expense; apply consistently (ASC 740-10-45-25) `[high]`.
- **Subsequent changes** (new info, audit settlement, statute-of-limitations lapse) re-measure the UTB; a SOL lapse is a **discrete** item in the interim period it occurs (§8) `[med]`.
- ASU 2023-09 expands UTP/rate-rec disclosure (effective for PBEs annual periods beginning after Dec 15, 2024) `[med]`.

---

## 7. Intraperiod tax allocation

Total tax for the period is **allocated** across financial-statement components without changing the total: **continuing operations, discontinued operations, OCI, and items charged/credited directly to equity** `[high]` (PwC Ch.12; Deloitte Ch.6).

**Mechanic — the "with-and-without" / incremental approach:**
1. First, compute tax on **continuing operations** as if it were the only component.
2. Then allocate the *remaining* total tax to the other components on an **incremental** basis (each component's incremental effect).

**Key exception change (ASU 2019-12, load-bearing):** the FASB **removed** the old exception that required considering income from *other* components when there was a **loss from continuing operations**. Now you determine the tax on continuing operations **without** regard to the tax effects of items outside continuing operations `[high]` (PwC; BDO). This simplified—but did not eliminate—the allocation; OCI, discontinued ops, and equity items still get their incremental share.

> **Practitioner trap:** "backwards tracing" of stranded tax effects in **AOCI** is *not* permitted under GAAP the way it is conceptually under IFRS; the stranded effect generally remains until the underlying item is sold/extinguished (ASU 2018-02 gave a one-time reclassification election for the 2017 rate-change stranding only) `[med]`.

---

## 8. Interim reporting — ASC 740-270 (the estimated annual ETR)

Interim tax is **not** "this quarter's pre-tax income × statutory rate." Under ASC 740-270 `[high]` (Bloomberg, Moss Adams, Baker Tilly, Deloitte Ch.7):

```
1. Project the ESTIMATED ANNUAL EFFECTIVE TAX RATE (AETR) on ORDINARY income
   = forecast full-year tax on ordinary income ÷ forecast full-year ordinary pre-tax income.
2. Apply AETR to YEAR-TO-DATE ordinary income → YTD tax on ordinary income.
3. Interim-period tax on ordinary income = YTD tax − tax recognized in prior interim periods.
4. ADD discrete items, computed individually IN the period they occur.
```

**Discrete items (recognized in the period, NOT in the AETR):** changes to a **prior-year-end** valuation allowance, effects of **enacted** tax-law/rate changes (in the enactment period), settlement/SOL-lapse of UTPs, stock-comp windfalls/shortfalls, and other unusual/infrequent items `[high]`. (Note: a change to a VA on a DTA *created in the current year* goes **into** the AETR, not discrete — a frequently-missed split `[med]`.)

**Special-case rules** practitioners must remember:
- If a reliable AETR estimate **cannot** be made (e.g., small pre-tax income makes the rate hyper-sensitive), use the **actual YTD effective rate** `[med]`.
- **Loss-limitation cap:** the tax benefit of a YTD ordinary loss is limited to what is realizable; you cannot record a benefit you don't expect to realize (interaction with the VA assessment) `[med]`.
- Jurisdictions with losses for which **no benefit** is recognized are excluded from the consolidated AETR and handled separately `[med]`.

---

## 9. US GAAP vs. IAS 12 — the divergences that matter

| Topic | **US GAAP (ASC 740)** | **IFRS (IAS 12 / IFRIC 23)** |
|---|---|---|
| **Uncertain tax positions** | **Two-step**: (1) MLTN recognition on technical merits, (2) largest amount >50% cumulative probability `[high]` | **Single-step** under IFRIC 23: reflect uncertainty using **most-likely-amount** *or* **expected-value**, whichever better predicts resolution `[high]`. No separate recognition gate; measurement methods can yield different numbers. |
| **DTA realizability** | DTA recognized in full, then reduced by a **valuation allowance** if not MLTN realizable (gross-then-allowance) `[high]` | DTA recognized **only to the extent realization is probable** (≈MLTN) — net recognition, **no separate VA account** `[high]` |
| **Tax-rate basis** | **Enacted** rate only `[high]` | **Enacted or substantively enacted** rate `[high]` — timing of recognizing a rate change can differ by a reporting period |
| **DTA/DTL classification** | **All noncurrent** since ASU 2015-17 (PBEs: periods beginning after Dec 15, 2016) `[high]` | **All noncurrent** under IAS 1 `[high]` — **converged here**; the old current/noncurrent split is gone under both |
| **Interest & penalties** | Policy election: tax vs. interest/other expense `[high]` | IAS 1 presentation applies; no equivalent codified election `[med]` |
| **Outside basis / intra-group transfers** | Several specific exceptions (e.g., APB 23 indefinite-reinvestment for foreign subs) `[med — unverified detail]` | IAS 12 has its own (narrower) exceptions; intra-group asset transfers recognize tax immediately (no GAAP-style deferral) `[med]` |

The two-step vs. single-step UTP fork and the **enacted vs. substantively-enacted** rate fork are the two divergences most likely to change a reported number for a dual-reporter. Classification is **converged** (all noncurrent) — confirmed both directions `[high]`.

---

## 10. Integrating the provision into the close and a three-statement model

**The provision build (close workflow):**
```
Pre-tax BOOK income
  ± Permanent differences            → affects current tax & ETR only
  ± Temporary differences            → affects current tax now; reverses into deferred
  = Taxable income
  × current statutory rate − credits = CURRENT tax expense (→ income tax payable)
Roll DTA/DTL schedule (begin → end), incl. VA change & enacted-rate remeasurement
  = DEFERRED tax expense
CURRENT + DEFERRED = TOTAL provision  → ties to ETR × pre-tax book income
```

**Where it lands:**
- **Income statement:** total provision (continuing ops portion) as "Income tax expense"; discontinued-ops tax sits within that line.
- **Balance sheet:** income taxes **payable/receivable** (current); net **DTA/DTL** as a single **noncurrent** amount per tax jurisdiction/component (ASU 2015-17) `[high]`; UTB liability (often noncurrent unless cash settlement expected <12 mo).
- **Cash flow:** start from net income, **add back deferred tax expense** (non-cash) in the operating section; the change in taxes payable is a working-capital line. Cash taxes paid is a required supplemental disclosure.

**Return-to-provision (RTP) true-up:** when the actual return is filed, the estimate booked in the provision is trued up `[high]`. **Permanent-item** RTP differences hit **tax expense**; **temporary-item** RTP differences are generally a **reclass between payable/receivable and the DTA/DTL** (no expense impact) — distinguishing a *change in estimate* (prospective) from an *error* (restatement) is a documented judgment `[high]` (TaxOps).

---

## 11. The common practitioner error modes

Curated from befreeltd, TaxOps, Forvis Mazars, Moss Adams, and the firm guides `[high]` unless noted:

1. **Wrong enacted rate / enactment timing.** Using an expected (not enacted) rate, or recognizing a rate change in the wrong period — rate changes are **discrete in the enactment period**, applied to *all* deferreds.
2. **Missing a valuation-allowance trigger** — most often ignoring a **cumulative loss** as significant negative evidence, or over-relying on un-verifiable projections.
3. **Blending current and deferred incorrectly** — putting a permanent difference into the deferred roll, or a temporary difference into the ETR; both distort deferred balances and the rate rec.
4. **Naive interim ETR** — applying YTD statutory rate instead of the **AETR under 740-270**, or mis-sorting discrete items (esp. the **current-year vs. prior-year-end VA change** split).
5. **Forgetting RTP true-ups**, or mis-classifying an RTP difference (permanent → expense vs. temporary → balance-sheet reclass), or treating a true-up as an error.
6. **SBC windfall/shortfall surprises** — not modeling the stock-price-driven discrete benefit/deficiency, producing ETR forecast misses.
7. **Treating naked credits / indefinite-lived DTLs as a source of taxable income** for VA support (§5) — a classic realization overstatement.
8. **Deferred roll-forward that doesn't tie** to the prior-year provision — opening balances unexplained turns review into reconstruction `[high]`.
9. **Mis-applying intraperiod allocation** post-ASU 2019-12 (still considering other components when computing continuing-ops tax during a loss year).
10. **State taxes done in aggregate** — failing to account for apportionment, conformity, and rate differences by state; The Tax Adviser flags this as a persistent due-diligence gap `[med]`.

---

## Sources

- [Deloitte Roadmap — ASC 740 (DART): 5.3 Sources of Taxable Income; Ch.4 Uncertainty; Ch.6 Intraperiod; Ch.7 Interim; App. E differences; 13.2 classification](https://dart.deloitte.com/USDART/home/codification/expenses/asc740-10/deloitte-s-roadmap-income-taxes/) — _403 to WebFetch; cited from search excerpts._
- [PwC Income taxes guide (Viewpoint): 4.2 basic approach; 5.2 valuation allowance; 10.4/2.4 DTA/DTL & exceptions; Ch.12 intraperiod; 16.3 classification](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/income_taxes/income_taxes__16_US.html)
- [KPMG — Accounting for income taxes Handbook (US GAAP), July 2024 (PDF)](https://kpmg.com/kpmg-us/content/dam/kpmg/frv/pdf/2024/accounting-for-income-taxes.pdf)
- [RSM — U.S. GAAP vs. IFRS: Income taxes (PDF); Interim period tax reporting; Current & deferred taxes; Uncertain tax positions](https://rsmus.com/insights/services/business-tax/assessing-the-need-for-a-valuation-allowance.html) — _PDF 403 to WebFetch; cited from search excerpts._
- [Bloomberg Tax — ASC 740 Tax Provision Guide; Valuation Allowances; Two-Step UTP; Interim Reporting; Reporting & Disclosure](https://pro.bloombergtax.com/insights/provision/how-to-calculate-the-asc-740-tax-provision/) — _403 to WebFetch; cited from search excerpts._
- [The Tax Adviser (AICPA) — Assessing the need for a valuation allowance; Indefinite-lived assets / naked credits; Permanent component of a temporary difference; State taxes due diligence; Updated 740 footnote (Nov 2025)](https://www.thetaxadviser.com/issues/2023/apr/assessing-the-need-for-a-valuation-allowance/)
- [BDO — One Big Beautiful Bill Act implications for income taxes; Pillar Two; FASB Simplifies Accounting for Income Taxes (ASU 2019-12)](https://www.bdo.com/insights/tax/one-big-beautiful-bill-act-implications-for-accounting-for-income-taxes)
- [Moss Adams / Baker Tilly — ASC 740-270 Q1 impacts (interim AETR & discrete items)](https://www.mossadams.com/articles/2024/04/asc-740-270-q1-impacts)
- [TaxOps — Return-to-provision adjustment; Getting ASC 740 right (errors)](https://taxops.com/navigating-return-to-provision-adjustment-in-asc-740/)
- [befreeltd — Common ASC 740 tax provision errors](https://befreeltd.com/us/resources/blogs/common-asc-740-income-tax-provision-errors/)
- [Forvis Mazars — Common income tax accounting pitfalls](https://www.forvismazars.us/forsights/2023/12/common-income-tax-accounting-pitfalls)
- [GAAP Dynamics — UTP under IFRS (IFRIC 23) vs ASC 740](https://www.gaapdynamics.com/the-guidance-is-clear-uncertain-tax-positions-and-ifrs-ifric-23/)
- [Journal of Accountancy / CPA Journal — ASU 2015-17 noncurrent deferred-tax classification](https://www.journalofaccountancy.com/news/2015/nov/deferred-taxes-balance-sheet-201513434/)
