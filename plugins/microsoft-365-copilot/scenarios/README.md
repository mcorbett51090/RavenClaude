# Microsoft 365 Copilot extensibility scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) M365 Copilot extensibility engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engagement war stories of "we were extending Copilot, hit problem X, here was the situation, these were the constraints, we tried A/B/C, D fixed it." Unlike the canonical knowledge bank (curated, maintainer-reviewed, in [`../knowledge/`](../knowledge/)), scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced behind the mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

These are **extensibility-engineering** field notes — a declarative agent that won't surface, a connector that overshares, an API-plugin OBO loop, a grounding-freshness gap. The "Resolution" is a design/config move grounded in the cited knowledge bank, not a black-box code fix.

## The 9-field schema (mirrors the marketplace scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: microsoft-365-copilot
product: <declarative-agent | copilot-connector | api-plugin | custom-engine-agent | copilot-governance>
product_version: <"DA manifest v1.7" | "plugin manifest v2.x" | "unknown">    # the surface ships ~monthly — pin what you saw
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (tenant/licensing/permissions posture — the analogue of "Constraints context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** tenant-identifying info, no real org names, no secrets, no app/client IDs, no SharePoint URLs attributable to a named tenant. Numbers and names are illustrative or marked `[ESTIMATE]`. This mirrors the `/wrap` scrub discipline and the plugin's advisory-not-deploying posture (CLAUDE.md §6 — the consumer's tenant lives outside the repo).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-declarative-agent-scope-too-broad.md`](2026-06-05-declarative-agent-scope-too-broad.md) | likely-general | declarative-agent, instructions, scope, grounding, rai-validation | medium |
| [`2026-06-05-connector-everyone-acl-oversharing.md`](2026-06-05-connector-everyone-acl-oversharing.md) | likely-general | graph-connector, acl, oversharing, semantic-label, recrawl | high |
| [`2026-06-05-api-plugin-obo-auth-loop.md`](2026-06-05-api-plugin-obo-auth-loop.md) | likely-general | api-plugin, oauth, on-behalf-of, entra, operationid, consent | medium |
| [`2026-06-05-agent-not-surfacing-in-copilot.md`](2026-06-05-agent-not-surfacing-in-copilot.md) | likely-general | agent-registry, publish, admin-gate, license, conversation-starters, surfacing | medium |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank. Because the Copilot surface ships ~monthly, weigh a scenario's `product_version` and `contributed_at` heavily — a connector or manifest detail from two quarters ago may already be stale (`[verify-at-build]`).
