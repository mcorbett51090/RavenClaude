# The Weekly Customer Touchpoint Is Infrastructure, Not an Event

**Status:** Pattern
**Domain:** Product discovery / continuous discovery
**Applies to:** `product-management`

---

## Why this exists

Discovery that happens in quarterly research sprints produces insights that are already stale by the time they reach the roadmap. Customer behavior, needs, and context change faster than quarterly cycles. Teams that treat customer interviews as an event — "we do research before we build" — build a single point-of-knowledge that decays. Teams that maintain a standing weekly touchpoint with customers (even just one interview per week) build a continuous prior that makes every product decision better-informed and reduces the probability that a six-month build is invalidated by a market shift. The weekly rhythm also keeps the team empathetic; a team that hasn't spoken to a customer in 90 days makes decisions based on institutional memory, not current reality.

## How to apply

Set up the weekly customer touchpoint as a recurring, scheduled program — not as an ad hoc research effort.

```
Weekly Discovery Infrastructure — Setup Checklist
──────────────────────────────────────────────────────
□ CUSTOMER PANEL
  Maintain a list of 20–30 customers or potential customers who have agreed
  to be contacted for research.
  Replenishment: recruit 2–3 new participants per month to offset churn from the panel.

□ SCHEDULING
  Set a standing 30-minute slot each week (same day / time).
  Use an automated scheduling tool (Calendly or equivalent) with a panel-specific link.
  One PM or discovery lead owns the slot; they may not cancel but may rotate the interviewer.

□ INTERVIEW FOCUS
  Each week's interview has a pre-stated focus question derived from the current
  highest-priority unknown in the opportunity-solution tree.
  Keep a running question backlog; pick the top question for the week's session.

□ SYNTHESIS
  After each interview: 5-minute voice or written note on key quotes and observations.
  Monthly: review the last 4–5 interview notes for pattern synthesis.
  Share synthesis in the weekly product review; don't hoard insights in a researcher silo.

□ ATTENDANCE
  Rotate engineering leads and designers through interview observations quarterly.
  A team that observes real users is harder to convince by internal authority alone.
```

**Do:**
- Protect the weekly slot as rigorously as a sprint ceremony; it is not optional when busy.
- Use the weekly touchpoint for discovery (problem and context understanding), not usability testing — keep the two separate.
- Keep the focus question connected to the opportunity-solution tree, not to the latest feature in development.

**Don't:**
- Run the weekly touchpoint as a feature feedback session ("here's what we're building, what do you think?") — this is a common drift that kills the discovery value of the practice.
- Skip weeks because "we have enough data" — the value is in the continuity, not in the individual sessions.
- Keep insights locked in a research repo that the team never reads; synthesis and sharing are mandatory steps, not optional documentation.

## Edge cases / when the rule does NOT apply

- **Pre-launch, no existing customers** — the panel is potential customers; recruit from the target segment, not from the internal network.
- **Very regulated products** where customer contact is legally constrained (e.g., certain financial services) — work with the compliance team to identify a legally permissible touchpoint format (e.g., research panels, user advisory boards).

## See also

- [`../agents/product-discovery-lead.md`](../agents/product-discovery-lead.md) — owns the continuous discovery program and the weekly touchpoint infrastructure.
- [`./discovery-is-continuous.md`](./discovery-is-continuous.md) — the upstream house opinion; this doc operationalizes the weekly rhythm that makes discovery continuous in practice.

## Provenance

Codifies the product-discovery-lead's continuous discovery discipline from the product-management plugin's CLAUDE.md §2 #2 (talk to customers every week, test assumptions before building). The weekly touchpoint infrastructure pattern is drawn from Teresa Torres' "Continuous Discovery Habits" framework and standard product management practice at product-led growth companies.

---

_Last reviewed: 2026-06-05 by `claude`_
