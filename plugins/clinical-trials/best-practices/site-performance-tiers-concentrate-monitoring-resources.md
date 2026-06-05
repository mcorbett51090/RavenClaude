# Site Performance Tiers Concentrate Monitoring Resources

**Status:** Pattern
**Domain:** Site management / monitoring
**Applies to:** `clinical-trials`

---

## Why this exists

In a typical multi-site trial, 20% of sites deliver 80% of enrollment. Treating all sites identically — equal monitoring visit frequency, equal CRA attention, equal sponsor escalation — wastes monitoring budget on dormant sites while under-serving the high-enrollers that carry the timeline. Risk-based monitoring (RBM) is the regulatory-endorsed framework (ICH E6 R3, FDA guidance 2013/2023), and site performance tiering is how RBM is operationalized.

## How to apply

Assign each site a performance tier monthly using these three dimensions:

| Dimension | High (Tier 1) | Mid (Tier 2) | Low (Tier 3) |
|---|---|---|---|
| Enrollment rate vs. target | ≥90% of target | 50–89% | <50% |
| Protocol deviation rate | <2% of visits | 2–5% | >5% |
| Data entry lag (days to entry) | ≤3 days | 4–7 days | >7 days |

**Tier 1 (high-performing):** remote monitoring with quarterly on-site visit; provide support, not burden.

**Tier 2 (mid):** monthly remote check-in plus bi-monthly on-site; identify specific barriers (staffing, equipment, patient population).

**Tier 3 (low-performing):** escalation within 30 days — on-site visit, corrective action plan (CAP), 60-day decision gate (rescue vs. replace).

```
Site tier review cadence:
  Monthly: Re-tier all sites against current-month data.
  Quarterly: Review tier distribution — if >40% of sites are Tier 3, re-assess the protocol or site selection criteria.
  Milestone: At 25%, 50%, and 75% enrollment, run a formal site performance report for the Steering Committee.
```

**Do:**
- Apply tiering prospectively, not as a retrospective audit.
- Give every Tier 3 site a written CAP with a named CRA owner and a 30-day check-in.
- Document tiering criteria in the monitoring plan before the first site initiates.

**Don't:**
- Use enrollment rate as the only tiering dimension — a high enroller with high deviation rates is a data quality risk.
- Replace a Tier 3 site without first running a root-cause analysis (staffing gap vs. patient population vs. protocol burden).
- Apply Tier 1 monitoring intensity to a newly activated site regardless of enrollment; new sites need closer early oversight.

## Edge cases / when the rule does NOT apply

Single-site or small-n trials (e.g., a 3-site Phase I FIH) cannot be tiered meaningfully by statistical performance. Apply RBM principles differently: focus on a risk-based source data verification (SDV) rate rather than site tiering.

## See also

- [`../agents/clinical-operations-manager.md`](../agents/clinical-operations-manager.md) — owns site management, monitoring, and CRA deployment.
- [`../agents/trials-engagement-lead.md`](../agents/trials-engagement-lead.md) — escalation path for persistent Tier 3 sites to the sponsor/CRO leadership.
- [`./site-activation-is-the-schedules-long-pole.md`](./site-activation-is-the-schedules-long-pole.md) — site activation quality drives early-stage tier assignment.

## Provenance

Codifies ICH E6(R3) risk-based monitoring principles and FDA "Oversight of Clinical Investigations — A Risk-Based Approach to Monitoring" (Aug 2013, updated 2023). Tiering as a resource-allocation mechanism is standard CRO practice.

---

_Last reviewed: 2026-06-05 by `claude`_
