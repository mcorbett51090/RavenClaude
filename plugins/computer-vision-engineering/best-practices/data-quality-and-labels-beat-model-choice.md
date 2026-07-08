# Data quality and labels beat model choice

**Status:** Absolute rule
**Domain:** Modeling / data
**Applies to:** `computer-vision-engineering`

> Engineering rule. Model/checkpoint specifics are `[verify-at-use]`. No PII, no image data stored.

---

## Why this exists

The instinct when a vision model underperforms is to reach for a bigger or newer architecture. On most real projects that is the wrong lever: inconsistent labels, mislabeled edge cases, and augmentation that doesn't reflect real-world variation cap the achievable metric no matter how good the backbone. A cleaner dataset and consistent annotations move the metric more, and more cheaply, than swapping ResNet for a ViT — and they compound, because every future model trains on the better data.

## How to apply

- Audit labels first: measure inter-annotator agreement, fix systematic labeling errors, resolve ambiguous classes.
- Design augmentation to reflect production variation — lighting, scale, occlusion, sensor/camera differences — not just the defaults.
- Prefer transfer learning from a pretrained backbone; only reach for a larger/newer architecture after the data is clean.
- Attribute a regression to data vs model deliberately — re-run the eval on a fixed, clean split before blaming the architecture.

**Do:** clean the labels and fix augmentation before upgrading the model.
**Don't:** treat a bigger backbone as the first fix for a low metric.

## Edge cases / when the rule does NOT apply

Genuinely capacity-bound problems (the model class truly can't represent the task) do need a bigger/different architecture — but confirm the data is clean first, or you'll pay for capacity you can't use.

## See also

- [`../skills/cv-model-training-and-evaluation/SKILL.md`](../skills/cv-model-training-and-evaluation/SKILL.md)
- [`./label-and-annotation-cost-drives-the-pipeline.md`](./label-and-annotation-cost-drives-the-pipeline.md)

## Provenance

Codifies `cv-model-engineer` house opinion and the model-family-choice tree. Model specifics: [`../knowledge/cv-reference-2026.md`](../knowledge/cv-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
