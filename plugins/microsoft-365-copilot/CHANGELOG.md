# Changelog — microsoft-365-copilot

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.5.3] — 2026-07-01

Research-sweep **refresh** (Tier-A weekly news sweep) — the PAYG-metering hedge's self-declared refresh trigger **fired**. `knowledge/copilot-admin-governance-2026.md` deferred "Pay-as-you-go (PAYG) metering for some agent consumption `[verify-at-build]`" to a future "when PAYG metering … reach GA" trigger; **Copilot Cowork went GA 2026-06-16 with usage-based "Copilot Credits" billing** (also the Work IQ API) — a concrete GA instance of that metering. Verified 2026-07-01 against MS Learn Cowork what's-new + Partner Center June 2026.

### Fixed

- **`knowledge/copilot-admin-governance-2026.md`** — the PAYG line now records Cowork GA 2026-06-16 + Copilot Credits as the live PAYG-metered surface (with inline MS Learn / Partner Center citations); which agents/actions meter which credits stays `[verify-at-build]` as coverage expands. The refresh-trigger list is updated to note PAYG reached GA (Agent 365 split onto its own line, still pending GA). Panels: usefulness → USEFUL; detailed review → APPROVE.
- Version **0.5.2 → 0.5.3** in `.claude-plugin/plugin.json` **and** `marketplace.json` (lockstep). **Migration:** none — knowledge-file content only.

## [0.5.2] — 2026-06-13

Research-sweep **correction** (Tier-A weekly news sweep) — **custom org-built federated connectors are now supported** (the prior "synced only / no custom federated connectors" restriction was lifted). Re-verified this session against the primary source via the Microsoft-Learn MCP: [Set up custom federated connectors](https://learn.microsoft.com/microsoft-365/copilot/connectors/set-up-custom-federated-connectors). Routed through the full panel process — usefulness → USEFUL; detailed review flagged a P0 (the edit overwrote a 2026-06-11-verified "no" with a "yes"), so it was **escalated to a tiebreak panel**, which ruled **APPROVE-WITH-FIX** once the orchestrator re-verified against Microsoft Learn this session; the required fixes (this-session verification marker + `[verify-at-use]` + a `security-reviewer` routing note for the org-operated MCP server) are applied.

### Fixed

- **`knowledge/copilot-connectors-2026.md`** — the federated-connector line stated "**no custom federated connectors** (synced only)"; this is now false. Documented that a custom federated connector starts with an **org-stood-up remote MCP server** exposing **read-only** tools (`search`/`fetch`/`query`, `readOnlyHint`-annotated), auth via **Entra SSO or OAuth 2.0**, created in **Admin Center → Copilot → Connectors → Gallery → "Created by your org"**. Added a mandatory **`ravenclaude-core/security-reviewer` routing note** for the org-operated server's auth/scope/ACL (house opinion #7), a this-session verification marker, and `[verify-at-use]`. Updated the refresh-trigger note.
- Version **0.5.1 → 0.5.2** in `.claude-plugin/plugin.json` **and** `marketplace.json` (lockstep).

## [0.5.1] — 2026-06-11

Research-sweep **correction** — flipped the stale `[verify-at-build]` GA marker on federated/MCP connectors, re-verified 2026-06-11 against `learn.microsoft.com` via the Microsoft-Learn MCP.

### Fixed

- **`knowledge/copilot-connectors-2026.md`** — **Federated (MCP) Copilot connectors are now GA (2026-06-02)** (was tagged `[verify-at-build]` "verify GA status"). Added the verified specifics: GA across **M365 Copilot Chat, the Researcher agent, and Agent Mode in Excel**; admin-managed in **Admin Center → Copilot → Connectors** with a **7-day admin review window** + staged rollout; read-only, Purview-auditable; Microsoft-published or partner-approved; **no custom federated connectors**. Source: [release notes 2026-06-02](https://learn.microsoft.com/microsoft-365/copilot/release-notes#june-2,-2026), [federated connectors overview](https://learn.microsoft.com/microsoft-365/copilot/connectors/federated-connectors-overview).
- Version **0.5.0 → 0.5.1** in `.claude-plugin/plugin.json` + `marketplace.json` (lockstep).

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
