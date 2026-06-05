# Fuel Surcharge Recovery Is a Contract Clause, Not a Market Wish

**Status:** Absolute rule
**Domain:** Fuel management / contract economics
**Applies to:** `fleet-logistics`

---

## Why this exists

Carriers frequently assume that rising diesel prices will be absorbed by shippers through a fuel surcharge. They are wrong unless the contract says so explicitly. Fuel surcharge (FSC) recovery depends entirely on whether the carrier has a contractual FSC schedule tied to a published index (DOE national average, OPIS regional), what the trigger price is, and what the per-mile rate table looks like. A carrier with no FSC clause is absorbing 100% of diesel price movement. A carrier with a weak schedule (wide bands, lagging trigger) may recover only 40–60% of actual fuel cost increases. Treating FSC as a market expectation rather than a contract deliverable is a margin leak that compounds every quarter.

## How to apply

Audit every contract for FSC terms before fuel exposure becomes a problem:

```
FSC contract audit checklist:
1. Does the contract include an FSC clause? (yes / no — if no, it must be added at renewal)
2. What index does it reference? (DOE national, OPIS regional, other)
3. What is the base/trigger price? (the price at which FSC starts — lower is better for carrier)
4. What is the per-mile rate per $0.01 increment above trigger?
5. Is there a cap on FSC (a ceiling that limits recovery)? (any cap > $0.50 above trigger is risky)
6. What is the update frequency? (weekly, monthly — weekly better matches actual diesel cost)

Recovery test:
  Actual diesel cost increase per mile vs. FSC recovered per mile
  Gap = unrecovered fuel exposure
```

For spot freight: price the FSC explicitly in the all-in rate using the current DOE average, or the load is priced at yesterday's cost.

**Do:**
- Negotiate FSC clauses at the same time as the rate, not as an afterthought — retroactive FSC additions are hard.
- Use a weekly-updating DOE national average index; monthly updates create a one-month lag in recovery during fast-moving markets.
- Verify FSC recovery monthly: pull invoiced FSC vs. actual fuel cost and report the gap.

**Don't:**
- Assume that a standard carrier agreement automatically includes a market-standard FSC — many shipper templates do not.
- Accept a fixed fuel surcharge (e.g., "$0.10/mile regardless of diesel price") — it protects neither party and becomes wrong immediately when the market moves.

## Edge cases / when the rule does NOT apply

All-inclusive spot rates quoted on a load board already embed the FSC in the per-mile rate — there is no separate clause to audit. For owner-operators on percentage-of-revenue arrangements, the FSC flows through the percentage; the analysis shifts to whether the rate itself is adequate.

## See also

- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the FSC recovery audit and gap calculation.
- [`../agents/fleet-engagement-lead.md`](../agents/fleet-engagement-lead.md) — flags FSC gaps during the engagement scoping read.
- [`./fuel-is-the-swing-variable-manage-it-dont-just-absorb-it.md`](./fuel-is-the-swing-variable-manage-it-dont-just-absorb-it.md) — FSC recovery is the contract side of managing fuel exposure; that rule covers the operational side.

## Provenance

Standard carrier contract management practice; FSC clause structuring is covered in the American Trucking Associations' carrier contracting guidance and is a primary topic in freight contract negotiations.

---

_Last reviewed: 2026-06-05 by `claude`_
