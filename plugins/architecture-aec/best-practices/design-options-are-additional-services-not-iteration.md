# Design Options Are Additional Services, Not Iteration

**Status:** Pattern
**Domain:** Architecture/AEC
**Applies to:** `architecture-aec`

---

## Why this exists

"Can you show us two more options?" is the most common scope-creep trigger in design. The client experiences it as a reasonable request; the architect experiences it as burning hours against a fixed fee. The distinction that protects the fee is between refining the agreed design direction (in-scope iteration) and developing an alternative concept the client might choose instead (an additional service). Without this distinction in writing, the architect is effectively doing speculative design on the client's behalf for free.

## How to apply

Define iteration vs. option in the engagement letter, and track each design-option request against the definition:

```
Design Option Policy (for inclusion in engagement letters)
───────────────────────────────────────────────────────────
Basic Services include [X] design concepts at SD and [Y] rounds of refinement
per phase following owner direction. Additional design concepts, studies, or
options developed at the owner's direction after the initial concept presentation
are additional services billed at the hourly rate in Exhibit A.

Tracking log:
  | Date | Description | Type (iteration / option) | ASA issued? | Hours |
  |------|-------------|--------------------------|-------------|-------|
```

The working rule:
- **Iteration:** refining the selected direction in response to owner feedback → in-scope.
- **Option:** developing an alternative concept for the owner to choose between → additional service.
- **Study:** analyzing a specific question at the owner's request (massing, structural alternative, cost scenario) → additional service unless explicitly included in the scope.

**Do:**
- State the number of included concepts and revision rounds in the engagement letter — a specific number converts an ambiguous scope into a clear threshold.
- Flag a request as an option rather than iteration at the moment it arrives, before starting work.
- Issue a brief scope memo when the boundary is ambiguous — "You've asked for a second scheme. We're treating this as an additional-services study at $X. Please confirm to proceed."

**Don't:**
- Accept "just sketch out one more idea" without documenting it — quick sketches that lead nowhere still consume hours.
- Let a pattern of option requests accumulate without issuing ASAs; the conversation gets harder with each deferred authorization.
- Retroactively reclassify completed work as options to generate an invoice; the reclassification must happen prospectively.

## Edge cases / when the rule does NOT apply

Design competitions, developer feasibility studies, and concept-phase engagements explicitly contracted for multiple options are scoped as option-development work from the start; the iteration/option distinction applies to the post-concept development phases.

## See also

- [`../agents/design-architect.md`](../agents/design-architect.md) — owns design-phase scope management and iteration tracking.
- [`./additional-services-authorization-before-work-not-after.md`](./additional-services-authorization-before-work-not-after.md) — the downstream rule on authorizing any additional service before beginning work.

## Provenance

Codifies CLAUDE.md §3 #2 (scope creep is the margin killer — control additional services) applied specifically to the design-option failure mode. The iteration/option distinction is a practical AEC project-management discipline that is not widely codified in AIA forms but is standard in firm-level scope management practice [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
