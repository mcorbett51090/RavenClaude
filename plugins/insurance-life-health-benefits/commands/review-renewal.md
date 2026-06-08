---
description: "Decompose and pressure-test a group renewal: trend vs experience vs pooling vs demographics vs plan change, a credibility/loss-ratio/MLR read, and the levers that move the rate — educational, not actuarial advice."
argument-hint: "[group size + renewal % + claims/loss-ratio data + plan changes]"
---

You are running `/insurance-life-health-benefits:review-renewal`. Use `underwriting-and-actuarial-analyst` + the `underwriting-and-rating` skill.

## Steps
1. Establish credibility: is the group big enough for its own experience to drive the rate, or is this manual/blended? Name the credibility weight first.
2. Decompose the renewal into trend + own experience + pooling/large-claim + demographic drift + plan change. "+X%" is not a finding — show the parts. If the carrier won't, recommend re-marketing.
3. Read the loss ratio (claims ÷ premium) and separately the ACA MLR test + rebate thresholds (`[verify-at-build]` the current percentages). Don't conflate them.
4. Name the levers that move the rate: plan change, funding move, contribution shift, re-marketing. For self-funded groups, model the specific/aggregate stop-loss attachment.
5. Route: plan/funding redesign → benefits-advisor; carrier coordination + the enrollment that follows → enrollment-and-compliance-lead.
6. Emit the renewal-and-rate review + the Structured Output block (with `Not advice:` and `Coverage gaps flagged:`). `[verify-at-build]` every figure; name the actuary/broker sign-off.
