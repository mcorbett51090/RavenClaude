# Offtake Structure Determines Financing Eligibility Before the Pro-Forma

**Status:** Absolute rule
**Domain:** Project finance / development
**Applies to:** `renewable-energy`

---

## Why this exists

A solar project's pro-forma is built on an assumed revenue stream. The revenue stream depends entirely on the offtake structure — PPA, merchant, net metering, FiT, SREC — and each structure has different financeability, risk profile, and lender appetite. A project modeled as a 20-year fixed-price PPA with an investment-grade counterparty can support non-recourse project financing. The same project selling merchant power into an ISO market cannot. Running a detailed financial model before locking the offtake structure wastes time and produces numbers that will not survive due diligence. The offtake decision gates the entire pro-forma architecture.

## How to apply

Build the offtake decision framework before starting the pro-forma:

```
Offtake structure evaluation (per project):
  Segment:
    Residential:     net metering (where available) or PPA/lease under 48E
    C&I:             direct PPA with host, net metering, or utility PPA
    Utility-scale:   long-term PPA (utility or C&I offtaker) or merchant with hedge
    Community solar: subscription-based; check state program rules for capacity and term limits
    Storage:         capacity market, demand charge, arbitrage, or paired with solar PPA

  Financeability test (by structure):
    20-yr fixed-price PPA, IG counterparty:   bankable (preferred by project lenders)
    10-yr PPA, BB counterparty:              conditionally bankable (requires credit support)
    Net metering only:                        bankable for residential; state policy risk
    Merchant:                                may require hedge; lenders require P90 coverage ratio
    SREC/REC revenue:                        not bankable as primary revenue; treated as upside

  Required offtake document milestones before pro-forma:
    [ ] Letter of Intent (LOI) or term sheet from offtaker
    [ ] Credit check on counterparty
    [ ] Confirm offtake term is ≥ debt tenor + 2 years
```

**Do:**
- Identify the likely offtake structure and counterparty credit quality before building any financial model.
- For C&I projects, confirm that the host's electricity load is sufficient to absorb the system's production year-round before sizing to net metering limits.
- For utility-scale, check whether the ISO or utility has a solicitation open or whether the PPA must be bilateral; the path determines timeline.

**Don't:**
- Build a financial model assuming a 20-year PPA before the offtaker has signed even a term sheet — the model will be rebuilt when the structure changes.
- Count SREC or carbon credit revenue as bankable primary revenue in the base case; treat it as optionality.

## Edge cases / when the rule does NOT apply

Fully self-funded projects (developer equity only, no debt) can use merchant revenue without the financeability test — but the risk profile of the investment must still reflect the revenue uncertainty. Behind-the-meter C&I with 100% self-consumption and no export have a unique structure where the "offtake" is the host's own load; the analysis shifts to the host's credit and lease term.

## See also

- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — owns the pro-forma architecture and revenue modeling by offtake structure.
- [`../agents/renewables-engagement-lead.md`](../agents/renewables-engagement-lead.md) — frames the offtake decision during the engagement scoping.
- [`./lcoe-and-project-irr-are-different-questions-show-both.md`](./lcoe-and-project-irr-are-different-questions-show-both.md) — the revenue assumption from the offtake structure feeds both the LCOE and the IRR; offtake gates both.

## Provenance

Offtake structure and financeability is a foundational topic in project finance for renewable energy; the bankability of PPA vs. merchant structures is covered in SEIA financing guides and project-finance legal and banking practice.

---

_Last reviewed: 2026-06-05 by `claude`_
