# Fintech & Payments Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real payments engagements. War stories of "we hit X problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real payment/billing work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment before applying.")

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `../best-practices/`; scenarios never replace it, and they never override a PCI/regulatory verdict (route those to `ravenclaude-core/security-reviewer` / `regulatory-compliance` per CLAUDE.md §3).

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: fintech-payments-engineering
product: <stripe | adyen | braintree | generic | etc.>
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
| [`2026-06-05-idempotency-key-double-charge.md`](2026-06-05-idempotency-key-double-charge.md) | likely-general | idempotency, double-charge, retries, dedup-key, psp-key | high |
| [`2026-06-05-webhook-replay-and-reconciliation.md`](2026-06-05-webhook-replay-and-reconciliation.md) | likely-general | webhook, signature, replay, dedup, reconciliation, out-of-order | high |
| [`2026-06-05-decline-retry-storm-and-dunning.md`](2026-06-05-decline-retry-storm-and-dunning.md) | likely-general | declines, hard-vs-soft, retries, backoff, dunning, network-flag | high |
| [`2026-06-05-pci-scope-creep-tokenization.md`](2026-06-05-pci-scope-creep-tokenization.md) | likely-general | pci-dss, saq-a, tokenization, scope-reduction, hosted-fields | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or a `best-practices/` rule. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.
</content>
</invoke>
