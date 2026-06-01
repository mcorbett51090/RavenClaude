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

### C3 business domains — PENDING
### C4 dev/CRM/web/core — PENDING

## Status log
- 2026-06-01: baseline taken; Panel 1 launched. C1 + C2 reported (23 BP + 16 trees proposed so far). Awaiting C3, C4.
