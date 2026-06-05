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

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer):
  - [`knowledge/terraform-iac-decision-trees.md`](knowledge/terraform-iac-decision-trees.md) — state-isolation, module-boundary, remote-backend, environment-promotion, drift (codify/import/revert), module-vs-inline, Terraform-vs-OpenTofu, promotion-across-envs, plus a dated capability map.
  - [`knowledge/terraform-state-operations-decision-trees.md`](knowledge/terraform-state-operations-decision-trees.md) — **complements** the base file with the two trees it points at but doesn't resolve: **which state operation** (import vs `moved`/`state mv` vs `state rm` vs `-replace` vs `force-unlock`, with a danger table) and **module versioning & rollout** (semver-by-interface-change, ship `moved` blocks inside the module on breaking restructures, pin registry/git refs).

  **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol. Every state-mutating leaf is **high-blast and operator-reviewed**.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (drift import-recovery, backend migration + stale-lock recovery, destroy blast-radius, secrets-in-state remediation). Secondary source; never replaces the knowledge bank, and a state-mutating op in a scenario is a recommendation to review, not an auto-runnable recipe.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

Terraform/IaC is a **code** domain (HCL configuration), so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time HCL intelligence — go-to-definition across modules, find-references for variables/outputs, completion, and diagnostics — instead of grep-and-guess. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section, 2026-06-05); Claude Code LSP-plugin support is version-gated `[verify-at-use]`.

It configures HashiCorp's official Terraform language server:

| Language | Server | `command` | Handles | Install (consumer, separate) |
|---|---|---|---|---|
| Terraform HCL | **terraform-ls** (HashiCorp, official) | `terraform-ls serve` | `.tf` (`terraform`), `.tfvars` (`terraform-vars`) | `brew install hashicorp/tap/terraform-ls` **or** `go install github.com/hashicorp/terraform-ls@latest` **or** the [releases page](https://github.com/hashicorp/terraform-ls/releases) (single binary on `PATH`) |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If `terraform-ls` isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and HCL intelligence degrades — Claude Code and all other tools keep working (the **loud-but-non-fatal** posture). LSP servers start only after the workspace is trusted, and `/reload-plugins` picks up a config change mid-session.

> The binary name, the `serve` invocation, the stdio transport, and the `terraform` / `terraform-vars` language IDs are verified against the terraform-ls docs (USAGE.md + installation.md, 2026-06-05). terraform-ls deliberately does **not** handle `*.tf.json` / `*.tfvars.json` / Packer HCL — so we scope `.lsp.json` to `.tf` and `.tfvars` only. Re-confirm the install paths and any Claude-Code LSP version gate at use — both are version-volatile.

## 7. Recommended (not bundled) MCP server — Terraform MCP

This plugin **bundles no MCP server**, on purpose. HashiCorp ships an official [`terraform-mcp-server`](https://github.com/hashicorp/terraform-mcp-server) — real and useful — but it does **not** clear the bundle bar in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) (a bundled server must be **zero-config AND read-only**).

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Terraform MCP** ([`hashicorp/terraform-mcp-server`](https://github.com/hashicorp/terraform-mcp-server), HashiCorp first-party) | The **public-registry/docs** toolset *is* zero-config + read-only (provider/module/policy lookup, no token) — but the **same server also exposes write-capable HCP/TFE workspace operations** (create/update/delete workspaces, run management) gated behind `ENABLE_TF_OPERATIONS` + `TFE_TOKEN`, and the genuinely valuable private-registry/workspace features are **per-tenant + token-authenticated**. "Write-capable OR per-consumer config" → **recommend, don't bundle**; and a first-party vendor server is a recommend (not bundle) row regardless. | `claude mcp add terraform -- docker run -i --rm -e ENABLE_TF_OPERATIONS=false hashicorp/terraform-mcp-server:<pinned-tested-tag>` for the **registry-only, read-only** subset. For HCP/TFE features, pass `TFE_TOKEN` as a **reference** (env-var name / vault URI, never a literal) and gate any write capability through `ravenclaude-core/security-reviewer` before adoption (Step 5 of the doctrine + Gate 25 allowlist). Pin the image tag and record the tested version. |

**Why not bundled (the load-bearing reasoning):** even the read-only registry toolset rides in the same binary as the write/token-bearing HCP/TFE verbs, and the high-value features need a per-tenant token — both push it to **recommend-not-bundle** under the decision table. Shipping it as `mcpServers` would auto-start a server whose write surface we can't pre-gate per consumer. If you adopt it, prefer the registry-only toolset (`--toolsets registry` / `ENABLE_TF_OPERATIONS=false`), keep the token a reference, and route write adoption through `security-reviewer`.

> Verified 2026-06-05 against the [`terraform-mcp-server` README](https://github.com/hashicorp/terraform-mcp-server/blob/main/README.md): image `hashicorp/terraform-mcp-server` (latest example tag `0.5.2`); toolsets `registry` / `registry-private` / `terraform` / `all` / `default`; `ENABLE_TF_OPERATIONS` (default `false`) gates the approval-required write tools; `TFE_TOKEN` (default empty) unlocks HCP/TFE + private registry. Image tag, toolset names, and env-var semantics are volatile — pin and re-confirm at adoption.

## 8. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). Builds on PR #315, which already added the consolidated `knowledge/*-decision-trees.md`, `best-practices/`, and `templates/`; this round fills the net-new gaps (scenarios + runtime tier).

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — `scenarios/` + README + 4 scenarios (drift import-recovery, backend migration + stale-lock, destroy blast-radius, secrets-in-state remediation) on the 9-field schema; state-mutating ops flagged high-blast/operator-reviewed. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/terraform-state-operations-decision-trees.md`: state-operation triage + module-versioning/rollout trees. Complements (does not duplicate) PR #315's base trees — these are the two the base file points at but doesn't resolve. Grounded + cited + dated. |
| 3 | **LSP server** | **BUILT** — `.lsp.json` configuring terraform-ls (HashiCorp official), wired via `plugin.json` `lspServers`. Genuinely useful for an HCL/code domain; binary installs separately (§6). |
| 4 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. The official `terraform-mcp-server` is real but write-capable (HCP/TFE) + per-tenant-token for its high-value features, and is first-party-vendor → recommend-not-bundle. Documented the registry-only, read-only `claude mcp add` path with a `security-reviewer` gate for writes. No invented server. |
| 5 | **Runnable script under scripts/** | **N-A** — no script clears the "real value, doesn't shadow the operator's CLIs" bar. The agents should call the real `terraform`/`tofu`/`tflint`/`conftest`/`terraform-ls` directly; a wrapper would duplicate them and the advisory hook already flags anti-patterns. |
| 6 | **bin/ / monitors / output-styles / settings / themes** | **N-A** — none groundable to broad value here. `bin/` would shadow the real CLIs; there's no long-running process to monitor (a drift-detection cadence is a CI concern → `devops-cicd`); deliverables are reviewed plans/HCL governed by the agents' Output Contract, not a styling surface. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 7 skills, 4 commands, 4 templates, 1 advisory hook already cover module design, state safety, state surgery, and policy-as-code. The new scenarios + decision trees extend reach without a new agent or skill (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.3.0` entry. No `NOTICE.md` (nothing third-party is bundled — the MCP server is recommend-not-bundle, not vendored). |

## 9. Milestones

- **v0.2.2** — 3-agent Terraform/IaC team: 7 skills, the consolidated decision-tree knowledge bank, 12 best-practices, 4 templates, 4 commands, 1 advisory hook (incl. PR #315's consolidation).
- **v0.3.0** — value-add build-out: scenarios bank (4 scenarios), the LSP runtime tier (`.lsp.json` → terraform-ls), a 2nd topic-specific decision-tree knowledge file (state-operation triage + module versioning), CHANGELOG. MCP dispositioned recommend-not-bundle with the real HashiCorp server documented (§7); `bin/`/scripts/monitors/styles/themes dispositioned N-A with reasons (§8).
