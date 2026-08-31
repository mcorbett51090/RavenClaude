# Forms-engineering scenarios bank

> Unverified, dated, scope-tagged narratives. Consulted by agents as a **secondary** source, always behind the unverified-scenario preamble in [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md).

Each file is a "the form had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number" story. Schema-validated, **not** maintainer-reviewed.

## The schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: forms-engineering
product: <form-intake | form-telemetry | form-hardening | form-platform>
product_version: "n/a"
scope: practice-specific | segment-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context
## Attempts
## Resolution
```

> **Privacy:** no client-identifying information, no real company names, no attributable figures. Numbers are illustrative and marked `[ESTIMATE]` unless they carry a public source.

## What's in this bank

| File | Scope | Tags | Confidence |
| --- | --- | --- | --- |
| [`2026-08-17-the-honeypot-flagged-real-customers.md`](2026-08-17-the-honeypot-flagged-real-customers.md) | likely-general | honeypot, assistive-tech, autofill, silent-rejection, anti-abuse | medium |
| [`2026-08-17-we-removed-fields-and-conversion-fell.md`](2026-08-17-we-removed-fields-and-conversion-fell.md) | likely-general | field-count, conversion, denominator, intake, measurement | medium |
| [`2026-08-17-the-upload-endpoint-stored-nothing.md`](2026-08-17-the-upload-endpoint-stored-nothing.md) | likely-general | attachments, storage-binding, silent-failure, observability, delivery-defect | medium |
