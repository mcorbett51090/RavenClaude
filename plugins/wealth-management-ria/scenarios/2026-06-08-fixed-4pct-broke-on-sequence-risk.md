---
scenario_id: 2026-06-08-fixed-4pct-broke-on-sequence-risk
contributed_at: 2026-06-08
plugin: wealth-management-ria
product: planning
product_version: "unknown"
scope: likely-general
tags: [withdrawal, sequence-risk, guardrails, retirement, assumptions]
confidence: high
reviewed: false
---

## Problem

A planning team built retirement projections for near-retirees on a flat "4% rule" assumption and a single average-return number, presented as one confident "you can spend $X/year for life" figure. When a couple retired into two weak market years early in their drawdown, the plan that had looked safe on paper was suddenly on track to deplete a decade early — and the clients were blindsided because the plan had never shown a downside path. Trust cratered: the number had been presented as a promise, not a hypothesis.

## Constraints context

- The plan output was a single point estimate; assumptions (return, inflation, longevity) were buried in a spreadsheet nobody surfaced.
- Spending was modeled as fixed and inflation-adjusted regardless of how the portfolio performed.
- Educational vs personalized-advice line was blurry — the projection read like a guarantee.

## Attempts

- Tried: just lowering the assumed return to be "more conservative." Failed — it made every plan look unaffordable and still hid the real risk (the *order* of returns, not the average), and clients couldn't see what drove the change.
- Tried: a static Monte Carlo "success probability" number. Helped a little but a single 85%-success figure was still a point estimate clients over-trusted and didn't connect to any action.
- Tried: reframing the output as a scenario range (good / expected / poor *sequence*), surfacing the assumptions as a named editable list, and pairing a guardrail withdrawal rule (cut spending if the portfolio drops past a band, raise it if it runs ahead) with an explicit not-a-guarantee disclaimer. This worked.

## Resolution

Showing the poor-sequence path next to the expected one made sequence-of-returns risk concrete, and the dynamic guardrail gave the clients a pre-agreed action ("in a bad early stretch we trim spending X%") instead of a panic. The plan stopped being a single promised number and became a monitored hypothesis with a review trigger. Because the assumptions were now visible and editable, clients could see exactly what changed when an input did — and the educational framing kept it on the right side of the not-personalized-advice line.

## Lesson

A withdrawal rate is a planning hypothesis to monitor, not a guarantee. Surface every assumption as an editable list, present a scenario range that includes a poor *sequence* (not just a lower average), and prefer dynamic guardrails over a blind fixed percentage when the plan is tight. And keep the framing educational — a confident single number reads as a personalized promise the practice can't make.
