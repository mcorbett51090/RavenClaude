# computer-vision-engineering — best-practice docs

Named, citable rules for the `computer-vision-engineering` team's specialists. Each file is **one rule**. Engineering judgment, not a benchmark or compliance verdict; model/hardware/runtime specifics are `[verify-at-use]`; no PII, no image data stored.

---

## Index

_5 rules across the metric, the data, the deployment target, in-the-wild evaluation, and the annotation pipeline._

| Doc | Status | Use when |
|---|---|---|
| [`measure-with-the-metric-that-matches-the-decision.md`](./measure-with-the-metric-that-matches-the-decision.md) | Absolute rule | Any vision project — pick the metric and operating point that mirror the business cost before training. |
| [`data-quality-and-labels-beat-model-choice.md`](./data-quality-and-labels-beat-model-choice.md) | Absolute rule | Modeling — fix labels and augmentation before reaching for a bigger architecture. |
| [`optimize-for-the-deployment-target-from-day-one.md`](./optimize-for-the-deployment-target-from-day-one.md) | Absolute rule | Architecture & modeling — the target fixes the model-size and latency budget; choose the model with it in mind. |
| [`evaluate-in-the-wild-not-just-on-the-benchmark.md`](./evaluate-in-the-wild-not-just-on-the-benchmark.md) | Absolute rule | Evaluation — measure on the real distribution, per-slice, and watch for drift. |
| [`label-and-annotation-cost-drives-the-pipeline.md`](./label-and-annotation-cost-drives-the-pipeline.md) | Pattern | Data strategy — annotation is the dominant cost; design active learning and a labeling workflow. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile model/hardware/runtime/metric specifics live (dated, verify-at-use) in [`../knowledge/cv-reference-2026.md`](../knowledge/cv-reference-2026.md).
