# Churn Signal Back-Test Report

> **Use for:** documenting the back-test result for a candidate churn signal or a full tier rule sweep. One report per signal per back-test run. Produced by the `churn-signal-backtest` skill; handed to the `cs-analytics-architect` to update the tier rule and the knowledge bank.

---

**Signal name:** [signal name — e.g. usage_slope_30d]
**Proposed threshold:** [value + window — e.g. slope < -0.1 over 30 days]
**Report date:** [YYYY-MM-DD]
**Produced by:** [agent or analyst name]
**Data range:** [YYYY-MM-DD to YYYY-MM-DD]

---

## Outcome data summary

| Outcome | Count | % of sample |
|---|---|---|
| Churned | [N] | [%] |
| Renewed | [N] | [%] |
| Expanded | [N] | [%] |
| **Total** | **[N]** | **100%** |

Sample notes: [any caveats — e.g., "excludes accounts with < 6 months tenure"; "provisional — N < 30"]

---

## Back-test result at proposed threshold

| Metric | Value | Bar | Result |
|---|---|---|---|
| True Positives | [N] | — | — |
| False Positives | [N] | — | — |
| False Negatives | [N] | — | — |
| True Negatives | [N] | — | — |
| **Precision** | **[value]** | **> 40%** | **PASS / FAIL** |
| **Recall** | **[value]** | **> 30%** | **PASS / FAIL** |
| F1 score | [value] | — | — |

---

## Threshold sweep (if proposed threshold failed)

| Threshold | Precision | Recall | F1 | Recommended? |
|---|---|---|---|---|
| [value 1] | [%] | [%] | [value] | [yes/no] |
| [value 2] | [%] | [%] | [value] | [yes/no] |
| [value 3] | [%] | [%] | [value] | [yes/no] |

Recommended operating point: [threshold value] — because [1 sentence tradeoff rationale]

---

## Segment breakdown

| Segment | Precision | Recall | N | Note |
|---|---|---|---|---|
| [segment 1] | [%] | [%] | [N] | [above/below bar] |
| [segment 2] | [%] | [%] | [N] | [above/below bar] |
| All | [%] | [%] | [N] | — |

Segment-specific threshold needed: [yes / no — reason if yes]

---

## Recommendation

- [ ] **Include in tier rule** — threshold tuned to [value], window [window]
- [ ] **Sub-indicator only** — show in explainability panel; do not include in tier expression
- [ ] **Validate first** — insufficient sample (N=[N]); re-test after [date] with outcome data from [renewal cycle]
- [ ] **Do not include** — [lagging signal / no predictive value at any threshold / reason]

---

## Signal metadata (for knowledge bank update)

| Field | Value |
|---|---|
| Signal name | [name] |
| Source table | [mart table name] |
| Column | [column name] |
| Grain | [account, daily] |
| Window | [30d / 60d / 90d] |
| Validated date | [YYYY-MM-DD] |
| Validated by | [agent or analyst] |
| Renewal cycle covered | [YYYY Q1 / H1 / other] |

---

## Open questions

- [ ] [Any follow-up needed before the signal enters the tier]
- [ ] [Any segment where a separate threshold is warranted]
