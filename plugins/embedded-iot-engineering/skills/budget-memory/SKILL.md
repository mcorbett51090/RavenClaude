---
name: budget-memory
description: "Track flash and RAM (image, static, worst-case stack/heap) against the part's limits. Reach for this on any memory or footprint question."
---

# Skill: Budget memory

Running out of RAM in the field is a brick, not a warning — budget memory like money (§3 #3).

## Step 1 — Measure the regions
Image size (flash), static RAM, worst-case stack and heap.

## Step 2 — Compare to the part
Flash and RAM used vs available per region via `embedded_iot_calc.py memory-budget` (§3 #3).

## Step 3 — Require headroom
Leave margin for stack peaks and OTA dual-bank; no-headroom is over-budget (§3 #3 #5).

## Step 4 — Flag fragmentation risk
Treat heap fragmentation and stack overflow as design defects (§3 #3 #4).

## Output
A flash/RAM budget per region vs the part's limits, with headroom % and an over-budget flag.
