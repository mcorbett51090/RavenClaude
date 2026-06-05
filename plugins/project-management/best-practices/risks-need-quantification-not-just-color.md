# Quantify high-scored risks with EMV — a colour is not a decision

**Status:** Pattern
**Domain:** Risk management
**Applies to:** `project-management`

---

## Why this exists

A 5×5 risk matrix with a red-highlighted cell tells the team that a risk is "high" — but it does not tell them how much contingency reserve to hold, whether the risk is worth the cost of the proposed mitigation, or how it compares to other high risks in priority order. Expected Monetary Value (EMV) is the calculation that converts a probability and a financial impact into a decision-usable number. Without EMV, "high" risks compete for attention based on whoever on the project team talks the loudest. With EMV, the top-three risks are the three with the highest expected loss, and the mitigation budget can be calibrated to the expected benefit.

## How to apply

**EMV formula:**
```
EMV = Probability (%) × Financial Impact (USD or cost equivalent)
```

**Example calculation — worked:**

| Risk | Probability | Financial impact | EMV |
|---|---|---|---|
| Key vendor misses delivery by 4 weeks | 40% | USD 80,000 (4-week delay cost) | **USD 32,000** |
| Integration environment unavailable for UAT | 25% | USD 50,000 (2-week delay + rework) | **USD 12,500** |
| Regulatory approval delayed | 15% | USD 200,000 (full project delay) | **USD 30,000** |

The regulatory risk has the lowest probability but the highest EMV — it should rank higher for mitigation investment than the vendor risk, despite lower probability. Without EMV, the vendor risk (40% — "likely!") often captures all the attention.

**How to estimate the financial impact:**
- **Schedule delay** — cost of delay per week/month (project overhead, team standing time, revenue lost, penalty clauses).
- **Rework** — estimated labour hours × loaded day rate.
- **Compliance / regulatory** — fine exposure, remediation cost, or contract penalty as stated in the contract/regulation.
- If exact figures are not available, use a **three-point estimate**: Optimistic / Most Likely / Pessimistic, then calculate EMV against the Most Likely.

**When to apply EMV (not every risk needs it):**

| Risk score | EMV required? |
|---|---|
| High (top quartile of 5×5 matrix, or P ≥ 3 and I ≥ 3 on a 1–5 scale) | YES — calculate and include in risk register |
| Medium | OPTIONAL — calculate when mitigation budget is being allocated |
| Low | NO — qualitative assessment sufficient |

**Contingency reserve guidance:**
The sum of EMVs for the top-N risks is a data-driven input to the contingency reserve calculation. It is not the only input (schedule risk, known unknowns also contribute), but it anchors the number in analysis rather than gut feel.

**Do:**
- Calculate EMV for every risk that scores in the top quartile of the register.
- Present EMV alongside the qualitative score in the steering pack risk summary — it gives the sponsor a basis for approving contingency.
- Update EMV when probability or impact estimates change (e.g., after a risk trigger event).

**Don't:**
- Treat EMV as a precise prediction — it is a decision-support tool and an order-of-magnitude estimate.
- Quote EMV without stating the probability and impact assumptions explicitly; the number is only as good as the assumptions.
- Omit EMV from the risk register because the numbers are uncertain — an approximate EMV is more useful than a precise colour.

## Edge cases / when the rule does NOT apply

For risks where the impact is entirely non-financial (reputation, team morale, strategic positioning), EMV in monetary terms is not applicable. Qualitative scoring on a defined rubric (with a stated impact descriptor at each level) is the correct approach. The principle — justify prioritisation with more than a colour — still holds.

## See also
- [`../agents/risk-and-raid-analyst.md`](../agents/risk-and-raid-analyst.md) — full risk register methodology
- [`../skills/raid-facilitation/SKILL.md`](../skills/raid-facilitation/SKILL.md) — risk scoring rubric and response assignment

## Provenance

Codifies `risk-and-raid-analyst`'s quantitative risk discipline. Grounded in PMBOK 6 §11.4 (Perform Quantitative Risk Analysis) and EMV as a standard decision-analysis technique.

---

_Last reviewed: 2026-06-05 by `claude`_
