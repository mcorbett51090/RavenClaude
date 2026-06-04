---
description: "Improve frontend performance to a budget: bundle code-splitting, CWV tuning, media/font optimization, hydration reduction."
argument-hint: "[perf symptom: bundle/CWV/hydration]"
---

You are running `/frontend-engineering:optimize-frontend-perf`. Use `frontend-performance-engineer` + the `frontend-performance` skill.

## Steps
1. Measure (field data + bundle analysis).
2. Code-split by route; lazy-load heavy/below-the-fold; optimize images/fonts.
3. Reduce hydration (RSC/islands); kill render-blocking/waterfalls.
4. Set a CI perf budget (with devops-cicd).
5. Emit (from `templates/perf-budget.md`) + Structured Output block.
