# Scope the MVP by the Learning Goal, Not by Feature Completeness

**Status:** Pattern
**Domain:** Product discovery / delivery
**Applies to:** `product-management`

---

## Why this exists

An MVP defined by "minimum features to be viable" tends to inflate toward the feature set the team originally planned, because every feature removed feels like a risk. An MVP defined by "minimum scope to test the riskiest assumption" is constrained by the learning goal, not by the feature backlog. The distinction matters because the first definition optimizes for "not embarrassing" while the second optimizes for "generates evidence cheaply." The most expensive MVP failure is a six-month build that confirms what a two-week smoke test would have revealed: the riskiest assumption was wrong, and the elaborate feature set is irrelevant.

## How to apply

Start the MVP scoping process by writing the learning goal and the minimum-evidence test before writing the feature list.

```
MVP Scoping — Learning-Goal-First Process
──────────────────────────────────────────────────────
Step 1 — NAME THE RISKIEST ASSUMPTION TO TEST
  (From the assumption map — the highest risk score)
  e.g., "Users in this segment struggle with the handoff step enough to pay or
         change their workflow for a solution"

Step 2 — DEFINE THE MINIMUM EVIDENCE THAT WOULD VALIDATE IT
  e.g., "5 out of 7 users in a structured prototype test complete the handoff
         step using our prototype AND express intent to use it over their
         current method"

Step 3 — CHOOSE THE CHEAPEST METHOD TO GENERATE THAT EVIDENCE
  Fake door / landing page → no engineering
  Wizard-of-Oz → manual back-end, product front-end
  Concierge → manual delivery of the service for a small group
  Prototype (clickable) → no production code
  Narrow slice → one flow end-to-end, not the full product

Step 4 — SCOPE THE MVP AS THAT METHOD ONLY
  The MVP contains exactly what Step 3 requires — not one feature more.
  Features needed for future scale are NOT in scope.
  Features for edge cases are NOT in scope.
  Features for polish are NOT in scope unless the riskiest assumption is about polish.

Step 5 — DEFINE THE DECISION GATE
  "If we see [evidence], we proceed to the next phase."
  "If we see [counter-evidence], we revisit the opportunity or pivot."
  Pre-commit in writing before the MVP ships.
```

**Do:**
- Write the decision gate before the MVP scope is finalized — the gate is what makes the learning usable.
- Be explicit about what the MVP does NOT test; scope exclusions are as important as inclusions.
- Communicate the learning goal and decision gate to the engineering team; they will make better trade-off decisions when they understand what the build is trying to prove.

**Don't:**
- Expand the MVP scope based on stakeholder requests unless those requests address the riskiest assumption.
- Treat a narrow MVP as a commitment to build only that — it is a learning instrument, not a product roadmap.
- Skip the decision gate; a shipped MVP without a decision gate produces observations without decisions.

## Edge cases / when the rule does NOT apply

- **Regulatory or compliance-driven deliverables** where the "minimum" is set by the regulation, not by a learning goal — scope is still appropriate to minimize, but the gate is "compliance confirmed," not a metric threshold.
- **Iterating on an existing, validated product feature** — the assumption has already been validated; the scoping discipline applies to new bets, not to incremental improvements on confirmed product-market fit.

## See also

- [`../agents/product-discovery-lead.md`](../agents/product-discovery-lead.md) — owns MVP framing and minimum-viable experiment design.
- [`./ship-to-learn.md`](./ship-to-learn.md) — the upstream house opinion; this doc operationalizes the scoping process that makes "ship to learn" concrete.

## Provenance

Codifies the product-discovery-lead's MVP scoping discipline from the product-management plugin's CLAUDE.md §2 #2 (discovery is continuous; test assumptions before building). The learning-goal-first scoping process reflects Eric Ries' Lean Startup methodology and Teresa Torres' minimum-viable experiment framing.

---

_Last reviewed: 2026-06-05 by `claude`_
