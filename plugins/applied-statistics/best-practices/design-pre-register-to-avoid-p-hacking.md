# Pre-register the analysis plan — the structural defense against p-hacking and peeking

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Experiment design / research integrity
**Applies to:** `applied-statistics`

---

## Why this exists

Most "false discoveries" aren't fraud — they're **researcher degrees of freedom** exercised after seeing the data: trying a few subgroups, a few cutoffs, a few covariate sets, and reporting the combination that crossed α=0.05. Each choice is individually defensible; collectively they are p-hacking (pitfall #1), and they invalidate the p-value because the test no longer reflects a single pre-specified hypothesis. **Peeking** (pitfall #3) is the temporal version: watching a running experiment and stopping when it looks significant inflates the false-positive rate far above α. Writing the plan down *before* seeing data — metric, test, segments, stopping rule, correction — removes the degrees of freedom by construction. It is the cheapest defense against fooling yourself (house opinion #5), and it is *structural*, not a matter of willpower.

## How to apply

Fill the pre-registration before any data is seen; treat everything not in it as **exploratory** and label it so in the report.

```
Pre-registration (write BEFORE launch — see ../templates/analysis-plan.md):
  Primary metric:     <the one metric the decision hinges on>
  Hypothesis:         <directional — "B increases <metric> vs control">
  Test:               <from the decision tree: data type → #groups → paired?>
  Sample size / n:    <from the power analysis — α, power, MDE>
  Stopping rule:      <fixed-horizon: do not look until n reached
                       OR a named sequential method (mSPRT / always-valid)>
  Segments / guardrails: <named up front>
  Multiplicity:       <FWER for confirmatory, FDR for exploratory>
```

**Do:**
- Write metric, test, n, stopping rule, segments, and correction down before launch; store it with the experiment-design doc.
- Label any analysis not in the plan **exploratory** — surface it as a candidate, never as a confirmed effect.
- Report **all** tests run, not just the significant ones.

**Don't:**
- Choose the subgroup / cutoff / covariate set after seeing which one is significant.
- Peek at a fixed-horizon test and stop when it crosses α — either fix n up front or use a sequential method built for peeking.
- Quietly promote an exploratory hit to a headline finding without a pre-registered confirmatory follow-up.

## Edge cases / when the rule does NOT apply

- **Genuinely exploratory / hypothesis-generating work** is legitimate and need not be pre-registered — but it must be *labeled* exploratory, corrected with FDR, and never dressed up as confirmatory.
- **Observational / retrospective analyses** can't pre-register data collection, but you can still pre-specify the analysis (estimand, model, covariates) before touching the data, and pre-register a blind-to-outcome analysis plan.
- **Adaptive designs** (sequential, multi-armed bandits) deliberately change course mid-study — that is not peeking *if* the adaptation rule was specified in advance.

## See also

- [`../templates/analysis-plan.md`](../templates/analysis-plan.md) — the fill-the-boxes pre-registration template.
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — pitfall #1 (p-hacking) and #3 (peeking / optional stopping).
- [`../knowledge/experiment-design-and-ab-testing.md`](../knowledge/experiment-design-and-ab-testing.md) — the settled spine and the fixed-horizon-vs-sequential frontier.
- [`./design-power-and-sample-size-before-collecting.md`](./design-power-and-sample-size-before-collecting.md) — the n the stopping rule depends on.

## Provenance

Codifies house opinion #5 ("pre-register the analysis plan") in [`../CLAUDE.md`](../CLAUDE.md) §3 and pitfalls #1 / #3 in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) (last reviewed 2026-05-26; Tier 1 spine / Tier 3 sequential frontier — verify vendor sequential methods before quoting). The advisory hook does not catch p-hacking mechanically; this is the human-discipline backstop.

---

_Last reviewed: 2026-05-30 by `claude`_
