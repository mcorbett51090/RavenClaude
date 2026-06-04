---
id: agent-harness-loop
title: "How the harness drives each turn"
category: "Platform model"
kind: ravenclaude-built
order: 8
summary: "Every agent turn runs a loop: assemble prompt → call model → run tools → feed results back → repeat until done. RavenClaude is the 'harness' layer wrapping that loop."
see_also: [command-review-tribunal, capability-banner, audit-gates]
node_links:
  D: command-review-tribunal
sources:
  - label: "RavenClaude orchestration model — ravenclaude-core/CLAUDE.md"
    url: "plugins/ravenclaude-core/CLAUDE.md"
  - label: "\"The Anatomy of an Agent Harness\" (Akshay Pachaar)"
    url: "https://x.com/_avichawla/status/2062082282878627946"
---

An LLM on its own is stateless — it forgets what it did three steps ago, tool calls fail silently, and the context window fills with noise. The **harness** is the software wrapping the model that fixes this: the orchestration loop, tools, memory, context management, guardrails, and verification. As the saying goes, *"if you're not the model, you're the harness."*

RavenClaude **is** a harness layer. It rides on Claude Code's (and Copilot CLI's) loop and adds the machinery: orchestrator-worker dispatch (the **Team Lead**), the **Structured Output Protocol** for parseable handoffs, memory in `CLAUDE.md`/`AGENTS.md` + run artifacts, the **Thing** tribunal as the guardrail, and `audit-gates.sh` + the definition-of-done gate as verification. The step-by-step view below walks one turn through that loop — press **Play** to watch each stage, or step through with the arrows.

A guiding principle the harness inherits: treat memory as a *hint* and verify against real state before acting. That's why a turn doesn't end at "looks done" — it ends when the verification gates say it's done.

```mermaid
flowchart TD
  U[Your goal] --> P[1 · Assemble prompt]
  P --> L[2 · Call the model]
  L --> C{3 · Tool calls?}
  C -->|yes| T[4 · Execute tools]
  T --> R[5 · Package results]
  R --> X[6 · Update context]
  X --> P
  C -->|no| D[Done · verified by gates]
  class P,L,C,T,R,X,D built
```

<!-- step: Assemble the prompt: system prompt + tool schemas + CLAUDE.md/AGENTS.md memory + history + your message. -->
```mermaid-step
flowchart LR
  A[Assemble prompt] --> B[Call model] --> C[Classify output] --> D[Execute tools] --> E[Package results] --> F[Update context] --> G[Loop / done]
  class A built
```

<!-- step: Call the model. RavenClaude's Team Lead may dispatch a focused specialist for this slice. -->
```mermaid-step
flowchart LR
  A[Assemble prompt] --> B[Call model] --> C[Classify output] --> D[Execute tools] --> E[Package results] --> F[Update context] --> G[Loop / done]
  class B built
```

<!-- step: Classify the output: tool calls → execute and loop; plain text with no tool call → the turn ends. -->
```mermaid-step
flowchart LR
  A[Assemble prompt] --> B[Call model] --> C[Classify output] --> D[Execute tools] --> E[Package results] --> F[Update context] --> G[Loop / done]
  class C built
```

<!-- step: Execute tools — the Thing tribunal gates each risky call (ALLOW / EDIT / DENY) before it runs. -->
```mermaid-step
flowchart LR
  A[Assemble prompt] --> B[Call model] --> C[Classify output] --> D[Execute tools] --> E[Package results] --> F[Update context] --> G[Loop / done]
  class D built
```

<!-- step: Package results as observations. Errors return as results so the model can self-correct, not crash. -->
```mermaid-step
flowchart LR
  A[Assemble prompt] --> B[Call model] --> C[Classify output] --> D[Execute tools] --> E[Package results] --> F[Update context] --> G[Loop / done]
  class E built
```

<!-- step: Update context; compact when it fills. Dispatched specialists return ~1–2k-token summaries, not raw output. -->
```mermaid-step
flowchart LR
  A[Assemble prompt] --> B[Call model] --> C[Classify output] --> D[Execute tools] --> E[Package results] --> F[Update context] --> G[Loop / done]
  class F built
```

<!-- step: Loop until done — then verification gates (audit-gates.sh, the DoD gate) confirm "done" really means done. -->
```mermaid-step
flowchart LR
  A[Assemble prompt] --> B[Call model] --> C[Classify output] --> D[Execute tools] --> E[Package results] --> F[Update context] --> G[Loop / done]
  class G built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  P[prompt] --> M[model] --> T[tools] --> P
  class P,M,T built
```
