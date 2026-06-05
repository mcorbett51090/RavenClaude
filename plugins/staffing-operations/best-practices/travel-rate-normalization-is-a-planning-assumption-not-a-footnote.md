# Travel-Rate Normalization Is a Planning Assumption, Not a Footnote

**Status:** Pattern
**Domain:** Staffing operations — Healthcare-travel segment; forecasting
**Applies to:** `staffing-operations`

---

## Why this exists

The 2021–2022 travel-nurse crisis produced contract bill rates that ran 2–3× pre-pandemic norms. Firms that built revenue models, headcount plans, or growth projections on crisis-era rates experienced sharp corrections when rates normalized in 2023–2024. The cautionary lesson — which the team's knowledge bank encodes — is that **peak crisis rates are not a sustainable baseline for a travel-staffing model**. As of mid-2026, rates have returned closer to pre-pandemic trends, but with permanent structural shifts (floor is higher than 2019, spread compression from hospital negotiating leverage, MSP consolidation). The risk is now symmetric: a model built on 2021 peak rates overstates economics, and a model that extrapolates 2024 correction to further decline may understate a recovering market. Every travel-segment forecast must state its rate assumption explicitly and source it.

## How to apply

**Rate assumption disclosure (required in every travel-segment deliverable):**

```
Travel-segment rate assumption:
  - Bill rate range used: $[X]–$[Y]/week ([specialty], [geography])
  - Source: [internal recent placements / SIA Travel Nurse benchmark / AMN bill-rate report]
  - Retrieval date: [YYYY-MM-DD]
  - Normalization assumption: [post-correction baseline / recovering toward $Z by Q[X] YYYY /
    scenario range]
  - Spread assumed: $[X]/week (bill minus total pay package + burden)
```

**Scenario planning structure for travel-rate uncertainty:**

| Scenario | Bill rate assumption | Spread | Implied margin | Notes |
|---|---|---|---|---|
| Conservative | $[X]/week — floor (2024 trough) | $[X] | [Y%] | Use for downside cash planning |
| Base | $[X]/week — current market | $[X] | [Y%] | Use for operating plan |
| Recovery | $[X]/week — partial rebound | $[X] | [Y%] | Use for upside / volume scenarios |
| **Do NOT use** | 2021 crisis peak | — | — | Not a sustainable planning baseline |

**Spread compression check:**

Post-normalization, hospital systems and MSPs have captured more of the spread reduction at the bill rate line (lower bill rates) rather than passing the reduction through to traveler pay packages equally. This means spread (gross profit per traveler) compressed more than gross bill rate declined. Always decompose:

```
Spread = Bill rate − (Base pay + Housing stipend + M&IE stipend +
          Benefits + FICA/payroll taxes + Workers' comp + Malpractice + Travel)
```

If a colleague or client says "margins are back to normal because rates are back to normal," challenge this with the spread, not just the bill rate.

**Do:**
- Source every travel-rate figure used in a deliverable (SIA, AMN rate index, internal placements — cite the source and date).
- Distinguish between rate normalization (rates are lower than the peak) and rate recovery (rates are rising from the trough) — these are different phases with different planning implications.
- Model spread, not just bill rate, when assessing travel-segment margin; the burden stack (housing, benefits, compliance) is relatively sticky even as bill rates move.

**Don't:**
- Use 2021–2022 crisis-era rates as a "typical" travel baseline in any forward projection without explicitly flagging them as anomalous and unsustainable.
- State travel-rate trends without a date — the market has moved significantly over 18-month intervals; a stale benchmark misstates current economics.
- Conflate per-diem and travel-contract economics in the same rate line — their bill-rate structures, pay packages, and spreads are different products.

## Edge cases / when the rule does NOT apply

- **Locum tenens:** the rate normalization story applies differently — locum rates are driven by physician specialty supply constraints and are less correlated with the travel-nurse cycle. Analyze separately with specialty-specific data.
- **Allied health:** allied specialties (PT, OT, SLP, radiology) have their own supply and rate dynamics. Do not apply travel-nurse rate assumptions to allied positions without segment-specific sourcing.

## See also

- [`../agents/workforce-market-analyst.md`](../agents/workforce-market-analyst.md) — sources current rate benchmarks and tracks the normalization trend
- [`../agents/healthcare-staffing-specialist.md`](../agents/healthcare-staffing-specialist.md) — owns the bill/pay/spread mechanics for the travel segment
- [`../knowledge/healthcare-staffing-economics.md`](../knowledge/healthcare-staffing-economics.md) — the rate-cycle history and spread decomposition reference
- [`./decompose-margin-before-calling-it-pricing.md`](./decompose-margin-before-calling-it-pricing.md) — companion rule on margin decomposition

## Provenance

Codifies the post-2023 planning discipline for travel-healthcare staffing. The 2021–2022 rate spike and its 2023–2024 correction is the most significant recent event in healthcare staffing economics; its planning lesson is that anomalous-period rates are not a defensible baseline. Anchored in the team's knowledge bank `knowledge/healthcare-staffing-economics.md` and `knowledge/staffing-market-trends-2026.md`.

---

_Last reviewed: 2026-06-05 by `claude`_
