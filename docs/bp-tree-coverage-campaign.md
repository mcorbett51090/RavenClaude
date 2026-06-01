# Best-practices + decision-tree buildout — coverage campaign (tracking)

**Goal (user directive, 2026-06-01):** flesh out best-practices + decision trees across all 16 plugins to cover **98% of situations**. Process per plugin/cluster: **Panel 1** (research + plan) → **Panel 2** (independent research + gap analysis) → **Panel 3** (tiebreak where the two disagree) → build → PR. Iterate until panels agree. Persist across token resets — this file is the durable state.

## Operating definition
- **"98% coverage"** = the review panels cannot name a *material, common* situation in the plugin's domain that lacks a best-practice rule or a decision-tree leaf. Rare/exotic edge cases are the 2% tail, explicitly out of scope.
- **"Agreement"** = Panel 2's gap analysis surfaces no P0/P1 gap that Panel 1 missed (P2 polish is acceptable to defer). Disagreement on a *material* gap → Panel 3 tiebreak (binding).
- **Design-philosophy guard:** respect each plugin's intended shape. A deliberately-lean plugin (e.g. `ai-coding-model-guidance` = 3 agents over 1 dated lineup) gets decision-tree depth where it fits, NOT a padded 19-file BP library that contradicts its "one file refreshes" design. The panels judge fit, not raw count.

## Baseline inventory (2026-06-01, `main`)
| Plugin | BP files | KN files | Decision trees | Agents | Priority |
|---|---|---|---|---|---|
| ai-coding-model-guidance | 0 | 1 | 1 | 3 | **P1 — thinnest** |
| ravenclaude-core | 4 | 5 | 4 | 14 | special (core) |
| finance | 21 | 2 | 6 | 7 | KN/tree thin |
| regulatory-compliance | 22 | 2 | 16 | 6 | KN thin |
| microsoft-graph | 18 | 3 | 12 | 3 | KN thin |
| tableau | 26 | 3 | 32 | 3 | KN thin |
| applied-statistics | 16 | 6 | 6 | 1 | mid |
| web-design | 19 | 8 | 6 | 7 | trees thin |
| data-platform | 19 | 14 | 6 | 4 | trees thin |
| claude-app-engineering | 20 | 14 | 7 | 6 | trees mid |
| edtech-partner-success | 19 | 17 | 7 | 6 | mid |
| microsoft-365-copilot | 19 | 10 | 8 | 6 | mid |
| azure-cloud | 19 | 11 | 15 | 7 | rich |
| microsoft-fabric | 21 | 10 | 9 | 7 | rich |
| salesforce | 49 | 13 | 31 | 5 | rich |
| power-platform | 58 | 12 | 68 | 11 | richest |

## Cluster assignment (Panel 1 research)
- **C1 Microsoft stack:** power-platform, microsoft-fabric, microsoft-365-copilot, microsoft-graph
- **C2 Cloud / AI-app / data:** azure-cloud, claude-app-engineering, data-platform, ai-coding-model-guidance
- **C3 Business domains:** finance, regulatory-compliance, edtech-partner-success, applied-statistics
- **C4 Dev / CRM / web / core:** salesforce, tableau, web-design, ravenclaude-core

## Panel 1 — research + proposed plan (raw, pre-gap-analysis)

### C1 Microsoft stack (in)
- **power-platform** — comprehensive/minor. +2 BP (`connector-custom-connector-auth-and-policy`, `bi-refresh-and-gateway-reliability`), +2 trees (PBI deploy/refresh; custom-connector build-vs-HTTP-vs-certified).
- **microsoft-fabric** — MATERIAL. +3 BP (`warehouse-scd-and-merge-patterns`, `warehouse-security-rls-cls-masking`, `rti-retention-and-caching-policy`), +2 trees (security-plane; RTI alerting). Deepen onelake-security.
- **microsoft-365-copilot** — minor. +2 BP (`eval-test-agent-responses-before-and-after-ship`, `apiplugin-render-responses-with-adaptive-cards`), +1 tree (eval/monitoring strategy).
- **microsoft-graph** — minor. +3 BP (`workloads-use-immutable-ids-for-stored-references`, `workloads-mail-and-attachments-at-scale`, `workloads-calendar-recurrence-and-timezone`), +2 trees (ID stability; recurring-event read).
- C1 total: **10 BP, 7 trees.** Flag for Panel 2: is agent-resident craft (fabric warehouse-SCD, m365 adaptive-cards) a real gap or deliberate?

### C2 Cloud/AI/data (in)
- **azure-cloud** — minor. +4 BP (`reliability-multi-region-bcdr-by-tier`, `data-tier-pick-the-azure-database`, `migration-assess-then-iac-not-lift-and-shift`, `network-front-door-waf-and-ddos-at-the-edge`), +2 trees (resilience ladder; data-tier). Deepen observability+networking.
- **claude-app-engineering** — minor. +3 BP (`multimodal-extract-vs-native-document-input`, `model-migrate-behind-an-eval-gate`, `streaming-design-the-token-ux`[borderline]), +2 trees (document-input; model-version-migration).
- **data-platform** — MATERIAL. +4 BP (`pipeline-monitor-freshness-and-row-counts`, `connector-handle-source-schema-drift`, `migration-spreadsheet-to-warehouse-staged-cutover`, `reverse-etl-when-the-warehouse-feeds-back`[lower-pri]), +2 trees (pipeline-failure-response; schema-change-response).
- **ai-coding-model-guidance** — comprehensive by design. +2 durable-reasoning BP only (`right-size-by-cost-per-resolved-task-not-rank`, `scope-model-availability-by-surface-plan-date`), +3 trees (all in the existing lineup file: reasoning-vs-bigger-model; retired-model; cost-escalation). NO BP library (respects §7).
- C2 total: **13 BP, 9 trees.**

### C3 business domains (in)
- **finance** — minor. +2 BP (`controller-accrual-vs-prepaid-vs-deferral-cutoff`, `audit-classify-deficiency-severity-cd-sd-mw`), +3 trees (ASC-606 rev-rec timing; audit deficiency CD/SD/MW; treasury cash-shortfall response ladder). Deepen finance-decision-trees + variance-root-cause.
- **regulatory-compliance** — minor. +2 BP (`reporting-classify-the-entity-before-you-file`, `bermuda-state-the-capital-regime-before-you-model`), +2 trees (which-return/entity-classification; Bermuda class & capital regime). Bermuda agent currently has ZERO dedicated rule/tree.
- **edtech-partner-success** — COMPREHENSIVE. +0 BP, +1 optional tree (segment-equivalent privacy regime FERPA/higher-ed/GDPR — closes stated segment-agnosticism gap).
- **applied-statistics** — COMPREHENSIVE. +0 BP, +1 tree (FWER-vs-FDR multiple-comparison method choice — only genuine branching gap).
- C3 total: **4 BP, 7 trees.**

### C4 dev/CRM/web/core (in)
- **salesforce** — COMPREHENSIVE. +0/+0 (49 BP / 31 trees already saturate the space).
- **tableau** — COMPREHENSIVE. +0/+0 (26 BP / 14 unique trees).
- **web-design** — MATERIAL (trees only; BP library comprehensive). +0 BP, +6 trees (IA flat/hier/hub-spoke; conversion intervention; content KKCR; technical-SEO method; responsive breakpoint-vs-container; CMS headless-vs-traditional). Home: new `knowledge/ux-content-ia-decision-trees.md` or extend web-design-decision-trees.
- **ravenclaude-core** — COMPREHENSIVE by design (domain-neutral; BP = protocols in CLAUDE.md + repo-root docs/best-practices). +0/+0 (proposing domain BP would violate house rule).
- C4 total: **0 BP, 6 trees.**

## PANEL 1 FINAL TALLY: 27 best-practices + 29 trees proposed across 16 plugins.
- At 98% bar already (no change): edtech-partner-success, applied-statistics, salesforce, tableau, ravenclaude-core.
- Material gaps: microsoft-fabric (warehouse craft), data-platform (pipeline observability/schema drift), web-design (tree surface).
- Minor gaps: power-platform, m365-copilot, microsoft-graph, azure-cloud, claude-app-engineering, finance, regulatory-compliance, ai-coding-model-guidance.

## Panel 2 — independent gap analysis (vs Panel 1)

### C1 Microsoft (in)
- **power-platform**: AGREE 4, CUT 0, ADD 0. (Scope caveat: connector tree must not re-tread PA-vs-LogicApps-vs-Function.)
- **microsoft-fabric**: AGREE 4 (3 BP + security tree), CUT 1 → **TIEBREAK: RTI-alerting tree** (P1=tree / P2=agent-prose, no real branch). Scope caveat: warehouse-security BP defers two-plane model to existing workspace-domain-governance BP.
- **microsoft-365-copilot**: AGREE 0, CUT 3 → **TIEBREAK ×3**: eval BP (P2: already a shipped skill `copilot-agent-eval-harness` + house opinion #15), adaptive-cards BP (P2: established agent prose), eval/monitoring tree (P2: not a branch).
- **microsoft-graph**: AGREE 5, CUT 0, ADD 0. (Scope: mail-attachments BP avoid overlap with file-upload tree.)

### C2 Cloud/AI/data (in)
- **azure-cloud**: AGREE 2 (`data-tier-pick-the-azure-database`, `migration-assess-then-iac`), CUT 4 → **TIEBREAK**: `network-front-door-waf-ddos` (P2: already in networking knowledge:13-21), `reliability-multi-region-bcdr` (P2: already in landing-zones:35-36 + region tree), Resilience-ladder tree + Data-tier tree (P2: redundant / fold to BP).
- **claude-app-engineering**: AGREE 2 BP + 1 tree, CUT 2 → `streaming-design-token-ux` (P2: web-design lane + reliability BP covers it — P1 already flagged borderline; low-contest), version-migration tree (P2: linear procedure not a branch, fold into BP). Document-input tree + multimodal BP + model-migrate BP all AGREE.
- **data-platform**: AGREE 2 BP + 1 tree, CUT 3 → **TIEBREAK (material-vs-minor)**: P1 said MATERIAL; P2 says MINOR — spreadsheet-migration (already database-setup-guide.md:13-14,50,74) + reverse-ETL (already etl-pipeline-engineer.md:54 + ipaas knowledge) covered; schema-change tree folds into pipeline-failure tree. Keep: schema-drift BP, row-count-reconcile BP (re-scope off freshness), pipeline-failure tree.
- **ai-coding-model-guidance**: AGREE 2 reasoning-rules but **reframe (semi-disagree)**: keep them as named sections IN the lineup file, NOT a best-practices/ dir; cut trees +3 → +1 max (keep reasoning-vs-bigger-model dial only). §7 governs volatile facts, not durable reasoning — so +2 reasoning is OK in-file.

### C3 business — PENDING
### C4 dev/CRM/web/core — PENDING

## Tiebreak queue (Panel 3) — material disagreements only
1. m365-copilot: are eval-BP / adaptive-cards-BP / eval-tree real gaps, or already covered by the shipped skill + agent prose? (P2 strongly says covered.)
2. azure-cloud: are BCDR-by-tier + Front-Door-WAF real BP gaps, or already in knowledge? + are the 2 trees redundant?
3. data-platform: MATERIAL or MINOR? (spreadsheet-migration + reverse-ETL already covered per P2.)
4. microsoft-fabric: RTI-alerting — tree or agent-prose?
5. ai-coding-model-guidance: trees +3 or +1; BP-dir vs in-file sections.

## Status log
- 2026-06-01: Panel 1 complete (27 BP + 29 trees). Panel 2 C1+C2 in — pattern is Panel 1 OVER-added (P2 cut 4 in C1, 11 in C2; 0 ADDs). Strong convergence: power-platform, microsoft-graph, claude-app (mostly). Awaiting Panel 2 C3+C4, then Panel 3 tiebreak on the queue above.
