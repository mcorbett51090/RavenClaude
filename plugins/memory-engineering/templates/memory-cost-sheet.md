# Memory Cost Sheet — &lt;system / period&gt; — &lt;date&gt;

> The write path priced before the read path (§3 #1). Math from [`memory_engineering_calc.py`](../scripts/memory_engineering_calc.py) `amortize` / `store-growth` / `cache-economics`. The tool ships **no vendor constants** — every priced input below is yours, read fresh.

## 1. Build cost (the write path)

| Field | Value |
|---|---|
| One-off construction cost | |
| Construction wall-clock | |
| Ongoing per-event write cost (extraction / consolidation calls) | |
| Does each ingestion **read** the store before writing? | if yes, the cost slope is super-linear |

## 2. Break-even against a **named** baseline

**`--baseline` is required and has no default.** `full-context-prefill` and `lexical-retrieval` do the same job; `stateless` does **not** and the tool warns before it prints a number.

| Field | Value |
|---|---|
| Named baseline | |
| Per-query cost **with** memory | |
| Per-query cost **without** (the baseline) | |
| `n*` — break-even query volume | |
| Queries per month → months / days | |

```
memory_engineering_calc.py amortize \
  --build-cost <float> --per-query-cost-with <float> --per-query-cost-without <float> \
  --baseline {full-context-prefill|lexical-retrieval|stateless} [--queries-per-month <float>]
```

If the denominator is ≤ 0 there is **no break-even at any volume**. Record that outcome verbatim; the only argument left is accuracy, so go to the [eval sheet](memory-eval-sheet.md).

## 3. Cache-invalidation bill

| Field | Value |
|---|---|
| Prefix tokens | |
| Cache write multiplier / read multiplier **(read fresh, dated)** | `[verify-at-use]` — [memory surfaces](../knowledge/memory-surfaces-2026.md) |
| Invalidations per turn | |
| Turns per month | |
| Monthly delta, breaking vs stable prefix | |
| **Computed** effective multiple | |

A write that lands ahead of the reused prefix invalidates everything after it. Append memory at the end of the prompt, or pay this every turn.

## 4. Growth projection (§3 #3)

| Horizon | Items | KB |
|---|---|---|
| 30 days | | |
| 90 days | | |
| 365 days | | |

| Field | Value |
|---|---|
| TTL / cap in force | |
| Calendar day the cap is reached | |
| Behaviour **at** the cap (hard failure vs silent truncation) | |
| Retention owner (role) | |

## 5. Verdict

| Field | Value |
|---|---|
| Does this system ever pay for itself against the named baseline? | |
| What would have to change for the answer to flip? | |

**Sources:** &lt;URL — retrieval date&gt; for every external figure (§4 cite-or-mark rule).
