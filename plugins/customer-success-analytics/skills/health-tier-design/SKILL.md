---
name: health-tier-design
description: "Design a transparent, explainable rule-based customer-success health tier (Green/Yellow/Red) from multi-source signals: signal selection, weighting, thresholds, per-signal evidence display, and tuning against actual past churn. Reach for this skill when designing a new health tier, refreshing one that has stopped predicting outcomes, or deciding how a Red account should explain itself. Domain-neutral — generalized from the EdTech partner-health-scoring pattern; no vertical assumptions."
---

# Skill: Health-Tier Design

A customer-success health tier is useful only when it changes what the CS team does on Tuesday morning. A tier nobody acts on is decoration; a tier nobody can explain is distrusted. This skill keeps the tier transparent, explainable, and honest.

This is the **domain-neutral** generalization of the partner-health-scoring pattern — the reusable CS mechanics, with vertical specifics (K-12 / EdTech / LMS / segment calendars) stripped out. Used by `cs-analytics-architect` (designs the tier into the data model) and `churn-signal-analyst` (validates the signals + thresholds).

## Step 0 — One opinion up front: rule-based and explainable in phase 1

Phase 1 is a **transparent rule-based tier**, not a learned model. Every Red shows *why*. Anchor on the customer-success platform's native health score if the team already trusts it (pull it as-is; don't silently recompute), and surface extra signals *additively* as visible sub-indicators. A black-box ML score is a later option, never the phase-1 default — trust and adoption are the whole game early, and a tier nobody can read torpedoes both. See [`../../knowledge/cs-health-metrics-and-churn-indicators.md`](../../knowledge/cs-health-metrics-and-churn-indicators.md) §7.

## Step 1 — Define the outcome the tier predicts

A tier is a prediction of *something*. Pick the one that drives the most action:

- **Churn risk** — probability of non-renewal in the next 90 / 180 days (the usual phase-1 choice)
- **Expansion readiness** — probability the account is ready for a grow motion this quarter
- **Adoption trajectory** — directional (improving / flat / declining) regardless of absolute level
- **Composite "health"** — blended; least precise, most-loved by leadership; a fallback when nothing else fits

If tempted to say "all of them," pick the one that drives the most action. Composite is the fallback.

## Step 2 — Pick the signals (5-7 max; more is noise)

Choose signals that *predict the outcome*, not signals the dashboard happens to have. Domain-neutral signal categories:

| Category | Example signals |
|---|---|
| **Usage trend** | 30/60/90-day usage *slope* (not absolute level); rolling active count vs. baseline |
| **Health-score trend** | 7/30-day delta of the CSP's native score (direction beats the absolute number) |
| **Renewal proximity × engagement** | `days_to_renewal` *combined with* a down trend / low touch — never proximity alone |
| **Support load** | support volume + **P1/P2 rate** (rate matters more than raw volume); median first-response time |
| **Sentiment** | NPS with recency weighting; CSAT after support resolution |
| **Relationship strength** | champion / sponsor presence (1 champion = single point of failure); review attendance |
| **Collaboration signal** | escalation-keyword density; *dead-channel* detection (derived signals only, never raw bodies) |

> **Leading vs lagging gate:** before a signal enters the tier, classify it. A signal that moves *after* the churn decision (Closed-Lost opp, cancellation) is *lagging* — it is context on the dashboard, never a tier input. Only leading signals compose the tier.

**Anti-pattern:** picking signals the dashboard *has* rather than signals that *predict*. If a category isn't predictive, leaving it out is correct. Fewer, sharper signals beat more, fuzzier ones.

## Step 3 — Weight the signals

**Equal-weighting is rarely right** — different signals predict with different strength. Tune weights / threshold cut-points against historical churn when you have it; use cohort comparison when you don't.

**Anti-pattern:** weighting by which department lobbied hardest (the "leadership-loves-NPS-so-NPS-is-30%" pattern) produces a tier that looks comprehensive and predicts nothing.

When the native CSP score is the anchor, you may not need explicit weights at all in phase 1 — the anchor *is* the score, and the additive signals are surfaced as their own visible sub-indicators. Defer a custom weighted composite until those sub-signals demonstrably diverge from the anchor.

## Step 4 — Set the thresholds and write the rule

Express the tier as a **readable boolean rule** over the leading signals, with named threshold values:

```
Red    := health_score_trend_30d = down
          AND days_to_renewal < 90
          AND (support_p1_p2_rate_30d > t_support OR escalation_signal_7d > t_escalation)
Yellow := any single leading signal tripped AND renewal not imminent
Green  := otherwise
```

- **Renewal proximity is a gate, not a term** — it multiplies urgency; it never stands alone as risk.
- **Thresholds are tuned against real churn, not guessed** (Step 6). A threshold you can't back-test is a guess wearing a number — mark it **provisional** and schedule the retune.

## Step 5 — Per-signal evidence display (every Red shows why)

The tier is useless to the leader and unconvincing to the account if it says "Red" with no reason. The **explainability contract**: every Red (and Yellow) carries its 2-3 driving signals, each with:

- the **signal name**
- its **value**
- the **threshold** it crossed
- the **window** measured

This ships *with* the tier, not as an afterthought. It is the single biggest driver of CS-team adoption.

## Step 6 — Tune against actual past churn

- **When historical outcomes exist:** back-test against the last renewal cycle. Did the Red list match the accounts that actually churned? Did any **Green account churn** (a *signal gap* — the most valuable finding; it names the missing signal)? Did a signal **correlate but not predict** (drop it — noise dressed as signal)?
- **When they don't:** start from a documented default, mark it provisional, retune after cycle 1.
- **Refresh each cycle.** A tier never refreshed against outcomes is suspect by default.

## Step 7 — Independent red-flag triggers (alongside the tier, not inside it)

A composite reacts too slowly to a sudden event. Independent fast triggers fire a recovery motion *immediately*, regardless of the tier's color:

- Active-user count drops sharply week-over-week
- Named champion departs / sponsor lost
- N+ consecutive support escalations to leadership tier
- Account explicitly states "we're evaluating alternatives"

These run beside the tier and key the renewal/save workflow (see [`../renewal-workflow-design/SKILL.md`](../renewal-workflow-design/SKILL.md)).

## What this skill does NOT cover

- Building the pipeline / warehouse / connectors that source the signals → `data-platform`
- Building the dashboard UI / BI surface that renders the tier → `data-platform/dashboard-builder`
- The renewal-risk workflow + save-play triggers the tier feeds → [`../renewal-workflow-design/SKILL.md`](../renewal-workflow-design/SKILL.md)
- Segment-specific overlays (budget cycles, academic calendars) → a vertical plugin (e.g. `edtech-partner-success`)

## References

- Knowledge: [`../../knowledge/cs-health-metrics-and-churn-indicators.md`](../../knowledge/cs-health-metrics-and-churn-indicators.md)
- Companion skill: [`../renewal-workflow-design/SKILL.md`](../renewal-workflow-design/SKILL.md)
- Template: [`../../templates/cs-health-data-model.md`](../../templates/cs-health-data-model.md)
- Generalized from: [`../../../edtech-partner-success/skills/partner-health-scoring/SKILL.md`](../../../edtech-partner-success/skills/partner-health-scoring/SKILL.md)
