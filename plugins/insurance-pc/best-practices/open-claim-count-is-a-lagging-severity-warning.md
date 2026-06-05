# Rising Open Claim Count Is a Lagging Severity Warning Signal

**Status:** Primary diagnostic
**Domain:** Claims operations
**Applies to:** `insurance-pc`

---

## Why this exists

The paid loss ratio is a lagging indicator — it reflects claims that have been resolved. The open claim count and the case reserve adequacy on open claims are leading indicators of where the incurred loss ratio is going. A rising open claim count, especially combined with a longer average age of open claims, signals that claims are not closing and that the outstanding reserve will continue to develop. Waiting until the development appears in the paid loss ratio to recognize the severity problem means the reserve was inadequate for one or more prior reporting periods — and the cost of the late recognition is borne in the current period's combined ratio.

## How to apply

Monitor open claim count, average age of open claims, and claim closure rate as standard metrics in the claims management report, alongside the loss ratio.

```
Open Claim Metrics — Monthly Claims Management Report
──────────────────────────────────────────────────────
Metric                      | Current month | Prior month | 3-month trend
─────────────────────────────────────────────────────────────────────────
Open claim count            | XXX           | XXX         | ▲/▼/─
New claims opened           | XXX           |             |
Claims closed               | XXX           |             |
Closure rate (%)            | XX.X%         | XX.X%       | ▲/▼/─
Average age of open claims  | XX days       | XX days     | ▲/▼/─
Claims open > 180 days (%)  | XX.X%         | XX.X%       | ▲/▼/─
Average case reserve / open | $XXX          | $XXX        | ▲/▼/─

Red flags:
  □ Open count rising while new claim count is flat or falling
    → Closure rate declining; investigate handler capacity, litigation, complexity
  □ Average age increasing 3+ months in a row
    → Systemic closure problem; escalate to claims manager
  □ Average case reserve / open increasing without a change in mix
    → Reserve strengthening in the open inventory; watch for IBNR impact
```

**Do:**
- Segment the open claim metrics by line of business — a rising open count in commercial auto liability is a different problem from a rising count in property.
- Correlate open claim age with the case reserve on those claims — the oldest open claims should not have the lowest case reserves.
- Review the top 10 open claims by case reserve amount monthly; large open claims with stale reserve dates and no recent activity notes are a reserve-adequacy risk.

**Don't:**
- Treat the closure rate as the sole performance metric for claims handlers — closing files quickly at inadequate reserves is worse than holding them open at adequate ones.
- Allow the "average age" metric to mask a bimodal distribution (many fast-closing small claims and a long tail of complex open claims); segment by complexity or reserve tier.
- Ignore an upward trend in the 180+ day open percentage; this cohort disproportionately drives reserve development.

## Edge cases / when the rule does NOT apply

- **Claims-made policies** where the reporting date governs, not the accident date — open count metrics must be segmented by reporting year, not accident year, to be meaningful.
- **Workers' compensation long-term disability** (pension-type claims) — open claim counts are structurally high and represent ongoing payment obligations; the relevant metric is active-payment claim count vs. claim reserve adequacy, not closure rate.

## See also

- [`../agents/claims-specialist.md`](../agents/claims-specialist.md) — owns claims operations metrics, cycle time management, and reserve adequacy at the claim level.
- [`./claims-is-a-leakage-and-cycle-time-problem-not-just-payout.md`](./claims-is-a-leakage-and-cycle-time-problem-not-just-payout.md) — the house opinion that frames cycle time as a managed metric; this doc operationalizes open-count monitoring as the leading indicator within that framework.

## Provenance

Codifies the claims-specialist's open-claim monitoring discipline from the insurance-pc plugin's CLAUDE.md §3 #7 (claims is a leakage-and-cycle-time problem) and the `knowledge/pc-kpi-glossary.md`. The open-count/age/closure-rate metrics reflect standard P&C claims management KPI practice.

---

_Last reviewed: 2026-06-05 by `claude`_
