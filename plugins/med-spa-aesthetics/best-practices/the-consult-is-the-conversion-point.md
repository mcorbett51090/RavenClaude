# The consult is the conversion point

**Status:** Absolute rule
**Domain:** Patient flow / conversion
**Applies to:** `med-spa-aesthetics`

> Operations rule. No patient PHI/PII. Conversion benchmarks are `[verify-at-use]`. The provider owns the treatment plan; the coordinator operationalizes the path to book.

---

## Why this exists

In aesthetics, most of the revenue decision is made at the consult. A practice that draws plenty of consults but converts few is not a marketing problem — it's a conversion-at-the-consult problem, and spending on more leads only widens the leak. The consult is where clarity of the (provider-set) plan, transparent pricing, financing, and a same-day path to book turn interest into booked treatment.

## How to apply

- Instrument the funnel: inquiry → booked consult → showed → converted → rebooked-on-cadence. Fix the biggest drop first.
- Communicate the **provider's** recommended plan clearly; the coordinator never improvises a clinical recommendation.
- Make pricing transparent and offer a **same-day book-or-hold**, not a follow-up call later.
- Enroll membership at the moment of trust; hand the economics to `med-spa-operations-lead`.

**Do:** measure conversion past the booked consult; close the biggest leak; book same-day.
**Don't:** send consults home with "think about it and call us"; let the coordinator make a clinical or scope call.

## Edge cases / when the rule does NOT apply

A consult for a service the practice can't clinically or compliantly deliver should not be converted — route the scope question to `aesthetics-compliance-advisor` first.

## See also

- [`../skills/consult-to-treatment-conversion/SKILL.md`](../skills/consult-to-treatment-conversion/SKILL.md)
- [`rebook-on-the-treatment-cadence.md`](./rebook-on-the-treatment-cadence.md)

## Provenance

Codifies the `patient-coordinator-lead` house opinions and the conversion skill. Benchmarks: [`../knowledge/med-spa-reference-2026.md`](../knowledge/med-spa-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-04 by `claude`_
