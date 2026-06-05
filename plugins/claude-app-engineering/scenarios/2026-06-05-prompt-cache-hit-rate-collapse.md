---
scenario_id: 2026-06-05-prompt-cache-hit-rate-collapse
contributed_at: 2026-06-05
plugin: claude-app-engineering
product: prompt-caching
product_version: "unknown"
scope: likely-general
tags: [prompt-caching, cache-hit-rate, cost-blowout, prefix-invalidation, tool-defs, system-prompt]
confidence: high
reviewed: false
---

## Problem

A customer-support assistant had prompt caching configured — a large system prompt (product docs + policies, ~40K tokens) above a `cache_control` breakpoint — and the bill was still climbing roughly linearly with traffic. The team assumed caching "wasn't working" and considered ripping it out. The actual signal: `usage.cache_read_input_tokens` was **0** on essentially every request, while `cache_creation_input_tokens` was paid (the ~1.25× write premium) on *every* request. They were paying the cache-write surcharge on each call and never reading a single cached token — strictly worse than no caching at all.

## Constraints context

- Caching is a **prefix match**: any byte change anywhere before a breakpoint invalidates everything after it (render order `tools` → `system` → `messages`). `[verify-at-use]` against [`../knowledge/prompt-caching-playbook.md`](../knowledge/prompt-caching-playbook.md).
- The system prompt was assembled with an f-string that interpolated `Current date: {datetime.now()}` into the header — so the first bytes of the prefix differed on every request.
- A separate, subtler invalidator: the tool list was built with `tools=build_tools(user)` and the per-user tool set varied, and `json.dumps()` of the tool schemas ran without `sort_keys=True`, so key order wasn't deterministic. Tools render at position 0 — any churn there busts the whole cache.

## Attempts

- Tried: raising the cache TTL from 5m to 1h. Did nothing — the problem wasn't expiry, it was that no two requests shared a prefix to begin with, so the longer TTL just held an entry nobody ever re-read. (And the 1h write premium is 2× vs 1.25×, so it made the per-request surcharge *worse*.)
- Tried: adding a second `cache_control` breakpoint deeper in the prompt. Also nothing — a breakpoint can't cache a prefix that changes above it; markers don't fix a non-stable prefix.
- Tried (the move that worked): **diffed the rendered prompt bytes between two consecutive requests.** The `datetime.now()` in the system header and the unsorted/­per-user tool JSON jumped out immediately. Froze the system prompt (moved the date into a `messages` turn, after the breakpoint), made tool serialization deterministic (`sort_keys=True`) and the tool set stable, and confirmed `cache_read_input_tokens` jumped to ~40K on the second request.

## Resolution

**A zero `cache_read_input_tokens` across repeated same-shape requests is the diagnostic — not "caching is broken," but "a silent invalidator is mutating the prefix."** The fix is never more breakpoints or a longer TTL; it's making the prefix byte-stable.

1. **Verify with the usage fields, not vibes.** `cache_read_input_tokens` ≈ 0 over repeated requests with a "shared" prefix means the prefix isn't actually shared. `cache_creation_input_tokens` paid every request confirms you're eating the write premium for nothing.
2. **Freeze the system prompt.** No `datetime.now()` / `uuid4()` / per-user f-string interpolation above a breakpoint. Inject volatile context (date, session id, the user's question) *after* the last breakpoint — as `messages` content, or a mid-conversation `role:"system"` message where supported `[verify-at-use]`.
3. **Make tools deterministic and stable.** Tools render at position 0; serialize with sorted keys, and don't vary the tool set per user/request mid-session (that's the #1 cache killer — house opinion #1). Use tool *search* if the set genuinely must be dynamic — it appends rather than swaps, preserving the prefix.
4. **Right minimum prefix.** A prefix below the model's cacheable minimum silently won't cache (no error, `cache_creation_input_tokens: 0`). Confirm the prefix clears the minimum for the model in use `[verify-at-use]`.

The trap is that caching *looks* configured — there's a breakpoint, the code reads right — so the instinct is to distrust the feature. The actual fault is one volatile byte upstream of the breakpoint, and the usage fields point straight at it.

**Action for the next engineer:** before touching breakpoints or TTL, diff the rendered prompt bytes between two requests and read `cache_read_input_tokens`. If it's zero, hunt the silent invalidator (timestamp / UUID / unsorted JSON / per-user tool set) — that's the cause ~every time.

Cross-reference: the field-note complement to [`../best-practices/cache-the-static-prefix.md`](../best-practices/cache-the-static-prefix.md) and the audit checklist in [`../knowledge/prompt-caching-playbook.md`](../knowledge/prompt-caching-playbook.md). Cache *economics* (when 1h TTL pays off, pre-warming) → [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md). All pricing/minimums are dated — `[verify-at-use]`.
