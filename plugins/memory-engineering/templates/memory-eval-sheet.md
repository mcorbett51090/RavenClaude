# Memory Eval Sheet — &lt;system / change&gt; — &lt;date&gt;

> Prove the memory system earns its write path (§3 #8). Accuracy without cost is unfalsifiable; **`cost-per-correct` is shared with the cost lane and owned by neither.** Math from [`memory_engineering_calc.py`](../scripts/memory_engineering_calc.py) `cost-per-correct`.

## Golden set — with provenance

| Field | Value |
|---|---|
| Items | |
| Where each item came from | |
| Who judged it, and when | |
| Memory-dependent items (cannot be answered stateless) | |
| Contains user data or stored memory content? | **must be "no"** (§4) |

A golden set nobody can trace is a vendor benchmark with your logo on it.

## Judged failure modes — not just correctness

| Failure mode | Count | Notes |
|---|---|---|
| Stale fact (right once, wrong now) | | |
| Unresolved contradiction (two entries disagree) | | |
| Confabulated recall (remembered something never stored) | | |
| Poisoned recall (acted on an entry from untrusted input) | | |
| Over-retention (should have forgotten) | | |
| Amnesia (should have remembered) | | |

Aggregate accuracy hides all six. This table is the reason the sheet exists.

## The bake-off

| System | Total cost | Queries | Accuracy | **Cost per correct answer** |
|---|---|---|---|---|
| Baseline: &lt;named&gt; | | | | |
| Candidate: &lt;named&gt; | | | | |

```
memory_engineering_calc.py cost-per-correct \
  --total-cost-a <float> --queries-a <int> --accuracy-a <0..1> --system-name-a "<baseline>" \
  --total-cost-b <float> --queries-b <int> --accuracy-b <0..1> --system-name-b "<candidate>"
```

## Verdict

| Field | Value |
|---|---|
| Did the candidate beat the **named** baseline on cost per correct answer? | |
| Did it beat it on accuracy alone? | |
| If those two disagree, which decides — and why | |

**No published ranking is admissible here** (§3 #8). Every external figure carries a source URL and a retrieval date, or an `[unverified — training knowledge]` mark; volatile vendor facts are `[verify-at-use]` against [memory surfaces](../knowledge/memory-surfaces-2026.md).

**Sources:** &lt;URL — retrieval date&gt; for every external number.
