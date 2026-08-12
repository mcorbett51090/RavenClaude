---
name: budget-memory-costs
description: "Put a defensible number on a memory system — break-even against a named baseline, growth and caps, cache-invalidation cost, and cost per correct answer. Reach for this on any pay-for-itself question."
---

# Skill: Budget memory costs

**Decision 5 of the six-decision spine — *what does it cost, and when does it amortize?*** A memory system's cost lives on the **write path**, and every accuracy benchmark in the field is blind to it (§3 #1).

This skill drives [`memory_engineering_calc.py`](../../scripts/memory_engineering_calc.py). The formulas are mirrored in [memory economics](../../knowledge/memory-engineering-economics.md); **where the two ever disagree, the script is the contract** — run `--help`.

> **`cost-per-correct` is shared with [build-memory-eval](../build-memory-eval/SKILL.md) and owned by neither skill.** This one supplies the **cost** half; that one supplies the **accuracy** half. Neither number means anything alone, and neither skill is the mode's home. Do not go looking for it somewhere else.

## The calculator's actual interface

Four modes. **Zero baked-in vendor constants** — every priced fact is a required flag with no default, so the tool can never quietly become a stale data source. Exit codes are a contract: **`0` success, `2` any validation failure or argparse usage error, and no exit `1` anywhere.**

| Mode | Required flags | Optional flags |
|---|---|---|
| **`cost-per-correct`** (the spine) | `--total-cost-a` `--queries-a` `--accuracy-a` | `--system-name-a`; and the all-or-nothing set `--total-cost-b` `--queries-b` `--accuracy-b` `--system-name-b` |
| `amortize` | `--build-cost` `--per-query-cost-with` `--per-query-cost-without` `--baseline` | `--queries-per-month` |
| `store-growth` | `--writes-per-day` `--avg-size-kb` | `--ttl-days` `--max-items` `--max-kb` |
| `cache-economics` | `--prefix-tokens` `--cache-write-multiplier` `--cache-read-multiplier` `--invalidations-per-N-turns` `--turns-per-month` | — |

`--baseline` takes exactly one of `full-context-prefill`, `lexical-retrieval`, `stateless`. **It is required and has no default.**

## Step 1 — Name the baseline. This is not a formality

An amortization figure is uninterpretable until you say what it is measured against, so the tool refuses to run without it (missing `--baseline` exits `2` at the parser).

| Baseline | What it means | Same job? |
|---|---|---|
| `full-context-prefill` | Re-send the whole raw history every query (Paradigm I) | **Yes** — same answers, zero construction cost |
| `lexical-retrieval` | Deterministic top-*k*, e.g. BM25 or an embedding index (Paradigm II) | **Yes** — same job, cheap construction |
| `stateless` | Answer with no injected history at all | **No** — it cannot answer a memory-dependent query at any accuracy |

Against a genuinely stateless baseline the break-even is arithmetically correct and analytically worthless, which is why `--baseline stateless` prints a boxed **FUNCTIONAL NON-EQUIVALENCE** panel **before** the number. The warning is a precondition on reading the figure, not a footnote to it.

## Step 2 — Amortize

```
memory_engineering_calc.py amortize \
  --build-cost 50.00 --per-query-cost-with 0.004 --per-query-cost-without 0.05 \
  --baseline full-context-prefill --queries-per-month 3000
```

Observed: `Break-even : 1,087 queries at baseline=full-context-prefill`, then `0.362 months (~11 days)`. Eleven days is a *good* answer.

Flip the two per-query costs and the same command prints the labelled branch instead:

```
>> NEVER AMORTIZES at baseline=lexical-retrieval
```

That is not a failure — it is the finding. When there is no break-even, the only argument left for the memory system is **accuracy**, and the unit becomes cost per correct answer (step 5).

**Fold re-construction into `--build-cost`.** The mode prices the build once. A store that is re-embedded, rewritten or re-consolidated pays construction again, and omitting that flatters the memory path.

## Step 3 — Project growth and caps

```
memory_engineering_calc.py store-growth --writes-per-day 40 --avg-size-kb 2.5 \
  --ttl-days 90 --max-items 2000
```

Observed: day 30 / 90 / 365 footprints, `Steady state : 3,600 items / 9,000 KB (TTL holds it flat)`, and `--max-items cap : reached on day 50`. With no TTL and no cap the same mode prints the fixed *nothing forgets by default* NOTE — an unbounded store is a decision nobody made (§3 #3). Policy design is [design-forgetting-policy](../design-forgetting-policy/SKILL.md); this step only sizes it.

## Step 4 — Price the cache-invalidation bill

The bill a memory design hides. A write that lands **ahead** of the reused prefix invalidates everything after it, so the design pays a re-warm every turn instead of a cheap cached read.

```
memory_engineering_calc.py cache-economics --prefix-tokens 30000 \
  --cache-write-multiplier 1.25 --cache-read-multiplier 0.1 \
  --invalidations-per-N-turns 1 --turns-per-month 4000
```

Observed with those inputs: `Monthly delta : 137,965,500 cache-adjusted input tokens/month` and `Effective multiple: 12.46x (COMPUTED from your inputs, not quoted as a constant)`.

Three things to get right:

- **The multipliers are inputs, never defaults.** Read today's published values, with their date, from [memory surfaces (2026)](../../knowledge/memory-surfaces-2026.md) and pass them in. The multiplier that applies depends on the cache TTL you actually configured.
- **`--invalidations-per-N-turns` is a rate per turn**, not a count: `1` = every turn breaks the prefix, `0.1` = one turn in ten, `0` = never. The script clamps the resulting count at the turn count.
- **Results are cache-adjusted input tokens, not currency.** Multiply by your model's current input price per token. The tool ships no price, deliberately.

**The design fix is usually free:** append memory at the **end** of the prompt so the stable prefix stays stable.

## Step 5 — Cost per correct answer — the spine

```
memory_engineering_calc.py cost-per-correct \
  --total-cost-a 240.00 --queries-a 2000 --accuracy-a 0.62 --system-name-a "memory build" \
  --total-cost-b 90.00 --queries-b 2000 --accuracy-b 0.20 --system-name-b "lexical baseline"
```

Observed: `memory build : $0.193548 per correct answer` against `lexical baseline : $0.225`, then

```
>> NOTE: the raw cost-per-query ranking DISAGREES with this one.
```

**That NOTE is the entire point of the mode.** On raw cost per query the lexical baseline is less than half the price; on cost per *correct answer* it loses. Comparing cost across systems with different accuracy is meaningless, and a design that looks like "a little more accurate for twice the money" can be the cheaper system once accuracy is priced in.

Both denominator factors — queries **and** accuracy — are guarded in the script; that pairing, not a queries-only check, is what makes the expression safe.

Supply only the A-side and the tool says so rather than pretending: *"one system only. A cost-per-correct figure is a comparison unit."* **You cannot run this mode without an accuracy number, and an accuracy number needs a golden set** — that is [build-memory-eval](../build-memory-eval/SKILL.md), and it is a hard dependency, not a nice-to-have.

## Step 6 — Read the guards as documentation

Every validation failure prints its violated constraint to stderr and exits `2`. Two of them are documented golden rejection cases because each used to be a *silently wrong* answer:

```
memory_engineering_calc.py cost-per-correct --total-cost-a 100 --queries-a 0 --accuracy-a 0.5
  → error: --queries-a > 0 ; exit 2

memory_engineering_calc.py amortize --build-cost -50 --per-query-cost-with 0.004 \
  --per-query-cost-without 0.05 --baseline full-context-prefill
  → error: --build-cost >= 0 ; exit 2
```

Both reproduce verbatim. Every money guard is `>= 0`, never "any float" — a negative build cost produces a negative break-even that reads like a valid, actionable answer, and a plausible wrong number is worse than a crash.

## Step 7 — Name the costs the calculator cannot see

Add these to the write-up by hand, because none of them is a token count:

- **Build wall-clock.** On one published corpus, a lexical baseline finished construction in about 16 minutes while heavier systems took hours. That is the number nobody puts on the slide.
- **Every mechanism that makes context smaller costs something somewhere else.** Clearing content from a prompt invalidates the cache at the clearing point; conversation summarization requires an extra sampling pass that is billed; an offline consolidation job is billed at standard token rates and scales with input volume. Free compression does not exist — sources in [memory economics](../../knowledge/memory-engineering-economics.md).
- **The unbilled return.** Shrinking the prompt buys concurrency headroom, not just token price, because a serving stack becomes bound by cached key/value bytes resident in device memory before it becomes compute-bound. An accuracy benchmark will never show you that.
- **Risk is not priced here at all.** The cost of a poisoned or un-erasable memory lives in [memory security and privacy](../../knowledge/memory-security-and-privacy.md).

## Guardrails

- Mark every price, multiplier and cap you did not verify today, and carry its retrieval date (§4).
- Never present a calculator output as a quoted price. It is arithmetic on **your** inputs; the disclaimer prints on every run for a reason.
- No user data and no memory-store contents in any input or output.

## Output

A break-even against a named baseline, a growth projection with the cap day, a cache-invalidation delta, and a cost per correct answer paired with the accuracy source that produced it — each with owner, date and expected movement. The sheet for this is [`memory-cost-sheet.md`](../../templates/memory-cost-sheet.md).
