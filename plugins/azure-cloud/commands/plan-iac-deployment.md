---
description: Plan a safe passwordless IaC deployment — lint, what-if/plan preview as a reviewed PR gate, preflight policy check, Deployment-Stack apply with a deletion guard, then promote — never apply blind to a shared environment.
argument-hint: "[the change, e.g. 'deploy the payments Bicep to prod']"
---

# Plan an IaC deployment

You are running `/azure-cloud:plan-iac-deployment`. Build the deploy runbook for what the user described (`$ARGUMENTS`), following this plugin's `bicep-iac-engineer` discipline — the preview is a required gate, applying blind is the click-ops sin in declarative clothing.

## When to use this

An IaC change is about to touch a shared (especially prod) environment. For a throwaway sandbox under the loose-policy archetype you can relax the deletion guard and promotion stages — but still run the preview to catch template errors.

## Steps

1. **Run `what-if` / `plan` and read it** before every deploy — `az deployment ... what-if` (or `--confirm-with-what-if` interactively) / `terraform plan -out=tfplan` (`iac-what-if-before-every-deploy.md`). Make it a **required PR check**; a reviewer approves the printed change set before the apply stage runs.
2. **In Terraform, apply the saved plan file** (`apply tfplan`) so the thing reviewed is exactly the thing applied — no re-plan drift between review and apply (same file).
3. **Treat the change set carefully:** read past the known `what-if` noise (deployment-time defaults showing as spurious Delete/change), and remember `what-if` can't resolve `reference()` or expand nested templates — a clean preview is necessary, not sufficient; pair with a non-prod stage deploy (same file).
4. **Authenticate passwordless** — workload identity federation (GitHub OIDC / Azure DevOps WIF), no `AZURE_CREDENTIALS` secret, only public client/tenant/subscription IDs passed (`passwordless-by-default.md`).
5. **Apply as a Deployment Stack with `denySettings`** so the managed set is tracked and prod resources are guarded against out-of-band portal deletes; choose `--action-on-unmanage` deliberately (`detachAll` safe vs `deleteAll` clean) (`iac-deployment-stacks-for-lifecycle-and-deletion-guard.md`).
6. **Rely on preflight policy:** the audit-first guardrails surface violations before the deploy lands; promote tier-0 → wider after verifying (`gov-azure-policy-as-guardrails.md`). Use the `templates/azure-cicd-runbook.md` shape.

## Guardrails

- Never run `create`/`apply` with no preview "because it's a small change" — small changes delete subnets too.
- Never `terraform apply` without a saved plan, and never set `--action-on-unmanage deleteAll` on a stack you're iterating on without reading the what-if first.
- This plugin is advisory: emit the exact commands and pipeline stages for the engineer to run with their own credentials — it does not deploy against the consumer's subscription.
