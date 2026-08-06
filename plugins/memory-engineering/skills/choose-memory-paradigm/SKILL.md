---
name: choose-memory-paradigm
description: "Decide whether to build a memory system at all, and if so which paradigm — raw context, flat retrieval, LLM-extraction or agentic — behind a mandatory baseline-first gate. Reach for this before any memory design work."
---

# Skill: Choose a memory paradigm

**Decision 1 of the six-decision spine — *what earns a write?*** The cheapest store is none, and the second cheapest is a keyword index. This skill exists to make both of them compete before anyone builds anything (§3 #2).

The order below is not a suggestion. Steps 2 and 3 are **stops**: if either is unmeasured, the answer to "which paradigm?" is *"you cannot know yet"* — not a paradigm. Traverse Tree 1 in [the decision trees](../../knowledge/memory-engineering-decision-trees.md) alongside this.

## Step 1 — Name the durable question

Write one sentence: **what must survive this session, and which later session reads it?** If you cannot name the reader, you are designing a log, not a memory system.

Then separate two things that get conflated constantly:

| You have | You need |
|---|---|
| A fact a later session must recall | **Memory** — this skill |
| A prompt that is too long *right now* | **Context pressure management** — see [map-memory-surface](../map-memory-surface/SKILL.md) |

Context editing and compaction shrink a live prompt. Neither is durable. Memory is what has to survive both.

## Step 2 — STOP. Prove the no-memory baseline loses

Run your real queries with **no injected history at all** and record accuracy and cost. This is the `stateless` baseline.

- **Never measured?** Stop here. Build the golden set first — [build-memory-eval](../build-memory-eval/SKILL.md) is the procedure.
- **No-memory is good enough?** Do not build memory. Write that finding down; it is the most valuable result this skill produces.
- **No-memory loses?** Continue — and carry the measured gap forward, because it is the only thing that will later justify the write path.

**Honest caveat on this baseline:** stateless is *not the same job*. It cannot answer a memory-dependent query at any accuracy. Use it to size the gap, never as the amortization baseline — the calculator prints a boxed warning for exactly this reason (§3 #1).

## Step 3 — STOP. Prove flat lexical retrieval loses

Run deterministic top-*k* retrieval over the same history — BM25 or an embedding index, no LLM in the construction path — and record accuracy and cost.

This step exists because of the single most uncomfortable result in the literature: **in the published benchmark suite, plain lexical retrieval scored the highest accuracy *and* the lowest cost per correct answer of every system measured**, LLM-mediated ones included. Conditions, figures and source: [the paradigms knowledge file](../../knowledge/memory-engineering-paradigms.md).

- **Flat retrieval wins?** Ship Paradigm II and stop. It amortizes almost immediately.
- **Flat retrieval loses?** Now — and only now — you have a memory problem. Continue to step 4.

Any memory proposal that skips this step is selling something, including this one.

## Step 4 — Classify along the four axes

The **four axes** and the **four paradigms** are different fours. Classify the candidate design on all four axes before naming a paradigm:

| Axis | The question | Why it decides cost |
|---|---|---|
| **Construction** | Is an LLM in the write path, and does it run per-event or in a batch? | This is where the money goes (§3 #1) |
| **Storage** | Flat rows, a vector index, a graph, or in-context blocks? | Sets the growth slope and the erasure residue |
| **Retrieval** | Deterministic top-*k*, or a model deciding what to fetch? | Sets per-query latency and variance |
| **Mutability** | Append-only, overwrite, or reconcile-on-write? | Decides who resolves contradictions, and when |

## Step 5 — Name the paradigm and the bill it pays

| Paradigm | What it does | The bill it pays |
|---|---|---|
| **I — raw context** | Prefill the full history at every query | Zero construction cost; per-query cost grows with the history |
| **II — flat retrieval** | No LLM in construction; deterministic top-*k* | Cheap build; amortizes almost immediately |
| **III.a — structure-augmented** | LLM-mediated extraction into a graph or index | Large **offline batch** indexing traffic |
| **III.b — consolidating fact store** | LLM-mediated extraction into a mutable fact store | Sequential **per-event** traffic on the write-loop critical path |
| **IV — agentic** | The model decides when to write, which tool, and whether the evidence suffices | Per-event traffic **plus** a read of the growing store before every write — the only family with a super-linear cost slope |

**The III.a / III.b split is load-bearing, not pedantry.** It predicts the *shape* of the write traffic, which is what decides whether your build is a nightly batch job or a latency tax on every single turn. Named examples per row: [the paradigms knowledge file](../../knowledge/memory-engineering-paradigms.md).

## Step 6 — Amortize against the baseline you just beat

Take the baseline that lost in step 2 or 3 and put a break-even number on the paradigm you chose. Hand off to [budget-memory-costs](../budget-memory-costs/SKILL.md), which drives [the calculator](../../scripts/memory_engineering_calc.py) `amortize` mode.

If there is **no break-even**, the only argument left is accuracy — and then the unit is **cost per correct answer**, which needs the accuracy half from [build-memory-eval](../build-memory-eval/SKILL.md).

## Step 7 — Record the decision, not the conversation

A paradigm chosen in chat is not a decision. Write down, in the [memory design record](../../templates/memory-design-record.md): **paradigm · the baseline that lost · the measured gap · break-even query volume · who decided · the date.** The next three skills all read from that record.

## Guardrails

- **Do not pick a paradigm from a leaderboard.** Every published memory-system ranking is self- or competitor-reported (§3 #8). Rank on your own data or do not rank.
- **Do not carry a benchmark number into a client deliverable without its conditions.** The measured results in this plugin come with a fixed query count, a fixed model, and a fixed corpus; strip those and the number becomes a claim it cannot support.
- Every external figure gets a source URL and a retrieval date, or an explicit unverified marker (§4).

## Output

A paradigm decision with both baselines measured and beaten, the four-axis classification, the bill that paradigm pays, and a break-even against a named baseline. Traverse Tree 1 in [the decision trees](../../knowledge/memory-engineering-decision-trees.md).
