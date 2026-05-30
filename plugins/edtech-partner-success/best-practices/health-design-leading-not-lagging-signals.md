# Build the health score on leading usage signals, not lagging ones

**Status:** Pattern

**Domain:** Learning analytics / Health-score design

**Applies to:** `edtech-partner-success`

---

## Why this exists

A health score built from lagging signals tells the PSM a partner is in trouble only after the partner is already in churn motion — too late to run anything but a recovery play under duress. The most common design failure is a composite dominated by lagging indicators (renewal-quarter sentiment, total cumulative logins, last NPS) that move *after* the decision to leave has formed. Leading signals (depth-of-feature adoption trend, champion engagement frequency, train-the-trainer completion, week-over-week active-teacher trend within a school) move *before* the outcome and give the PSM runway. The `learning-analytics-analyst` house opinion is explicit: a red-flag trigger that fires after the partner is already churning is a lagging-vs-leading defect, and red-flag triggers run *alongside* the score, not inside it.

## How to apply

Classify every candidate signal as leading or lagging before it enters the composite, and weight leading signals to dominate the score the PSM acts on.

```
Signal classification (do this before weighting):
  LEADING (predicts the outcome — weight these in the actionable score):
    - depth-of-feature adoption TREND (rising/falling), not absolute count
    - active-teacher % within a school, week-over-week
    - champion touch frequency (silence is the leading signal)
    - train-the-trainer completion / PD-hour progress
    - support-ticket sentiment shift (tone, not volume)
  LAGGING (confirms an outcome already formed — context, not trigger):
    - renewal-quarter NPS / CSAT
    - cumulative total logins / sessions (vanity — can rise while failing)
    - last-QBR satisfaction
  → Two scores beat one: a fast-decay "current state" + a slow-decay "trajectory".
  → Red-flag triggers (sudden 30% active-user drop, champion departure,
     3 weeks zero touchpoints) fire a play independent of the composite.
```

- Every leading signal needs a defined half-life (login frequency decays fast; deep-feature adoption decays slow) — a signal with no decay pollutes the score forever (house opinion §3 #3).
- Normalize to partner size; absolute counts hide per-capita decline in large districts.
- Make the composite drillable — the PSM clicks "yellow" and sees which 2-3 leading components dropped (cite the signal, §3 #4).

**Do:**
- Audit quarterly: correlate final-score × renewal outcome; below ~0.5 the score is broken — recalibrate, don't reassure.
- Run leading signals through the calendar-dead-zone overlay so a December dip doesn't fire a false leading-signal alarm.

**Don't:**
- Put a metric on the PSM dashboard that can move up while the partner is failing (total logins is the canonical offender).
- Bury component weights so the PSM can't see what moved — a hidden-weight composite is unactionable.

## Edge cases / when the rule does NOT apply

- **Outcome-only buyers** (some K-12 boards) judge renewal on the lagging outcome metric (assessment gains) regardless of leading adoption — surface the lagging metric *for them* while keeping the leading score *for the PSM*. Two audiences, two surfaces.
- **Brand-new instrumentation** with no outcome history — you can't yet validate which signals lead; start with adoption-depth trend as the prior and validate against the first renewal cohort.
- **Cohorts < 10 partners** — leading-signal thresholds derived from a sub-10 cohort are noise; use segment-level baselines until the cohort grows.

## See also

- [`./onboarding-instrument-first-value-from-day-one.md`](./onboarding-instrument-first-value-from-day-one.md) — first-value is the canonical leading signal
- [`./risk-early-warning-fire-the-save-play-while-it-still-saves.md`](./risk-early-warning-fire-the-save-play-while-it-still-saves.md) — leading signals are what give the save play runway
- [`../knowledge/partner-health-score-drift.md`](../knowledge/partner-health-score-drift.md) — drift typology and the quarterly correlation audit
- [`../agents/learning-analytics-analyst.md`](../agents/learning-analytics-analyst.md) — owns signal selection and decay design

## Provenance

Distilled from `agents/learning-analytics-analyst.md` opinions (leading-not-lagging, two-scores-beat-one, red-flags-alongside-not-inside), `knowledge/partner-health-score-drift.md` (correlation audit, decay typology), `knowledge/psm-metrics-glossary.md` (vanity-metric pitfalls), and house opinions §3 #3 and #4. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
