---
description: "Build a B2B sales forecast as a methodology: choose the method and name its bias, derive coverage from win-rate, inspect the pipeline, and back-test."
argument-hint: "[target + historical deal data + current stages + where the forecast misses]"
---

You are running `/revops:build-forecast`. Use `pipeline-and-forecast-analyst` + the `forecast-methodology` skill.

## Steps
1. Inspect the pipeline first: flag stuck/aged/past-close-date/no-activity deals and report the cleaned number — no aggregate on un-inspected pipeline.
2. Choose a forecast method (weighted-by-stage vs commit/category vs AI/regression) for the data they actually have, and name its known bias.
3. Anchor each stage's probability to your own historical stage→close conversion (not the CRM defaults); report weighted and commit side by side with the gap.
4. Derive the coverage target = gap ÷ stage-weighted win-rate (never a folk 3x); compute win-rate and sales velocity and name which lever moves the number.
5. Back-test the method against recent quarters; report the bias and the tolerance.
6. Route warehouse/dashboard build → data-platform / tableau; significance questions → applied-statistics. Emit the forecast-and-pipeline spec + the Structured Output block (with `Revenue impact:` and `Handoff to system teams:`).
