---
description: "Build a weighted QA scorecard for a support team — define dimensions and weights, write the scoring rubric, set calibration protocol, and specify the minimum review cadence."
argument-hint: "[team context, e.g. 'B2B SaaS chat + email team, 12 agents, currently no QA process, CSAT dropping']"
---

You are running `/customer-support-cx-operations:build-qa-scorecard`. Use the
`support-quality-analyst` discipline and the `support-quality-and-csat` skill.

## Steps

1. Gather context: channel(s), team size, existing QA process (if any), top failure themes visible
   in CSAT or manager observation, and any non-negotiable compliance dimensions.

2. Design the scorecard dimensions and weights. Default starting distribution:
   - Resolution accuracy: 40%
   - Communication quality: 25%
   - Empathy and rapport: 15%
   - Process adherence: 10%
   - Escalation discipline: 10%
   Adjust weights if the team's context demands it (e.g., a compliance-regulated team shifts
   process adherence higher). Document the rationale.

3. Write the scoring rubric for each dimension: Pass (full points), Partial (half points), Fail
   (zero). Each descriptor must be behavioral and observable — no subjective judgments without an
   anchor example.

4. Set the calibration protocol: anchor conversations per period (one clear pass, one clear fail,
   one ambiguous), blind-score-first discipline, variance threshold (≤10 percentage points weighted),
   and calibration-meeting agenda.

5. Set the minimum review cadence: conversations reviewed per agent per period (minimum: 5 for
   low-volume agents, 10 for high-volume), pass threshold (≥80% weighted score), and escalation
   rule (two consecutive fails → coaching plan).

6. Fill `templates/qa-scorecard.md` with the completed scorecard. Emit the Structured Output block
   with: scorecard dimensions + weights, calibration protocol, cadence targets, and handoffs to
   `support-quality-analyst` for the coaching-loop design and to `knowledge-and-deflection-strategist`
   if the top failure theme is KB or macro quality.
