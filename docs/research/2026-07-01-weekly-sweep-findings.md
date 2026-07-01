# Weekly news-cadence sweep — findings, panels & triage (2026-07-01)

A Tier-A weekly news-cadence sweep per [`docs/research-routine-two-cadence.md`](../research-routine-two-cadence.md). Five parallel research agents covered the Tier-A clusters (Microsoft stack · cloud/infra · data/BI · AI-Claude-web · security). Every candidate was **grounded against the actual repo text** before counting — the step that dissolved most — and the survivors were routed through two expert panels (usefulness → detailed review). Both panels concurred on all three survivors, so no tiebreak panel was convened.

**Triage key:** **CORRECTION** = the repo currently states something now-false/stale (ship first). **REFRESH** = a self-declared refresh trigger has fired (record the concrete instance). **ADDITION** = a new capability not yet documented (queue). **EVAPORATED** = did not survive repo-grounding. **NULL** = checked, nothing in-window.

## What shipped this run (built + panel-reviewed)

Three findings, all knowledge-file freshness corrections/refreshes (patch bumps, mirrors in lockstep, CHANGELOG entries, no consumer migration):

### A — CORRECTION (highest priority): Fable 5 / Mythos 5 export controls LIFTED 2026-06-30
The US Dept of Commerce / BIS **withdrew** the 2026-06-12 export-control directive that had suspended **Claude Fable 5** (`claude-fable-5`) and **Mythos 5** worldwide; Anthropic said it would **begin restoring access 2026-07-01**. The repo pinned "SUSPENDED … disabled worldwide" as a **current-status** fact across two Tier-A plugins — actively misleading (it told a router "uncallable worldwide" and stamped the suspension "re-verified still-active 2026-06-22"). Flipped **every carried location** to "controls lifted / access restoring — re-verify per-surface callability before routing; interim route to Opus 4.8 until your surface confirms restored," with the fluid `[verify-at-use]` hedge retained (restoration is in progress, not yet independently confirmed complete on every surface). Safety-fallback / billing mechanics untouched.

Full fan-out (the #1 partial-flip risk Panel 1 flagged — done in all locations):
- **claude-app-engineering** `knowledge/model-selection-and-2026-capability-map.md` — banner, Fable 5 lineup row, Mythos 5 note, routing ladder, capability-status row, advisor-tool pairing, `Last reviewed` (→ **0.9.6**).
- **ai-coding-model-guidance** `knowledge/cross-tool-model-lineup-2026.md` — header `Last reviewed`, coding-agent table row, Fable 5 Copilot bullet, free-window parenthetical, + a new **2026-07-01 sweep note** superseding the older dated "remains suspended" notes (kept as historical record) (→ **0.3.9**).
- **ravenclaude-core** `knowledge/orchestrator-data-egress.md` — the ZDR aside (ZDR-ineligibility fact unchanged) (→ **0.182.1**). `CHANGELOG.md:187` (a dated historical changelog entry) intentionally left as-is.

Primary: [Anthropic statement](https://www.anthropic.com/news/fable-mythos-access) + Anthropic's 2026-06-30 restoration notice; corroborated by [CNBC (2026-06-30)](https://www.cnbc.com/2026/06/30/anthropic-says-trump-admin-has-lifted-export-controls-on-claude-fable-5-and-mythos-5.html), Fox Business, Axios. anthropic.com 403s automated fetch → cross-referenced secondaries (the repo's accepted pattern); the primary tweet + CNBC verified this session via `WebSearch`.

### B — REFRESH: microsoft-365-copilot PAYG-metering trigger fired
`knowledge/copilot-admin-governance-2026.md` deferred "PAYG metering for some agent consumption `[verify-at-build]`" to a future "when PAYG metering … reach GA" refresh trigger. That trigger **fired**: **Copilot Cowork went GA 2026-06-16 with usage-based "Copilot Credits" billing** (also the Work IQ API). Recorded Cowork GA + Copilot Credits as the live PAYG-metered surface (which agents/actions meter which credits stays `[verify-at-build]` as coverage expands), added inline MS Learn / Partner Center citations, and updated the refresh-trigger list. (→ **microsoft-365-copilot 0.5.3**.) Primary: MS Learn [Cowork what's-new](https://learn.microsoft.com/microsoft-365/copilot/cowork/whats-new) + [Partner Center June 2026](https://learn.microsoft.com/partner-center/announcements/2026-june).

### C — CORRECTION: analytics-engineering dbt Fusion scope understated
`knowledge/analytics-engineering-decision-trees.md` said "Fusion engine **Stable** for new envs." Per docs.getdbt.com (about-fusion), the Fusion engine is **GA for dbt-platform projects on Snowflake and in preview for other adapters** (BigQuery/Redshift/Databricks) — materially narrower than an unqualified "Stable" (an engineer on a non-Snowflake adapter could adopt Fusion into a new env expecting production readiness that only exists on the Snowflake path). Corrected both occurrences (`:145` prose + `:224` capability-map row) + re-stamped `[verify-at-use 2026-07-01]`. The **"dbt Core v2.0 in alpha — not GA"** clause is preserved (still true). (→ **analytics-engineering 0.3.3**.)

## Panels
- **Panel 1 (usefulness)** — 3 seats (production-consumer engineer · marketplace knowledge-curator · SMB-fit skeptic). **All three USEFUL.** A high (banner-level now-false, ~8 locations), C high (mis-stated scope in a decision-tree file), B med-high (a legitimately fired self-declared trigger, cheap to close). Binding note: A must flip **every** carried location or none (partial flip → self-contradicting file, worse than consistent-but-stale).
- **Panel 2 (detailed review)** — 3 seats (technical-correctness · accuracy/citation · editorial-fit). **APPROVE on all three, no blocking changes.** Confirmed no surviving "suspended = current" line, honest in-progress hedging, no over-claim, safety-fallback/billing mechanics untouched, v2.0-alpha clause preserved. One optional advisory (add an inline MS Learn URL to Finding B) — **applied.**
- **Tiebreak** — not triggered (both panels concurred).

## EVAPORATED / already-built (recorded so a later sweep doesn't re-chase)
- **microsoft-graph** — FIDO2 self-service registration GA (an Entra Registration-Campaign feature, not a Graph API — the plugin correctly documents the *programmatic app-on-behalf* Graph surface); fileStorageContainer 10→40 and alert `category→categories` **not pinned** in repo. All evaporate.
- **microsoft-fabric** — Fabric Graph GA / Eventstream Kafka-still-preview / Data-Agents-in-M365 GA-vs-preview split all **already documented** (2026-06-19 sweep) and still accurate. Fabric AI-functions default model (`gpt-5-mini`) is an unpinned ADDITION, low priority.
- **microsoft-365-copilot** — Copilot Cowork itself is an undocumented ADDITION (a stub could be queued); "policy-based agent-lifecycle rules" not isolable as a distinct primary-verified feature beyond existing Agent Registry content.
- **tableau** — hosted/managed Tableau MCP + "Tableau Agent in Dashboards = Beta/Pilot, NOT GA" are real but the plugin **pins no MCP GA state** (recommend-not-bundle self-hosted block only) → nothing false to correct; genuine ADDITION candidate, queued.
- **cloud/infra** — k8s 1.36 / OpenTofu ≥1.10 / OTel Profiles Alpha / Backstage-not-pinned / Azure AI Inference beta-SDK-retirement-2026-08-26 all current or already hedged. Patch churn (k8s 1.36.x, OpenTofu 1.12.3, Prometheus/Grafana/Backstage patches) deliberately **not counted** — anchors already current.
- **data/BI** — Flink 2.x/Kafka 4.x + PG18 anchors (2026-06-22) not regressed; Snowflake Iceberg v3 not pinned.
- **security** — auth-identity OAuth 2.1 still draft / WebAuthn L3 still CR / NIST 800-63B-4 date correct; security-engineering OWASP Top-10:2025 + CVSS v4.0 current; cybersecurity-grc frameworks current. **Clean NULL.**

## Queued — verified ADDITIONS not built this run (need their own primary re-verify + panel pass)
- **tableau** — document the hosted/managed Tableau MCP (`mcp.tableau.com`, OAuth) + the load-bearing "Tableau Agent in Dashboards = Beta/Pilot, not GA" caveat.
- **microsoft-365-copilot** — a Copilot Cowork knowledge stub (GA, model picker incl. Claude Opus 4.8, usage-based billing, Purview governance).
- **microsoft-fabric** — AI-functions default model (`gpt-5-mini` default / `gpt-5.1` supported) if the plugin decides to pin a model default.
- **ravenclaude-core** — Claude Code changelog: `post-session` lifecycle hook (v2.1.169) + `disallowed-tools`/skill-frontmatter (v2.1.152) are absent from `knowledge/claude-code-permissions.md` (the right home) — a marketplace-authoring-relevant ADDITION carried from 2026-06-22.

## Honest nulls (checked, nothing actionable in-window)
- **security cluster** (security-engineering, cybersecurity-grc, auth-identity) — 0 net-new; standards move slowly and are already hedged.
- **cloud/infra cluster** — 0 corrections; every anchor current or hedged.
- **ai-rag-engineering / ml-engineering / web-design / frontend-engineering** — 0 primary-verified in-window deltas that falsify a pinned fact.
- **power-platform, data-platform, database-engineering, data-streaming-engineering, analytics-engineering (beyond Finding C)** — no further dated-fact drift.
