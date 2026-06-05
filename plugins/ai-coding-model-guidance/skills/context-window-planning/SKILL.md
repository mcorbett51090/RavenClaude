---
name: context-window-planning
description: "Estimate a coding task's context demand and match it to a model tier whose window is sufficient, without quoting specific token counts that churn monthly. Reach for this skill when the task involves large codebases, long conversation histories, or multi-file agentic runs where context overflow would produce silent truncation errors."
---

# Skill: Context Window Planning

Context window limits cause one of the most silent failures in AI coding tools: a request is truncated mid-input, the model completes it anyway, and the output is confidently wrong because half the code was never seen. This skill estimates demand, matches to a tier, and flags the overflow risk before it bites.

## The key principle: estimate relative demand, not absolute tokens

Specific context-window sizes change frequently and belong in the dated knowledge bank (`../../knowledge/cross-tool-model-lineup-2026.md`) with `[verify-at-use]` markers. This skill works with **relative demand tiers** that remain stable even as the specific numbers churn:

| Demand tier | Typical workload |
|---|---|
| Low | Single file or function; short chat turn; one-shot completion |
| Medium | 2-5 files; a PR diff; a focused refactor with context |
| High | Entire module or package; cross-repo project with many files |
| Very high | Full repo scan; long autonomous agent run; many-turn conversation with large file contents |

## Step 1 — Estimate the task's context demand

Walk through each input category and classify:

1. **Code payload** — how many files, LOC estimate, are imports/dependencies included?
2. **Conversation history** — is this a long multi-turn session, or a fresh request?
3. **Tool outputs** — does the agent run read test results, linting output, or API responses mid-run?
4. **Output space** — large generated artifacts (a full module, a test suite) consume output tokens that reduce the effective context.

Add up the categories and assign a demand tier (Low / Medium / High / Very High).

## Step 2 — Flag overflow-risk patterns

These patterns almost always exceed a medium-tier window and should be called out explicitly before the run:

- **Full-repo scans** — asking the agent to "review everything" or "find all usages" across a codebase
- **Long agentic runs** — an autonomous task that accumulates tool outputs over many steps
- **Very long diffs** — a PR diff exceeding several thousand lines
- **History-heavy sessions** — a chat conversation that has been running for hours with large file pastes

For each flagged pattern, recommend **chunking**: break the task into scoped sub-tasks that fit within a medium-demand window.

## Step 3 — Match demand tier to model tier

The model tier and the context window are independent axes, but they interact:

```
Low demand    → any tier works; optimize for cost/latency
Medium demand → balanced default tier; verify window in lineup [verify-at-use]
High demand   → frontier tier OR context-chunking strategy; verify window [verify-at-use]
Very high     → chunking is required regardless of model tier; no model currently covers all production codebases in a single call
```

**Do not recommend a frontier model purely for its window size when a chunking strategy on the balanced model would serve the task.** Chunking is almost always cheaper and produces more debuggable results.

## Step 4 — Verify before naming a specific SKU

After identifying the required tier, verify the current maximum window for that tier in the dated lineup before naming a model. Apply the `[verify-at-use]` marker to any specific window size quoted.

```
Report format:
  Task demand: [tier] — [1 sentence reason]
  Recommended model tier: [tier]
  Context strategy: [single-call | chunked into N sub-tasks]
  Verify window size: [verify-at-use — YYYY-MM] from [lineup source]
```

## Pitfalls

- Quoting a specific token limit without a retrieval date — limits change with model updates.
- Assuming the largest available model has an "unlimited" window — all current models have limits.
- Choosing a frontier model to avoid chunking when chunking produces better-scoped output anyway.
- Forgetting output tokens: a task that generates a large file consumes output space that reduces the effective input window.

## See also

- [`../../knowledge/cross-tool-model-lineup-2026.md`](../../knowledge/cross-tool-model-lineup-2026.md) — the dated lineup with `[verify-at-use]` window entries
- [`../../knowledge/ai-coding-decision-trees.md`](../../knowledge/ai-coding-decision-trees.md) — vendor-neutral task-tier tree
- [`../coding-agent-task-scoping/SKILL.md`](../coding-agent-task-scoping/SKILL.md) — companion skill for scoping autonomous runs
