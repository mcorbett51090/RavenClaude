---
name: build-move-estimate
description: "Turn a household-goods move into a defensible estimate by building a cube sheet (room-by-room inventory, cube→weight at the ~7 lb/cf rule of thumb) or a weight basis, choosing the estimate type (binding vs non-binding vs not-to-exceed vs local hourly) as a deliberate risk-allocation decision, pricing local (hourly) vs long-distance/interstate (weight-and-distance against a tariff), adding packing/materials and accessorials, and stating the flip conditions. Reach for this when the user asks 'how do I quote this move?', 'binding or hourly?', 'how much for a 3-bedroom cross-country?', or 'why do I keep losing money on jobs?'. Used by `moving-operations-lead` (primary); consulted by `moving-compliance-and-claims-specialist` to confirm the estimate rests on a valid tariff and the type is disclosed."
---

# Skill: build-move-estimate

> **Invoked by:** `moving-operations-lead` (primary). Also consulted by `moving-compliance-and-claims-specialist` to confirm the estimate rests on a **valid, current tariff** and that the estimate type is **disclosed** as required.
>
> **When to invoke:** "How do I quote this move?"; "binding, non-binding, not-to-exceed, or hourly?"; "how much for a 3-bedroom long-distance?"; "why do my jobs lose money?"; any move from an inventory to a priced estimate.
>
> **Output:** the cube/weight build + the estimate-type choice + local-vs-long-distance pricing + packing/materials/accessorials + the 1-2 flip conditions. Capture it in [`../../templates/move-estimate-and-cube-sheet.md`](../../templates/move-estimate-and-cube-sheet.md).

## Procedure

1. **Build the cube sheet before quoting a number.** Go room-by-room; assign each item its estimated **cubic feet**; total the cube. Convert cube→weight at roughly **~7 lb per cubic foot** _(rule of thumb — verify against the shipment)_. An estimate without an inventory is a coin flip. See [`../../knowledge/moving-relocation-patterns-2026.md`](../../knowledge/moving-relocation-patterns-2026.md).
2. **Choose the estimate type as a risk-allocation decision.** **Binding** (fixed price, mover carries under-count risk), **non-binding** (final on actual weight, customer carries it, federal cap on over-collection at delivery — verify), **not-to-exceed** (customer pays the lower of estimate/actual — customer-favorable), or **local hourly** (crew-hours × rate + travel + materials). Recommend deliberately; the *disclosure* of the type routes to the specialist.
3. **Price local vs long-distance on the right basis.** **Local** = hourly (crew size × rate × hours + travel/trip + materials). **Long-distance/interstate** = weight-and-distance (or cube) against a **tariff** + accessorials. Never price a long-haul like a local job or vice versa.
4. **Add packing/materials and accessorials.** Packing level (full-pack / fragile-only / self-pack), boxes/paper/tape/pads, and accessorials (long carry, stairs/elevator, shuttle, bulky items, storage-in-transit). These are real cost, not rounding.
5. **Confirm the tariff basis (route to specialist).** For interstate/long-distance, confirm the number rests on a **valid, current tariff** — the specialist owns whether the tariff is valid and whether the estimate type is disclosed as required.
6. **Sanity-check against margin.** Back the estimate out to a margin at the crew/truck cost it implies — an estimate that doesn't clear the job's labor + truck + materials cost is a loss, however the customer likes the price.
7. **State the flip conditions.** Name the 1-2 facts that would change the estimate (e.g. "if the actual cube exceeds the survey by >10%, a binding estimate eats it — re-survey or switch to not-to-exceed").

## Worked example

> User: "3-bedroom house, moving 900 miles across state lines. Do I quote binding or hourly, and how do I price it?"

- **Branch:** estimating; and note this is **interstate** → authority + disclosures route to the specialist before dispatch.
- **Cube sheet:** room-by-room ≈ 1,400 cf → ~9,800 lb at ~7 lb/cf _(verify with a survey)_.
- **Estimate type:** **not hourly** — 900 miles is long-distance, priced weight-and-distance against the tariff. Offer **binding** or **not-to-exceed**; not-to-exceed is customer-favorable (pays the lower) and reduces dispute risk if the survey was tight.
- **Price:** tariff rate for ~9,800 lb × 900 mi + accessorials (long carry, packing) + materials; confirm the tariff is valid/current (→ specialist).
- **Margin check:** back out crew, truck, fuel, and interline to confirm the number clears margin.
- **Flip condition:** if the physical survey lands >10% over the cube estimate, a binding number eats the gap — re-survey or use not-to-exceed.
- **Routed to specialist:** USDOT/MC authority, the tariff validity, and the required federal disclosures ("Your Rights and Responsibilities When You Move" + BOL) before the job is booked.
- **Captured in** [`../../templates/move-estimate-and-cube-sheet.md`](../../templates/move-estimate-and-cube-sheet.md).

## Guardrails

- Never quote a number without a **cube sheet / inventory** — build the estimate from the physical shipment, not a guess.
- The **estimate type is a risk-allocation decision** — recommend binding vs non-binding vs not-to-exceed vs hourly deliberately; the *disclosure* of it is the specialist's.
- **Local is hourly; long-distance is weight-and-distance against a tariff** — don't cross the wires.
- For **interstate** work, route operating authority, tariff validity, and the required disclosures to the specialist **before** the job is dispatched.
- Estimate-type rules (esp. the non-binding over-collection cap) and tariff conventions are **federal/state and volatile** — carry a **retrieval date**; this is operational guidance, not legal advice.
- The cube→weight ~7 lb/cf factor is a **rule of thumb** — verify against the actual shipment before relying on it.
