# Submarket Fundamentals Must Precede Property Underwriting

**Status:** Pattern
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

A property underwritten in isolation from its submarket can look attractive on a trailing-12 in-place-income basis while sitting in a fundamentally weakening market. The submarket read — vacancy trend, net absorption, competitive supply pipeline, and rent growth direction — is the context that determines whether in-place income is defensible, growing, or about to be competed away. Underwriting without submarket context mistakes current income for future income.

## How to apply

Conduct a submarket fundamentals review before the first pass of the property-level model:

```
Submarket Fundamentals Brief — [Market] / [Submarket]
───────────────────────────────────────────────────────
Property type:  ________________
Market / submarket:  ________________
Data source + date:  ________________

Vacancy:
  Submarket overall:    ___%  (trailing direction: ▲ / ▼ / stable)
  Asset tier (Class A/B/C):  ___%
  Tenant tier (credit/non-credit):  per analysis

Net absorption (trailing 4 quarters):  _____ sf (positive / negative)
  YTD vs. prior year:  _____ sf vs. _____ sf

Rent trend:
  Asking rent (face):   $___/sf  (change: +/-___% YoY)
  Effective rent (est.): $___/sf

Supply pipeline (next 24 months):  _____ sf under construction / planned
  As % of existing submarket inventory:  ___%
  Notable deliveries that compete directly with this asset:  ________________

Demand drivers:
  Top employment sectors in submarket:  ________________
  Notable move-ins / expansions / move-outs:  ________________

Summary:  [ ] Strengthening  [ ] Stable  [ ] Weakening  [ ] Cyclically peaked
Underwriting implication:
  Rent growth assumption supported by data?  [ ] Yes  [ ] No — cap at ___% or flat
  Vacancy assumption realistic vs. submarket trend?  [ ] Yes  [ ] Revise to ___%
```

**Do:**
- Complete the submarket brief before building the property model; update the model assumptions to reflect the submarket read.
- Source every data point with a broker report, CBRE/JLL/CoStar data, or a named primary source with a date — submarket data ages in 90–180 days.
- Flag any case where the property-level assumption for vacancy or rent growth is more optimistic than the submarket trend.

**Don't:**
- Use MSA-level vacancy figures as a proxy for submarket — submarket vacancy can diverge materially from the metro average.
- Skip the supply pipeline analysis; competitive deliveries 12–24 months out are the most common reason rent growth assumptions fail.
- Treat the submarket brief as a single static document; refresh it for IC review if more than 90 days have elapsed since the initial analysis.

## Edge cases / when the rule does NOT apply

Sale-leaseback transactions where the tenant is creditworthy and the lease extends well beyond the hold period with no submarket re-leasing risk may de-weight the submarket analysis in favor of credit analysis. The submarket brief still runs; its weight in the IC memo is lower.

## See also

- [`../agents/cre-market-analyst.md`](../agents/cre-market-analyst.md) — owns the submarket fundamentals brief.
- [`./vacancy-is-bifurcated-never-quote-it-without-the-tier.md`](./vacancy-is-bifurcated-never-quote-it-without-the-tier.md) — the companion rule on reporting vacancy with asset-tier context.

## Provenance

Codifies CLAUDE.md §3 #4 (vacancy is bifurcated) and §3 #8 (cite source and date) applied to the submarket analysis workflow. Submarket-before-property sequencing is standard institutional due diligence practice [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
