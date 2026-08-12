# Prove the no-memory baseline loses before you build memory.

**Status:** Absolute rule. **Constitution:** §3 #2, §4.

## Use when

The first time "we should add memory" is said out loud — and again before any migration from one paradigm to another.

## The rule

**Two baselines must lose on your own data before an LLM-mediated memory store is justified: the no-memory baseline and the lexical-retrieval baseline.** In the same suite that produced this plugin's economics, lexical BM25 retrieval was the most accurate *and* the cheapest system measured. A memory system that never beat a keyword index is a build cost with no return.

This is a **gate**, not a preference. It sits at the top of [Tree 1](../knowledge/memory-engineering-decision-trees.md) and nothing downstream is worth designing until it has been passed.

## Why it matters

The literature the field cites is contested in a way that flatters memory systems: the most-quoted multi-session conversation benchmark runs conversations comfortably inside a modern context window, so a long-context baseline with **no** memory system at all is a serious contender on it. Any guidance — including this plugin's — that does not make you seriously consider plain lexical retrieval first is selling something. Skipping the gate is how a team ends up maintaining an extraction pipeline that a `BM25` index would have beaten on both axes.

## How to apply

1. Write down the **queries the system must answer** before writing down the architecture. If none of them depend on state from a prior session, stop: the answer is no memory.
2. Stand up the **no-memory baseline** (full history in the prompt, or no injected history where that is honest) and measure it on your golden set.
3. Stand up the **lexical baseline** (deterministic top-*k*, BM25 or an embedding index with no LLM in the construction path) and measure it on the same set.
4. Only if both lose — on **accuracy and on cost per correct answer**, not accuracy alone — proceed to Paradigm III or IV.
5. Record the losing baselines, with their numbers, in the [memory design record](../templates/memory-design-record.md). A design record whose alternatives section is empty did not run this gate.

## The anti-pattern this prevents

The §4 failure mode: **building memory without first proving the no-memory and lexical-retrieval baselines lose.** Its usual disguise is a proposal that compares two memory systems to each other and never to the cheap thing neither of them beat.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) §3 #2 — the house opinion this rule encodes.
- [`../knowledge/memory-engineering-paradigms.md`](../knowledge/memory-engineering-paradigms.md) — the paradigms, the four axes, and the humbling baseline.
- [`../knowledge/memory-engineering-decision-trees.md`](../knowledge/memory-engineering-decision-trees.md) — Tree 1 puts this gate first by construction.
- [`../agents/memory-architect-lead.md`](../agents/memory-architect-lead.md) — the agent that runs the gate.
