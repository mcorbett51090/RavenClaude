---
scenario_id: 2026-06-05-throttling-429-retry-after-cascade
contributed_at: 2026-06-05
plugin: microsoft-graph
product: graph-api
product_version: "v1.0"
scope: likely-general
tags: [throttling, 429, retry-after, backoff, batch]
confidence: high
reviewed: false
---

## Problem

A nightly directory-sync job that read all users + their group memberships started failing roughly an hour into the run. The logs showed a wall of `429 Too Many Requests`, and once the 429s began they never stopped until the job was killed — a self-sustaining cascade. The team's first instinct ("add more workers to finish faster") had made it dramatically worse: more concurrency meant the throttle window was exhausted in minutes instead of an hour.

## Constraints context

- Application-permission daemon (no user), client-credentials flow, calling `/users` then `/users/{id}/memberOf` per user — the classic N+1 fan-out.
- ~40,000 users, so ~40,001 calls minimum before any batching.
- The retry logic was `except: time.sleep(1); retry` — a fixed 1-second sleep, ignoring the `Retry-After` header entirely.
- Six parallel workers, no jitter, all reading the same tenant's directory budget (a *shared* per-app-per-tenant budget, so the workers were competing with each other).

## Attempts

- Tried: more workers to "get under the wire faster." Failed — throttling is per-app-per-tenant, so adding workers just burns the shared budget faster and the cascade starts sooner. Concurrency is not a throttle workaround.
- Tried: the fixed `sleep(1)` retry. Failed — Graph's `Retry-After` on a directory throttle was frequently 20–60+ seconds; sleeping 1s and retrying consumed another throttle unit and *restarted* the window, which is exactly the cascade mechanism. Honoring `Retry-After` as a floor is the contract, not advisory `[verify-at-use]`.
- Tried (worked): three changes together — (1) honor `Retry-After` as the minimum wait with `max(Retry-After, 2**attempt) + jitter`; (2) collapse the N+1 with `$batch` (up to 20 sub-requests per round-trip — a sub-request can still be individually `429` even though the batch envelope returns `200`, so retry only the throttled sub-requests by reading their per-response `Retry-After`); (3) replace the full nightly re-read with a **delta query** so steady-state runs only pull what changed.

## Resolution

The cascade had two independent root causes and both had to be fixed. **Cause 1 — the retry was the throttler.** A retry that ignores `Retry-After` and fires inside the still-open throttle window is indistinguishable from the original over-call; it keeps the window open forever. Reading `Retry-After` and waiting at least that long lets the window actually close. **Cause 2 — the workload was N+1 and full-scan.** `$batch` cut the round-trips ~20x and a delta query cut steady-state volume to near-zero. Note `$batch` reduces *round-trips*, not *throttle-unit consumption* — it is not itself a throttle fix, but fewer round-trips plus correct backoff plus delta together took the job from "always cascading" to "completes in minutes with zero 429s in steady state."

**Action for the next engineer:** when a Graph job cascades into nonstop 429s, the first thing to check is whether the retry path honors `Retry-After` — a fixed `sleep(N)` retry *is* the cascade. Then check for an N+1 fan-out that `$batch` collapses, and a full re-read that a delta query replaces. Adding workers is never the fix.

**Sources (retrieved 2026-06-05):**
- Microsoft Graph throttling guidance — https://learn.microsoft.com/graph/throttling
- Combine delta query and change notifications to reduce throttling — https://learn.microsoft.com/graph/delta-query-overview#combine-delta-query-and-change-notifications

Throttle limits are volatile and per-resource — `[verify-at-use]`. Cross-reference: [`../best-practices/api-honor-throttling-and-retry-after.md`](../best-practices/api-honor-throttling-and-retry-after.md), [`../best-practices/api-batch-to-cut-round-trips.md`](../best-practices/api-batch-to-cut-round-trips.md), the [`throttling-backoff-handler`](../skills/throttling-backoff-handler/SKILL.md) skill, and [`api-query-decision-trees.md`](../knowledge/api-query-decision-trees.md).
