# Priority-score design decisions — the 9-signal rubric and why it is what it is

> **Last reviewed:** 2026-06-04. Sources: v3 cold-review of the build plan ([`docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md`](../../../docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md) §0 cumulative changelog); the leading-vs-lagging discipline in [`../../customer-success-analytics/knowledge/cs-health-metrics-and-churn-indicators.md`](../../customer-success-analytics/knowledge/cs-health-metrics-and-churn-indicators.md) §1; the PSM-cadence dead-zone discipline in [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md); the K-12 renewal-clock anchor in [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md). Refresh when: (a) the weights are SME-tuned against a real post-Q1 renewal cohort, (b) a new signal is proposed for the rubric, or (c) the build plan ships a tier that uses these weights and the PSM team reports gut-feel disagreement on ranking.

This file is the **consult-prior** for the Tier 0 `dashboard-priority-score-rubric.md` deliverable. The build plan tells Codex to author that file with the math; **this file gives Codex (and any future PSM defending the score) the reasoning behind every number.** When the PSM team asks "why is `arr_percentile` only 5% but `open_escalations` is 20%?", the answer lives here.

Companion files: the rubric math (formulas + caps) is in the deliverable `dashboard-priority-score-rubric.md`. The leading-vs-lagging signal classification is in the CS-analytics file linked above — read both.

---

## 1. The 9 signals — formulas, caps, and rationale (v3-corrected)

The full math is in the rubric deliverable. Here we record the **why** for every signal.

| Signal | Default weight | Cap source | Leading? | Why this signal at all |
|---|---|---|---|---|
| `renewal_timing` | 18 | Bucket model (build plan §Step 8) | Leading-when-paired | Days-to-renewal **alone** is not risk — every account hits 90 days. But proximity multiplies the urgency of *every other signal*. The bucket model (100 at ≤30d → 0 at >270d) is a coarse approximation of "how urgent is everything else now"; the rubric pairs it with the engagement signals so proximity never stands alone. |
| `health_decline` | 18 | `max(0, 100 - health_score)` (natural cap at 100) | Leading | The native health-score is the team's anchor signal (per `cs-health-metrics-and-churn-indicators.md` §4, anchor on the CSP's score, add signals additively). Inverted to make `lower health = higher priority` — the rubric is a *priority surface*, not a health surface. |
| `sentiment_decline` | 10 | `max(0, 100 - sentiment_score)` (natural cap) | Leading | Sentiment trend predicts churn; the level is the snapshot. Tier 0 has only point sentiment, so this signal reads as point-decline; Tier 1+ should switch to slope (per CS-analytics §2 "slope beats absolute level"). The 10% weight reflects this Tier-0 limitation — the signal is half-strength until the slope is computable. |
| `days_overdue_vs_cadence` | 10 | Bucket model 100 at ≥60d → 0 at <7d, **suppressed during dead zones** | Leading | "PSM hasn't touched this partner in N days past expected cadence" is one of the strongest single PSM-controllable signals. The bucket cap exists because the v2 first cut was unbounded and broke the score for partners that went radio-silent. **Dead-zone suppression** (`k12-psm-operating-cadence.md`) prevents winter break / state testing windows from firing false alarms. |
| `open_escalations` | 20 | `min(100, open_escalations * 25)` | Leading | The highest single weight in the rubric. Escalations are direct, named partner pain — they outrank a 60-day renewal because an open escalation at T-60 is more recoverable now than at T-30. PSM NEW P1-1 from the v3 cold review bumped this from 15 to 20 over `renewal_timing` after reviewing actual PSM intervention outcomes. **The 25-per-escalation multiplier means 4 escalations = max; this is intentional** — beyond 4 the response is the same (drop everything else), so the priority signal saturates. |
| `ticket_volume` | 5 | `min(100, open_tickets * 10)` | **Lagging** (see §3) | Tickets are a *lagging* signal in CS analytics terms — the partner already filed them, so the dissatisfaction is in the record, not in the future. The low weight (5) reflects the lagging-not-leading discipline; the signal is on the rubric because it's a useful tiebreaker between two similarly-stressed partners, not because it predicts churn. **See §3 for the full leading/lagging audit.** |
| `arr_percentile` | 5 | `100 * percentile_rank(arr, all_partner_arrs)` (natural 0–100) | Context | NOT a risk signal — it's a *value-weight* tiebreaker. A big partner in yellow band outranks a small partner in yellow band when PSM time is constrained. The v3 cold review (P0-4 in v2 → resolved in v3) changed this from a $5k-hard-cap to portfolio-percentile to handle both SMB and enterprise books. Low weight intentionally — it's a tiebreaker, not a driver. |
| `top15_bonus` | 5 | `100 if member else 0` (binary natural cap) | Context | Strategic-logo override. The Top-15 list is an executive-stated "if this one churns, it's a strategic loss" set. The 5% weight is enough to surface a Top-15 partner ahead of a non-Top-15 partner in the same band, but small enough that a non-Top-15 partner with stronger leading signals still outranks them. The discipline is that Top-15 status doesn't excuse a green Top-15 partner from yellow-priority queue position. |
| `usage_decline` | 9 | v3-corrected formula: `0 if usage_trend_30d_pct ≥ 0 else min(100, abs(usage_trend_30d_pct) * 2)` | Leading | The v3 cold review's data-eng NEW P0-2 finding: v2's formula was directionally wrong (growth scored as high decline) and unbounded (declining partners scored >100, schema collision). The corrected formula clamps growth to 0 contribution and caps decline at 100 at -50%. The 9% weight is mid-tier because Tier 0 has only point trend; Tier 1+ should use a 30/60/90 slope. |

**Sum: 18 + 18 + 10 + 10 + 20 + 5 + 5 + 5 + 9 = 100.** Enforced by Check #4 of the integrity gate.

---

## 2. Bucket vs linear scoring — why both, and where each is right

The rubric uses **two scoring modes**: linear functions (e.g., `100 - health_score`) and **bucket functions** (e.g., `renewal_timing` and `days_overdue_vs_cadence`). The decision rule:

**Use a bucket function when the signal has a known threshold structure.**
- `renewal_timing` — the K-12 renewal clock has documented PSM-action thresholds at 180d, 120d, 90d, 60d, 30d (per `renewal-pricing-conversations-edtech.md`). A linear function maps these to gradients that don't reflect the actual action-trigger structure. At 90 days the next motion fires; at 91 days it doesn't. Linear smoothing hides that.
- `days_overdue_vs_cadence` — same thinking. A 7-day overdue is "noticeable"; a 30-day overdue is "intervene"; a 60-day overdue is "PSM coverage gap." The buckets reflect a coarse-grained action surface.

**Use a linear function when the signal is continuous and the action gradient is smooth.**
- `health_decline` — every point of health score is a meaningful gradient; thresholds are arbitrary.
- `usage_decline` — same.
- `arr_percentile` — by definition a continuous percentile.

**Worked example — why linear mis-ranks `renewal_timing`:** Suppose two partners, A (health 50, renewal 30d) and B (health 50, renewal 60d). With a linear `renewal_timing = max(0, 100 - days_to_renewal)`, A scores 70 and B scores 40 — a 30-point gap. With the bucket model (A: 100, B: 85) the gap is 15 points. The bucket gap reflects the actual PSM-decision delta — at 30 days you fire the T-30 motion; at 60 days you fire the T-60 motion, which is similar shape but earlier and slower. The linear scoring over-weights the difference, pulling A up the queue past partners who are objectively in worse shape.

The v2 first cut was all-linear. The v3 cold review's data-eng NEW P0-1 finding was the bucket-model correction for `days_overdue_vs_cadence`.

---

## 3. Leading-vs-lagging — the per-signal audit (the audit Codex won't do unprompted)

This is the section the gap audit flagged. `cs-health-metrics-and-churn-indicators.md` §1 says "before adding any signal to the tier, classify it leading or lagging. If it lags, it is context, not a predictor." The build plan ships 9 signals into the rubric without this audit. Here it is:

| Signal | Classification | Tier-0 verdict | Tier-1+ refinement needed? |
|---|---|---|---|
| `renewal_timing` | **Context** (gates urgency of every other signal) | KEEP at 18% — but the value comes from being a multiplier, not a predictor | No |
| `health_decline` | **Leading** | KEEP at 18% | None — this is the model-anchor signal |
| `sentiment_decline` | **Leading-when-slope, lagging-when-level** | KEEP at 10% (point sentiment, half-strength) | **Yes** — Tier 1+ should use a 7/30-day slope. Re-weight when slope is available. |
| `days_overdue_vs_cadence` | **Leading** | KEEP at 10% | None |
| `open_escalations` | **Leading** | KEEP at 20% (the highest weight) | None |
| `ticket_volume` | **Lagging** — CS-analytics §3 #4 explicit on this | KEEP at 5% as a **tiebreaker only** | **Yes** — Tier 1+ should switch to ticket-spike-rate (P1/P2 in the 30-day window, per CS-analytics) which IS leading. The current weight reflects the lagging-not-leading discount. |
| `arr_percentile` | **Context** (value weight, not risk) | KEEP at 5% | No |
| `top15_bonus` | **Context** (strategic override) | KEEP at 5% | No |
| `usage_decline` | **Leading-when-slope, lagging-when-level** | KEEP at 9% (point trend, partial-strength) | **Yes** — Tier 1+ should use a 30/60/90-day slope. |

**Three signals need Tier-1+ refinement** (sentiment, ticket, usage). The discipline: when refining, **adjust the weights at the same time** — making a signal stronger by switching it from level to slope means the weight should rise. The current weights are tuned for the Tier-0 point-measurement floor.

**Cross-reference seam.** `cs-analytics-architect` and `churn-signal-analyst` ([`../../customer-success-analytics/`](../../customer-success-analytics/)) are the right reviewers for this audit. The build plan does not route to them; future tiers should.

---

## 4. Why portfolio-percentile beats absolute-cap for `arr_percentile`

The v2 first cut had a `$5,000 hard cap on monthly ARR contribution`. The cold-review finding was: this works for a 25-partner SMB book but fails for an enterprise book (median ARR $50k, top quartile $500k). A $5k cap means every partner in the top 80% scores the same. The rubric stops distinguishing.

Portfolio-percentile-rank fixes this: no matter what the book's ARR distribution looks like, the signal is `where does this partner rank inside this book`. A median partner in an SMB book and a median partner in an enterprise book both score 50 — which is correct. The signal carries the book's shape with it.

**The discipline:** `percentile_rank` must be computed at fixture-write time, not at render time. The percentile is a function of the full book; recomputing it at render time on a filtered view (e.g., only Top-15) would produce wrong ranks. The synthesizer is the right computer.

---

## 5. Why `open_escalations` outweighs `renewal_timing`

This is the second weight-change the v3 cold review made (PSM NEW P1-1). The reasoning:

- An open escalation at any time is **active, named, recoverable** partner pain. The PSM has a defined motion: own the escalation, drive resolution, follow up at 7-day intervals until closed.
- A renewal at 60 days is **planned work** — the T-60 motion exists, but it's a scheduled motion, not a fire drill.
- An open escalation at T-60 is **both** — the escalation has to close before the T-60 conversation can be productive. So the priority is correctly "address the escalation first."

The 20 vs 18 weight ratio reflects this **active-pain-outranks-planned-work** principle. The ratio is intentionally small (2 points, ~10% relative) — the rubric does not say a single escalation at T-180 outranks a renewal at T-30. It says, all else equal, the escalation-side noise matters more.

The empirical test: when this rubric ships against a real post-Q1 cohort, audit whether partners with `open_escalations ≥ 1 AND renewal_date ≤ 60` were addressed in escalation-first order or renewal-first order, and whether the escalation-first cohort had better outcomes. The weight is calibrated to that test.

---

## 6. Composition contract — derivation, rounding, render-time discipline

```python
priority_breakdown[k] = round(per_signal_formula(partner_data), 2)  # 0–100, clamped
priority_score = round(sum(weights[k] * priority_breakdown[k]) / 100, 2)
```

Both rounded to 2 decimals **at construction** in `synthesize.py`, not at output time. The check-psm-data-integrity.py Check #6 verifies `priority_score == round(sum(...) / 100, 2)` for every partner using the same rounding discipline.

**Per-signal contribution percent — derived at render time, never stored:**

```
contribution[k] % = (weights[k] * priority_breakdown[k]) / (priority_score * 100) * 100
```

Why derived: the contribution is a function of the score, which is a function of the weights. Storing it means a weight-tuning change requires regenerating every partner's stored contributions. The render-time derivation costs nothing (the renderer already has the weights and breakdown).

`field-classifications.json` marks `priority_breakdown` as both `synthetic_only` (in the Tier 0 fixture) AND `derived_at_render` (for Tier 1+ on real data) — Tier 1+ doesn't carry pre-computed signal values; it computes from `partner` + signal source at render time.

---

## 7. Default weights and the SME-review gate

The default weights in §1 are an SME starting point. The build plan ships them as the Tier 0 default. **They are not load-bearing tuning.** The post-Tier 0 discipline:

1. **First-Q gate.** After Tier 1 ships and the first real PSM week passes, the PSM (or the cs-analytics-architect agent) audits the top-10 priority partners against the PSM's gut-feel ranking. **A diff of more than ~3 partners is a weight-tuning trigger.**
2. **First renewal-cycle gate.** After the first renewal cycle's outcomes are known, back-test the rubric against actual churn / save / renewal-flat / expansion outcomes. The signals whose weight was wrong are the ones whose breakdown values were strong but the outcome contradicted, or weak but the outcome confirmed.
3. **The output is a weight-tuning PR**, not a rubric-redesign PR. Weights move; formulas don't (Tier 1+); the rubric becomes config-driven (per the strategic plan A4). The formula-change conversation requires both a PSM AND a cs-analytics-architect sign-off.

**Until the first SME review lands, all weights are MARKED PROVISIONAL** in the rubric deliverable. The build plan does not flag this; future PRs should.

---

## 8. Anti-patterns this file exists to prevent

- Shipping the priority-score rubric without naming the lagging signals (`ticket_volume`, point-sentiment, point-usage) as lagging.
- Defending a weight by appeal to "feels right" — the §5 reasoning for `open_escalations > renewal_timing` is the model.
- Adding a new signal without classifying it leading-or-lagging in §3 first.
- Tuning weights to match a PSM's pre-existing gut-feel ranking instead of using the gut-feel ranking as a back-test cohort (`partner-health-score-drift.md` §"Anti-patterns" calls this overfitting to existing bias).
- Hardcoding the rubric's caps at fixture-time and forgetting to re-derive at render-time when the partner data changes.
- Storing `contribution[k]%` in the data file (force-derives the renderer's weights into the data, making weight-tuning a data-rewrite).
- Using a `$X` absolute cap on `arr_percentile` (breaks for non-SMB books — see §4).
- Linear-scoring `renewal_timing` (mis-ranks at the threshold gradients — see §2).
- Shipping a config-driven rubric whose defaults haven't passed SME review (§7 — the rubric-defaults-must-be-SME-reviewed best-practice is the discipline).

---

## 9. Refresh triggers for this document

- The default weights are SME-tuned against a real post-Q1 cohort — record the change in §1 with a date and the cohort details.
- A new signal is proposed for the rubric — record the leading/lagging classification in §3 BEFORE shipping the signal.
- The Tier 1+ slope-conversion lands for `sentiment`, `usage`, or `ticket-rate` — re-weight per the §3 "Tier-1+ refinement needed" column.
- The strategic plan A4 config-driven rubric arrives — keep this file as the rationale source; the rubric file becomes the YAML / JSON config.
- A PSM team disputes a partner's ranking and the dispute is traced to a signal-formula issue — record the dispute, the diagnosis, and the resolution in this file.
