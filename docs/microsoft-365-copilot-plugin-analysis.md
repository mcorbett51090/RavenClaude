# Microsoft 365 Copilot — plugin analysis + buildout plan

**Date:** 2026-05-30
**Status:** Decision + research synthesis + v0.1.0 scope. Grounding: first-party Microsoft Learn, retrieved 2026-05-30 (URLs inline in the knowledge bank as built). Schema/preview-gated facts are flagged for the Researcher sweep.

---

## 0. TL;DR

Ship a new **`microsoft-365-copilot`** plugin — a specialist team for the **Microsoft 365 Copilot extensibility & administration** surface: declarative agents, custom-engine agents, Copilot (Graph) connectors, API plugins, the M365 Agents SDK/Toolkit, the app-package publish lifecycle, and the M365-admin-center + Purview governance layer. It is **disjoint** from the existing `power-platform` Copilot Studio coverage (low-code, Dataverse-backed, Power Platform admin center) and carries operational craft a generalist lacks (the declarative-agent hard-limit wall, manifest/RAI validation, connector ACL/semantic-label hygiene, Entra/OAuth API-plugin auth, Purview oversharing remediation).

## 1. Architecture decision — new plugin vs. expand `power-platform`

**New plugin. YES.** The decisive cut, grounded in Microsoft's own three-way agent framing:

| Build path | Owner |
|---|---|
| **Declarative agent / Copilot extensibility SDK / Graph connectors / M365 publish + govern** | **microsoft-365-copilot** (new) |
| **Copilot Studio low-code maker / Dataverse-backed / Power Platform ALM + DLP** | **power-platform** (existing `copilot-studio-engineer`) |
| **Custom-engine agent's engine on Claude (orchestrator/evals/caching)** | **claude-app-engineering** |
| **Entra app regs/consent + hosting a CEA (Foundry/Container Apps)** | **azure-cloud** |

Folding this into `power-platform` would violate that plugin's Dataverse/maker identity and bloat its 11-agent roster with a non-Dataverse concern. The house-rule test ("could a core agent + skill + knowledge produce indistinguishable output?") **fails** for the connector-ACL, manifest-limit-math, and Purview-governance work → ship agents. The governance slice (M365 admin center Agent Registry, Purview DLP-for-Copilot, Restricted SharePoint Search, data residency) is disjoint from power-platform's PP-admin-center scope and cannot be a skill on `power-platform-admin`.

## 2. The surface (research synthesis, 2026)

- **Two agent shapes:** **declarative agent** (your instructions+knowledge+actions on *Copilot's* orchestrator/models; no hosting; inherits M365 compliance) vs **custom-engine agent** (you bring orchestrator+models+hosting; proactive/autonomous; off-M365 channels).
- **Declarative-agent hard limits** (the load-bearing wall): grounding **50 items**, plugin response **25 items**, **~4,096** tokens, **45 s** timeout — *all inclusive of overhead; optimize to ~66%* — and **single grounding op + single tool call, sequential, NO loops.** Hitting iterative reasoning forces a custom-engine agent.
- **Manifest** schema ships ~monthly (latest verified v1.7); pin the version.
- **Grounding:** synced Copilot connector (index into Graph, semantic ranking, honors ACLs) vs federated connector (real-time over **MCP**, no index) vs SharePoint/OneDrive knowledge (license-gated) vs API plugin (OpenAPI; real-time fetch *or transactional action*).
- **Build tools:** Agent Builder (no-code) → SharePoint (no-code, not org-publishable) → Copilot Studio (low-code → power-platform) → **Agents Toolkit** (`atk`, pro-code, Playground, CI/CD, the M365 Agents SDK — Bot Framework's successor).
- **Agents are apps:** ship as an M365 app package; publish = sideload → org catalog (**admin-approved**) → AppSource. RAI validation runs on sideload/publish.
- **Governance:** M365 admin center **Agent Registry** (AI-Admin/Global-Admin approves); MCP tools need separate tenant consent; **Purview DLP-for-Copilot** (E5/Suite-gated; citations still leak titles); **Restricted SharePoint Search / Restricted Content Discovery are NOT security boundaries**; PDL-driven data residency.

## 3. Plugin scope (v0.1.0)

### 3.1 Roster — 6 agents (per the house rule; do not exceed 7)

| Agent | Mission |
|---|---|
| `copilot-extensibility-architect` | Routing brain: DA vs CEA vs Copilot-Studio; grounding-source choice; "will this hit the 50-item/45s/no-loop wall?"; channel + publish path |
| `declarative-agent-engineer` | Authors/reviews DA manifests (pinned schema), instructions, capabilities, conversation starters; Agent Builder vs Agents Toolkit; manifest + RAI validation; API actions |
| `graph-connector-engineer` | Synced vs federated (MCP) Copilot connectors; schema + semantic labels; ACL ingestion/trimming; semantic-index latency; connector SDK/Graph APIs |
| `api-plugin-engineer` | API plugins/actions from OpenAPI; plugin-manifest↔`operationId` mapping; Entra/OAuth2/API-key auth; GCC-High caveat |
| `agents-sdk-engineer` | Custom-engine agents on the M365 Agents SDK/Teams SDK: channel/turn/state, streaming/citations, DA→CEA conversion, multi-channel publish |
| `copilot-admin-governance` | Agent Registry lifecycle, agent + MCP-tool approval, licensing/PAYG, Purview DLP + sensitivity labels for Copilot, Restricted SharePoint Search/RCD, data residency — **the plugin's reason to exist** |

Security design (connector ACLs, API-plugin auth, prompt-injection over ingested content) **escalates to `ravenclaude-core/security-reviewer`** (mirrors every other domain plugin).

### 3.2 Knowledge bank — 9 docs (citation-grounded; ✦ = Mermaid decision tree)

1. `agent-platform-decision-2026.md` ✦ — DA vs CEA vs Copilot-Studio, with explicit seams; cross-links `power-platform/knowledge/copilot-agents-2026.md`.
2. `declarative-agent-manifest-2026.md` — schema capability map + the hard limits (50/25/4096/45s, sequential no-loop) + version-pin discipline.
3. `grounding-source-decision-2026.md` ✦ — synced/federated connector vs SharePoint knowledge vs API plugin; semantic-index latency + license gating.
4. `copilot-connectors-2026.md` — schema, semantic labels, ACL ingestion/trimming, connector SDK/Graph APIs, prebuilt gallery.
5. `api-plugins-and-auth-2026.md` — four-file architecture, OpenAPI-for-Copilot constraints, Entra/OAuth2/API-key, GCC-High caveat.
6. `agents-sdk-and-toolkit-2026.md` — M365 Agents SDK (Bot-Framework lineage), Agents Toolkit/`atk`, Playground, DA→CEA conversion.
7. `copilot-admin-governance-2026.md` — Agent Registry lifecycle, AI-Admin/Global-Admin gates, MCP-tool approval, licensing/PAYG, Agent 365 pointer.
8. `copilot-security-purview-2026.md` — Purview DLP-for-Copilot (E5/Suite gate, citation leakage, EXTRACT right), sensitivity-label inheritance, oversharing remediation sequence (RCD→RSS→Purview→disable), "not a security boundary."
9. `data-residency-and-compliance-2026.md` — PDL-driven residency, ADR/Multi-Geo, EU Data Boundary, audit/eDiscovery/retention.

### 3.3 Skills (~5) + templates (~5) + hook

- Skills: `declarative-agent-manifest-authoring`, `copilot-connector-schema-design`, `api-plugin-openapi-hygiene`, `oversharing-remediation-playbook`, `copilot-agent-eval-harness`.
- Templates: declarative-agent manifest skeleton, Copilot-connector schema, API-plugin (plugin-manifest + OpenAPI) pair, agent app-package checklist, oversharing-remediation runbook.
- 1 advisory `flag-copilot-anti-patterns.sh` hook enforcing the grep-able house opinions.

### 3.4 House opinions (15 stances; the hook flags the grep-able ones)

DA-first/CEA-only-when-forced · pin the manifest schema version · optimize to ~66% of every hard limit · synced-connector-for-scale / federated-for-realtime / API-plugin-for-actions · semantic labels mandatory · connector ACLs are a security control (→ security-reviewer) · no org-data grounding without a license story ("Licensing impact:" line) · RSS/RCD are not security boundaries · remediate oversharing before enabling Copilot · DLP blocks processing not citation · every agent ships as a validated app package · org-catalog publish is admin-gated · source-control the project, sideload for dev · the Claude engine / Azure host / Copilot-Studio path are other plugins' jobs · no DA without a golden-prompt regression set.

### 3.5 Cross-plugin seams

power-platform (Copilot Studio boundary — cross-link, don't duplicate) · claude-app-engineering (CEA engine on Claude) · azure-cloud (Entra + CEA hosting) · ravenclaude-core (security-reviewer, architect, deep-researcher) · microsoft-fabric (Fabric/OneLake data surfaced via a connector).

## 4. Risks / open questions

- Overlap *perception* with power-platform — mitigated by the sharp Copilot-Studio-low-code vs M365-surface line + a shared decision-tree doc cross-linked from both.
- Schema/feature velocity (monthly manifest) — budget the Researcher sweep; pin versions.
- **Agent 365 / Agent 365 SDK** (Entra agent identity + governed MCP) is emerging — track, don't over-invest until GA [unverified this session].
- Preview-gated features (Copilot Retrieval API, remote SharePoint knowledge) — flag preview status in docs.

## 5. v0.1.0 scope (summary)

6 agents · 9-doc citation-grounded knowledge bank (2 Mermaid decision trees) · 5 skills · 5 templates · 1 advisory hook (15 house opinions) · seams wired (Copilot-Studio→power-platform, Claude engine→claude-app-engineering, Entra/host→azure-cloud, security→ravenclaude-core) · requires `ravenclaude-core@>=0.7.0` · core stays domain-neutral. Ships as its own PR with full audit-gates + frontmatter schema on every agent + repo-guide regen.
