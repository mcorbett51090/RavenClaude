---
id: subagents
title: "Subagents & orchestration"
category: "Foundations"
kind: platform-fact
difficulty: intermediate
order: 4
summary: "A lead agent can spawn focused subagents, each with its own clean context window, and get back a short summary — not the raw work. It's how big tasks stay inside finite context."
see_also: [context-window, agent-harness-loop, tool-use]
last_verified: 2026-06-05
refresh_when: "Claude Code changes the subagent dispatch model, the Task/Agent tool shape, or how subagent results return to the parent."
sources:
  - label: "Subagents — Claude Code"
    url: "https://code.claude.com/docs/en/sub-agents"
  - label: "Building agents with the Agent SDK"
    url: "https://code.claude.com/docs/en/agent-sdk"
---

A single agent doing a sprawling task hits two walls: its **context window fills** with the noise of exploration, and a long linear chain has no parallelism. **Subagents** solve both. The lead agent (the *orchestrator*) hands a self-contained slice of work to a **subagent** — a fresh agent with its **own clean context window**, its own tools, and a focused brief. The subagent does the legwork and returns a **short summary** to the lead. The raw files it read and dead-ends it explored never touch the lead's context.

This is the **orchestrator–worker** pattern, and the load-bearing idea is *information hiding*: the lead pays only for the conclusion, not the investigation. A research subagent might read forty files and reply with a two-paragraph answer — forty files' worth of tokens spent in a context the lead never has to carry.

What it's good at, and where it bites:

- **Fan-out.** Independent slices run in parallel — three subagents searching three areas at once, returning three summaries. Big wall-clock win when the slices don't depend on each other.
- **Focus.** A narrowly-scoped subagent with the right tools beats one giant agent juggling everything, the same way a specialist beats a generalist.
- **The summary is the seam — and the risk.** The lead sees *only* what the subagent reports back. A subagent that summarizes badly, or drops a detail the lead needed, silently loses that information. Briefs should say what to return, not just what to do.
- **Subagents don't share memory with each other.** Each is isolated by design, so coordination happens through the lead, not sideways between workers.

RavenClaude's Team Lead is exactly this pattern with named specialists; the command-review tribunal's parallel reviewer seats are another instance — several focused agents, one aggregated verdict.

```mermaid
flowchart TD
  U[Your goal] --> L[Lead agent · orchestrator]
  L --> A[Subagent A<br/>own context · own tools]
  L --> B[Subagent B<br/>own context · own tools]
  L --> C[Subagent C<br/>own context · own tools]
  A --> SA[short summary]
  B --> SB[short summary]
  C --> SC[short summary]
  SA --> L2[Lead integrates summaries]
  SB --> L2
  SC --> L2
  L2 --> OUT[Result · lead never carried the raw work]
  class L,L2,A,B,C fact
  class OUT built
```

```mermaid-mini
flowchart LR
  L[lead] --> S[subagents<br/>clean context] --> R[short summaries] --> L
  class L,S,R fact
```
