---
scenario_id: 2026-06-05-capacity-cu-throttling-background-rejection
contributed_at: 2026-06-05
plugin: microsoft-fabric
product: fabric-capacity
product_version: "2026.05"
scope: likely-general
tags: [capacity, cu, throttling, smoothing, background-rejection, isolation]
confidence: high
reviewed: false
---

## Problem

An enterprise on a single **F64** capacity reported that executive Power BI dashboards "froze" every weekday morning — reports timed out or returned `capacity throttled` for ~30–45 minutes around 7:30 a.m., then recovered on their own. The reflex from the platform team was "we've outgrown F64, scale to F128." The ask was to confirm the sizing diagnosis before committing to roughly double the annual capacity spend.

## Constraints context

- One **F64** capacity (64 CU) carrying *everything*: interactive BI, two Spark medallion notebooks, three Data Factory pipelines, and a nightly semantic-model refresh — no workload isolation (CLAUDE.md §3 #5 anti-pattern: "one capacity for everything").
- The morning stall lined up exactly with a 7:00 a.m. pipeline + Spark refresh window feeding the gold layer.
- Region single-tenant; no second capacity provisioned. Capacity admin available.
- The Fabric Capacity Metrics app showed `InteractiveRejection` spiking while smoothed `Background %` was already near the ceiling from the overnight/early-morning jobs.

## Attempts

- Tried: reading the **Capacity Metrics app** over a long (multi-day) window before any sizing change — house opinion #5 and the capacity-throttled decision tree's first node ("one-off spike vs sustained"). Found the stall was **not** sustained all-day overload; it was a **collision** — heavy *background* work (Spark + pipelines) smoothing over 24 h pushed the capacity into **background rejection**, and because many "interactive-looking" SQL/UI ops are billed as **background**, the morning BI traffic got rejected alongside it. Outcome: ruled out "genuinely undersized" — the capacity was busy, not too small.
- Tried (rejected): scale F64 → F128. Would have absorbed the collision by brute force but at ~2× cost, and left the root cause (no isolation) in place — a bigger shared capacity still co-mingles BI and background, so the same collision returns at higher volume. Outcome: ruled out as the first move.
- Tried (the move that worked): **isolated** the noisy workloads. Interactive BI stayed on F64 (tagged Mission Critical); the Spark notebooks + Data Factory pipelines moved to a smaller **F16** prep capacity. On the remaining shared edges, set **surge protection** background-rejection/recovery thresholds tuned from the Metrics charts (rejection ~65%, recovery ~50%). Outcome: morning stalls disappeared; total spend (F64 + F16) came in below the F128 alternative, and BI was now structurally protected from a background surge.

## Resolution

The throttling was a **workload-collision problem**, not a sizing problem. Background smoothing (background ops average over 24 h; interactive over 5–64 min) meant the early-morning Spark/pipeline burst was still "occupying" the capacity when BI users arrived, and per-capacity throttling rejected the interactive traffic. **Isolation** (move noisy background work off the BI capacity) plus **surge protection** on shared edges fixed it for less than the scale-up would have cost.

**Action for the next consultant hitting this pattern:** when a single capacity throttles at a *predictable time of day* that coincides with background jobs, do **not** scale up first. Read the Metrics app over a long window to separate a one-off spike from sustained overload (smoothing hides short stress tests), confirm whether interactive rejection is riding a background surge, then **isolate before you scale** — scale-up is the move only once the workload is lean *and* already isolated. Traverse [`../knowledge/fabric-decision-trees.md`](../knowledge/fabric-decision-trees.md) "Capacity is throttled — what do I do right now?" (order: verify → optimize → isolate/surge-protect → scale) and apply [`../best-practices/capacity-isolate-noisy-workloads.md`](../best-practices/capacity-isolate-noisy-workloads.md) + [`../best-practices/capacity-size-to-average-not-peak.md`](../best-practices/capacity-size-to-average-not-peak.md). The field-note complement to those canonical rules.

**Sources (Microsoft Learn, retrieved 2026-06-05 — Fabric ships monthly, `[verify-at-use]`):** [Throttling policy](https://learn.microsoft.com/fabric/enterprise/throttling) · [Surge protection](https://learn.microsoft.com/fabric/enterprise/surge-protection) · [Evaluate and optimize capacity](https://learn.microsoft.com/fabric/enterprise/optimize-capacity) · [Capacity Metrics app](https://learn.microsoft.com/fabric/enterprise/metrics-app). SKU/CU numbers and threshold examples are illustrative; validate against the client's actual Metrics-app charts before a deliverable (house opinion #9).
