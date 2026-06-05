# Changelog — devops-cicd

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-05

Value-add build-out — extending the PR #315 base (consolidated decision-trees + best-practices + templates) against the full value-add menu. Every menu item was dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `flaky-pipeline-stabilization` (classify each failure — retry only transient infra, quarantine real defects, fix isolation flakes at the root), `slow-build-cache-strategy` (lockfile-keyed cache + Dockerfile layer order + affected-only execution, not a bigger runner), `canary-rollback-no-health-signal` (a timer is not a canary — wire the SLO signal to the promote/abort gate), `secrets-in-ci-leak-remediation` (rotate first, move to OIDC, scan — deleting the line is not remediation). README + 9-field schema, each cross-linked to the decision trees + best-practices.
- **Decision-tree knowledge.** `knowledge/deployment-strategy-and-runner-cache-decision-trees.md` — two Mermaid trees that **complement** #315's: (1) deployment-strategy **preconditions** (migration-first, the health-signal gate, blue-green shared-state safety, rollback-before-ship), and (2) **runner & build-cache placement** (hosted-vs-self-hosted, ephemeral-vs-persistent, lockfile-keyed cache, Dockerfile layer ordering, registry/remote build cache), plus a dated capability map.
- **LSP code-intelligence config.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring Red Hat `yaml-language-server` — schema-driven completion/hover/diagnostics on the plugin's authored surface (workflow + manifest YAML). Ships the config, not the binary; binary installs separately (loud-but-non-fatal if missing). Verified against the Claude Code plugins reference (2026-06-05).
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier), §7 (recommended-not-bundled MCP servers), §8 (value-add completeness table), §9 (milestones).

### Decisions (recorded, not built)

- **No bundled MCP server.** The two real first-party CI/CD/VCS servers — GitHub MCP (`github/github-mcp-server`, MIT) and CircleCI MCP (`@circleci/mcp-server-circleci`) — are both credentialed (token/OAuth) and GitHub's is write-capable by default, so neither clears the doctrine's zero-config + read-only bar. Documented the recommended setup paths instead (GitHub in `--read-only` mode; secrets as environment references, never literals). No invented servers.
- **No runnable `scripts/` artifact.** A DORA-metrics calculator needs per-team deployment/incident data (overlaps `observability-sre`) and a pipeline-cost calc would be a thin arithmetic wrapper — neither cleared the "real value, doesn't duplicate a neighbour" bar this round.
- **No `bin/`, monitors, output-styles, settings, or themes** — none groundable to broadly-valuable, non-duplicative instances.
- **Skills/commands/templates/hooks coverage held sufficient** — the #315 surface (5 skills, 4 commands, 4 templates, 1 advisory hook) covers the domain; no new component added to avoid gold-plating.

### Verify-at-use

- LSP support landed in Claude Code 2.0.74; the `yaml-language-server` npm package name + `--stdio` invocation; GitHub MCP server image tag / remote URL / read-only flag; CircleCI MCP version (latest observed `0.1.8`). All version-volatile — re-confirm against the vendor before quoting.

## [0.2.2] — earlier

4-agent DevOps & CI/CD team (pipeline-engineer, release-engineer, gitops-engineer, build-and-artifact-engineer): 5 skills, 4 commands, 4 templates, 1 advisory hook, 12 best-practices, and (PR #315) the consolidated `knowledge/devops-cicd-decision-trees.md` decision-tree bank. Seams to terraform-iac, cloud-native-kubernetes, observability-sre, ravenclaude-core/security-reviewer, the cloud plugins, and team-portfolio.
