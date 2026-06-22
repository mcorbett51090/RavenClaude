# Dispense from managed-care formularies knowingly

**Status:** Pattern
**Domain:** Optical / managed vision care
**Applies to:** `optometry-eyecare-practice`

> Advisory operations rule, not benefits advice. Plan allowances and formularies are payor-specific, volatile, and `[verify-at-use]`. No PII/PHI.

---

## Why this exists

Managed-vision-care plans cover specific materials up to specific allowances, with everything else an out-of-pocket upgrade. An optician who quotes **before** knowing the plan's covered formulary either price-shocks the patient (and loses the capture) or quotes wrong (and eats the difference). Knowing the formulary first lets the patient hear one honest number.

## How to apply

- Before quoting, identify what the patient's plan covers vs what is an upgrade (`[verify-at-use]` against the plan).
- Train formulary literacy into the dispensing workflow, not into a single optician's head.
- Present covered-baseline + clearly-labeled upgrades, so the choice is the patient's and the number is honest.

**Do:** check the plan, then quote.
**Don't:** quote a number and discover coverage after; assume one plan behaves like another.

## Edge cases / when the rule does NOT apply

Cash/private-pay patients have no formulary to read — quote the practice's own menu.

## See also

- [`./capture-rate-is-the-optical-profit-lever.md`](./capture-rate-is-the-optical-profit-lever.md)
- [`../skills/optical-capture-and-dispensary/SKILL.md`](../skills/optical-capture-and-dispensary/SKILL.md)

## Provenance

Codifies `optical-dispensary-manager` house opinion (#5). Plan/formulary specifics: [`../knowledge/eyecare-practice-reference-2026.md`](../knowledge/eyecare-practice-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-06-22 by `claude`_
