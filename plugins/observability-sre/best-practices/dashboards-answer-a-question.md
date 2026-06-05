# A dashboard answers a specific question — not "show me everything"

**Status:** Pattern
**Domain:** Observability / dashboards
**Applies to:** `observability-sre`

---

## Why this exists

A dashboard with 40 panels covering every metric the service emits is an intimidating wall that tells an engineer nothing quickly during an incident. They end up writing ad-hoc queries anyway because the dashboard doesn't answer the question they arrived with. Effective dashboards are narrow-purpose: "Is the service healthy right now?" (an overview dashboard), or "Where is the P99 latency coming from?" (an investigation dashboard). A dashboard with a stated question can be evaluated: does it answer the question in under 30 seconds?

## How to apply

Before building a dashboard, write down the question it answers and who the audience is. Design every panel to contribute to answering that question; delete any panel that doesn't.

Dashboard taxonomy:

| Type | Question | Audience | Panel count |
|---|---|---|---|
| Service health / RED | "Is this service healthy right now?" | On-call, team | < 8 panels |
| Capacity / saturation | "Are we approaching a resource limit?" | SRE, ops | < 10 panels |
| Investigation / deep-dive | "Which component is causing the latency spike?" | Engineer investigating | 10-20 panels |
| Business / KPI | "How are users engaging today vs. last week?" | Product, EM | < 12 panels |
| SLO burn-rate | "How fast is the error budget consuming?" | On-call, SRE | 3-5 panels (fast+slow burn) |

```
# Dashboard design checklist
- [ ] The dashboard title is the question it answers
- [ ] Primary panels are above the fold (visible without scrolling)
- [ ] Every panel has a title and a unit (ms, %, rps — not "value")
- [ ] Thresholds (SLO target, capacity limit) are drawn as reference lines
- [ ] The time picker default shows the most relevant window (1h for ops, 7d for trends)
- [ ] A link to the runbook or related dashboard appears in the description
```

**Do:**
- Name the dashboard "Is MyService Healthy?" or "MyService Latency Investigation" — not "MyService Metrics".
- Limit the service overview to the RED metrics (Rate, Errors, Duration) plus the SLO burn-rate panel.
- Link dashboards: overview → investigation → trace exemplar (not one mega-dashboard).

**Don't:**
- Add panels "just in case" — they dilute the signal from the panels that matter.
- Build a dashboard with no designated owner — it will drift out of date.
- Use auto-generated "all metrics" dashboards as a substitute for purpose-built ones.

## Edge cases / when the rule does NOT apply

Ephemeral investigation dashboards built during an active incident to answer a one-time question are exempt from the "delete what doesn't contribute" rule. Delete them or archive them after the incident closes.

## See also

- [`../agents/observability-engineer.md`](../agents/observability-engineer.md) — owns dashboard design and the instrumentation pipeline.
- [`./measure-the-four-golden-signals.md`](./measure-the-four-golden-signals.md) — the four golden signals are the foundation of the service health dashboard.

## Provenance

Codifies the "dashboards as questions" framing from Cindy Sridharan's "Monitoring in the Time of Cloud Native" and the RED method (Rate/Errors/Duration) from Tom Wilkie, now standard practice in the Grafana ecosystem.

---

_Last reviewed: 2026-06-05 by `claude`_
