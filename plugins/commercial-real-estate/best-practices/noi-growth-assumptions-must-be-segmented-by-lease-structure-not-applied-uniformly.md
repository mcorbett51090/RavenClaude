# NOI Growth Assumptions Must Be Segmented by Lease Structure, Not Applied Uniformly

**Status:** Absolute rule
**Domain:** Commercial real estate / underwriting
**Applies to:** `commercial-real-estate`

---

## Why this exists

A common underwriting error is applying a single "NOI growth rate" — say 3%/year — uniformly across a property's income without accounting for the contractual constraints that govern how and when each income component can actually grow. A gross lease with a 5-year term and no rent bumps cannot grow until renewal; a NNN lease with annual 2% rent bumps grows exactly 2%, not 3%; a multi-tenant office building with staggered expirations has a lumpy NOI profile, not a smooth compounding curve; a vacancy recovery scenario has NOI growing at 20–30% in the absorption years, not 3%. Applying a single escalation rate to all of these is a modeling error that overstates or understates returns depending on the lease structure, and it masks the lease-rollover risk that is often the dominant hold-period uncertainty.

## How to apply

Build NOI growth from the lease schedule up, not from a top-down escalation rate:

```
NOI Growth Build — [Asset] [Hold Period Start: ___] [End: ___]
──────────────────────────────────────────────────────────────
Revenue components:

1. In-place leases (contractual)
   Tenant          │ Sq ft │ Current rent │ Annual bump │ Expiry │ Notes
   ────────────────┼───────┼──────────────┼─────────────┼────────┼──────
   [Tenant A]      │       │ $___/sf       │ ___% CPI    │        │ renewal option at $___
   [Tenant B]      │       │ $___/sf       │ Fixed $___  │        │ no renewal right
   [Vacant]        │       │ $0            │ N/A         │        │ lease-up assumed: [mo]

2. Lease rollover assumptions (spaces expiring during hold)
   Expiry date  │ Sq ft │ Downtime (mo) │ New rent (vs. current) │ TI/LC cost
   ─────────────┼───────┼───────────────┼────────────────────────┼──────────
                │       │               │ [market rent comp: $___ │
                │       │               │  source + date: ___]    │

3. Vacancy and credit loss
   Year 1: ___% of gross potential rent
   Years 2–5: ___% (trend: [ ] declining lease-up  [ ] stable  [ ] increasing risk)

4. Expense growth (by category)
   Taxes:        ___% (reassessment risk at: [sale price threshold])
   Insurance:    ___% (source: [trailing 3-yr actual or quote])
   Management:   ___% of EGR (fixed rate per management contract)
   Utilities:    ___% (or pass-through: % of gross)
   Repairs/Capex reserve: $___/sf/year (source: ___)

NOI projection:
   Year │ Gross rent │ Vacancy/CL │ Net rent │ OpEx │ NOI │ NOI growth vs. prior yr
   ─────┼────────────┼────────────┼──────────┼──────┼─────┼────────────────────────
     1  │            │            │          │      │     │ —
     2  │            │            │          │      │     │
     3  │            │            │          │      │     │
```

**Warning flags in the NOI model:**

| Flag | What it signals |
|---|---|
| Uniform rent escalation applied to all tenants | Lease schedule not read; rollover risk hidden |
| NOI grows smoothly at 3%/year every year | Lease-rollover timing not modeled |
| Vacancy held constant over the hold | Lease expiration pipeline ignored |
| Expense growth = revenue growth | Recovery ratio changes not modeled |
| No TI/LC reserve line against lease expirations | Leasing cost excluded from NOI |

**Do:**
- Read every lease before building the model — rent bumps, renewal options, termination rights, and expense stops all affect NOI growth.
- Model the lease-rollover timeline explicitly in the NOI build; the years when large tenants expire are the years when NOI is most uncertain.
- Sensitize the model around the renewal vs. vacancy scenario for the largest lease expiration in the hold period — that single lease event often has more impact on IRR than any other assumption.
- Source market rents for rollover assumptions from recent comps (net effective, not face rent) with retrieval dates.

**Don't:**
- Apply CPI or a fixed escalation to gross lease spaces that have no contractual rent bumps — they grow only at renewal.
- Exclude TI and leasing commission costs from the NOI or CapEx line — they are cash costs in the hold period and reduce levered returns.
- Present a "stabilized NOI" figure without specifying the year in which stabilization is achieved and the vacancy and rent assumptions that define it.

## Edge cases / when the rule does NOT apply

Single-tenant NNN assets with long-remaining lease terms (10+ years, no rollover in the hold period) may reasonably use the contractual rent-bump schedule as the entire NOI model — lease-rollover is not an in-hold risk. Ground-lease structures where land and improvements are separately owned require a specific NOI attribution methodology that differs from standard building-level underwriting.

## See also
- [`../agents/acquisitions-underwriter.md`](../agents/acquisitions-underwriter.md) — builds the lease-schedule-up NOI model.
- [`../agents/asset-property-manager.md`](../agents/asset-property-manager.md) — manages the lease-rollover execution in the hold period.
- [`../knowledge/cre-underwriting-economics.md`](../knowledge/cre-underwriting-economics.md) — covers NOI build-up, lease economics, and TI/LC modeling.

## Provenance

Codifies standard commercial real estate underwriting practice; the lease-up NOI build from contractual schedule is the method required in institutional CRE underwriting (NCREIF, PERE standards) and commercial mortgage underwriting (CREFC standards) [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
