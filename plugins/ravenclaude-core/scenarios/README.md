# ravenclaude-core scenarios bank

> Unverified, dated, scope-tagged narratives about **agentic orchestration** — the Team-Lead / dispatch pattern and the plugin's own epistemic protocols. Added as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — war stories of "the orchestration hit failure-mode X, here was the situation, these were the constraints, we tried A/B/C, D was the move that worked." Unlike a domain plugin's scenarios (a vet-clinic throughput problem, a Power Platform 403), these are **domain-neutral orchestration scenarios**: a mis-routed dispatch, a worker that tried to orchestrate, a false-negative blocked report, a decision routed past the safety envelope. The "Resolution" is a *procedural* move grounded in the plugin's own constitution — not a code fix.

Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../skills/scenario-retrieval/SKILL.md`](../skills/scenario-retrieval/SKILL.md), which this plugin itself defines)

These teach the plugin's **own** patterns: route-before-spawning, the orchestrator-worker hierarchy and recursion guard, the Capability Grounding Protocol (alternate-methods + read-the-error + honest blocked-reporting), and the comfort-posture / decision-review tribunal envelope. They are grounded in the constitution + best-practices, not external facts; volatile or install-specific details carry a `[verify-at-use]` marker.

## The schema (the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: ravenclaude-core
product: orchestration
product_version: "n/a"          # protocol/pattern, not a versioned product
scope: tenant-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (surface, the rule that was violated, why it slipped)
## Attempts
## Resolution
```

> **Privacy:** these scenarios carry **no** consumer-identifying info, no repo names, no real engagement details — they are pattern narratives about the orchestration protocols themselves. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Teaches | Confidence |
|---|---|---|---|
| [`2026-06-05-keyword-routed-to-wrong-specialist.md`](2026-06-05-keyword-routed-to-wrong-specialist.md) | likely-general | route-before-spawning — traverse the routing tree, don't keyword-match to an agent name; earliest-blocking gate wins | medium |
| [`2026-06-05-subagent-tried-to-spawn-subagents.md`](2026-06-05-subagent-tried-to-spawn-subagents.md) | likely-general | orchestrator-worker hierarchy + recursion guard — a worker escalates a structured handoff, it does not dispatch peers | medium |
| [`2026-06-05-blocked-report-skipped-alternate-methods.md`](2026-06-05-blocked-report-skipped-alternate-methods.md) | likely-general | Capability Grounding — read the error, enumerate alternatives, load the deferred/MCP route before reporting "can't" | medium |
| [`2026-06-05-decision-routed-to-tribunal-not-human.md`](2026-06-05-decision-routed-to-tribunal-not-human.md) | likely-general | decision-review envelope — route every yes/no, but high-blast + genuine-preference calls always `defer` to the human | medium |

## How agents use this bank

Per [`../skills/scenario-retrieval/SKILL.md`](../skills/scenario-retrieval/SKILL.md): glob this directory, filter by `tags`/`scope`, surface at most the top 2-3 matches, and **always** lead with the mandatory unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment before applying"). Scenarios are **secondary** to the canonical constitution + `knowledge/` files — never let a scenario override a canonical routing tree, the orchestration rules, or the CGP/decision-review safety envelope. The most-likely-to-benefit consumer is the **Team Lead** (routing + dispatch + decision-routing) and any specialist about to file a blocked report.

## Promotion path

When ≥2 independent scenarios (different sessions / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../knowledge/orchestration-decision-trees.md`](../knowledge/orchestration-decision-trees.md) or `docs/best-practices/`. Promotion is manual; leave the scenario in place even after the rule is canonicalized — the narrative stays useful as context.
