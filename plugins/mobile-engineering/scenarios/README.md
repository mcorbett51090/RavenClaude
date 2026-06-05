# Mobile Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real mobile engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real mobile work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: mobile-engineering
product: <ios | android | react-native | flutter | swiftui | jetpack-compose | generic | etc.>
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
| [`2026-06-05-cold-start-jank-main-thread.md`](2026-06-05-cold-start-jank-main-thread.md) | likely-general | cold-start, jank, main-thread, startup, profiling | high |
| [`2026-06-05-offline-sync-conflict-duplication.md`](2026-06-05-offline-sync-conflict-duplication.md) | likely-general | offline-first, sync, conflict, idempotency, last-write-wins | high |
| [`2026-06-05-ios-code-signing-release-pipeline.md`](2026-06-05-ios-code-signing-release-pipeline.md) | likely-general | code-signing, ci, fastlane, provisioning, release | medium |
| [`2026-06-05-push-notification-delivery-gaps.md`](2026-06-05-push-notification-delivery-gaps.md) | likely-general | push, apns, fcm, delivery, background, doze | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
