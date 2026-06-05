# The Expense Ratio Has Two Levers — Acquisition Cost and Internal Expense

**Status:** Primary diagnostic
**Domain:** Portfolio analytics / expense management
**Applies to:** `insurance-pc`

---

## Why this exists

An elevated combined ratio attributable to the expense side requires different interventions depending on which component is driving it. Acquisition costs (commissions, brokerage, premium taxes) and internal expense (underwriting, claims, IT, overhead) respond to entirely different levers: acquisition cost is managed by channel mix, commission structure, and volume; internal expense is managed by staffing, automation, and overhead allocation. A management report that shows only total expense ratio obscures which lever to pull. Similarly, a carrier that benchmarks its expense ratio to industry without disaggregating the two components may conclude it is competitive when its acquisition cost is high and its operating expense is low — or vice versa.

## How to apply

Present the expense ratio in two components in every portfolio management report.

```
Expense Ratio Decomposition
──────────────────────────────────────────────────────
Component                         | Current period | Prior period | Industry bench [unverified]
──────────────────────────────────|────────────────|──────────────|──────────────
Acquisition cost ratio            | XX.X%          | XX.X%        |
  Agent / broker commission       | XX.X%          |              |
  Contingent commissions          |  X.X%          |              |
  Premium taxes / assessments     |  X.X%          |              |
Internal expense ratio            | XX.X%          | XX.X%        |
  Underwriting and servicing      |  X.X%          |              |
  Claims management (ULAE)        |  X.X%          |              |
  Technology and overhead         |  X.X%          |              |
───────────────────────────────────────────────────────────────────
Total expense ratio               | XX.X%          | XX.X%        |

Note: Express on a written-premium or earned-premium basis — state which.
      Be consistent between periods.
```

**Do:**
- Show the YOY movement for each component separately — a combined-ratio improvement in expense that comes entirely from a one-time commission reduction does not represent structural improvement.
- Compare acquisition cost ratio to broker/channel mix changes; rising commission ratios often track to a shift toward higher-commission distribution.
- Note whether any reinsurance cession commission is netting against the expense ratio — present gross and net separately if ceding commissions are material.

**Don't:**
- Report a single expense ratio without the two-component split — it is insufficient for management decision-making.
- Use industry benchmarks for the total expense ratio without checking whether the comparator has the same distribution model (direct writer vs. independent agent vs. MGA all have structurally different acquisition cost ratios).
- Allow the internal expense ratio to grow while the acquisition cost ratio falls — the internal cost trend is a structural margin story, and it compounds.

## Edge cases / when the rule does NOT apply

- **Very early-stage carriers** with insufficient premium volume to load internal expenses meaningfully against earned premium — the ratio will be distorted by the denominator; disclose the premium volume and note the distortion.
- **Pure MGAs** with no underwriting balance sheet — the relevant "expense" metrics are the MGA's operating overhead as a percentage of GWP, not a P&C combined-ratio expense presentation.

## See also

- [`../agents/actuarial-pricing-analyst.md`](../agents/actuarial-pricing-analyst.md) — owns the combined-ratio decomposition analysis.
- [`./the-combined-ratio-is-loss-plus-expense-read-both.md`](./the-combined-ratio-is-loss-plus-expense-read-both.md) — the upstream house opinion that establishes the loss/expense separation; this doc drills into the expense component's internal structure.

## Provenance

Codifies the actuarial-pricing-analyst's expense decomposition discipline from the insurance-pc plugin's CLAUDE.md §3 #1 (combined ratio is loss plus expense — read both). The acquisition cost vs. internal expense split reflects standard P&C carrier management reporting practice (NAIC Annual Statement schedule, ISO expense exhibit conventions).

---

_Last reviewed: 2026-06-05 by `claude`_
