# Wellness Plan Programs Smooth Revenue and Improve Compliance

**Status:** Pattern
**Domain:** Practice economics / patient compliance
**Applies to:** `veterinary-practice`

---

## Why this exists

Wellness plans — prepaid or monthly-billed packages covering routine preventive care (exams, vaccines, parasite prevention, basic diagnostics) — address two of the most persistent veterinary practice problems simultaneously. For the practice, they convert episodic revenue into recurring monthly income, reducing the seasonal and appointment-driven cash-flow volatility that makes staffing and expense management difficult. For patients, prepayment and bundling dramatically improve preventive care compliance rates because the economic barrier to each individual visit is removed. A practice that does not offer a wellness plan is leaving both compliance and revenue predictability on the table.

## How to apply

Design wellness plans as products, not just discount packages.

```
Wellness plan design principles:
1. Identify the core preventive bundle (what every patient should receive annually):
   - Annual exam(s): 1–2 depending on life stage
   - Core vaccines: per AAHA vaccination guidelines
   - Parasite prevention: flea/tick/heartworm based on regional risk
   - Annual diagnostics: CBC/chemistry for senior patients; fecal for all

2. Pricing model:
   - Price the plan so total value of included services exceeds monthly-payment total by 15–20%
     — the client perceives savings; the practice captures the compliance volume
   - Offer monthly auto-debit (EFT) — lowers the perceived cost, increases plan adoption
   - Tier by life stage: puppy/kitten, adult, senior — different service bundles, different price points

3. Enrollment targets [unverified — training knowledge]:
   - Target: ≥30% of active patients enrolled in a wellness plan
   - Track: monthly plan enrollments, lapses, and active plan count

4. Compliance tracking:
   - Compare: services utilized by plan patients vs. non-plan patients for the same age cohort
   - Expected finding: plan patients have significantly higher preventive care utilization
   - Use this data to justify the plan to skeptical DVMs and staff

5. Operational requirements:
   - Designate a plan administrator (front-desk lead or practice manager) who owns enrollment and renewal
   - Configure PIMS to flag plan patients and auto-generate reminders for included services
   - Define the lapse protocol: auto-lapse after missed payment, grace period, reinstatement terms
```

**Do:**
- Present wellness plans at every new-patient appointment and at first wellness visit for existing patients.
- Train the entire team — DVMs and technicians, not only the front desk — to explain the plan's clinical value.
- Review plan pricing annually when the fee schedule is reviewed; plans that are underpriced relative to current service fees erode margin.

**Don't:**
- Design plans as pure discount vehicles — if the only pitch is "save money," the practice margins suffer and clients who primarily value cost will still price-shop.
- Launch a wellness plan without a PIMS workflow to track enrollment, utilization, and lapse — manual tracking does not scale.
- Offer plans that include unlimited office visits — open-ended inclusions are margin destroyers and attract the wrong utilization behavior.

## Edge cases / when the rule does NOT apply

Specialty-only and emergency-only practices typically do not offer wellness plans — their patient relationship is episodic by design. Mixed practices should offer plans for the general-practice side only.

## See also

- [`../agents/vet-finance-analyst.md`](../agents/vet-finance-analyst.md) — owns revenue analytics and the practice scorecard where plan enrollment rate belongs.
- [`./compliance-is-medicine-and-revenue-track-it.md`](./compliance-is-medicine-and-revenue-track-it.md) — wellness plans are a structural mechanism for improving compliance rates.

## Provenance

Standard veterinary practice management; grounded in Banfield Pet Hospital and VCA wellness plan models; wellness plan design principles from Nationwide (formerly VPI) and AVMA practice management resources; compliance improvement data from published veterinary practice plan-adoption studies.

---

_Last reviewed: 2026-06-05 by `claude`_
