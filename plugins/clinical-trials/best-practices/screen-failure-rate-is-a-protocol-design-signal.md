# Screen-Failure Rate Is a Protocol Design Signal

**Status:** Primary diagnostic
**Domain:** Enrollment / protocol feasibility
**Applies to:** `clinical-trials`

---

## Why this exists

A screen-failure rate above 30–40% is not bad luck — it is a legible signal that the eligibility criteria are misaligned with the enrolled population. At ~$6,533 per recruited patient and an average of 2–3 screens per enrolled patient in over-restricted protocols, screen failures are one of the most expensive and preventable drivers of enrollment shortfall. Ignoring the screen-failure rate while trying to fix enrollment by adding sites treats the symptom, not the cause.

## How to apply

Track and report screen-failure rate at least monthly, decomposed by the specific exclusion criterion that triggered each failure:

```
Screen-failure dashboard (monthly):
  Total screened this month:         ___
  Total failed this month:           ___
  Screen-failure rate:               ___% (target: <30% in general populations; <50% in rare disease)
  
  Failures by criterion:
    Criterion A (e.g., lab threshold):   ___ (___%)
    Criterion B (e.g., prior therapy):   ___ (___%)
    Criterion C (e.g., comorbidity):     ___ (___%)
    Other / consent withdrawal:          ___ (___%)
  
  Protocol amendment indicated?      Yes / No
  Amendment type:                    Minor / Substantial / N/A
```

When a single criterion accounts for >20% of screen failures, flag it immediately to the `protocol-design-specialist` for feasibility re-assessment. The amendment pathway (IRB/EC, HA notification) should be opened within 30 days of the signal, not after enrollment falls further behind.

**Do:**
- Log the specific criterion that drove each screen failure in the CTMS on the day of failure.
- Run a monthly screen-failure Pareto — the top 1–2 criteria usually account for >60% of failures.
- Present screen-failure data to the Protocol Review Committee (PRC) at every monthly review.
- Treat a protocol amendment to loosen a restrictive criterion as a legitimate enrollment rescue tool.

**Don't:**
- Aggregate screen failures into a single "screen fail" category without criterion-level detail — you lose the signal.
- Wait for a quarterly review to flag a screen-failure spike; enrolment cascades degrade quickly.
- Loosen criteria without regulatory notification where required — eligibility amendments are substantial in most jurisdictions.

## Edge cases / when the rule does NOT apply

In oncology trials selecting for specific biomarkers (e.g., a HER2+ enrichment design), screen-failure rates of 60–80%+ are expected by design. The rule still applies — the benchmark changes, and the screen-failure rate should be tracked against the pre-specified biomarker prevalence assumption. If the observed prevalence is lower than assumed, that is the actionable signal.

## See also

- [`../agents/protocol-design-specialist.md`](../agents/protocol-design-specialist.md) — owns eligibility criteria review and protocol amendment feasibility.
- [`../agents/clinical-operations-manager.md`](../agents/clinical-operations-manager.md) — owns the CTMS and recruitment funnel data.
- [`./enrollment-is-a-rate-not-a-count-track-the-funnel.md`](./enrollment-is-a-rate-not-a-count-track-the-funnel.md) — screen-failure feeds directly into funnel efficiency.

## Provenance

Codifies standard industry practice referenced in TransCelerate BioPharma enrollment benchmarks and SCRS (Society for Clinical Research Sites) site productivity surveys. Screen-failure rate as a protocol design signal is a consensus position in clinical operations management.

---

_Last reviewed: 2026-06-05 by `claude`_
