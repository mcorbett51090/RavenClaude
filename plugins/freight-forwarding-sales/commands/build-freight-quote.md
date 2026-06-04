---
description: "Build an all-in, customer-ready freight quote — settle the chargeable basis and Incoterm scope first, stack every surcharge, show buy/sell/margin, set a validity date, and list exclusions. Never a bare base rate."
argument-hint: "[the shipment/lane, e.g. '1x40HC Shanghai->Rotterdam FCA, buy 1800, margin 12%']"
---

# Build a freight quote

You are running `/freight-forwarding-sales:build-freight-quote`. Build an all-in quote for what the user described (`$ARGUMENTS`), using this plugin's `freight-rate-quoter` discipline and the `freight-pricing-mechanics` + `incoterms-2020` skills.

## Steps
1. **Confirm scope first.** Identify mode (FCL/LCL/air/road), the Incoterm + named place, and therefore which charges are in-scope (whose quote is this). If the Incoterm is unstated, ask or assume-and-flag (default FCA for containers) — get this right before pricing.
2. **Settle the chargeable basis.** FCL = per container; LCL = per W/M (max of CBM vs tonnes); air = chargeable weight (volumetric vs actual, IATA /6000 unless a different divisor is given). Run `scripts/freight_calc.py air|ocean` to compute it — don't hand-math.
3. **Stack the surcharges.** Add every applicable line (BAF/LSS, CAF, OTHC/DTHC as scope dictates, GRI, PSS, ISPS, AMS/ENS, doc, customs, haulage, accessorials). Label any amount you don't have a live source for as `[example — confirm vs your tariff]`.
4. **Apply margin and show it.** Use `scripts/freight_calc.py quote --base <buy> --surcharge NAME=amt ... --margin <m>%`. State the method (on-cost vs on-sell) and print **buy / sell / margin (absolute + %)**.
5. **Set validity + exclusions.** Add a "valid until" date and an explicit Exclusions section (duty/VAT, insurance, out-of-scope legs per the Incoterm).
6. **Emit the quote sheet** in the plugin's Output Contract format, then the Structured Output JSON block.

## Guardrails
- All-in or it's not a quote — no bare base rate.
- Scope must match the Incoterm (no destination charges on an FOB quote; no missing origin haulage on EXW).
- Margin is always shown, with its method named.
- Examples are labeled as examples; live numbers are the seller's to confirm.
