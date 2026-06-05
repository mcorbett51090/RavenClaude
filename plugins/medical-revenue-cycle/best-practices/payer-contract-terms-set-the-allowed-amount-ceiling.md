# Payer Contract Terms Set the Allowed-Amount Ceiling

**Status:** Absolute rule
**Domain:** Payer contracting / revenue integrity
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

Net collection rate is bounded by the payer's contracted allowed amount — the ceiling above which no billing effort will collect more. A practice that focuses on denial management and A/R collections without periodically reviewing its contracted rates is optimizing the collection of a shrinking allowed amount. Payer contracts typically include annual fee schedule updates (or the absence of them — fee schedules that are frozen while costs rise are an implicit rate cut). Most practices cannot recall the exact fee schedules for their top 5 payers and have never modeled whether their contracted rates cover their cost of service. The contract is the upstream variable that governs everything downstream in the revenue cycle.

## How to apply

Treat payer contract review as an annual revenue-cycle governance event.

```
Annual payer contract review:
1. Inventory all active payer contracts:
   - Payer name, contract effective date, fee schedule anchor (% of Medicare, % of billed charges, 
     or absolute fee table)
   - Contract termination notice period (important for timely re-negotiation)

2. Rate adequacy analysis (top 10 payers by revenue volume):
   - Pull: contracted allowed amount for top 20 CPT codes by volume
   - Compare to: current Medicare rates for same codes (useful benchmark)
   - Compare to: practice's cost per RVU (if available)
   - Flag: any code where the allowed amount is below the cost of service

3. Rate trend analysis:
   - Has the contracted rate increased YoY?
   - If the contract has a "lesser of billed charges or contracted rate" clause:
     are billed charges above the contracted rate? (if not, you may be self-limiting the allowed amount)

4. Re-negotiation opportunity:
   - Contracts with no rate increase in 2+ years → re-negotiate or put on the watch list
   - Payer contracts approaching their anniversary → 90-day notice window is the opening

5. Termination analysis:
   - For bottom-tier payers (lowest allowed amounts, highest administrative burden):
     model patient volume impact of termination vs. margin improvement from dropping
```

**Do:**
- Know your top-5 payer contracts' fee schedules by memory or have them in a single accessible reference.
- Request itemized fee schedules from payers at each contract renewal — summary-level allowable quotes are not specific enough for code-level analysis.
- Use Medicare rates as a reference benchmark but not as a target — commercial rates should exceed Medicare for most services.

**Don't:**
- Allow contracts to auto-renew without a rate review — auto-renewal at unchanged rates is an implicit rate cut in an inflationary environment.
- Negotiate contract rates without data; the negotiation position must be grounded in cost-of-service or market rate data, not "we want more."
- Confuse payer-fee-schedule review with claims-level adjudication review — they are different activities with different owners.

## Edge cases / when the rule does NOT apply

Medicare fee-for-service rates are set by CMS annually and are not negotiable. The analysis still applies — understanding the Medicare rate level and trend informs the position on commercial contracts and Medicare Advantage negotiations.

## See also

- [`../agents/rcm-engagement-lead.md`](../agents/rcm-engagement-lead.md) — payer contract strategy is an engagement-level question that frames the entire RCM analysis.
- [`./net-collection-rate-not-gross-measures-the-cycle.md`](./net-collection-rate-not-gross-measures-the-cycle.md) — the allowed amount set by contract is the denominator in net collection rate.

## Provenance

Standard RCM payer contracting and revenue integrity practice; grounded in HFMA and MGMA payer contracting best practices; the contract-as-ceiling framing reflects fundamental RCM economics that every revenue-cycle leader should own.

---

_Last reviewed: 2026-06-05 by `claude`_
