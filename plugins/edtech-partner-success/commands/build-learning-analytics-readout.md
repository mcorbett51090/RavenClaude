---
description: "Build a learning-analytics readout a PSM can act on — verify rostering before trusting any number, normalize every metric to partner size with a named baseline, separate leading from lagging signals, and screen cohort-level cuts for the FERPA residual."
argument-hint: "[the readout, e.g. 'engagement trends for a mid-sized district this quarter']"
---

# Build a learning-analytics readout

You are running `/edtech-partner-success:build-learning-analytics-readout`. Turn the data the user described (`$ARGUMENTS`) into a defensible, decision-ready readout — the work the `learning-analytics-analyst` agent owns. A number without its baseline gets the PSM asked the question they can't answer at the next touchpoint.

## When to use this

You need an engagement / adoption / outcomes readout for a partner or for internal health tracking. NOT for the QBR narrative itself (that is `/edtech-partner-success:compose-qbr`, which consumes this) or a save play.

## Steps

1. **Verify rostering before trusting any number** (`rostering-sync-succeeded-is-not-the-same-claim-as-data-is-correct.md`, `check-rostering-before-calling-a-partner-red.md`): a sync that "succeeded" is not a claim that the data is correct — confirm rosters before calling a partner red or presenting a decline.
2. **Normalize every metric to partner size** (`analytics-normalize-to-partner-size-and-state-the-comparison-baseline.md`): use per-capita / per-school rates, not raw totals — a 30-school and a 2-school district aren't comparable on absolute counts, and a real decline in a big partner can look like growth.
3. **Attach a named baseline to every percentage** (`analytics-normalize-to-partner-size-and-state-the-comparison-baseline.md`): "up 18%" is unanswerable until you say versus what — last quarter (trending?), the cohort (average?), or the onboarding target (on plan?). Carry the source query and date range with every claim.
4. **Separate leading from lagging signals** (`health-design-leading-not-lagging-signals.md`): label which signals give the PSM runway (depth-of-adoption trend, champion engagement) versus which only confirm an outcome already in motion (cumulative logins, last NPS).
5. **Distinguish a real movement from noise**: a two-point move isn't a trend and a small-denominator swing isn't signal — quantify the metric's own variation before calling a move "real" (the seam to `applied-statistics` — escalate a genuine signal-vs-noise question there).
6. **Screen any cohort-level cut for the FERPA residual** (`screen-parent-comms-for-the-cohort-residual.md`): small-denominator breakdowns can re-identify individuals — route student-level cuts through `ferpa-comms-translator`. Use generic placeholders (`<district>`) in every example; no real student data.

## Guardrails

- Calling a partner red off an unverified roster is a false alarm — rostering correctness gates the conclusion, not just the sync status.
- Absolute counts mislead across partner sizes and a baseline-less percentage is unactionable — normalize and baseline every number.
- A small-cohort breakdown can identify students from context — screen for the residual before any cut leaves internal use, and keep examples generic.
