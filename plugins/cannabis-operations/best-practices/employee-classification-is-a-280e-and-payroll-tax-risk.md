# Classify cannabis workers correctly — misclassification amplifies 280E exposure

**Status:** Absolute rule
**Domain:** Cannabis operations / HR / 280E / payroll tax
**Applies to:** `cannabis-operations`

---

## Why this exists

Under 280E, only labor allocated to COGS-eligible activities (cultivation, manufacturing, and the direct cost of goods for a reseller) reduces taxable income. Misclassifying a retail or administrative employee as a production worker inflates COGS fraudulently; misclassifying a production worker as an independent contractor loses the COGS allocation entirely (contractor cost is a disallowed business expense, not production COGS). Either error is compounded when the misclassification also triggers IRS payroll-tax penalties and state labor claims, which themselves are non-deductible under 280E.

## How to apply

Maintain a labor classification matrix, updated when any role changes:

```
Labor classification matrix — [entity] — [state] — updated [date]

Role title        | Classification | Activity bucket      | COGS-eligible? | Basis
----------------- | -------------- | -------------------- | -------------- | -----
Master grower     | W-2 employee   | Production (§471)    | Yes            | Direct labor
Trim technician   | W-2 employee   | Production (§471)    | Yes            | Direct labor
Budtender         | W-2 employee   | Retail operations    | No (§280E)     | Selling
Store manager     | W-2 employee   | G&A                  | No (§280E)     | Admin
Extraction tech   | W-2 employee   | Manufacturing (§471) | Yes            | Direct labor
Delivery driver   | [W-2 or 1099?] | Distribution         | Partial — see note
```

For each role, apply the IRS ABC/common-law test (behavioral control, financial control, relationship type) before assigning 1099. Document the basis in the HR file and review annually.

**Do:**
- Default to W-2 for any worker with regular hours, employer-supplied tools, or supervisory direction — the IRS test is not optional.
- Distinguish production roles (COGS-eligible labor) from retail/admin roles (280E-disallowed) in the payroll system at the cost-center level; the split drives the COGS allocation.
- Route any role that straddles production and retail (e.g., a cultivation manager who also handles some retail) to the cannabis CPA for an explicit allocation percentage.

**Don't:**
- Use contractor status to avoid payroll taxes on workers who meet W-2 criteria — the IRS cannabis enforcement unit scrutinizes this pattern.
- Blend production and non-production labor into a single cost center; the COGS allocation collapses if it cannot be traced to a role.
- Treat the COGS labor split as a year-end tax exercise; it must be live in the payroll system to be defensible.

## Edge cases / when the rule does NOT apply

- Genuine project-based contractors (e.g., a licensed electrician doing a one-time installation) are properly 1099 and their cost may be capitalized, not expensed — a different classification, not an exception to the rule.
- Owner-operators who draw distributions rather than wages create their own 280E allocation question; route to a cannabis CPA, not this rule.

## See also

- [`../agents/cannabis-finance-analyst.md`](../agents/cannabis-finance-analyst.md) — builds the payroll cost-center split supporting the COGS allocation.
- [`./280e-makes-cogs-allocation-existential-not-academic.md`](./280e-makes-cogs-allocation-existential-not-academic.md) — labor classification feeds the COGS allocation directly.
- [`./harvest-batch-cost-accounting-drives-cogs-defensibility.md`](./harvest-batch-cost-accounting-drives-cogs-defensibility.md) — the harvest batch cost record includes the direct labor line this matrix classifies.

## Provenance

Derived from IRS 280E enforcement practice, worker-classification doctrine, and cannabis payroll tax guidance. `[unverified — training knowledge]` — validate the classification matrix with a licensed cannabis CPA and employment attorney before use.

---

_Last reviewed: 2026-06-05 by `claude`_
