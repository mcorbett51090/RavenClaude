---
name: srm-detection
description: "Procedure for detecting and diagnosing Sample-Ratio Mismatch in A/B experiments — covers the chi-squared test, common causes by layer, and the decision rule for whether to trust or discard a result."
---

# SRM Detection

## When to Use This

Before reading any metric from an A/B experiment. Sample-Ratio Mismatch (SRM) means the assignment split doesn't match the intended split — which means the groups are not comparable, and any observed difference may be assignment bias rather than treatment effect. Always check SRM before interpreting results.

## What is SRM?

If an experiment is designed as 50/50, you expect roughly equal users in each variant. SRM occurs when the actual split deviates more than chance explains. A 50/50 experiment that actually lands 52/48 isn't necessarily SRM — with enough traffic, even a 51/49 can be statistically significant. The question is whether the deviation is beyond chance.

## Step 1 — Run the Chi-Squared Test

Collect: `n_control`, `n_treatment`, and the intended split ratio (e.g., 0.5 / 0.5).

```python
from scipy.stats import chisquare

n_control = 10432
n_treatment = 9811
total = n_control + n_treatment
intended_split = 0.5  # 50/50

expected_control = total * intended_split
expected_treatment = total * (1 - intended_split)

stat, p_value = chisquare(
    f_obs=[n_control, n_treatment],
    f_exp=[expected_control, expected_treatment]
)

print(f"Chi-squared: {stat:.2f}, p-value: {p_value:.4f}")
# p < 0.01 → SRM present
```

**Decision rule:**
- `p >= 0.01`: no SRM detected — proceed to metric analysis.
- `p < 0.01`: SRM present — **do not read metrics**; investigate the cause first.

Use `p < 0.01` (not 0.05) as the threshold — you're not testing a hypothesis about the product, you're testing the integrity of the apparatus. A more conservative threshold reduces false "all clear" verdicts.

## Step 2 — Identify the Cause

SRM almost always comes from one of these layers:

| Layer | Common cause | Diagnostic |
|---|---|---|
| **Assignment** | Hash collision; non-uniform random; assignment bug in SDK | Check assignment distribution by time segment; look for all-one-variant periods |
| **Exposure logging** | Inconsistent exposure event firing; event dropped under load | Compare assignment count vs exposure event count per variant |
| **Filtering** | Post-assignment exclusion applied to only one variant (e.g., bot filter, geo filter) | Check exclusion counts per variant |
| **Redirect / UX** | One variant redirects to a different page, causing session drop | Compare bounce rates per variant in the first 30 seconds |
| **Instrumentation** | Tracking code only fires in treatment (e.g., new pixel added to variant) | Check event count per variant for session-start or page-load events |
| **Deployment / rollout** | Treatment wasn't fully deployed; some hosts serving old code | Check variant exposure by host/pod; look for partial rollout |

## Step 3 — Segment the Check

If the overall chi-squared is borderline, run segmented checks:

```python
# Check by day — SRM that appeared on a specific date points to a deploy or config change
for date, group in df.groupby('date'):
    n_c = group[group.variant == 'control'].user_id.nunique()
    n_t = group[group.variant == 'treatment'].user_id.nunique()
    stat, p = chisquare([n_c, n_t], [n_c + n_t) * 0.5, (n_c + n_t) * 0.5])
    print(f"{date}: n_c={n_c}, n_t={n_t}, p={p:.4f}")
```

A spike on a specific date points to a deployment event. A consistent imbalance from day one points to an assignment or exposure bug.

## Decision Table

| SRM result | Action |
|---|---|
| No SRM (`p >= 0.01`) | Proceed to metric analysis |
| SRM from known, correctable cause (e.g., one day of bad exposure logging) | Exclude the affected period; re-run chi-squared on clean data |
| SRM from assignment bug or hash collision | Stop experiment; fix the assignment mechanism; restart with clean assignment |
| SRM from filtering applied post-assignment | Redesign experiment to apply filter pre-assignment (only assign eligible users) |
| SRM cause unknown after investigation | Do not ship on this result; escalate to experimentation platform team |

**Never ship a result with unexplained SRM.** The metric difference may be real, but you cannot know which direction the bias runs.

## Pitfalls

- Reading the primary metric before checking SRM — confirmation bias makes it harder to invalidate a significant result afterward.
- Using `p < 0.05` as the SRM threshold — too permissive; 5% false negatives on apparatus checks are unacceptable.
- Fixing SRM by trimming one variant to match the other's size — the trimmed users are not random; you've introduced selection bias.
- Checking SRM only at experiment end — check at 24 hours, 72 hours, and weekly to catch deployment-window bugs before the experiment runs to completion.

## See Also

- [`../../agents/experimentation-architect.md`](../../agents/experimentation-architect.md) — experiment lifecycle, SRM and trustworthiness checks
- [`../../agents/feature-flag-engineer.md`](../../agents/feature-flag-engineer.md) — assignment and exposure logging infrastructure
