# Write the error-budget policy before you set the SLO target

**Status:** Absolute rule
**Domain:** SRE / SLO management
**Applies to:** `observability-sre`

---

## Why this exists

An SLO without a written error-budget policy is a metric, not a decision-making tool. The policy is what transforms "we consumed 40% of this month's budget" from a data point into an action: freeze risky deploys, stop toil, call a reliability sprint. Without the policy pre-agreed and written down, the response to budget consumption becomes a recurring debate that consumes the same reliability-vs-velocity meeting every week — and the meeting always ends differently depending on who attends. The policy is the pre-committed answer; the SLO is just the trigger.

## How to apply

Write the error-budget policy document before finalizing the SLO target. The policy must answer four questions: what action happens at each budget consumption threshold, who decides to override the policy, what "resuming velocity" looks like, and how often the policy is reviewed.

```markdown
# Error Budget Policy — MyService Availability SLO
**SLO:** 99.9% availability (22 min/month budget)
**Policy owner:** Checkout Team + SRE Lead
**Last reviewed:** 2026-06-05

## Consumption thresholds and actions

| Budget consumed | Action | Decision-maker |
|---|---|---|
| < 50% | Normal velocity; ship features at will | Team |
| 50–80% | Increase reliability investment; reduce risky changes | Team + SRE lead |
| 80–100% | Freeze new features; reliability-only work until budget recovers | Engineering manager |
| 100% (budget exhausted) | Deploy freeze; escalate to director; reliability sprint this week | Director + SRE lead |

## Override criteria
An override of the freeze at 80-100% requires:
1. A named decision-maker (EM or above) sign-off in writing.
2. A documented rollback plan for the change.
3. Review in the next postmortem.

## Budget recovery
Resume normal velocity when 7-day trailing consumption rate projects < 50% for the remainder of the window.

## Policy review
Quarterly, at the SLO review meeting.
```

**Do:**
- Write the policy document before announcing the SLO target — the target is meaningless without the policy.
- Get explicit sign-off from the engineering manager and product counterpart on the freeze thresholds.
- Link the policy document from the SLO document and from the runbook.

**Don't:**
- Set the freeze threshold at 100% (budget exhausted) — that means users already had the bad experience.
- Write the policy so conservatively that budget is never spent (no risk ever taken) — that's over-engineering reliability.
- Change the policy retroactively to avoid a freeze that inconveniently applies to a shipped feature.

## Edge cases / when the rule does NOT apply

Internal tools with no revenue or SLA dependency can have a lightweight policy ("notify the team, no automatic freeze"). The rule is non-negotiable for any service with an external SLA or customer-visible impact.

## See also

- [`../agents/sre-reliability-engineer.md`](../agents/sre-reliability-engineer.md) — owns the SLO design and budget policy authoring.
- [`./error-budget-is-the-decision-rule.md`](./error-budget-is-the-decision-rule.md) — the budget policy is what makes the budget a decision rule.

## Provenance

Codifies the error budget policy concept from Google SRE Workbook Chapter 2 ("Implementing SLOs") and the SRE Workbook's sample error budget policy template.

---

_Last reviewed: 2026-06-05 by `claude`_
