# Run `what-if` / `plan` before every deploy — never apply blind

**Status:** Absolute rule — applying IaC to a shared environment without previewing the change set is the click-ops sin in declarative clothing.

**Domain:** IaC / Deployment

**Applies to:** `azure-cloud`

---

## Why this exists

The whole value of declarative IaC is that you can see the delta *before* it touches a running estate — yet the most common way a Bicep/Terraform change causes an outage is someone running `az deployment ... create` (or `terraform apply`) straight from a branch without reading the preview. A deployment in **complete mode**, a renamed resource, or a changed `addressPrefix` can silently delete a subnet or recreate a database. House opinion #2 is "IaC or it didn't happen — **what-if/plan before apply**." The preview is also a free validation pass: `what-if` validates the template for errors and, on Bicep, surfaces **preflight policy** violations *before* anything deploys. Make the preview a required, reviewed PR gate — not an optional courtesy.

## How to apply

Gate every deploy on a previewed, human-reviewed change set. Use `--confirm-with-what-if` for interactive runs and a separate `what-if` PR stage for pipelines.

```bash
# Interactive: preview, then confirm at the prompt (one command)
az deployment group create \
  --resource-group rg-payments-prod-eastus-001 \
  --template-file main.bicep --parameters main.bicepparam \
  --confirm-with-what-if          # shows the diff, waits for y/N

# Pipeline PR gate: emit the change set for review, fail the job on error
az deployment sub what-if \
  --location eastus --template-file main.bicep --parameters main.bicepparam

# Terraform equivalent
terraform plan -out=tfplan        # review, then `terraform apply tfplan` on the SAME plan
```

**Do:**
- Make `what-if` (Bicep) / `terraform plan` a **required PR check**; require a reviewer to approve the printed change set before the apply stage runs.
- In Terraform, `apply` the **saved plan file** (`apply tfplan`), so the thing reviewed is exactly the thing applied — no drift between plan and apply.
- Treat `Delete` / `DeployIfNotExists`-noise lines in the `what-if` output as a signal to read carefully, not to skip the review.

**Don't:**
- Run `create` / `apply` with no preview "because it's a small change" — small changes delete subnets too.
- Approve a change set you didn't read, or `terraform apply` *without* a saved plan (re-planning at apply time can pick up new drift).

## Edge cases / when the rule does NOT apply

- **`what-if` noise** — properties set as deployment-time defaults can show as spurious `Delete`/change; that's a known limitation, not a reason to skip the review. Read past the noise.
- **`reference()` / nested-template expansion** — `what-if` can't resolve `reference()` and won't expand `templateLink` nested deployments, so some changes won't show; a clean preview is necessary, not sufficient. Pair with a non-prod stage deploy.
- **First-ever greenfield deploy** into an empty RG has nothing to diff against — the preview is all `Create`; still run it to catch template errors.

## See also

- [`../knowledge/azure-iac-decision-and-bicep.md`](../knowledge/azure-iac-decision-and-bicep.md) — `what-if` vs `plan`, preflight policy validation, Deployment Stacks
- [`../knowledge/azure-deployment-cicd.md`](../knowledge/azure-deployment-cicd.md) — the pipeline shape (lint → preview → policy → deploy → promote → drift)
- [`./iac-deployment-stacks-for-lifecycle-and-deletion-guard.md`](./iac-deployment-stacks-for-lifecycle-and-deletion-guard.md) — protecting the resources this preview touches
- [`../agents/bicep-iac-engineer.md`](../agents/bicep-iac-engineer.md) — owns IaC authoring + the deploy pipeline

## Provenance

Codifies house opinion #2 from [`../CLAUDE.md`](../CLAUDE.md) §3 and the §4 anti-pattern ("applying without what-if/plan"). Grounded in Microsoft Learn [Bicep what-if](https://learn.microsoft.com/azure/azure-resource-manager/bicep/deploy-what-if) (`az deployment group/sub/mg/tenant what-if`, `--confirm-with-what-if`, the `reference()` / nested-template limitations, and the default-value "noise" caveat — retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
