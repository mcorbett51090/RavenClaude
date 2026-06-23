# Changelog — terraform-iac

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.2] — 2026-06-22

Version bump previously unlogged here; the change that set `0.3.2`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.3.1] — 2026-06-11

Research-sweep **correction** — refreshed the stale OpenTofu version stamp + added OCI-registry distribution, re-verified 2026-06-11 against the OpenTofu releases + docs.

### Fixed

- **`knowledge/terraform-iac-decision-trees.md`** — the "Last verified … OpenTofu **1.8**" stamp now reflects the current GA **OpenTofu 1.12.x** (1.12.0 2026-05-14, 1.12.1 2026-05-27). Added that since **OpenTofu 1.10**, modules **and** providers can be distributed via **OCI registries** (new row in the module-distribution tradeoffs table — reuse existing container-registry infra). Sources: [OpenTofu releases](https://github.com/opentofu/opentofu/releases), [OCI registry integrations](https://opentofu.org/docs/cli/oci_registries/). (Native S3 state locking was already documented — not changed.)
- Version **0.3.0 → 0.3.1** in `.claude-plugin/plugin.json` + `marketplace.json` (lockstep).

## [0.3.0] — 2026-06-05

Value-add build-out against the full menu — adds the scenarios bank, the technical-runtime tier (LSP code intelligence), a second topic-specific decision-tree knowledge file, and honestly dispositions every remaining menu item. Builds on PR #315 (the consolidated decision-trees + best-practices + templates), filling the net-new gaps: scenarios + runtime tier.

### Added

- **scenarios/ bank (4 field notes).** New `scenarios/` directory + README + 4 dated, scope-tagged engagement scenarios on the 9-field schema: `state-drift-import-recovery` (classify drift per-resource — codify/import/revert — never a blanket apply), `backend-migration-state-lock` (verify the state copy landed; `force-unlock` only the exact-ID of a provably-dead holder), `destroy-blast-radius-plan-review` (blast radius is state shape, not `-target`; isolate + `prevent_destroy`), `secrets-in-state-remediation` (rotate-first; `sensitive` hides display not storage; `state rm` is not a remediation). Each carries an "Action for the next engineer" lesson and flags state-mutating ops as high-blast/operator-reviewed.
- **LSP code-intelligence config (`.lsp.json`).** Referenced from `plugin.json` `lspServers`. Configures **terraform-ls** (HashiCorp's official Terraform language server) over `terraform-ls serve` (stdio) for `.tf` → `terraform` and `.tfvars` → `terraform-vars`. Ships the config, **not the binary** — install separately (`brew install hashicorp/tap/terraform-ls`, `go install github.com/hashicorp/terraform-ls@latest`, or the releases page); loud-but-non-fatal if missing. See CLAUDE.md §6.
- **2nd decision-tree knowledge file** (`knowledge/terraform-state-operations-decision-trees.md`) — complements PR #315's base trees with two new topic-specific Mermaid trees the base file points at but doesn't resolve: (1) **which state operation fits** (import vs `moved`/`state mv` vs `state rm` vs `-replace` vs `force-unlock`, with a danger table), and (2) **module versioning & rollout** (semver-by-interface-change, ship `moved` blocks inside the module on breaking restructures, pin registry/git refs, roll out per-caller). Grounded + cited + dated.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP runtime tier), §7 (recommended-not-bundled MCP server), §8 (value-add completeness disposition table), §9 (milestones).

### Decisions (recorded, not built)

- **No bundled MCP server.** HashiCorp's official `terraform-mcp-server` exists and is real, but it does **not** clear the doctrine's bundle bar: its registry/docs read-only mode is zero-config but the same server also carries **write-capable** HCP/TFE workspace operations (gated behind `ENABLE_TF_OPERATIONS` / `TFE_TOKEN`), and the useful private-registry + workspace features are **per-tenant + token-authenticated**. Per `docs/best-practices/bundled-mcp-servers.md` that is **recommend-not-bundle** (write-capable OR per-consumer config). Documented the recommended `claude mcp add … docker run hashicorp/terraform-mcp-server:<pinned>` path (registry-only toolset, `ENABLE_TF_OPERATIONS=false`, token as a reference not a literal) in CLAUDE.md §7 instead of shipping an `mcpServers` entry. No invented server.
- **No `bin/`, scripts/, monitors, output-styles, settings, or themes.** None cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or the operator's `terraform`/`tofu`/`tflint`/`conftest` CLIs" bar. A wrapper script would shadow the real CLIs the agents should call directly; the advisory hook already covers anti-pattern flagging.
- **Skills/commands/templates/hooks coverage held sufficient** — 7 skills, 4 commands, 4 templates, 1 advisory hook already cover module design, state safety, state surgery, and policy-as-code; the new scenarios + decision trees extend reach without a new agent or skill.

### Verify-at-use

- terraform-ls invocation (`terraform-ls serve`, stdio), language IDs (`terraform`/`terraform-vars`), and install paths (Homebrew `hashicorp/tap/terraform-ls`, `go install …@latest`) verified 2026-06-05 against the terraform-ls repo docs — version-volatile; re-confirm at use. Claude Code LSP-plugin support is version-gated (`[verify-at-use]`).
- `terraform-mcp-server` image (`hashicorp/terraform-mcp-server`, latest example tag `0.5.2`), toolsets (`registry`/`registry-private`/`terraform`/`all`/`default`), and the `ENABLE_TF_OPERATIONS` write gate verified 2026-06-05 against the repo README — version-volatile; pin and re-confirm at adoption.
- Decision-tree version-introduced facts (`moved` 1.1, `import` block 1.5, `taint` deprecated for `-replace`) are version-volatile — re-confirm against the user's Terraform/OpenTofu version.

### Shared-file changes (orchestrator-owned, NOT done here)

- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/.lsp.json` — no new glob needed. (`.mcp.json` is intentionally absent — MCP is recommend-not-bundle, no file shipped.)
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.2.2` → `0.3.0`.

## [0.2.2] — earlier

3-agent Terraform/IaC team (`iac-architect`, `terraform-module-engineer`, `iac-policy-and-state-engineer`): 7 skills, a decision-tree knowledge bank (state-isolation + module-boundary + remote-backend + env-promotion + drift + module-vs-inline + Terraform-vs-OpenTofu trees + a dated tooling map), 12 best-practices, 4 templates, 4 commands, 1 advisory hook. Seams to aws/azure/gcp cloud plugins, devops-cicd, security-engineering.
