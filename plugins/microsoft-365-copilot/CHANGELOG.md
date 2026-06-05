# Changelog — microsoft-365-copilot

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.5.0] — 2026-06-05

Value-add build-out against the full marketplace value-add menu, building on PR #315 (which added the consolidated decision-trees knowledge, `best-practices/`, and `templates/`). Every menu item is dispositioned (built or recorded N-A with reason) in [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `declarative-agent-scope-too-broad` (over-broad grounding + over-stuffed instructions → tighten grounding, trim instructions, golden-prompt set), `connector-everyone-acl-oversharing` (per-item ACLs + semantic labels are both non-negotiable; RSS/RCD is not a boundary), `api-plugin-obo-auth-loop` (app-only used where delegated/OBO required; `operationId`↔manifest mismatch), `agent-not-surfacing-in-copilot` (publish ≠ available — Agent Registry approval + license + conversation starters). README + 9-field schema mirroring the marketplace pattern.
- **Bundled MCP server — `microsoft-learn` (Microsoft Learn MCP Server).** A first-party, zero-auth, **read-only** remote HTTP MCP at `https://learn.microsoft.com/api/mcp` (tooling repo `MicrosoftDocs/mcp`, MIT) exposing `microsoft_docs_search` / `microsoft_code_sample_search` / `microsoft_docs_fetch`. It is the fitting grounding companion for a plugin whose #1 risk is the ~monthly-velocity Copilot surface — agents verify a volatile manifest/connector/auth fact against current Learn docs instead of recalling a stale schema. Wired in `plugin.json` (`mcpServers` HTTP type + `x-mcpAttribution`) with a `NOTICE.md` attribution + doctrine block in CLAUDE.md §11a. **Nothing to install** (remote endpoint, no auth, no local subprocess); loud-but-non-fatal if `learn.microsoft.com` is unreachable.
- **New decision-tree knowledge.** `knowledge/grounding-freshness-decision-2026.md` — a Mermaid staleness-diagnosis tree (federated vs SharePoint-index-latency vs deletion-gap vs cadence-cap vs structural-re-architect) plus a freshness-strategy tradeoffs table. Complements PR #315's connector-mode/crawl-strategy trees (which pick the source/mode) by diagnosing *why grounding is stale* and routing the fix; referenced by the connector + DA scenarios.
- **CLAUDE.md** — §8a rewritten from "scenarios TODO" to the live scenarios bank wiring; new §11a (recommend-not-bundle the per-tenant Microsoft Graph / Enterprise MCP) reframing §11; the knowledge-bank table gained the freshness tree; new § "Value-add completeness (build-out 2026-06-05)" disposition table.

### Decisions (recorded, not built)

- **Microsoft Graph MCP / Microsoft MCP Server for Enterprise — recommend-not-bundle.** It is **per-tenant + Entra-authenticated + public-preview** (requires tenant registration + admin-granted MCP scopes), so it cannot ship a hardcoded `mcpServers` entry and is documented as a consumer-configured `claude mcp add` path with a `security-reviewer` gate (CLAUDE.md §11a). No invented servers.
- **LSP — N-A.** LSP is a code-editing protocol; this is an advisory extensibility-design/governance plugin with no single source language to operate on. (A consumer's own DA/plugin project is TS/JSON, but the LSP config belongs in *their* repo / `backend-engineering` / a TS plugin, not here.)
- **Runnable script (`scripts/`) — N-A.** The plugin is advisory + emits artifacts (manifest JSON, OpenAPI, CLI snippets) the engineer runs against their own tenant; there is no tenant-independent calculation with real value (contrast `veterinary-practice`'s `vet_calc.py`). Forcing one would be noise.
- **`bin/` / monitors / output-styles / settings / themes — N-A.** No groundable, broadly-valuable, non-duplicative instance; deliverables are Markdown reports + emitted artifacts governed by the Output Contract.
- **skills / hooks / commands / templates — sufficient.** 5 skills, 1 advisory anti-pattern hook (15 house opinions), 5 commands, 5 templates already cover the surface; the new scenarios + freshness tree + Learn MCP extend reach without a new agent (team-growth-as-knowledge house rule).

### Verify-at-use / unverified

- The Copilot extensibility surface (DA manifest schema version, connector crawl cadence + semantic-index latency windows, plugin-auth scheme support, GCC-High caveats, RSS/RCD behavior, Agent Registry lifecycle) ships ~monthly — every fast-moving fact carries `[verify-at-build]` and a Microsoft Learn source URL. Re-confirm against current Learn docs before relying on a specific version/cadence/window.
- The Learn MCP endpoint (`https://learn.microsoft.com/api/mcp`), its zero-auth/read-only posture, and the `claude mcp add --transport http` flag shape are version-volatile — `[verify-at-use]`.

## [0.4.x] — earlier

6-agent M365 Copilot extensibility & administration team; 9-doc citation-grounded knowledge bank (incl. PR #315's consolidated decision-trees), `best-practices/`, `templates/`, 5 skills, 5 commands, 1 advisory hook (15 house opinions). Seams: Copilot Studio → power-platform; CEA engine → claude-app-engineering; Entra/hosting → azure-cloud; security → ravenclaude-core.
