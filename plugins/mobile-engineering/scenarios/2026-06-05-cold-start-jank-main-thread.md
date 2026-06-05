---
scenario_id: 2026-06-05-cold-start-jank-main-thread
contributed_at: 2026-06-05
plugin: mobile-engineering
product: android
product_version: "unknown"
scope: likely-general
tags: [cold-start, jank, main-thread, startup, profiling, anr]
confidence: high
reviewed: false
---

## Problem

An Android app's cold start crept from ~1.1 s to ~3.4 s over a year of feature work, and the first frame after launch janked badly — a visible white-then-stutter before the home screen settled. Play Console's Android vitals flagged a rising "excessive slow cold starts" rate, and a few low-end devices logged ANRs during launch. The team's instinct was "the app got bigger, buy faster startup with a splash animation to hide it" — i.e. mask the symptom.

## Constraints context

- Single mobile app, native Android (Kotlin), targeting a wide device range including budget hardware where the main thread is the scarce resource.
- Several SDKs (analytics, crash reporter, A/B framework, an ads SDK) were each initialized synchronously in `Application.onCreate()` — the worst place, because everything there runs on the main thread before the first frame.
- A dependency-injection graph that eagerly constructed singletons at startup, and a disk read (a JSON config) on the main thread in the first activity's `onCreate`.

## Attempts

- Tried: adding a branded splash screen to "cover" the delay. Made the *perceived* start worse — the splash just gave the jank a stage. Cosmetic, not a fix; rejected.
- Tried: a release build + R8 and assuming that would reclaim the time. Helped binary size, not the main-thread serial work in `onCreate`. Wrong layer.
- Tried (the diagnosis that worked): captured a system trace (Perfetto / Android Studio profiler) of a cold start and read the main-thread timeline. The startup was a staircase of SDK `init()` calls and the synchronous config disk read — all blocking the first frame. The work, not the app size, was the cost.
- Tried (the fix): moved non-critical SDK init off the critical path with **App Startup** (`androidx.startup`) and lazy/background initialization; deferred analytics/ads init to after first frame; made the config read async (coroutine on `Dispatchers.IO`) with a sane default until it loads; let the DI graph construct startup singletons lazily. Cold start dropped back under ~1.3 s and the first-frame jank cleared.

## Resolution

**Cold start is a main-thread budget problem, not an app-size problem — measure the startup timeline before optimizing anything.** The reliable shape:

1. **Trace first.** Capture a cold-start system trace and read what the main thread actually does between process fork and first frame. The cause is almost always serial work on the main thread (SDK init, disk/JSON, eager singletons), not raw binary size.
2. **Get work off the critical path.** Only what the first frame *needs* runs before it. Everything else (analytics, ads, non-essential SDKs) initializes lazily or after first frame. `androidx.startup` (App Startup) sequences initializers and is the sanctioned hook; background-thread the rest.
3. **No disk or network on the main thread at launch.** Read config asynchronously with a default until it arrives; never block the first frame on I/O.
4. **Watch the right metric.** Track Time To Initial Display / Time To Full Display and the Play vitals cold-start buckets — not a stopwatch on a flagship device. The budget is set by the *slowest* supported device, where the main thread has the least headroom.

The mental model: the splash screen hides nothing the user can't feel. Every millisecond of main-thread work before the first frame is a millisecond of jank you're paying for — move it off the thread or defer it past the frame.

**Action for the next engineer:** when startup is slow or janky, do not add a splash or blame app size first. Capture a cold-start trace, find the serial main-thread work in `Application.onCreate()` / first-activity `onCreate`, and move the non-essential parts off the critical path. The iOS analog is identical — pre-`main`/`UIApplicationDidFinishLaunching` work on the main thread and synchronous framework init are the equivalent staircase.

Cross-reference: complements [`../best-practices/keep-the-main-thread-free.md`](../best-practices/keep-the-main-thread-free.md), [`../best-practices/instrument-crashes-and-anrs.md`](../best-practices/instrument-crashes-and-anrs.md), and [`../best-practices/background-work-uses-os-schedulers.md`](../best-practices/background-work-uses-os-schedulers.md). Background-API selection lives in the "Background work" tree in [`../knowledge/mobile-engineering-decision-trees.md`](../knowledge/mobile-engineering-decision-trees.md).
</content>
</invoke>
