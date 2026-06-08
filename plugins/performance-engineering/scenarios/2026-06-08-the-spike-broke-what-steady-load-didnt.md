---
scenario_id: 2026-06-08-the-spike-broke-what-steady-load-didnt
contributed_at: 2026-06-08
plugin: performance-engineering
product: k6
product_version: "unknown"
scope: likely-general
tags: [spike-test, elasticity, autoscaling, recovery, test-the-edges]
confidence: high
reviewed: false
---

## Problem

A platform comfortably held its peak at a steady ramp and signed off. The first real marketing drop sent traffic from baseline to roughly 6x in under a minute, and the system fell over — a flood of 5xx and timeouts for several minutes — then took far longer than expected to recover even after traffic settled. The steady-load numbers had been fine; the sudden surge was a different failure mode entirely.

## Constraints context

- All pre-prod load came from a gradual ramp (minutes-long), which let autoscaling and warm caches keep pace.
- Real demand was bursty and event-driven (drops, push notifications), arriving far faster than the ramp ever modeled.
- Autoscaling existed but had a cold-start lag; nobody had measured how the system behaved during the lag window.

## Attempts

- Tried: raising the steady-state peak target and re-ramping gradually to "prove more headroom". Failed — a slower ramp gave autoscaling time to react, so it kept passing; the gradual arrival pattern was the thing hiding the failure, not the magnitude.
- Tried: pre-scaling to the expected peak before the event. Failed as a general fix — it worked for a known scheduled drop but didn't cover unscheduled surges, and it meant paying for peak capacity continuously.
- Tried: an explicit spike test — step (not ramp) from baseline to peak, hold, then drop — measuring error rate during the surge and the recovery curve after. This worked: it exposed both the cold-start gap (errors during the scale-up lag) and a thundering-herd retry storm that lengthened recovery, neither visible under a ramp.

## Resolution

The spike test made the surge-specific failures measurable: errors spiked during the autoscaler's cold-start window, and aggressive client retries during that window piled on, stretching recovery well past when traffic normalized. The capacity/headroom work (a warm baseline pool sized for the surge floor) was owned here; the retry/backpressure fix for the herd routed to backend-engineering, and the autoscaler warm-pool/min-replica tuning routed to cloud-native-kubernetes. Sign-off was re-gated on a spike run, not just a ramp.

## Lesson

A gradual ramp lets autoscaling and caches keep up, so it hides exactly the failure a sudden surge causes — step from baseline to peak, don't ramp, and measure both the error rate during the surge and the recovery curve after. Elasticity and recovery are their own test; passing steady load says nothing about surviving a spike.
