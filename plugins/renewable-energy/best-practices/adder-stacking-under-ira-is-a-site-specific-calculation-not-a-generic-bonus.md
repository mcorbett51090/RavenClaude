# Adder Stacking Under IRA Is a Site-Specific Calculation, Not a Generic Bonus

**Status:** Absolute rule
**Domain:** Incentive structuring / project finance
**Applies to:** `renewable-energy`

---

## Why this exists

The Inflation Reduction Act (IRA) introduced a base 30% ITC (48E, technology-neutral) plus a set of stackable adders — domestic content (10%), energy community (10%), and low-income/environmental justice bonus credits (10–20%). These adders are not automatic, and they are not universally available: domestic content requires specific component sourcing documentation; the energy community bonus requires that the site qualify under one of the statutory definitions (brownfield, coal mine/power plant closure zone, census tract with fossil fuel employment); the low-income adder requires IRS approval and specific project characteristics. A developer who models 30% + 10% + 10% = 50% ITC without verifying each adder's specific eligibility requirements is building a pro-forma on unverified assumptions that will not survive IRS review.

## How to apply

Build the adder eligibility checklist before including any adder in the base-case pro-forma:

```
IRA adder eligibility checklist (per project, as of 2026):
  Base ITC (48E, 30%):
  [ ] Placed in service before 2034 (base phase-out starts 2034 [unverified])
  [ ] Meets prevailing wage and apprenticeship requirements (systems >1 MW)

  Domestic Content Adder (10%):
  [ ] Steel and iron: 100% domestic manufacturing
  [ ] Manufactured products: 40% domestic content by cost (rising to 55% by 2026 [unverified])
  [ ] Documentation: procurement records + manufacturer attestation
  → Include in pro-forma: ONLY if procurement plan confirms sourcing can meet threshold

  Energy Community Adder (10%):
  [ ] Site within qualifying brownfield (EPA definition)?
  [ ] Site in census tract with ≥0.17% fossil fuel employment + adjacent qualifying tract?
  [ ] Site in census tract with coal mine or coal plant closure since 1999?
  → Include in pro-forma: ONLY after verifying site location against IRS/Treasury published maps

  Low-Income / Environmental Justice Adder (10–20%):
  [ ] Project qualifies as Low-Income Community (LIC) project (≤5 MW, IRS pre-approval)?
  [ ] Federally subsidized residential housing project?
  [ ] Low-income economic benefit project?
  → Include in pro-forma: ONLY after IRS capacity allocation received (limited annual capacity)
```

**Do:**
- Model three scenarios: base ITC only, base + confirmed adders, base + all potential adders — present the confirmed scenario as the base case.
- Use the IRS and Treasury published guidance (Notice 2023-29, Revenue Procedure 2023-27) and their updates — tax law interpretations move fast.
- Coordinate with a tax attorney or CPA on domestic content and energy community determinations; these are not self-certifying.

**Don't:**
- Include any adder in the base-case pro-forma without the specific eligibility documentation — a challenged ITC adder becomes a recapture risk.
- Assume that the energy community maps from 2023 are current — Treasury has updated them and will continue to update them.

## Edge cases / when the rule does NOT apply

Elective payment (direct pay) projects — government entities, tax-exempt organizations — receive the credit as a cash payment rather than a tax credit; the same adder eligibility rules apply, but the cash mechanics differ. PTC (48E production tax credit) projects use the same adder framework; the stacking discipline is identical.

## See also

- [`../agents/solar-project-developer.md`](../agents/solar-project-developer.md) — owns the adder eligibility screening and documentation requirements.
- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — models the confirmed vs. potential adder scenarios in the pro-forma.
- [`./the-incentive-structure-changed-in-2025-design-to-the-live-p.md`](./the-incentive-structure-changed-in-2025-design-to-the-live-p.md) — the parent rule on incentive-pathway design; adder stacking is the site-specific execution of that discipline.

## Provenance

IRA adder provisions are defined in IRC §48E and related Treasury guidance (IRS Notice 2023-29; Revenue Procedure 2023-27; Treasury proposed regulations); guidance is evolving and should be verified against current IRS publications before any project decision.

---

_Last reviewed: 2026-06-05 by `claude`_
