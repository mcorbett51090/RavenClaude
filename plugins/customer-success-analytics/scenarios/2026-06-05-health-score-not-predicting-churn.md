---
scenario_id: 2026-06-05-health-score-not-predicting-churn
contributed_at: 2026-06-05
plugin: customer-success-analytics
product: health-tier
product_version: "n/a"
scope: likely-general
tags: [health-score, lagging-signal, back-test, false-confidence, retune]
confidence: medium
reviewed: false
---

## Problem

A B2B SaaS team had a "customer health score" everyone trusted, but Green accounts kept churning at renewal while the score sat green right up to the cancellation. Leadership had stopped believing the score and were back to gut-feel triage. The ask was "fix the score" — but the score wasn't broken arithmetic, it was built on the **wrong signals**.

## Context

- Segment: mid-market B2B SaaS, ~400 accounts, one CS platform with a native health score plus a homegrown composite layered on top.
- Constraint: the composite blended ~9 signals with equal-ish weights, **including two lagging ones** — a "renewal opportunity stage" field and a "has an open cancellation request" flag. Those two only move *after* the churn decision is effectively made.
- No back-test had ever been run. The thresholds were set by intuition at launch and never revisited against an actual renewal cycle.

## Attempts

- Tried: back-tested the composite against the last 12 months of completed renewals before touching any weight. Finding: the score's accuracy was carried almost entirely by the two **lagging** signals — which is why it looked "accurate" in aggregate but gave **zero lead time**. By the time they moved, the account was gone. The genuinely leading signals (usage-trend slope, health-score 30-day delta, champion silence) were under-weighted to near-irrelevance. Outcome: reframed from "tune the weights" to "the signal *set* is wrong."
- Tried: pulled the two lagging signals **out of the tier entirely** and re-surfaced them as dashboard *context* (shown, never scored). Re-weighted toward the leading signals, with the slope (not the absolute usage level) as the primary driver. Marked the new thresholds **provisional** pending the next cycle. Outcome: the Red list started catching accounts ~60–90 days earlier.
- Tried: ran the `cs_calc.py health-score` mode over the proposed signal set to make the **lagging-signal share** of the score explicit on every account, so the team could see at a glance how much of a "Red" was driven by signals that can't predict. Outcome: made the design smell visible and kept it from creeping back in.

## Resolution

The score wasn't miscalibrated — it was **built on lagging signals dressed up as predictors**. A lagging signal (closed-lost stage, open cancellation) *confirms* churn; it never *leads* it, so a score that leans on them is accurate-in-hindsight and useless-in-time. The fix was to classify every signal leading-vs-lagging first, move the lagging ones to context, re-weight toward the slope/delta leading signals, and **back-test before trusting** — then re-tune after the cycle.

**Action for the next consultant hitting this pattern:** when a health score "doesn't predict churn," **don't tune the weights first — audit the signal set for lagging signals**. Run the leading-vs-lagging classification (`cs-health-metrics-and-churn-indicators.md` §1) and back-test against actual outcomes before changing a single threshold. A score that looks accurate in aggregate but gives no lead time is the tell. Mark new thresholds `provisional` until a real renewal cycle validates them.

**Sources (retrieved 2026-06-05):** health-score-that-predicts-churn design (leading vs lagging, calibrate quarterly, transparency) — https://www.supportbench.com/building-health-score-predicts-churn/ ; effective models ~60–80% churner identification with <30% false-positive — https://www.everafter.ai/glossary/customer-health-score . Accuracy figures are vendor-reported ranges; treat as `[ESTIMATE]` and validate against the team's own back-test, never quote as a guaranteed number.
