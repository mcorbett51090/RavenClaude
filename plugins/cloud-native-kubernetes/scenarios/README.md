# Cloud-Native & Kubernetes scenarios bank

> Unverified, dated, scope-tagged narratives from real Kubernetes engagements. War stories of "the cluster/workload hit X, here was the situation, these were the constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real cluster-operations and workload-design work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `../best-practices/`; scenarios never replace it.

These are **operational engagements**: a crash loop, a stuck rollout, an ingress/DNS failure, a cost/right-sizing review. The "Resolution" is a diagnosis-then-fix move plus a measured outcome, not just a config snippet.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: cloud-native-kubernetes
product: <kubernetes | helm | istio | ingress-nginx | gateway-api | generic | etc.>
product_version: <"1.30" | "unknown">
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

> **Safety boundary:** scenarios carry **no** cluster-identifying info, no kubeconfig contents, no real cluster names, namespaces, or secrets. Manifests are illustrative. A diagnosis from a scenario is decision-support — verify against the live cluster before applying any change, especially a destructive one (delete, rollout restart, scale-to-zero).

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-crashloopbackoff-oomkilled-triage.md`](2026-06-05-crashloopbackoff-oomkilled-triage.md) | likely-general | crashloopbackoff, oomkilled, resource-limits, probes, exit-137, triage | high |
| [`2026-06-05-rollout-stuck-pdb-deadlock.md`](2026-06-05-rollout-stuck-pdb-deadlock.md) | likely-general | rollout, pdb, maxunavailable, deadlock, drain, surge | high |
| [`2026-06-05-ingress-503-dns-and-readiness.md`](2026-06-05-ingress-503-dns-and-readiness.md) | likely-general | ingress, 503, dns, readiness-probe, endpoints, service-selector | medium |
| [`2026-06-05-cluster-cost-right-sizing.md`](2026-06-05-cluster-cost-right-sizing.md) | likely-general | cost, right-sizing, requests, bin-packing, vpa, utilization | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or a `best-practices/` rule. As of this bank's version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or override a destructive-action safety check. The most-likely-to-benefit specialists — `kubernetes-architect`, `k8s-platform-operator`, `service-mesh-networking-engineer` — should check the bank when a situation matches.
