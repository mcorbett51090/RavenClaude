# Weekly Deep Research Sweep — 2026-09-23

**Trigger:** GitHub issue [#1229](https://github.com/mcorbett51090/RavenClaude/issues/1229), "Researcher Weekly Deep Research Sweep".
**Scope:** Tier-A (news-cadence) plugins only, per [`.ravenclaude/plugins/sweep-tiers.yaml`](../../../.ravenclaude/plugins/sweep-tiers.yaml) — 28 plugins across 6 categories (`ai_and_claude_tooling`, `microsoft_stack`, `cloud_and_infra`, `data_and_bi`, `security`, `web_and_docs`).
**Method:** 7 parallel `deep-researcher` agents, one per sub-cluster (cloud_and_infra was split into `cloud-providers` + `platform-devops` for tractable batch size). Full per-cluster reports live under [`.ravenclaude/runs/researcher-weekly-sweep-2026-09-23/reports/`](../../../.ravenclaude/runs/researcher-weekly-sweep-2026-09-23/reports/) (gitignored run-tier — the per-cluster detail, file:line references, and full source citations live there; this document is the durable, committed summary).

**Epistemic status:** this document aggregates claims *reported* by the 7 dispatched agents. Confidence levels (High / Medium-High / Medium / Low) are each agent's own self-assessment against the sources it cites in the per-cluster reports; this session has not independently re-run a probe against every claim below. Read each line as "the sweep reports X, sourced as noted in the linked per-cluster report" rather than an independently re-verified fact.

## Executive summary

- **7/7 clusters reported.** 2 (`ai-and-claude-tooling`, `microsoft-stack`) hit turn/search-budget limits and are **partial** — see Coverage gaps below.
- **~35 high/medium-high-confidence CORRECTIONS reported** across ~18 plugins — facts the repo currently states that the sweep's sources indicate are now false.
- **~90 ADDITIONS** queued (new capabilities/facts reported as worth adding, not urgent).
- **~230 decision trees** flagged with a `Last verified:` date past the 90-day window (most clusters' trees were last verified in a single batch ~110-118 days ago), plus dozens with no per-tree date at all.
- **One security-relevant finding warrants attention independent of this sweep's normal cadence:** `security-engineering`'s CI examples reportedly cite `trivy-action@master` (an unpinned reference) — the pattern the March 2026 Trivy supply-chain compromise is reported to have exploited. See Security cluster below; this should be independently verified before the fix ships.
- Multiple clusters report the same root cause for incomplete coverage: **the egress proxy blocked most primary vendor doc domains** in this session, so results lean on GitHub mirrors, npm registries, and search snippets. This is a transport limitation, not evidence the underlying facts are wrong — but it means confidence on some findings is lower than a direct fetch would allow.

## Corrections reported, by cluster (candidates to verify and ship)

### AI & Claude tooling (partial — see gaps)
- **claude-app-engineering** (9 reported corrections): Opus 5.5 (2026-09-22) and Fable 5.1 reportedly now lead the model lineup, with Opus 5 / Fable 5 / Opus 4.8 moved to Legacy. Forced `tool_choice` (`any`/`tool`) is reported to now return HTTP 400 on the newest models — which the agent says breaks a stated house opinion. Cache-read multipliers and cache minimums are flagged stale.
- **ai-coding-model-guidance** (5 reported corrections): GPT-6 Astra/Sol/Luna and Grok 4.7 are reported to have shipped; Copilot is reported to deprecate GPT-5.5 and Grok 4.5 on 2026-10-19; Opus 5.5 / Fable 5.1 are reported now available in Copilot.
- **ravenclaude-core** (3 reported corrections): the agent reports the auto-mode description in `claude-code-permissions.md` no longer matches current behavior (needs independent re-verification before shipping — see the per-cluster report for the agent's stated basis); the research-preview label in `dynamic-workflows.md` is flagged as outdated; `model-catalog.json` is flagged as still listing Legacy models as current.
- **ai-rag-engineering**: reported up to date (names no vendors by design) — but its Voyage-model facts live in `claude-app-engineering` and are flagged stale there.
- **ml-engineering** (coverage incomplete, 0 corrections found so far): TFLite reportedly renamed LiteRT.

### Microsoft stack (partial — see gaps)
- **microsoft-fabric** (3 reported corrections, High confidence): Runtime 1.3 is reported end-of-support-announced (support ends 2026-09-30, then LTS to March 2027; Microsoft recommends Runtime 2.0) — repo currently shows it as "current GA (LTS) — production default". Cosmos DB in Fabric is reported GA since Nov 2025 (repo says "GA-track (verify)"). Materialized lake views are reported GA since March 2026 (repo says "GA-track (verify)"). Also flagged: Data Agent access via the Assistants API is reported to have ended 2026-08-26 — closing a P0 left over from August; migrate to the MCP endpoint or Responses client.
- **microsoft-365-copilot** (1 probable correction, Medium confidence): the Retrieval API is reported to now have a v1.0 endpoint; repo says "preview" — needs a GA announcement confirmed before shipping.
- **microsoft-graph**: partially checked, no corrections reported yet; the agent's primary source (Microsoft's what's-new page) only reached July.
- **power-platform**: **not reached this sweep at all** — needs a dedicated follow-up.

### Cloud providers (complete)
- **aws-cloud** (High confidence): AWS App Runner is reported closed to new customers since 2026-04-30, in maintenance mode — AWS is reported to recommend ECS Express Mode (no scale-to-zero) as the replacement. Cited by the agent in 6+ files (decision tree, skill, agent, CLAUDE.md, README, plugin.json).
- **azure-cloud** (High confidence): Azure Cache for Redis is reported to block new creation for existing customers from 2026-10-01 (replacement: Azure Managed Redis); PostgreSQL Single Server is reported retired 2025-03-28 (repo says "retiring"); the Assistants API is reported retired 2026-08-26 (repo describes as future).
- **gcp-cloud** (High confidence): "Cloud Functions" is reported to have been renamed "Cloud Run functions" since August 2024 — cited by the agent in ~15 places across decision trees, skills, agent, CLAUDE.md, README, plugin.json, and 3 best-practices files.
- **finops-cloud-cost**: no corrections reported (states no dated vendor facts by design).

### Platform / DevOps (complete)
- **cloud-native-kubernetes** (5 reported corrections): Kubernetes 1.37 is reported to have made HPA scale-to-zero beta and on-by-default (repo says "HPA min 1, use KEDA"); distroless image tags `-debian12`/`nodejs20` are flagged stale (upstream reportedly lists only `-debian13`; Node 20 is EOL); the upgrade tree's support window is flagged as understated (~14 months, not 12; 1.34 reportedly supported until 2026-10-27); the VPA "Auto means pod restarts" and "Istio ambient emerging" leaves are flagged outdated.
- **terraform-iac** (2 reported corrections): the OpenTofu minimum should reportedly rise to 1.12.6 (or 1.11.14) — a reported credential leak on OCI-registry redirects; Terraform is reported to have deprecated DynamoDB state locking in 1.11.
- **devops-cicd** (2 reported corrections + 1 urgent cross-cutting item): Workflow execution protections reportedly went GA 2026-09-17; public repos are reported to get `pull_request_target` disabled by default from 2026-11-02; Node 20 is reported removed from Actions runners today (shared root cause with the Kubernetes distroless finding above — several examples reportedly still pin Node-20-era action versions).
- **observability-sre**: no corrections reported — the agent's checks on CVE-2026-54704's fix version and OTel Profiles' alpha status both held.
- **platform-engineering-idp** (1 plugin-wide reported correction): DORA is reported to now have 5 metrics; MTTR reportedly renamed "failed deployment recovery time"; the 2025 report is reported to have dropped the elite/high/medium/low tiers.

### Data & BI (complete)
- **analytics-engineering** (significant — 3 reported corrections): dbt v2 is reported GA (2026-09-14), not "alpha, not GA" as the repo states (Fusion reportedly now called "dbt"; Core v2 now "dbt OSS"); the incremental-materialization tree is flagged as incorrectly sending Redshift to `insert_overwrite`, which dbt-redshift reportedly doesn't support; the semantic-layer tree is flagged for citing Cube v0.35 against a reported current version of 1.7.43.
- **data-platform** (minor — 3 reported corrections): Snowflake Adaptive Compute is reported GA (2026-06-16), repo says Preview; the sizing recipe is flagged as merging Gen2 and Adaptive into one product; a skill is flagged for mislabeling dbt-core as MIT-licensed (reportedly Apache-2.0).
- **data-streaming-engineering**: version facts reportedly check out — no corrections.
- **database-engineering** (1 reported correction): the `NOT NULL ... NOT VALID` step is flagged as only working on PostgreSQL 18+.
- **tableau** (1 reported correction): "Data Cloud" is reported renamed "Data 360".

### Security (complete)
- **security-engineering** (significant — 5 reported corrections): **BOD 22-01 is reported revoked**, replaced by BOD 26-04 (2026-06-10) — cited by the agent in 5 places including `sec_risk.py` and CLAUDE.md. **Two CI examples are flagged unsafe/deprecated: `trivy-action@master` is unpinned (reportedly the exact pattern exploited in the March 2026 Trivy compromise — verify independently before fixing); `semgrep-action@v1` is reported deprecated since 2024.** Stale versions flagged: SLSA v1.2 (not v1.0), OSV-Scanner v2.6.0 (not v2.4.0), `codeql-action` v3 reported deprecated December 2026.
- **cybersecurity-grc**: no corrections reported — additions only (newer questionnaire/control-catalogue editions).
- **auth-identity** (3 reported corrections): Clerk's free tier is reported now 50K retained users (not 10K); the Cognito free-tier cut date is flagged as dating from November 2024 (not 2026), default tier reportedly ~$0.015/user; Better Auth issue #4203 is reported closed but fix status unconfirmed — the agent recommends keeping the existing guard.

### Web & docs (complete)
- **web-design** (significant — 10 reported corrections): the dark-mode tree is flagged as showing Tailwind v3 setup while claiming v4; "INP is the most-failed metric" is flagged wrong (agent cites Web Almanac 2025 mobile "good" rates: LCP 62%, INP 77%, CLS 81%); the repo is flagged for stating Popover traps focus, where MDN reportedly states popovers are always non-modal; FAQPage guidance is flagged stale (Google reportedly dropped FAQ rich results 2026-05-07); React Router is reported at v8, not v7; cross-document View Transitions are flagged as not Baseline (no Firefox); an INP code sample is flagged for calling `scheduler.yield()` unguarded (reportedly breaks in Safari); the accessibility auditor is flagged for using 44×44 (AAA) as its target-size bar when the AA floor is reportedly 24×24.
- **frontend-engineering** (1 small reported correction): "Next/Remix" naming. Additions flagged include React Compiler 1.0, a CVSS-10 React Server Components RCE (CVE-2025-55182 — route to `security-reviewer`), React 19.2/19.3, and Next 16's `middleware` reportedly renamed `proxy`.

## Coverage gaps (need follow-up)

1. **power-platform** — not reached at all this sweep. Needs a dedicated pass.
2. **ravenclaude-core** and **ml-engineering** — only partially covered (turn/search-limit exhaustion); most knowledge files in each were not reached.
3. **microsoft-graph** — August-September changelog not checked (source page only reached July).
4. Several individual fact conflicts flagged as unresolved within otherwise-complete clusters (see the per-cluster reports for specifics) — e.g. Azure Flex Consumption rolling-updates GA status, GCP Cloud Run service-health GA month, Foundry's Hosted-on-Anthropic preview status.

## Decision-tree staleness

Every cluster reports the large majority of its dated decision trees past the 90-day re-verification window — in most cases because a whole plugin's trees were stamped in one batch during initial authoring (mid-2026-05 to mid-2026-06) and have not been individually re-checked since. Re-dating should happen only after a real re-check per file, never a blind stamp (per this repo's own knowledge-file-staleness-sweep convention) — so this sweep intentionally does not re-stamp any tree; that is downstream work tied to actually shipping each correction.

## Disposition

- **Corrections** listed above are candidates being independently verified and shipped as a small number of per-cluster PRs (touching only the plugins with real corrections, one version bump per touched plugin).
- **Additions** are queued here as the durable record; picking them up is future work, not blocking.
- **Follow-up research** for power-platform and the two partial AI-tooling plugins is a tracked gap, not silently dropped.
- **Security-relevant findings** (the AWS IAM role manager's PowerUserAccess default, the Azure private-outbound-by-default change, the CVE-2025-55182 RCS RCE, and the `trivy-action@master`/`semgrep-action@v1` CI examples) are routed to `security-reviewer` review as part of the corrections PRs that touch them.
