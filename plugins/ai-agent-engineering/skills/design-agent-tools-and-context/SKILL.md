---
name: design-agent-tools-and-context
description: "Design the tools/functions an agent calls and the context/memory strategy that keeps it coherent — unambiguous tool names, typed parameters, examples-in-description, errors that teach recovery, a small-enough tool count, plus a context plan (what stays in-window, what gets summarized, what moves to external memory) and short-term-vs-long-term memory design under a per-turn token budget. Reach for this when the user says 'the agent keeps calling tools wrong', 'the context overflows', or 'the agent loses track on long runs'. Used by `agent-implementation-engineer` (primary)."
---

# Skill: design-agent-tools-and-context

> **Invoked by:** `agent-implementation-engineer` (primary). Also consulted by `agentic-systems-architect` when a design needs the tool surface and memory model sketched before the topology is finalized.
>
> **When to invoke:** "the agent calls the wrong tool / passes bad arguments"; "the context window overflows on long runs"; "the agent drifts / loses the thread"; "what should the agent remember between turns / between runs?"; "how many tools is too many?".
>
> **Output:** tool/function schemas (names, typed params, descriptions with examples, recovery-teaching errors), a context strategy (in-window vs summarized vs external), and a memory design (short-term vs long-term) under a stated per-turn token budget.

## Procedure

1. **Inventory the tools the agent actually needs.** List every action the agent must take on the world. Collapse near-duplicates. **Fewer tools is better** — a large tool set is the most common cause of wrong tool selection. If two tools are chosen wrongly for each other, merge or disambiguate them.
2. **Design each tool like an API for a capable-but-literal caller.**
   - **Name:** unambiguous and action-shaped (`get_order_by_id`, not `order`).
   - **Parameters:** typed, with required-vs-optional explicit; prefer enums over free text where the domain is closed.
   - **Description:** say what it does, when to use it (and when NOT to), and include **one concrete example call**.
   - **Errors teach recovery:** return actionable messages (`"start_date must be YYYY-MM-DD, got '3rd'"`), not `"invalid input"` — the model reads the error and retries.
   - **Blast radius:** mark read-only vs write; writes get a confirmation gate downstream.
3. **Plan the context window as a budget.** For each turn, decide what belongs **in-window** (the current task, recent tool results, the running plan), what gets **summarized/compacted** (older turns, long tool outputs), and what moves to **external memory/retrieval** (documents, prior runs, large state). Set a **per-turn token budget** and design to stay under it.
4. **Design memory in two tiers.** **Short-term** = a scratchpad/working state for the current task (plan, intermediate results), cleared when the task ends. **Long-term** = a store queried across runs (user facts, prior outcomes, learned preferences) — decide what gets written, when it's read, and how staleness is handled. Not every agent needs long-term memory; add it only when cross-run recall is required.
5. **Close the loop between tools and context.** Large tool outputs are a context-overflow source — return **summaries or IDs**, not raw blobs, and let the agent fetch detail on demand. Keep tool results structured so they compact cleanly.

## Output format

- **Tool schemas:** one per tool — name, typed params, description-with-example, error-recovery notes, read/write flag.
- **Context strategy:** in-window / summarized / external, with the per-turn token budget.
- **Memory design:** short-term scratchpad shape + (if needed) long-term store's write/read/staleness rules.
- **Volatile facts** (tool-call formats, context-window sizes, model IDs): dated + `[verify-at-use]`.

## Guardrails

- **Too many tools is a bug** — if the model can't reliably choose, the tool set is the problem, not the model.
- **An error that doesn't teach recovery wastes a loop iteration** — every error message is a chance to self-correct.
- **Never let a raw tool blob into the window** when a summary + fetch-on-demand would do.
