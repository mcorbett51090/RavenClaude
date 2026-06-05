# Investigator Selection Drives Data Quality, Not Just Enrollment

**Status:** Pattern
**Domain:** Site management / investigator qualification
**Applies to:** `clinical-trials`

---

## Why this exists

Investigator selection is typically framed as an enrollment-capacity exercise — does this site have enough patients? But the investigator's prior trial experience, staff stability, and regulatory inspection history are stronger predictors of data quality, protocol compliance, and audit readiness than the patient volume estimate alone. A high-volume site run by an inexperienced or audit-cited investigator creates disproportionate data management burden, protocol deviations, and submission risk that can offset the enrollment gain.

## How to apply

Evaluate investigator candidates on a two-axis scorecard: enrollment capacity and quality track record. Weight both before selecting.

```
Investigator selection scorecard:
Capacity axis (0–5):
  - Estimated eligible patients per month (from feasibility survey)
  - Therapeutic area patient flow (referral network vs. captive population)
  - Available visit slots and dedicated study coordinator FTE

Quality axis (0–5):
  - Prior trial experience in this indication and phase
  - FDA/competent-authority inspection history (no critical findings, no Warning Letters)
  - Protocol deviation rate in prior studies (request from sponsor/CRO network)
  - Site staff stability (PI + coordinator tenure >18 months preferred)
  - IRB/ethics turnaround time (proxy for administrative readiness)

Scoring rule: sites with Quality score <3 require Medical Monitor sign-off regardless of Capacity score.
```

**Do:**
- Request the investigator's CV and GCP training certificate as standard, not as an exception.
- Check FDA Establishment Inspection Report (EIR) database and EudraGMP for inspection findings before selection.
- Factor in the coordinator-to-protocol ratio at the site — overloaded coordinators produce the most data-entry errors.

**Don't:**
- Select a site based solely on the investigator's enrollment estimate from the feasibility survey — these are systematically optimistic.
- Ignore historical protocol deviation rate because "this protocol is simpler" — site behavior patterns are sticky.
- Treat site qualification as a one-time event; re-qualify sites at protocol amendment if the amendment materially changes the visit burden.

## Edge cases / when the rule does NOT apply

Rare-disease trials where the investigator is the only expert center for that indication — enrollment feasibility may override quality concerns, with enhanced monitoring to compensate.

## See also

- [`../agents/clinical-operations-manager.md`](../agents/clinical-operations-manager.md) — owns site selection, qualification, and activation.
- [`./site-activation-is-the-schedules-long-pole.md`](./site-activation-is-the-schedules-long-pole.md) — activation timing follows selection; quality problems discovered post-selection delay activation.
- [`./site-performance-tiers-concentrate-monitoring-resources.md`](./site-performance-tiers-concentrate-monitoring-resources.md) — performance tier assignment begins at selection.

## Provenance

Standard sponsor/CRO clinical operations practice; grounded in ICH E6(R3) investigator qualification requirements and FDA regulations 21 CFR 312.53; the two-axis model codifies site-management practice observed across phase-II/III drug and device programs.

---

_Last reviewed: 2026-06-05 by `claude`_
