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
- Western Electric & Nelson rules — [Wikipedia: Western Electric rules](https://en.wikipedia.org/wiki/Western_Electric_rules); [QualityGurus: Nelson and Western Electric Rules](https://www.qualitygurus.com/nelson-rules-and-western-electric-rules-for-control-charts/); [MetricGate: Control Chart Rules](https://metricgate.com/docs/control-chart-rules/) — retrieved 2026-06-03.
