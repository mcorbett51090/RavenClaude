# Bonus Depreciation and ITC Interact — Model the Tax Basis Explicitly

**Status:** Absolute rule
**Domain:** Project finance / tax structuring
**Applies to:** `renewable-energy`

---

## Why this exists

The Investment Tax Credit (ITC) and bonus depreciation (MACRS 5-year accelerated depreciation) interact in a way that consistently trips up project pro-formas built by non-tax-specialist modelers. The ITC reduces the depreciable tax basis: a project taking the full 30% ITC must reduce the depreciable basis by 50% of the credit (to 85% of cost basis) for MACRS calculation. A model that applies both the full ITC and full bonus depreciation on the same basis is overstating the tax benefit by ~4–5% of project cost [unverified — ESTIMATE]. In a $5M project, that is a $200,000–$250,000 pro-forma overstatement that will not survive tax equity due diligence.

## How to apply

Build the tax basis reduction explicitly in every pro-forma:

```
ITC and depreciation basis model:
  Project cost basis:                                        $______
  ITC rate (30% under 48E through 2033 [unverified]):        ______%
  ITC amount:                                                $______

  Depreciable basis reduction (IRS basis adjustment):
    Depreciable basis = project cost − (50% × ITC amount)
    Example: $5M project, 30% ITC → $5M − ($750K × 50%) = $5M − $375K = $4.625M

  Depreciation schedule (MACRS 5-year):
    Year 1 (with bonus depreciation):   ____% of $4.625M = $______
    Year 2:                             ____% × $4.625M = $______
    (Use current-year MACRS table — bonus depreciation phase-out affects year 1 rate)

  Tax benefit summary:
    ITC credit:                          $______
    PV of depreciation tax shield:       $______ (at marginal tax rate × PV of deductions)
    Total tax benefit:                   $______
    Effective net cost:                  project cost − total tax benefit = $______
```

**Do:**
- Always reduce the depreciable basis by 50% of the ITC before running MACRS; the IRS requirement is not optional.
- Confirm the current bonus depreciation percentage for the placed-in-service year — bonus depreciation has been phasing down (80% in 2023, 60% in 2024, 40% in 2025 [unverified — training knowledge]).
- Have a CPA or tax advisor review the tax benefit model before presenting to investors or tax equity partners.

**Don't:**
- Apply MACRS depreciation on the full project cost without the basis reduction — the model will overstate tax equity value and fail due diligence.
- Assume bonus depreciation rates from prior years apply to the current placed-in-service year; the phase-down schedule changes annually.

## Edge cases / when the rule does NOT apply

Non-profit or governmental entities using direct pay (elective payment) under IRA provisions may have a different tax basis treatment; consult a tax advisor for the specific pathway. Projects using the Production Tax Credit (PTC) instead of ITC have a different but equally complex interaction with depreciation; the same discipline of explicit tax basis modeling applies.

## See also

- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — owns the pro-forma tax benefit model and ITC/depreciation interaction.
- [`../agents/renewables-engagement-lead.md`](../agents/renewables-engagement-lead.md) — flags tax structuring as a gating question during the engagement scoping.
- [`./the-incentive-structure-changed-in-2025-design-to-the-live-p.md`](./the-incentive-structure-changed-in-2025-design-to-the-live-p.md) — the incentive landscape that determines the ITC rate feeding this model.

## Provenance

ITC basis adjustment is defined in IRC § 50(c); MACRS 5-year depreciation for solar is defined in IRC § 168. The interaction is covered in IRS Publication 946, SEIA tax equity guidance, and project finance legal practice. All rate figures marked `[unverified — training knowledge]`.

---

_Last reviewed: 2026-06-05 by `claude`_
