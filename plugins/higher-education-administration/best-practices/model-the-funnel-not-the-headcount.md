# Model the funnel, not the headcount

**Status:** Pattern
**Domain:** Enrollment management / funnel modeling
**Applies to:** `higher-education-administration`

> Advisory operations rule. Stage rates and benchmarks are institution-specific — `[verify-at-use]`. FERPA-aware: cohorts only, no student PII.

---

## Why this exists

"We need 1,200 first-years" is an *output*, not a plan. The output is produced by five inputs — inquiries, apply rate, admit rate, yield, and melt — and a headcount target tells you nothing about which of them is failing. Teams that manage to the headcount reach for the only lever they can see (buy more inquiries) even when the leak is three stages down at yield. Modeling the funnel turns a wish into a diagnosis: it shows the stage that actually moved and the cheapest lever to move it back.

## How to apply

- Decompose the target: class = inquiries × apply rate × admit rate × yield × (1 − melt).
- Compute each stage rate, attach its **definition** (`[verify-at-use]`), and compare to prior year to find the stage that moved.
- Target the **leaking stage** with its cheapest lever — don't default to the top of the funnel.
- Carry the model through to **net tuition revenue**, not just headcount, so a "bigger class" that loses money is visible.

**Do:** manage the stage rates; find and fix the actual leak.
**Don't:** manage to a headcount number and buy inquiries by reflex.

## Edge cases / when the rule does NOT apply

Very small programs with tiny cohorts can have stage rates too noisy to model precisely — use multi-year trends and treat single-cycle swings cautiously.

## See also

- [`../skills/enrollment-funnel-and-yield/SKILL.md`](../skills/enrollment-funnel-and-yield/SKILL.md)
- Template: [`../templates/enrollment-funnel-model.md`](../templates/enrollment-funnel-model.md)

## Provenance

Codifies `enrollment-management-strategist` and `higher-ed-administration-lead` house opinion and the funnel decision trees. Benchmarks: [`../knowledge/higher-ed-reference-2026.md`](../knowledge/higher-ed-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
