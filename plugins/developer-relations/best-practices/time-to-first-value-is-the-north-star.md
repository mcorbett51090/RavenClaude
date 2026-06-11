# Time-to-first-value is the north-star input

**Status:** Pattern.

**Rule:** Time-to-first-value (TTFV) — the median wall-clock time from sign-up to first success — is
the single best leading predictor of activation. Track it (median and p90) and treat every minute of
first-hour friction as a measurable activation cost.

## Why

Activation rate is a lagging outcome; TTFV is the leading input you can engineer down today. The two
move together: shorten the path to first success and activation rises. The p90 matters as much as the
median — it's where the silent failures (hidden steps, version drift, cryptic errors) hide while the
median looks fine.

## What it looks like in practice

- TTFV is instrumented as `sign_up → first_success` wall-clock, reported as median **and** p90.
- Every onboarding change is justified by its expected TTFV effect and re-measured after.
- A rising p90 with a stable median triggers a clean-machine quickstart run to find the silent killer.

## Anti-pattern

Optimizing the getting-started **page** (bounce rate, time-on-page) instead of the **funnel** (TTFV,
activation). A beautiful docs page with a 40-minute TTFV is a failing onboarding.
