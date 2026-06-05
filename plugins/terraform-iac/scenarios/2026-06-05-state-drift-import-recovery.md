---
scenario_id: 2026-06-05-state-drift-import-recovery
contributed_at: 2026-06-05
plugin: terraform-iac
product: terraform
product_version: "unknown"
scope: likely-general
tags: [drift, import, out-of-band, codify, plan-review, state]
confidence: high
reviewed: false
---

## Problem

A routine `terraform plan` on the networking stack showed 30+ resources queued for **replacement** — security-group rules, a NAT gateway, and route-table associations all marked `-/+`. Nobody had changed the Terraform code. During an incident the week before, an on-call engineer had hand-edited several SG rules in the cloud console to stop an outage, and a separate team had clicked "create" on a NAT gateway that Terraform now wanted to delete and recreate. A reflexive `apply` to "make the plan green" would have reverted the emergency fix and destroyed the out-of-band NAT gateway — re-breaking prod.

## Constraints context

- Production networking state — high blast radius; a wrong `apply` takes down the VPC's egress.
- Two distinct kinds of drift in one plan: (a) **managed** resources changed out-of-band (the SG rules Terraform already tracks), and (b) an **unmanaged** resource created out-of-band (the NAT gateway Terraform has never seen and wants to delete the *code's* version of).
- The hand-fix during the incident was **correct and load-bearing** — it could not simply be reverted.

## Attempts

- Tried: `terraform apply` to "resolve the diff." Caught in plan review before running — the diff was a *revert*, not a convergence. The plan-is-the-review-artifact rule (CLAUDE.md §2 #4) stopped it. Outcome: did not run; classified the drift first.
- Tried: classifying every drifted resource through the drift decision tree (`knowledge/terraform-iac-decision-trees.md` → "Drift found — codify, import, or revert?"). Split the 30 resources into: managed-and-intentional (the SG rules) → **codify**; unmanaged-and-intentional (the NAT gateway) → **import + write config**; and one genuinely-accidental tag change → **revert**. Outcome: a per-resource disposition instead of one blanket apply.
- Tried (the move that worked): updated the HCL to match the emergency SG rules (codify), wrote matching config for the NAT gateway and `terraform import`ed it into state, then re-ran `plan` until the *only* remaining diff was the one accidental tag. Applied **just that**. Outcome: state and reality reconciled with zero destructive change; a follow-up `plan` showed 0 diff.

## Resolution

**A drift plan is a diagnosis, not a to-do list — classify before you converge.** The unit of work is the resource, not the plan: each drifted resource is independently *codify*, *import*, or *revert*, and you never run a blanket `apply` that mixes a revert of an emergency fix with a destroy of an out-of-band resource. `terraform import` brings the unmanaged NAT gateway under management without recreating it; codifying the SG rules makes the emergency fix the new source of truth; the single accidental change is the only thing reverted.

**Action for the next engineer:** when a no-code-change plan shows a large diff, **stop before `apply`**. For each resource ask the drift-tree's two questions — "was the real-world change intentional and correct?" and "is this resource managed by this state?" — and write a per-resource disposition (codify / import / revert) before touching state. Import is **state-mutating and high-blast**; review the import target and the resource address with the operator before running, and always `plan` after to confirm the import produced zero diff (a non-zero post-import diff means the written config doesn't match reality yet). State surgery routes through `iac-policy-and-state-engineer` and the Capability Grounding Protocol.

Cross-reference: [`../best-practices/never-edit-state-by-hand.md`](../best-practices/never-edit-state-by-hand.md), [`../best-practices/plan-is-the-review-artifact.md`](../best-practices/plan-is-the-review-artifact.md), [`../best-practices/detect-drift-on-a-cadence.md`](../best-practices/detect-drift-on-a-cadence.md). The per-cloud `import` block / resource-argument detail belongs to the relevant cloud plugin; this team owns the classify-then-reconcile discipline.
