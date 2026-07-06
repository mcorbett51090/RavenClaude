# Measure with the metric that matches the decision

**Status:** Absolute rule
**Domain:** Task framing / evaluation
**Applies to:** `computer-vision-engineering`

> Engineering rule. Metric definitions are durable; the operating point is `[verify-at-use]` per use-case. No PII.

---

## Why this exists

A single accuracy number hides the decision the system actually makes. A defect detector that is "98% accurate" can still miss every defect if defects are 2% of the data — accuracy rewards it for saying "fine" every time. The metric has to mirror the cost of the specific mistake: a false negative on a safety defect and a false positive that halts a line are not equal, and the operating point (the threshold you run at) is where that cost lives. Pick the metric and the operating point before training, because they are the acceptance criterion the model is built against.

## How to apply

- Choose the metric from the task and the cost: mAP/IoU for detection/segmentation, precision/recall at a stated threshold for a cost-asymmetric classifier.
- **State the operating point up front** — the false-positive rate (or recall floor) you can live with — `[verify-at-use]` per use-case.
- Report per-class and per-slice, never just the average — a dead rare class hides behind a high mean.
- Make the metric the acceptance criterion in the eval harness, so "better" is defined before anyone trains.

**Do:** derive the metric from the cost of a miss; fix the operating point before training.
**Don't:** optimize overall accuracy on an imbalanced or cost-asymmetric problem.

## Edge cases / when the rule does NOT apply

Early exploration can use a quick proxy metric to iterate — but no result is trusted until it's measured with the decision-matching metric at the stated operating point.

## See also

- [`../skills/cv-task-and-data-strategy/SKILL.md`](../skills/cv-task-and-data-strategy/SKILL.md)
- Template: [`../templates/cv-evaluation-plan.md`](../templates/cv-evaluation-plan.md)

## Provenance

Codifies `cv-systems-architect` house opinion and the vision-task-selection tree. Metric definitions: [`../knowledge/cv-reference-2026.md`](../knowledge/cv-reference-2026.md) (operating point verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
