# Web Design scenarios bank

> Unverified, dated, scope-tagged narratives from real web-design / build engagements. War stories of "the site had problem X, here was the situation, these were the constraints, we tried A/B/C, D fixed the number."

This directory holds **scenarios** — field notes from real web work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a _secondary_ source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `best-practices/`; scenarios never replace it. In particular, a scenario **never overrides the cited WCAG / CWV standard or a verified browser-support fact** — those are the canonical bank's lane.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: web-design
product: <html-css | react | nextjs | astro | tailwind | generic | etc.>
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

> **Privacy:** scenarios carry **no** client-identifying info, no real site names or attributable revenue figures. Numbers are illustrative ranges or carry a public-benchmark source. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-wcag-contrast-and-focus-order-audit.md`](2026-06-05-wcag-contrast-and-focus-order-audit.md) | likely-general | wcag, contrast, focus-order, keyboard, audit, remediation | high |
| [`2026-06-05-lcp-perf-budget-hero-image.md`](2026-06-05-lcp-perf-budget-hero-image.md) | likely-general | lcp, core-web-vitals, perf-budget, hero-image, preload, fonts | high |
| [`2026-06-05-design-token-drift-hardcoded-hex.md`](2026-06-05-design-token-drift-hardcoded-hex.md) | likely-general | design-tokens, drift, hardcoded-hex, dark-mode, style-dictionary | high |
| [`2026-06-05-cls-layout-shift-and-seo-meta-regression.md`](2026-06-05-cls-layout-shift-and-seo-meta-regression.md) | likely-general | cls, layout-shift, seo, meta, og, responsive | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or a `best-practices/` entry. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a _secondary_ source, always behind the unverified-scenario preamble, and never let a scenario override the cited WCAG/CWV standard or a verified browser-support fact. The most-likely-to-benefit specialists — `accessibility-auditor`, `performance-engineer`, `visual-designer`, `content-strategist` — should check the bank when a situation matches.
