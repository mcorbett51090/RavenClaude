# Six Sigma statistics & SPC reference

> The measurement/statistics reference **specific to process improvement** — the seam doc. Sigma-level ↔ DPMO ↔ yield (with the 1.5σ shift), Cp/Cpk/Pp/Ppk with thresholds, control-chart selection + Western Electric / Nelson out-of-control rules, and MSA / Gage R&R basics. It is deliberately scoped to **what a process-improvement project needs**; the **deeper inference** (hypothesis testing, DOE, regression, sample-size/power, formal capability inference) **routes to [`applied-statistics`](../../applied-statistics/CLAUDE.md)** — see §6. Implements house opinions #1 (baseline before change), #4 (don't reinvent the statistics), #8 (every quantitative claim carries its grounding) from [`../CLAUDE.md`](../CLAUDE.md).

**Last verified:** 2026-06-03. The DPMO/sigma table, the 1.5σ-shift convention, the capability formulas + thresholds, and the control-chart selection + WE/Nelson rules are stable, long-established reference facts; each is cited inline with its retrieval date. Process-specific numbers (a given baseline, a given Cpk) always carry their own spec limits + sample window per CLAUDE.md #8.

---

## 1. Sigma level ↔ DPMO ↔ yield (with the 1.5σ shift)

**DPMO** = Defects Per Million Opportunities = (defects ÷ (units × opportunities-per-unit)) × 1,000,000. The **sigma level** is a normalized quality score; higher is better. The standard table assumes the **1.5σ long-term shift** convention (below) — verified 2026-06-03 (MoreSteam Six Sigma Conversion Table; iSixSigma).

| Sigma level (long-term, 1.5σ-shifted) | DPMO | Yield |
|---|---|---|
| 1σ | ~691,462 (~690,000) | ~30.9% |
| 2σ | ~308,538 (~308,000) | ~69.1% |
| 3σ | ~66,807 (~66,800) | ~93.32% |
| 4σ | ~6,210 | ~99.38% |
| 5σ | ~233 | ~99.977% |
| **6σ** | **3.4** | **99.99966%** |

**The 1.5σ shift convention.** A *static* normal process with 6σ between the mean and the nearest spec limit would give ~0.002 DPMO (2 parts per billion). But processes drift over time, so the Six Sigma convention assumes the mean can wander by **±1.5σ** long-term. Under that shift, the *effective* short-term distance to the spec limit at "6σ quality" is 4.5σ, which yields the famous **3.4 DPMO** — verified 2026-06-03 (MoreSteam; LegalClarity). State whether a quoted sigma level is **short-term** (process potential, no shift) or **long-term** (shifted) every time (CLAUDE.md anti-pattern).

**Conversion (long-term/shifted):** `Sigma = NORMSINV(1 − DPMO/1,000,000) + 1.5` — verified 2026-06-03 (CalcBee; iSixSigma). (Drop the `+ 1.5` for the short-term sigma.)

---

## 2. Process capability & performance — Cp, Cpk, Pp, Ppk

These indices compare the **voice of the process** (its spread) to the **voice of the customer** (the spec limits USL/LSL). Verified 2026-06-03 (Six Sigma Study Guide; SuperEngineer; ASQ Exam Prep).

| Index | Formula | Uses which σ | Answers |
|---|---|---|---|
| **Cp** | (USL − LSL) / (6σ_within) | **short-term** (within-subgroup) | "How capable *could* this process be if centered?" (potential; ignores centering) |
| **Cpk** | min( (USL − μ)/(3σ_within), (μ − LSL)/(3σ_within) ) | **short-term** (within-subgroup) | "How capable *is* it, accounting for centering?" (potential, centered) |
| **Pp** | (USL − LSL) / (6σ_overall) | **long-term** (overall) | "How capable *could* it be, historically?" |
| **Ppk** | min( (USL − μ)/(3σ_overall), (μ − LSL)/(3σ_overall) ) | **long-term** (overall) | "How capable *was* it, historically + centering?" |

**The one distinction that matters:** **Cp/Cpk use the *within-subgroup* (short-term) standard deviation** (process *potential* under stable conditions); **Pp/Ppk use the *overall* (long-term) standard deviation** including between-subgroup drift — verified 2026-06-03. A large gap between Cpk and Ppk signals the process is unstable / drifting (the short-term capability isn't being held long-term).

**Rule-of-thumb thresholds** (verified 2026-06-03; SuperEngineer; iFactory):

| Cpk / Ppk | Interpretation |
|---|---|
| < 1.00 | Not capable — the spread exceeds the spec; expect significant defects. |
| 1.00 – 1.33 | Marginal — capable only if centered and stable; little margin. |
| **≥ 1.33** | **Capable** — the common general-manufacturing / automotive (AIAG) baseline for ongoing production (~63 PPM). |
| **≥ 1.67** | Highly capable — typical for critical / safety characteristics (~0.6 PPM). |
| ≥ 2.00 | "Six Sigma" capability; sometimes required for flight-/safety-critical dimensions. |

> **House rule (CLAUDE.md anti-pattern):** **capability is meaningless on an out-of-control process.** Confirm statistical *control* (§3) *first*; only a stable process has a meaningful Cpk/Ppk. And never report a capability index without its **spec limits + sample window + the stability check**.

---

## 3. Control-chart selection (which chart for which data)

The first fork is **variable (continuous, measured) vs attribute (discrete, counted)** data; the second is **subgroup size** (variables) or **defects vs defectives** (attributes) — verified 2026-06-03 (SPC for Excel; Six Sigma Study Guide; Minitab).

| Data type | Condition | Chart |
|---|---|---|
| **Variable** (continuous) | Individual values, subgroup = 1 | **I-MR** (Individuals & Moving Range) |
| **Variable** (continuous) | Subgroup size **2–~9** | **Xbar-R** (mean & range) |
| **Variable** (continuous) | Subgroup size **~9+** (≥10) | **Xbar-S** (mean & std dev — at larger n, S estimates spread better than R) |
| **Attribute — defectives** (a unit pass/fails) | **Constant** subgroup size | **np** (count of defectives) |
| **Attribute — defectives** | **Variable** subgroup size | **p** (proportion defective) |
| **Attribute — defects** (a unit can have several) | **Constant** opportunity/area | **c** (count of defects) |
| **Attribute — defects** | **Variable** opportunity/area | **u** (defects per unit) |

**Mnemonic:** *defectives* → p/np (a unit is good or bad); *defects* → c/u (count flaws, several possible per unit). *Constant* size → np / c; *variable* size → p / u. (Full Mermaid tree: [`process-improvement-decision-trees.md`](process-improvement-decision-trees.md) §2.)

### 3a. Control-chart constants — the table you need to actually draw the chart

The selection table above names Xbar-R and Xbar-S as the majority case, but neither chart can be built without the subgroup-size constants. They are here so the recommendation is executable rather than aspirational.

**Convention — read this before using a value.** These are the standard published constants (ASTM E2587 / AIAG SPC manual / the classic ASQ tables); Minitab, JMP and SPC for Excel all use the same set. They assume an approximately **normal** process and a **constant** subgroup size `n`. Every table in circulation tabulates them to **3 decimal places**, and the derived factors (A2, A3, D3, D4, B3, B4) are conventionally computed from the *already-rounded* d2/d3/c4 — so a direct recomputation from unrounded values can differ in the third decimal (D4 at n=3 is the known case: the tabulated 2.574 vs 2.5745 computed from unrounded d3). **Quote the tabulated value**, so your limits reconcile with whatever software the customer audits you with.

**Verified 2026-08-17** by direct numerical computation, not recall: d2 and d3 were recomputed as the mean and standard deviation of the range of `n` standard normal variates (numerical integration of the range distribution), and c4 exactly as `c4(n) = sqrt(2/(n-1)) · Γ(n/2) / Γ((n-1)/2)`. All 9 rows of the Xbar-S block and 8 of the 9 Xbar-R rows reproduced the published table to 3 decimals; the ninth is the D4-at-n=3 rounding convention noted above.

**Xbar-R** (subgroups of 2–~9) — `R-bar` is the mean subgroup range:

| n   | d2    | A2    | D3    | D4    |
| --- | ----- | ----- | ----- | ----- |
| 2   | 1.128 | 1.880 | 0     | 3.267 |
| 3   | 1.693 | 1.023 | 0     | 2.574 |
| 4   | 2.059 | 0.729 | 0     | 2.282 |
| 5   | 2.326 | 0.577 | 0     | 2.114 |
| 6   | 2.534 | 0.483 | 0     | 2.004 |
| 7   | 2.704 | 0.419 | 0.076 | 1.924 |
| 8   | 2.847 | 0.373 | 0.136 | 1.864 |
| 9   | 2.970 | 0.337 | 0.184 | 1.816 |
| 10  | 3.078 | 0.308 | 0.223 | 1.777 |

- Xbar chart: `CL = X-double-bar`, `UCL/LCL = X-double-bar ± A2 · R-bar`
- R chart: `CL = R-bar`, `UCL = D4 · R-bar`, `LCL = D3 · R-bar`
- Process sigma estimate: `sigma-hat = R-bar / d2` — this is the **within-subgroup (short-term)** sigma that feeds **Cp/Cpk** in §2. (D3 is 0 below n = 7 because the lower 3-sigma bound on the range goes negative and a range cannot be negative — the LCL is not "missing", it is structurally zero.)

**Xbar-S** (subgroups of ~9+) — `S-bar` is the mean subgroup standard deviation:

| n   | c4     | A3    | B3    | B4    |
| --- | ------ | ----- | ----- | ----- |
| 2   | 0.7979 | 2.659 | 0     | 3.267 |
| 3   | 0.8862 | 1.954 | 0     | 2.568 |
| 4   | 0.9213 | 1.628 | 0     | 2.266 |
| 5   | 0.9400 | 1.427 | 0     | 2.089 |
| 6   | 0.9515 | 1.287 | 0.030 | 1.970 |
| 7   | 0.9594 | 1.182 | 0.118 | 1.882 |
| 8   | 0.9650 | 1.099 | 0.185 | 1.815 |
| 9   | 0.9693 | 1.032 | 0.239 | 1.761 |
| 10  | 0.9727 | 0.975 | 0.284 | 1.716 |

- Xbar chart: `UCL/LCL = X-double-bar ± A3 · S-bar`
- S chart: `CL = S-bar`, `UCL = B4 · S-bar`, `LCL = B3 · S-bar`
- Process sigma estimate: `sigma-hat = S-bar / c4`

**I-MR** (subgroup = 1) uses the n = 2 row applied to the *moving* range of successive pairs: `I-chart UCL/LCL = X-bar ± (3/d2) · MR-bar = X-bar ± 2.66 · MR-bar` (3 / 1.128 = 2.66), and `MR-chart UCL = D4 · MR-bar = 3.267 · MR-bar`, `LCL = 0`. These are the two constants [`../scripts/lss_calc.py`](../scripts/lss_calc.py) `imr` hard-codes, and Gate 218 asserts them against hand-checked limits.

⛔ These are **control** limits (voice of the process), computed from the data. They are never the spec limits — see [`../best-practices/control-chart-limits-are-not-spec-limits.md`](../best-practices/control-chart-limits-are-not-spec-limits.md).

---

## 4. Out-of-control rules — Western Electric & Nelson

A point inside the ±3σ control limits with a *random* pattern = **common-cause** variation (leave it alone). A signal from these rules = a **special cause** (investigate). Control limits are computed from the data (±3σ); they are **not** the spec limits.

### Western Electric (WECO) rules — the original four (1956)

Verified 2026-06-03 (Wikipedia: Western Electric rules; QualityGurus). Zones A/B/C = the 1σ/2σ/3σ bands either side of the centerline.

1. **1 point** beyond 3σ (outside a control limit).
2. **2 of 3** consecutive points beyond 2σ on the same side.
3. **4 of 5** consecutive points beyond 1σ on the same side.
4. **8 points in a row** on the same side of the centerline.

### Nelson rules — the eight (Lloyd S. Nelson, 1984)

Nelson extended WECO to balance the false-alarm probability across tests — verified 2026-06-03 (QualityGurus; MetricGate; Grokipedia). The canonical set:

1. **1 point** > 3σ from centerline. *(gross error / extreme variation)*
2. **9 points** in a row on the same side of the centerline. *(sustained shift)*
3. **6 points** in a row steadily increasing or decreasing. *(trend — e.g. tool wear, drift)*
4. **14 points** in a row alternating up and down. *(over-adjustment / systematic oscillation)*
5. **2 of 3** points in a row > 2σ on the same side. *(approaching a limit)*
6. **4 of 5** points in a row > 1σ on the same side. *(shift)*
7. **15 points** in a row within 1σ (either side). *(stratification — variation suspiciously small; often a sampling/measurement artifact)*
8. **8 points** in a row beyond 1σ on **both** sides, none within. *(mixture — two distinct populations)*

> **Practical note:** more rules = more sensitivity *and* more false alarms. Many shops run a reduced set (e.g. Nelson 1–4 or the WE four) to keep the false-alarm rate manageable. The "is this signal real or a false alarm?" judgment for a borderline pattern is exactly the kind of question to route to `applied-statistics` (§6).

---

## 5. Measurement System Analysis (MSA) / Gage R&R — basics

Before trusting *any* baseline, confirm the *measurement system* isn't the source of the variation you're seeing. **Gage R&R** decomposes measurement variation into:

- **Repeatability** — variation when the *same* appraiser measures the *same* item repeatedly (the gauge/instrument itself).
- **Reproducibility** — variation *between* appraisers measuring the same item (the people/method).

Rule of thumb (commonly cited): **%R&R < 10%** of total variation = acceptable; **10–30%** = marginal (may be acceptable depending on cost/criticality); **> 30%** = unacceptable — the measurement system masks the process `[unverified — training knowledge]` for the exact bands; the *concept* (repeatability + reproducibility, confirm the gauge before the process) is standard MSA. For attribute data, use an **attribute agreement analysis** (do appraisers agree with each other and with a known standard?). The **statistical computation + acceptance inference** for a Gage R&R study routes to `applied-statistics` (§6).

---

## 6. What routes to `applied-statistics` (the explicit seam)

This plugin owns **process framing + method choice + the reference facts above**. The **inferential math** is `applied-statistics`' lane (CLAUDE.md #4). Route the following across the seam to [`applied-statistics/applied-statistician`](../../applied-statistics/agents/applied-statistician.md):

| Question | Route to (applied-statistics) |
|---|---|
| "Is the Analyze-phase candidate cause statistically associated with the defect?" | `choose-statistical-test` (t-test / ANOVA / chi-square / nonparametric — by data type) |
| "Did the Improve-phase pilot actually move the metric (vs noise)?" | `experiment-analysis` (effect size + CI, multiplicity, peeking screen) |
| "How many samples / how long must the pilot run?" | `power-and-sample-size` |
| "Design an experiment to find the optimal factor settings (DOE)." | `applied-statistician` (DOE design + analysis) |
| "What process inputs drive the output? / forecast the metric." | `regression-and-forecasting-review` |
| "Is this SPC / baseline movement signal or noise?" | `statistical-qa-of-metrics` (the data-platform/applied-statistics seam) |
| "Compute + interpret the Gage R&R / formal capability confidence interval." | `applied-statistician` (capability inference) |

**The boundary in one line:** *this plugin* says **which** metric, **which** chart, **which** tool, and **what a Cpk of 1.1 means for this process**; *applied-statistics* certifies **"is the difference real?"** with the effect size + CI.

---

## Sources

- Sigma ↔ DPMO ↔ yield + 1.5σ shift — [MoreSteam: Six Sigma Conversion Table](https://www.moresteam.com/toolbox/six-sigma-conversion-table); [iSixSigma: Yield to Sigma Conversion Table](https://www.isixsigma.com/sigma-level/yield-to-sigma-conversion-table/); [CalcBee DPMO Calculator](https://calcbee.com/calculators/manufacturing/six-sigma/dpmo-calculator/); [LegalClarity: DPMO Formula & Sigma Levels](https://legalclarity.org/defects-per-million-opportunities-formula-and-sigma-levels/) — retrieved 2026-06-03.
- Cp/Cpk/Pp/Ppk formulas, short-vs-long-term σ, thresholds — [Six Sigma Study Guide: Process Capability Pp/Ppk/Cp/Cpk](https://sixsigmastudyguide.com/process-capability-pp-ppk-cp-cpk/); [SuperEngineer: Cp Cpk](https://www.superengineer.net/blog/spc-cp-cpk) and [Pp Ppk](https://www.superengineer.net/blog/spc-pp-ppk); [iFactory: Process Capability](https://ifactoryapp.com/blog/process-capability-cp-cpk); [ASQ Exam Prep](https://asqexamprep.com/blog/how-to-calculate-process-capability-cp-cpk-pp-ppk) — retrieved 2026-06-03.
- Control-chart selection — [SPC for Excel: Selecting the Right Control Chart](https://www.spcforexcel.com/knowledge/control-chart-basics/selecting-right-control-chart/); [Six Sigma Study Guide: I-MR Chart](https://sixsigmastudyguide.com/i-mr-chart/); [Minitab: Xbar-R overview](https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/control-charts/how-to/variables-charts-for-subgroups/xbar-r-chart/before-you-start/overview/) — retrieved 2026-06-03.
- Control-chart constants (§3a: d2/A2/D3/D4 and c4/A3/B3/B4, n = 2–10) — the standard ASTM E2587 / AIAG SPC / ASQ table, as used by Minitab, JMP and [SPC for Excel: Control Chart Constants](https://www.spcforexcel.com/knowledge/control-chart-basics/control-chart-constants/). **Independently recomputed 2026-08-17** rather than recalled: d2/d3 by numerical integration of the range distribution of `n` standard normals, c4 exactly from `sqrt(2/(n-1))·Γ(n/2)/Γ((n-1)/2)`. 17 of the 18 rows reproduced the published values to 3 decimals; the sole difference (D4 at n = 3) is the published-table rounding convention documented inline in §3a.
- Western Electric & Nelson rules — [Wikipedia: Western Electric rules](https://en.wikipedia.org/wiki/Western_Electric_rules); [QualityGurus: Nelson and Western Electric Rules](https://www.qualitygurus.com/nelson-rules-and-western-electric-rules-for-control-charts/); [MetricGate: Control Chart Rules](https://metricgate.com/docs/control-chart-rules/) — retrieved 2026-06-03.
