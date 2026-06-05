# Security Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real security engagements. War stories of "we hit X security problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real AppSec / supply-chain / cloud-posture / threat-modeling work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it. **This team proposes; the ship/no-ship verdict on any finding routes to `ravenclaude-core/security-reviewer`** — a scenario never overrides that escalation. Scenarios carry **no secret values, tenant identifiers, or live credentials** (a leaked secret in a scenario is itself a finding).

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: security-engineering
product: <semgrep | trivy | osv-scanner | github | snyk | dependabot | generic | etc.>
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
| [`2026-06-05-dependency-cve-triage-sla.md`](2026-06-05-dependency-cve-triage-sla.md) | likely-general | cve, sca, reachability, kev, sla, supply-chain | high |
| [`2026-06-05-committed-secret-rotation-ir.md`](2026-06-05-committed-secret-rotation-ir.md) | likely-general | secret-leak, rotation, incident-response, git-history, oidc | high |
| [`2026-06-05-sast-finding-false-positive-triage.md`](2026-06-05-sast-finding-false-positive-triage.md) | likely-general | sast, semgrep, false-positive, taint, triage, signal | medium |
| [`2026-06-05-broken-object-level-authz-remediation.md`](2026-06-05-broken-object-level-authz-remediation.md) | likely-general | authz, bola, idor, access-control, multi-tenant | high |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
