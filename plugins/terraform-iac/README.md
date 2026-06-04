# Terraform & Infrastructure-as-Code

The **terraform-iac** plugin — cloud-agnostic infrastructure-as-code done well — composable Terraform/OpenTofu modules, safe state and backend design, environment promotion, and policy-as-code guardrails — with per-cloud resource detail deferred to the cloud plugins.

## Agents

- **`iac-architect`** — IaC strategy: the module decomposition and boundaries, state isolation by blast radius, the environment-promotion model (workspaces vs directories vs Terragrunt), the repo layout, and the Terraform-vs-OpenTofu and module-registry decisions
- **`terraform-module-engineer`** — Writing composable modules: typed variables with validation, documented outputs, single-responsibility design, for_each over count, version pinning, examples, and module testing
- **`iac-policy-and-state-engineer`** — State backend safety (remote, locked, encrypted, isolated, no secrets), drift detection, and policy-as-code guardrails (OPA/Conftest/Sentinel) on the plan in the pipeline, plus import/state-surgery operations

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install terraform-iac@ravenclaude
```

## Seams

- **The specific cloud resources and their arguments (what an `aws_s3_bucket` / `azurerm_*` / `google_*` actually needs)** → `aws-cloud` / `azure-cloud` / `gcp-cloud`; this team owns the IaC *craft* (modules, state, promotion), they own the resource semantics. Azure-native Bicep also lives in `azure-cloud`.
- **Running `plan`/`apply` in CI with a reviewed plan + OIDC** → `devops-cicd/pipeline-engineer`.
- **The security verdict on a posture finding the policy gate raises** → `security-engineering/cloud-security-engineer` → `ravenclaude-core/security-reviewer`.
- **Reconciling Kubernetes manifests (not infra)** → `devops-cicd/gitops-engineer` + `cloud-native-kubernetes`; IaC stands up the cluster, GitOps fills it.
- **Cross-cloud architecture / landing-zone strategy** → the cloud plugins; IaC implements their design.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
