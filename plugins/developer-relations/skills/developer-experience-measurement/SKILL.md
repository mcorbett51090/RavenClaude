---
name: developer-experience-measurement
description: "Measure developer experience and DevRel impact — instrument the activation funnel, compute time-to-first-value and activation rate, separate vanity inputs from outcome metrics, and build a DevRel scorecard the exec team will trust."
---

# Developer Experience Measurement

**Purpose:** replace vanity reporting with an activation-and-adoption scorecard — measure what moves
a developer toward value, and instrument it so the numbers are trustworthy.

---

## Steps

### 1. Instrument the activation funnel

Define the funnel with concrete, instrumentable events:

```
sign_up → credential_created → first_api_call → first_success → recurring_use → production
```

Each arrow is a conversion rate. The steepest drop is where the next investment goes.

### 2. Compute the core DX metrics

Use [`../../scripts/devrel_calc.py`](../../scripts/devrel_calc.py):

| Metric | Definition | Why it matters |
|---|---|---|
| Time-to-first-value (TTFV) | Median time from sign-up to first success | The single best predictor of activation; every minute of friction costs activations |
| Activation rate | First-success ÷ sign-ups | The outcome most vanity metrics pretend to be |
| Funnel conversion | Stage-to-stage rates | Localizes the drop so the fix is targeted |
| Content ROI | Activations attributable ÷ content effort | Stops effort going to content that informs but doesn't convert |
| Community health | Active ratio, answer-rate, contributor conversion | Distinguishes a live community from a member count |

### 3. Separate vanity inputs from outcomes

Maintain two columns. Inputs (stars, followers, impressions, attendees) may appear only when paired
with the outcome they're meant to drive. An input reported alone is removed from the scorecard.

### 4. Set the cadence and the decision each metric informs

Every metric names the decision it triggers: TTFV up → onboarding investigation; activation flat
despite sign-up growth → DX bottleneck; answer-rate falling → community staffing or docs gap.

### 5. Report outcomes to the exec team

Lead the scorecard with activation and adoption. Vanity inputs go below the fold, paired, never as
the headline.

---

## Output

A DevRel scorecard (inputs vs. outcomes, definitions, sources, cadence, the decision each informs)
and an instrumented funnel diagnosis. See
[`../../knowledge/devrel-decision-trees.md`](../../knowledge/devrel-decision-trees.md) for the
metrics-selection decision tree.
