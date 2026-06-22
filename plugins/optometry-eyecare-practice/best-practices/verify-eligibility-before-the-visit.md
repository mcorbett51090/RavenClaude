# Verify eligibility before the visit

**Status:** Absolute rule
**Domain:** Billing / eligibility
**Applies to:** `optometry-eyecare-practice`

> Advisory operations rule, not billing advice. Payor eligibility rules are `[verify-at-use]`. No PII/PHI.

---

## Why this exists

The cheapest denial is the one prevented before the patient walks in. The single highest-yield fix for eye-care collection failures is knowing the benefit **at scheduling**, not discovering it at check-in or, worse, in a denial weeks later. Because an eye-care visit may route to medical *or* vision, both benefits must be checked.

## How to apply

- At scheduling, verify **both medical and vision benefits** — the visit may go either way.
- Confirm: active coverage, the plan on file, remaining materials allowance, and any frequency limits (`[verify-at-use]`).
- Re-confirm at check-in to catch plan changes since scheduling.
- Make eligibility a named step with a named owner in the front-desk workflow, not an ad-hoc check.

**Do:** treat eligibility as a pre-visit gate.
**Don't:** discover the benefit at checkout; assume last visit's plan still applies.

## Edge cases / when the rule does NOT apply

A same-day urgent medical visit may bypass the scheduling check — verify eligibility before claim submission instead, and document why.

## See also

- [`./route-the-claim-to-medical-or-vision-deliberately.md`](./route-the-claim-to-medical-or-vision-deliberately.md)
- [`../skills/eligibility-and-claims/SKILL.md`](../skills/eligibility-and-claims/SKILL.md)

## Provenance

Codifies `front-office-billing` house opinion (#2). Eligibility specifics: [`../knowledge/eyecare-practice-reference-2026.md`](../knowledge/eyecare-practice-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-06-22 by `claude`_
