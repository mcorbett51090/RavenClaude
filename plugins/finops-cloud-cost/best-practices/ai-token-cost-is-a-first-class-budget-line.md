# AI token cost is a first-class budget line

**Status:** Pattern
**Domain:** AI/GenAI inference cost governance
**Applies to:** `finops-cloud-cost`

---

## Why this exists

Historically, API fees — including early LLM API fees — have been categorized as "miscellaneous"
or absorbed into software/SaaS line items in the cloud budget. This was tolerable when LLM usage
was experimental and spend was small. It is no longer tolerable when AI features go to production.

A single viral AI feature can multiply inference costs by 10–100× in a week. A model upgrade
(from a lightweight to a frontier model across a feature set) can triple the inference cost
overnight. These are not anomalies — they are the normal lifecycle of AI feature development.
Without a dedicated budget line, a first-party forecast, and anomaly detection, the engineering
organization will not discover the cost trajectory until the cloud bill arrives.

AI token cost needs its own budget line, its own unit economics definition (cost per feature-user,
cost per API request), and its own anomaly alerting — exactly as compute and storage do.

## How to apply

- In the annual cloud budget, create a dedicated "AI inference" line item alongside compute, storage,
  database, and network. Do not roll it into software/SaaS or API fees.
- Instrument every inference API call with the feature/team tag. Without per-feature attribution,
  all AI cost lands in one bucket that cannot be actionable.
- Forecast with scenarios: baseline (stable model, stable volume) and a growth scenario
  (2× volume and/or model upgrade). Present the range as the budget ask — not a point estimate.
- Set a per-feature token budget: daily and monthly caps with alerting on breach.
- Set anomaly detection on total inference spend (z-score or percentage-over-baseline). A week-
  long viral traffic spike can exhaust the monthly AI budget in 5 days.
- All per-token price inputs carry the retrieval date and `[verify-at-use]` — LLM pricing changes
  frequently and materially.

**Do:**

- Treat AI token cost forecasting like compute forecasting: request volume × unit cost × a growth
  multiplier.
- Include AI inference in the FinOps weekly digest alongside compute and storage.
- Define the unit economics for each AI feature (cost per active user, cost per API call) and track
  the trend — a rising cost-per-user is a signal of model over-tiering or prompt inefficiency.
- Right-size model choices: use the cheapest model that meets the quality bar. A model tier change
  often saves 5–10× before any prompt optimization.

**Don't:**

- Hardcode a per-million-token price in any doc, IaC file, or budget model without a date. LLM
  pricing changes frequently; a stale price is a misleading forecast.
- Treat a model upgrade as a zero-cost engineering decision — a model upgrade is a budget event.
- Let AI inference costs land in "misc API fees" or "third-party software" — they will grow there
  invisibly until they become a crisis.
- Wait for the monthly cloud bill to notice an inference cost spike — set real-time alerts.

## Edge cases / when the rule does NOT apply

For organizations in the very early stages of AI adoption (a handful of experiments, no production
features, spend <$500/month), a dedicated budget line may be premature overhead. In these cases,
at minimum: tag every inference call with the feature/project, set a spend alert threshold, and
commit to promoting it to a first-class line item before any feature goes to production. The rule
applies fully once any AI feature is in production.

## See also

- [`./anomaly-detection-beats-the-monthly-surprise.md`](./anomaly-detection-beats-the-monthly-surprise.md)
- [`../skills/ai-and-token-cost-governance/SKILL.md`](../skills/ai-and-token-cost-governance/SKILL.md)
- [`../agents/ai-cost-governance-engineer.md`](../agents/ai-cost-governance-engineer.md)

## Provenance

Reflects the emerging FinOps Foundation guidance on AI/ML cost governance and the observed
industry pattern of AI inference costs growing faster than compute costs for organizations
deploying production GenAI features (2024–2026). Pricing volatility observation is current
observation, not a historical artifact.

---

_Last reviewed: 2026-06-08 by `claude`._
