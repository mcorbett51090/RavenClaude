# Prove root cause with data before improving — don't spend on a fix until the cause is confirmed

**Status:** Absolute rule — a countermeasure attached to an unproven cause is a guess with a budget. Root cause is proven with data, not with group consensus.

**Domain:** DMAIC / root-cause analysis

**Applies to:** `process-improvement`

---

## Why this exists

Teams jump to solutions. This is natural — solutions feel productive, and spending time on analysis when the problem is hurting real people feels like delay. The pattern plays out predictably:

1. The team agrees on "the obvious cause" (usually the one the highest-ranking person in the room names).
2. Resources are spent on a fix for that cause.
3. The problem persists, or a different problem appears, because the real cause was never touched.
4. The next round of analysis starts from a more complicated, more-expensive-to-fix baseline.

The cost of skipping cause validation is not the analysis time saved — it is the cost of the wrong fix plus the delayed correct fix. In operational processes, this cycle repeats annually until someone insists on data.

Root cause is **proven** when:
- A plausible causal mechanism connects the cause to the observed effect.
- Data shows the effect metric changes systematically when the cause is present vs. absent (or at high vs. low levels).
- The change is large enough to explain the observed magnitude of the problem.

Root cause is **not proven** by: team consensus, management assertion, similarity to a previous problem, or a strong hunch from someone with domain experience.

## How to apply

After the fishbone and 5 Whys produce a set of candidate root causes:

1. **State the hypothesis explicitly** — "We believe that [cause] is responsible for [effect]. Specifically, we expect that when [cause] is present/high, [effect metric] will be [higher/lower/more variable] than when [cause] is absent/low."

2. **Select a validation method** matched to the cause type:

   | Cause type | Validation method | Who executes |
   |---|---|---|
   | Categorical cause (yes/no, team A vs. B) | Stratified comparison — compare defect rate between the two groups | `process-analyst` or `lean-six-sigma-blackbelt` |
   | Continuous cause (wait time, batch size) | Scatter plot + correlation; if sample is small, route to `applied-statistics` | Visualization here; inference in `applied-statistics` |
   | Multiple causes interacting | Design of Experiments (DOE) | **Route to `applied-statistics`** — DOE is not in scope for this plugin |
   | Any statistical test of significance | t-test, ANOVA, chi-square, regression | **Route to `applied-statistics`** — name the question, they run and defend it |

3. **Collect the validation data** — the same operational definitions used in the baseline. Do not collect new data with a different definition.

4. **Apply the statistics seam** — this plugin frames which question to ask and which candidate test to name; `applied-statistics`'s `applied-statistician` runs the test, checks assumptions, and returns a verdict with effect size and confidence interval. Do not run hypothesis tests inline in the process-improvement workflow — they will be wrong.

5. **Evaluate the result against the gate:**
   - **Confirmed** — the data shows the cause explains the effect at a meaningful magnitude; proceed to Improve.
   - **Not confirmed** — the data does not show a significant relationship; return to the fishbone and identify the next candidate.
   - **Inconclusive** — the sample was too small or the data too noisy; collect more data or route the sample-size question to `applied-statistics`.

6. **Document the validated cause in the Analyze tollgate** — state the cause, the validation method, the data, and the result. This documentation is the basis for the Improve-phase solution design.

```
Validated root cause — example:
  Cause: "Claims arrive without supporting documentation in ~40% of cases"
  Hypothesis: Claims missing documentation have a rework rate > 80%,
              vs. < 5% rework for claims with complete documentation.
  Validation: Stratified comparison of 320 claims (Oct–Dec 2025)
    - Missing docs (n=129): 84% rework rate
    - Complete docs (n=191): 3% rework rate
  Chi-square test → route to applied-statistics → p < 0.001; effect confirmed.
  Conclusion: Proceed to Improve. Countermeasure addresses documentation completeness.
```

**Do:**
- Name the test before collecting data (to avoid data dredging)
- Validate the top two or three fishbone candidates, not just one
- Accept a "not confirmed" result — it means the team avoided spending on the wrong fix

**Don't:**
- Proceed to Improve after a failed or inconclusive validation; collect more data or identify the next candidate
- Treat a scatter plot that "looks correlated" as validation without the statistical test
- Run the hypothesis test inline in the DMAIC workflow — route it to `applied-statistics`
- Count "the team all agreed" as validation

## Edge cases

- **The evidence is overwhelming and the fix is free** — if a poka-yoke (e.g., add a required field to a form) addresses a documented 84% rework rate and costs zero, the risk of acting before formal validation is low. Document the reasoning. The rule applies with full force when the fix is expensive, irreversible, or complex.
- **The cause is also the solution** — sometimes the validation experiment IS the pilot (you controlled the cause and observed the effect). This is valid — state clearly that the pilot data is both validation and Improve-phase result.
- **The data doesn't support any candidate** — this means the fishbone was incomplete. Go back to the process walk with the frontline workers; the real cause is likely in a category that was under-explored.

## See also

- Skill: [`../skills/root-cause-analysis/SKILL.md`](../skills/root-cause-analysis/SKILL.md) — the step-by-step for fishbone, 5 Whys, Pareto, and validation
- Template: [`../templates/fishbone-and-5-whys.md`](../templates/fishbone-and-5-whys.md) — includes the validation section and Analyze gate
- Best-practice: [`./measure-the-baseline-before-you-change-anything.md`](./measure-the-baseline-before-you-change-anything.md) — the prerequisite; you cannot validate a cause without a measured baseline
- `applied-statistics/agents/applied-statistician.md` — the seam for all inferential validation
- `applied-statistics/skills/statistical-qa-of-metrics/SKILL.md` — ensures the metric used in the validation study is reliable

## Provenance

Distilled from `CLAUDE.md` §3 house opinion #4 ("No solution-jumping before root cause is proven") and §4 anti-pattern ("Solution-jumping — a countermeasure proposed before the root cause is proven with data"). The statistics seam (§8 in CLAUDE.md) is the structural reason this plugin doesn't run hypothesis tests inline — the distinction between framing the question and running the math is load-bearing. The skip-to-solution failure mode is documented across Six Sigma literature; the specific consequence sequence above ("the real cause was never touched") is distilled from practitioner experience, not verified in a primary source.

---

_Last reviewed: 2026-06-03 by `claude`_
