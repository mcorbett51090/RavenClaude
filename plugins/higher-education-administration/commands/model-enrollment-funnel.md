---
description: "Model an entering class stage-by-stage (inquiry->apply->admit->yield->melt) and its net tuition revenue at each aid scenario, naming the leaking stage and the cheapest lever (verify-at-use)."
argument-hint: "[institution/program + entering term + known stage counts or rates + discount rate]"
---

You are running `/higher-education-administration:model-enrollment-funnel`. Use `enrollment-management-strategist` + the `enrollment-funnel-and-yield` and `financial-aid-and-discount-rate` skills.

> Advisory, not financial-aid-compliance advice. Every benchmark / discount-rate norm is `[verify-at-use]` against the institution's IR definitions. Cohort-level only — no student PII.

## Steps
1. Capture the funnel inputs (inquiries, apply/admit/yield/melt rates, discount rate) and attach each stage **definition** from the institution's IR office.
2. Traverse the **yield/melt intervention** and **discount-rate / aid-leverage decision** trees in `knowledge/higher-ed-decision-trees.md`.
3. Decompose the target: class = inquiries × apply rate × admit rate × yield × (1 − melt); find the stage that moved vs prior cohort.
4. Model **net tuition revenue** at each discount scenario and state the break-even yield — flag every benchmark `[verify-at-use]`.
5. Name the leaking stage, its cheapest lever, and the responsive aid segment.
6. Emit using `templates/enrollment-funnel-model.md` + the Structured Output block.
