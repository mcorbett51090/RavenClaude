---
description: "Forecast spend and set anomaly thresholds so cost is managed, not a monthly surprise. Reach for this on a budget/anomaly question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Forecast and alert

You are running `/finops-cloud-cost:forecast-and-alert` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Build the forecast — Trend the allocated spend forward; budget against the forecast (§3 #7).
2. Set the threshold — Alert on deviation from forecast, sized to catch a runaway early (§3 #7).
3. Route the alert — To the owning team via showback, so the alert reaches the spender (§3 #6).
4. Tune false positives — A threshold too tight is noise; calibrate to real anomalies.

## Output
A spend forecast with an anomaly threshold routed to the owning team. See [`../skills/forecast-and-alert/SKILL.md`](../skills/forecast-and-alert/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No billing/account PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
