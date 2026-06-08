---
scenario_id: 2026-06-08-stockout-next-to-overstock
contributed_at: 2026-06-08
plugin: retail-store-operations
product: inventory
product_version: "unknown"
scope: likely-general
tags: [allocation, replenishment, weeks-of-supply, open-to-buy, store-sku]
confidence: high
reviewed: false
---

## Problem

A multi-store retailer kept seeing lost sales on a hero SKU even though the chain-level inventory report showed "plenty on hand." One flagship store had been stocked out for two weeks during its peak, while three lower-volume stores were each sitting on 12–16 weeks of supply of the same SKU. Because the buyer read availability at the aggregate, the instinct was to buy more — which would have pushed the category past its open-to-buy and pre-committed a markdown on the stores that were already overstocked.

## Constraints context

- ~40 stores, wide volume spread; allocation ran on a flat, equal-units rule at receipt, ignoring per-store demand rate.
- Replenishment was chain-level, not store-SKU level.
- Open-to-buy for the category was nearly exhausted; another buy would have gone over.

## Attempts

- Tried: buying more to "fix the stockout." Caught before commitment — the OTB calc (planned sales − planned markdowns + target ending inventory − on-hand − on-order) showed the category was already over-bought; more units would deepen the overstock, not cure the stockout.
- Tried: an equal-units re-allocation across stores. Failed — equal units to unequal demand just recreates the imbalance; the flagship would re-stock out while the slow stores stayed long.
- Tried: a weeks-of-supply-based transfer — move units from the 12–16-week stores down toward a target WOS and re-point the flagship's replenishment to its own demand rate. This cured the stockout with zero incremental buy and pulled the overstocked stores back toward target.

## Resolution

The fix was a store-SKU-level transfer sized by weeks-of-supply (not equal units), plus a per-store replenishment reset keyed to each store's demand rate, all inside the existing open-to-buy. The aggregate had been hiding the whole problem: total availability looked fine while the store-SKU truth was a stockout next to an overstock. No additional buy was needed.

## Lesson

Allocate and replenish at the store-SKU level — aggregate availability is a comforting lie during a stockout — and respect the open-to-buy cap before buying your way out of an imbalance that's actually a distribution problem. Size transfers and replenishment by weeks-of-supply against each store's demand rate, never by equal units.
