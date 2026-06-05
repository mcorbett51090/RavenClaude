# Bid Alternates Are Scope Control, Not Value Engineering

**Status:** Pattern
**Domain:** Architecture & AEC — project delivery, fee management
**Applies to:** `architecture-aec`

---

## Why this exists

Bid alternates are frequently misused as a post-bid value-engineering backstop — "we'll add alternates in case we're over budget." That approach produces documents that are expensive to prepare, difficult to coordinate, and rarely executed as drawn. A properly structured alternate strategy sets the scope boundary before CDs begin: the base bid is complete and constructable on its own; each alternate is a clearly bounded add or deduct that the owner can exercise at bid time with no redesign. When alternates are added late or poorly scoped, they generate RFIs, coordination gaps between the alternate and the base, and change orders after award.

## How to apply

**Establish the alternate strategy at SD, not at 95% CDs:**

| Step | Owner | Timing |
|---|---|---|
| Identify candidate alternates (deducts and adds) | Architect + Owner | SD completion |
| Confirm each alternate is bounded and doesn't affect the base-bid critical path | Architect | DD completion |
| Assign each alternate a specification section and drawing tag | Project Architect | 50% CDs |
| Coordinate base-bid drawings against alternates at 95% CDs | Arch + Subs | 95% CDs |
| Issue bid form with alternates clearly numbered and described | Architect | Bid set |

**How to scope a clean alternate:**
```
Each alternate must:
- Have a complete scope statement in the bid form ("Alternate 1: Add standing-seam
  metal roof in lieu of base-bid TPO membrane; see drawings A-601, A-602, Spec 07 61 00")
- Be self-contained — base bid is complete and code-compliant without it
- Have no inter-alternate dependencies (Alternate 2 must not require Alternate 1)
- Carry its own spec sections — don't share sections with base-bid unless split is explicit
```

**At bid analysis:**
- Evaluate base bid first; confirm it is within budget before adding any alternates.
- Present the owner with a priority-ranked alternate list and the cost-to-add/deduct for each.
- Document the owner's acceptance/rejection of each alternate in writing before award.

**Do:**
- Treat deduct alternates as scope-reduction options priced against a fully documented base.
- Issue an alternate matrix to subs so every trade prices the same scope.
- Make alternate acceptance part of the owner sign-off at bid award.

**Don't:**
- Add alternates as a substitute for a thorough design-phase budget check.
- Use alternates to defer scope decisions the owner hasn't made ("TBD — alternate").
- Allow alternates to create drawing coordination conflicts with the base-bid set.

## Edge cases / when the rule does NOT apply

On negotiated GMP contracts, alternates are replaced by allowances and contingency drawdown within the GMP. The scoping discipline still applies — each allowance or scope item must be bounded — but the formal bid alternate structure isn't used.

## See also
- [`../agents/aec-project-analyst.md`](../agents/aec-project-analyst.md) — runs the phase-by-phase budget check that makes alternates unnecessary as a last-minute fix.
- [`../agents/construction-documents-specialist.md`](../agents/construction-documents-specialist.md) — coordinates the alternate scope across the drawing set.

## Provenance

Codifies standard procurement practice for design-bid-build delivery; reflects AIA A701 bid form conventions and CSI MasterFormat alternate-pricing discipline. [unverified — training knowledge]

---

_Last reviewed: 2026-06-05 by `claude`_
