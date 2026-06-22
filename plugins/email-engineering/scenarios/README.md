# Email-engineering scenarios bank

> Unverified, dated, scope-tagged narratives from realistic email-deliverability/sending engagements. Surfaced by agents as a **secondary** source, always behind the mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md)).

This directory holds **scenarios** — war stories of "we had email problem X, here was the setup + constraints, we tried A/B/C, and D was the fix." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — never overriding the cited knowledge bank or best-practices

## The schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: email-engineering
product: <authentication | deliverability | sending-integration | templates | suppression>
product_version: "n/a"
scope: engagement-specific | domain-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no real company names, no proprietary values. Domains are `example.com`; numbers are illustrative and marked `[ESTIMATE]` or carry a public citation.

## What's in this bank

| File | Scope | Tags | Confidence |
| --- | --- | --- | --- |
| [`2026-06-13-dmarc-reject-broke-forwarding.md`](2026-06-13-dmarc-reject-broke-forwarding.md) | likely-general | dmarc, p-reject, spf, forwarding, dkim-alignment | medium |
| [`2026-06-13-gmail-yahoo-bulk-sender-compliance.md`](2026-06-13-gmail-yahoo-bulk-sender-compliance.md) | likely-general | bulk-sender, gmail, yahoo, one-click-unsubscribe, spam-rate | medium |

## How agents use this bank

Surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank ([`../knowledge/`](../knowledge/)) or the [`../best-practices/`](../best-practices/) rules. The canonical method always wins; the scenario is the war story beside it.
