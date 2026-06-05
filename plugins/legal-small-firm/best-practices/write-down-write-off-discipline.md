# Distinguish Write-Downs from Write-Offs and Track Both Separately

**Status:** Absolute rule
**Domain:** Small-firm legal practice
**Applies to:** `legal-small-firm`

---

## Why this exists

A write-down (reducing a billed amount before it goes to A/R) and a write-off (removing an A/R balance that never collected) are economically identical in their impact on realization but occur at different points in the billing cycle and demand different remedies. Lumping them into a single "adjustment" line hides whether the problem is pricing-at-billing or A/R collection failure. A practice that writes down heavily at billing has a scope or billing-judgment problem; one that writes off heavily at collection has a client-selection or engagement-terms problem.

## How to apply

Track and report three distinct rows in every practice P&L review:

```
Billed hours (standard-rate value)           $  X
  Less: write-downs at billing               $ (D)   ← billing-judgment / scope issue
A/R balance carried forward                  $  W
  Less: write-offs from A/R                  $ (O)   ← collection / client-fit issue
Collected revenue                            $  C

Billed realization   = (X − D) / X
Collected realization = C / X
```

**Do:**
- Break the realization waterfall into two stages: billed realization and collected realization.
- Document the reason code for each write-down (scope ambiguity, write-down-to-agreed-flat, client dispute) and each write-off (uncollectible A/R, settlement, write-off policy).
- Review the write-down rate by matter type quarterly — a pattern in a single segment signals a fee-structure or scoping problem, not just a one-off.

**Don't:**
- Net write-downs and write-offs into a single "adjustments" line.
- Accept a blended "realization rate" figure without confirming which stage it covers.
- Treat write-offs as inevitable overhead rather than tracing them to the intake or engagement-terms decision.

## Edge cases / when the rule does NOT apply

If the practice is flat-fee only and there are no hourly billings, there are no write-downs in the traditional sense. Track discount-from-quoted-flat-fee as the analog.

## See also

- [`../agents/legal-operations-analyst.md`](../agents/legal-operations-analyst.md) — owns the realization waterfall and the A/R aging analysis.
- [`./realization-waterfall-reporting.md`](./realization-waterfall-reporting.md) — the companion rule on structuring the full realization report.

## Provenance

Codifies the `legal-operations-analyst`'s opinion in CLAUDE.md §3 #1 and §3 #7 — realization is the master number, and collections are part of the matter, not after it. Standard practice-management accounting (Thomson Reuters, Law360 benchmarking surveys) distinguishes the two stages; they are not interchangeable.

---

_Last reviewed: 2026-06-05 by `claude`_
