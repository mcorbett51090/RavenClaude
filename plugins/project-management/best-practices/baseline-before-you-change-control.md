# Baseline first, then change-control every scope/schedule/cost change

**Status:** Absolute rule (predictive track) — once a project is baselined, a change to scope, schedule, or cost is a **change request** with an impact analysis, not a silent edit. A change absorbed without that analysis is a defect.

**Domain:** Project management

**Applies to:** `project-management`

---

## Why this exists

The whole point of a baseline is to make change *visible and measurable*. When teams quietly absorb "small" scope additions, the baseline stops meaning anything: schedule slips with no traceable cause, the sponsor is surprised at the end, and earned-value status reads green while the project drifts. Integrated change control is the mechanism that keeps the plan-of-record honest. (On the agile track the equivalent discipline is re-prioritizing the backlog *visibly* each cycle — see the edge cases.)

## How to apply

1. **Baseline before you measure against it.** No change control until scope (scope statement + WBS), schedule, and cost are agreed and baselined. Pre-baseline, you're still planning.
2. **Every change is a request with an impact analysis** against the baseline: what scope moves, the schedule delta (incl. critical-path effect), the cost delta, and the options.
3. **An explicit disposition:** approve (and re-baseline), defer, or reject — with a named approver. "We just did it" is not a disposition.
4. **Re-baseline on approval.** An approved change updates the baseline so future status measures against the new plan; the change log preserves the history.
5. **No assessment, no absorb.** A scope change with no schedule/cost impact assessment does not enter the plan — surface it as a pending change request instead.

**Do:** baseline first; raise every scope/schedule/cost change as a request with impact + options + a named disposition; re-baseline on approval and keep the change log.

**Don't:** absorb "small" scope silently; report green while un-controlled changes accumulate; change the baseline without an approval trail.

## Edge cases / when the rule does NOT apply

On a **pure agile** project there is no fixed scope baseline to change-control — the discipline shifts to *visible* backlog re-prioritization each sprint (the change is still explicit, just managed empirically rather than against a frozen baseline). On a **hybrid (fixed wrapper)** project, change-control applies at the outer-baseline/milestone level while the interior flexes — reconcile the burn-up against the baseline each cycle. Genuine error corrections (fixing a defect within agreed scope) are not scope changes. Specific change-control thresholds and approval authorities are engagement-/governance-specific — confirm them against the actual project governance.

## See also

- [`../knowledge/pm-decision-trees.md`](../knowledge/pm-decision-trees.md) — the predictive and hybrid leaves where this rule binds.
- [`./commitments-have-one-owner-and-one-date.md`](./commitments-have-one-owner-and-one-date.md) — every change request has a named approver + date.
- [`../agents/delivery-lead.md`](../agents/delivery-lead.md) — owns the baseline + change control.
- PMBOK 7 — integrated change control (domain-standard framing).

## Provenance

Authored with the `project-management` plugin (2026-06-01). Grounded in the PMBOK integrated-change-control discipline; the agile carve-out is stated so the rule isn't misapplied to a backlog.

---

_Last reviewed: 2026-06-01 by `claude`_
