---
scenario_id: 2026-06-05-workloads-before-landing-zone-retrofit
contributed_at: 2026-06-05
plugin: azure-cloud
product: landing-zone
product_version: "n/a"
scope: likely-general
tags: [landing-zone, caf, management-group, subscription-vending, governance, retrofit]
confidence: medium
reviewed: false
---

## Problem

A company had run on Azure for two years with **everything in one subscription directly under the tenant root** — prod, dev, and a couple of client demos all mixed, no management-group structure, no Azure Policy, ad-hoc naming, and no cost separation. They wanted to "do landing zones properly," and the proposed plan was to **build a deep management-group hierarchy mirroring the org chart and migrate everything into it over a weekend.** Both halves of that plan were wrong.

## Constraints context

- Segment: services firm, single Entra tenant, ~1 large subscription, mixed prod/non-prod, growing toward needing per-client isolation.
- Resources **cannot move between regions**, and moving them between subscriptions/RGs is disruptive (resource-ID changes, RBAC re-grants, dependency breakage) — so a big-bang migration is high-blast and largely irreversible.
- A deep MG tree mirroring the org chart is a known CAF anti-pattern: it ossifies around a structure that reorgs, and policy inheritance becomes hard to reason about.
- This is foundation/governance work for `azure-architect` (+ `azure-ops-engineer` for the policy/cost guardrails); cross-domain whole-system calls escalate to `ravenclaude-core/architect`.

## Attempts

- Tried: the org-chart-shaped MG hierarchy. Rejected on the CAF guidance — **flat, 3–4 levels max, organized by archetype (platform / landing zones / sandbox / decommissioned), not by department.** Outcome: redesigned to the flat archetype shape.
- Tried: the weekend big-bang migration of all existing resources into new subscriptions. Rejected — too much irreversible blast radius for a live estate. Outcome: replaced with an incremental plan.
- Tried (the moves that worked):
  1. **Stood up the flat MG hierarchy first** (intermediate root → platform + landing-zones + sandbox + decommissioned) and applied **Azure Policy as audit-only first** (`Audit`/`AuditIfNotExists`), not `Deny` — so the existing estate's drift was *visible* before anything was enforced.
  2. **Vended new subscriptions** for net-new workloads via subscription-vending (one sub per workload-environment under the right archetype) — new work landed correctly without touching the legacy sub.
  3. **Tightened policy to `Deny` only after** the audit pass showed what would break, and remediated the legacy resources incrementally.
  4. Migrated the legacy subscription's contents **last and piecemeal** (prod-isolation first), accepting that some resources would be recreated rather than moved.
  Outcome: a CAF-aligned foundation, new workloads compliant from day one, and the legacy estate drained incrementally instead of in a risky big bang.

## Resolution

Two lessons. First, **landing-zone-first is about *new* work** — you don't have to (and shouldn't) big-bang-migrate a live estate into it; stand up the foundation, **vend** new subscriptions into it, and **drain the legacy estate incrementally**. Second, **the MG hierarchy is flat and archetype-shaped (3–4 levels), never the org chart** (house opinion #1). The sequencing that de-risks it: **Policy in audit/`AuditIfNotExists` mode first to surface drift, then `Deny` once you know what breaks.** See [`../knowledge/azure-landing-zones-and-governance.md`](../knowledge/azure-landing-zones-and-governance.md) and the best-practices `lz-flat-management-group-hierarchy.md` + `lz-subscription-vending-not-manual-creation.md`.

**Action for the next consultant hitting this pattern:** don't migrate first — build the flat archetype MG hierarchy, apply policy as **audit-only** to make existing drift visible, vend subscriptions for new workloads, then remediate + migrate the legacy estate incrementally (prod isolation first). Resist the org-chart MG tree. Big-bang subscription migration of a live estate is a high-blast, largely irreversible action — treat it as a deliberate, staged decision, never a weekend. CAF MG-depth guidance and AVM ALZ/vending module versions are volatile — `[verify-at-use]`.

**Sources (retrieved 2026-06-05):**
- CAF — management group hierarchy + Azure landing zone design areas — https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups
- Subscription vending — https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/subscription-vending
- Azure Policy effects (Audit / AuditIfNotExists / Deny) — https://learn.microsoft.com/azure/governance/policy/concepts/effect-basics

CAF guidance and the AVM ALZ accelerator/vending module versions change — `[verify-at-use]` before committing a topology.
