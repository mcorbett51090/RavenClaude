---
scenario_id: 2026-06-08-coordinated-omission-hid-the-tail
contributed_at: 2026-06-08
plugin: performance-engineering
product: jmeter
product_version: "unknown"
scope: likely-general
tags: [load-test, coordinated-omission, open-vs-closed, percentiles, k6]
confidence: high
reviewed: false
---

## Problem

A team's load test reported a beautiful p99 of 180 ms at 2,500 req/s and signed off the release. In production the same traffic produced p99s over 4 seconds and a wave of timeouts. The test had passed; the system had not. The reported tail latency was simply not real.

## Constraints context

- The load test was a closed-model JMeter plan: a fixed pool of ~200 threads, each looping "send request → wait for response → think → repeat".
- Real traffic was open-arrival (user-driven), independent of how fast the system responded.
- Sign-off was gated on the test's reported p99, which everyone trusted.

## Attempts

- Tried: re-running the same closed-model test with more threads. Failed — it just shifted the same lie; when the server slowed, each thread *waited*, so it never issued the requests that would have recorded the worst latencies (coordinated omission). The tail stayed artificially clean.
- Tried: reporting the average from the run to "smooth out noise". Failed — the average was even more flattering and hid the tail completely; the mean was the number that lied.
- Tried: rebuilding the test in k6 with a constant-arrival-rate (open-model) executor that keeps issuing requests on schedule regardless of response time, plus latency correction. This worked — the recorded p99 jumped to match what prod actually saw, and the knee at ~1,900 req/s became visible before release.

## Resolution

The open-model executor stopped the generator from self-throttling, so the worst-case latencies were actually requested and recorded. The "passing" run now failed at the real target, which is exactly what a useful test does — it caught the saturation pre-prod. The team re-gated sign-off on the open-model p99 and added a stress run to locate the knee explicitly.

## Lesson

A closed-model load test on open-arrival traffic hides saturation by throttling itself, and an uncorrected generator omits the worst latencies (coordinated omission) so the reported tail is a lie. Use an open arrival-rate executor with latency correction, report p95/p99/max not the average, and distrust any tail number whose executor you can't name.
