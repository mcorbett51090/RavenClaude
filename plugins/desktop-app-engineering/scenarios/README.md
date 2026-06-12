# Desktop App Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real desktop-app work. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real desktop engagements. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: desktop-app-engineering
product: <electron | tauri | native | generic | etc.>
product_version: <"2026.04" | "unknown">
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
| [`2026-06-12-electron-nodeintegration-rce.md`](2026-06-12-electron-nodeintegration-rce.md) | likely-general | electron, security, nodeintegration, context-isolation, rce | high |
| [`2026-06-12-macos-notarization-gatekeeper-block.md`](2026-06-12-macos-notarization-gatekeeper-block.md) | likely-general | macos, signing, notarization, gatekeeper, notarytool | medium |
| [`2026-06-12-auto-update-fleet-outage.md`](2026-06-12-auto-update-fleet-outage.md) | likely-general | auto-update, rollout, rollback, signature, version-floor | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
