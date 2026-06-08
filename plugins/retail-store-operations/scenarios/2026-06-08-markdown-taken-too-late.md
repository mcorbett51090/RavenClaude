---
scenario_id: 2026-06-08-markdown-taken-too-late
contributed_at: 2026-06-08
plugin: retail-store-operations
product: merchandising
product_version: "unknown"
scope: likely-general
tags: [markdown, sell-through, weeks-of-supply, seasonal, clearance]
confidence: high
reviewed: false
---

## Problem

A specialty retailer ran a seasonal apparel line and held the line at full price deep into the season because "it might still sell." By the time the buyer agreed to mark it down, sell-through had stalled at ~35% with eight weeks of supply and only four selling weeks left. The eventual markdown had to go to 60% off to clear, and even then a tail of units went to a liquidator below cost. The four-wall margin on the line came in far under plan, and the back room stayed full through the next season's set, which delayed the new planogram.

## Constraints context

- Seasonal line with a hard end-of-season date; no replenishment.
- Markdown authority sat with a buyer who was measured on full-price sell-through, so every markdown felt like admitting a miss.
- No standing rule tying the first markdown to a sell-through / weeks-of-supply trigger — markdowns were ad hoc and emotional.

## Attempts

- Tried: holding at full price and hoping demand returned. Failed — sell-through kept decaying while weeks-of-supply stayed high relative to the weeks remaining; the gap only widened.
- Tried: one big late markdown to clear. Failed on margin — a single deep cut late in the season gave away far more margin than a shallow early one would have, and still left a liquidation tail.
- Tried: a sell-through-triggered cadence — a shallow first markdown the moment sell-through fell below the life-cycle plan with weeks-of-supply above the terminal threshold, then a scheduled step-down to terminal clearance. Modeled against the prior season, this cleared the line inside the season at a materially better blended margin.

## Resolution

The team adopted a standing markdown cadence: the first markdown is triggered by sell-through falling below the life-cycle curve while weeks-of-supply exceeds the weeks remaining, taken shallow and early, then stepped down on a schedule to terminal clearance. Decoupling the trigger from the buyer's full-price metric removed the emotional delay. Blended margin on seasonal lines improved and the back room cleared in time for the next set.

## Lesson

Markdown is a decision tied to sell-through and weeks-of-supply, not a default and not a calendar event — and the first markdown is the cheapest one you'll take. Holding for hope trades a shallow early cut for a deep late cut plus carrying cost plus a delayed planogram. Put the trigger in a rule, not in the buyer's gut.
