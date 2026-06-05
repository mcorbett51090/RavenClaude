---
scenario_id: 2026-06-05-destroy-blast-radius-plan-review
contributed_at: 2026-06-05
plugin: terraform-iac
product: terraform
product_version: "unknown"
scope: likely-general
tags: [destroy, blast-radius, plan-review, state-isolation, lifecycle, prevent-destroy]
confidence: high
reviewed: false
---

## Problem

An engineer wanted to tear down an obsolete staging environment and ran `terraform destroy` in what they believed was the staging directory. Because the whole estate — network, data, and app — lived in **one monolithic state**, the destroy plan proposed deleting the shared VPC, a transit gateway used by *production*, and an RDS instance that staging and a nightly analytics job both depended on. The `-target` they reached for to "just destroy the app" wouldn't have helped: the dependency graph pulled in the shared resources anyway. One confirmation away from a multi-environment outage.

## Constraints context

- Single state for the entire estate (the anti-pattern the team had been meaning to fix) — so the destroy's blast radius was "everything," not "staging app."
- Shared resources (VPC, transit gateway, the RDS instance) were referenced by both staging and prod through the same state — there was no isolation boundary to stop a destroy at.
- The destroy was *intended* to be small (one obsolete env's app tier) but the state shape made it large.

## Attempts

- Tried: `terraform destroy -target=module.staging_app`. The plan still showed the shared VPC and RDS queued for deletion because targeted destroy follows dependencies; `-target` is an escape hatch, not a blast-radius fence. Outcome: rejected — `-target` masks the real problem (state shape) and HashiCorp documents it as exceptional-use-only.
- Tried: reading the **full destroy plan** before confirming (plan-is-the-review-artifact). Counted the resources: the plan touched prod-shared infrastructure. Outcome: the review caught it; the destroy was **not** confirmed.
- Tried (the move that worked): treated the destroy as blocked-by-design and fixed the cause. Split state by blast radius — a `network` state (shared, `prevent_destroy` on the VPC/TGW), a `data` state (RDS, `prevent_destroy` + deletion protection), and per-environment `app` states. Once staging-app was its own state with no shared resources in it, `terraform destroy` in that directory had a blast radius of exactly the staging app. Outcome: the obsolete env came down safely; a future fat-finger can't reach prod because the resources aren't in the same state.

## Resolution

**Blast radius is a property of state shape, not of the command you type.** `-target` does not bound a destroy — it follows the dependency graph and is an exceptional-use flag, not a safety fence. The real fix is **isolate state by blast radius** (CLAUDE.md §2 #2) so a destroy *can't* reach across the boundary, plus `lifecycle { prevent_destroy = true }` on the irreplaceable stateful resources as a second line of defense. Always read the **full** destroy plan and count what it touches before confirming.

**Action for the next engineer:** before any `destroy`, read the entire plan and ask "what is the blast radius of *this state*?" If the plan touches resources outside the thing you meant to delete, the state is too coarse — stop, and isolate before you destroy. `destroy` is **high-blast and irreversible**; it routes to operator review (Capability Grounding Protocol) and never auto-resolves. Put `prevent_destroy` on stateful/shared resources so even a wrong destroy errors out instead of executing.

Cross-reference: [`../best-practices/isolate-state-by-blast-radius.md`](../best-practices/isolate-state-by-blast-radius.md), [`../best-practices/lifecycle-prevent-destroy-for-stateful.md`](../best-practices/lifecycle-prevent-destroy-for-stateful.md), [`../best-practices/plan-is-the-review-artifact.md`](../best-practices/plan-is-the-review-artifact.md), and the "How to isolate state" tree in [`../knowledge/terraform-iac-decision-trees.md`](../knowledge/terraform-iac-decision-trees.md).
