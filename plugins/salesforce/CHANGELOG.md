# Changelog — salesforce

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.6.5] — 2026-07-09

Research-sweep **knowledge update** — recorded the Summer '26 Agentforce authoring shift in `knowledge/agentforce-determinism-and-trust.md` (the determinism & Trust doc). Led with the determinism-relevant angle: **Agent Script** (schema-driven language mixing deterministic expressions with agentic NL instructions) and the new **Agentforce Builder** are **GA in Summer '26** — a first-class surface for the "push work toward the deterministic end" discipline (house opinion #14). Also noted the legacy *New Agent* builder cutover (week of **2026-07-13**, tagged `[verify-at-use]`) and the Apache-2.0 open-sourcing of the Agent Script toolchain (`github.com/salesforce/agentscript`). Each sub-claim carries its own distinct citation; all tagged `[verify-at-build]`. Verified 2026-07-09.

### Changed

- `knowledge/agentforce-determinism-and-trust.md`: added a dated (2026-07-09) note under the Atlas / Agentforce-builder section plus three source links (Agent Script guide, Summer '26 release guide, `salesforce/agentscript` repo).
- Version **0.6.4 → 0.6.5** in `.claude-plugin/plugin.json` (marketplace.json bumped separately in lockstep).

## [0.6.4] — 2026-07-08

Research-sweep **correctness fix** — the plugin recommended `WITH SECURITY_ENFORCED` as the primary CRUD/FLS enforcement clause (house opinion #7, the reviewer rubric, two skills, the security decision tree, templates). Salesforce **Summer '26 / API v67.0** **removes `WITH SECURITY_ENFORCED`** — an Apex class set to v67.0+ that uses it **does not compile** — and defaults database operations to **user mode** and omitted sharing keywords to **`with sharing`**. Following the old guidance on a v67.0+ class produced non-deployable code. Verified 2026-07-08 against salesforce.com (Summer '26 architect highlights) + developer.salesforce.com.

### Changed

- Lead all CRUD/FLS-enforcement guidance with **`WITH USER_MODE`** and flag `WITH SECURITY_ENFORCED` as removed-at-v67.0+ (valid only on pre-v67.0 classes), across: house opinions #6/#7 (`CLAUDE.md`), `agents/apex-engineer.md`, `agents/salesforce-reviewer.md`, `skills/soql-authoring`, `skills/lwc-component-scaffold`, `knowledge/apex-decision-trees.md` (security mechanism-choice tree + tradeoffs table), `knowledge/sharing-and-security-model.md`, and the `templates/lwc-bundle.md` + `templates/batch-apex-class.md` code samples. Nuance preserved (mirroring the 0.6.2 end-of-support precedent): it is a compiler behavior at v67.0+, not a retroactive break of pre-v67.0 classes. Tagged `[verify-at-build]`.
- Version **0.6.3 → 0.6.4** in `.claude-plugin/plugin.json` + `marketplace.json` (lockstep).

## [0.6.2] — 2026-06-24

### Changed

- **Process Builder & Workflow Rules now framed as end-of-support, not just "legacy."** Salesforce ended support for Process Builder and Workflow Rules on **Dec 31, 2025** (retired for new automation; all new declarative automation → Flow via the "Migrate to Flow" tool). The plugin previously named them only as "legacy" inventory items; it now flags them as **migration targets** while preserving the accuracy nuance that end-of-support is not a runtime shutoff (existing instances still execute, just unsupported). Updated `knowledge/flow-vs-apex-decision.md`, `agents/flow-automation-architect.md` (discipline #1), and `best-practices/flow-vs-apex-one-entry-point.md`, tagged `[verify-at-build]`. Source: Salesforce Help end-of-support article (verified 2026-06-24).

## [0.6.1] — 2026-06-05

Version bump previously unlogged here; the change that set `0.6.1`:

- fix(trees): unblock render + lazy-load decision-tree SVGs (#336)

## [0.6.0] — 2026-06-05

Value-add build-out — the plugin was missed in the earlier marketplace-wide enrichment pass and had no scenarios bank. Every value-add menu item is now dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes + README index).** `soql-in-loop-101-on-trigger` (hoist the query out of the loop, bind `IN :ids`, prove with a 200-record test), `trigger-recursion-runaway-update` (static recursion guard is mandatory; before-context dissolves same-record DML), `guest-user-sharing-data-exposure` (layer `with sharing` + CRUD/FLS + OWD + least-privilege guest profile on a public surface), `agentforce-nondeterministic-action-misfire` (push fixed paths to Flow/Apex; scope topics tightly; gate with the Trust Layer). 9-field schema, every volatile limit/behavior tagged `[verify-at-build]`.
- **Automation-density decision trees.** `knowledge/automation-density-decision-trees.md` — two new Mermaid trees: "where does this new automation go on a busy object?" (the multi-automation density problem, house opinion #12) and "order-of-execution — why does my field get the wrong value?". Fills the gap left by the existing single-requirement Flow-vs-Apex tree; the plugin's other ~20 trees already cover async/security/trigger/SOQL/bulk/integration/LDV/packaging/Agentforce.
- **LSP code-intelligence config.** `.lsp.json` — the **Apex Language Server** (`java -cp ${APEX_JORJE_LSP_JAR} apex.jorje.lsp.ApexLanguageServerLauncher`, the `apex-jorje-lsp.jar` that ships inside the Salesforce Apex VS Code extension; needs JDK ≥ 11, JDK 21 recommended) plus typescript-language-server and vscode-html-language-server for LWC (.js/.ts/.html). Ships the *config*, not the binaries; the Apex jar path is consumer-specific and supplied via `${APEX_JORJE_LSP_JAR}` (honestly documented as a hard prerequisite — see CLAUDE.md § LSP).
- **Runnable governor-smell script.** `scripts/apex_governor_smell.py` (stdlib-only, ruff-clean) — a heuristic static scanner for SOQL/DML-in-loop across a tree of `.cls`/`.trigger` files, strips comments/strings to cut false positives, JSON or text output, exit 1 on any finding. Complements the single-file advisory hook by scanning a whole directory (e.g. in CI). Decision-support, not a guarantee — every finding says "prove the fix with a 200-record bulk test."
- **CLAUDE.md** §§ for the scenarios bank, the runtime/LSP tier, the recommended-not-bundled MCP disposition, and the value-add completeness table.

### Decisions (recorded, not built)

- **No bundled MCP server.** The official **Salesforce DX MCP Server** (`@salesforce/mcp`) and the **Salesforce Hosted MCP Servers** are **org-credentialed** — they require an authorized org (`--orgs` flag / OAuth via an External Client App), and even the read-only `sobject-reads` hosted server enforces per-user OAuth. That fails the doctrine's zero-config + no-secret bar → **recommend-not-bundle**, with the connection secret kept as a **reference** (never a literal) and a `ravenclaude-core/security-reviewer` gate before adoption. No zero-config no-auth Salesforce docs MCP was found to bundle. No invented servers. (`docs/best-practices/bundled-mcp-servers.md`.)
- **No `bin/`, output-styles, monitors, settings defaults, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface" bar; the advisory hook + the new script + 5 skills already cover the runnable surface.
- **Skills/commands/templates/hooks coverage held sufficient** — 5 skills, 8 commands, 5 templates, 1 advisory hook already cover the surface; the new scenarios + density trees + script extend reach without a new agent (team-growth-as-knowledge house rule).
- **No new NOTICE.md** — nothing third-party is bundled (the script is original stdlib-only; the LSP/MCP packages are referenced, not vendored).

### Verify-at-use

- `@salesforce/mcp` package + version (0.26.9 at time of writing; still pilot/beta), the Salesforce Hosted MCP server set, and the External-Client-App OAuth flow. The Apex Language Server jar name (`apex-jorje-lsp.jar`), launcher main class, and Java version floor (≥ 11, JDK 21 recommended). Governor-limit numbers (SOQL 100 sync / 200 async, DML 150, trigger depth 16) and all Agentforce/Atlas/Trust-Layer + guest-user-security specifics. All version-volatile — re-confirm against Salesforce docs / the limits cheat sheet before quoting.

## [0.5.1] — earlier

5-agent Salesforce team (apex-engineer, flow-automation-architect, agentforce-architect, salesforce-platform-architect, salesforce-reviewer): governor-safe bulkified Apex, declarative-automation triage, Agentforce design under determinism + Trust Layer, org architecture (data model / sharing / LDV / 2GP packaging / DevOps / integration), and a forked review rubric (the 15 house opinions as pass/fail). Citation-grounded knowledge bank (~20 Mermaid decision trees), 5 skills, 8 commands, 5 templates, 1 advisory anti-pattern hook, ~70 best-practice rules.
