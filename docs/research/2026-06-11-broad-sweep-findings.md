# Broad research sweep — findings & triage (2026-06-11)

A breadth sweep across the Tier-A (news-cadence) clusters, run after the focused Claude/AI-coding sweep that produced PR #408. Four parallel research agents covered the Microsoft stack, the Claude/AI cluster, cloud/DevOps/IaC, and data/AI. This file is the **triaged record** of everything found — what shipped, what's queued — and is the feed for the retuned weekly news cadence (`docs/research-routine-two-cadence.md`).

**Triage key:** **CORRECTION** = the repo currently states something now-false (ship first). **ADDITION** = a new capability not yet documented (queue). Confidence + source per item; every dated fact carries `[verify-at-use]` when written into a knowledge file.

## Shipped

- **PR #408** (merged) — claude-app-engineering + ai-coding-model-guidance: refusal-billing + server-side classifier fallback, Managed Agents cron/vaults, Foundry Fable-5 caveat.
- **This PR** — Microsoft-stack CORRECTIONS (self-re-verified via the Microsoft-Learn MCP):
  - microsoft-fabric: Runtime 2.0 = **Spark 4.1 / Delta 4.1 / Python 3.13** (was 4.0); OneLake security + data access roles **GA + default-on** (was "preview") + authorized-engine model + ReadWrite.
  - microsoft-365-copilot: Federated (MCP) connectors **GA 2026-06-02** (was `[verify-at-build]`).

## Queued — verified findings not yet built

Each was returned by a research agent with a primary/authoritative source. **Re-verify against the cited primary before writing into a knowledge file** (the agents flagged several as `[verify-at-use]` where they read a search snippet rather than fetching the primary). Grouped by plugin; **C** = correction, **A** = addition.

### microsoft-fabric
- **A** — **Fabric Graph** reached GA (June 2026); no coverage in the capability map. Source: `learn.microsoft.com/fabric/graph/overview` + Fabric what's-new.
- **A** — **Copy job native CDC for the SQL estate** (Azure SQL DB / SQL Server / Azure SQL MI) GA (June 2026); **Eventstream Kafka + Azure Service Bus** connectors GA (June 2026). Removes the "needs separate change-tracking infra" caveat in the data-movement tree. Source: Fabric what's-new (verified — both appear in the June-2026 GA table).
- **C/A** — `onelake-security-and-governance.md` (the dedicated security doc) still carries the pre-GA "preview" matrix + "third-party engines preview"; bring it in line with the capability-map correction shipped in this PR (GA + default-on + authorized-engine model + supported-items list). Also CLAUDE.md §3 #14 ("prerequisite for OneLake-security data preview") is now stale.

### microsoft-365-copilot
- **A** — **Fabric Data Agents** discoverable/chat-able inside M365 Copilot, GA (June 2026). Source: `learn.microsoft.com/fabric/data-science/concept-data-agent` + Fabric what's-new. (Cross-plugin with Fabric.)
- **A** — **Policy-based rules for agent lifecycle** (bulk-install 1P agents, auto-reassign ownerless agents), 2026-06-02. Source: M365 Copilot release notes (verified). Add to `copilot-admin-governance-2026.md`.

### microsoft-graph
- **A** — `agentUser` resource + `verifiedIdProfile` resources GA in v1.0 (May 2026); `agentIdentity` blueprint/risk model in beta. Source: `learn.microsoft.com/graph/whats-new-overview`.
- **A** — **Programmatic FIDO2 passkey registration** GA (June 2026): `fido2AuthenticationMethod: creationOptions` → POST `publicKeyCredential`. Source: Graph what's-new.
- **A** (low) — `ownerlessGroupPolicy` resource added to v1.0 (May 2026).

### claude-app-engineering
- **A** (high value) — the **advisor tool** (beta `advisor-tool-2026-03-01`) is entirely absent from the knowledge bank: executor/advisor pairing, `max_tokens`/`max_uses`/`caching` cost controls, API + Claude-Platform-on-AWS only (not Bedrock/Vertex/Foundry). Add to `server-side-tools-and-files.md` + a capability-map row. Source: `platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool` (agent read the full doc).
- **A** — **Claude for Foundation Models** Swift package (`ClaudeForFoundationModels`) — a new Apple-platform build surface (iOS/iPadOS/macOS/visionOS/watchOS 27); Xcode 27 integrates the Agent SDK. Add to the build-surface material. Source: `claude.com/blog/claude-for-foundation-models` + `platform.claude.com/docs/en/cli-sdks-libraries/libraries/apple-foundation-models`. `[verify-at-use — developer beta, package-name spelling]`
- **(low fit)** — Enterprise admin permissions in custom roles: verified but a product/admin-console feature, not an API/build capability — likely out of scope.

### ravenclaude-core
- **A** — Claude Code changelog cluster: **`disallowed-tools` in skill/slash-command frontmatter** (a new permission lever directly relevant to marketplace skill authoring) and the **`post-session` lifecycle hook**. Source: `code.claude.com/docs/en/changelog`. `[verify-at-use — exact version numbers (2.1.169 / 2.1.152) via the live changelog]`

### analytics-engineering
- **C** — anchors on **dbt Core v1.8**; current context is **dbt Core v2.0 in ALPHA** (Rust engine; Apache-2.0) with **v1.x remaining the production default** — and the Fusion + Snowflake connection path GA. **Anti-fabrication guard: write "v2.0 alpha", NOT "v2.0 GA"** (secondary coverage gets this wrong; the dbt-core GitHub roadmap is the primary). Source: `github.com/dbt-labs/dbt-core/blob/main/docs/roadmap/2026-06-announcing-v2.md`.

### tableau
- **A** — **Tableau 2026.2** (Desktop GA 2026-06-09): Agentic Analytics Platform, "Tableau Agent in Dashboards" (beta/pilot late July — keep out of GA recs), **Hosted Tableau MCP for Tableau Cloud** (GA late June, OAuth 2.1). Refresh the "Next-gen surface" tree. Source: `tableau.com/support/releases/desktop/2026.2` (search snippets — `[verify-at-use]`, 403 blocked direct fetch).

### data-platform
- **A** (medium) — Snowflake **Iceberg v3 GA** at Summit 2026 + Snowflake-managed Iceberg storage. Lower priority for the SMB-consulting framing. Source: Snowflake press release (snippet — `[verify-at-use]`).

### cloud-native-kubernetes
- **C/A** — capability map has **no Kubernetes version anchor**; add: current GA **1.36** (2026-04-22); **DRA GA since 1.34**; **cgroup v1 removed in 1.35** (nodes must be cgroup v2); **User Namespaces GA in 1.36**; **containerd 1.x phase-out** (verify the exact min-version pin). Sources: kubernetes.io release blogs (1.34 DRA, 1.36 release, UserNS GA verified; cgroup-v1/containerd pins `[verify-at-use]`).

### terraform-iac
- **C** — "Last verified … against **OpenTofu 1.8**" stamp is stale; current GA is **1.12.x** (1.12.0 2026-05-14, 1.12.1 2026-05-27). Source: `github.com/opentofu/opentofu/releases`.
- **A** — **OCI-registry distribution for modules AND providers** (since OpenTofu 1.10) — not in the module-registry tree. (Native S3 locking is **already** documented — not net-new.) Source: `opentofu.org/docs/cli/oci_registries/`.

### azure-cloud
- **A** (medium) — **AKS Azure Linux 2.0 retirement**: security updates ended 2025-11-30; node images removed 2026-03-31 — frame as "ensure migrated to AzureLinux3." Source: Microsoft Learn (AKS retirement callout + Azure/AKS#4988).

## Verified-but-NOT-counted (honest nulls + off-altitude)

These were checked and deliberately **not** turned into findings — recording them so a later sweep does not re-chase them:

- **aws-cloud, gcp-cloud, devops-cicd, finops-cloud-cost, ml-engineering, database-engineering, data-streaming-engineering, ai-coding-model-guidance, ai-rag-engineering, power-platform** — **0 net-new** in-window. New AWS services (Graviton5/M9g, S3 Vectors, AWS MCP GA) don't change documented guidance; OTel declarative-config-stable is real but off the SRE plugin's altitude; ml-engineering's Databricks Summit is **2026-06-15..18 (after today)** — re-check after the 18th.
- **Pre-existing staleness, NOT a last-2-weeks finding** (flagged for a deeper freshness pass, not this sweep): data-streaming-engineering anchors on **Flink 1.19 / Kafka Streams 3.7** (Flink 2.x / Kafka 4.0 shipped Mar 2025); database-engineering's generic "PostgreSQL current major" predates **PG18** (GA 2025-09-25). These are version-anchor rot, not news.

## Notes for the next sweep
- Re-verify each queued item against its primary before writing (several rest on search snippets where vendor docs 403'd direct fetch — dbt-core roadmap, tableau.com, snowflake.com).
- The clearest CORRECTIONS still open: analytics-engineering (dbt v1.8→v2.0-alpha), terraform-iac (OpenTofu 1.8→1.12), cloud-native-kubernetes (no version anchor). Prioritize these — they actively mislead.
- Highest-value ADDITION: claude-app-engineering advisor tool (a whole tool absent from the bank).
