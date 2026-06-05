# RCM KPI glossary

The metrics a revenue cycle is judged on — formulas, the misreads, and the cited, dated benchmark each is read against. Every external benchmark carries a source URL + retrieval date or an `[unverified]` mark (§3 #8). Benchmarks are payer- and specialty-dependent and **dated** — validate against the client's own data before any deliverable.

## Efficiency metrics

| Metric | Formula | Benchmark (dated) | The misread |
|---|---|---|---|
| Clean-claim / first-pass rate | claims paid without rework ÷ claims submitted | **95%+ good, 98%+ excellent** (2025) [verify-at-use] | Treating "it pays eventually" as fine — every point below target is rework (cost + delayed cash), §3 #2 |
| Denial rate (initial) | denied claims ÷ claims submitted | target **<5%**, world-class <3%; **2025 average ~6–11%** by specialty/payer; AHA reported initial denials **11.8% in 2024** [verify-at-use] | An uncategorized aggregate is unactionable — break it out by CARC + owner, §3 #5 |
| Cost to collect | total RCM operating cost ÷ payments collected | efficient operations **<3%** [verify-at-use] | Each unnecessary touch costs roughly **$2.50–$8** [verify-at-use] — rework is the hidden driver |

First-pass resolution is the **master efficiency number** (§3 #2): every point of rework is cost and delayed cash.

## Cash metrics

| Metric | Formula | Benchmark (dated) | The misread |
|---|---|---|---|
| Net collection rate (NCR) | payments ÷ allowed amount (charges − contractual adjustments) | **96–98%** best practice; large groups 98–100%, smaller ~94% [verify-at-use] | Reading against **gross charges** (gross collection rate) — a vanity number against fee schedules nobody pays, §3 #4 |
| Days in A/R | total outstanding A/R ÷ average daily charges | high performers **<30**; **31–40 acceptable** (MGMA/AAFP, HFMA) [verify-at-use] | A single blended average hides where cash is stuck — read by aging bucket + payer, §3 #3 |
| A/R over 90 days | A/R aged >90 days ÷ total A/R | **<10%** [verify-at-use] | Hidden concentration (a credentialing block, one slow payer) lives here |

Net, not gross, measures the cycle (§3 #4). Read A/R **by bucket and payer**, never as a single average (§3 #3). The [`../scripts/rcm_calc.py`](../scripts/rcm_calc.py) calculator computes `ar-days` (+ over-90 flag) and `net-collection` (with the gross gap exposed).

## Denial & recovery metrics

| Metric | What it measures | Benchmark / context (dated) |
|---|---|---|
| Denial rate by category | denials by CARC root cause + payer as % of claims | top categories are usually front-end (eligibility, prior auth) — build the Pareto, §3 #5 |
| Appeal / denial overturn rate | appealed denials overturned ÷ appealed | commercial **~40–60%**; well-managed technical/admin higher; Medicare Advantage appeals overturned **>80%** [verify-at-use] |
| Denials never reworked | denied claims never resubmitted ÷ denied | **50–65% never reworked** (MGMA); ~**two-thirds recoverable** [verify-at-use] |
| Recovery rate decay | recovery by age of denial | **~70–80% worked within 60 days** vs **~40–60% after 90 days** [verify-at-use] — speed compounds value |
| Write-off rate | write-offs ÷ charges, split contractual vs bad debt | separate **contractual adjustment** (correct, e.g. CARC CO-45 at contracted rate) from **bad debt** (recoverable balance lost), §3 #4 |

The [`../scripts/rcm_calc.py`](../scripts/rcm_calc.py) `denial-recovery` mode quantifies recoverable cash in an unworked queue; `clean-claim` quantifies the rework cost of points below target.

## CARC / RARC quick reference (the codes the trees route on)

**CARC** = Claim Adjustment Reason Code; **RARC** = Remittance Advice Remark Code. The authoritative lists are maintained by X12 ([CARC](https://x12.org/codes/claim-adjustment-reason-codes) / [RARC](https://x12.org/codes/remittance-advice-remark-codes)). Group codes: **CO** = contractual obligation (provider write-down), **PR** = patient responsibility, **OA** = other adjustment, **PI** = payer-initiated.

| Code | Meaning | Disposition (see the decision trees) |
|---|---|---|
| CO-16 | Claim/service lacks information or has a submission/billing error | Corrected claim (fix info) + tune scrubber |
| CO-11 | Diagnosis inconsistent with the procedure | Corrected claim; recurring → coding CAPA |
| CO-22 | Coordination of benefits — covered by another payer | Front-end eligibility / COB order |
| CO-27 | Expenses after coverage terminated | Front-end eligibility verification |
| CO-29 | Time limit for filing has expired | **Permanent loss** — fix submission pipeline / charge-capture lag |
| CO-45 | Charge exceeds fee schedule / contracted amount | Contractual write-off **only if** paid = contracted; if paid < contracted → underpayment escalation |
| CO-50 | Not deemed a medical necessity by the payer (often LCD-driven, RARC N115) | Appeal with clinical documentation if defensible |
| CO-197 | Precertification/authorization absent — service required prior auth | Front-end auth checklist; retro-auth appeal if window open |
| PR-1 / PR-2 / PR-3 | Deductible / coinsurance / copay | Patient balance — move financial conversation to the front end, not the appeal queue |

> The "denial rates climbing from 30% (2022) to 41% (2025)" figure circulating in some vendor blogs is **[unverified]** and conflicts with AHA's initial-denial-rate data (11.8% in 2024); it likely conflates a different denominator. Do not put it in a deliverable without a primary source.

## Sources (retrieved 2026-06-05)

- RCM benchmarks (NCR, days-in-A/R, clean-claim, A/R>90) — https://www.mdclarity.com/blog/rcm-benchmarks
- 7 KPIs providers should track (HFMA) — https://www.hfma.org/revenue-cycle/kpis/7-kpis-providers-should-be-tracking/
- Healthy A/R and denial rates in 2025 — https://www.medicalbillersandcoders.com/blog/what-healthy-ar-and-denial-rates-look-like-in-2025/
- Net collection ratio benchmarks (multi-specialty) — https://www.medicalbillersandcoders.com/blog/net-collection-ratio-benchmarks-multi-specialty-groups/
- Cost of denials / never-reworked / recoverable — https://www.os-healthcare.com/news-and-blog/measuring-the-cost-of-denials-and-impact-of-prevention
- Denial recovery rate — https://www.mdclarity.com/rcm-metrics/denial-recovery-rate
- Appeal overturn rates — https://revecore.com/denial-overturn-rate/ and https://www.healthcaredive.com/news/insurance-denials-overturned-appeal-new-york-study-JAMA/817490/
- CARC/RARC codes — https://www.sprypt.com/denial-codes/carc-and-rarc-codes and https://x12.org/codes/claim-adjustment-reason-codes

## Sourcing note

Benchmark figures here are public-source-cited with retrieval dates; specialty/payer-specific figures carry `[verify-at-use]`. Any figure that lacks a citation is marked `[unverified — training knowledge]` at point of use. Validate against a primary source and the client's own data before putting any figure in a deliverable (§3 cite-or-mark rule).
