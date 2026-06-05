---
id: context-window
title: "The context window"
category: "Foundations"
kind: platform-fact
order: 3
summary: "Everything the model 'knows' this turn is the text in its context window — system prompt, tools, history, files. It's finite, it fills up, and when it's full the harness compacts."
see_also: [agent-harness-loop, tool-use, session-start-context]
last_verified: 2026-06-05
refresh_when: "Frontier context-window sizes change materially, or Claude Code changes its compaction / auto-compact behavior."
sources:
  - label: "Context windows — Claude API"
    url: "https://docs.claude.com/en/docs/build-with-claude/context-windows"
  - label: "Manage context — Claude Code"
    url: "https://code.claude.com/docs/en/costs"
---

A model has **no memory between turns.** Everything it "knows" while answering is whatever text sits in its **context window** right now: the system prompt, the tool schemas, the project instructions (`CLAUDE.md` / `AGENTS.md`), the conversation so far, and the contents of any file or tool result that's been pulled in. Nothing outside that window exists to the model — if it isn't in context, the model can't see it, no matter how relevant.

The window is **finite** (measured in tokens — roughly ¾ of a word each). Two consequences follow:

- **It fills up.** Long sessions, big files, and chatty tool output all consume the budget. As it fills, the *effective* room for reasoning shrinks, and far-back details get crowded out — the model can genuinely "forget" what happened early in a long session.
- **When it's nearly full, the harness compacts.** Claude Code summarizes the older part of the conversation into a compact recap and continues with that plus the recent turns. The work isn't lost, but it's now a *summary* — which is why durable facts belong in `CLAUDE.md` or committed files, not just in chat.

The practical model: treat context like a **desk, not a filing cabinet.** Things on the desk are usable now; everything else has to be fetched back on (a tool call, a file read) before the model can use it — and fetching it costs space. Good agent design keeps the desk clear: focused tool results, subagents that return short summaries instead of raw dumps, and important state written somewhere persistent.

This is also why a **SessionStart** context injection (the orientation banner) is deliberately kept small — it rides in *every* session's window, so it's a recurring tax on the budget.

```mermaid
flowchart TD
  subgraph W[Context window · finite token budget]
    S[System prompt + tool schemas]
    P[Project memory · CLAUDE.md / AGENTS.md]
    H[Conversation history]
    F[Pulled-in files + tool results]
  end
  W --> M[Model reasons over ONLY what's in the window]
  H --> FULL{Near the limit?}
  FULL -- yes --> C[Harness compacts older turns to a summary]
  C --> W
  FULL -- no --> M
  class S,P,H,F,M fact
  class C built
```

```mermaid-mini
flowchart LR
  C[context window] --> L{full?}
  L -- yes --> S[compact to summary]
  L -- no --> R[model reasons]
  class C,R fact
```
