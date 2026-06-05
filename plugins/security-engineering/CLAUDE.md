# Security Engineering (AppSec) Plugin — Team Constitution

> Team constitution for the `security-engineering` Claude Code plugin — **4** specialist agents for building security into software — threat modeling, application security testing (SAST/DAST/SCA), secrets management, software supply-chain integrity, and cloud security posture. It proposes; ravenclaude-core/security-reviewer holds the verdict. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`appsec-engineer`](agents/appsec-engineer.md) | Application security testing and the AppSec program: SAST/DAST/IAST/SCA in CI, OWASP Top 10 (web), vulnerability triage by exploitability, secure-coding guidance, security gates in the pipeline | "set up SAST/SCA", "triage these scan findings", "is this code injectable?", "add a security gate to CI" |
| [`threat-modeler`](agents/threat-modeler.md) | Threat modeling: data-flow diagrams, trust boundaries, STRIDE per element, attack trees, ranking threats by likelihood × impact, and mapping each to a mitigation or an accepted risk | "threat model this feature", "what could go wrong with this design?", "do a STRIDE analysis", "where are our trust boundaries?" |
| [`supply-chain-security-engineer`](agents/supply-chain-security-engineer.md) | Software supply-chain integrity from the consume side: SBOM ingestion and dependency inventory, CVE triage and patching strategy, dependency pinning and update policy, SLSA provenance verification, typosquat/malicious-package defense | "are our dependencies safe?", "triage this CVE", "verify build provenance", "how do we handle dependency updates safely" |
| [`cloud-security-engineer`](agents/cloud-security-engineer.md) | Cloud security posture: CSPM-style misconfiguration detection, IAM least-privilege analysis, network exposure (public buckets, open security groups), encryption-at-rest/in-transit, and guardrails (policy-as-code) | "audit our cloud security", "is this S3 bucket / storage public?", "tighten these IAM permissions", "add security guardrails" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Security engineering proposes; it does not pronounce the verdict.** The ship/no-ship call on a finding is `ravenclaude-core/security-reviewer`'s. This team finds, models, and fixes — it routes the decision.
2. **Shift left, but don't shift the verdict.** Catch issues in design (threat model) and CI (SAST/SCA), not in pen-test the week before launch. Cheaper, earlier, and the fix is still cheap.
3. **Least privilege is the default, always.** Every identity, token, and role starts with nothing and earns each grant. A wildcard permission is a finding.
4. **Secrets never live in code, config, or logs.** Detect them, vault them, rotate them, and federate with short-lived credentials. A committed secret is compromised — rotate, don't just delete.
5. **You can't secure what you can't enumerate.** An SBOM and an asset/dataflow inventory precede any real assessment. Unknown dependencies are unpatched CVEs waiting.
6. **Defense in depth, but fix the front door first.** Layered controls are good; an unauthenticated public endpoint with a SQL injection is not a 'layer' problem — triage by exploitability and blast radius.

## 3. Seams (the bridges to neighbouring plugins)

- **The ship/no-ship VERDICT on any finding** → `ravenclaude-core/security-reviewer` (mandatory). This team produces the evidence and the recommended control; the verdict is not ours.
- **API-specific authorization flaws (BOLA/BOPLA/BFLA) and the OWASP API Top 10** → `api-engineering/api-security-engineer` owns that craft; we cover web OWASP + the cross-cutting program.
- **End-user authentication, OAuth/OIDC flows, session/token storage** → `auth-identity`; we threat-model the design, they implement it.
- **Data privacy, PII handling, GDPR/CCPA mechanics, DLP** → `data-governance-privacy`.
- **The artifact-side SBOM/provenance *production*** → `devops-cicd/build-and-artifact-engineer`; we *consume and verify* it.
- **Cloud IAM/network primitives** → `azure-cloud`/`aws-cloud`/`gcp-cloud`; we assess the posture across them.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer):
  - [`knowledge/security-engineering-decision-trees.md`](knowledge/security-engineering-decision-trees.md) — the consolidated bank (vuln-triage priority, secret-found, shift-left placement, auth-vs-authz, patch-now-vs-schedule, emergency-vs-scheduled dependency update, secret-in-repo response, cloud-misconfig preventive-vs-reactive) + a dated capability map.
  - [`knowledge/vulnerability-severity-vs-risk-decision-tree.md`](knowledge/vulnerability-severity-vs-risk-decision-tree.md) — **Mermaid** — CVSS base → reachability/exposure/auth/KEV context → **risk band + proposed SLA**. Makes the "CVSS-in-the-abstract → risk-in-your-deployment" translation explicit, grounded in CVSS v4.0 metric groups, CISA KEV, SSVC, EPSS, BOD 22-01.
  - [`knowledge/sast-dast-sca-scanner-selection-decision-tree.md`](knowledge/sast-dast-sca-scanner-selection-decision-tree.md) — **Mermaid** — which **scanner class** (SAST / SCA / DAST / secret / image / IaC-policy) catches which defect class, where it runs, and which currently-published tools fit. Names that *no scanner catches a design flaw* — that's `threat-modeler`'s lane.

  **Traverse the relevant Mermaid tree top-to-bottom before triaging or recommending** — the proactive complement to the Capability Grounding Protocol. The two new trees **complement** the consolidated bank; they do not restate it.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (dependency-CVE triage/SLA, committed-secret rotation/IR, SAST false-positive triage, broken-object-level-authz remediation). Secondary source; never replaces the knowledge bank, and never overrides the `security-reviewer` verdict escalation. Scenarios carry **no secret values, tenant identifiers, or live credentials**.

## 6. Technical-runtime tier — MCP & LSP (researched; recommend-not-bundle, dated 2026-06-05)

Security engineering is a **code** domain, so the runtime tier was evaluated honestly. The conclusion: **bundle nothing**, recommend the real, currently-published servers with their setup paths — every candidate fails the doctrine's zero-config + read-only bar, and one is deprecated. Per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a write-capable, per-consumer-path, network-bound, or credentialed server is **recommend-not-bundle**.

### 6.1 Recommended (not bundled) security MCP servers

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Semgrep MCP** (`semgrep-mcp`, MIT, third-party) | Operates on the **consumer's source tree** (path-bound, like the filesystem-server case) and the **standalone `semgrep/mcp` repo is DEPRECATED** — it was folded into the official `semgrep` binary (so the bundling target is a moving artifact). Basic scan needs no token, but connecting to the Semgrep AppSec Platform needs `SEMGREP_APP_TOKEN` (a secret → reference-not-literal). | `claude mcp add semgrep -- uvx semgrep-mcp` (or `pipx install semgrep-mcp`); for platform features set `SEMGREP_APP_TOKEN` as an **env-var reference**, never a literal. Track the migration into the `semgrep` binary. Owned by `appsec-engineer`. |
| **OSV-Scanner MCP** (Google, Apache-2.0, first-party-to-OSV) | The MCP server is **experimental** (`osv-scanner` `mcp`/`experimental-mcp` subcommand), is **repo-path-bound** (scans the consumer's lockfiles), and is **network-bound** (queries osv.dev / deps.dev). Experimental + path + network → recommend-not-bundle. | Install `osv-scanner` (Go binary, v2.3.8 May 2026), then wire the experimental MCP subcommand per its docs. Owned by `supply-chain-security-engineer`. |
| **Trivy MCP** (`aquasecurity/trivy-mcp`, Apache-2.0, vendor) | Scans **local filesystem / images / remote repos** (per-consumer path) and is **network-bound** (downloads the vuln DB). Per-consumer config → recommend-not-bundle. | `trivy plugin install mcp` then `trivy mcp` (verify the plugin invocation at use). Owned by `supply-chain-security-engineer` (deps/images) + `cloud-security-engineer` (image/IaC). |

**Why none are bundled (the load-bearing reasoning):** the doctrine's decision table sends "per-consumer config OR write-capable OR secret-handling" straight to **recommend, don't bundle** — and additionally, a bundled MCP server's **tool results are untrusted input** flowing into agent context (a malicious dependency name / scan finding is data, not instructions). A deprecated upstream (Semgrep's standalone repo) and an experimental server (OSV-Scanner) compound the supply-chain risk of auto-starting on every consumer's `/plugin marketplace update`. If a genuinely zero-config, read-only, maintained security server appears, revisit with the doctrine block in [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4. **No server/version/CVE here is invented** — each is web-verified (sources in `CHANGELOG.md` § Verify-at-use).

### 6.2 LSP — N-A (no single source language; Semgrep LSP is a findings surface)

Unlike `backend-engineering` (which bundles an `.lsp.json` for Python/TS/Go go-to-definition), this is an **AppSec/advisory** domain with **no single source language** to drive code intelligence — the plugin reasons *about* a consumer's code in whatever language it's written, so a bundled language-server config has no canonical target. The real **Semgrep LSP** (`semgrep lsp`, experimental — the same daemon the official Semgrep IDE extensions use) is a **findings/diagnostics** surface, not a navigation one; it's documented as a recommend-not-bundle option for `appsec-engineer` consumers who want inline SAST in their editor, not a plugin-bundled config.

## 7. Runnable tooling — `scripts/sec_risk.py`

[`scripts/sec_risk.py`](scripts/sec_risk.py) (stdlib only, Python 3.9+, ruff-clean) removes guesswork — and CVSS-only theater — from two recurring triage decisions:

- `risk-band` — CVSS base + deployment context (reachability, internet exposure, auth-to-trigger, KEV/known-exploited, optional EPSS) → a **risk band** (emergency / critical / high / medium / low) + a **proposed SLA**. Its leaves mirror [`knowledge/vulnerability-severity-vs-risk-decision-tree.md`](knowledge/vulnerability-severity-vs-risk-decision-tree.md) exactly. An **unknown** reachability/exposure fails safe toward higher urgency.
- `cvss-temporal` — a transparent, **approximate** within-band re-weighting (exploit-maturity × remediation-level) to break ties where KEV is silent. It shows its arithmetic and is **explicitly not** the official CVSS calculator (use FIRST's for an authoritative vector); it never overrides the KEV/reachability gate.

It is a **calculator, not a data source** — the user supplies every input; it fetches no CVE, no KEV catalog, no EPSS score. Outputs are decision-support; the ship/no-ship / accept-the-risk **verdict routes to `ravenclaude-core/security-reviewer`** (§2). Owned primarily by `appsec-engineer` + `supply-chain-security-engineer`.

## 8. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason), building on PR #315's consolidated knowledge/best-practices/templates:

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 real-engagement scenarios (dependency-CVE triage/SLA, committed-secret rotation/IR, SAST false-positive triage, broken-object-level-authz remediation) + README + 9-field schema, per the veterinary-practice/backend-engineering pattern. |
| 2 | **Decision-tree knowledge** | **BUILT** — 2 NEW Mermaid trees: `vulnerability-severity-vs-risk-decision-tree.md` (severity→risk band+SLA) and `sast-dast-sca-scanner-selection-decision-tree.md` (scanner-class selection). Both **complement** PR #315's `security-engineering-decision-trees.md` (which already covers vuln-triage/secret/shift-left/auth-authz/patch/cloud), grounded + cited + dated. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §6.1. Web-researched the real published security servers: Semgrep MCP (MIT, third-party, **deprecated** standalone repo, source-path-bound), OSV-Scanner MCP (Apache-2.0, **experimental**, repo-path + network-bound), Trivy MCP (Apache-2.0, per-consumer-path + network-bound). None clears zero-config + read-only. Documented the `claude mcp add` paths + a `security-reviewer` gate instead. No invented servers/versions. |
| 4 | **LSP server** | **N-A** — §6.2. No single source language to drive code intelligence in an AppSec/advisory domain; the real Semgrep LSP is a findings surface, documented as recommend-not-bundle. The `.lsp.json` config pattern is N-A here. |
| 5 | **Runnable script (`scripts/`)** | **BUILT** — `sec_risk.py` (`risk-band` + `cvss-temporal`). Real value: removes CVSS-only-theater from triage and mirrors the new severity-vs-risk tree's logic. Stdlib-only, ruff-clean. |
| 6 | **bin/ / monitors / output-styles / settings defaults / themes** | **N-A** — no groundable, broadly-valuable instance. A security-review output-style would overlap the agents' Output Contract; the plugin is config-light by design. The `scripts/sec_risk.py` calculator covers the one runtime item with real value (no compiled `bin/` warranted). |
| 7 | **skills / hooks / commands / templates** | **Coverage sufficient** — 5 skills (appsec-scanning, secrets-detection-and-remediation, secrets-management, supply-chain-security, threat-modeling-stride), 4 commands, 4 templates, and 1 advisory anti-pattern hook already cover the surface. The new trees + calculator extend reach without a new agent (team-growth-as-knowledge house rule); no clear gap warrants a 6th skill or hook. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.3.0` entry. No `NOTICE.md` (nothing third-party is bundled — every source is cited inline, not vendored). |

## 9. Milestones

- **v0.2.x** — security-engineering (AppSec) team: 4 agents, 5 skills, consolidated decision-tree knowledge + dated capability map, 12 best-practices, 4 templates, 4 commands, 1 advisory hook. PR #315 added the consolidated `knowledge/*-decision-trees.md` + `best-practices/` + `templates/`.
- **v0.3.0** — value-add build-out: scenarios bank (4 scenarios), 2 new complementary Mermaid decision-tree knowledge files, `scripts/sec_risk.py` (risk-band + cvss-temporal), runtime-tier disposition (MCP + LSP recommend-not-bundle, web-researched + dated), CHANGELOG. Every menu item dispositioned (§8).
