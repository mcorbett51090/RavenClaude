---
name: optimize-occupancy-and-dynamic-pricing
description: Turn a self-storage facility's occupancy and rate picture into a revenue plan by reading physical vs economic occupancy, comparing street rate to in-place rate by unit type, designing the ECRI program (existing-customer rate increases — cadence, increase size by tenure and gap, churn guardrail), setting dynamic-pricing floors and ceilings, rebalancing the unit mix, and pricing promotions against the ECRI that recovers them — returning the recommended moves with projected NOI lift and the conditions that would flip them. Reach for this when the user asks "how do I raise rates on existing tenants?", "my street and in-place rates are far apart", "should I run a $1-first-month promo?", or "why is my full facility not making money?". Used by `storage-revenue-and-occupancy-specialist` (primary).
---

# Skill: optimize-occupancy-and-dynamic-pricing

> **Invoked by:** `storage-revenue-and-occupancy-specialist` (primary). Also consulted by `self-storage-operations-lead` to read occupancy before routing the revenue call.
>
> **When to invoke:** "How/when do I raise rates on existing tenants (ECRI)?"; "my street rates and in-place rates are far apart"; "should I discount to fill units?"; "why is my 95%-full facility not making money?"; any move from an occupancy/rate picture to a revenue plan.
>
> **Output:** the occupancy read (physical vs economic + the gap) + street-vs-in-place by unit type + the ECRI program + dynamic-pricing floor/ceiling + unit-mix + promotion policy + projected lift + the 1-2 flip conditions. Capture it in [`../../templates/ecri-and-pricing-plan.md`](../../templates/ecri-and-pricing-plan.md).

## Procedure

1. **Read the two occupancy numbers before touching rates.** Compute **physical/unit occupancy** (units rented ÷ total) and **economic occupancy** (actual revenue ÷ revenue-at-current-street-rate). The **gap** is the diagnostic — a full facility with low economic occupancy is losing money to discounts, stale in-place rates, and delinquents, not to empty units. See [`../../knowledge/self-storage-patterns-2026.md`](../../knowledge/self-storage-patterns-2026.md).
2. **Lay out street vs in-place rate by unit type.** For each unit type (size × drive-up/climate), the current street rate vs the average in-place rate the sitting tenants pay. The spread, across the base, is the ECRI opportunity.
3. **Design the ECRI program — the core profit lever.** Existing-customer rate increases raise in-place rates toward street on tenants past a tenure threshold. Set: the **cadence** (first increase after ~6–12 months, then periodic — verify against the base), the **increase size scaled by tenure and the in-place-vs-street gap**, and a **churn guardrail** (an acceptable move-out rate; the increase wins when retained-revenue lift > churn loss). Never a blanket hike. High switching costs are why this flows almost entirely to NOI.
4. **Set street rate dynamically with a floor and a ceiling.** Street rate moves with unit-type occupancy and demand — automate it (native PMS pricing or a revenue-management layer) inside a floor (never below cost/market) and a ceiling. Don't hand-set once a year.
5. **Rebalance the unit mix to demand.** Flag a mix that caps revenue (too many of one size, no 5×5s / no climate / no drive-up); price scarce types up; consider conversion/repartition where the demand justifies it.
6. **Price promotions against the recovering ECRI.** A $1-first-month / free-month / % promo is an **acquisition cost** — model its payback against the in-place rate and ECRI cadence that recover it over the expected stay. If the ECRI can't recover it, don't run it.
7. **Project the lift and state the flip conditions.** Estimate the NOI lift from the ECRI + dynamic pricing + mix moves, and name the 1-2 facts that would change the plan (e.g. "if the submarket softens and street rates fall, the ECRI ceiling tightens").

## Worked example

> User: "We're 96% physically full but revenue feels flat. Should I discount to hit 100%?"

- **Occupancy read:** 96% physical but **economic occupancy 79%** → a 17-point gap. The facility isn't short of tenants; its sitting tenants are ~20% below street and two long-tenants haven't seen an increase in 3 years. **Discounting to 100% would make it worse.**
- **Street vs in-place:** 10×10 climate street rate $165; average in-place $132 — a $33 gap across ~40 units.
- **ECRI:** raise the tenants >12 months in place toward street in a staged increase (e.g. +$15 now, revisit in 6 months), sized by each tenant's gap and tenure; churn guardrail = tolerate up to ~3% move-out because the retained lift dominates. Projected: most of the ~$33 × occupied-unit gap recovered to NOI.
- **Dynamic pricing:** put street rate on auto with a $150 floor / $185 ceiling for the 10×10 climate type.
- **Promotion:** the $1-first-month is fine *only* because the ECRI recovers it within ~5 months — modeled, not assumed.
- **Flip condition:** if a new competitor opens and street rates drop, retighten the ECRI ceiling and pause the promo.

## Guardrails

- Never make a rate call before separating physical from economic occupancy — physical occupancy flatters.
- ECRIs are sized by tenure + gap with a churn guardrail — never a blanket hike, never "we don't raise on existing tenants."
- Street rate is dynamic (floor + ceiling); in-place rate is closed toward it by the ECRI — don't conflate the two.
- A promotion is an acquisition cost with a payback model against the recovering ECRI — not a giveaway.
- The rate-change notice an ECRI requires is contractual/state-specific — verify; this is operational guidance, not legal advice.
- Volatile claims (PMS/pricing-tool features, REIT benchmarks, market street rates) carry a **retrieval date** — re-verify before a client commitment.
