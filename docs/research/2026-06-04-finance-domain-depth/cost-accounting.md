# Cost Accounting (Managerial + Inventory Costing): A Practitioner Synthesis

_Audience: controllers, cost accountants, FP&A, manufacturing finance. Date: 2026-06-04._

## Method note

This synthesis fans across nine WebSearch queries covering: ASC 330 normal-capacity absorption and abnormal-cost period treatment; ASU 2015-11 (LCM → LCNRV) and its LIFO/retail exception; absorption-vs-variable income divergence; job/process/hybrid costing; activity-based costing (ABC) and time-driven ABC (TDABC) limits; the full standard-cost variance set and fixed-overhead volume variance; variance disposition (proration vs COGS); predetermined overhead rate and under-/over-applied disposition; cost behavior / CVP; the cost-of-goods-manufactured (COGM) schedule; and US GAAP vs IFRS (IAS 2) divergence. **Source quality:** authoritative — the FASB ASU 2015-11 PDF and Codification language (via SEC EDGAR and PwC Viewpoint excerpts), KPMG and RSM GAAP-vs-IFRS comparisons, OpenStax/LibreTexts/Saylor managerial-accounting texts, AccountingCoach, CFI, AccountingTools, and peer-reviewed TDABC literature. **Blocked domains:** PwC Viewpoint (`viewpoint.pwc.com`), AccountingVerse, and Saylor (`saylordotorg.github.io`) returned HTTP 403 on WebFetch; for those I relied on the search-result excerpts plus independent corroboration, and flag any claim resting on a single excerpt as `[med]`. Variance formulas are standard managerial-accounting canon corroborated across ≥2 of {AccountingCoach, OpenStax, LibreTexts, principlesofaccounting} `[high]`.

**Confidence convention:** `[high]` = codification/standard or ≥2 independent authoritative sources; `[med]` = single authoritative source; `[unverified — training knowledge]` = recalled, not re-grounded this session.

---

## 1. The framing a controller actually needs

Cost accounting splits into two jobs that share machinery but answer to different masters:

- **Inventory costing for external reporting** — governed by **ASC 330** (US GAAP) and **IAS 2** (IFRS). The constraint is the standard; the answer must be defensible to auditors and the SEC. **Absorption (full) costing is mandatory** here. `[high]`
- **Managerial / decision costing** — governed by relevance and judgment, not by a standard. Variable costing, contribution margin, ABC, and CVP live here. They are *internal-only* and may freely diverge from the GAAP inventory number. `[high]`

The recurring practitioner failure is letting the wrong frame leak into the other: shipping variable-costing inventory to the balance sheet (a GAAP violation), or feeding fully-absorbed unit cost (with allocated fixed overhead) into a make-or-drop decision (a relevance error). Keep the two ledgers of thought separate.

---

## 2. Product / inventory costing methods

### 2.1 Job-order vs process vs operation (hybrid) costing

The choice is dictated by **product heterogeneity and cost-traceability**, not by industry label. `[high]`

- **Job-order costing** — costs accumulate per **job/batch**. Use when output is custom or in distinct lots and direct costs trace cleanly to a unit (construction, aircraft, custom machining, professional services, print-to-order). `[high]`
- **Process costing** — costs accumulate per **process/department** and are smeared over equivalent units. Use for continuous, homogeneous mass production where per-unit tracing is uneconomic (chemicals, refining, food, paper, CPG). `[high]`
- **Operation / hybrid costing** — combines both: process costing for common conversion steps, job costing for the customizing steps. Use when a common platform is finished into variants (autos, apparel, configurable electronics). `[high]`

**Decision tree — which product-costing system:**

```
Are units distinct, custom, or made-to-order with directly traceable costs?
├─ YES → are they grouped in identifiable batches/lots?
│        ├─ YES → JOB-ORDER costing (cost per job/batch)
│        └─ NO (one-off projects) → JOB-ORDER / project costing
└─ NO (homogeneous, continuous, mass) →
         Is there a common process AND a later customizing step?
         ├─ YES → OPERATION / HYBRID costing
         │        (process cost the common steps, job cost the variants)
         └─ NO  → PROCESS costing (cost per dept, equivalent units)
```

Note: the costing **method** (job/process/hybrid) is orthogonal to the **cost-measurement basis** (actual / normal / standard) and to the **inventory cost-flow assumption** (FIFO / weighted-average / LIFO). A plant can run *process costing on a standard-cost basis with weighted-average flow*. Don't conflate the three axes.

### 2.2 Activity-based costing (ABC)

ABC replaces a single volume-based allocation with multiple **cost pools**, each drained by its own **cost driver** that reflects actual resource consumption. `[high]` Hierarchy of activities (and natural drivers):

| Activity level | Examples | Driver |
|---|---|---|
| Unit-level | machining, assembly | machine hours, units |
| Batch-level | setups, inspections, material moves | # setups, # inspections |
| Product-level | engineering, BOM maintenance | # products, ECN count |
| Facility-level | plant rent, plant management | (often NOT assignable to product — period or arbitrary) |

**When ABC beats traditional allocation** — ABC's payoff rises with: **product-mix diversity** (high- vs low-volume products sharing a plant); **a high and growing proportion of overhead** to direct labor; and **batch/complexity costs that don't scale with volume** (many setups for small runs). `[high]` Traditional plantwide volume allocation then commits **cost smoothing/cross-subsidization**: high-volume simple products are *over-costed* and low-volume complex products are *under-costed*, because the complex products consume disproportionate batch/setup resources that a labor-hour rate spreads evenly. `[high]`

**When ABC is *not* worth it** — when overhead is small, products are homogeneous, or the maintenance burden of estimating driver quantities exceeds the decision value. Classic ABC is data-hungry and decays; **Time-Driven ABC (TDABC)** was created to cut that cost (model capacity-cost-rate × time per transaction, via time equations), but TDABC carries its own errors — estimation error in the time equations and input-data error — and is still too heavy for small operations. `[high]`

**The capacity / death-spiral trap (load-bearing):** if you allocate the cost of *idle/unused* capacity into product cost, unit cost rises → price rises or the product looks unprofitable → volume drops → even more idle capacity → unit cost rises again. ABC/TDABC's discipline is to **cost products at the practical-capacity rate and route the cost of unused capacity to a period expense**, not onto the surviving products. `[high]` (This is the same principle ASC 330 enforces for GAAP — see §5.)

---

## 3. Absorption (full) vs variable (direct) costing

| | Absorption (full) | Variable (direct) |
|---|---|---|
| **Fixed mfg overhead** | **product cost** — capitalized into inventory | **period cost** — expensed as incurred |
| **Inventoriable cost** | DM + DL + variable OH + fixed OH | DM + DL + variable OH |
| **External GAAP/IFRS?** | **Required** | **Prohibited** for inventory valuation |
| **Income statement form** | gross-margin format | contribution-margin format |
| **Income moves with** | production *and* sales | sales only |

**GAAP requires absorption** for external reporting and inventory valuation — fixed manufacturing overhead is a product cost under ASC 330. `[high]` Variable costing is an internal-decision tool only. `[high]`

### 3.1 The income divergence (the core mechanic)

When **production ≠ sales**, the two methods report different operating income, and the gap is exactly:

> **Δ income = (units produced − units sold) × fixed manufacturing overhead per unit** `[high]`

- **Production > sales (inventory builds):** absorption income **>** variable income, because fixed overhead attached to the unsold units is **deferred in ending inventory** instead of expensed. `[high]`
- **Production < sales (inventory draws down):** absorption income **<** variable income, because fixed overhead deferred in *prior* periods is **released from inventory** into this period's COGS. `[high]`
- **Production = sales:** the two converge. `[high]`

_Worked illustration (corroborated): produce 15,000, sell 12,000, fixed OH $10/unit → absorption defers 3,000 × $10 = $30,000 of fixed overhead into ending inventory, so absorption income is $30,000 higher than variable that period._ `[high]`

### 3.2 Why variable costing kills the produce-to-inventory game

Under absorption, a manager can **lift reported income by overproducing** — building inventory parks fixed overhead on the balance sheet rather than the P&L. Variable costing expenses all fixed overhead in-period, so income tracks **sales, not production**, removing the incentive. `[high]` This is the single most important reason internal performance reporting and incentive comp often run on contribution-margin (variable) statements even though the books close on absorption.

**Decision tree — absorption vs variable, which for which purpose:**

```
What is the number for?
├─ External financial statements / tax / GAAP inventory → ABSORPTION (required)
├─ Internal short-run decision (special order, make-or-buy,
│   drop-a-product, pricing a marginal unit) → VARIABLE / contribution
│   (exclude unavoidable fixed OH; use only relevant/incremental costs)
├─ Performance eval / incentive comp where you must NOT
│   reward building inventory → VARIABLE (income tracks sales)
└─ Long-run pricing that must recover full cost → ABSORPTION or ABC
    (a sustained price below full cost erodes capital)
```

Caveat on §3.2 leaf: contribution analysis is a **short-run** tool. Repeatedly pricing at variable cost ignores fixed-capacity recovery; over the long run prices must cover fully-absorbed (or ABC) cost.

---

## 4. Standard costing & variance analysis

Standard costing books inventory at predetermined (standard) costs and isolates the difference from actual as **variances**. Notation: **AQ** actual qty, **SQ** standard qty allowed for actual output, **AP/AR** actual price/rate, **SP/SR** standard price/rate. Sign convention throughout: **actual > standard cost ⇒ Unfavorable (U); actual < standard ⇒ Favorable (F).** `[high]`

### 4.1 The full variance set

**Direct materials**
- **Price variance (MPV)** = (AP − SP) × AQ `[high]`
- **Quantity / usage variance (MQV)** = (AQ − SQ) × SP `[high]`
- **Purchase Price Variance (PPV):** the materials price variance computed on **quantity purchased** (not used) so the variance is isolated at receipt and inventory carries standard cost. Computing it on quantity *used* defers recognition. Most ERP systems book PPV at PO receipt/invoice. `[high]`

**Direct labor**
- **Rate variance (LRV)** = (AR − SR) × AH `[high]`
- **Efficiency variance (LEV)** = (AH − SH) × SR `[high]`

**Variable overhead**
- **Spending variance** = actual VOH − (AH × standard VOH rate) `[high]`
- **Efficiency variance** = (AH − SH) × standard VOH rate `[high]` — note this captures *only* the inefficiency in the **allocation base**, not in spending.

**Fixed overhead**
- **Spending / budget variance** = actual fixed OH − budgeted fixed OH `[high]`
- **Production-volume variance** = budgeted fixed OH − applied fixed OH = (denominator/normal-capacity hours − standard hours for actual output) × fixed OH rate `[high]`
  - This variance is **purely an artifact of the denominator choice** — it measures whether you produced at the activity level assumed when setting the rate. It has **no spending meaning**; an unfavorable volume variance signals under-utilization of capacity, not overspending. `[high]` (Many practitioners over-read it.)

A clean reconciliation: total flexible-budget overhead variance = spending variances; total volume variance = the fixed-OH production-volume piece only. Variable OH has **no** volume variance (variable costs flex with the base).

### 4.2 Variance disposition at period end

**Decision tree — variance disposition:**

```
Is the aggregate variance IMMATERIAL (qualitatively + quantitatively;
no fixed % bright line — SEC rejects automatic thresholds)?
├─ YES → write the entire variance to COGS (expense in period)
└─ NO (material) → is it driven by ABNORMAL causes
     (idle capacity, abnormal spoilage/freight, gross inefficiency)?
     ├─ YES → expense the abnormal portion to the P&L now
     │        (ASC 330: NOT inventoriable — see §5); prorate only the
     │        "normal" residual
     └─ NO (normal operating variance) → PRORATE across the accounts
          where the standard costs reside: Raw Materials, WIP,
          Finished Goods, and COGS, so ending inventory approximates
          actual cost
```

Mechanics: prorate **material** variances on the relative direct-material balances in RM/WIP/FG/COGS; prorate **labor and overhead** variances on relative conversion (DL or DL-based) cost in WIP/FG/COGS. `[high]` The materiality line is judgment, not a number — a common rule-of-thumb writes variances under ~5% of standard cost straight to COGS, but the SEC has explicitly **rejected any fixed percentage as an automatic bright line**, requiring quantitative *and* qualitative analysis. `[high]` Practitioner failure mode: dumping a large, *favorable* variance entirely into COGS, which understates inventory and overstates current margin — proration is required precisely so the balance sheet reflects something close to actual cost. `[med]`

---

## 5. Overhead allocation, capacity, and the ASC 330 normal-capacity rule

### 5.1 Predetermined overhead rate and applied overhead

**Predetermined OH rate = estimated overhead ÷ estimated allocation base** (DL hours, DL dollars, machine hours, or DM cost), set at the start of the period and applied as production occurs. `[high]` At period end:

- **Applied > actual ⇒ over-applied overhead** (generally favorable: spent less than absorbed). `[high]`
- **Applied < actual ⇒ under-applied overhead.** `[high]`

Dispose of the balance by (a) writing it to COGS if immaterial, or (b) prorating across WIP / FG / COGS in proportion to the overhead in each — the theoretically correct route when the amount is material. `[high]`

**Plantwide vs departmental vs ABC rates:** a single plantwide rate is acceptable only when overhead consumption is uniform across products. With diverse product mix or unlike departments (a labor-intensive line and a machine-intensive line under one roof), a plantwide rate **cross-subsidizes** — move to departmental rates, or ABC if batch/complexity costs dominate. `[high]` Using a plantwide rate on a diverse mix is one of the most common real-world costing errors (§7).

### 5.2 Capacity-level choice — the denominator decision

The activity level in the rate denominator changes both unit cost and the volume variance:

| Capacity basis | Definition | Effect |
|---|---|---|
| **Theoretical** | max output, no stoppages — unattainable | lowest unit cost; huge chronic unfavorable volume variance |
| **Practical** | theoretical less unavoidable downtime | the basis ASC 330 effectively favors; idle cost surfaces as period expense |
| **Normal** | average demand over several years/cycles | smooths seasonality; ASC 330-acceptable |
| **Master-budget / expected** | next period's expected volume | ties cost to one year's demand; can feed the death spiral |

`[med]` on the table's fine distinctions (single-source-leaning); the **normal-capacity** requirement itself is `[high]`.

### 5.3 ASC 330 normal-capacity rule (the GAAP guardrail)

ASC 330-10-30 fixes the absorption of **fixed production overhead** to the **normal capacity** of the facilities — the production expected over several periods under normal circumstances, net of planned maintenance, treated as a *range*. `[high]` The load-bearing consequences:

1. **The per-unit fixed-overhead charge is NOT increased because of abnormally low production or an idle plant.** `[high]`
2. **Unabsorbed fixed overhead from abnormally low volume is a period expense** — recognized in the period incurred, **not** capitalized into inventory. `[high]` This is GAAP's codified version of the §2.2 "don't park idle-capacity cost in product" rule.
3. **Abnormal freight, handling, and spoilage (wasted material) are current-period charges, never inventoriable.** `[high]`
4. In **high** production periods, the per-unit fixed-overhead charge **is** reduced (so inventory isn't measured above cost). `[med]`

So a controller closing a low-volume quarter cannot let standard absorption "soak up" fixed overhead into ending inventory to flatter gross margin — the abnormal idle portion must hit the P&L. Capitalizing abnormal idle capacity is both a GAAP violation and an income-inflation game (§7).

---

## 6. Cost behavior & CVP

**Cost behavior** within the **relevant range**: **variable** (total varies with volume, unit constant), **fixed** (total constant, unit declines with volume), **mixed/semi-variable** (both). The relevant range is the band over which these patterns hold — extrapolating outside it is a classic error. `[high]`

**Estimating the fixed/variable split:**
- **High-low method** — variable rate = (cost at high − cost at low) ÷ (activity high − low); fast but uses only two points and is sensitive to outliers. `[high]`
- **Regression (least-squares)** — uses all observations; preferred for reliability and gives R² as a fit diagnostic. `[high]`

**CVP toolkit:**
- **Contribution margin (CM)** = sales − variable costs; **CM ratio** = CM ÷ sales. `[high]`
- **Break-even (units)** = fixed costs ÷ CM per unit; **break-even ($)** = fixed costs ÷ CM ratio. `[high]`
- **Target-profit units** = (fixed costs + target profit) ÷ CM per unit. `[high]`
- **Margin of safety** = current (or budgeted) sales − break-even sales; zero at break-even. `[high]`
- **Degree of operating leverage (DOL)** = CM ÷ operating income. High DOL (fixed-cost-heavy structure) means a small sales change produces a large profit swing — upside *and* downside. `[high]`

The **contribution-margin income statement** (sales − variable = CM − fixed = operating income) is the CVP/variable-costing form; it differs from the **absorption (gross-margin) statement** (sales − COGS = gross margin − operating expenses). Don't compute break-even off an absorption statement — fixed manufacturing overhead is buried in COGS and unit cost there is volume-dependent. `[high]`

CVP assumptions to flag: linear costs/revenues in the relevant range, constant sales mix, production = sales (so it ties to variable costing), and volume as the sole cost driver. Supplement with sensitivity/scenario analysis. `[high]`

---

## 7. Cost flows & the controller's close

### 7.1 The flow and the COGM schedule

Costs flow: **Raw Materials → Work-in-Process → Finished Goods → COGS.** `[high]` Each transfer obeys: *beginning balance + additions − ending balance = transferred out.* `[high]`

**Cost of Goods Manufactured (COGM):**

```
Direct materials used
  = Beg. RM + RM purchases − End. RM
+ Direct labor
+ Manufacturing overhead applied
= Total manufacturing costs
+ Beginning WIP
− Ending WIP
= COST OF GOODS MANUFACTURED (COGM)        [high]

Cost of Goods Sold:
  Beginning FG + COGM − Ending FG = COGS     [high]
```

### 7.2 Where it meets the close

- **Inventory valuation** must be absorption-based and respect the ASC 330 normal-capacity rule (§5.3) — abnormal idle/spoilage/freight stripped to period expense before inventory is struck.
- **Variance capitalization** — material normal variances prorated into RM/WIP/FG so the balance-sheet inventory approximates actual cost; abnormal variances expensed (§4.2).
- **LCM / LCNRV write-down** — the final inventory haircut, per §8.

### 7.3 Most common practitioner errors (consolidated)

1. **Plantwide rate on a diverse product mix** → cross-subsidization; high-volume simple products over-costed, low-volume complex products under-costed. Fix: departmental or ABC rates. `[high]`
2. **Treating fixed overhead as variable in a decision** — using fully-absorbed unit cost (with allocated fixed OH) in a special-order/make-or-buy/drop call. Fix: use relevant/incremental (variable + avoidable fixed) costs only. `[high]`
3. **Mis-disposing variances** — dumping a *material* (especially favorable) variance entirely into COGS, distorting inventory and margin; or proration when immaterial (needless effort). `[med]`
4. **Capitalizing abnormal idle capacity / spoilage / freight** into inventory — a direct ASC 330 violation and an income-inflation move. `[high]`
5. **Absorption-costing income games** — overproducing to defer fixed overhead into inventory and lift reported income. Detect via the (production − sales) × fixed-OH-per-unit bridge; report performance on variable costing. `[high]`
6. **Over-reading the fixed-overhead volume variance** as overspending when it is purely a denominator/utilization artifact. `[high]`
7. **Computing break-even off an absorption statement** — fixed OH hidden in COGS. Use the contribution-margin statement. `[high]`
8. **Allocating unused-capacity cost onto surviving products** → the death spiral. Cost at practical capacity; route unused-capacity cost to period expense. `[high]`

---

## 8. US GAAP vs IFRS divergence (must-know for dual reporters)

| Topic | US GAAP (ASC 330) | IFRS (IAS 2) |
|---|---|---|
| **LIFO** | **Permitted** | **Prohibited** `[high]` |
| **Subsequent measurement** | LCNRV for FIFO/avg-cost (post ASU 2015-11); **LCM retained for LIFO and retail method** `[high]` | **Lower of cost and NRV** for all methods `[high]` |
| **"Market" definition (LIFO/retail under LCM)** | replacement cost, bounded by an NRV ceiling and an NRV-less-normal-margin floor `[high]` | n/a — NRV directly `[high]` |
| **Reversal of write-downs** | **Prohibited** — write-down sets a new cost basis `[high]` | **Required** when NRV recovers, up to original cost `[high]` |
| **Fixed OH absorption / normal capacity** | normal-capacity rule; abnormal idle expensed | substantively the same normal-capacity rule `[med]` |

**ASU 2015-11 (effective for public entities fiscal years beginning after 15 Dec 2016):** replaced **LCM with LCNRV** — inventory measured by FIFO or average cost is carried at the **lower of cost and net realizable value** (NRV = estimated selling price − reasonable costs of completion, disposal, and transport). `[high]` The **LIFO and retail-inventory-method exception** keeps those two on the old LCM regime, because the Board judged the transition cost of moving them to LCNRV unjustified. `[high]`

---

## Source-quality assessment

The codified, load-bearing claims (ASC 330 normal-capacity and abnormal-cost period treatment; ASU 2015-11 LCM→LCNRV with the LIFO/retail carve-out; IFRS LIFO prohibition and write-down reversal) rest on the standard-setter text plus ≥2 independent professional sources (FASB ASU PDF, SEC EDGAR, KPMG, RSM, PwC excerpt) — high confidence. The managerial mechanics (absorption-vs-variable income bridge, COGM, CVP, the variance formula set and disposition) are stable textbook canon corroborated across OpenStax, LibreTexts, Saylor, AccountingCoach, CFI, and AccountingTools — high confidence on substance. Three authoritative domains (PwC Viewpoint, AccountingVerse, Saylor) 403'd on direct fetch, so a few fine distinctions — the capacity-level table nuances, the high-production per-unit reduction, and the favorable-variance disposition failure mode — rest on single excerpts and are tagged `[med]`. No claim here rests on practitioner-blog assertion alone.

### Sources

- [FASB ASU 2015-11, Inventory (Topic 330)](https://storage.fasb.org/ASU%202015-11.pdf)
- [PwC Viewpoint — 1.4 Full absorption costing (excerpt; 403 on fetch)](https://viewpoint.pwc.com/content/pwc-madison/ditaroot/us/en/pwc/accounting_guides/inventory/Inventory-Guide/Chapter-1-Inventory-costing/1_4_Full_absorption_costing.html)
- [SEC comment letter applying ASC 330 normal-capacity / idle facility](https://www.sec.gov/Archives/edgar/data/939930/000119312510096631/filename1.htm)
- [KPMG — Inventory accounting: IFRS vs US GAAP](https://kpmg.com/us/en/articles/2023/inventory-accounting.html)
- [RSM — US GAAP vs IFRS: Inventory](https://rsmus.com/pdf/us-gaap-vs-ifrs-inventory.pdf)
- [CPA Journal — "Net Realizable Value Is the New Market"](https://www.cpajournal.com/2018/06/26/net-realizable-value-is-the-new-market/)
- [Forvis — Inventory Standard Costing Fundamentals](https://www.forvis.com/alert-article/2022/02/inventory-standard-costing-fundamentals-other-current-trends)
- [Accounting For Management — variable vs absorption operating income](https://www.accountingformanagement.org/why-variable-and-absorption-costing-produce-different-operating-income/)
- [OpenStax — Variable vs Absorption Costing](https://openstax.org/books/principles-managerial-accounting/pages/6-5-compare-and-contrast-variable-and-absorption-costing)
- [AccountingTools — Job vs process costing](https://www.accountingtools.com/articles/what-is-the-difference-between-job-costing-and-process-costi.html)
- [Wall Street Prep — Activity-Based Costing](https://www.wallstreetprep.com/knowledge/activity-based-costing/)
- [AccountingCoach — Standard Costing explanation](https://www.accountingcoach.com/standard-costing/explanation)
- [AccountingCoach — PPV reclassification to actual cost](https://www.accountingcoach.com/blog/how-is-the-purchase-price-variance-reclassified)
- [AccountingTools — Predetermined overhead rate](https://www.accountingtools.com/articles/what-is-a-predetermined-overhead-rate.html)
- [AccountingTools — Fixed overhead volume variance](https://www.accountingtools.com/articles/what-is-the-fixed-overhead-volume-variance.html)
- [Accounting In Focus — Allocating overhead variances to WIP/FG/COGS](https://accountinginfocus.com/managerial-accounting-2/overhead-allocation/allocating-overhead-variances-to-work-in-progress-finished-goods-and-cost-of-goods-sold/)
- [CFI — CVP Analysis Guide](https://corporatefinanceinstitute.com/resources/accounting/cvp-analysis-guide/)
- [OpenStax — Margin of Safety and Operating Leverage](https://openstax.org/books/principles-managerial-accounting/pages/3-5-calculate-and-interpret-a-companys-margin-of-safety-and-operating-leverage)
- [CFI — Cost of Goods Manufactured (COGM)](https://corporatefinanceinstitute.com/resources/accounting/cost-of-goods-manufactured-cogm/)
- [ResearchGate — Costing Systems and the Spare Capacity Conundrum (death spiral)](https://www.researchgate.net/publication/256016412_Costing_Systems_and_the_Spare_Capacity_Conundrum_Avoiding_the_Death_Spiral)
- [Time-driven activity-based costing: theory, applications and limitations](https://www.researchgate.net/publication/305730517_Time-driven_activity-based_costing_Theory_applications_and_limitations)
