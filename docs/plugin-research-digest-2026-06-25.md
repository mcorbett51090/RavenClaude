# Plugin research digest — 2026-06-25

Automated scheduled-routine output. Researched recent (≈Dec 2025 – Jun 2026) developments for every active plugin, ran each candidate finding through two independent expert panels (usefulness + build-readiness) with a third tiebreaker panel for disagreements, then applied a vetted **Tier-1** subset to plugin knowledge files. This doc is the full audit trail and the backlog for follow-up PRs.

## Method

- **13 research scouts** swept all ~120 plugins (web search, primary-source-biased), returning only specific, dated, citable findings — **110 candidate findings**, plus ~13 explicit NONEs (cli-tooling-engineering, developer-tooling, performance-engineering, customer-success-analytics, product-management, technical-program-management, engineering-management, legal-ops-clm, startup-fundraising, developer-relations, edtech-partner-success, renewable-energy, k12-school-administration).
- **Panel 1 (usefulness):** KEEP/DROP + impact. Kept 104, dropped 6.
- **Panel 2 (build-readiness):** independent BUILD/HOLD + confidence, with web spot-checks of the highest-uncertainty claims against primary sources.
- **Panel 3 (tiebreaker):** resolved the 18 findings where the two panels disagreed.
- **Outcome:** ~101 findings passed review; **15 findings (12 plugins) applied this cycle**; 5 deferred (pending/future-dated legal status); 4 excluded by both panels.

## Applied this PR (Tier-1: highest-impact, primary-verified, cleanly buildable, domain-diverse)

| Plugin | Ver | Finding | Source-dated |
|---|---|---|---|
| claude-app-engineering | 0.9.5→0.9.6 | Current Claude lineup (Opus 4.8 `claude-opus-4-8` $5/$25 1M-ctx; Sonnet 4.6; Haiku 4.5) + advanced tool use (Tool Search Tool, memory tool, context editing, programmatic tool calling) | F12 |
| ravenclaude-core | 0.182.0→0.182.1 | New `claude-code-harness-2026.md`: MCP spec 2025-11-25, Claude Code SDK→Claude Agent SDK rename, Bash `sandbox` settings block (+`sandbox.credentials`), blockable PreCompact hooks | F96–F99 |
| security-engineering | 0.3.2→0.3.3 | OWASP Top 10:2025 final (Jan 2026): new A03 Software Supply Chain Failures, A10 Mishandling Exceptional Conditions, Security Misconfig→A02, SSRF→A01 | F26 |
| data-science-research | 0.2.0→0.2.1 | pandas 3.0.0 (2026-01-21) repro-pinning boundary: enforced CoW, default PyArrow-backed `str` dtype, Python ≥3.11 (PyArrow-required nuance corrected per primary docs) | F49 |
| database-engineering | 0.3.2→0.3.3 | PostgreSQL 18 (2025-09-25): async I/O (read-only), UUIDv7, OAuth | F22 |
| frontend-engineering | 0.4.0→0.4.1 | React 19.2 (2025-10-01) + React Compiler 1.0 GA (automatic memoization) | F19 |
| mortgage-lending | 0.1.0→0.1.1 | 2026 conforming loan limits: baseline $832,750 / ceiling $1,249,125; FHA floor $541,287; HMDA exemption $59M | F58 |
| people-operations-hr | 0.1.0→0.1.1 | 2026 IRS limits (401k $24,500, IRA $7,500, HSA $4,400/$8,750, FSA $3,400); SECURE 2.0 Roth catch-up >$150k; restored FLSA $684/wk threshold | F72 |
| medical-revenue-cycle | 0.2.1→0.2.2 | CMS CY2026 PFS dual conversion factors ($33.57 QP / $33.40 non-QP); CPT 2026 = 418 changes | F63 |
| cannabis-operations | 0.3.1→0.3.2 | Medical/FDA-approved marijuana → Schedule III (eff. 2026-04-28), 280E relief; recreational unaffected | F110 |
| salesforce | 0.6.2→0.6.3 | Summer '26 API v67.0 breaking: Apex user-mode default, `with sharing` default, `WITH SECURITY_ENFORCED` removed→`WITH USER_MODE`; Connected Apps→External Client Apps; Flow Orchestration GA | F36 |
| browser-extension-engineering | 0.2.0→0.2.1 | Manifest V2 fully sunset in Chrome (no exemptions); Firefox-only blocking `webRequest` divergence | F39 |

Each edit matches the file's dated-knowledge house style and carries primary/authoritative source links stamped `retrieved 2026-06-25`. Knowledge content only — no agent prompts, hooks, or constitution text changed.

## Backlog — passed review, ready to apply in a follow-up PR

These cleared both panels (or the tiebreaker) but were held out of this PR to keep it reviewable. Each is a candidate for a future cycle.

**Cloud/infra:** F1 aws (re:Invent 2025), F2 azure (gpt-4o-mini retirement), F3 gcp (Next '26 GA), F4 k8s 1.35, F5 terraform 1.15/OpenTofu 1.12, F6 Backstage 1.49 NFS, F7 FOCUS 1.4, F8 OTel Profiles.
**AI/data:** F9 llm-d CNCF, F10 pgvector/Milvus, F11 AI coding roster, F14 dbt Fusion, F15 Airflow 3.2, F16 Kafka 4.x/Flink 2.2, F17 dbt Semantic Layer YAML.
**Core eng:** F18 Node 24 LTS, F20 RN New Arch mandatory, F21 Tauri 2.x, F23 OpenAPI 3.2, F24 Loro 1.0.
**DevOps/security:** F25 GitHub Artifact Attestations, F27 PCI DSS 4.x mandatory, F28 WebAuthn L3 CR, F29 UK OSA age assurance, F31 agentic COBOL migration.
**Microsoft/platform:** F32 Copilot manifest 1.7, F33 Fabric GA, F34 Graph 2026 retirements, F35 Power Platform Wave 1, F38 WP 6.9/7.0.
**Web/specialty:** F40 Tailwind v4.2, F41 EAA enforced (WCAG 2.1 AA), F42 MF2 not-default, F43 Outlook bulk-sender, F44 Pectra/Fusaka+Solidity 0.8.35, F45 Zephyr 4.3, F46 UE 5.8/Godot 4.6/Unity, F47 PCI 4.0.1/PSD3.
**Data/quality:** F48 US state privacy + EU AI Act timeline, F50 R 4.6.0, F51 Elasticsearch 9/BBQ, F52 QGIS 4.0, F53 Statsig/OpenAI, F54 Playwright Test Agents.
**Finance/legal:** F55 OBBBA bonus depr/199A, F56 Reg S-P, F57 ASU 2024-03 + 2026 IRS limits, F59 NAIC AI/CO AI Act, F60 2026 ACA/HSA limits, F61 CA IOLTA 2026.
**Healthcare:** F62 ICH E6(R3) Annex 2, F64 behavioral-health DMHT codes, F65 DSCSA/PBM, F66 CDT 2026, F67 DEA telemedicine/vet-tech, F68 optometry 2026 codes, F69 PT KX threshold/RTM, F70 HH/SNF PPS 2026, F71 FY2026 hospice/HOPE.
**Ops/business:** F73 GA4/Privacy Sandbox, F74 Agentforce Sales rename, F76 Salesforce/Fin + Zendesk pricing, F77 PMBOK 8/PMP 2026.
**Industry ops:** F78 Section 232 tariffs, F79 EU Omnibus CSRD/CSDDD, F81 FMCSA ELD/broker rules, F82 de minimis suspension, F83 EPA A2L refrigerant, F84 IL interchange delay, F85 PCI e-skimming/Shopify, F86 CA allergen/FSMA 204, F87 FTC junk fees/NYC, F88 OBBBA charitable, F89 FTC junk fees/StubHub, F90 SAG-AFTRA 2026, F92 ITIL v5, F93 OpenAPI 3.2/MkDocs, F94 EU CRA/SPDX, F95 DORA 2025 metrics, F101 2024 IBC/GA, F102 I-Code transition, F103 FinCEN RRE vacated, F105 2026 NEC, F107 SEC climate rescission/CSRD, F108 federal+CA AI EOs, F109 FTC dealer pricing.

## Deferred (tiebreaker) — pending / future-dated legal status; re-evaluate when status firms up

- **F30** regulatory-compliance — AMLR/Travel Rule largely future-phased application (~2027).
- **F37** tableau — mix of beta + 2026.2 future features; needs per-version verification.
- **F80** procurement-sourcing — FAR "Revolutionary Overhaul" is an evolving/pending rulemaking.
- **F91** process-improvement — ISO 9001:2026 still FDIS; publication ~Sept 2026.
- **F104** property-management — HUD disparate-impact removal is a *proposed* rule (comment period open).

## Excluded (both panels negative)

- **F13 / F100** claude-app-engineering / ravenclaude-core — MCP spec **2026-07-28** is a release candidate dated *after* today; encode when it ships as stable.
- **F75** sales-engineering — Vivun "VivunOne" launch: low-confidence GA date, vendor PR.
- **F106** precision-agriculture — 2026 Farm Bill is a *draft*, not enacted.

## Caveats carried from research (for whoever picks up the backlog)

- email-engineering: a claimed "June 2026 DMARC np/p parameter change" was **unverified** and dropped; only the verified Outlook bulk-sender rule (F43) stands.
- embedded-iot (F45): Zephyr 4.3 verified; Matter/ESP-IDF specifics were not confirmed.
- itsm (F92): ITIL v5 rests on secondary sources with conflicting launch dates — verify against PeopleCert/Axelos before writing.
- renewable-energy: NONE — the existing 2026 policy file already covers the in-window facts (OBBBA begin-construction deadline, Notice 2025-42).
