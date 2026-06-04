---
name: health-score-v2-extension
description: Extends the existing 6-component health-score schema (adoption / touchpoint / outcome / sentiment / champion / usage) to add support (ticket health), financial (renewal / expansion signal), rostering_health (K-12), and leadership_stability (K-12). Defines recommended weights per lifecycle stage, per-signal decay half-lives, and per-signal leading/lagging tagging. Additive and opt-in — existing rubrics keep working unchanged.
last_reviewed: 2026-06-04
confidence: high
primary_skill: partner-health-scoring
status: extension proposal — additive only, default weight 0 for new components in legacy rubrics
---

# Health Score v2 — Extension to the Existing 6-Component Schema

> **Scope.** This document specifies a non-breaking extension to the schema in [`../bi-report/data.json`](../bi-report/data.json) and the [`partner-health-scoring`](../skills/partner-health-scoring/SKILL.md) skill. It does NOT replace the existing rubric. Consumers opt in by raising weights on the new components from 0.
>
> **Migration discipline.** Run v1 and v2 in parallel for one quarter against a hold-out cohort (per [`partner-health-score-drift.md`](partner-health-score-drift.md) Step 3 "Run both scores in parallel for one quarter") before cutting over. Don't ship v2 weights to production without that proof.
>
> **Refresh trigger.** When a new signal class earns its keep against the existing rubric on a hold-out test; when an existing component's contribution falls below noise (per [`partner-health-score-drift.md`](partner-health-score-drift.md) "vanity metrics polluting the composite").

---

## 1. The existing schema (v1, in production)

From [`../bi-report/data.json`](../bi-report/data.json):

| Key | Name | Default weight | Half-life (days) | Plain description |
|---|---|---|---|---|
| `adoption` | Adoption depth | 25% | 90 | How deeply they actually use the product |
| `touchpoint` | Touchpoint recency | 20% | 14 | How recently we talked with them |
| `outcome` | Business outcome | 20% | 90 | Are they getting the results they bought it for? |
| `sentiment` | Sentiment | 15% | 60 | Do they sound happy in surveys and calls? |
| `champion` | Champion strength | 10% | 60 | Is our main supporter still strong and still here? |
| `usage` | Usage breadth | 10% | 30 | How many of the features they use |

Bands: green 70-100, yellow 50-69, red <50.

The v1 schema is well-established and corroborated against [`partner-health-score-drift.md`](partner-health-score-drift.md). **It stays.** v2 adds.

---

## 2. The gap (why extend)

Cross-vendor synthesis (research §3.1, [`/tmp/research-psm-dashboards-k12.md`](/tmp/research-psm-dashboards-k12.md) — accessed 2026-06-04) shows two components are present in every major CSP rubric but absent from the v1 schema:

- **Support load** — Gainsight (10%), Planhat, Totango (Support & Operations: tickets, SLA), ChurnZero, Vitally (25%). Practitioner consensus: support-ticket-velocity + unresolved-P1-count is one of the highest-correlation leading indicators of churn ([SupportLogic — Support Health Score](https://www.supportlogic.com/resources/blog/support-health-score-unifying-customer-support-success/); [Vitally — 4 Metrics](https://www.vitally.io/post/how-to-create-a-customer-health-score-with-four-metrics), both accessed 2026-06-04).
- **Financial / payment health** — partial coverage at Gainsight, Planhat, ChurnZero, Vitally. Captures renewal posture, contract amendments, payment status, ESSER-funding-source flag.

Two more are K-12-specific:

- **Rostering health** — when the data isn't right, it's almost always rostering (house opinion §3 #8 in [`../CLAUDE.md`](../CLAUDE.md)). Already present as alert flags; not yet quantified.
- **Leadership stability** — superintendent / CTO / curriculum-director turnover as renewal-risk event ([User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/); [K-12 Dive](https://www.k12dive.com/news/high-superintendent-turnover-staffed-up/804337/), accessed 2026-06-04). v1's `champion` partially captures it; v2 separates the named-champion signal from the institutional-leadership signal because they decay differently and signal differently.

---

## 3. The v2 components (new)

### 3.1 `support` — ticket-health component

**Rationale.** Support-ticket-velocity + unresolved-P1-count is one of the highest-correlation leading indicators of churn in B2B SaaS ([Vitally — 4 Metrics](https://www.vitally.io/post/how-to-create-a-customer-health-score-with-four-metrics): 25% weight on support; [SupportLogic — Support Health](https://www.supportlogic.com/resources/blog/support-health-score-unifying-customer-support-success/), accessed 2026-06-04). v1's absence of this component means the score doesn't react to a P1 spike until adoption/usage drops, which is 2-4 weeks too late.

**Schema entry:**
```json
{
  "key": "support",
  "name": "Support load",
  "weight": 10,
  "half_life_days": 14,
  "leading": true,
  "plain": "How heavy and how stuck their support situation is.",
  "sub_signals": {
    "ticket_velocity_30d": "tickets per active user, last 30d",
    "unresolved_p1_count": "active P1/P2 tickets open >5 days",
    "escalation_count_30d": "leadership-tier escalations, last 30d",
    "first_response_time_p95": "p95 first-response time, last 30d (seconds)"
  }
}
```

**Recommended weight (default in v2):** 10% — splits 5pp from `usage` (vanity-prone per [`partner-health-score-drift.md`](partner-health-score-drift.md) §6) and 5pp from `touchpoint` (highest-correlated component already; can lose 5pp without losing predictive power).

**Half-life: 14 days** — ticket impact lingers but isn't permanent (research §3.2, accessed 2026-06-04).

**FERPA class:** district-aggregate.

### 3.2 `financial` — renewal / expansion-signal component

**Rationale.** Captures the slow-moving signals that v1 misses entirely: contract amendments (downsizing, term-shortening), payment status, RFP appearance, multi-year-to-annual conversion, and funding-source flags (ESSER-funded districts carry structural renewal risk through 2027 [verify-at-use — 2026-06-04]). Multiple sources put this signal as "partial" across vendors — meaning even the leading CSPs haven't formalized it, but the practitioners are tracking it informally ([Recurly research cited in `renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md): 71% cite price increases as #1 churn driver — a financial signal).

**Schema entry:**
```json
{
  "key": "financial",
  "name": "Financial / renewal posture",
  "weight": 5,
  "half_life_days": 180,
  "leading": false,
  "plain": "Renewal-side signals: payment status, contract shape, funding source.",
  "sub_signals": {
    "payment_status": "current / 30d late / 60d+ late",
    "contract_amendment_12mo": "boolean: any reduction-in-scope amendment in last 12mo",
    "multi_year_status": "single-year / multi-year-locked / multi-year-with-out",
    "funding_source": "general-fund / state-line / esser / title-i / unconfirmed",
    "competitive_rfp_signal": "boolean: vendor selection RFP detected in last 12mo"
  }
}
```

**Recommended weight (default in v2):** 5% — splits from `usage` 5pp.

**Half-life: 180 days** — slow-moving; a contract amendment in March is still meaningful in September. Research §3.2 explicitly recommends 180d for outcome / financial signals (accessed 2026-06-04).

**FERPA class:** district-aggregate.

### 3.3 `rostering_health` — K-12-specific

**Rationale.** Rostering is the silent killer (house opinion §3 #8 in [`../CLAUDE.md`](../CLAUDE.md); see also [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md)). v1's signals don't catch sync failures until they manifest as missing students / classes weeks later. Surfacing rostering as a first-class component lets the dashboard flag the upstream cause, not the downstream symptom.

**Schema entry:**
```json
{
  "key": "rostering_health",
  "name": "Rostering health",
  "weight": 5,
  "half_life_days": 7,
  "leading": true,
  "plain": "Is roster sync running and producing clean data?",
  "sub_signals": {
    "last_sync_hours_ago": "hours since last successful sync",
    "sync_success_rate_30d": "% of attempted syncs that completed cleanly, 30d",
    "active_error_count": "count of active rostering errors",
    "roster_completeness_pct": "% of expected students/teachers present in rostered set",
    "id_drift_count_30d": "count of IDs that changed identity in last 30d"
  }
}
```

**Recommended weight (default in v2):** 5% — K-12 segment only; 0% for higher-ed / corp-ld.

**Half-life: 7 days** — sync issues compound fast.

**FERPA class:** district-aggregate (the sub-signals are operational counts, not student-level).

**Cross-reference:** [`k12-signal-taxonomy.md`](k12-signal-taxonomy.md) §8 lists the underlying signals; this component is the rolled-up composite.

### 3.4 `leadership_stability` — K-12-specific

**Rationale.** v1's `champion` captures the *named* champion (e.g., "Dr. Smith, curriculum director"). It does NOT capture the *institutional-leadership* signal — superintendent / CTO / board-chair turnover that triggers a renewal re-evaluation even when the named champion is still in role.

**Schema entry:**
```json
{
  "key": "leadership_stability",
  "name": "Leadership stability",
  "weight": 5,
  "half_life_days": 365,
  "leading": true,
  "plain": "Are the institutional decision-makers stable, or in transition?",
  "sub_signals": {
    "superintendent_change_12mo": "boolean",
    "cto_change_12mo": "boolean",
    "curriculum_director_change_12mo": "boolean",
    "board_chair_change_12mo": "boolean",
    "admin_disengagement_with_teacher_usage_holding": "diagnostic flag: admin -30% over 60d while teacher flat"
  }
}
```

**Recommended weight (default in v2):** 5% — K-12 segment only; 0% for higher-ed / corp-ld (different leadership dynamics — president / provost / CHRO have different turnover and signal patterns).

**Half-life: 365 days** — leadership transitions resolve over months-to-a-year; the signal shouldn't decay faster than the renewal cycle.

**FERPA class:** district-aggregate.

---

## 4. The v2 composite — full schema

| Key | Name | v1 weight | v2 default weight (K-12) | v2 weight (higher-ed / corp-ld) | Half-life (days) | Leading? |
|---|---|---|---|---|---|---|
| `adoption` | Adoption depth | 25% | 20% | 25% | 90 | leading |
| `touchpoint` | Touchpoint recency | 20% | 15% | 18% | 14 | leading |
| `outcome` | Business outcome | 20% | 20% | 22% | 90 | lagging |
| `sentiment` | Sentiment | 15% | 12% | 15% | 7 *(was 60)* | leading |
| `champion` | Champion strength | 10% | 8% | 10% | 30 *(was 60)* | leading |
| `usage` | Usage breadth | 10% | 5% | 5% | 30 | leading |
| **`support`** | Support load | 0% | 10% | 10% | 14 | leading |
| **`financial`** | Financial posture | 0% | 5% | 5% | 180 | lagging |
| **`rostering_health`** | Rostering health (K-12) | 0% | 5% | 0% | 7 | leading |
| **`leadership_stability`** | Leadership stability (K-12) | 0% | 5% | 0% | 365 | leading |
| **Sum** | | 100% | 100% | 100% | | |

### 4.1 Notes on the half-life changes

Two existing components get faster decay in v2:

- **`sentiment` 60 → 7 days.** Research §3.2 ([Customers.ai](https://customers.ai/recency-weighted-scoring), [Velaris — CS Health Scores](https://www.velaris.io/articles/cs-health-scores), accessed 2026-06-04) explicitly recommends **7d for sentiment** — surveys + call pulses are the freshest signal class and decay rapidly. The v1 60d is too slow; per [`partner-health-score-drift.md`](partner-health-score-drift.md) §2 "Decay too slow," this is the most-common drift cause.
  - **HOWEVER** — for slow-cadence sentiment instruments (annual NPS survey, quarterly CSAT), 7d is too aggressive and the signal will read as "missing" instead of "stable." The half-life applies to the *event* (a survey response, a meeting note); between events the signal holds at its last value rather than decaying. Implementation: decay applies from the most-recent event timestamp, capped at "no signal" not "negative signal."
- **`champion` 60 → 30 days.** A departed champion should ramp toward 0 over a month (research §3.2 "Champion presence: 30 days," accessed 2026-06-04). v1's 60d kept stale champion scores too long.

The v1 → v2 migration path:
1. Quarter 1: deploy v2 schema with new components at 0% weight; run v2 silently against the v1 cohort for one quarter.
2. Quarter 2: raise new-component weights to defaults; keep v1 running.
3. Quarter 3: compare renewal-prediction correlation. If v2 ≥ v1 + ~0.05 correlation, cut over.
4. Quarter 4: v1 retired; v2 is the production rubric.

This is the parallel-run discipline from [`partner-health-score-drift.md`](partner-health-score-drift.md) Step 3.

---

## 5. Per-signal half-life rationale (the full table)

Research §3.2 (accessed 2026-06-04) explicit recommendations:

| Signal class | Half-life | Why | Primary source |
|---|---|---|---|
| Sentiment | **7d** | Surveys + verbal pulses are freshest signals; decay rapidly between events. | [Customers.ai — Recency-Weighted Scoring](https://customers.ai/recency-weighted-scoring); [Velaris — CS Health Scores](https://www.velaris.io/articles/cs-health-scores) |
| Touchpoint | **14d** | Meeting impact lingers ~2 weeks. | [Factors.ai — Time Decay](https://www.factors.ai/blog/time-decay-attribution-model) |
| Support | **30d** *(research listed 30d; we recommend 14d for K-12)* | Ticket impact lingers but isn't permanent. **K-12 modification:** 14d because back-to-school + state-testing windows compress the support cycle. | [SupportLogic — Support Health](https://www.supportlogic.com/resources/blog/support-health-score-unifying-customer-support-success/) |
| Adoption | **90d** | Adoption is a slow-moving signal; deep-feature engagement takes months to build or erode. | [Heap — Leading vs Lagging](https://www.heap.io/blog/from-lagging-to-leading-indicators-a-proactive-approach-to-account-health-scoring) |
| Outcome | **90d** *(research listed 180d)* | Delivered outcomes shouldn't decay fast. **K-12 modification:** 90d to align with quarterly QBR cadence and the K-12 academic-quarter rhythm. | Research §3.2; [Velaris](https://www.velaris.io/articles/cs-health-scores) |
| Financial | **180d** | Slow-moving; contract events stay meaningful for months. | Research §3.2 |
| Champion | **30d** | A departed champion should ramp toward 0 over a month. | Research §3.2 |
| Rostering health | **7d** | Sync issues compound fast. | [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) |
| Leadership stability | **365d** | Leadership transitions resolve over months-to-a-year. | [`k12-signal-taxonomy.md`](k12-signal-taxonomy.md) §4 |
| Usage | **30d** *(v1 default holds)* | Mid-range — usage volume decays faster than adoption depth. | Convergent across vendors |

**Sentinel rule.** The half-life applies to **decay between events**. The signal *value* at the event time is the data; decay tells you how much weight that value still carries today. A signal with no recent events is treated as "no signal" (omitted from the composite) rather than as "0" (which would drag the score down spuriously).

---

## 6. Leading / lagging discipline

Every component carries a `leading | lagging` tag. The dashboard shows the **leading-indicator-weighted subscore** as a separate at-risk filter (per research §3.3 [Heap — Lagging to Leading Indicators](https://www.heap.io/blog/from-lagging-to-leading-indicators-a-proactive-approach-to-account-health-scoring); [Gainsight — Customer Health Scores](https://www.gainsight.com/blog/customer-health-scores/), accessed 2026-06-04).

| Component | Leading or Lagging | Why |
|---|---|---|
| `adoption` | leading | Predicts renewal; precedes outcome by months |
| `touchpoint` | leading | A relationship signal precedes any value signal |
| `outcome` | **lagging** | Measurable result of the partnership; what happens after adoption + value-realization |
| `sentiment` | leading | NPS / CSAT / verbal cues precede churn signals by 30-90 days |
| `champion` | leading | Champion departure precedes admin disengagement by weeks |
| `usage` | leading | Volume signal, but high-volume + low-adoption-depth is misleading; pair with adoption |
| `support` | leading | Ticket spike precedes formal escalation, which precedes churn |
| `financial` | **lagging** | Payment / amendment / RFP signals are mostly outcomes of upstream dissatisfaction |
| `rostering_health` | leading | Sync issues precede data-quality complaints, which precede dissatisfaction |
| `leadership_stability` | leading | Turnover precedes the renewal re-evaluation window by 6-12 months |

The PSM dashboard surfaces:
- **Composite score** (all components × weights × decay): the standard health-band signal.
- **Leading-indicator subscore** (leading components only × weights × decay, renormalized): the forward-looking filter for "what's about to go wrong?" Sorts the at-risk queue.

---

## 7. Persona-segmented subscores

From [`k12-signal-taxonomy.md`](k12-signal-taxonomy.md) §2: every adoption / sentiment / champion signal in K-12 must be tagged per persona. The composite must surface persona-segmented subscores.

```json
{
  "composite": 68,
  "leading_subscore": 64,
  "persona_subscores": {
    "teacher": { "adoption": 84, "sentiment": 78, "champion_strength": null },
    "admin": { "adoption": 38, "sentiment": 52, "champion_strength": 70 },
    "decision_maker": { "touch_recency": 38, "sentiment": 60, "champion_strength": 0 },
    "family": { "activation_pct": 67, "message_open_rate": 41 }
  }
}
```

**Why this matters.** A composite "68 — yellow" hides the buyer-user-decision-maker mismatch ([User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04). Persona-segmented subscores let the PSM diagnose: "teacher persona is green, decision-maker persona is dark red → this is a Recovery — Sponsor Re-Anchor situation, not a product-adoption problem."

The persona subscores are advisory — the composite remains the band-assignment basis — but they appear in the Account 360 drill-down per [`psm-dashboard-canon-2026.md`](psm-dashboard-canon-2026.md) §2.

---

## 8. Migration note for the existing `partner-health-scoring` skill

**Backwards-compatible additive change.** The v1 6-component rubric remains the default; the v2 components default to weight 0 in legacy rubric configs.

### 8.1 Opt-in path

A consumer enables v2 components by adding them to their `components[]` array in `bi-report/data.json` (or equivalent config) with non-zero weights. The skill detects the presence of new keys and routes through the v2 composite math.

### 8.2 Parallel-run convention

The skill SHOULD support `mode: v1 | v2 | parallel`. In `parallel` mode it computes both scores and emits both in the output, letting the PSM team validate v2 against v1 on real renewal outcomes before cutting over (per [`partner-health-score-drift.md`](partner-health-score-drift.md) Step 3).

### 8.3 Documentation requirement

Every component change (add / remove / re-weight) gets a dated entry in the `partner-health-scoring` skill's CHANGELOG-style block (per [`partner-health-score-drift.md`](partner-health-score-drift.md) Step 4 "Document the cut-over").

---

## 9. Anti-patterns (added to the analyst's flag list)

In addition to the existing list in [`partner-health-score-drift.md`](partner-health-score-drift.md):

- A v2 component added without a parallel-run quarter — opinion: cut-over without proof.
- `support` weight raised above 15% — symptom: overfitting to one noisy quarter of escalations.
- `financial` weight raised above 10% — symptom: lagging signal dominating leading-indicator subscore.
- `rostering_health` activated for higher-ed / corp-ld segments — symptom: schema misuse; rostering is K-12 specific.
- `leadership_stability` weighted higher than `champion` — symptom: institutional signal overwhelming named-relationship signal, which is rarely correct.
- Persona subscores not surfaced when persona deltas exceed ~25 points — symptom: hiding the buyer-user-decision-maker mismatch.
- v2 deployed without updating the `daily-action-queue` skill's lifecycle-weight table to reference the new components (per [`../skills/daily-action-queue/SKILL.md`](../skills/daily-action-queue/SKILL.md) §2.3).

---

## 10. Refresh triggers

- A new component class earns its keep on a hold-out cohort (e.g., usage-of-AI-features as a separate signal).
- An existing component's contribution to renewal prediction falls below noise — retire it ([`partner-health-score-drift.md`](partner-health-score-drift.md) §6 "vanity metrics").
- Research updates the convergent half-life numbers (e.g., new academic study revises sentiment decay).
- The K-12-specific components (`rostering_health`, `leadership_stability`) stop being K-12-specific (e.g., higher-ed adopts equivalent dynamics).

---

## 11. References (existing plugin artifacts)

- [`../bi-report/data.json`](../bi-report/data.json) — v1 schema in production.
- [`../skills/partner-health-scoring/SKILL.md`](../skills/partner-health-scoring/SKILL.md) — the skill this extends.
- [`partner-health-score-drift.md`](partner-health-score-drift.md) — drift symptoms and parallel-run discipline this migration follows.
- [`k12-signal-taxonomy.md`](k12-signal-taxonomy.md) — the K-12 signal catalog feeding `rostering_health` and `leadership_stability`.
- [`psm-dashboard-canon-2026.md`](psm-dashboard-canon-2026.md) — the dashboard surface the composite + subscores populate.
- [`ferpa-dashboard-boundaries.md`](ferpa-dashboard-boundaries.md) — the compliance gate every component must clear.
- [`../skills/daily-action-queue/SKILL.md`](../skills/daily-action-queue/SKILL.md) — the action queue that consumes the composite + leading subscore.
- [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) — the rostering diagnostic underlying `rostering_health`.
- [`psm-metrics-glossary.md`](psm-metrics-glossary.md) — the segment-neutral metric glossary referenced for component definitions.
