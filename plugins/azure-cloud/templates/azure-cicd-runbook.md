# Azure CI/CD runbook — <PROJECT>

> Owned by `bicep-iac-engineer`. See `knowledge/azure-deployment-cicd.md`. Principle: passwordless (workload identity federation), what-if/plan gates, dev→test→prod.

## Identity (no secrets)
- CI platform: <GitHub Actions | Azure DevOps>
- **Workload identity federation**: federated credential subject = <repo:org/repo:environment:prod | branch> (case-sensitive); audience `api://AzureADTokenExchange`
- Azure DevOps: ARM service connection using workload identity federation

## Stages
| Stage | Subscription | Trigger | Gate |
|---|---|---|---|
| validate | — | PR | `az bicep build` / `terraform validate` + fmt |
| preview | dev | PR | **what-if / plan** (required review) |
| deploy-dev | dev | merge to main | `az deployment` / `terraform apply` |
| deploy-test | test | manual / auto | environment approval |
| deploy-prod | prod | manual | environment approval + change window |

## Guardrails
- [ ] No secrets in pipeline YAML or IaC (Key Vault refs / managed identity)
- [ ] No prod click-ops; drift reconciled to IaC (Deployment Stack denySettings)
- [ ] Remote, locked Terraform state (Azure Storage)
- [ ] Pipeline identity / federated credential reviewed by `ravenclaude-core/security-reviewer`
- [ ] Rollback: redeploy prior state / Git revert
