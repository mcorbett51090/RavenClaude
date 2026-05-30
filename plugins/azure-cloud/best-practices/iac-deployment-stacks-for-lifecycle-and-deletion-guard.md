# Group lifecycle with Deployment Stacks + denySettings — Blueprints is deprecated

**Status:** Pattern — strong default for any grouped-resource lifecycle; a plain RG deployment for shared infra needs a written reason.

**Domain:** IaC / Governance

**Applies to:** `azure-cloud`

---

## Why this exists

Two recurring failures motivate this rule. First, **Azure Blueprints is deprecated** — teams still reaching for it are building on a dead surface; the replacement is **Deployment Stacks + Azure Policy + the ALZ accelerator**. Second, a normal Bicep/Terraform deployment has no memory of *which* resources it owns and no guard against someone deleting one in the portal — so infra drifts and out-of-band deletions go unnoticed until something breaks. **Deployment Stacks** (GA) solve both: a stack is a first-class resource that tracks the set of resources it manages (clean lifecycle + managed-resource cleanup on update) and applies **`denySettings`** so the managed resources can't be deleted or modified out-of-band, even by an Owner in the portal. This is the Bicep answer to Terraform's `lifecycle`/`prevent_destroy`. House opinion #3 names it explicitly.

## How to apply

Deploy a managed group of resources as a **stack** with `denySettings` set to block out-of-band deletes/edits. Updates to the stack reconcile the managed set (and can clean up resources removed from the template).

```bash
# Create/update a Deployment Stack at resource-group scope with a deletion guard
az stack group create \
  --name payments-platform \
  --resource-group rg-payments-prod-eastus-001 \
  --template-file main.bicep --parameters main.bicepparam \
  --deny-settings-mode denyDelete \          # block out-of-band deletion of managed resources
  --action-on-unmanage detachAll            # on update, detach (don't delete) resources dropped from the template
```

```hcl
# Terraform equivalent of the deletion guard
resource "azurerm_key_vault" "this" {
  # ...
  lifecycle { prevent_destroy = true }
}
```

**Do:**
- Use a **Deployment Stack** for any grouped lifecycle (a workload's resources, a platform subscription's baseline) so the set is tracked and reconciled.
- Set **`denySettings`** (`denyDelete` or `denyWriteAndDelete`) on prod stacks to block portal/out-of-band deletion of managed resources.
- Choose `--action-on-unmanage` deliberately: `detachAll` (safe — leaves orphans) vs `deleteAll` (clean — removes resources dropped from the template).
- Migrate any remaining **Blueprints** usage to Stacks + Policy + ALZ.

**Don't:**
- Build new governance on **Azure Blueprints** — it's deprecated.
- Leave prod infra with no deletion guard — `denySettings`/`prevent_destroy` is cheap insurance against the accidental portal delete.
- Set `--action-on-unmanage deleteAll` on a stack you're still iterating on without reading the `what-if` first (it will delete dropped resources).

## Edge cases / when the rule does NOT apply

- **Throwaway / sandbox** deployments under the `sandbox` archetype don't need a deletion guard — the point is they're disposable.
- **`denySettings` can block legitimate automation** (a sidecar tool that writes to a managed resource) — scope the deny mode (`denyDelete` vs `denyWriteAndDelete`) and use `excludedActions`/`excludedPrincipals` rather than turning the guard off.
- **A single ad-hoc resource** with no group lifecycle may not warrant a stack — but anything promoted to prod should be stack-managed.

## See also

- [`../knowledge/azure-iac-decision-and-bicep.md`](../knowledge/azure-iac-decision-and-bicep.md) — Deployment Stacks GA, `denySettings`, Blueprints deprecation
- [`../knowledge/azure-2026-capability-map.md`](../knowledge/azure-2026-capability-map.md) — the dated status (Deployment Stacks GA, Blueprints deprecated)
- [`./iac-what-if-before-every-deploy.md`](./iac-what-if-before-every-deploy.md) — preview the stack update before it reconciles
- [`../agents/bicep-iac-engineer.md`](../agents/bicep-iac-engineer.md) — owns Deployment Stacks

## Provenance

Codifies house opinion #3 (Deployment Stacks; Blueprints deprecated) from [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in the IaC + capability-map knowledge files (Microsoft Learn, retrieved 2026-05-28; Stacks GA + `denySettings` + Blueprints-deprecation re-confirmed against the IaC decision tree, 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
