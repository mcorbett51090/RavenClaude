---
name: context-window-engineering
description: "Decide what actually goes in the context window — static instructions vs just-in-time retrieval vs conversation history vs tools — with a per-section token budget and lost-in-the-middle-aware ordering. Reach for this when the window is bloating, quality is dropping as context grows, cost/latency is climbing, or you're unsure what to keep vs compress. Pairs with prompt-pattern-selection."
---

# Skill: Context-window engineering

The window is a **budget**, not a scratchpad. This skill decides what earns its
tokens and in what order.

## Step 0 — One opinion up front
**More context is not free, and past a point it hurts.** Cost and latency scale
with fill, and accuracy can *drop* (the lost-in-the-middle effect + dilution). If
quality falls as you add context, remove context.

## Step 1 — Classify every candidate
For each thing you're tempted to include, classify it (trace
[`../../knowledge/prompt-decision-trees.md`](../../knowledge/prompt-decision-trees.md) §3):
- **Needed every call** → static system context (instructions, schema, invariants,
  few-shot).
- **Query-dependent knowledge** → retrieve just-in-time (`ai-rag-engineering`),
  budgeted.
- **Conversation history** → keep recent verbatim; summarize/compress older turns.
- **Everything else** → probably doesn't belong.

## Step 2 — Budget tokens per section
Assign a token ceiling to each section (system, retrieved, history, tools, output
headroom). The sum must leave room for the response. Write the budget down.

## Step 3 — Order for the model, and for the cache
- **Lost-in-the-middle:** put the decisive material at the **start or end**, not
  buried in the middle.
- **Prompt caching:** put *stable* content first (system, schema, few-shot) so it
  caches; put *variable* content last. This is a cost and latency lever.

## Step 4 — Define eviction order
When the window approaches its limit, what gets dropped or compressed *first*?
(Usually: oldest history → least-relevant retrieved chunks → verbose examples.)
Make it a rule, not an accident.

## Step 5 — Hand off
- The **retrieval** that fills a query-dependent slot → `ai-rag-engineering`.
- The **model's window size / caching behavior** → `ai-coding-model-guidance` /
  `claude-api`.
- **Measuring** whether a context change helped → `prompt-reliability-engineer`.

## Output
A context-inclusion plan: each section classified, a per-section token budget,
the ordering (lost-in-the-middle + cache-aware), and the eviction order.
