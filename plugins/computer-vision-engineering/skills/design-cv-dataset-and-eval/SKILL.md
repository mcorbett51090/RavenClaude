---
name: design-cv-dataset-and-eval
description: "Design the dataset, annotation protocol, and evaluation for a CV task: label schema + labeling QA, a train/val/test split that honors real distribution shift (no scene/clip leakage), the task-appropriate metric with an acceptance threshold, and failure-slice analysis. Reach for this BEFORE training — a leaky eval makes every later number a lie."
---

# Skill: Design the CV Dataset & Eval

A held-out test set that mirrors production is worth more than a bigger model. This
skill designs the data + eval so the accuracy number is trustworthy. Driven by
`cv-systems-architect`; executed with `cv-implementation-engineer`.

## Step 1 — Label schema & annotation protocol

- Define the classes precisely, with edge-case rules written down (what counts as
  a "defect"? partial objects? occlusion?). Ambiguous schema → inconsistent labels
  → a ceiling on achievable accuracy.
- Choose the label type to match the task: boxes (detection), polygons/masks
  (segmentation), transcriptions (OCR), keypoints (pose).
- **QA the labels**: double-label a sample and measure inter-annotator agreement;
  disagreement above a small threshold means the schema is underspecified, not that
  the annotators are bad.

## Step 2 — Split against the REAL distribution shift

This is the step most projects get wrong:

- **Never split at the frame level when frames come from clips/scenes.** Adjacent
  frames are near-duplicates; frame-level splitting leaks the test set into training
  and inflates the metric. Split by **scene / clip / camera / patient / site**.
- The test set must mirror **production** variation: lighting, camera, angle,
  season, device. If production has night footage and your test set is all daytime,
  the metric is fiction.
- Hold out a **hard slice** deliberately (rare classes, worst lighting) so you can
  report worst-case, not just average.

## Step 3 — Pick the metric + acceptance threshold

| Task | Metric | Report |
|---|---|---|
| Classification | Accuracy / macro-F1 | Per-class, plus a confusion matrix. |
| Detection | mAP@[.5:.95] | Per-class AP + the operating confidence threshold. |
| Segmentation | IoU / Dice | Overall + small-object + boundary. |
| Tracking | MOTA / IDF1 | ID switches vs detection errors separately. |
| OCR | CER / WER | Character vs layout errors separately. |

State the **threshold that means ship** up front — decide "good enough" before you
see the number, not after.

## Step 4 — Failure-slice analysis (not one aggregate number)

A single headline metric hides where the model fails. Break results down by class,
by lighting/scene, by object size, by the hard slice. The failure slices are the
next iteration's work list (more labels, targeted augmentation, or a task re-frame).

## Step 5 — Consider data efficiency before labeling more

Before commissioning a big labeling run: try a zero-shot foundation model as a
baseline; use **active learning** (label the model's most-uncertain examples
first); consider **synthetic/augmented** data for rare cases. Labeling is the most
expensive line in a CV project — spend it where it moves the failure slices.

## Step 6 — Output

A dataset+eval plan: **schema + labeling protocol & QA + the split rule (the
leakage boundary named explicitly) + the metric & ship threshold + the failure
slices to track.** This plan is the contract `cv-implementation-engineer` builds and
reports against.
