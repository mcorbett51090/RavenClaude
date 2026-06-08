---
description: "Select, design, and implement a forecast methodology — weighted probability, commit/category (3-bucket), or AI-assisted — calibrated to the business's data maturity, sales cycle, and team discipline. Includes the pipeline-coverage calculation, the sales-velocity formula, and the rollup protocol."
---

# Forecasting Methodology

**Purpose:** produce a forecast that is a commitment with a named, defensible methodology —
not a hope built on optimistic stage rollups.

## When to use this skill

- Selecting or designing the forecast methodology for the first time.
- Diagnosing why forecast accuracy is poor (and fixing the methodology).
- Designing the pipeline-coverage calculation and the sales-velocity metric.
- Designing the manager/VP/CRO forecast rollup protocol.

## Step 1: Assess data and process maturity

Before selecting a methodology, assess:

| Dimension | Ad-hoc | Process | Integrated |
| --- | --- | --- | --- |
| CRM stage data quality | Stale, inconsistent | Clean, validated | Stage-exit criteria enforced |
| Stage probabilities | Vendor defaults | Manager estimate | Empirically calibrated |
| Activity capture | Sporadic | Manual logging | Auto-captured (Gong/Outreach) |
| Rep discipline | Inconsistent | Trained, audited | Embedded in review cadence |
| Historical data | < 1 year | 1-2 years | 2+ years, segmented |

**Rule:** choose the methodology your data can support, not the one you wish you had.

## Step 2: Select the methodology

Traverse the forecast-method decision tree in
[`../../knowledge/revops-decision-trees.md`](../../knowledge/revops-decision-trees.md) before
selecting. Summary of methods:

### Method A: Weighted probability forecast

`Forecast = Σ (deal ACV × stage probability)` across all open deals.

- **Use when:** CRM data is reasonably clean; stage probabilities are empirically calibrated; sales
  cycle is relatively consistent.
- **Requires:** stage probabilities calibrated from historical win-rate data (not vendor defaults).
- **Breaks when:** probabilities are not calibrated; reps game stage advancement; long-tail of
  large deals dominates the weighted number.

### Method B: Commit / category (3-bucket)

Rep submits a commit number (high-confidence deals) + best-case number (upside if things go well).
Manager applies a judgment overlay. Rollup: Commit + Upside bracket = Forecast range.

- **Use when:** enterprise/complex sales with high deal variability; experienced rep team with
  forecast discipline; deal counts are manageable for manager inspection.
- **Requires:** rep accountability for commit accuracy; manager calibration; a structured deal-review
  cadence to validate commits.
- **Breaks when:** reps systematically sandbag commits (hiding upside); no accountability for commit
  accuracy (no trailing-3-quarter accuracy score).

### Method C: AI-assisted (Clari, Gong Forecast, Salesforce Einstein)

Uses ML models trained on CRM data, email/call activity, and historical patterns to score deals
and generate a forecast.

- **Use when:** CRM data quality is high; activity capture is automated (Gong/Outreach/Salesloft);
  at least 2 years of historical closed-deal data; team size justifies the tool cost [verify-at-use].
- **Requires:** clean CRM data (AI multiplies data quality — good or bad), activity capture at
  scale, and a human override protocol for deals the model doesn't understand.
- **Breaks when:** adopted before CRM hygiene is established; model is trusted without human
  judgment; team uses it to avoid the deal-inspection work.

## Step 3: Design the pipeline coverage calculation

```
Coverage ratio = Open pipeline ACV ÷ Remaining quota gap
```

Benchmark: 3× coverage is a common heuristic, but the right number depends on win-rate.

```
Required coverage = 1 ÷ blended win-rate at current stage mix
```

Example: if blended win-rate is 25%, you need 4× coverage, not 3×. Always state win-rate
alongside the coverage ratio; a ratio without a win-rate denominator is misleading.

Segment coverage by: AE, segment (SMB/MM/Enterprise), product line, and territory.

## Step 4: Design the sales-velocity metric

```
Sales velocity = (# open opportunities × win-rate × average ACV) ÷ average sales cycle length (days)
```

Sales velocity measures how fast revenue is flowing through the pipeline. A declining velocity is
an early warning sign before the forecast number is impacted. Track it weekly by segment.

## Step 5: Design the rollup protocol

| Level | What they add | Not just |
| --- | --- | --- |
| AE | Commit number + best-case number; deal-level notes | Passing through the CRM rollup |
| Manager | Judgment overlay on each rep's commit; flag at-risk deals | Just averaging the reps |
| VP | Segment-level overlay; sanity-check against historical attainment by rep | Summing the managers |
| CRO | Final company commit; range (Commit → Best Case); upside narrative | The stage-weighted total |

## Step 6: Design the forecast cadence

- **Weekly:** manager inspects late-stage pipeline against exit criteria; reps update commit.
- **Monthly:** VP review; coverage analysis by segment; velocity trend.
- **Quarterly:** CRO commit to CFO/board; methodology retrospective (accuracy vs. submitted).

## Anti-patterns

- A forecast number with no named methodology — "we used the pipeline" is not an answer.
- Stage probabilities that are the CRM vendor's defaults and have never been calibrated.
- A coverage ratio cited without a win-rate denominator.
- An AI forecasting tool adopted before CRM data quality prerequisites are in place.
- A commit that is never compared against actual close (no accountability loop).

## Output

A forecast methodology design document naming the selected method, the data prerequisites, the
pipeline-coverage calculation with win-rate context, the sales-velocity formula, and the rollup
protocol. Pass to `crm-operations-architect` for CRM stage-probability updates; pass to
`revops-lead` for governance integration.
