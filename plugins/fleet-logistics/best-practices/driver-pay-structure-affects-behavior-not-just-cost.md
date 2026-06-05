# Driver Pay Structure Affects Behavior, Not Just Cost

**Status:** Pattern
**Domain:** Driver economics / retention
**Applies to:** `fleet-logistics`

---

## Why this exists

Most carriers analyze driver pay as a line item in CPM. That misses the behavioral signal: pay structure — cents-per-mile, percentage-of-load, hourly, or salary — directly shapes the choices drivers make about speed, detention acceptance, and load selection. A CPM-paid driver has an incentive to maximize miles, which can mean speeding or rejecting high-dwell loads. A percentage-of-load driver cares about rate, which can mean cherry-picking. Retention economics collapse when pay structure and operational goals are misaligned, and modeling the cost without modeling the behavior produces a wrong answer.

## How to apply

Before recommending a pay change, map pay structure to the operational behaviors you want:

| Goal | Pay structure that incentivizes it |
|---|---|
| Maximize loaded miles | Cents-per-loaded-mile (with dwell penalty or detention pay) |
| Maximize revenue yield | Percentage-of-revenue (works for owner-operators; aligns on rate) |
| Predictable cost + retention | Hourly or mileage-plus-hourly hybrid |
| Dedicated routes | Day rate or weekly guarantee |

Diagnostic checklist when turnover spikes:
1. Is the pay structure penalizing the driver for factors outside their control (detention, weather, shipper delays)?
2. Is the total package — base pay + benefits + home time — competitive vs. regional peers?
3. Is there a mismatch between pay structure and the lanes/work the driver is actually assigned?

**Do:**
- Model the driver's effective hourly rate (total gross pay ÷ total hours on duty, including detention) when benchmarking competitiveness — not just the cents-per-mile posted rate.
- Include detention pay and layover pay in the total CPM model; they are part of the cost of holding a driver through a high-dwell operation.
- Flag pay-structure mismatches when analyzing turnover: a mile-paid driver on a high-dwell lane is a predictable attrition risk.

**Don't:**
- Cut pay rates in isolation as a CPM fix without modeling the retention cost of the resulting turnover.
- Assume that paying above-market rate alone solves retention — home time, equipment quality, and dispatch respect are co-equal factors.

## Edge cases / when the rule does NOT apply

Owner-operators on percentage-of-load arrangements are essentially small businesses; behavioral alignment works differently when the driver owns the truck and chooses loads. For owner-operators, the analysis is load economics, not pay structure.

## See also

- [`../agents/fleet-engagement-lead.md`](../agents/fleet-engagement-lead.md) — scopes pay/retention as part of the engagement read.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — models driver effective hourly rate and total retention cost.
- [`./driver-turnover-is-a-unit-economics-problem-not-hr-overhead.md`](./driver-turnover-is-a-unit-economics-problem-not-hr-overhead.md) — the parent rule; this doc operationalizes the pay-structure dimension.

## Provenance

Synthesized from industry practice and ATRI Driver Compensation Studies; behavioral pay-structure analysis is standard in fleet HR consulting and large-carrier operations research.

---

_Last reviewed: 2026-06-05 by `claude`_
