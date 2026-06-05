---
scenario_id: 2026-06-05-frame-time-gc-hitch
contributed_at: 2026-06-05
plugin: game-development
product: unity-csharp
product_version: "unknown"
scope: likely-general
tags: [frame-time, gc, hitch, allocation, object-pool, profiler]
confidence: high
reviewed: false
---

## Problem

A mobile action game held a steady 60 FPS in the profiler's average, but players reported a "stutter" every couple of seconds during combat. The average frame time looked healthy (~14 ms); the problem was invisible until the team stopped looking at the mean and started looking at the worst frames. A periodic ~40 ms spike — a single dropped frame — recurred on a rhythm that tracked enemy spawns and damage-number popups. The instinct was "the GPU can't keep up, lower the graphics tier." That was wrong.

## Context

- Unity / C# (the managed-runtime GC-hitch pattern is the same on any tracing-GC runtime — Unity's Mono/IL2CPP, a C# server, a GC'd scripting layer).
- 60 FPS target → a **16.67 ms frame budget**. A 40 ms spike is ~2.4 frames of work in one frame: a guaranteed visible hitch.
- The combat code allocated per-event: a `new` damage-number string each hit, a fresh `List<>` of hit targets per attack, a closure captured per projectile. None individually large; together they fed the managed heap until a Gen-0 collection fired mid-combat.
- The "average FPS" readout hid it completely — one 40 ms frame among sixty 14 ms frames barely moves the mean.

## Attempts

- Tried: lowering the render tier (shadows, particle count). Outcome: the average got *better* and the hitch stayed exactly the same — proof it was not GPU-bound. Lowering graphics to fix a CPU/GC hitch treats the wrong subsystem.
- Tried: reading **percentile frame time, not average** — captured a frame-time histogram and looked at the 99th percentile / max. The spikes lined up with GC.Collect markers in the profiler timeline. Outcome: named the cause as managed allocation, not rasterization.
- Tried (the fix): killed per-frame allocation in the hot path — pooled the damage-number objects, reused a pre-sized hit-target buffer instead of `new List<>` per attack, hoisted the closures out of the per-projectile loop. Allocations-per-frame in combat dropped from kilobytes to ~zero. Outcome: the periodic Gen-0 collection stopped firing during combat; the 99th-percentile frame time fell under budget; the stutter was gone.

## Resolution

**A hitch is a frame-budget problem, and you find it in the worst frames, not the average.** The order that worked:

1. **Convert the FPS target to a per-frame millisecond budget** (60 → 16.67 ms, 30 → 33.3 ms) and measure against *that*. "60 FPS average" is not "no frame missed 16.67 ms."
2. **Read the 99th-percentile and max frame time**, not the mean — a hitch is a tail-latency event by definition; the mean launders it away (the §3 "metric needs a window + baseline" discipline applied to frame time).
3. **Correlate the spike with the profiler's GC markers.** A periodic spike on a managed runtime is a GC collection until proven otherwise; a spike that tracks a gameplay event (spawn, hit, load) points at that event's allocations.
4. **Eliminate the per-frame allocation** — object-pool the churned objects, reuse buffers, avoid closures/boxing/LINQ in the hot path. Don't fight the GC with `GC.Collect()` tuning; remove the garbage so it never runs mid-frame.

The trap: the average frame rate is the *reassuring* number and the dropped frame is the *quiet* cause, so the instinct is to lower graphics. That treats a GPU symptom the game doesn't have.

**Action for the next engineer:** when a game "runs at 60 but stutters," stop quoting average FPS. Pull a frame-time histogram, read the max/99th-percentile against the millisecond budget, and check whether the spikes sit on GC markers before you touch the render settings. Cross-reference [`../knowledge/gamedev-runtime-performance-decision-trees.md`](../knowledge/gamedev-runtime-performance-decision-trees.md) (the "frame is over budget" tree) and the frame-budget mode of [`../scripts/gamedev_budget.py`](../scripts/gamedev_budget.py).
