---
description: "Frame the vision task (classification / detection / segmentation / OCR / pose / tracking / VLM), decide build-vs-fine-tune-vs-API jointly with the deployment target, choose the model family, and name the metric and operating point — with a data & annotation strategy (model/metric specifics verify-at-use)."
argument-hint: "[vision problem + data you have/can label + where it must run]"
---

You are running `/computer-vision-engineering:choose-cv-approach`. Use `cv-systems-architect` + the `cv-task-and-data-strategy` skill.

> Engineering judgment, not a benchmark or compliance verdict. Every model name/version, accelerator spec, and accuracy/latency detail is `[verify-at-use]`. No PII, no image data stored.

## Steps
1. Capture the decision the system must make, the data available or affordable to label, and the deployment target (not the newest model).
2. Traverse the **vision-task selection**, **build-vs-fine-tune-vs-API**, **model-family choice**, and **deployment-target choice** trees in `knowledge/cv-decision-trees.md`.
3. Decide the task, the build-vs-API call (jointly with the target), and the model family — each model/version specific flagged `[verify-at-use]`.
4. Name the metric and the operating point that mirror the cost, and outline the data & annotation strategy (schema + active-learning loop).
5. Emit using `templates/cv-project-architecture.md` + the Structured Output block, handing training/eval to `cv-model-engineer` and export/latency to `vision-deployment-engineer`.
