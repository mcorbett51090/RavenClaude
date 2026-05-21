# Power Platform scenarios bank

> Unverified, dated, scope-tagged narratives from real Power Platform engagements. The first plugin to enable the marketplace-wide scenarios bank (v0.1.0 of the feedback loop, 2026-05-21).

This directory holds **scenarios** — war stories of "we hit X problem, here was the scenario, these were our permissions, we tried A/B/C, D worked." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install` (privacy-protected by the `/wrap` scrub step that strips client-identifying info)
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble

For the full architecture, see [`../../ravenclaude-core/skills/scenario-retrieval.md`](../../ravenclaude-core/skills/scenario-retrieval.md). For how to contribute a scenario, see [`../../ravenclaude-core/commands/wrap.md`](../../ravenclaude-core/commands/wrap.md) (`/wrap` slash command).

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: power-platform
product: <dataverse | power-automate | power-apps | power-bi | etc.>
product_version: <"2026.04" | "unknown">
scope: tenant-specific | version-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Permissions context
## Attempts
## Resolution
```

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-05-21-spn-flow-create-403.md`](2026-05-21-spn-flow-create-403.md) | likely-general | spn, dataverse, application-user, 403, permissions | medium |
| [`2026-05-21-pa-management-api-roles-null.md`](2026-05-21-pa-management-api-roles-null.md) | likely-general | spn, pa-management-api, oauth, client-credentials, 401, roles-null | high |
| [`2026-05-21-flow-clientdata-shape-drift.md`](2026-05-21-flow-clientdata-shape-drift.md) | version-specific | dataverse-web-api, workflow-entity, clientdata, flow-import | high |

## Promotion path (deferred to v0.2.0+)

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent will eventually propose promotion to `docs/best-practices/`. As of v0.1.0, promotion is manual:

1. A maintainer notices 2 scenarios converging
2. Drafts a best-practices doc by hand from the scenario contents
3. Promotes via the existing `/review-staged-contributions` flow
4. Leaves the scenarios in place (the narrative remains useful as context even after the rule is canonicalized)

## TODO for other plugins

Other plugins do **not** yet have a `scenarios/` directory. To enable the bank in a plugin:

1. Create `plugins/<plugin>/scenarios/`
2. Drop a `README.md` (copy the structure above; replace plugin-specific anchors)
3. Add the inline-prior pattern (see [`../../ravenclaude-core/skills/scenario-retrieval.md`](../../ravenclaude-core/skills/scenario-retrieval.md) §"Inline-prior pattern for agents") to the plugin's most-likely-to-benefit agents
4. Remove the `TODO: enable scenarios bank when first lesson surfaces` line from the plugin's CLAUDE.md

The trigger to enable a plugin's scenarios bank is **the first real engagement scenario that lands** — don't pre-create empty banks across the marketplace. The point is for the bank to exist where there's actual material.
