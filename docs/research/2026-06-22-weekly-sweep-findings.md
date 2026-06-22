# Weekly news-cadence sweep — findings, panels & triage (2026-06-22)

A Tier-A weekly news-cadence sweep per [`docs/research-routine-two-cadence.md`](../research-routine-two-cadence.md). Four parallel research agents covered the Tier-A clusters (Microsoft stack · cloud/infra · data/BI · AI-Claude-web). Every candidate finding was then **grounded against the actual repo text** before counting — the step that dissolved most of them — and the survivors were routed through two expert panels.

**Triage key:** **CORRECTION** = the repo currently states something now-false or stale (ship first). **ADDITION** = a new capability not yet documented (queue). **EVAPORATED** = the candidate did not survive repo-grounding (already documented, or not actually false). **NULL** = checked, nothing in-window.

## What shipped this run (built + panel-reviewed)

Two **version-rot CORRECTIONS**, both squarely inside the editor's own training knowledge (no post-cutoff dependency), both single-file, both leaving the surrounding guidance unchanged:

1. **data-streaming-engineering 0.3.0 → 0.3.1** — `knowledge/data-streaming-engineering-decision-trees.md`: re-anchored three per-tree "Last verified" stamps from **Apache Flink 1.19 / Kafka Streams 3.7** to **Flink 2.x (stable 2.2.x) / Kafka 4.x** (KRaft-only). Flink 2.0 and Kafka 4.0 are both long-GA; the documented join/backpressure/checkpoint semantics are version-stable, so only the anchors moved. `[verify-at-use]` on exact patch numbers.
2. **database-engineering 0.3.0 → 0.3.1** — `knowledge/database-engineering-decision-trees.md`: tightened the capability-map's vague `PostgreSQL | GA, current major` to the concrete, verifiable **PG18 (GA 2025-09-25)** anchor, kept `[verify-at-build]`.

Each carries a `plugin.json` + `marketplace.json` lockstep bump and a CHANGELOG entry.

### Verification (editor re-check, this session)
- **Flink 2.x / Kafka 4.0 KRaft-only** — both GA *before* the editor's Jan-2026 training cutoff (confirmed from training knowledge); the 2.2.x / 4.3.x patch lines are post-cutoff and so carry `[verify-at-use]`. The OLD 1.19 / 3.7 anchor is unambiguously stale either way. Corroborated across multiple primary release pages by the data/BI research agent (apache.org Flink/Kafka release blogs).
- **PostgreSQL 18 GA 2025-09-25** — within the editor's training cutoff (confirmed); a precise current-major anchor replacing a vague phrase, no guidance change.

## Panel 1 — Usefulness

Three seats (production data-infra engineer · marketplace knowledge-curator · SMB-consulting-fit skeptic).

> **VERDICT: USEFUL · CONFIDENCE: high**
> Both are pure CORRECTIONS to dated facts the plugins explicitly stamp with a "Last verified" date — the exact payload the two-cadence routine exists to keep fresh. A version anchor two major lines behind (Flink 1.19 when 2.x is GA; Kafka Streams 3.7 when 4.0 removed ZooKeeper) actively misleads an engineer who trusts the stamp. The PG "current major" phrase is not false but is a weaker anchor than a dated version; resolving it costs nothing and improves precision. Both are in-scope, audience-relevant, zero-risk to consumers on `/plugin marketplace update`. **DISSENT: none** (skeptic noted the PG change is low-magnitude — "refinement, not rescue" — but agreed it's net-positive and free).

## Panel 2 — Detailed review

Three seats (technical-correctness · accuracy/citation · editorial-fit).

> **VERDICT: APPROVE-WITH-CHANGES · CONFIDENCE: high**
> Required: (1) do **not** encode the exact patch numbers (2.2.1 / 4.3.0 / PG18.4) as bare facts — they are post-cutoff and rest on research-agent search snippets; state the major-line anchor and mark patch specifics `[verify-at-use]`. (2) Keep the version-stable semantics untouched — the join/window/checkpoint content is correct and must not be "modernized" speculatively. (3) Bump `marketplace.json` in lockstep with each `plugin.json`. (4) Frame the PG row as a precision tightening, not a correction-of-falsehood, so the changelog stays honest.

### Disposition of Panel 2's flags
| Flag | Action |
|---|---|
| Don't encode bare patch numbers | **Done** — text says "Flink 2.x (current stable 2.2.x)" / "Kafka 4.x" / "PG18 (2025-09-25)" with `[verify-at-use]` / `[verify-at-build]`; no patch encoded as load-bearing fact. |
| Leave version-stable semantics alone | **Done** — only the "Last verified" anchor lines + the one PG cell changed; no tree body edited. |
| `marketplace.json` lockstep | **Done** — both plugins bumped in `plugin.json` + `marketplace.json`. |
| PG framing honesty | **Done** — CHANGELOG calls it a precision tightening, not a falsehood fix. |

## Tiebreak
**Not triggered** — both panels concurred (USEFUL + APPROVE-WITH-CHANGES). No third panel convened.

## EVAPORATED on repo-grounding (candidates that did NOT survive)
Recording these so a later sweep does not re-chase them. Each was a plausible research-agent finding that dissolved the moment it was checked against the repo:

- **microsoft-365-copilot — Federated (MCP) connectors GA 2026-06-02** → **already documented** (`copilot-connectors-2026.md` line 4, re-verified 2026-06-11).
- **microsoft-365-copilot — declarative-agent manifest v1.7** → **already cited** as the current pinned version across the knowledge file + best-practice.
- **finops-cloud-cost — FOCUS 1.3 → 1.4** → **no FOCUS version is pinned** in the plugin (only a passing scenario mention); nothing to correct.
- **terraform-iac — OpenTofu 1.12.x / OCI distribution** → **already anchored** to 1.12.x (re-verified 2026-06-11); 1.12.3 is a patch within the same anchor.
- **ai-coding-model-guidance / claude-app-engineering — Sonnet 4 / Opus 4 retired 2026-06-15** → the repo **never lists the retired model IDs** (`…-4-20250514`) as callable; it correctly anchors on 4.6 / 4.8 / 4.5. The only "Sonnet 4 / Opus 4" mention is a note about Microsoft Foundry's *deployable-model table*, which is accurate. Nothing to correct.
- **claude-app-engineering — advisor tool** → **already built** (PR #420, v0.9.0).

## Patch-version churn — deliberately NOT counted (anchors already correct)
The cloud/infra cluster surfaced a wave of in-window patch releases — **k8s 1.36.2 / 1.37-alpha.1, containerd patch wave, OpenTofu 1.12.3 (CVE GHSA-q7j3-v8qv-22vq fix), Pulumi 3.247, Prometheus 3.5.4, Grafana Tempo 2.10.7, Backstage 1.52** — but the plugins' anchors (k8s 1.36, OpenTofu 1.12.x) are already current and patch bumps don't change documented guidance. This is exactly the noise the two-cadence routine warns about; logged, not built. (If a deeper freshness pass wants the OpenTofu CVE noted as a security rider, that's a fair small follow-up — left out here to keep this PR to clean corrections.)

## Queued — VERIFIED additions not built this run (need their own primary re-verify + panel pass)
Honest triage: these are real and additive but each needs post-cutoff primary verification and a focused build, deliberately not padded into a corrections PR.

- **microsoft-graph** — programmatic FIDO2 passkey **self-service registration GA** (v1.0, June 2026), with admin-provisioning-on-behalf-of-a-user still preview; `fileStorageContainer` upsert-permission limit 10→40; `security alert` `category`→`categories` deprecation. (Graph plugin currently documents no FIDO2 surface.)
- **microsoft-fabric** — Fabric Graph GA (firm); Eventstream **Apache Kafka + Azure Service Bus sources are still PREVIEW** (the prior queue note's "GA" was wrong — do NOT add as GA); Fabric Data Agents-in-M365-Copilot GA/preview doc-internal contradiction (what's-new says GA, consume page still shows a preview banner — prefer the conservative per-feature page).
- **microsoft-365-copilot** — policy-based agent-lifecycle rules (shipped 2026-06-02); Copilot Cowork GA + usage-based "Copilot Credits" (a licensing/SKU fact, only if the plugin documents Copilot billing).
- **tableau** — 2026.2: Hosted (Cloud) Tableau MCP **GA late June**; **Tableau Agent in Dashboards is Beta/Pilot late-July — NOT GA** (the load-bearing caveat). `[verify-at-use]` — tableau.com 403'd direct fetch.
- **ravenclaude-core** — Claude Code changelog: **`post-session` lifecycle hook shipped v2.1.169 (2026-06-08)**; **`disallowed-tools` in skill/slash-command frontmatter shipped v2.1.152 (2026-05-27, pre-window)** — both relevant to marketplace skill/hook authoring. Needs an editor re-verify against `code.claude.com/docs/en/changelog` and the right home in the bank.
- **data-platform** — Snowflake Iceberg v3 GA (low priority for the SMB framing).
- **azure-cloud** — AKS Azure Linux 2.0 retirement framing (status unchanged in-window).

## Honest nulls (checked, nothing actionable in-window)
- **ai-rag-engineering, ml-engineering** — 0 net-new primary-verified in-window (Voyage 4 / Inferact funding are Jan-2026, pre-window).
- **azure-cloud, finops-cloud-cost, devops-cicd, observability-sre, platform-engineering-idp** — 0 net-new dated-fact changes in-window (release churn sat just outside the window or didn't change guidance).
- **power-platform** — 0 confirmed net-new GA flips (June activity was wave-1 release-date slips, inherently `[verify-at-use]`).
- **web-design — Core Web Vitals thresholds UNCHANGED** (LCP 2.5s / INP 200ms / CLS 0.1); no threshold to encode.
- **analytics-engineering / data-platform — dbt Core v2.0 still ALPHA** (no GA transition; correctly left as-is).

## Notes for the next sweep
- The two-cadence model held up: of ~28 Tier-A plugins, the honest yield was **2 corrections + a queue of verified additions** — the rest 0-net-new, exactly as the routine predicts.
- Highest-value still-open items: the **microsoft-graph FIDO2** addition and the **ravenclaude-core Claude Code changelog** cluster (both need a primary re-verify first).
- Universal WebFetch 403 on most non-Anthropic/non-Microsoft domains this session — Microsoft-Learn MCP and GitHub release pages fetched cleanly; tableau.com / apache.org / aws.amazon.com / cisa.gov 403'd, so those findings carry `[verify-at-use]`.
