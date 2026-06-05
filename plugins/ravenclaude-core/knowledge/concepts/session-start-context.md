---
id: session-start-context
title: "SessionStart context injection"
category: "Platform model"
kind: platform-fact
difficulty: intermediate
order: 22
summary: "SessionStart hooks inject additionalContext into every session — additive only; they can't block or delay startup and are capped near 10k chars."
see_also: [hook-lifecycle, capability-banner]
node_links:
  H: hook-lifecycle
last_verified: 2026-05-26
refresh_when: "Anthropic changes the SessionStart additionalContext field, its size cap, or matcher set."
sources:
  - label: "Hooks reference"
    url: "https://code.claude.com/docs/en/hooks"
---

`PreToolUse` hooks gate tool calls; **`SessionStart` hooks can't gate anything.** Their job is to add text to the session via a different field — `hookSpecificOutput.additionalContext` — and nothing more. The output is read **only on exit 0**; a non-zero exit is a non-blocking error and the session still starts. A SessionStart hook can never block or delay a session; its output is purely additive.

Rules that bite: `additionalContext` is **capped near ~10,000 characters** (it's injected every session, so it's a recurring token cost — keep it tight); **multiple SessionStart hooks run in parallel and their outputs are concatenated**; the optional `matcher` is `startup` / `resume` / `clear` / `compact`; and like other hooks it **fails open** on timeout. This is the mechanism RavenClaude's capability banner rides on.

```mermaid
flowchart TD
  S[Session starts] --> H[SessionStart hooks run in parallel]
  H --> EX{exit 0?}
  EX -- no --> SKIP[Non-blocking error · session starts anyway]
  EX -- yes --> ADD[additionalContext concatenated into context]
  ADD --> CAP[~10k char cap · injected every session]
  CAP --> GO[Session proceeds · never blocked]
  SKIP --> GO
  class S,H,EX,SKIP,GO fact
  class ADD,CAP built
```

<!-- step: A session starts; SessionStart hooks run in parallel. -->
```mermaid-step
flowchart LR
  N1[Session starts] --> N2[Hooks parallel] --> N3[Exit 0 only] --> N4[Context added] --> N5[10k cap]
  class N1 built
```

<!-- step: They can't gate anything — output is read only on exit 0. -->
```mermaid-step
flowchart LR
  N1[Session starts] --> N2[Hooks parallel] --> N3[Exit 0 only] --> N4[Context added] --> N5[10k cap]
  class N2 built
```

<!-- step: A non-zero exit is a non-blocking error; the session starts anyway. -->
```mermaid-step
flowchart LR
  N1[Session starts] --> N2[Hooks parallel] --> N3[Exit 0 only] --> N4[Context added] --> N5[10k cap]
  class N3 built
```

<!-- step: Each hook's additionalContext is concatenated into the session context. -->
```mermaid-step
flowchart LR
  N1[Session starts] --> N2[Hooks parallel] --> N3[Exit 0 only] --> N4[Context added] --> N5[10k cap]
  class N4 built
```

<!-- step: Capped near 10k chars (injected every session); fails open on timeout. -->
```mermaid-step
flowchart LR
  N1[Session starts] --> N2[Hooks parallel] --> N3[Exit 0 only] --> N4[Context added] --> N5[10k cap]
  class N5 built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  S[SessionStart] --> A[additionalContext]
  A --> C[added to context<br/>· can't block]
  class A built
```
