# Google Cloud (GCP) Plugin — Team Constitution

> Team constitution for the `gcp-cloud` Claude Code plugin — **4** specialist agents for designing and operating Google Cloud well — the resource hierarchy and org policy, least-privilege IAM, VPC networking, the right compute (Cloud Run/GKE/Functions), and the data services (BigQuery, Pub/Sub) at a selection level. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`gcp-architect`](agents/gcp-architect.md) | GCP architecture and the resource hierarchy: organization/folders/projects layout, org policy constraints, region/zone design, service selection across the estate, and resilience posture | "design our GCP project structure", "how should we lay out folders/projects", "which GCP services for this", "set org policies" |
| [`gcp-iam-engineer`](agents/gcp-iam-engineer.md) | GCP identity and access: predefined/custom roles over primitive, service accounts + Workload Identity Federation (no key files), Workload Identity for GKE, IAM Conditions, and policy at the right hierarchy level | "write least-privilege GCP IAM", "we're using Owner everywhere", "stop exporting SA key files", "federate CI to GCP" |
| [`gcp-network-engineer`](agents/gcp-network-engineer.md) | GCP networking: VPC and Shared VPC design, firewall rules (default-deny + tags/SAs), Private Google Access, Private Service Connect, Cloud NAT, Cloud Load Balancing, and Cloud DNS | "design our VPC / Shared VPC", "is this firewall rule too open?", "make this private", "connect our projects' networks" |
| [`gcp-data-and-compute-engineer`](agents/gcp-data-and-compute-engineer.md) | Compute selection (Cloud Run / GKE / Cloud Functions / GCE) and the data services at a selection level: BigQuery (as a service), Pub/Sub event-driven integration, Cloud SQL/Spanner/Firestore choice, and autoscaling | "Cloud Run or GKE?", "how should this run on GCP?", "design our Pub/Sub flow", "which database — Cloud SQL, Spanner, Firestore?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Use the resource hierarchy.** Organization → folders → projects is your blast-radius and policy boundary. A pile of unrelated resources in one project is GCP's version of one giant account.
2. **Predefined roles over primitive (Owner/Editor/Viewer).** Primitive roles are wildly over-broad; prefer predefined or custom roles scoped to the job. Owner on a project is rarely the right answer.
3. **No service-account key files.** Use Workload Identity Federation (and Workload Identity for GKE) — exported JSON keys are long-lived secrets that leak. Attach service accounts; don't download keys.
4. **Org policy constraints set guardrails.** Constrain allowed regions, disable SA key creation, enforce no-public-IP — preventive guardrails at the org/folder level beat per-project vigilance.
5. **Private by default.** Private Google Access, Private Service Connect, no public IPs on VMs unless required, firewall default-deny. Public exposure is an exception.
6. **Pick compute by operational burden.** Stateless containers/HTTP → Cloud Run; need k8s → GKE (Autopilot to cut ops); event functions → Cloud Functions; legacy → GCE. Cloud Run is the right default for most services.

## 3. Seams (the bridges to neighbouring plugins)

- **Multi-cloud / which-cloud and AWS/Azure equivalents** → `aws-cloud` / `azure-cloud` (reciprocal); this team owns GCP specifics.
- **BigQuery as the analytics warehouse (modeling, ELT, BI)** → `data-platform` (and `analytics-engineering` for dbt); we own BigQuery as a GCP *service* (IAM, slots, datasets), not the analytics modeling.
- **Provisioning as IaC** → `terraform-iac`.
- **Running on GKE (workload design, mesh)** → `cloud-native-kubernetes`; we own the cluster's GCP control plane + Workload Identity.
- **The security verdict on a posture finding** → `security-engineering/cloud-security-engineer` → `ravenclaude-core/security-reviewer`.
- **CI deploy via Workload Identity Federation to GCP** → `devops-cicd`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/gcp-cloud-decision-trees.md`](knowledge/gcp-cloud-decision-trees.md) (compute selection, data-store selection, hierarchy layout, network connectivity, IAM grant, secret access, network isolation, billing scope + a dated capability map) and [`knowledge/gcp-edge-and-resilience-decision-trees.md`](knowledge/gcp-edge-and-resilience-decision-trees.md) (load-balancer/edge-exposure selection + zonal/regional/multi-region resilience tier). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (service-account key sprawl + over-grant, public GCS bucket exposure, Shared-VPC firewall connectivity, committed-use + right-sizing overspend). Secondary source; never replaces the knowledge bank. The most-likely-to-benefit specialists — `gcp-iam-engineer`, `gcp-network-engineer`, `gcp-architect`, `gcp-data-and-compute-engineer` — check the bank when a situation matches. Scenarios carry no consumer-specific credentials, project IDs, or PII.

## 6. Technical-runtime tier — LSP (N-A) and recommended (not bundled) MCP servers

**LSP code-intelligence — N-A.** LSP is a code-editing protocol for a source language in the consumer's workspace. This plugin operates at the **GCP design / posture / selection** layer (hierarchy, IAM, networking, compute & data-service *selection*) — it authors no source language of its own. Provisioning GCP *as code* is `terraform-iac`'s lane (HCL intelligence belongs there, if anywhere), and application code behind a service is `backend-engineering`'s (which already ships an `.lsp.json`). So there is no GCP-specific language server to wire here; LSP is honestly N-A for this domain, unlike `backend-engineering` where it is genuinely useful.

**Bundled MCP server — N-A (recommend-not-bundle).** Per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a credentialed, per-tenant, or write-capable server is **recommend-not-bundle**. Every GCP-useful MCP server fails the zero-config-read-only bar — they all bind to the consumer's authenticated `gcloud`/ADC credentials and most are write-capable — so we **document the recommended `claude mcp add …` paths** instead of shipping an `mcpServers` entry, and gate any write-capable adoption through `security-reviewer`. No server is invented.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **MCP Toolbox for Databases** (`googleapis/mcp-toolbox`, formerly `genai-toolbox`, Apache-2.0, first-party Google — latest `v1.6.0`, 2026-07-01 `[verify-at-use]`) | **Per-tenant + authenticated** — it connects to the consumer's own Cloud SQL / AlloyDB / Spanner / BigQuery / Bigtable instances using *their* credentials/connection config (a connection string is a secret). Ships **write-capable** generic tools (e.g. `execute_sql`). Both axes disqualify bundling; the secret-handling adds an Absolute-rule "reference-not-literal" + `security-reviewer` gate. | Consumer-configured (download the pinned `toolbox` binary or container, point it at *their* DB with credentials as a **reference**, prefer the read-only/prebuilt tool subset), `security-reviewer` sign-off before adoption. BigQuery-dataset usage is the most likely fit here — but BigQuery *analytics modeling* is `data-platform`'s lane, not ours. |
| **gcloud MCP** (`@google-cloud/gcloud-mcp`, `googleapis/gcloud-mcp`, Apache-2.0, first-party Google — **preview, may break** `[verify-at-use]`) | **Credentialed + write-capable** — "the permissions of the gcloud MCP are directly tied to the permissions of the active gcloud account," and its `run_gcloud_command` tool executes `gcloud` (it blocks some unsafe commands but is *not* read-only). Per-consumer auth + write verbs → never bundle; gate through `security-reviewer`, and prefer **service-account impersonation with a least-privilege role** over the engineer's own broad account. | `claude mcp add gcloud -- npx @google-cloud/gcloud-mcp` after the consumer has installed + authenticated `gcloud`; constrain via impersonation; `security-reviewer` sign-off. Sibling `cloud-run-mcp` / `storage-mcp` / `observability-mcp` carry the same posture. |

**Why none are bundled (the load-bearing reasoning):** both are first-party Google and well-maintained, but each binds to the consumer's authenticated GCP credentials (per-tenant config we can't hardcode) **and** carries write verbs — the doctrine's decision table sends "per-consumer config OR write-capable" straight to **recommend, don't bundle**, and the credential handling makes it an Absolute-rule "reference-not-literal" + `security-reviewer` situation. If a genuinely zero-config, read-only, broadly-useful GCP server ever appears, revisit with the doctrine block in [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4.

> Verified 2026-06-05 via web research: `googleapis/mcp-toolbox` (renamed from `genai-toolbox`, MCP-supporting, latest release `v1.6.0` 2026-07-01 — re-verified 2026-07-08 via [github.com/googleapis/mcp-toolbox releases](https://github.com/googleapis/mcp-toolbox/releases/tag/v1.6.0), Apache-2.0, write-capable generic tools, multi-DB incl. BigQuery), and `googleapis/gcloud-mcp` (`@google-cloud/gcloud-mcp`, Apache-2.0, preview, write-capable `run_gcloud_command`, permissions tied to the active gcloud account). Package names, versions, preview/GA status, and read/write surface are version-volatile — re-confirm against the vendor before quoting. Sources: github.com/googleapis/mcp-toolbox, cloud.google.com MCP-Toolbox blog, github.com/googleapis/gcloud-mcp, docs.cloud.google.com/run/docs/use-cloud-run-mcp.

## 7. Value-add completeness (build-out 2026-06-05)

This is a **CLOUD/infra** domain, so the technical-runtime tier genuinely applies and is dispositioned honestly below (built vs. recorded N-A with reason). PR #315 had already landed the consolidated knowledge decision-trees, `best-practices/`, and `templates/`; this build-out closed the net-new gaps (the scenarios bank + runtime-tier dispositioning) and added one complementary topic-specific decision-tree file.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 dated, scope-tagged field notes matching the existing `scenarios/README.md` index + 9-field schema: SA key sprawl + over-grant (IAM), public GCS bucket exposure (data exposure), Shared-VPC firewall connectivity (networking), committed-use + right-sizing overspend (cost/FinOps). The README already indexed all four; two existed on disk pre-build-out, two were the net-new gap and are now written. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/gcp-edge-and-resilience-decision-trees.md`: two NEW Mermaid trees (load-balancer/edge-exposure selection; zonal/regional/multi-region resilience tier) **complementing** PR #315's `gcp-cloud-decision-trees.md` (which already covers compute & data-store selection, hierarchy, networking, IAM, secrets, network isolation, billing). Grounded + dated + capability map; no overlap with the existing file. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §6. Real published first-party Google servers exist (MCP Toolbox for Databases; gcloud MCP) but both are credentialed/per-tenant + write-capable, so they fail the zero-config-read-only bar. Documented the recommended `claude mcp add …` paths with reference-credential + `security-reviewer` gates. No invented servers/versions. |
| 4 | **LSP server** | **N-A** — §6. No GCP-specific source language to wire; provisioning-as-code is `terraform-iac`'s lane, app code is `backend-engineering`'s. Honestly N-A for a design/posture/selection domain. |
| 5 | **Runnable script (`scripts/`)** | **N-A** — the high-value cost arithmetic this plugin touches (right-sizing, committed-use, budget thresholds) is **entirely consumer-data- and price-dependent**, and the repo's accuracy rule forbids baking in volatile prices. A calculator with no baked prices would just echo the user's own inputs — no real value-add over the decision trees + the `label-everything` / `budget-alerts` best-practices, which route the user to *their own* billing-export-to-BigQuery data. Built nothing rather than ship a no-value stub. |
| 6 | **bin/ · monitors · output-styles · settings · themes** | **N-A** — no `rc-*` binary clears the "namespace + prefer Bash-tool skills" bar over the existing advisory hook + skills; nothing to watch (no build/repo/long-running process in an advisory design domain); output styling is a code/UX concern (deliverables are Markdown governed by the agents' Output Contract); no tool-permission surface beyond what `ravenclaude-core` + the comfort-posture system already provide. |
| 7 | **skills / hooks / commands / templates** | **SUFFICIENT** — 5 skills (compute-selection, cost-governance, least-privilege-IAM, private-networking, resource-hierarchy), 1 advisory anti-pattern hook, 4 commands, 4 templates, 30 best-practices already cover the surface. The new decision-tree file + scenarios extend reach without a new agent (team-growth-as-knowledge house rule). No obvious high-value gap this round. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled — the MCP servers are *recommended*, not vendored). |

## 8. Milestones

- **v0.2.x** — initial GCP team + PR #315 consolidation: 4 agents, 5 skills, 4 templates, 4 commands, 1 advisory hook, the `gcp-cloud-decision-trees.md` knowledge bank (8 trees + dated capability map), 30 best-practices, and the first 2 scenarios + scenarios README.
- **v0.3.0** — CLOUD-domain value-add build-out: completed the scenarios bank to the 4 the README indexes (added Shared-VPC firewall + committed-use/right-sizing), added `knowledge/gcp-edge-and-resilience-decision-trees.md` (load-balancer + resilience-tier trees), dispositioned the full runtime tier (LSP N-A; MCP recommend-not-bundle with researched first-party servers; script N-A — no baked prices), and added the CHANGELOG + value-add completeness table.
