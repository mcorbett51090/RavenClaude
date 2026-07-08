---
name: model-unit-economics
description: "Build a royalty-loaded unit-economics model for a franchise unit: revenue with royalty + ad-fund + fees taken off the top, then COGS / labor / occupancy / other opex to a unit profit and a break-even, plus total investment and months-to-ramp — so a buy/expand decision rests on bottom-up numbers, not the brand's Item-19 headline. Reach for it before any franchise buy or expansion. Used by `franchise-operations-strategist` (primary). Not investment advice."
---

# Skill: model-unit-economics

> **Invoked by:** `franchise-operations-strategist` (primary). Deep model mechanics/projections route to `finance`.
>
> **When to invoke:** evaluating a franchise buy, an expansion unit, or any "will this pencil?" question.
>
> **Output:** a royalty-loaded unit P&L + break-even + total investment + months-to-ramp. Fee figures carry a retrieval date + `[verify-at-use]`; this is business decision-support, not investment advice.

## Procedure

1. **Build revenue bottom-up.** Don't start from the brand's average unit volume (AUV). Estimate from your market/site: traffic × ticket, or capacity × utilization. Cross-check against Item 19 — but treat Item 19 as a sanity band, not the input.
2. **Take the franchise fees off the top.** Royalty (% of gross), ad/brand fund (% of gross), tech/other recurring fees — subtract from revenue *first*. This is the step operators skip; it's where a unit that looked profitable turns marginal. Verify the exact percentages from the current FDD (Item 5/6) `[verify-at-use]`.
3. **Layer the operating costs.** COGS %, labor % (prime cost = the two together), occupancy/rent, utilities, insurance, local marketing, other opex — to a unit-level operating profit.
4. **Compute break-even and contribution.** Fixed cost ÷ contribution margin = break-even revenue; compare to your bottom-up revenue for headroom.
5. **Total the investment and the ramp.** Franchise fee + build-out + equipment + initial inventory + **working capital to cover the ramp to break-even**. Undercapitalization during ramp is the #1 unit killer — model the months of negative cash.
6. **Stress it.** Sensitivity on revenue (−15/−25%), labor (+3-6 pts), and rent. If it only works at the top of the range, it's a no.

## Worked example

> QSR unit, bottom-up revenue \$850k.

- Fees off the top → 6% royalty + 2% ad fund = \$68k → net \$782k `[verify-at-use]`.
- COGS 30% (\$255k) + labor 28% (\$238k) = prime 58%; occupancy \$90k; other opex \$95k → unit profit ≈ \$104k.
- Investment → \$45k franchise fee + \$400k build-out + \$90k working capital ≈ \$535k; ramp ≈ 5 months negative.
- Stress → at −20% revenue the unit is near break-even → thin; decision hinges on site confidence.

## Guardrails

- **Never underwrite on the brand's headline AUV** — model bottom-up, use Item 19 as a band.
- **Fees come off revenue before the P&L** operators usually look at — the most common modeling error.
- **Working capital for the ramp is part of the investment** — undercapitalization kills otherwise-good units.
- **Exact fee percentages are per-FDD-edition** — verify from the current document.
