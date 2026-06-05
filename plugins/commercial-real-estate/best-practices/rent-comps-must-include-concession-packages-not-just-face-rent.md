# Rent Comps Must Include Concession Packages, Not Just Face Rent

**Status:** Absolute rule
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

In a market where landlords are competing for tenants, concession packages — TI allowances, free rent, moving allowances, lease-buyout contributions — can represent 2–4 years of effective rent erosion on a 10-year lease. A rent comp quoted at "$42/sf asking" for a comparable building may be transacting at $34/sf NER once the market concession package is normalized. Using face-rent comps to support an underwriting model without deducting current market concessions overstates the achievable rent, overstates the income, and overprices the asset.

## How to apply

Every rent comp must include the concession package alongside the face rent:

```
Rent Comp Template — [Property Name] Analysis
───────────────────────────────────────────────
Date:  ________________   Source:  ________________

Comparable:         ________________
Market / submarket: ________________
Transaction date:   ________________

Face rent:          $___/sf ([ ] gross  [ ] NNN  [ ] MG)
Lease term:         ___ years
Rentable SF:        ___

Concession package:
  TI allowance:       $___/sf
  Free rent:          ___ months  (value: $___/sf)
  Other concessions:  ________________ (value: $___/sf)
  Total concession value:  $___/sf

NER calculation:
  Face rent (PV of lease payments):  $___/sf
  Less: TI amortized over term:      ($___/sf)
  Less: free rent amortized:         ($___/sf)
  Less: other concessions:           ($___/sf)
  Net effective rent (NER):          $___/sf  ← use this for underwriting

Market concession trend:
  TI/sf trend:  ▲ rising / ▼ declining / stable  [source + date]
  Free rent trend:  months trending ▲ / ▼ / stable
```

**Do:**
- Collect concession packages on every comp — a comp without concession data is incomplete; note it as "concessions unknown" and apply a market-standard concession estimate with a source.
- Track concession trends separately from asking-rent trends; in a softening market, concessions rise before face rent falls.
- Use NER for all underwriting comparisons — face rent is a marketing figure; NER is the economic figure.

**Don't:**
- Quote a comp at face rent in the IC memo without the NER calculation — a committee member who knows the market will immediately ask for the NER.
- Average face rents from comps that span materially different concession environments — a 2022 comp and a 2025 comp may have the same face rent but vastly different NERs.
- Omit TI amortization from the NER calculation — TI is the largest single component of the NER-to-face-rent gap in most office and retail markets.

## Edge cases / when the rule does NOT apply

Industrial and self-storage markets often transact with minimal concession packages; confirm by market before applying an office-rate TI assumption. Where market concessions are negligible, face rent and NER converge and the NER calculation is a brief confirmation step, not a material adjustment.

## See also

- [`../agents/cre-market-analyst.md`](../agents/cre-market-analyst.md) — owns rent comp sourcing and concession package analysis.
- [`./net-effective-rent-is-the-real-number-not-face-rent.md`](./net-effective-rent-is-the-real-number-not-face-rent.md) — the governing rule on NER as the economic standard.

## Provenance

Codifies CLAUDE.md §3 #5 (net effective rent is the real number, not face rent) with a specific comp-collection instrument. Concession-adjusted NER is the standard underwriting metric in office and retail acquisitions; its omission is a well-documented source of acquisition pricing errors [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
