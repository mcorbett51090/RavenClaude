# Microsoft Graph scenarios bank

> Unverified, dated, scope-tagged narratives from real Microsoft Graph engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real Graph development. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) (the Mermaid decision trees) and [`../best-practices/`](../best-practices/); scenarios never replace it.

**No secrets / no tenant identifiers.** A scenario never carries a real client secret, certificate, tenant ID, app ID, or any other credential — secret/credential handling escalates to `ravenclaude-core/security-reviewer` (CLAUDE.md §3 #8, §8).

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: microsoft-graph
product: <graph-api | entra-id | exchange-online | teams | sharepoint | onedrive | generic>
product_version: <"v1.0" | "beta" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Constraints context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-throttling-429-retry-after-cascade.md`](2026-06-05-throttling-429-retry-after-cascade.md) | likely-general | throttling, 429, retry-after, backoff, batch | high |
| [`2026-06-05-app-only-consent-failure.md`](2026-06-05-app-only-consent-failure.md) | likely-general | consent, application-permission, admin-consent, delegated, 403 | high |
| [`2026-06-05-delta-query-410-resync.md`](2026-06-05-delta-query-410-resync.md) | likely-general | delta-query, paging, deltatoken, 410-gone, resync | medium |
| [`2026-06-05-subscription-silent-expiry.md`](2026-06-05-subscription-silent-expiry.md) | likely-general | change-notifications, subscription, renewal, lifecycle, webhook | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or a `best-practices/` rule. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context. Several of these scenarios already have a canonical home in `best-practices/` (cross-referenced in each file); the scenario is the *war story* behind the rule, not a substitute for it.
