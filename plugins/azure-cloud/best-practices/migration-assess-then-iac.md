# Migrate by assess-then-IaC — never lift-and-shift into portal drift

**Status:** Pattern — strong default for any brownfield/portal-built estate moving onto a managed footing; deviate only with a written reason.

**Domain:** Migration / IaC

**Applies to:** `azure-cloud`

---

## Why this exists

Migrations and brownfield takeovers are where the whole "infrastructure as code, governed estate" discipline either takes hold or is quietly abandoned. The tempting path — rehost the VMs/resources by hand in the portal and "IaC it later" — produces an estate with no source of truth, no reproducibility, and drift from day one; "later" never comes. The opposite mistake is rewriting everything before anything moves. The durable middle is **assess first, then land the migrated workload directly into IaC** so the new home is captured as code from the moment it exists. This rule is the stance the scattered migration mentions (Blueprints→Stacks, B2C→External ID, hub→Foundry) never consolidated into.

## How to apply

1. **Assess before you move.** Inventory the source (Azure Migrate for VMs/DBs, or an export/audit of an existing portal-built subscription). Capture dependencies, sizing, data gravity, and compliance/residency constraints. Decide per workload: **retire / rehost / replatform / refactor** — don't blanket-lift.
2. **Land into IaC, not the portal.** Author the target as Bicep or Terraform (per the IaC decision tree) — Azure Verified Modules where they fit. For an *existing* portal-built estate, capture current state into code (export templates / `aztfexport` / Terraform import) and reconcile, rather than continuing to click.
3. **Modernize the obvious wins during the move, not as a separate project:** passwordless/managed-identity auth, private data planes, zone-redundant prod, diagnostic settings to Log Analytics from day one — fold these in as you land each workload (they're cheaper to do at migration than to retrofit).
4. **Cut over deliberately:** stand the IaC target beside the source, validate, then switch — keep the source until the target is proven.

**Do:** assess → classify (retire/rehost/replatform/refactor) → author target as IaC → fold in the security/reliability baselines → validate → cut over.

**Don't:** hand-rehost in the portal with "IaC later"; big-bang refactor everything before moving; carry forward public data planes / secret literals / single-zone prod just because the source had them.

## Edge cases / when the rule does NOT apply

A genuine throwaway (a short-lived spike, a dev sandbox you'll delete) doesn't need the full assess-then-IaC ceremony. A pure **rehost with a hard deadline** may rehost first and capture to IaC immediately after — acceptable *only* if the IaC capture is a committed next step with a date, not "later." Azure Migrate's exact supported-source matrix and the `aztfexport`/template-export fidelity are version-sensitive — `[verify-at-build]`.

## See also

- [`../knowledge/azure-iac-decision-and-bicep.md`](../knowledge/azure-iac-decision-and-bicep.md) — Bicep vs Terraform for the target
- [`./pick-compute-from-the-decision-tree.md`](./pick-compute-from-the-decision-tree.md) — where each migrated workload should run
- [`./private-by-default-paas-data-planes.md`](./private-by-default-paas-data-planes.md) · [`./passwordless-by-default.md`](./passwordless-by-default.md) · [`./compute-zone-redundant-by-default-for-prod.md`](./compute-zone-redundant-by-default-for-prod.md) — the baselines to fold in during the move
- [`../agents/azure-architect.md`](../agents/azure-architect.md) — owns migration architecture
- [Cloud Adoption Framework — migrate](https://learn.microsoft.com/azure/cloud-adoption-framework/migrate/) · [Azure Migrate](https://learn.microsoft.com/azure/migrate/) — authoritative

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01): migration appeared only as scattered piecemeal notes (Blueprints→Stacks, B2C→External ID, hub→Foundry) with no overarching assess-then-IaC stance. Grounded in the Microsoft Cloud Adoption Framework migrate methodology + Azure Migrate. Supported-source matrix + export fidelity are `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
