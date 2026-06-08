---
name: support-quality-and-csat
description: "Build weighted QA scorecards with calibration protocols, design CSAT and CES measurement programs, run VOC root-cause analysis on quality drops, and design agent coaching loops that close feedback into behavior change."
---

# Support Quality and CSAT

**Purpose:** make quality measurable, calibrated, and actionable — and make satisfaction signals
(CSAT and CES) meaningful by separating what they measure and closing the loop from signal to
coaching to improvement.

## The operating loop

1. **Design the QA scorecard.**
   Define dimensions and weights. A standard weighted split:
   - Resolution accuracy (40%): was the customer's issue actually solved?
   - Communication quality (25%): clarity, grammar, appropriate tone.
   - Empathy and rapport (15%): acknowledgment, de-escalation where relevant.
   - Process adherence (10%): macro usage, escalation protocol, tagging discipline.
   - Escalation discipline (10%): was the escalation necessary? Was the reason code recorded?
   
   Score each dimension: Pass (full weight), Partial (half weight), Fail (zero). Overall pass
   threshold: typically ≥80% of weighted score.

2. **Establish calibration.**
   Select 3–5 anchor conversations per scoring period (one clear pass, one clear fail, one
   ambiguous). All reviewers score blind, independently. Variance threshold: ≤10 percentage points
   on weighted score between any two reviewers. Run calibration meetings to resolve disagreements
   via the rubric, not seniority. Log calibration variance; tighten rubric language where variance
   is highest.

3. **Design the CSAT program.**
   - Survey instrument: 5-point scale (Very Satisfied → Very Dissatisfied) + verbatim field.
   - Dispatch: post-resolution, not in-flight. Minimum 30-minute delay after ticket closes.
   - Sample rate: 100% of resolved tickets for low-volume teams; statistical sample (n≥30/month
     per agent, confidence 95%) for high-volume.
   - Response-rate target: ≥25% for email surveys; ≥40% for in-app.
   - Reporting: CSAT% = (4+5 ratings) / total responses. Report by agent, by contact category,
     by channel. Do not report averages without sample-size disclosure.

4. **Design the CES program (separate from CSAT).**
   - Survey instrument: "How easy was it to resolve your issue today?" — 7-point CES scale or
     3-point (Easy / Neither / Difficult).
   - Dispatch: immediately post-interaction (within 5 minutes of close).
   - Interpret separately: CES predicts repurchase and churn for low-complexity service encounters
     more strongly than CSAT alone. High CSAT + high effort = solved the problem the hard way.
   - Report CES as % Easy (6+7 on 7-point) or Easy% on 3-point, separately from CSAT.

5. **Run VOC root-cause analysis on a CSAT drop.**
   - Pull tickets from the drop window. Filter to CSAT ≤ 3 (dissatisfied/very dissatisfied).
   - Category breakdown: which contact categories have the highest negative-CSAT rate AND the
     highest volume? Rank by `(negative rate × volume)` — that is your driver list.
   - Verbatim cluster: read the verbatims for the top 3 drivers. What recurring themes appear?
   - Fishbone / 5-why on each theme: is the root cause agent knowledge, macro quality, policy,
     escalation routing, or product?
   - Output a ranked fix plan with owners: KB gap → `knowledge-and-deflection-strategist`;
     structural tier issue → `cx-ops-lead`; agent skill gap → coaching loop (step 6).

6. **Design the coaching loop.**
   - Score → Identify pattern (individual vs systemic: if >25% of agents in the same category
     fail the same dimension, it's systemic, not individual).
   - Coaching session template: share the scored conversation, name the specific behavior (not
     the person), agree on the one behavioral change, set a re-review date (within 2 weeks).
   - Re-review: pull 3 conversations from the same category post-coaching. Did the behavior change?
   - Aggregate trend: quarterly rollup — is the QA score moving? Is the systemic failure rate
     declining? If not, escalate the content or routing root cause.

## Anti-patterns

- A QA scorecard with no calibration protocol — inter-rater variance above 10% means the score
  is measuring the reviewer, not the conversation.
- CSAT and CES scores combined into a single index or used interchangeably.
- Survey dispatched during the interaction (response bias).
- A coaching session that shares the score without naming the specific behavior to change.
- A VOC root-cause analysis built on star ratings without reading verbatims.

## Output

A QA scorecard (use [`../../templates/qa-scorecard.md`](../../templates/qa-scorecard.md)), a
CSAT+CES program design, a VOC root-cause report with a ranked fix plan, or a coaching-loop
design. Use [`../../scripts/cx_calc.py`](../../scripts/cx_calc.py) for CSAT% and CES% calculations
from raw rating counts.
