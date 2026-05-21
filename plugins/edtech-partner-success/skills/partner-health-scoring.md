---
name: partner-health-scoring
description: Design and maintain a partner health score that actually predicts renewal / churn for EdTech partners. Signal selection, weighting, half-life / decay, red-flag triggers, and threshold-to-play mapping. Reach for this skill when designing a new score, refreshing one that's stopped predicting outcomes, or interpreting a score move.
---

# Skill: Partner Health Scoring

A partner health score is useful when it changes the PSM's behavior. A score that nobody acts on is decoration. This skill keeps the score honest.

## Step 1 — Define the outcome you're predicting

A health score is a prediction of *something*. Pick one:

- **Churn risk** — probability of non-renewal in the next 90 / 180 days
- **Expansion readiness** — probability the partner is ready for an upsell / cross-sell motion this quarter
- **Adoption trajectory** — directional indicator (improving / flat / declining) regardless of absolute level
- **Composite "health"** — blended view (least precise, most-loved by leadership)

If you're tempted to say "all of them," pick the one that drives the most action. Composite is a fallback when nothing else fits.

## Step 2 — Pick the signals (4–7 max; more is noise)

Signal categories and example signals:

| Category | Examples |
|---|---|
| **Adoption depth** | % of seats actively using the deepest 2–3 features; share of users reaching the "aha" milestone within onboarding window |
| **Usage breadth** | active users / total seats (normalized for partner size); rolling 30-day active count vs. baseline |
| **Sentiment** | NPS with follow-up answer; CSAT after support resolution; quarterly check-in sentiment score |
| **Business outcomes** | the partner's own KPI that the product is supposed to move (test scores, time-to-skill, course completion, etc.) — only when measurable + shareable |
| **Touchpoint cadence** | days since last meaningful (non-boilerplate) interaction; PSM-to-partner response latency |
| **Champion strength** | number of active champions (1 = single point of failure, 2 = thin, 3+ = robust); champion engagement frequency |
| **Commercial signal** | contract anniversary proximity; multi-year vs single-year posture; payment-history flags |

**Anti-pattern:** picking signals that the dashboard *has* rather than signals that *predict the outcome*. If a category isn't predictive, leaving it out is correct.

## Step 3 — Weight the signals

**Equal-weighting is rarely right.** Different signals predict different outcomes with different strength. Tune weights based on historical churn / renewal data when possible; use cohort comparison when not.

**Anti-pattern:** weighting based on which department lobbied hardest. The CS-leadership-loves-NPS-so-NPS-is-30% pattern produces scores that look comprehensive but don't predict anything.

When in doubt, start with these defaults for *churn risk*:
- Adoption depth: 25%
- Touchpoint cadence (recency): 20%
- Business outcomes (when available, otherwise redistribute): 20%
- Sentiment: 15%
- Champion strength: 10%
- Usage breadth: 10%

Adjust based on what you observe in the first 90 days.

## Step 4 — Design the half-life / decay (this is the part most teams skip)

**A signal from 6 months ago is not a signal today.** Every component needs a defined decay rate. Examples:

- **Login frequency / usage** — fast decay (half-life ~14 days). Last 30 days matters most.
- **Adoption-of-a-deep-feature** — slow decay (half-life ~90+ days). Once adopted, stays adopted unless the user leaves.
- **NPS score** — medium decay (half-life ~60 days). The most recent NPS dominates; older surveys fade.
- **Champion-engagement frequency** — fast decay. A champion who hasn't engaged in 60 days is no longer effectively a champion.
- **Business outcome metric** — depends on the metric's natural reporting cadence. Quarterly test scores have a 90+ day half-life.

**Rule:** if you can't write down the half-life for a component, you haven't designed it; you've just added it.

## Step 5 — Red-flag triggers (run alongside the score, not inside it)

A composite score reacts too slowly. **Independent red-flag triggers** fire a recovery play immediately, regardless of the composite. Examples:

- Active-user count drops >30% week-over-week
- Champion departure (named champion no longer in the role)
- 21+ days of zero meaningful touchpoints during the partner's active season
- Renewal date within 90 days AND decision-maker not yet confirmed alive in role
- 2+ consecutive support escalations to leadership tier
- Partner explicitly states "we're evaluating alternatives"

The composite score is a trailing indicator. The triggers are leading indicators.

## Step 6 — Threshold-to-play mapping

The score itself is useless without an answer to "what does the PSM do when it says X?" Define:

- **Green (e.g., 70–100):** maintain cadence; consider expansion-readiness check
- **Yellow (e.g., 50–69):** investigate which components dropped; light-touch recovery play; weekly review
- **Red (e.g., <50):** mandatory recovery play; cross-functional alert; PSM lead daily review until cleared

Plus: which **trigger** fires which play, independent of the composite color.

## Step 7 — Dashboard surface (if it's not visible Tuesday morning, it doesn't drive behavior)

The PSM sees:

- Composite score + week-over-week delta
- The 2–3 component drivers behind the score (drill-down)
- The trigger status: any active red-flag triggers, in plain language
- The recommended play for the current state
- The history (12-week sparkline) for context

If the dashboard requires the PSM to compute anything mentally, redesign it.

## Step 8 — Refresh the score quarterly

A score that's never been refreshed is suspect. Quarterly review:

- For each renewed partner, did the score correctly predict the renewal outcome?
- For each churned partner, did the score show red in time to act?
- Did any red-flag trigger fire after the partner was already in churn motion? (lagging → leading correction needed)
- Did any green partner churn? (signal gap; add the missing signal)
- Are any signals correlating but not predicting? (drop them; they're noise dressed as signal)

## What this skill does NOT cover

- Building the dashboard UI (route to the `learning-analytics-analyst` or `ravenclaude-core/data-engineer` for instrumentation)
- Designing the plays that fire from the thresholds (route to `success-playbook-designer`)
- Comms-shape variants when the score informs partner-facing claims (route to `ferpa-comms-translator`)
- The narrative that explains the score in a QBR (route to `qbr-composer`)
