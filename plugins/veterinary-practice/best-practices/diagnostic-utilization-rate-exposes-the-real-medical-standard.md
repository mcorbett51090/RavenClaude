# Diagnostic Utilization Rate Exposes the Real Medical Standard

**Status:** Primary diagnostic
**Domain:** Clinical protocols / practice economics
**Applies to:** `veterinary-practice`

---

## Why this exists

The diagnostic utilization rate — the percentage of visits of a given type where a specific diagnostic panel is performed — is the observable proxy for the practice's actual medical standard. A practice that says it recommends pre-anesthetic bloodwork for every patient over age 7 but has a 25% utilization rate for that panel in that cohort is not following its own protocol. The utilization rate makes the gap between stated standard and actual behavior visible and measurable, which is a prerequisite for closing it. Without utilization data, the gap is invisible — and an invisible gap cannot be managed.

## How to apply

Configure the PIMS to report diagnostic utilization by procedure and patient cohort, and review monthly.

```
Diagnostic utilization dashboard:
Key metrics (review monthly, by DVM and practice-wide):

1. Pre-anesthetic diagnostics:
   - % of patients ≥7 years with a scheduled anesthetic procedure who received a
     CBC/chemistry panel at or before the procedure
   - Target: ≥90% [unverified — set to your practice standard]

2. Annual wellness diagnostics (senior screen):
   - % of patients ≥7 years who received an annual chemistry/CBC + urinalysis in
     the last 12 months
   - Target: ≥60% [unverified — varies by market; benchmark against peer practices]

3. Parasite diagnostics:
   - % of wellness visits including a fecal parasite screen
   - Target: per CAPC (Companion Animal Parasite Council) guidelines by region

4. Diagnostic tier at sick visit:
   - % of sick visits (vomiting/GI, urinary, respiratory) where a minimum diagnostic
     workup consistent with the practice's protocol was performed or offered
   - Variation >20% between DVMs on the same case type → protocol gap or coaching need

Per-DVM view:
  - Rank diagnostic utilization per DVM per case type
  - Highlight outliers — both below-protocol (under-diagnosing) and above-protocol (over-ordering)
  - Use in monthly DVM performance conversations as quality, not billing, data
```

**Do:**
- Pull the diagnostic utilization report from the PIMS directly — don't rely on staff recall or "we think we're doing it."
- Present utilization data as a quality improvement metric, framed around patient outcomes, not revenue.
- Use the DVM-level variation data to drive protocol compliance coaching, not compensation penalties.

**Don't:**
- Set utilization targets without grounding them in a named clinical protocol — a utilization target disconnected from a specific standard is just a revenue quota.
- Confuse utilization rate with recommendation rate — a DVM who recommends 90% of the time but whose clients only accept 40% has a different problem than a DVM who recommends 40% of the time.
- Conflate high diagnostic utilization with quality; it is a compliance proxy, not a quality measure, and over-ordering should be flagged the same way under-ordering is.

## Edge cases / when the rule does NOT apply

Emergency triage presentations have different diagnostic workup logic driven by clinical urgency and patient stability — utilization rates on emergency visits should not be benchmarked against the elective/wellness standards.

## See also

- [`../agents/clinical-protocol-specialist.md`](../agents/clinical-protocol-specialist.md) — owns protocol design and utilization compliance.
- [`../agents/vet-finance-analyst.md`](../agents/vet-finance-analyst.md) — diagnostic utilization affects ACT and revenue analytics; the two views must reconcile.
- [`./multi-dvm-protocol-variation-is-a-margin-and-quality-problem.md`](./multi-dvm-protocol-variation-is-a-margin-and-quality-problem.md) — diagnostic utilization data is the primary evidence of multi-DVM variation.

## Provenance

Codifies the CLAUDE.md §3 #4 compliance principle (compliance is medicine and revenue) at the diagnostic-specific level; grounded in AAHA accreditation diagnostic standards and veterinary practice management consulting.

---

_Last reviewed: 2026-06-05 by `claude`_
