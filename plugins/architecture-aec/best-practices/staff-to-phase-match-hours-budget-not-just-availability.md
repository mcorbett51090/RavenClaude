# Staff to Phase: Match Hours Budget, Not Just Availability

**Status:** Pattern
**Domain:** Architecture/AEC
**Applies to:** `architecture-aec`

---

## Why this exists

Staffing a project with whoever is available rather than whoever fits the hours budget is how firms generate the overruns that kill net multiplier. A senior principal on production hours at a blended rate that doesn't match the phase fee loading turns a fee-adequate project into a loss. Conversely, an under-staffed project misses phase deadlines and generates client relationship risk. The discipline is to model each phase with a role/rate/hours budget before assigning people — then staff to match the budget, not the other way around.

## How to apply

Build a staffing model for each phase before the project kickoff:

```
Phase Staffing Model
──────────────────────
Project:   ________________
Phase:     ________________  Phase fee: $________

Role             | Rate ($/hr) | Budgeted hrs | Budgeted $ | Assigned staff
─────────────────|-------------|--------------|------------|────────────────
Principal-in-charge | ___  |     ___      |  $___      | ________________
Project manager  | ___         |     ___      |  $___      | ________________
Project architect| ___         |     ___      |  $___      | ________________
Technical staff  | ___         |     ___      |  $___      | ________________
Admin/coordination| ___        |     ___      |  $___      | ________________
─────────────────|-------------|--------------|------------|────────────────
Totals           |             |     ___      |  $___      |
Phase fee:       $______    Margin at budget:  $______   (%_____)
```

**Do:**
- Set the PIC role to a bounded number of hours — principal-level review and sign-off hours, not open-ended involvement.
- Flag any assignment where the billed rate multiplied by the budgeted hours produces a phase overspend before the project starts; renegotiate the fee or the scope before kickoff.
- Update the staffing model when an ASA adds scope — the additional fee funds additional hours, and the model must reflect both.

**Don't:**
- Staff by seniority when the phase budget requires production-rate hours — a principal-heavy staffing mix on a production phase destroys the multiplier.
- Assign staff without showing the role rate and budgeted hours to the PM — the PM cannot manage burn without knowing the plan.
- Use a prior project's staffing as a default; each phase has its own fee loading and required competencies.

## Edge cases / when the rule does NOT apply

Very small projects (under $20 k fee) with a single staff member may run a simplified version: budgeted total hours × rate vs. fee, rather than a multi-role model. The discipline of budget-before-assignment still applies.

## See also

- [`../agents/aec-project-analyst.md`](../agents/aec-project-analyst.md) — owns the staffing model and fee-burn tracking.
- [`./project-fee-burn-must-be-tracked-weekly-not-at-billing.md`](./project-fee-burn-must-be-tracked-weekly-not-at-billing.md) — the companion rule on tracking actual burn against the phase model.

## Provenance

Codifies CLAUDE.md §3 #4 (net multiplier and utilization are the firm's master numbers) at the project-staffing level. Role-to-budget matching is a standard AEC project management practice described in PSMJ, ZweigWhite, and AIA practice management frameworks [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
