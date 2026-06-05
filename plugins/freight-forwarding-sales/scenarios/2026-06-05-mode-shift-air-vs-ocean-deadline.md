---
scenario_id: 2026-06-05-mode-shift-air-vs-ocean-deadline
contributed_at: 2026-06-05
plugin: freight-forwarding-sales
product: mode-selection
product_version: "n/a"
scope: likely-general
tags: [mode-selection, air, ocean, sea-air, deadline, inventory-carrying-cost]
confidence: medium
reviewed: false
---

## Problem

A shipper called in a panic: a production line in Europe would stock out in ~12 days, and the replenishment cargo (high-value-density electronics, ~400 kg chargeable) was still in Asia. The customer's instinct was "put it all on air, whatever it costs." The seller's job was to land the deadline **and** not reflexively burn the customer's money — full air was the obvious answer but not automatically the right one, and an all-or-nothing framing missed the cheaper options that still beat the stock-out.

## Context

- Segment: manufacturing BCO, time-critical replenishment; the real cost the customer was avoiding was the **stock-out / line-down cost**, which dwarfed any freight premium — that's the comparison that governs a mode-shift, not freight price in isolation.
- Constraint: air runs **~4–10× ocean per kg** on the lane; full ocean FCL door-to-door was ~25–35+ days (misses the deadline); a **sea-air hybrid** via a transshipment hub trades some transit for large savings vs pure air and can still hit a tight-but-not-immediate window. [verify-at-use]
- The customer conflated "fastest" with "all air" — the right question was the **cheapest mode that still beats the deadline**, weighing inventory-carrying / stock-out cost against the freight premium, exactly what the mode-selection decision tree routes.

## Attempts

- Tried: anchored on the **deadline and the stock-out cost first**, not the freight quote — quantified what a line-down day costs so the air premium could be judged against it rather than against the ocean rate. Outcome: reframed "air is expensive" as "air is cheap relative to the line going down," which made the decision rational instead of emotional.
- Tried: priced **three options** — full air (hits the deadline, highest cost), **sea-air hybrid** (hits a tight window, ~mid-cost), and a partial split (air the minimum to bridge the stock-out, ocean the balance). Used `scripts/freight_calc.py air` to settle the **chargeable weight** (volumetric vs actual) before quoting, so the air number was real. Outcome: gave the customer a cost/transit menu instead of a single panic number.
- Tried: recommended the **split** — enough air to bridge the 12-day gap, the rest on ocean — as the lowest total-cost option that still protected the line. Outcome: landed the deadline at materially less than full-air cost.

## Resolution

The right answer was **not** "all air." Framing the decision as *cheapest mode that still beats the deadline*, with the stock-out cost (not the ocean rate) as the benchmark, surfaced a part-air / part-ocean split that protected the production line at far less than full-air cost. The chargeable-weight calc kept the air quote honest. Mode selection under a deadline is a total-landed-cost trade, not a speed-at-any-price reflex.

**Action for the next consultant hitting this pattern:** quantify the **deadline and the stock-out / inventory-carrying cost first** — that's the benchmark the freight premium is judged against, not the ocean rate. Price a menu (full air / sea-air hybrid / air-bridge-plus-ocean-split), settle **chargeable weight** before quoting air, and recommend the lowest total-landed-cost mode that still beats the deadline. "All air" is a reflex; the split is usually cheaper and still on time.

**Sources (retrieved 2026-06-05):** air runs ~4–10× ocean per kg; ocean FCL door-to-door ~25–42 days; sea-air hybrid trades transit for cost — https://www.exfreight.com/air-freight-vs-ocean-freight-cost-transit-decision-framework/ ; https://blogs.tradlinx.com/air-vs-ocean-freight-in-2025-rising-costs-e-commerce-and-the-great-shift-in-global-logistics/ . Per-kg ratios, transit times, and the air/ocean crossover weight are lane- and date-volatile — treat any figure as `[example — confirm against your live rates/schedule]` (§3 #8).
