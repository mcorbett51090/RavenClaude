# IaC deployment spec — <STACK>

> Owned by `bicep-iac-engineer`. See `knowledge/azure-iac-decision-and-bicep.md` + `azure-deployment-cicd.md`.

## Tool
- **Bicep | Terraform** — why: <Azure-only → Bicep; multi/hybrid-cloud or existing TF → Terraform>
- **AVM modules**: <which Azure Verified Modules; pinned versions>

## Resources
| Resource | AVM module | Key params | Secrets via |
|---|---|---|---|
| | | | Key Vault ref / managed identity |

## Lifecycle & state
- **Bicep**: Deployment Stack? `denySettings`? scope (RG/sub/MG)?
- **Terraform**: remote state backend (Azure Storage), locking, encryption — **never `backend "local"`**

## Pipeline (passwordless)
- CI: <GitHub Actions | Azure DevOps> + **workload identity federation** (no secret)
- Gates: `what-if` / `terraform plan` on PR; environments + approvals for prod
- Promotion: dev → test → prod (separate subscriptions)

## Checks
- [ ] No secrets/GUIDs hardcoded (parameterized)
- [ ] what-if/plan reviewed before apply
- [ ] Drift strategy (re-run / Deployment Stack denySettings)
