# Evaluate in the wild, not just on the benchmark

**Status:** Absolute rule
**Domain:** Evaluation / monitoring
**Applies to:** `computer-vision-engineering`

> Engineering rule. A benchmark number is not a production guarantee. Metric specifics `[verify-at-use]`. No PII.

---

## Why this exists

A held-out test split is not production. A model that scores 95% on a curated split can fail constantly in the field because production has different lighting, cameras, angles, occlusion, and a distribution the split never captured — and because a single average metric hides the slices that matter. The only score that counts is measured on data that looks like production, per-slice, and tracked over time, because the world drifts: new products, new cameras, seasonal changes all move the distribution out from under a model that was accurate at launch.

## How to apply

- Build the eval set from real production-like data — the actual cameras, lighting, and distribution, including the hard and rare cases.
- Report per-class and per-slice metrics, not just the average, so a dead slice can't hide.
- Keep a fixed regression suite so a "better" model can't silently regress an important slice.
- Monitor for drift once live — track the metric (or a proxy) on fresh data and alarm when the distribution or score moves.

**Do:** evaluate on production-like data, per-slice, and watch for drift.
**Don't:** trust a benchmark split as evidence the system works in the field.

## Edge cases / when the rule does NOT apply

Early model selection can compare candidates on a clean benchmark split for speed — but no candidate is declared good until it's measured on production-like data at the operating point.

## See also

- [`../skills/cv-model-training-and-evaluation/SKILL.md`](../skills/cv-model-training-and-evaluation/SKILL.md)
- Template: [`../templates/cv-evaluation-plan.md`](../templates/cv-evaluation-plan.md)

## Provenance

Codifies `cv-model-engineer` house opinion and the eval discipline. Metric definitions: [`../knowledge/cv-reference-2026.md`](../knowledge/cv-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
