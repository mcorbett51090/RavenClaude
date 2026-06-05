# Control Plan Owner Must Be a Named Person, Not a Role

**Status:** Absolute rule
**Domain:** Process Improvement — Control phase
**Applies to:** `process-improvement`

---

## Why this exists

A control plan that lists "Process Owner" or "Quality Manager" as the responsible party is an orphan the moment the current holder of that title changes jobs. Sustainment requires a *named individual* who accepts the obligation, understands the reaction plan, and has the authority to act on an out-of-control signal. This is the single most common reason gains regress: the improvement was real, the control plan was written, but when the named role changed hands no one transmitted ownership of the plan.

## How to apply

**Control plan ownership block (required in every control plan):**

```
Control Plan Owner (named): [First Last]
Title / role:               [current title — for traceability, not as the identifier]
Date accepted:              [YYYY-MM-DD]
Review cadence:             [monthly / quarterly — when the owner reviews the control chart and reaction plan]
Escalation contact:         [First Last — who the owner pages when an OOC signal triggers]
Succession note:            On role change, this plan transfers to [role] — current holder must brief the successor before departure.
```

**What the named owner is responsible for:**
1. Monitoring the control chart at the stated review cadence.
2. Acting on the reaction plan when a Western Electric / Nelson out-of-control rule fires.
3. Keeping the standard work current when the process changes.
4. Transferring ownership at role change.

**Do:**
- Get a written acknowledgment from the named owner before the project closes.
- Include the control plan review as a recurring calendar event, not a "check in when you remember."
- Build the succession note into the onboarding checklist for the role.

**Don't:**
- List a team, department, or role as the owner.
- Close the DMAIC project before a named owner has accepted the plan in writing.
- Treat the control plan as a document deliverable rather than a live operating procedure.

## Edge cases / when the rule does NOT apply

- **Automated process controls** (a statistical alert built into a monitoring system that auto-escalates): the named owner is the person who receives the alert and acts on it — the automation does not eliminate human ownership of the reaction.
- **Kaizen improvements in a team environment** where work rotates: name the team lead as owner; the standard work document replaces the individual memory.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — writes the control plan in the Control phase
- [`./a-fix-without-a-control-plan-didnt-happen.md`](./a-fix-without-a-control-plan-didnt-happen.md) — the parent rule requiring a control plan at all

## Provenance

Codifies the project-management seam between `process-improvement` and `project-management` (CLAUDE.md §2 routing): the project-management `commitments-have-one-owner-and-one-date` rule applied to the Control phase artifact. Standard practice: ASQ Control Plan template requires a named control-plan owner. _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
