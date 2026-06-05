# team-portfolio scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) cross-repo activity-tracking setups. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — operations war stories of "the portfolio had problem X, here was the situation, these were the constraints, we tried A/B/C, D fixed it." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted as a _secondary_ source** — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike the veterinary-practice bank (a clinical/operations vertical), this is a **code-adjacent tooling** bank: the problems are config drift, token scope, a stale scheduled Action, and cross-repo attribution — and the "Resolution" is a config/operational fix plus a verification step, not a code change to the plugin's own scripts (the scripts are the source of truth; see [`../CLAUDE.md`](../CLAUDE.md) §4).

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: team-portfolio
product: <collector | reports | dashboard | scheduled-action | config>
product_version: "n/a"          # the plugin's scripts are stdlib tooling, not a versioned product surface
scope: setup-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (repos/team size, public vs private, Actions vs local — the analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** real org names, no private-repo contents, no individual contributor's real activity counts attributed to a named person. GitHub logins shown are illustrative placeholders (`alice`, `dependabot[bot]`), numbers are illustrative ranges or marked `[ESTIMATE]`. This mirrors the marketplace `/wrap` scrub discipline and CLAUDE.md §1–§2 (the hub reads GitHub; it stores no secrets and surfaces activity as a signal, not a verdict).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-repo-silently-dropped-from-tracking.md`](2026-06-05-repo-silently-dropped-from-tracking.md) | likely-general | config-drift, missing-repo, fail-soft, 404, onboarding | medium |
| [`2026-06-05-collector-rate-limit-and-token-scope.md`](2026-06-05-collector-rate-limit-and-token-scope.md) | likely-general | rate-limit, token-scope, 403, fine-grained-pat, private-repo | medium |
| [`2026-06-05-stale-dashboard-scheduled-action-stopped.md`](2026-06-05-stale-dashboard-scheduled-action-stopped.md) | likely-general | scheduled-action, cron, stale-dashboard, default-branch, 60-day-disable | medium |
| [`2026-06-05-project-status-misattributed-across-repos.md`](2026-06-05-project-status-misattributed-across-repos.md) | likely-general | project-filter, over-match, label, title-prefix, cross-repo-attribution | medium |

## Promotion path

When ≥2 independent scenarios (different setups / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override a canonical knowledge file ([`../knowledge/multi-repo-tracking-model.md`](../knowledge/multi-repo-tracking-model.md), [`../knowledge/team-portfolio-decision-trees.md`](../knowledge/team-portfolio-decision-trees.md)) or a best-practice rule.
