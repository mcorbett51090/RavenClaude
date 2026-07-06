# Prefer the least-effort path

**Rule.** Take the cheapest path that clears the accuracy bar: **zero-shot
foundation model → fine-tune a pretrained backbone → train custom.** Justify every
step up — each costs data, time, and MLOps.

**Why.** Foundation models (open-vocabulary detectors, SAM-family segmenters,
vision-LLMs) now solve zero-shot what used to need a labeled dataset. Training when
you didn't need to is the most expensive avoidable mistake in a CV project.

**Smell.** Commissioning a thousand-image labeling run before anyone tried an
open-vocab detector or SAM as a baseline; "train from scratch" proposed for a
problem close to pretraining distribution.

**Cite:** plugin §4.4; the data-availability branch of
`knowledge/cv-task-to-model-decision-tree.md`.
