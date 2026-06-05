# Perio Protocol Compliance Is a Clinical and Revenue Lever

**Status:** Pattern
**Domain:** Hygiene department / periodontal care
**Applies to:** `dental-practice`

---

## Why this exists

Periodontal disease prevalence in adult patients is significantly higher than most practices' perio treatment rates suggest. When a hygiene department under-diagnoses or under-presents periodontal treatment (scaling and root planing, periodontal maintenance), the practice is both missing a genuine patient-health need and leaving substantial revenue on the table — periodontal services typically carry higher reimbursement than prophylaxis. A practice with a low perio acceptance rate is usually facing a communication and presentation problem, not a demand problem: the patients with disease are already in the chair.

## How to apply

Track perio protocol compliance as a hygiene-department metric distinct from overall hygiene production.

```
Perio compliance metrics (track monthly):
- Perio prevalence rate: % of active hygiene patients with a documented perio diagnosis
  (target: reflects clinical reality — typically 40–50%+ of adults have some periodontal disease)
  [unverified — training knowledge; validate against CDC periodontal prevalence data]
- Perio treatment acceptance rate: SRP/perio maintenance recommended vs. accepted
  Target: ≥70% acceptance of presented perio treatment [unverified — training knowledge]
- Perio maintenance compliance: % of perio patients returning on 3–4 month recall
  Target: ≥80% compliance [unverified — training knowledge]

Presentation standards:
  [ ] Perio charting documented at each hygiene visit (probing depths, BOP, recession)
  [ ] Diagnosis communicated to patient in plain language with visual aid if available
  [ ] Treatment presented by hygienist + confirmed by dentist at exam
  [ ] Financial options and insurance coverage discussed before scheduling
```

**Do:**
- Establish a consistent perio charting and diagnosis standard across all hygienists — variation in charting thresholds produces variation in diagnosis rates, which is clinical, not just operational.
- Present periodontal treatment as a health recommendation, not an optional upgrade — patient language matters.
- Track SRP completion and perio maintenance compliance as separate metrics; they measure different parts of the protocol.

**Don't:**
- Use "patients don't want perio treatment" as an explanation for low perio acceptance without examining the presentation process.
- Allow the perio chart to age more than 12 months without an updated probing — outdated charting leads to missed diagnoses.
- Treat perio maintenance slots as interchangeable with prophylaxis slots in the schedule template; they are different appointments clinically and financially.

## Edge cases / when the rule does NOT apply

A practice with a documented patient population skewed young and healthy may have genuinely low perio prevalence — check against population-level benchmarks before concluding the protocol is underperforming.

## See also

- [`../agents/clinical-treatment-planner.md`](../agents/clinical-treatment-planner.md) — presentation of perio treatment falls under case acceptance mechanics.
- [`./the-hygiene-department-is-a-profit-engine-not-a-loss-leader.md`](./the-hygiene-department-is-a-profit-engine-not-a-loss-leader.md) — perio protocol compliance is the primary driver of hygiene revenue beyond basic recall.

## Provenance

Standard dental hygiene operations and periodontal protocol management; grounded in CDC/AAP periodontal prevalence data and dental practice management benchmarks; perio acceptance and compliance targets from Dental Economics and dental consulting practice frameworks.

---

_Last reviewed: 2026-06-05 by `claude`_
