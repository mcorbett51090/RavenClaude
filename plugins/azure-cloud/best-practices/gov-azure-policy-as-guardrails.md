# Use Azure Policy as guardrails — audit first, then deny; DeployIfNotExists to remediate

**Status:** Pattern — strong default for any governed estate; assign at MG scope, roll out audit→deny safely.

**Domain:** Governance

**Applies to:** `azure-cloud`

---

## Why this exists

Guardrails that live in people's heads (or a wiki) don't hold — the only governance that survives turnover and Cursor/Codex/portal edits is the kind the platform **enforces**. **Azure Policy** is that mechanism: assigned at **management-group scope** so every nested subscription inherits it (the flat-MG-hierarchy rule exists to make this clean), it can **`deny`** non-compliant creates (no public SQL, no untagged resource, no disallowed region/SKU), **`audit`** for visibility, or **`DeployIfNotExists`** to auto-remediate (deploy a diagnostic setting, enable Defender). House opinion #13 is "Defender for Cloud + Azure Policy on by default across all subscriptions." The load-bearing discipline is the **rollout order**: assign new `deny`/DINE policies in **`DoNotEnforce` / `audit` mode first**, watch what they *would* have blocked, then flip to `Default`/`deny` once you've confirmed they don't break legitimate deploys — Microsoft's documented safe-deployment practice. Policy is for **governing** workloads, **not** for deploying them.

## How to apply

Assign at the archetype/MG scope. Start in audit (`enforcementMode: DoNotEnforce` or `audit` effect), confirm the would-block set, then promote to `Default`/`deny`. Use `DeployIfNotExists` (with a managed identity) for remediation.

```bicep
// Guardrail assigned at the archetype MG — inherited by every nested subscription.
// Phase 1: DoNotEnforce (audit only). Phase 2: flip to Default once verified.
targetScope = 'managementGroup'
resource denyPublicPaaS 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'deny-public-paas'
  properties: {
    policyDefinitionId: tenantResourceId('Microsoft.Authorization/policySetDefinitions', '<initiative-id>')
    enforcementMode: 'DoNotEnforce'    // audit first; switch to 'Default' to enforce
  }
}
```

```text
# Safe rollout of a deny/DINE policy (Microsoft's documented practice):
#   1. Assign in audit / DoNotEnforce at a canary/sandbox scope
#   2. Review compliance: what WOULD have been denied/remediated?
#   3. Flip enforcementMode to Default (a.k.a. Enabled) on tier 0, then widen by region/tier
#   DINE/Modify assignments need a managed identity for remediation tasks.
```

**Do:**
- Assign policies/initiatives at **MG scope** so subscriptions inherit; keep **root-MG** assignments to the few truly universal ones.
- Roll out `deny`/`DeployIfNotExists` **audit-first** (`DoNotEnforce`), review the would-block set, then promote to `Default`.
- Use **`DeployIfNotExists`** (with a remediation managed identity) to auto-fix drift — diagnostic settings, Defender enablement, required configs.
- Pair policy with **Defender for Cloud** on by default (house opinion #13).

**Don't:**
- Flip a brand-new `deny` straight to enforced across prod — you'll block legitimate deploys; audit first.
- Use Azure Policy to **deploy whole workloads** — it governs and remediates; use Bicep/Terraform/portal to deploy (Microsoft is explicit on this).
- Pile policies onto the **root MG** — over-broad root assignments are the hardest to debug.

## Edge cases / when the rule does NOT apply

- **Regulatory environments** may legitimately stay in **audit-only** (phase 1) forever and never adopt DINE auto-remediation — supported and documented; not a defect.
- **A genuinely public asset** (static-site Storage, public feed) needs a scoped **exemption**, not a disabled policy — exempt the one resource, keep the guardrail.
- **`deny` ordering** matters: `disabled` → `append`/`modify` → `deny` → `audit` → DINE; a `modify` can make a request compliant before `deny` fires.
- Policy *design* for security controls (network, identity) routes to `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/azure-landing-zones-and-governance.md`](../knowledge/azure-landing-zones-and-governance.md) — policy-driven governance, MG-scoped assignment
- [`./lz-flat-management-group-hierarchy.md`](./lz-flat-management-group-hierarchy.md) — the hierarchy these policies inherit down
- [`./cost-budgets-tags-and-policy-guardrails.md`](./cost-budgets-tags-and-policy-guardrails.md) — allowed-SKU/location/tag policies
- [`./ops-diagnostic-settings-to-log-analytics-from-day-one.md`](./ops-diagnostic-settings-to-log-analytics-from-day-one.md) — the DINE diagnostic-settings policy
- [`../agents/azure-ops-engineer.md`](../agents/azure-ops-engineer.md) — owns Policy authoring/enforcement

## Provenance

Codifies house opinion #13 from [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in Microsoft Learn [Policy effect basics](https://learn.microsoft.com/azure/governance/policy/concepts/effect-basics) (effect order; `deny`/`DeployIfNotExists`/`audit`/`modify`), [ALZ policy-driven governance / adopt guardrails](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/enterprise-scale/dine-guidance) (audit→enforce, `DoNotEnforce`/`Default`, DINE needs a managed identity, don't deploy workloads with Policy), and [safe-deployment of policy assignments](https://learn.microsoft.com/azure/governance/policy/how-to/policy-safe-deployment-practices) — retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
