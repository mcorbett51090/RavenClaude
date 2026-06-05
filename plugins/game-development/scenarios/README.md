# Game Development scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) game-development engagements. Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — engineering and production war stories of "we hit problem X, here was the situation, these were the constraints, we tried A/B/C, D worked." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

This is a **code vertical**: the scenarios lean toward the runtime/engineering craft (frame budget, draw-call batching, netcode model, save migration) where the "Resolution" is a diagnosis order plus a code fix, alongside the plugin's production/design lane. Scenarios never replace the cited knowledge bank.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: game-development
product: <unity-csharp | generic-engine | generic-multiplayer | godot-gdscript | unreal | etc.>
product_version: <"2026.04" | "unknown">
scope: project-specific | engine-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (genre, platform, engine, constraints — the analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** studio-identifying info, no unreleased-title names, no player PII, and no real revenue figures attributable to a named studio. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public source. This mirrors the marketplace `/wrap` scrub discipline and the team's §2 (the team stores no player PII).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-frame-time-gc-hitch.md`](2026-06-05-frame-time-gc-hitch.md) | likely-general | frame-time, gc, hitch, allocation, object-pool, profiler | high |
| [`2026-06-05-draw-call-batching-perf.md`](2026-06-05-draw-call-batching-perf.md) | likely-general | draw-calls, batching, cpu-bound, atlas, material, gpu-instancing | high |
| [`2026-06-05-netcode-lag-rollback.md`](2026-06-05-netcode-lag-rollback.md) | likely-general | netcode, rollback, client-prediction, lag, authority, reconciliation | medium |
| [`2026-06-05-save-system-migration.md`](2026-06-05-save-system-migration.md) | likely-general | save-system, serialization, schema-version, migration, backward-compat | high |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the mandatory unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment"), and never let a scenario override the cited knowledge bank or a measured profile of the actual game. The most-likely-to-benefit specialist is [`gameplay-engineer`](../agents/gameplay-engineer.md) (runtime/perf/netcode/save scenarios); the lead and live-ops analyst check the bank when a situation matches.
