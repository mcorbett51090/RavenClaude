# Measure prevalence, not just enforcement volume

**Status:** Absolute rule
**Domain:** Trust & Safety measurement
**Applies to:** `trust-and-safety`

---

## Why this exists

"We removed 2 million posts" feels like progress and proves nothing. Volume rises when you enforce harder **and** when abuse rises — it cannot tell you whether a user is safer (house opinion #3). The honest question is **prevalence**: how much violating content does a user actually *experience*? A post nobody saw and a viral post seen a million times are not equal harm, so the denominator must be **impressions**, not content counts. Prevalence is the headline; enforcement volume, precision, and recall are supporting numbers that only make sense against it. Reporting volume as success is the vanity metric this plugin exists to refuse.

## How to apply

Lead every program-health report with prevalence, trended and per-category; relegate volume to context.

```
prevalence = violating impressions / total impressions        (per 10k, trended, per category)

Read it WITH:
  precision / recall  — at the operating point, on a named eval set + date
  time-to-action SLA  — p90 per harm tier (read the tail, not the mean)
  appeal-overturn rate — the quality signal

Validity: send any precision/recall number to applied-statistics for a CI before quoting it.
```

**Do:**
- Lead with prevalence on impressions; trend it and break it out by policy category.
- Report precision and recall as a pair, tied to the operating point and the eval set.
- Send a measured precision/recall to `applied-statistics` for a confidence interval before it goes to leadership.

**Don't:**
- Present "items actioned" as a safety outcome — it is an activity count.
- Quote a single precision or recall number with no operating point, eval set, or date.
- Read a p50 SLA and ignore the p99 tail where the real harm sits.

## Edge cases / when the rule does NOT apply

- **Cold-start / pre-instrumentation** programs may have to start with volume + spot-checks while a prevalence-measurement panel is built — but volume is the placeholder, not the goal, and the plan must say so.
- **Extremely rare, extremely severe** harms are measured by *time-to-action* and *recall on known cases*, not prevalence (the base rate is too low to estimate stably) — pick the denominator that matches the harm.

## See also

- [`../knowledge/trust-safety-metrics.md`](../knowledge/trust-safety-metrics.md) — prevalence, precision/recall, SLA, and overturn-rate formulas.
- [`../skills/measure-enforcement-quality/SKILL.md`](../skills/measure-enforcement-quality/SKILL.md) — the scorecard procedure.
- [`../agents/abuse-detection-engineer.md`](../agents/abuse-detection-engineer.md) — the eval-validity (`applied-statistics`) seam.

## Provenance

Codifies house opinion #3 (measure prevalence, not volume) in [`../CLAUDE.md`](../CLAUDE.md) §3. Consensus Trust & Safety measurement practice; the statistical-validity caveat routes to the `applied-statistics` plugin.

---

_Last reviewed: 2026-06-17 by `claude`_
