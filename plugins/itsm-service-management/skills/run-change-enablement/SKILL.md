---
name: run-change-enablement
description: "Classify a change (standard/normal/emergency), assess its risk, and route it — pre-authorizing repeatable changes and reserving the CAB for genuine risk. Reach for this on any 'does this need approval / a CAB?' question."
---

# Skill: Run change enablement

Maximize successful changes while controlling risk — not slow every change to a crawl (§2 #2).

## Step 1 — Classify the change type
- **Standard** — low-risk, repeatable, well-understood → pre-authorized via a model, **no CAB**.
- **Normal** — needs assessment; higher-risk ones go to the **CAB**.
- **Emergency** — urgent (e.g. fixing a major incident) → expedited path (ECAB), with retrospective review.

Traverse the change-type tree in [`../../knowledge/itsm-decision-trees.md`](../../knowledge/itsm-decision-trees.md).

## Step 2 — Assess risk
Impact × likelihood × reversibility. A reversible, low-blast change needs little ceremony; an irreversible, high-blast one needs more. Set the approval level to match the risk, not to a fixed gate.

## Step 3 — Pre-authorize the repeatable
If this change recurs and is low-risk, build a **standard-change model** so it ships without a CAB meeting (§2 #3). This is the main lever for de-bottlenecking change.

## Step 4 — Build the RFC (normal change)
Document the change, risk, rollback, and schedule in the [`change-request-rfc`](../../templates/change-request-rfc.md). Take genuinely novel/higher-risk normal changes to the CAB.

## Step 5 — Coordinate the release
Coordinate scope, timing, and rollback; hand the deployment *automation* to `devops-cicd`. A failed change that causes an outage routes to the incident-and-problem-manager.
