# Salesforce — plugin analysis + buildout plan

**Date:** 2026-05-30
**Status:** Decision + research synthesis + v0.1.0 scope. Grounding: Salesforce official docs / architect.salesforce.com / Trailhead + credible community, retrieved 2026-05-30 (URLs inline in the knowledge bank as built). Fast-moving Agentforce facts are flagged `[verify-at-build]`.

---

## 0. TL;DR

Ship a new **`salesforce`** plugin — a senior Salesforce practitioner team covering Apex, Flow/automation, Agentforce, org/data-model/sharing architecture, and a forked review rubric. Salesforce is a large, idiosyncratic platform whose review criteria (governor limits, FLS enforcement, test rules, the trigger framework) are **genuinely incompatible** with a generalist's — clearing the house-rule bar for forked agents. No existing RavenClaude plugin covers it; overlap is at seams only.

## 1. Architecture decision — standalone plugin: YES

The house-rule test ("could a core agent + skill + knowledge produce indistinguishable output?") **fails** for the bulkification/CPU-budget/mixed-DML/CRUD-FLS reasoning, the automation-density judgment, and the Agentforce 2026 surface. These are operational craft a generalist lacks (a generalist writes loop-DML that passes review but fails at 200 records). Overlap with existing plugins is at *seams*, not core (integration→azure-cloud, analytics→data-platform/fabric, LWC UI→web-design).

## 2. The surface (research synthesis, 2026)

- **Clouds + data:** Sales/Service Cloud core; **Data Cloud ("Data 360")** is the data backbone (DSO→DLO→DMO), feeding analytics activation and AI grounding.
- **Agentforce (the 2026 shift):** Agent + Topics + Actions + the **Atlas Reasoning Engine** (ReAct loop). New graph-based **Agentforce Builder (GA Feb 2026 `[verify-at-build]`)** with **hybrid reasoning** (LLM + deterministic rules) authored in **Agent Script** (text DSL). **"Topics→Subagents" / "Topic Selector→Agent Router" rename April 2026 `[verify-at-build]`.** Grounding via Data Cloud RAG + Prompt Builder; governed by the **Einstein Trust Layer**.
- **Dev model:** Apex (governor-limited), **LWC** (LDS + `@wire`; `lightning/graphql` GA Spring '26), **Flow** (declarative-first), SOQL/SOSL.
- **Metadata/packaging:** `sf` CLI, source-tracked scratch orgs, **2GP** (unlocked / managed / org-dependent).
- **DevOps:** change sets (legacy) → DevOps Center (free, Git-backed) → full SFDX/2GP CI/CD (mature standard).
- **Security model:** OWD → role hierarchy → sharing rules → manual → Apex managed sharing; profiles + permission sets/groups; governor limits enforce multitenancy.
- **Integration:** REST/SOAP, **Bulk API v2**, **Platform Events / CDC / Streaming**, MuleSoft, Salesforce Connect.
- **Admin:** Developer / Developer Pro / Partial Copy / Full Copy sandboxes; seeding/masking.

## 3. Plugin scope (v0.1.0)

### 3.1 Roster — 5 agents (release-engineer held as a skill until usage justifies an agent)

| Agent | Mission | Why an agent (not a skill) |
|---|---|---|
| `apex-engineer` | Governor-safe, bulkified, secure Apex (triggers, async, services) | Bulkification / CPU-budget / mixed-DML / CRUD-FLS craft |
| `flow-automation-architect` | Declarative automation by automation-density; record-triggered/screen Flows | Density math, before/after-save semantics, "no pink in loops", Flow↔Apex escalation |
| `agentforce-architect` | Agentforce: topic/subagent decomposition, actions, Agent Script determinism, RAG grounding, Trust Layer | Entirely SF-specific 2026 surface; no generalist analog |
| `salesforce-platform-architect` | Org design: data model, sharing/security model, packaging, LDV | Irreversible-blast-radius decisions + deep platform mechanics |
| `salesforce-reviewer` | Review SF diffs against the house rubric (governor limits, FLS, test quality, trigger framework) | Review rubric **genuinely incompatible** with core's — the house-rule justification for a forked reviewer |

**Skills, not agents** (core agent + knowledge ≈ equal output): SOQL/SOSL authoring, LWC scaffolding (UI routes to `web-design` + skill), Bulk/REST client scripting, Data Loader / data-migration runbooks, sandbox-seeding. **LWC stays a skill in v0.1.0**; reassess if Lightning-specific craft (LDS/wire/LWS) justifies an agent later. Generic Git/PR/CI is core; SFDX/2GP metadata-ordering specifics ship as the `salesforce-release-pipeline` skill.

### 3.2 Knowledge bank — 9 docs (citation-grounded; ✦ = Mermaid decision tree)

1. `governor-limits-and-bulkification-2026.md` ✦ — limit table + bulk-safe patterns (limit-budget triage).
2. `automation-decision-2026.md` ✦ — Flow vs Apex vs no-code by **automation density** (load-bearing).
3. `trigger-framework-and-apex-architecture-2026.md` ✦ — one-trigger pattern, handler vs fflib (when to layer).
4. `async-apex-selection-2026.md` ✦ — future/Queueable/Batch/Scheduled + chaining/concurrency limits.
5. `sharing-and-security-model-2026.md` ✦ — OWD→role→rules→Apex; CRUD/FLS enforcement (load-bearing).
6. `packaging-and-devops-2026.md` ✦ — 2GP/unlocked/org-dependent + DevOps Center vs SFDX CI/CD + deployment ordering.
7. `integration-patterns-2026.md` ✦ — REST/Bulk/Platform Events/CDC/MuleSoft (which pattern).
8. `agentforce-agent-design-2026.md` ✦ — topics/subagents/actions, Agent Script determinism, RAG grounding, Trust Layer (deterministic vs reasoning); carries a freshness/version banner.
9. `large-data-volume-and-performance-2026.md` ✦ — selective queries, custom indexes, skinny tables, data skew.

### 3.3 Skills (~5) + templates (~5) + hook

- Skills: `soql-authoring`, `lwc-component-scaffold`, `bulk-rest-api-client`, `data-loader-runbook`, `salesforce-release-pipeline`.
- Templates: trigger-handler skeleton, Apex test-class skeleton (bulk + positive/negative), record-triggered Flow checklist, 2GP deployment-ordering runbook, Agentforce agent-design canvas.
- 1 advisory `flag-salesforce-anti-patterns.sh` hook enforcing the grep-able house opinions (SOQL/DML-in-loop, hard-coded IDs, `SeeAllData=true`, missing `with sharing`).

### 3.4 House opinions (15; the hook flags the grep-able ones)

Never SOQL/DML in a loop · one trigger per object via a thin trigger→handler · start declarative, escalate to Apex past Flow's ceiling · no "pink" elements in Flow loops · before-save Flow for same-record defaults · enforce CRUD/FLS explicitly + bind variables · OWD restrictive-first, open declaratively before Apex sharing · setup/non-setup DML never share a transaction · tests create own data, bulk-test at 200, assert ±, 75% is a floor · no hard-coded IDs · version control is source of truth (2GP/SFDX over change sets) · smallest async tool that fits · watch automation density per object · Agentforce: enforce sequence with Agent Script not reasoning, never bypass the Trust Layer · mind LDV thresholds (selective/indexed, watch >10k-child skew).

### 3.5 Cross-plugin seams

azure-cloud (MuleSoft/middleware + non-SF endpoints; SF owns Platform Events/CDC/callouts/Named Credentials) · data-platform / microsoft-fabric (downstream warehousing/BI; SF owns Data Cloud activation + CRM Analytics) · web-design (LWC styling/SLDS/a11y; SF owns LDS/`@wire`/Apex-controller wiring) · ravenclaude-core (agent-design methodology, generic DevOps, security-reviewer escalation for SOQL-injection/secrets).

## 4. Risks / open questions

- **Roster size.** 5 is right for v0.1.0; `salesforce-release-engineer` was the weakest standalone case → demoted to a skill, promote later if usage justifies.
- **LWC ambiguity.** No LWC agent in v0.1.0; route UI via web-design + a skill, reassess.
- **Agentforce volatility.** Fast-moving 2026 surface (Subagents rename, builder GA, Agent Script) — the Agentforce knowledge doc carries a freshness banner; exact API/naming tagged `[verify-at-build]`.
- **Governor-limit numbers** — reconfirm against the Spring '26 limits cheat sheet at build time.

## 5. v0.1.0 scope (summary)

5 agents (apex-engineer, flow-automation-architect, agentforce-architect, salesforce-platform-architect, salesforce-reviewer) · 9-doc citation-grounded knowledge bank (9 Mermaid decision trees) · 5 skills · 5 templates · 1 advisory hook (15 house opinions) · seams wired (integration→azure-cloud, analytics→data-platform/fabric, LWC→web-design, methodology/DevOps/security→ravenclaude-core) · requires `ravenclaude-core@>=0.7.0` · core stays domain-neutral. Ships as its own PR with full audit-gates + the gated frontmatter schema on every agent + repo-guide regen.
