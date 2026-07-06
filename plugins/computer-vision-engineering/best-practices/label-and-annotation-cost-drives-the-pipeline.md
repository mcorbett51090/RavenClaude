# Label and annotation cost drives the pipeline

**Status:** Pattern
**Domain:** Data strategy / annotation
**Applies to:** `computer-vision-engineering`

> Engineering rule. Annotation-tool specifics `[verify-at-use]`. No PII, no image data stored.

---

## Why this exists

On most production vision projects, annotation — not training or inference — is the dominant cost and the real bottleneck. Every design decision that ignores this pays for it later: a task framing that needs pixel-perfect masks when boxes would do, a one-shot "label everything" dump that spends the budget on redundant easy images, or a labeling workflow with no consistency checks that produces the noisy labels that cap the metric. Designing the annotation strategy — schema, workflow, quality, and an active-learning loop — is designing the pipeline.

## How to apply

- Choose the annotation type deliberately — the cheapest that supports the task (image labels < boxes < polygons/masks < keypoints in cost).
- Spend the budget with active learning: uncertainty/margin sampling, diversity, and hard-negative / failure-case mining pick the images that buy the most metric per label.
- Build a labeling workflow with consistency checks and inter-annotator agreement — noisy labels cap the achievable metric.
- Consider model-assisted / auto-labeling to speed correction, but watch for propagating the model's own bias.

**Do:** design an active-learning loop and a quality process; label the images that move the metric.
**Don't:** dump a one-shot labeling batch and assume more labels equals better.

## Edge cases / when the rule does NOT apply

If a general vision API or zero-shot foundation model already solves the task well enough, you may need little or no annotation — decide build-vs-API first (that's when this rule is cheapest to honor).

## See also

- [`../skills/cv-task-and-data-strategy/SKILL.md`](../skills/cv-task-and-data-strategy/SKILL.md)
- [`./data-quality-and-labels-beat-model-choice.md`](./data-quality-and-labels-beat-model-choice.md)

## Provenance

Codifies `cv-systems-architect` and `cv-model-engineer` house opinion and the build-vs-fine-tune-vs-API tree. Annotation-tool landscape: [`../knowledge/cv-reference-2026.md`](../knowledge/cv-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
