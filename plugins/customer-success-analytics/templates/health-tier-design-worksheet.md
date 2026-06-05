# Health-Tier Design Worksheet (template)

> **Use for:** designing a transparent, explainable, rule-based Green/Yellow/Red health tier from a chosen signal set — the fillable output of the [`health-tier-design`](../skills/health-tier-design/SKILL.md) skill. This is the **domain-layer spec** the `cs-analytics-architect` / `churn-signal-analyst` produces *before* handing the tier rule to `data-platform` to materialize in the mart.
>
> **Domain-neutral.** Signals are named by *role*, thresholds are placeholders. Fill for the engagement.
>
> **How to use:** copy this file, complete every section, run the `cs_calc.py health-score` mode over the proposed weights to make the per-signal contribution + lagging-share visible, then hand the finished rule expression to `data-platform` (the tier rule lives in the mart / semantic layer, computed once — never in the BI tool). Pairs with [`cs-health-data-model.md`](cs-health-data-model.md) (the schema) and the [`churn-signal-backtest-report.md`](churn-signal-backtest-report.md) (the validation).

---

## 0. Engagement context

| Field | Value |
|---|---|
| Engagement / book | `<name>` |
| Book size (accounts) | `<n>` |
| Segments (if multiple) | `<e.g. enterprise / mid-market / SMB>` |
| CS platform native score available? | `<yes/no — if yes, it is the phase-1 anchor>` |
| Renewal-cycle data available for back-test? | `<yes/no — gates whether thresholds are validated or provisional>` |
| Designed by / date | `<name — YYYY-MM-DD>` |

> **Anchor rule:** if a trusted CS-platform native score exists, it is the **phase-1 anchor** — pulled as-is. The signals below surface *alongside* it as visible sub-indicators, not folded into a silent composite until they demonstrably diverge (CLAUDE.md §4 #2).

---

## 1. Signal selection (5–7 signals — the phase-one discipline)

Aim for **5–7** signals (fewer is fragile, more is unexplainable). Classify each **leading or lagging** *before* including it. **Lagging signals do not enter the tier rule** — they are dashboard context only.

| # | Signal (role) | Leading / Lagging | Grain | Window | Normalized value 0–1 (1 = healthiest) | Source system | In tier rule? |
|---|---|---|---|---|---|---|---|
| 1 | usage-trend slope | leading | account/day | 30/60/90d | `<map>` | product analytics | yes |
| 2 | health-score delta | leading | account/day | 7/30d | `<map>` | CS platform | yes |
| 3 | renewal proximity × engagement | leading (gate) | account | to-renewal | `<map>` | CRM + usage | gate |
| 4 | support P1/P2 rate | leading | account | 30/90d | `<map>` | support tool | yes |
| 5 | champion / sponsor silence | leading | account | trailing | `<map>` | CRM + collab (derived) | yes |
| 6 | `<add if needed>` | `<l/l>` | | | | | |
| 7 | closed-lost / cancellation | **lagging** | account | — | — | CRM | **NO — context only** |

> Every signal must be a **slope/delta where one exists** (direction beats absolute level — §4 #3). A missing source signal is `NULL`, never `0` (§4 #7).

---

## 2. The tier rule (a readable boolean expression)

Write the rule as a boolean over the **leading** signals, with renewal proximity as a **gate (multiplier of urgency), never a standalone risk term**. Example shape:

```
Red    := health_score_trend_30d = down
          AND days_to_renewal < 90
          AND (support_p1_p2_rate_30d > t_support OR champion_silent = true)
Yellow := any one leading signal tripped, renewal not imminent
Green  := otherwise

# Independent fast-triggers run ALONGSIDE the tier, not inside it:
FastTrigger := champion_departed OR active_user_collapse OR explicit_eval_alternatives
            → fire the save play SAME DAY regardless of tier color
```

**Your rule:**

```
Red    := <fill>
Yellow := <fill>
Green  := <fill>
FastTrigger := <fill>
```

| Threshold | Value | Validated or provisional? | Back-test ref |
|---|---|---|---|
| `t_support` | `<value>` | `<validated / PROVISIONAL>` | `<link>` |
| `<others>` | | | |

> A threshold you can't back-test is a guess wearing a number — mark it **`provisional`** and schedule the retune for after the first renewal cycle (§4, `back-test-signals-before-adding-to-tier-rule`).

---

## 3. Weighting & contribution check (run the calculator)

Run `cs_calc.py health-score` with the proposed signal values + weights to make the per-signal contribution and the **lagging-signal share** explicit:

```
python3 ../scripts/cs_calc.py health-score \
    --signal usage_trend:<v>:<w> \
    --signal health_trend:<v>:<w> \
    --signal support_p1p2:<v>:<w> \
    --signal champion_silence:<v>:<w> \
    --signal <...> \
    --green <cut> --yellow <cut>
```

| Check | Pass? | Note |
|---|---|---|
| 5–7 signals | `<>` | calculator warns outside this band |
| Lagging-signal share of score is ~0 | `<>` | lagging signals should not drive the tier |
| Weights reflect predictive strength, not equal-by-default | `<>` | equal weighting is a placeholder, not a design |
| Green/Yellow cut-points justified | `<>` | from back-test, not intuition |

---

## 4. Explainability contract (every Red shows why)

Confirm the design produces, for **every Red and Yellow**, its 2–3 driving signals — each with **name / value / threshold / window**. This is non-negotiable (CLAUDE.md §4 #1, #6).

| Requirement | Met? |
|---|---|
| Every Red names its driving signals | `<>` |
| Each driver shows value, threshold crossed, and window | `<>` |
| No driverless Reds reach the call list | `<>` |

---

## 5. Validation & acceptance

| Gate | Status |
|---|---|
| Back-tested against last renewal cycle (or thresholds marked provisional) | `<>` |
| Did any Green account churn? (the most valuable finding — names the missing signal) | `<>` |
| **Acceptance test:** sort `(tier = Red AND days_to_renewal < 90)` → actionable call list in < 2 minutes | `<>` |
| Segment overrides applied where false-positives concentrate | `<>` |
| Retune scheduled for after the next renewal cycle | `<>` |

---

## 6. Handoff to data-platform

| Item | Owned here (domain) | Handed to data-platform (technical) |
|---|---|---|
| Signal definitions + grain + window | ✅ | — |
| Tier rule expression | ✅ (specify) | materialize in mart / semantic layer |
| Identity resolution / `bridge_account_xref` | — | ✅ (consume the resolved spine only) |
| Pipeline / warehouse / BI surface build | — | ✅ |
| Trend column materialization (slope/delta) | specify | ✅ build in mart |

> The tier rule and every metric live in the **mart / semantic layer, computed once** — never in the BI tool (§4 #12). This plugin specifies; `data-platform` builds.

---

## References

- Skill: [`../skills/health-tier-design/SKILL.md`](../skills/health-tier-design/SKILL.md)
- Calculator: [`../scripts/cs_calc.py`](../scripts/cs_calc.py) (`health-score` mode)
- Signal knowledge: [`../knowledge/cs-health-metrics-and-churn-indicators.md`](../knowledge/cs-health-metrics-and-churn-indicators.md)
- Back-test report template: [`churn-signal-backtest-report.md`](churn-signal-backtest-report.md)
- Data model template: [`cs-health-data-model.md`](cs-health-data-model.md)
