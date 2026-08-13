# Memory Engineering — Unit Economics

**Last verified:** 2026-08-06 · the formulas mirror [`memory_engineering_calc.py`](../scripts/memory_engineering_calc.py); every priced fact is supplied by you at run time, never baked in.

> **Re-verify before quoting.** Anthropic beta→GA transitions invalidate this file independently of its age; the 90-day sweep surfaces it on a date, it does not check it.

## The one-sentence version

**A memory system's cost lives on the write path, and every accuracy benchmark in the field is blind to it.** Accuracy tells you whether the system answers; cost per correct answer tells you whether it should exist.

## 1. Cost per correct answer — the spine

```
cost_per_correct = total_cost / (queries * accuracy)
```

`accuracy` is a fraction in (0, 1]. **Both factors in the denominator are guarded** in the calculator — that pairing, not a queries-only check, is what makes this expression safe.

Why this and not raw cost: comparing two systems on cost alone, when they differ in accuracy, is meaningless. The measured spread in the literature makes the point sharply — one system at **4,128 J per correct answer at 47.0% accuracy**, another at **185,873 J per correct answer at 27.7%**. A design that looks like "20% more accurate for twice the cost" can be "the same accuracy for forty times the cost per correct answer."

```
memory_engineering_calc.py cost-per-correct \
  --total-cost-a <float> --queries-a <int> --accuracy-a <0..1> [--system-name-a "<label>"] \
  [--total-cost-b <float> --queries-b <int> --accuracy-b <0..1> --system-name-b "<label>"]
```

System-B flags are all-or-nothing. This mode is **shared** with the eval skill and owned by neither: this file supplies the cost half, the golden set supplies the accuracy half, and neither number means anything without the other.

**Source for the measured figures:** arXiv 2606.06448, Table 3 — https://arxiv.org/html/2606.06448v1 (retrieved 2026-08-06).

## 2. Amortization — against a *named* baseline

```
n* = build_cost / (per_query_cost_without - per_query_cost_with)

months = n* / queries_per_month
days   = ceil(months * 30)
```

`n*` is the number of queries at which the build cost is repaid, rounded up. If the denominator is **≤ 0**, the memory system is more expensive per query than the baseline and there is **no break-even** — the calculator says so in a labelled branch and points you back at cost per correct answer, because at that point the only argument left for the memory system is accuracy.

```
memory_engineering_calc.py amortize \
  --build-cost <float> --per-query-cost-with <float> --per-query-cost-without <float> \
  --baseline {full-context-prefill|lexical-retrieval|stateless} [--queries-per-month <float>]
```

**`--baseline` is required and has no default.** This is the single most important design decision in the calculator, and it is not a formality:

| Baseline | What it means | Is it the same job? |
|---|---|---|
| `full-context-prefill` | Re-send the whole raw history every query (Paradigm I) | **Yes** — same answers, zero construction cost |
| `lexical-retrieval` | Deterministic top-*k*, e.g. BM25 or embedRAG (Paradigm II) | **Yes** — same job, cheap construction |
| `stateless` | Answer with no injected history at all | **No** — it cannot answer memory-dependent queries |

Against a genuinely stateless baseline a memory system's per-query cost is **strictly higher**, so the break-even degenerates to the constant "never amortizes." That number is arithmetically correct and analytically worthless, which is why `--baseline stateless` prints a boxed functional-non-equivalence warning **before** the number: the warning is a precondition on interpreting the figure, not a footnote to it.

### Worked example (non-degenerate)

```
memory_engineering_calc.py amortize \
  --build-cost 50.00 --per-query-cost-with 0.004 --per-query-cost-without 0.05 \
  --baseline full-context-prefill --queries-per-month 3000

n* = 50.00 / (0.05 - 0.004) = 50.00 / 0.046 ≈ 1087 queries
   ≈ 0.362 months ≈ 11 days
```

Eleven days is a *good* answer. If your honest inputs produce "never," you have learned something more valuable than a number.

## 3. Store growth — because nothing forgets by default

```
items(d)  = writes_per_day * min(d, ttl_days)        # unbounded when no TTL is set
kb(d)     = items(d) * avg_size_kb
cap_day   = ceil(cap_items / writes_per_day)        # cap_items = max_items, or max_kb / avg_size_kb
```

```
memory_engineering_calc.py store-growth --writes-per-day <float> --avg-size-kb <float> \
  [--ttl-days <float>] [--max-items <int>] [--max-kb <float>]
```

Output: footprint in items and KB at 30 / 90 / 365 days, and the calendar day a supplied cap is reached. **Every run with no TTL and no cap prints a fixed NOTE that nothing forgets by default** — the benchmark's own finding, and the reason an unbounded store is a decision nobody made.

Two things this model deliberately does not flatter:

- **Bytes are the tame axis.** Measured footprint varied about 9× across systems at 1M tokens; **construction token cost diverged far more sharply**, super-linearly for agentic paradigms, because each ingestion queries the growing store before writing. Project the growth *slope*, not the day-one footprint.
- **A cap is not a retention policy.** Hitting `max_items` on a Managed Agents store makes new writes **fail**; hitting the auto-memory index budget makes the overflow **silently disappear at load**. Same "cap", opposite failure mode. See [memory surfaces](memory-surfaces-2026.md).

## 4. Cache economics — the bill a memory design hides

```
invalidations = min(invalidations_per_turn * turns, turns)

breaking      = invalidations * prefix_tokens * W + (turns - invalidations) * prefix_tokens * R
stable        = prefix_tokens * W                 + (turns - 1)            * prefix_tokens * R

monthly_delta      = breaking - stable
effective_multiple = breaking / stable
```

`W` = `--cache-write-multiplier`, `R` = `--cache-read-multiplier`, both **required with no default**; `turns` = `--turns-per-month`. Results are in **cache-adjusted input tokens per month** — multiply by your model's current input price per token for currency. The tool ships no price, deliberately.

```
memory_engineering_calc.py cache-economics --prefix-tokens <float> \
  --cache-write-multiplier <float> --cache-read-multiplier <float> \
  --invalidations-per-N-turns <float> --turns-per-month <float>
```

`--invalidations-per-N-turns` is an **invalidation rate per turn** over the N turns you are modelling: `0.5` means every second turn breaks the cache, `1.0` means every turn does, `0` means none do. The script clamps the resulting count at `turns`. This file mirrors the shipped model; **where the two ever disagree, the script is the contract** — run `--help`.

One consequence worth designing around: **a write that lands ahead of the reused prefix invalidates everything after it.** Append memory at the *end* of the prompt, or pay this bill once per turn.

**The ceiling, computed rather than asserted.** With the multipliers published on 2026-08-06 — write 2× at a one-hour TTL, read 0.1× — a design that re-warms the entire prefix every turn instead of reading it pays up to **2.0 / 0.1 = 20×** on that prefix. That "20×" is **arithmetic on two documented multipliers, not a documented figure**, and it assumes a full prefix rewrite. The calculator computes the real multiple for your case from *your* inputs, which is why no vendor constant is baked into it. Multipliers and their retrieval date: [memory surfaces](memory-surfaces-2026.md).

## 5. Three documented places memory-adjacent work costs real money

Each of these is a vendor-documented cost, not an inference. All retrieved 2026-08-06.

| Mechanism | The cost | Source |
|---|---|---|
| **Context editing** | Clearing **invalidates the prompt cache** at the clearing point — hence the `clear_at_least` knob, described as helping "justify breaking prompt cache" | https://platform.claude.com/docs/en/build-with-claude/context-editing |
| **Compaction** | "requires an additional sampling step that contributes to rate limits and billing" — a model call, every time it fires | https://platform.claude.com/docs/en/build-with-claude/compaction |
| **Dreams** (consolidation) | Billed at standard API token rates; cost scales roughly linearly with the number of input sessions | https://platform.claude.com/docs/en/managed-agents/dreams |

The pattern: **every mechanism that makes context smaller costs something somewhere else.** Free compression does not exist.

## 6. The cost lives on the write path

The benchmark's finding, stated with its conditions: **construction energy exceeded the total query-phase energy across the benchmark's 300 queries** for LLM-mediated systems. **300 is that benchmark's fixed query count, not a measured crossover point** — no break-even was published, which is precisely why you compute your own with `amortize`.

The build wall-clock differences are what make this concrete on the same corpus: a lexical baseline finished construction in about 16 minutes; a consolidating fact store took ~3.9 h; a fully agentic system took ~14.4 h. That is the number nobody puts on the slide.

**Where each family spends:**

| Paradigm | Where the money goes |
|---|---|
| I — raw context | All of it per-query; grows with history; nothing to amortize |
| II — flat retrieval | Small one-off build; per-query cost is retrieval + a smaller prompt |
| III.a — structure-augmented | Big offline batch build; steady per-query cost afterwards |
| III.b — consolidating store | Per-event LLM call on the write path — a latency **and** cost tax on every turn |
| IV — agentic | Per-event, **plus** a read of the growing store before each write: the only family whose cost slope is super-linear |

**Source:** arXiv 2606.06448 — https://arxiv.org/html/2606.06448v1 (retrieved 2026-08-06).

## 7. The serving constraint

Three statements, in the order that matters:

1. **Prefill is O(n²)** in prompt length.
2. **KV-cached decode is O(n) per decoded token — linear, not quadratic.** The "quadratic per token" framing is wrong and a reader will catch it; the correction is C09 in [the corrections block](memory-engineering-paradigms.md).
3. **In production the binding constraint is usually neither.** It is **KV bytes resident in HBM**, which caps concurrency. A serving stack becomes KV-cache-bound before it becomes FLOP-bound, and throughput plateaus as the cache fills GPU memory.

`[unverified — training knowledge]` for statements 1 and 2: no source was fetched for attention complexity this session because it is textbook and uncontested; it follows from the definition of KV-cached autoregressive decoding. Statement 3 is verified — arXiv 2604.09852 reports vanilla vLLM becoming KV-cache-bound at high concurrency (https://arxiv.org/pdf/2604.09852, retrieved 2026-08-06).

**The engineering consequence for memory design:** shrinking the *prompt* buys you concurrency headroom, not just token price. That is the second, unbilled return on a memory system — and the one an accuracy benchmark will never show you.

## 8. Two golden rejection cases

Both were real defects in the design, and both are now the calculator's documented behaviour. They are here because a *silent wrong answer* is worse than a crash, and both of these used to be one or the other.

```
memory_engineering_calc.py cost-per-correct --total-cost-a 100 --queries-a 0 --accuracy-a 0.5
  → error: --queries-a > 0 ; exit 2
    (was a ZeroDivisionError and exit 1 — the one exit status this plugin's contract forbids)

memory_engineering_calc.py amortize --build-cost -50 --per-query-cost-with 0.004 \
  --per-query-cost-without 0.05 --baseline full-context-prefill
  → error: --build-cost >= 0 ; exit 2
    (was n* ≈ -1087, printed as a finite, actionable-looking break-even)
```

**The exit-code contract:** `0` on success, `2` on any validation failure, and **no exit 1 anywhere**. Every money guard is `>= 0`, never "any float" — a negative build cost produces a negative break-even that reads like a valid answer, which is the silent half and the worse of the two.

## 9. What the calculator will not do for you

- **It ships zero vendor constants.** No `default=` on any priced flag. One lookup per run buys staleness that is structurally impossible to hide.
- **It does not know your accuracy.** Cost per correct answer needs a golden set; without one you are computing cost per *answer*, which is a different and much less interesting number.
- **It does not rank systems.** Every published memory-system ranking is self- or competitor-reported. Run the bake-off on your own data — see [the corrections block and the landscape](memory-engineering-paradigms.md).
- **It does not price risk.** The cost of a poisoned or un-erasable memory is in [memory security and privacy](memory-security-and-privacy.md), and it is not a token count.
