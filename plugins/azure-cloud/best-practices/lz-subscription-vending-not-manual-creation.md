# Vend subscriptions, don't hand-create them — stamp policy + RBAC + budget + network at birth

**Status:** Pattern — strong default for any multi-subscription estate; a hand-clicked subscription with bolt-on governance needs a written reason.

**Domain:** Landing Zones / Governance

**Applies to:** `azure-cloud`

---

## Why this exists

When subscriptions are created by hand in the portal, governance arrives *late and unevenly* — someone deploys workloads, and only afterward does anyone remember to place it under the right MG, assign RBAC, attach a budget, wire diagnostic settings, and peer the network. Each manually-created subscription is a chance to forget one of those, and forgotten governance is exactly where incidents hide. **Subscription vending** inverts the order: a repeatable IaC module (AVM ships **subscription-vending** modules for both Bicep and Terraform) creates the subscription **and** places it under the correct archetype MG **and** stamps RBAC, budget, tags, policy inheritance, and baseline networking — all at creation, atomically. The platform team owns the vending module; application teams *request* a subscription and get a fully-governed one back. This is the operational complement to the flat-MG-hierarchy + policy-guardrail rules: those define *what* governance applies, vending guarantees it's applied *from the first second*.

## How to apply

Use the AVM subscription-vending module to create + govern the subscription in one deployment. Application teams parameterize their request; the module does placement, RBAC, budget, and network wiring.

```bicep
// Platform team's vending module call — subscription is born governed
module vend 'br/public:avm/ptn/lz/sub-vending:0.x.y' = {
  name: 'vend-payments-prod'
  params: {
    subscriptionAliasName: 'sub-payments-prod'
    subscriptionBillingScope: billingScope
    subscriptionManagementGroupId: 'corp'        // placed under the right archetype at birth
    subscriptionTags: { owner: 'team-payments', 'cost-center': 'CC-4187', environment: 'prod' }
    // + role assignments, budget, virtual-network + hub peering parameters
    roleAssignmentEnabled: true
    virtualNetworkEnabled: true
    virtualNetworkPeeringEnabled: true           // spoke peered to the hub on creation
  }
}
```

**Do:**
- Create subscriptions through a **vending module** (AVM `ptn/lz/sub-vending`), not the portal — placement + RBAC + budget + tags + network in one deploy.
- Place each new subscription under the **correct archetype MG** at creation so it inherits policy immediately.
- Let the **platform team own** the vending module; application teams submit a parameterized request.
- Stamp **budget + diagnostic settings + baseline network** as part of the vend (composes with the budget/diagnostics/policy rules).

**Don't:**
- Hand-create subscriptions and bolt governance on afterward — that's where the forgotten budget / unplaced MG / missing RBAC lives.
- Let application teams create their own subscriptions outside the vending path (require authorization on the MG hierarchy so they can't).
- Re-implement the management-group + vending plumbing by hand when the AVM ALZ-accelerator + vending modules exist.

## Edge cases / when the rule does NOT apply

- **A single-subscription estate** doesn't need vending machinery — the rule earns its keep at multi-subscription scale.
- **The very first platform subscriptions** (connectivity/identity/management) are often bootstrapped by the ALZ accelerator before a vending module exists — that's the foundation, not an exception to it.
- **Sandbox** subscriptions vend under the loose-policy archetype with relaxed guardrails (but still a budget).
- A **legacy estate mid-migration** may hold hand-created subscriptions — each is a tracked migration item onto the vending path, not a permanent exemption.

## See also

- [`./lz-flat-management-group-hierarchy.md`](./lz-flat-management-group-hierarchy.md) — the archetype MGs vending places subscriptions under
- [`./cost-budgets-tags-and-policy-guardrails.md`](./cost-budgets-tags-and-policy-guardrails.md) — the budget/tag/policy the vend stamps
- [`./iac-compose-from-azure-verified-modules.md`](./iac-compose-from-azure-verified-modules.md) — the AVM vending + ALZ-accelerator modules
- [`../knowledge/azure-landing-zones-and-governance.md`](../knowledge/azure-landing-zones-and-governance.md) — subscription vending in the CAF shape
- [`../agents/azure-architect.md`](../agents/azure-architect.md) · [`../agents/bicep-iac-engineer.md`](../agents/bicep-iac-engineer.md)

## Provenance

Codifies house opinion #1 (landing-zone-first; subscription-per-environment via vending) from [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in [`../knowledge/azure-landing-zones-and-governance.md`](../knowledge/azure-landing-zones-and-governance.md) (subscription vending stamps policy + RBAC + budgets at creation; AVM ships vending modules for Bicep + Terraform — Microsoft Learn CAF, retrieved 2026-05-28; AVM `ptn/lz/sub-vending` module conventions re-confirmed 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
