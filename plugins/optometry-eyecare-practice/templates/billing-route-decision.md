# Billing Route Decision — <visit type / scenario>

> Output template for the medical-vs-vision-plan routing decision. One per ambiguous visit *type* or policy (not per patient). **Advisory, not billing advice.** Every code/payor rule is `[verify-at-use]`. No PII/PHI — describe the scenario in general terms, never a patient record.

## Scenario
- **Visit type / chief complaint pattern:** _____
- **Prepared:** 2026-__-__

## The route
- **Decision:** ☐ Vision plan  ☐ Medical insurance  ☐ Split (both)
- **Decided on:** _the chief complaint and what the visit addressed_
- **If split:** _medical component vs vision component — and confirm the payor allows a split_ `[verify-at-use]`

## Basis
- **Chief complaint / reason for visit:** _____
- **What the visit addressed:** _____
- **Why this route (not the other):** _____

## Documentation & coding
- **Coding family (verify-at-use):** _____
- **Medical-necessity documentation present?** ☐ yes ☐ no (if medical and no → fix the record or route to vision)
- **Source/payor rule consulted:** _<source placeholder>_ — retrieved 2026-__-__ `[verify-at-use]`

## Eligibility
- **Medical benefit verified:** ☐  · **Vision benefit verified:** ☐  · **When:** _at scheduling / check-in_

## Verify-at-use flags
- _List every CPT code, payor rule, and benefit detail relied on — each must be re-confirmed against the payor before it drives a claim._

---
_Plus the ravenclaude-core Structured Output block._
