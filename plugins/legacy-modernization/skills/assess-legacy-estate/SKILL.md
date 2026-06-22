---
name: assess-legacy-estate
description: "Assess a legacy system and choose a modernization strategy with the 6 R's (retain/rehost/replatform/refactor/rearchitect/replace). Reach for this when the question is 'rewrite or refactor?' or 'is this worth modernizing?'."
---

# Skill: Assess the legacy estate

Decide *whether* and *how* to modernize before any code changes.

## Step 1 — Inventory the capability
List what the system does, its dependencies, runtime, data stores, and the team that owns it. Cite the pain it causes (incident load, lead time, change-failure rate) — don't assert it (§2 #7).

## Step 2 — Name the driver
The specific reason to change *this* now: scaling limit, change-failure rate, security/end-of-life, hiring drag, cost, or strategic pivot. **No driver → retain.**

## Step 3 — Pick the R (per capability)
Traverse the 6-R's tree in [`../../knowledge/legacy-modernization-decision-trees.md`](../../knowledge/legacy-modernization-decision-trees.md). Most estates are a *portfolio* of R's, decided capability by capability — not one verdict for the whole system.

## Step 4 — Make the carrying-cost case
Quantify the cost of *not* modernizing vs the cost/risk of doing it. Recommend only when the trade is favorable. Date and source every external figure.

## Step 5 — Sequence value-first
Order the work so increments ship early, the riskiest unknowns de-risk first, and rollback stays cheap. Capture it in the [`modernization-assessment`](../../templates/modernization-assessment.md) template.
