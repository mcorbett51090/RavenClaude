---
scenario_id: 2026-06-08-the-leak-only-showed-after-six-hours
contributed_at: 2026-06-08
plugin: performance-engineering
product: k6
product_version: "unknown"
scope: likely-general
tags: [soak-test, memory-leak, connection-pool, test-the-edges, regression]
confidence: high
reviewed: false
---

## Problem

A service passed every load test — p95/p99 green at peak traffic, the knee located by a stress run — and shipped. Three days into production, latency crept up over each day and the pods OOM-killed and restarted on a rough 8-hour cycle. The short tests had all been clean; the failure only existed over time, and nothing in the pre-prod suite could have caught it because nothing ran long enough.

## Constraints context

- The whole pre-prod suite was short: load and stress runs were 15–30 minutes each, never longer.
- Production traffic was steady but continuous; the symptom was a slow climb, not a spike.
- The restart cycle masked it for a while — each OOM-kill reset the memory, so dashboards looked "recovered" every few hours rather than obviously broken.

## Attempts

- Tried: re-running the 30-minute load test at higher RPS to reproduce the OOM. Failed — at 30 minutes the heap growth was still in the noise; the run finished long before the leak became visible, so it stayed green.
- Tried: bumping the pod memory limit to "buy headroom". Failed — it only lengthened the cycle from ~8 hours to ~14; the underlying growth was unbounded, so a bigger ceiling just delayed the same OOM.
- Tried: a 6-hour soak at steady expected load with heap + RSS + connection-pool gauges sampled throughout. This worked — RSS climbed linearly and the DB connection pool's in-use count never returned to baseline, pointing straight at connections (and their buffers) that were acquired but not released on one error path.

## Resolution

The soak made the slow leak observable: a non-happy-path branch returned without releasing a pooled connection, so under continuous traffic the pool's retained objects grew without bound until the heap hit the limit. The fix (release in a `finally`) routed to the owning service team; the soak test was added to the pre-prod gate at 6 hours minimum, and the connection-pool in-use gauge was committed as a baseline so the regression would be caught next time before release, not three days after.

## Lesson

Load and stress prove the steady state and the knee but never the leak — degradation over time only shows in a soak that runs for hours, not minutes. Watch RSS/heap growth and pool in-use counts over the whole soak; a number that doesn't return to baseline between requests is the leak. One short run is not a performance test; cover the edges or name which you skipped and why.
