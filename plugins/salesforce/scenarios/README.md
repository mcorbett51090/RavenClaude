# Salesforce scenarios bank

> Unverified, dated, scope-tagged narratives from real Salesforce engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real Salesforce platform work (Apex, Flow, Agentforce, sharing/security, governor limits). Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and [`../best-practices/`](../best-practices/); scenarios never replace it. Security verdicts (data exposure, FLS-as-control, SOQL injection) still escalate to `ravenclaude-core/security-reviewer` — a scenario informs the mechanism, never the sign-off.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: salesforce
product: <apex | flow | lwc | agentforce | experience-cloud | platform | integration | generic>
product_version: <"Spring '26" | "unknown">
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

> **Volatile-fact discipline.** Governor-limit numbers, Agentforce/Atlas/Trust-Layer behavior, and guest-user security defaults move by release. Every such number in a scenario carries a `[verify-at-build]` marker — confirm against the current Salesforce limits cheat sheet / docs before quoting it to a stakeholder. Never invent a limit.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-soql-in-loop-101-on-trigger.md`](2026-06-05-soql-in-loop-101-on-trigger.md) | likely-general | governor-limits, soql-101, soql-in-loop, bulkification, trigger, data-load | high |
| [`2026-06-05-trigger-recursion-runaway-update.md`](2026-06-05-trigger-recursion-runaway-update.md) | likely-general | trigger, recursion, recursion-guard, handler-framework, dml | high |
| [`2026-06-05-guest-user-sharing-data-exposure.md`](2026-06-05-guest-user-sharing-data-exposure.md) | likely-general | security, guest-user, sharing, crud-fls, experience-cloud, without-sharing, owd | high |
| [`2026-06-05-agentforce-nondeterministic-action-misfire.md`](2026-06-05-agentforce-nondeterministic-action-misfire.md) | likely-general | agentforce, determinism, atlas, trust-layer, topic-scope, guardrails | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or a `best-practices/` rule. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context. Each scenario above already maps to an existing canonical rule + decision tree (see its Cross-reference line), so this bank is corroboration, not new doctrine.
