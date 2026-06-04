# Terraform & Infrastructure-as-Code Plugin — Team Constitution

> Team constitution for the `terraform-iac` Claude Code plugin — **3** specialist agents for cloud-agnostic infrastructure-as-code done well — composable Terraform/OpenTofu modules, safe state and backend design, environment promotion, and policy-as-code guardrails — with per-cloud resource detail deferred to the cloud plugins. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`iac-architect`](agents/iac-architect.md) | IaC strategy: the module decomposition and boundaries, state isolation by blast radius, the environment-promotion model (workspaces vs directories vs Terragrunt), the repo layout, and the Terraform-vs-OpenTofu and module-registry decisions | "how should we structure our Terraform?", "our state is one giant file", "how do we promote across environments", "Terraform or OpenTofu?" |
| [`terraform-module-engineer`](agents/terraform-module-engineer.md) | Writing composable modules: typed variables with validation, documented outputs, single-responsibility design, for_each over count, version pinning, examples, and module testing | "write a reusable module for X", "refactor this copy-pasted config into a module", "our modules use count and break on reorder", "add input validation" |
| [`iac-policy-and-state-engineer`](agents/iac-policy-and-state-engineer.md) | State backend safety (remote, locked, encrypted, isolated, no secrets), drift detection, and policy-as-code guardrails (OPA/Conftest/Sentinel) on the plan in the pipeline, plus import/state-surgery operations | "set up remote state safely", "add policy guardrails to our plans", "we have drift", "safely import existing resources" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **State is precious and dangerous.** Remote, locked, encrypted, backed up — and never with secrets in it (state stores them in plaintext). A lost or corrupted state file is a manual reconciliation nightmare.
2. **Isolate state by blast radius.** One giant state for the whole estate means one `apply` can take down everything and every plan is slow. Split by lifecycle/environment/component.
3. **Modules are contracts, not copy-paste.** A module has typed inputs, documented outputs, a version, and a single responsibility. Versionless copy-paste modules drift into N divergent forks.
4. **Plan is the review artifact.** Never `apply` what you didn't read in a `plan`. Auto-apply without a reviewed plan in CI is how infra gets deleted by surprise.
5. **Pin providers and modules.** Floating versions make `terraform init` non-deterministic and turn a routine change into a surprise upgrade. Lock files are committed.
6. **Guardrails are policy-as-code in the pipeline.** Encode 'no public buckets, no wildcard IAM, tags required' as OPA/Sentinel/Conftest checks on the plan — preventive, not a post-hoc audit.

## 3. Seams (the bridges to neighbouring plugins)

- **The specific cloud resources and their arguments (what an `aws_s3_bucket` / `azurerm_*` / `google_*` actually needs)** → `aws-cloud` / `azure-cloud` / `gcp-cloud`; this team owns the IaC *craft* (modules, state, promotion), they own the resource semantics. Azure-native Bicep also lives in `azure-cloud`.
- **Running `plan`/`apply` in CI with a reviewed plan + OIDC** → `devops-cicd/pipeline-engineer`.
- **The security verdict on a posture finding the policy gate raises** → `security-engineering/cloud-security-engineer` → `ravenclaude-core/security-reviewer`.
- **Reconciling Kubernetes manifests (not infra)** → `devops-cicd/gitops-engineer` + `cloud-native-kubernetes`; IaC stands up the cluster, GitOps fills it.
- **Cross-cloud architecture / landing-zone strategy** → the cloud plugins; IaC implements their design.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.
