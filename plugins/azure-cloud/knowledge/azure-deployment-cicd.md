# Azure deployment & CI/CD

**Last reviewed:** 2026-05-28 · **Confidence:** high ([workload identity federation](https://learn.microsoft.com/entra/workload-id/workload-identity-federation), [Bicep vs Terraform CLI/pipelines](https://learn.microsoft.com/azure/developer/terraform/comparing-terraform-and-bicep), retrieved 2026-05-28).
**Owner:** `bicep-iac-engineer`.

## Passwordless pipelines (house opinion #4)
**Authenticate CI/CD with workload identity federation — no service-principal secrets.**
- **GitHub Actions** → federate a user-assigned managed identity / app registration to GitHub's OIDC; the workflow exchanges its OIDC token for an Entra token (`azure/login` with `client-id` + `tenant-id` + `subscription-id`, no secret). The federated credential's `subject` must match the workflow (branch/environment/tag) **case-sensitively** — a mismatch fails silently.
- **Azure DevOps** → an **Azure Resource Manager service connection using workload identity federation** (no stored secret).
See [`entra-identity-and-access.md`](entra-identity-and-access.md).

## The pipeline shape
1. **Lint/validate** — `az bicep build` / `terraform validate` + fmt.
2. **Preview** — `what-if` (Bicep) / `terraform plan` as a PR gate; require review.
3. **Policy** — Bicep preflight policy validation catches violations before deploy; Terraform fails on apply (shift left with `az policy` checks).
4. **Deploy** — `az deployment` / `terraform apply` to a stage; use **environments + approvals** for prod.
5. **Promote** dev → test → prod via separate stages (each its own subscription — see landing zones).
6. **Drift** — re-run IaC on a schedule; Deployment Stacks `denySettings` block out-of-band portal edits.

## Modules & reuse
Use **Azure Verified Modules (AVM)** from the Bicep Registry / Terraform Registry; pin versions; the **ALZ accelerator** modules bootstrap the management-group + policy foundation.

## Discipline
- **No prod click-ops** (house opinion #2) — portal changes get exported to IaC and reconciled.
- **Remote, locked Terraform state** (Azure Storage backend) — never `backend "local"` for shared infra (the hook flags it).
- **Secrets** via Key Vault references / managed identity, never in pipeline YAML or IaC (the hook flags literals).

> The application build/test pipeline (compiling the app) is `ravenclaude-core` (backend/frontend-coder + CI); this owns the **infrastructure** deployment pipeline.
