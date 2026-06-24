# Offline & Conflict Test Plan — <feature>

> Output template for verifying a collaborative feature. The happy-path demo proves nothing; the bugs live in concurrency, partition, and reconnect.

## Feature under test
- **Document type:** _____ · **Merge model:** _____
- **Prepared:** 2026-__-__

## Scenarios (each: setup → action → assert convergence AND intention)

| # | Scenario | Setup | Assert |
|---|---|---|---|
| 1 | Concurrent same-field edit | 2 clients edit field X simultaneously | converges; result preserves both intentions |
| 2 | Concurrent insert + delete at a spot | client A inserts after el, client B deletes el | converges; no dangling/lost insert |
| 3 | Network partition + heal | split, both edit, reconnect | reconverges; no lost/dup ops |
| 4 | Offline → reconnect | client offline edits, comes back | delta merge, NOT replay-as-new |
| 5 | Presence expiry | client disconnects | cursor/here clears on timeout |
| 6 | Long-lived growth | many deletes over time | size bounded by compaction/GC |
| 7 | Out-of-order delivery | deliver ops reordered | idempotent; converges |

## Property checks (where claimed)
- [ ] Op application idempotent (re-delivery harmless)
- [ ] Concurrent op pairs commute to the same state
- [ ] GC never collects history a lagging replica still needs

## Load (seam → performance-engineering)
- [ ] Behavior under reconnect storm / many rooms

---
_Plus the ravenclaude-core Structured Output block._
