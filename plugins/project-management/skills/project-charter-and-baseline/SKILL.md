---
name: project-charter-and-baseline
description: Stand up the predictive plan of record — a project charter (objective, success criteria, sponsor, high-level scope, assumptions/constraints), a scope statement + WBS decomposed to single-owner work packages, and the scope/schedule/cost baseline that change control is measured against. Reach for this at project initiation, a reset, or before any earned-value reporting. Used by `delivery-lead` (primary).
---

# Skill: project-charter-and-baseline

**Purpose:** Produce the defensible baseline a predictive project is measured against — charter first, then scope + WBS, then the baseline. Used by `delivery-lead`.

## When to use

- Project initiation (before any schedule exists).
- A reset / re-baseline after a major change.
- Before the first earned-value status (you can't measure against a baseline you don't have).

## The procedure

1. **Charter before plan.** Capture: the **objective**, **measurable success criteria**, the **sponsor** (one named person), **high-level scope** (in / out), and the **assumptions + constraints**. No schedule until this is agreed — a Gantt without a charter is a guess with a date.
2. **Scope statement → WBS.** Decompose the in-scope work to the **work-package** level. Each package: a deliverable, a **single named owner**, and an estimate basis. Deliverable-oriented, not activity-soup.
3. **Estimate + sequence.** Size each package (state the basis — analogous / parametric / three-point), identify dependencies, and find the **critical path** (name the path + its float — a slip there costs the project, not a buffer).
4. **Baseline.** Lock scope + schedule + cost as the baseline of record. From here, every change is a change request with an impact analysis (see the change-request template), not a silent edit.
5. **Choose predictive deliberately.** If the work is high-uncertainty / discovery-heavy, say so and route to the agile track (the delivery-approach decision tree) rather than forcing a baseline onto chaos.

## Anti-patterns this skill prevents

- A schedule with no charter / agreed success criteria behind it.
- WBS items owned by "the team"; packages with no estimate basis.
- A baseline you never actually locked (so "change" means nothing).
- A predictive plan forced onto genuinely exploratory work (should be agile/hybrid).

## Output

A charter + scope/WBS + baseline (see [`../../templates/project-charter.md`](../../templates/project-charter.md)). Changes thereafter route through [`../../templates/change-request.md`](../../templates/change-request.md). End with the `delivery-lead` Output Contract block; hand risk-register population to `risk-and-raid-analyst` and stakeholder packaging to `stakeholder-comms-lead`.
