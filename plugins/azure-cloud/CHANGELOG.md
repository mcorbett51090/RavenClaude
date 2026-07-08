# Changelog — azure-cloud

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

> Note: this file tracks the major arcs; the authoritative version history is the `version` field in `.claude-plugin/plugin.json` + git history (per the marketplace CHANGELOG convention). The 0.2.x–0.4.x bumps between the initial release and the build-out below were tracked in `plugin.json` + git, not back-filled here.

## [0.5.5] — 2026-07-08

Weekly Tier-A news sweep (2026-07-08) — **correction + additions** in `knowledge/azure-ai-foundry.md`. **Correction:** the `azure-ai-inference` retirement date was conflated with the Assistants API sunset — the package retires **2026-05-30** (migrate to the `openai` package); **2026-08-26** is the *separate* Assistants API sunset → Foundry Agents / Responses API. **Additions:** the new Microsoft Foundry portal is now **GA** (per-feature GA/preview split noted); Claude models (**Opus 4.8, Sonnet 5, Haiku 4.5**) are **GA hosted-on-Azure** in Microsoft Foundry (CCU-billed). Sources: MS Learn navigate-from-classic, Foundry GA overview, Claude-models-in-Foundry (Microsoft-Learn MCP). Routed through usefulness → review panels (both APPROVE). **Migration:** none — knowledge-file content only.

## [0.5.2] — 2026-07-02

### Fixed

- **`check-azure-anti-patterns.sh` STRICT mode now actually blocks.** `AZURE_STRICT=1` exited `1`, which Claude Code treats as a non-blocking error (silently swallowed), so the documented enforcement mode did nothing. Now exits `2` (the PreToolUse deny code). (Autonomous 3-panel repo review, P1.)

## [0.5.1] — 2026-06-22

Version bump previously unlogged here; the change that set `0.5.1`:

- Weekly Tier-A sweep: Microsoft-stack June-2026 GA/preview corrections (#451)

## [0.5.0] — 2026-06-05

Value-add completeness build-out (CLOUD/infra domain — runtime tier dispositioned). Builds on PR #315 (which consolidated the knowledge decision-trees + `best-practices/` + `templates/`); this release closes the net-new gaps. Full per-item disposition in CLAUDE.md "Value-add completeness (build-out 2026-06-05)".

- **Scenarios bank enabled** — `scenarios/README.md` + 4 dated, scope-tagged, unverified engagement narratives: Entra over-privileged `Owner` + break-glass sequencing; cost spike → Log Analytics/orphans/right-size-then-commit; Private Endpoint DNS resolution failure in hub-spoke; workloads-before-landing-zone retrofit. 9-field schema, every volatile fact dated + `[verify-at-use]`, routed to the most-likely specialist. CLAUDE.md §8a flipped from TODO to enabled.
- **New decision tree** — `knowledge/azure-data-store-decision-tree.md` (Mermaid): which managed database — Azure SQL / SQL Managed Instance / PostgreSQL Flexible Server / Cosmos DB / Storage. Complements #315's trees + the compute tree (data-store selection had a best-practice but no traversable diagram). Grounded + cited (Microsoft Learn, 2026-06-05).
- **Azure MCP Server doctrine** — CLAUDE.md §11a: the official **Azure MCP Server** (`@azure/mcp`, first-party `microsoft/mcp`) dispositioned **recommend-not-bundle** (per-tenant, Entra-credentialed, write-capable by default). Documents the `claude mcp add … --read-only` path with reference creds, `--namespace` scoping, and a mandatory `security-reviewer` gate. Package + flags verified against Microsoft Learn (2026-06-05).
- **Runtime tier dispositioned** — LSP (N-A: no standalone on-`PATH` Bicep language server; the LS ships inside the VS Code extension as `Bicep.LangServer.dll`, Azure/bicep #1141 closed without a standalone binary), runnable script (N-A: cost/right-sizing logic is live-tenant data covered by the MCP/`az` path, and no baked-in prices), bin/monitors/output-styles/settings/themes (N-A), skills/hooks/commands/templates (sufficient). No `NOTICE.md` (nothing third-party vendored).

## [0.1.0] — 2026-05-28

Initial release. An Azure cloud infrastructure & platform specialist team built from a researched, expert-reviewed plan (see [`docs/azure-cloud-plugin-analysis.md`](../../docs/azure-cloud-plugin-analysis.md)).

- **7 agents:** `azure-architect`, `bicep-iac-engineer`, `entra-identity-engineer`, `network-engineer`, `app-platform-engineer`, `integration-engineer`, `azure-ops-engineer`.
- **9-doc knowledge bank** (CAF/WAF + first-party, retrieval-dated 2026-05-28): landing zones & governance, IaC decision + Bicep, compute decision tree, Entra identity & access, networking & connectivity, integration decision, observability & FinOps, deployment & CI/CD, and the dated 2026 capability map.
- **6 templates:** landing-zone plan, IaC deployment spec, architecture spec, Entra identity design, cost & observability review, CI/CD runbook.
- **1 advisory hook** (`check-azure-anti-patterns.sh`, `AZURE_STRICT=1` to block): hardcoded secret, public exposure, Owner/Contributor at sub/MG scope, TLS/HTTPS off, hardcoded subscription/tenant GUID, Terraform local backend.
- **16 house opinions.** Ships **no** security/architect clone — escalates to core.

### Built per the round-3 expert review
- Added the `network-engineer` agent + `azure-networking-and-connectivity.md` (networking was unowned); added private-endpoint/deny-public-by-default + zone-redundant-prod + CAF-naming house opinions; moved CI/CD into `bicep-iac-engineer`.
- **Shipped the four reciprocal seam edits in the same release:** `power-platform/CLAUDE.md` (Logic-Apps↔Power-Automate, the #1 collision), `claude-app-engineering/CLAUDE.md` (Azure-host seam), `microsoft-fabric/CLAUDE.md` (raw Azure data services), `web-design/agents/web-architect.md` (Static Web Apps provisioning).
- Accuracy: B2C end-of-sale nuances, Deployment Stacks GA / Blueprints deprecated, Flex Consumption constraints, AVM ALZ + vending modules.

### Deferred to a later version
- `azure-ops-engineer` likely splits (observability / FinOps / governance) in v0.2.0.
- A `skills/` directory and a `scenarios/` bank when the first engagement scenario surfaces.
- Evaluate bundling an Azure MCP server if a stable community one emerges.
