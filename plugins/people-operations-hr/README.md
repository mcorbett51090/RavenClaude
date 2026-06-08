# people-operations-hr

The **internal HR & People Operations** plugin. This plugin's team helps you run structured hiring
pipelines, design interview loops and scorecards, build compensation bands and leveling frameworks,
facilitate performance calibration, and measure attrition and engagement ethically — so your People
team operates on evidence and structure, not gut feel and ad-hoc decisions.

> **The one-line philosophy:** structured process beats gut feel, and every consequential people
> decision — who to hire, how to level, what to pay, how to rate — deserves a documented, repeatable
> method that doesn't quietly favor the incumbent or the loudest manager.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Design our onboarding / choose an HRIS / write an HR policy" | **people-operations-hr** (`people-ops-lead`) |
| "Design an interview loop / write a scorecard / reduce hiring bias" | **people-operations-hr** (`talent-acquisition-strategist`) |
| "Build comp bands / calibrate performance / run a merit cycle / pay equity" | **people-operations-hr** (`performance-and-comp-analyst`) |
| "Analyze attrition / build a headcount plan / design people analytics ethically" | **people-operations-hr** (`people-analytics-engineer`) |
| "Run a staffing agency / manage client requisitions / bill contract staff" | `staffing-operations` |
| "Model headcount cost / budget the merit pool / forecast comp expense" | `finance` |
| "Build the data pipeline / warehouse schema for people data" | `data-platform` |
| "Run a regression / significance test on people data" | `applied-statistics` |

## What's inside

- **4 agents** — `people-ops-lead`, `talent-acquisition-strategist`, `performance-and-comp-analyst`,
  `people-analytics-engineer`.
- **3 skills** — `structured-hiring`, `performance-and-calibration`, `comp-bands-and-leveling`.
- **3 commands** — `/people-operations-hr:design-interview-loop`,
  `:build-comp-bands`, `:run-calibration`.
- **2 templates** — `interview-scorecard`, `leveling-matrix`.
- **Knowledge bank** — `knowledge/people-ops-decision-trees.md`: Mermaid trees for
  level/comp-band placement, build-vs-buy ATS/HRIS, and performance-model selection, plus a dated
  2026 capability map.
- **6 best-practices** and **1 advisory hook** (flags biased job-description language, plaintext
  PII, unanchored comp figures, interviews without structured scorecards).
- **`scripts/people_calc.py`** — comp-ratio, time-to-fill, annualized attrition, span of control,
  offer-accept rate.

## House opinions (the short list)

1. Structured process beats gut feel for every consequential people decision.
2. Comp and PII are need-to-know; handle with explicit audience awareness.
3. Performance is a system (continuous feedback), not an annual event.
4. People analytics measures the system — never punishes the individual.
5. Set the band before you make the offer, not after the finalist is chosen.
6. Calibrate to fight rater bias before ratings or merit dollars are communicated.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
