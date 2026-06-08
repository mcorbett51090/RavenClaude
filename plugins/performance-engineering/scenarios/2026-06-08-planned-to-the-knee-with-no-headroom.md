---
scenario_id: 2026-06-08-planned-to-the-knee-with-no-headroom
contributed_at: 2026-06-08
plugin: performance-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [capacity, littles-law, headroom, failover, saturation-point]
confidence: high
reviewed: false
---

## Problem

A team sized a fleet from a target of 5,000 req/s and a measured per-instance ceiling of ~1,000 req/s, provisioned exactly 5 instances, and called it done. It held in the load test. Then one node was lost during a routine deploy, the remaining four saturated instantly, latency went vertical, and the cascade took the whole fleet down. The capacity math had been arithmetically correct and operationally wrong.

## Constraints context

- The per-instance number used was the saturation ceiling (the knee), not a sustainable below-the-knee rate.
- The plan assumed all N instances are always healthy — no allowance for a node loss, a deploy, or organic growth.
- Demand was open-arrival (user traffic), so when capacity dropped, load did not back off; it kept arriving and queued.

## Attempts

- Tried: provisioning to exactly `target / per-instance` = 5 instances. Failed in the first node-loss event — planning to the knee means any single instance lost pushes the rest past saturation, and past the knee latency turns sharply non-linear, so the survivors collapsed rather than degraded gracefully.
- Tried: reacting with autoscaling only after saturation appeared. Failed — the autoscaler's cold-start lag was longer than the time it took the four overloaded instances to saturate and start erroring; scaling reactively couldn't outrun the cascade.
- Tried: re-sizing with explicit headroom — de-rate the per-instance ceiling so each instance plans below the knee, then size the fleet against that de-rated rate plus an allowance for N-1 survival and growth. This worked: at ~30% headroom the fleet absorbed a single node loss without crossing the knee.

## Resolution

The fix was to stop sizing to the saturation point. Using Little's law for the concurrency and the *measured* per-instance saturation rate de-rated by a headroom fraction (so each instance runs below its knee), the team sized the fleet to survive N-1 plus near-term growth rather than to exactly meet steady demand. Capacity planning was owned here (the math + the headroom target); the autoscaler/min-replica implementation routed to cloud-native-kubernetes. A node loss became a non-event instead of an outage.

## Lesson

Headroom is computed, not vibed, and you never plan to 100% utilization. Size from the measured saturation point de-rated by an explicit failover/growth headroom (Little's law gives the concurrency; the per-instance knee gives the ceiling) so the fleet survives a node loss without crossing the knee — past which latency goes non-linear and a shortfall becomes a cascade.
