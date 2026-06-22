---
name: measure-enforcement-quality
description: "Build the Trust & Safety measurement frame — prevalence (not just volume), enforcement precision/recall, time-to-action SLA, and appeal-overturn rate — with the formulas and the applied-statistics seam for eval validity. Reach for this when the user asks what to measure, whether moderation is working, or how to read a high overturn rate. Used by trust-safety-policy-lead + abuse-detection-engineer."
---

# Skill: measure-enforcement-quality

> **Invoked by:** `trust-safety-policy-lead` (the program-health frame) and `abuse-detection-engineer` (the detector's precision/recall and the prevalence it leaves behind).
>
> **When to invoke:** "what metrics prove moderation is working?"; "is our enforcement good?"; "our overturn rate is 20% — what does that mean?"; "what's our SLA on the worst queue?".
>
> **Output:** a metric set with formulas — prevalence, enforcement precision/recall, time-to-action SLA, appeal-overturn rate — plus the read on each and the `applied-statistics` seam for eval validity.

## Procedure

1. **Lead with prevalence, not volume.** "Posts removed" is a vanity metric. **Prevalence** = how much violating content a user actually encounters. Pull the formula and denominator choice from [`../../knowledge/trust-safety-metrics.md`](../../knowledge/trust-safety-metrics.md) (impressions-weighted, not content-count).
2. **Report enforcement precision and recall as a pair.** Precision = of the content we actioned, how much truly violated; recall = of the truly-violating content, how much we caught. One without the other hides the tradeoff. Tie both to the operating point the detector runs at.
3. **Measure time-to-action against an SLA, tiered by harm.** The critical tier (e.g. imminent-harm) has the tightest SLA; report the distribution (p50/p90), not just the mean — the tail is where the harm lives.
4. **Track the appeal-overturn rate as a quality signal, not noise.** A high overturn rate means the policy is ambiguous or the classifier is wrong — it is feedback, not a complaints box. Alarm above the per-category threshold.
5. **Send the eval to applied-statistics before quoting a number.** A precision/recall figure needs a confidence interval, an adequate labeled sample, and class-imbalance handling to be defensible — that is the `applied-statistics` seam.
6. **Assemble the scorecard** into the [`moderation-runbook`](../../templates/moderation-runbook.md) measurement section so the program is reviewed on the honest denominators.

## Worked example

> User: "We removed 2M pieces of spam last quarter — are we doing well?"

- **Reframe:** volume ≠ health. What's the **prevalence** — spam impressions per 10k total impressions — and is it falling?
- **Pair it:** at the auto-remove threshold, precision 0.94 / recall 0.68 → we're conservative; a third of spam still slips through (recall gap), which prevalence will confirm.
- **SLA:** p90 time-to-action on the high-harm queue is 9h against a 4h SLA → breach; investigate queue prioritization.
- **Overturn:** 14% of appeals overturned → the medium-tier category is ambiguous; tighten the policy definition.
- **Validity:** the precision/recall is from a 400-item labeled eval — send to `applied-statistics` for a CI before reporting it to leadership.

## Guardrails
- Never report enforcement volume as success — prevalence is the honest denominator.
- Never quote a single precision or recall number; report the pair, the operating point, the eval set, and the date.
- Treat a rising overturn rate as a policy/classifier defect, never as "users gaming appeals."
