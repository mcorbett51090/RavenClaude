# Applied-statistics scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) applied-statistics consulting engagements. Enabled as part of the value-add build-out (2026-06-05). Section 8b of the plugin [`CLAUDE.md`](../CLAUDE.md) (formerly the "TODO (planned)" placeholder) now points here.

This directory holds **scenarios** — engagement war stories of "the team had statistical question X, here was the data + constraints, we tried A/B/C, and D was the defensible read." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with a mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a code-vertical scenarios bank (a 403, a token error), these are **methodology engagements**: a false-discovery scare across many segments, an underpowered "no significant difference" read, a Simpson's-paradox reversal, a peeked-at A/B test. The "Resolution" is an *analytical* move plus the defensible verdict it produced — not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: applied-statistics
product: <hypothesis-testing | experiment-design | regression-forecasting | statistical-qa | causal-inference>
product_version: "n/a"          # non-code vertical — no product version
scope: engagement-specific | domain-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (data shape, sample size, design constraints — the non-code analogue of "Permissions context")
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** client-identifying info, no real company names, no proprietary metric values attributable to a named client. Numbers are illustrative ranges, marked `[ESTIMATE]`, or carry a public-source citation. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-segment-false-discovery-scare.md`](2026-06-05-segment-false-discovery-scare.md) | likely-general | multiple-comparisons, false-discovery, fdr, segments, benjamini-hochberg | medium |
| [`2026-06-05-underpowered-no-significant-difference.md`](2026-06-05-underpowered-no-significant-difference.md) | likely-general | underpowered, null-result, power, mde, equivalence | medium |
| [`2026-06-05-simpsons-paradox-conversion-reversal.md`](2026-06-05-simpsons-paradox-conversion-reversal.md) | likely-general | simpsons-paradox, confounding, aggregation, segmentation, causal | medium |
| [`2026-06-05-ab-peeking-early-stop.md`](2026-06-05-ab-peeking-early-stop.md) | likely-general | ab-testing, peeking, sequential, type-i-error, stopping-rule | medium |

## Coordination with experimentation-growth-engineering

The A/B-peeking scenario sits on the seam with the `experimentation-growth-engineering` plugin. **The lane split:** that plugin owns the *experiment apparatus* (assignment, exposure logging, feature flags, the sequential-testing harness that makes peeking safe); this plugin owns the *statistical verdict* (is the result valid given how it was collected?). The peeking scenario below is written from the **verdict** side — it diagnoses the inference error and names the fix, then hands the apparatus build-out to that plugin. Don't duplicate the harness narrative here.

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank ([`../knowledge/`](../knowledge/)) or the [`../best-practices/`](../best-practices/) rules. The canonical method always wins; the scenario is the war story beside it.
