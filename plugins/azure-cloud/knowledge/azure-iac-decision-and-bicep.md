# IaC decision: Bicep vs Terraform (+ AVM, Deployment Stacks)

**Last reviewed:** 2026-05-28 · **Confidence:** high ([Bicep vs Terraform](https://learn.microsoft.com/azure/developer/terraform/comparing-terraform-and-bicep), [AVM](https://learn.microsoft.com/community/content/azure-verified-modules), retrieved 2026-05-28).
**Owner:** `bicep-iac-engineer` (also owns CI/CD — see [`azure-deployment-cicd.md`](azure-deployment-cicd.md)).

## The decision (house opinion #3)
```mermaid
flowchart TD
    A[Need IaC for Azure] --> Q{Azure-only, or multi/hybrid-cloud?}
    Q -->|Azure-only| B[Bicep]
    Q -->|Multi/hybrid-cloud or existing TF estate| T[Terraform azurerm]
    B --> AVM1[Use Azure Verified Modules]
    T --> AVM2[Use Azure Verified Modules]
```

| | Bicep | Terraform |
|---|---|---|
| Scope | **Azure-only** | multi/hybrid-cloud |
| State | **no separate user-managed state file** (keeps deployment history + server-side resource state in Azure) | **`terraform.tfstate`** — back up + secure; use **remote state in Azure Storage** |
| Preview | `what-if` | `terraform plan` |
| Policy | **preflight policy validation** (fails *before* deploy) | fails *during* apply |
| Lifecycle / deletion | **Deployment Stacks** (GA; `denySettings`, managed-resource cleanup) | `lifecycle` meta-argument, `terraform destroy` |
| CLI | `az bicep`, `az deployment` | `terraform` |
| Portal | export ARM/Bicep from portal | `aztfexport` to import existing |

**Default to Bicep for Azure-only work; Terraform when the estate is multi-cloud or already Terraform.** Either way, **use Azure Verified Modules (AVM)** — Microsoft-maintained, WAF-aligned, versioned modules for both languages (including ALZ accelerator + subscription-vending modules).

## Discipline (house opinion #2)
- **IaC or it didn't happen.** Declarative, versioned, pipeline-deployed.
- **`what-if` / `plan` before `apply`** — always preview.
- **No prod click-ops.** If someone changed prod in the portal, export it to IaC and reconcile (drift).
- **Remote, locked, encrypted state** for Terraform (Azure Storage backend; never `backend "local"` for shared infra — the hook flags it).
- **Deployment Stacks** for grouped lifecycle + accidental-deletion protection (the Bicep answer to Terraform lifecycle). Blueprints is deprecated → Stacks + Policy + ALZ.
- **Secrets never in IaC** — Key Vault references / managed identity, never literals (the hook flags `password=`/`accountKey=`/`client_secret`/`connectionString`/`primaryKey`).
- **Parameterize** subscription/tenant IDs (the hook flags hardcoded GUIDs).

## CI/CD
Deploy via GitHub Actions / Azure DevOps with **workload identity federation** (passwordless), `what-if`/`plan` gates, environments + approvals — see [`azure-deployment-cicd.md`](azure-deployment-cicd.md) and [`entra-identity-and-access.md`](entra-identity-and-access.md).
