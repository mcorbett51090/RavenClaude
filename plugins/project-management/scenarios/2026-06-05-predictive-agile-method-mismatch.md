---
scenario_id: 2026-06-05-predictive-agile-method-mismatch
contributed_at: 2026-06-05
plugin: project-management
product: delivery-hybrid
product_version: "n/a"
scope: likely-general
tags: [delivery-approach, hybrid, agile, predictive, requirements-stability, tailoring]
confidence: medium
reviewed: false
---

## Problem

A team "ran agile" — two-week sprints, a board, stand-ups — on a project that had a **contractually fixed scope and a fixed go-live date** tied to a regulatory deadline. Every sprint review, the sponsor asked "are we going to make the date?" and got "velocity is trending up", which answered a different question. Conversely, an earlier project in the same org had run a full predictive Gantt over genuinely exploratory R&D work and re-baselined it four times in three months. The ask: the org's default was "we're an agile shop" (or, on the older team, "we Gantt everything") and both defaults were misfiring. How do we pick the approach from the work, not the habit?

## Context

- Track: the live project was nominally agile but sat under a fixed-scope, fixed-date, regulator-driven contract — the classic "fixed wrapper, uncertain interior" shape.
- Constraint: pure open-ended sprints gave the team good empirical feedback but **no answer to the fixed-date question** the contract demanded; there was no outer baseline to burn up against. The older R&D project had the opposite failure — a frozen Gantt manufacturing false precision over discovery work.
- The org culture treated methodology as identity ("we're agile") rather than as a tailoring choice.

## Attempts

- Tried: traversed the **Delivery-approach decision tree** in [`../knowledge/pm-decision-trees.md`](../knowledge/pm-decision-trees.md) against the *observable* inputs (requirement stability, contract shape, discovery level) rather than the org's self-label. The live project resolved to **HYBRID (fixed wrapper, uncertain interior)**: hold a predictive outer baseline + change control for the regulatory commitment, run agile increments inside, and reconcile burn-up vs baseline every cycle. Outcome: named the actual shape instead of the habitual one.
- Tried: for the older R&D case, the same tree resolved to **AGILE** — evolving requirements with flex on scope/date — confirming the four re-baselines were the *predictive frame fighting the work*, not a planning failure. Outcome: validated that the mismatch, not the team, had caused the churn.
- Tried (the move that worked): on the live project, stood up a thin outer milestone baseline (the `delivery-lead`) over the existing sprint cadence (the `scrum-master`), and changed the sprint-review answer from "velocity is up" to "burn-up vs the fixed-date baseline says we're tracking / at-risk." Outcome: the sponsor's fixed-date question finally got a fixed-date answer, while the team kept its empirical cadence inside.

## Resolution

Neither "we're agile" nor "we Gantt everything" is a delivery approach — they're habits. The work's **requirement stability + contract shape** picks the approach: a fixed-scope/fixed-date regulatory wrapper over an uncertain interior is a *hybrid*, and running it as pure agile left the fixed commitment unanswered; genuinely exploratory R&D is *agile*, and a frozen Gantt over it manufactures churn.

**Action for the next PM hitting this pattern:** when an org says "we're an agile shop" (or "we plan everything up front"), **don't take the label as the approach** — traverse the delivery-approach tree against the work's observable requirement-stability and contract shape. A fixed wrapper over an uncertain interior is a hybrid: keep a predictive outer baseline for the commitment and run agile inside, reconciling each cycle. Methodology is a means, tailored to the engagement (CLAUDE.md house opinion #9), not an identity.

**Sources for framings cited:** the predictive/agile/hybrid distinction and tailoring are standard PMBOK 7 (development-approach + tailoring) and Scrum Guide framings, used as domain-standard definitions (not engagement advice) — web-verified 2026-06-05 against the Delivery-approach tree's own `Last verified` note. No external numbers are load-bearing in this scenario; confirm the actual contract/governance before committing an approach.
