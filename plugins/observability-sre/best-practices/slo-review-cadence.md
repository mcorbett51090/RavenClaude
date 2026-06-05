# Review SLOs on a regular cadence — they drift from user reality

**Status:** Pattern
**Domain:** SRE / SLO management
**Applies to:** `observability-sre`

---

## Why this exists

An SLO written at launch reflects the team's best guess about user tolerance at that moment. As the product evolves, users' expectations shift, traffic patterns change, and the SLI query itself may no longer measure what it once did. A stale SLO breeds one of two failure modes: a target so easy that the error budget is never spent (no signal that reliability is over-engineered) or a target so tight that the budget is perpetually exhausted (no capacity for velocity). A regular review cycle keeps SLOs honest.

## How to apply

Schedule a quarterly SLO review meeting. The agenda has three questions: Is the SLI still measuring user-visible pain? Is the target still reflective of user need? Did the error budget policy drive good decisions?

| Review item | Trigger for change |
|---|---|
| SLI query accuracy | Service has new endpoints; SLI query misses them |
| Target value | Sustained budget surplus (loosen) or perpetual exhaustion (tighten or split) |
| Measurement window | Rolling 28 days is standard; change if release cadence has shifted |
| Error budget policy | Policy was consistently overridden — record why or update it |

```yaml
# Proposed quarterly review checklist
- [ ] Validate SLI query covers all user-facing endpoints/operations
- [ ] Check budget consumption last 90 days — were there freeze decisions?
- [ ] Compare target vs. actual: was the target aspirational or operational?
- [ ] Review postmortem action items that reference this SLO
- [ ] Update the SLO doc with today's review date and any changes
```

**Do:**
- Assign a named owner to each SLO who is responsible for the review.
- Log the review outcome even if no changes are made (a dated "reviewed, no changes" is valuable).
- Treat a perpetually-full budget as a signal to invest in velocity, not to tighten the target automatically.

**Don't:**
- Change an SLO target in response to a single incident; wait for the pattern.
- Remove an SLO because it was missed — fix the reliability problem instead.
- Set SLO targets by committee without looking at actual user pain data.

## Edge cases / when the rule does NOT apply

Newly launched services with fewer than three months of production data should not lock in SLO targets — establish a provisional target, run the review after 90 days of data, then formalize.

## See also

- [`../agents/sre-reliability-engineer.md`](../agents/sre-reliability-engineer.md) — owns SLO design and the review process.
- [`./error-budget-is-the-decision-rule.md`](./error-budget-is-the-decision-rule.md) — the error budget consumption data is the input to the review.

## Provenance

Codifies the SLO review cadence recommended in Google SRE Workbook Chapter 2 ("Implementing SLOs") and the SLO Document template practice.

---

_Last reviewed: 2026-06-05 by `claude`_
