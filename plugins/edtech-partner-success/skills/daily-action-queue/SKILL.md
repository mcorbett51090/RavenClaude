---
name: daily-action-queue
description: Compute "today's top N accounts" for a K-12 EdTech PSM as a ranked list with next-best-action + confidence + rationale. Weighted-signal formula (lifecycle-aware), with RICE / ICE as alternate framings. Every action carries an explicit rationale string naming the dominant signal + the threshold crossed + the prescribed play. Designed so the PSM can answer "why this account today?" in one sentence.
last_reviewed: 2026-06-04
confidence: high
primary_agent: partner-success-manager
secondary_agents: learning-analytics-analyst, success-playbook-designer
---

# Daily Action Queue — Skill

> **What this skill does.** Reads a PSM's portfolio + signal table + lifecycle stages + the day's date, and returns a ranked list of accounts with `{score, top_3_signals, recommended_action, rationale_string, confidence}`. The output is the data behind the **Daily Action Center** widget in the PSM home page (see [`../../knowledge/psm-dashboard-canon-2026.md`](../../knowledge/psm-dashboard-canon-2026.md) §2).
>
> **What this skill is NOT.** It's not a generic "top customers" ranker — it's the math behind the next-best-action surface that names the play. A bare ranking without a rationale string is a regression, not a feature.

---

## 1. Contract

### 1.1 Input

```yaml
psm_id: "dana.l"
portfolio:
  - account_id: "riverside-usd"
    lifecycle_stage: "renewal-build"      # onboarding | early-adoption | steady-state | renewal-build | renewal-active | recovery
    tier: 1                               # 1 (top 10-15%, monthly) | 2 (25-30%, quarterly) | 3 (55-65%, self-serve)
    arr_usd: 240000
    renewal_date: "2026-11-15"
    segment: "k12"
    flags:                                # K-12 overlay flags from k12-signal-taxonomy.md
      esser_funded: true
      superintendent_change_12mo: false
      state_testing_window_active: false
signal_table:
  - account_id: "riverside-usd"
    signals:
      teacher_adoption: { value: 84, leading: true, half_life_days: 7, last_event: "2026-06-03" }
      admin_engagement: { value: 88, leading: true, half_life_days: 14, last_event: "2026-06-02" }
      decision_maker_touch_recency: { value: 70, leading: true, half_life_days: 30, last_event: "2026-05-22" }
      # ... full schema in health-score-v2-extension.md
current_date: "2026-06-04"
framework: "weighted"                     # weighted (default) | rice | ice
top_n: 10
```

### 1.2 Output

```yaml
queue:
  - rank: 1
    account_id: "pinecrest-isd"
    score: 87.3                           # 0-100, higher = more urgent
    top_3_signals:
      - { signal: "champion_status", value: 0, delta_30d: -100, threshold: "champion departure" }
      - { signal: "decision_maker_touch_recency", value: 38, threshold: ">21d zero touchpoints" }
      - { signal: "esser_funded", value: 1, threshold: "structural renewal risk" }
    recommended_action: "Run Recovery — Sponsor Re-Anchor play"
    rationale_string: "Pinecrest ISD: named champion departed + 21d zero meaningful touchpoints + ESSER-funded with Oct renewal → Recovery — Sponsor Re-Anchor play, owner Marcus T., target meeting by 2026-06-09."
    confidence: 0.86
    play_id: "recovery-sponsor-re-anchor"
    suppressed_reason: null               # populated if signal suppressed by dead-zone (k12-psm-operating-cadence.md §2)
  - rank: 2
    # ...
```

The **rationale_string** is the differentiator. Without it, this skill is bare top-K ranking; with it, it's an NBA surface ([Inogic — NBA in CRM](https://www.inogic.com/blog/2026/05/how-ai-recommends-the-next-best-action-in-crm-with-real-examples/), accessed 2026-06-04).

---

## 2. The weighted-signal formula (default)

### 2.1 Core scaffold

> **Account priority score = Σᵢ (weightᵢ × signalᵢ × recency_decayᵢ) × tier_multiplier × lifecycle_multiplier × k12_overlay**

Signals are normalized 0-1. Weights sum to 1.0. Convergent scaffold from 5 independent sources ([Customers.ai — Recency-Weighted Scoring](https://customers.ai/recency-weighted-scoring); [Vitally — 4 Metrics](https://www.vitally.io/post/how-to-create-a-customer-health-score-with-four-metrics); [Gainsight — Customer Health Scores](https://www.gainsight.com/blog/customer-health-scores/) — SERP summary; [Typewise — Prioritizing Support Tickets](https://www.typewise.app/blog/prioritizing-support-tickets-method); [Heap — Lagging to Leading Indicators](https://www.heap.io/blog/from-lagging-to-leading-indicators-a-proactive-approach-to-account-health-scoring), all accessed 2026-06-04).

### 2.2 Recency decay

Per [`../../knowledge/health-score-v2-extension.md`](../../knowledge/health-score-v2-extension.md):

```
recency_decay(signal) = 2^(-Δdays / half_life_days)
```

Per-signal-class half-lives (defaults; configurable):
- Sentiment: **7d** — fast-decay, surveys + verbal pulses ([Customers.ai](https://customers.ai/recency-weighted-scoring), accessed 2026-06-04; convergent with [Velaris — CS Health Scores](https://www.velaris.io/articles/cs-health-scores)).
- Touchpoint: **14d** — meeting recency ([Factors.ai — Time Decay](https://www.factors.ai/blog/time-decay-attribution-model), accessed 2026-06-04).
- Support: **30d** — ticket impact lingers but isn't permanent.
- Adoption / outcome: **90d** — delivered outcomes shouldn't decay fast.
- Financial / renewal posture: **180d** — slow-moving.

Note: the research lists adoption / outcome at 90d half-life — this overrides the 7d default seen in marketing-attribution contexts because partner adoption isn't a click-event signal ([Heap — Leading vs Lagging](https://www.heap.io/blog/from-lagging-to-leading-indicators-a-proactive-approach-to-account-health-scoring), accessed 2026-06-04).

### 2.3 Lifecycle-aware weight vectors

"Early in the journey, usage and onboarding signals may be weighted more heavily, while later, outcomes and adoption patterns become stronger predictors" ([Heap](https://www.heap.io/blog/from-lagging-to-leading-indicators-a-proactive-approach-to-account-health-scoring), accessed 2026-06-04). The weight vector is a function of lifecycle stage, not a single fixed vector.

| Lifecycle stage | Adoption | Touchpoint | Outcome | Sentiment | Champion | Support | Financial |
|---|---|---|---|---|---|---|---|
| Onboarding (Day 1-90) | 35% | 25% | 5% | 10% | 10% | 15% | 0% |
| Early-adoption (Day 91-365) | 30% | 20% | 15% | 10% | 10% | 10% | 5% |
| Steady-state | 20% | 15% | 25% | 10% | 10% | 10% | 10% |
| Renewal-build (T-180 to T-90) | 15% | 15% | 25% | 10% | 15% | 5% | 15% |
| Renewal-active (T-90 to T-0) | 10% | 20% | 20% | 15% | 20% | 5% | 10% |
| Recovery | 25% | 25% | 15% | 5% | 20% | 10% | 0% |

These are seed weights; tune against renewal outcomes per [`partner-health-score-drift.md`](../../knowledge/partner-health-score-drift.md) Step 2 "Hold-out cohort."

### 2.4 Tier multiplier

Common-tier model (convergent across [Velaris — Account Prioritization](https://www.velaris.io/articles/account-prioritization-cs); [Customer Imperative — Portfolio Segmentation](https://customerimperative.com/customer-portfolio-segmentation-for-customer-success-managers/), accessed 2026-06-04):

| Tier | Multiplier | Description |
|---|---|---|
| 1 | ×1.3 | Top 10-15% ARR — monthly check-ins |
| 2 | ×1.0 | 25-30% — quarterly + automation |
| 3 | ×0.7 | 55-65% — self-serve + reactive |

### 2.5 K-12 overlay multipliers

From [`k12-signal-taxonomy.md`](../../knowledge/k12-signal-taxonomy.md):

- ESSER-funded account: ×1.3 (structural renewal risk through 2027 [verify-at-use — 2026-06-04]).
- Superintendent / CTO / curriculum-director change in last 12 months: ×1.2 (each, multiplicative — capped at ×1.5 total to prevent runaway).
- State-testing-window-active: **suppression** — usage signals contribute 0 to score during window; recovery rate post-window participates in next-day score.
- Funding-source unconfirmed AND in renewal-build stage: ×1.4.

---

## 3. Recommended-action mapping

The rationale string names the play. The play mapping is a lookup, owned by the `success-playbook-designer` agent:

| Dominant signal class | Lifecycle stage | Play |
|---|---|---|
| Champion departure | any | Recovery — Sponsor Re-Anchor |
| Admin disengagement + teacher usage holding | renewal-build / renewal-active | Recovery — Leadership-Watch Outreach |
| Roster sync errors active | any | Implementation — Rostering Diagnostic |
| State-testing-window post-recovery <50% | early-adoption / steady-state | Recovery — Post-Testing Re-Engagement |
| License claim rate <50% by Day 14 (Activation Watch) | onboarding | Onboarding — Phase 2 Recovery |
| Decision-maker touch recency >30d AND renewal-build | renewal-build | Renewal — Sponsor Confirmation Sync |
| Sentiment NPS drop >20 over 60d, admin persona | any | Account 360 — Diagnose persona |
| Outcome milestone met + sentiment up + tier-1 | steady-state | Expansion — Value-Trigger Outreach |
| Health composite stable, tier-3, low touch | steady-state | Maintain — async check-in |

Plays are defined under the [`success-playbook-designer`](../../agents/success-playbook-designer.md) agent's owned skills (`renewal-play-design`, `expansion-play-design`, `recovery-play-design`).

---

## 4. The rationale string — anatomy

Every entry in the queue produces a rationale string that names:

1. **The account** (named, not "Account #4")
2. **The dominant signal + the threshold crossed** (with numbers)
3. **The lifecycle context** (so the PSM knows why now)
4. **The prescribed play + owner + date target**

### 4.1 Good rationale strings

> "Westfield USD: usage -34% over 14d in Phase 2 onboarding (target: ≥75% weekly active by Day 30 — currently 41%) → run *Phase 2 Recovery* play, owner Dana L., target meeting by 2026-06-09."

> "Granite State University: NPS 'we're evaluating alternatives' + 2 consecutive support escalations to leadership tier in renewal-active stage (T-57) → *Recovery — Sponsor Re-Anchor*, owner Priya R., target exec sponsor call by 2026-06-07."

> "Northshore Academy: outcome milestone 'family activation >85%' met + sentiment +12 over 60d + tier-1 in steady-state → *Expansion — Value-Trigger Outreach*, owner Priya R., propose tier upgrade at next QBR 2026-06-25."

### 4.2 Bad rationale strings (regressions to top-K ranking)

> "Pinecrest ISD: low health score." ← no signal named, no threshold, no play.

> "Cedar Valley is trending down." ← no number, no lifecycle context, no action.

> "High-priority account." ← reveals nothing; the PSM has to do the work themselves.

The hook in [`../../hooks/flag-psm-anti-patterns.sh`](../../hooks/flag-psm-anti-patterns.sh) should be extended to flag rationale strings that omit any of (signal name | numeric threshold | play | owner | date).

---

## 5. NBA confidence — what to report

Every recommended action carries `confidence: 0.0-1.0` per the cross-plugin NBA convention ([Inogic — NBA in CRM](https://www.inogic.com/blog/2026/05/how-ai-recommends-the-next-best-action-in-crm-with-real-examples/), accessed 2026-06-04: "Each potential action … is given a score based on expected impact … Recommendations surface with priority levels and confidence percentages — for example, Recommendation A at high priority with 92% confidence").

### 5.1 Confidence calculation

```
confidence = min(
    signal_freshness_score,           # 1.0 if all top-3 signals < half-life; decays otherwise
    play_match_strength,              # 1.0 for exact lookup match; 0.6 if best-match fallback
    rationale_completeness            # 1.0 if all 4 anatomy components present; -0.2 per missing
)
```

### 5.2 Confidence bands

- **≥ 0.85** — present in queue, recommended for action today, auto-triggers Cited-Adjudicator review per [`../../../ravenclaude-core/rules/agent-collaboration.md`](../../../ravenclaude-core/rules/agent-collaboration.md).
- **0.70 - 0.84** — present in queue, surfaced for review; PSM judgment required.
- **< 0.70** — held back; surfaced as "low-confidence candidates" in a separate small-multiples panel, not the main queue. Avoids alarm fatigue ([Activu — SOC Best Practices](https://www.activu.com/security-operations-center-dashboard-best-practices-a-checklist-for-critical-situational-awareness/), accessed 2026-06-04).

---

## 6. Alternate frameworks — RICE / ICE

Sophisticated teams sometimes apply PM-prioritization frameworks to daily-queue ranking. Expose as alternates via `framework: rice|ice`.

### 6.1 RICE (Reach × Impact × Confidence ÷ Effort)

Borrowed from product roadmap prioritization ([ProductPlan — RICE](https://www.productplan.com/glossary/rice-scoring-model); [Intercom — RICE Prioritization](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/), accessed 2026-06-04).

PSM-adapted:
- **Reach** — number of stakeholders / classrooms / schools affected by the play (e.g., a district-wide rostering fix has high reach; a single-champion re-anchor has low reach).
- **Impact** — ARR at risk × probability the play addresses it (0.25 / 0.5 / 1 / 2 / 3 scale).
- **Confidence** — PSM's confidence the play succeeds (50% / 80% / 100%).
- **Effort** — PSM-hours to execute (1 / 2 / 5 / 8 scale).

Useful when the queue contains items of *very different sizes* — a 1-hour async check-in shouldn't outrank an 8-hour escalation prep just because the weighted-signal score is higher.

### 6.2 ICE (Impact × Confidence × Ease)

Lighter-weight; suitable for action-by-action triage ([Kaizenko — ICE / RICE / Weighted Scoring](https://www.kaizenko.com/scoring-frameworks-ice-rice-and-weighted-scoring-for-product-prioritization/), accessed 2026-06-04). Used as the default fallback when Effort estimation isn't available.

### 6.3 When to use which

| Framework | Use when |
|---|---|
| `weighted` (default) | Day-to-day operational queue. The PSM has a defined book; signals are the source of truth. |
| `rice` | Quarterly book-rebalance; deciding which plays to invest meaningful effort in over a longer horizon. |
| `ice` | Triage when many small actions compete and effort isn't easily quantified. |

The weighted-signal default is correct for ~90% of PSM operational use. RICE / ICE exist for the planning-mode cases the manager and PSM together review.

---

## 7. Worked examples

### 7.1 Example A — Recovery account (high-confidence)

**Input:**
- Account: Pinecrest ISD, K-12 district, ARR $180K, renewal 2026-10-01.
- Lifecycle: renewal-build (T-119).
- Tier: 2.
- Flags: ESSER-funded = true; superintendent_change_12mo = true.
- Signals (most recent):
  - `champion_status`: 0 (departed 2026-05-08) — leading, half-life 30d → recency_decay = 2^(-27/30) = 0.54
  - `decision_maker_touch_recency`: 38 (last touch 2026-05-08 = 27 days ago) — leading, half-life 30d → 0.54
  - `teacher_adoption`: 40 (last event 2026-06-02) — leading, half-life 7d → 2^(-2/7) = 0.82
  - `admin_engagement`: 38 — leading, half-life 14d → 0.91
  - `sentiment`: 52 — leading, half-life 7d → 0.82
  - `outcome`: 50 — lagging, half-life 90d → 0.99

**Calculation (renewal-build weights):**

```
base = 0.15×40×0.82 + 0.15×38×0.91 + 0.25×50×0.99 + 0.10×52×0.82
     + 0.15×0×0.54 + 0.05×ticket_score + 0.15×financial_score
    ≈ 0.15×32.8 + 0.15×34.6 + 0.25×49.5 + 0.10×42.6 + 0.15×0 + ...
    ≈ 4.9 + 5.2 + 12.4 + 4.3 + 0 + ...
    ≈ 26.8 (raw composite, 0-100, lower = sicker)
```

Convert to **urgency**: urgency = 100 - composite = 73.2.

Apply multipliers:
- Tier 2: ×1.0
- Lifecycle renewal-build: weights already applied
- K-12 overlay: ESSER ×1.3 × superintendent_change ×1.2 = ×1.56 (capped at ×1.5)

**Final score:** 73.2 × 1.5 = **109.8** → clamp to top of band; this account is **rank 1**.

**Top 3 signals (by leading-indicator-weighted contribution to deficit):**
1. `champion_status` (0; threshold "champion departure" crossed)
2. `decision_maker_touch_recency` (38; threshold ">21d zero touchpoints" crossed)
3. `esser_funded` flag (priority multiplier active)

**Recommended action:** Recovery — Sponsor Re-Anchor (mapped via §3 table; "Champion departure" → this play).

**Rationale string:** "Pinecrest ISD: named champion departed 2026-05-08 + 27d zero meaningful touchpoints + ESSER-funded with 2026-10-01 renewal (T-119, renewal-build) → *Recovery — Sponsor Re-Anchor* play, owner Marcus T., target sponsor call by 2026-06-09."

**Confidence:**
- signal_freshness_score = 0.82 (top signals' decay weighted)
- play_match_strength = 1.0 (exact lookup match)
- rationale_completeness = 1.0 (all 4 anatomy components present)
- **confidence = min(0.82, 1.0, 1.0) = 0.82**

### 7.2 Example B — Onboarding Phase 2 (mid-confidence)

**Input:**
- Account: Westfield USD, K-12 district, ARR $95K, contract started 2026-04-15.
- Lifecycle: onboarding (Day 50).
- Tier: 2.
- Signals: `teacher_adoption`: 41 (target ≥75% by Day 30); `license_claim_rate`: 62; `roster_sync_error_count`: 3 active.

**Top 3 signals:**
1. `teacher_adoption` (41; threshold "≥75% weekly active by Day 30" crossed downward — actually a -34% drop over 14d)
2. `license_claim_rate` (62; threshold "≥80% by Day 14" missed)
3. `roster_sync_error_count` (3 active; threshold "0 active errors" crossed)

**Recommended action:** Onboarding — Phase 2 Recovery.

**Rationale string:** "Westfield USD: usage -34% over 14d in Phase 2 onboarding (Day 50, target ≥75% weekly active by Day 30 — currently 41%) + 3 active roster errors → *Onboarding — Phase 2 Recovery* play, owner Dana L., diagnostic call + rostering escalation by 2026-06-09."

**Confidence:**
- signal_freshness_score = 0.95 (all signals < half-life)
- play_match_strength = 1.0 (exact match)
- rationale_completeness = 1.0
- **confidence = 0.95**

### 7.3 Example C — Suppression case (dead-zone)

**Input:**
- Account: Mesa Community College, higher-ed, contract steady-state.
- Date: 2026-12-23 (winter break).
- Signal: `teacher_adoption`: 18 (would normally trigger yellow).

**Computation:**
- `state_testing_window_active` = false but **calendar dead-zone** = "winter break" per [`k12-psm-operating-cadence.md`](../../knowledge/k12-psm-operating-cadence.md) §2.
- For higher-ed: finals week + winter break suppression active.

**Output:**
```yaml
- rank: null
  account_id: "mesa-cc"
  score: 0
  suppressed_reason: "winter-break dead zone active 2026-12-22 through 2026-01-02; resume signal evaluation 2026-01-03"
  recommended_action: null
  rationale_string: "Mesa Community College: signal suppressed — winter-break dead zone (2026-12-22 → 2026-01-02). Resume at 2026-01-03."
```

The suppressed item appears in a "Suppressed today" collapsible section, not the main queue. Avoids alarm fatigue ([Activu — SOC Best Practices](https://www.activu.com/security-operations-center-dashboard-best-practices-a-checklist-for-critical-situational-awareness/), accessed 2026-06-04).

---

## 8. Trigger thresholds (practitioner-validated)

From [Lyniro — 15-Play Playbook](https://lyniro.com/blog/customer-success-playbook/) and [Planhat — Churn & Retention](https://www.planhat.com/customer-success/churn-and-retention) (accessed 2026-06-04):

| Trigger | Threshold |
|---|---|
| Onboarding risk | <50% license utilization in first 30 days; 2-week decline in WAU during onboarding; no client activity for 10+ days; 2+ blocked tasks simultaneously |
| Renewal | health score enters defined risk band within 90 days of renewal; outreach 90 days before renewal for annual contracts (**K-12 overlay:** 120-180 days per [`renewal-pricing-conversations-edtech.md`](../../knowledge/renewal-pricing-conversations-edtech.md)) |
| Expansion | customers hitting plan limits; regularly engaging with advanced features |
| Churn | product usage drops below baseline for 2 consecutive weeks; health score <threshold; 2+ churn signals simultaneously |

These are the calibration anchors for the threshold language in rationale strings ("threshold X crossed" — point to one of these).

---

## 9. Anti-patterns this skill must flag

- Rationale strings without a named signal, threshold, play, owner, AND date (all 4 required — see §4).
- Confidence reported without the three sub-scores (signal_freshness / play_match / rationale_completeness).
- A queue item firing during a dead zone without `suppressed_reason` populated.
- A score that places a tier-3 self-serve account above a tier-1 high-ARR account *without* the tier multiplier having been applied.
- An ESSER-funded account in renewal-build stage that doesn't carry the priority-multiplier flag.
- A weighted-signal output where weights don't sum to 1.0 (rounding to 0.99-1.01 OK).
- A persona-aggregated signal where the per-persona breakdown contradicts the aggregate (e.g., teacher_adoption holding at 84 but admin_engagement at 18 → the aggregate "adoption: 51" hides the real signal; surface both).
- A renewal-build / renewal-active item where decision-maker touch recency >30d AND no Recovery — Sponsor Confirmation Sync play has fired.

---

## 10. Output Contract (skill-level)

The skill returns the queue, and (per the plugin's Output Contract in [`../../CLAUDE.md`](../../CLAUDE.md) §6) the calling agent emits:

```
Status: ✅  |  ⚠️ partial  |  ❌ blocked
Files changed: <relative paths or "none">
Partner / segment context: PSM portfolio (segment K-12 / higher-ed / corp-ld / mixed)
Signals cited: (per-item, named in the rationale strings)
Followups: top-N items with owners + dates (from rationale_string)
Open questions: any low-confidence items (<0.70) held back
Grounding checks performed: confidence sub-scores computed; dead-zone suppression rules applied
```

Plus the cross-plugin Structured Output Protocol JSON block.

---

## 11. References (existing plugin artifacts)

- [`../../knowledge/psm-dashboard-canon-2026.md`](../../knowledge/psm-dashboard-canon-2026.md) — the dashboard surface this queue populates.
- [`../../knowledge/k12-signal-taxonomy.md`](../../knowledge/k12-signal-taxonomy.md) — the K-12 signal catalog this queue weights.
- [`../../knowledge/health-score-v2-extension.md`](../../knowledge/health-score-v2-extension.md) — the composite health score used as a signal input.
- [`../../knowledge/partner-health-score-drift.md`](../../knowledge/partner-health-score-drift.md) — drift symptoms that retire signals from §2 weights.
- [`../../knowledge/k12-psm-operating-cadence.md`](../../knowledge/k12-psm-operating-cadence.md) — dead-zone suppression rules.
- [`../../knowledge/ferpa-dashboard-boundaries.md`](../../knowledge/ferpa-dashboard-boundaries.md) — FERPA compliance gate every signal must clear.
- [`../partner-health-scoring/SKILL.md`](../partner-health-scoring/SKILL.md) — the composite-score skill this queue consumes.
- [`../renewal-play-design/SKILL.md`](../renewal-play-design/SKILL.md), [`../expansion-play-design/SKILL.md`](../expansion-play-design/SKILL.md), [`../recovery-play-design/SKILL.md`](../recovery-play-design/SKILL.md) — the play library §3's mapping references.

---

## 12. Refresh triggers

- The convergent-weight-vector consensus shifts (e.g., new academic research on CS health-score validity).
- A new lifecycle stage emerges in the PSM's book (e.g., post-merger consolidation as a distinct stage).
- A play in §3's mapping table is retired or replaced.
- Confidence calibration shows confidence bands don't predict play-success rates (per [`partner-health-score-drift.md`](../../knowledge/partner-health-score-drift.md) Step 5 quarterly check-in).
- Vendor NBA conventions evolve away from the [confidence + rationale] standard.
