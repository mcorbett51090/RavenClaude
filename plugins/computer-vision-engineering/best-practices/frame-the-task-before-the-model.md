# Frame the task before the model

**Rule.** Name the *output* the system must produce (label / boxes / mask / text /
tracks / keypoints / free-form answer) before naming any model. The task
formulation — not the model — is the highest-leverage CV decision.

**Why.** Most failed CV projects solved the wrong task: detection when the
measurement needed a segmentation mask, classification when the user needed *where*.
The model is the conclusion, not the premise.

**Smell.** A project that starts "let's use YOLO / a VLM" before anyone has stated
whether the output is boxes, masks, or text.

**Cite:** plugin §4.1; the task→model tree in
`knowledge/cv-task-to-model-decision-tree.md`.
