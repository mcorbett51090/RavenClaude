---
description: Design a CAF-aligned Azure landing zone — flat management-group hierarchy, subscription vending that stamps RBAC/budget/policy/network at birth, allowed-SKU/location guardrails, and tag/naming to the CAF standard.
argument-hint: "[the estate, e.g. 'multi-team prod + nonprod under one tenant']"
---

# Design an Azure landing zone

You are running `/azure-cloud:design-landing-zone`. Lay out the platform foundation for the estate the user described (`$ARGUMENTS`) following this plugin's `azure-architect` discipline — governance that arrives *at creation*, before any workload, not bolted on after the first incident.

## When to use this

Standing up a new Azure estate, or reviewing a foundation before it scales to many subscriptions. For a single-subscription/sandbox estate the full vending machinery is overkill — say so and recommend the lighter shape. This is the foundation; the per-resource IaC is `scaffold-bicep-module`.

## Steps

1. **Flat management-group hierarchy** (`lz-flat-management-group-hierarchy`): 3–4 levels of archetype MGs (platform / landing zones / sandbox / decommissioned), not a deep tree mirroring the org chart — policy inherits down the archetypes.
2. **Vend subscriptions, don't hand-create them** (`lz-subscription-vending-not-manual-creation`): use the AVM `ptn/lz/sub-vending` module so each subscription is born placed under the right archetype MG with RBAC + budget + tags + baseline network + hub peering stamped atomically. The platform team owns the module; app teams submit a parameterized request.
3. **Cost + governance guardrails at creation** (`cost-budgets-tags-and-policy-guardrails`): a per-subscription budget (actual + forecasted alert thresholds), enforced `owner`/`cost-center`/`environment`/`application` tags via an `Append`/`Modify`/deny-untagged policy, and allowed-SKU/location policy — preventative controls, not a monthly retrospective.
4. **Policy as guardrails, not gates** (`gov-azure-policy-as-guardrails`): assign initiatives at MG scope (deny the unsafe, `DeployIfNotExists` the required) including the diagnostic-settings DINE so coverage doesn't depend on each author (`ops-diagnostic-settings-to-log-analytics-from-day-one`).
5. **Tag + name to the CAF standard** (`lz-tag-and-name-to-the-caf-standard`): `abbr-workload-env-region-instance` naming and the four required tags, applied uniformly so resources are attributable for chargeback.
6. **Compose the foundation from AVM** (`iac-compose-from-azure-verified-modules`): the ALZ-accelerator + vending AVM modules, pinned, rather than re-implementing the MG tree by hand.

## Guardrails

- Never recommend creating subscriptions by hand in the portal — that's where the forgotten budget / unplaced MG / missing RBAC lives.
- Workloads-before-a-landing-zone and deep org-chart MG hierarchies are the two named anti-patterns — flag them.
- This is an advisory design: emit the MG/subscription plan + Policy JSON + vending parameters the engineer runs; you don't provision against their tenant.
- The RBAC/PIM and network-security posture routes to `ravenclaude-core/security-reviewer`; whole-system cross-domain architecture routes to `ravenclaude-core/architect`.
