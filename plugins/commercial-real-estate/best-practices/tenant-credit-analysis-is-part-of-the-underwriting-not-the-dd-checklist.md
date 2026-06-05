# Tenant Credit Analysis Is Part of the Underwriting, Not the DD Checklist

**Status:** Pattern
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

A property whose income depends on one or two major tenants is a credit story as much as a real estate story. A credit-tenant building commands a different cap rate — and a different risk discount — than one with local, unrated, or financially stressed tenants. Leaving tenant credit analysis to the due-diligence checklist (post-LOI, post-PSA) rather than the underwriting model means the IC may approve a deal at a price that was set without pricing the credit risk. The right sequence is: credit assessment → cash-flow assumptions → valuation, not the other way around.

## How to apply

Complete a brief tenant credit assessment for every tenant representing more than 10% of GLA or rent before the initial underwriting pass:

```
Tenant Credit Assessment — [Property Name]
───────────────────────────────────────────
Tenant: ________________  SF: ___  % of GLA: ___  % of rent: ___
Lease expires: ________________  Option: ________________

Credit tier:
  [ ] Investment-grade / publicly rated (note rating: ___)
  [ ] Large private company (documented financials available)
  [ ] Small/local tenant (financial review limited)
  [ ] Financially stressed (note indicators: ___)

Credit indicators (use available sources):
  Revenue trend (if public):  ________________
  Industry health:  ________________
  Sector exposure (retail / office user / logistics / healthcare / gov):  ________________
  D&B or credit report available?  [ ] Yes  [ ] No

Underwriting adjustments based on credit tier:
  Renewal probability assumption:  ___%  (basis: ________________)
  Free-rent risk premium in NER calc:  [ ] Applied  [ ] Not applied
  Cap rate adjustment for credit risk:  [ ] Yes — ___ bps premium  [ ] No — investment-grade anchor

Summary:  [ ] Credit supports rent assumption  [ ] Credit is a downside risk — adjust underwriting
```

**Do:**
- Apply a higher re-leasing probability (lower renewal probability) for financially stressed or sector-at-risk tenants in the underwriting scenarios.
- Use tenant credit tier to calibrate the cap rate: a single-tenant property with a rated national tenant may trade at a tighter cap than one with a local operator of comparable in-place NOI.
- Re-assess credit between LOI and closing — a tenant in a deteriorating sector may change credit tier in the DD period.

**Don't:**
- Treat all tenants as equivalent credit in a multi-tenant building; a weighted-average credit score of the rent roll is more meaningful than a single building-level assessment.
- Assume a long remaining lease term compensates for weak credit — a 7-year lease with a tenant in bankruptcy is worth less than a 3-year lease with a strong national credit.
- Omit credit analysis for "small" tenants if they are anchors or if they represent more than 25% of rent.

## Edge cases / when the rule does NOT apply

Single-tenant credit properties where tenant credit is the stated investment thesis (e.g., a sale-leaseback with a publicly rated tenant) have the credit analysis as the primary underwriting document rather than an appendix.

## See also

- [`../agents/acquisitions-underwriter.md`](../agents/acquisitions-underwriter.md) — integrates tenant credit into the rent roll and NOI model.
- [`./lease-expiration-schedule-is-a-hold-period-risk-map.md`](./lease-expiration-schedule-is-a-hold-period-risk-map.md) — tenant credit risk is highest at lease expiration; these two tools run together.

## Provenance

Codifies CLAUDE.md §3 #1 (underwrite to in-place NOI) and §3 #4 (vacancy is bifurcated) applied to credit-driven re-leasing risk. Tenant credit assessment as part of acquisition underwriting is standard practice at institutional CRE investors and is a key determinant of cap rate pricing in single and multi-tenant net-lease markets [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
