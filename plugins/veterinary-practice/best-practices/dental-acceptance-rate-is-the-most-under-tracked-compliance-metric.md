# Dental Acceptance Rate Is the Most Under-Tracked Compliance Metric

**Status:** Pattern
**Domain:** Recommended-care compliance / clinical revenue
**Applies to:** `veterinary-practice`

---

## Why this exists

Veterinary dental disease is the most prevalent condition in companion animals, yet dental recommendation acceptance rates in most practices remain low — typically 30–60% of patients recommended for a dental procedure actually receive one in the same calendar year. [unverified — training knowledge] This gap is simultaneously a patient-health problem (dental disease is painful and systemic) and the largest single compliance revenue opportunity in most general practices. Unlike exotic diagnostics, dentals are routine, billable, and every patient with grade 2+ dental disease who doesn't receive treatment is an outcome and revenue gap. The reason dentals are under-tracked is that recommendation and acceptance are logged in different parts of the PIMS or not logged at all.

## How to apply

Instrument dental recommendation and acceptance as a named compliance metric in the practice scorecard.

```
Dental compliance tracking:
Metrics (monthly):
  - Dental examination score recorded at each wellness exam: % of visits with a dental score
    Target: 100% of wellness exams have a dental score documented [unverified]
  - Dental procedure recommended: % of patients with grade 2+ who have a dental recommendation
    in the active treatment plan
  - Dental acceptance rate: patients who received a recommended dental in the trailing 12 months
    ÷ patients with a dental recommendation in the same period
    Target: ≥65% acceptance within 12 months of recommendation [unverified — training knowledge]

Presentation standards:
  [ ] Dental score communicated verbally at every wellness visit (not only when grade 3+)
  [ ] Before-and-after photo capability or dental chart visual used in presentation
  [ ] Cost estimate presented at the same time as the recommendation — don't make the client ask
  [ ] Preanesthetic bloodwork discussed and offered at time of dental scheduling
  [ ] Recheck recommendation logged for clients who decline, with a 3–6 month follow-up scheduled
```

**Do:**
- Configure the PIMS to require a dental score entry at every wellness exam — unenforced documentation disappears.
- Present dental recommendations at every wellness visit regardless of prior-year acceptance, because dental disease progresses and the prior refusal may no longer stand.
- Track dental acceptance per DVM — variation between doctors on a multi-DVM team is a coaching and standardization signal.

**Don't:**
- Wait until grade 3 or 4 disease to recommend a dental — grade 2 is the actionable threshold, and early recommendation improves acceptance rates.
- Present dental cost without also presenting the health consequence of deferring — the "why now" clinical context is the strongest acceptance driver.
- Log the recommendation only in the exam notes; it must be in a discrete treatment plan field the compliance report can pull.

## Edge cases / when the rule does NOT apply

Patients with significant anesthetic risk (severe cardiac, hepatic, or renal disease, or geriatric patients flagged as high-risk by the attending DVM) may not be candidates for routine dental procedures — exclude them from the acceptance rate denominator with a documented reason.

## See also

- [`../agents/clinical-protocol-specialist.md`](../agents/clinical-protocol-specialist.md) — owns recommended-care compliance protocols including dental.
- [`./compliance-is-medicine-and-revenue-track-it.md`](./compliance-is-medicine-and-revenue-track-it.md) — dental acceptance is a specific instance of the broader compliance tracking mandate.

## Provenance

Codifies the recommended-care compliance principle (CLAUDE.md §3 #4) for the dental use case; grounded in AVDC (American Veterinary Dental College) and AAHA Dental Care Guidelines; acceptance rate benchmarks from veterinary practice management consulting.

---

_Last reviewed: 2026-06-05 by `claude`_
