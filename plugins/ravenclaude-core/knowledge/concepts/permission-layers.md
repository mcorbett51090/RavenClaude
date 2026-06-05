---
id: permission-layers
title: "Permission layers & precedence"
category: "Platform model"
kind: platform-fact
difficulty: intermediate
order: 10
summary: "Four settings files merge — a deny in ANY layer wins, and you can't override it down from a later layer."
see_also: [hook-lifecycle, command-review-tribunal]
widget: permission-resolver
try_it:
  label: "Set your own layers on the Settings tab"
  href: "#/settings"
last_verified: 2026-05-25
refresh_when: "Anthropic adds/removes a settings layer, or changes the cross-layer merge rule."
sources:
  - label: "Configure permissions"
    url: "https://code.claude.com/docs/en/permissions"
  - label: "Claude Code settings"
    url: "https://code.claude.com/docs/en/settings"
---

Permission rules live under `permissions.allow`, `permissions.ask`, and `permissions.deny` in any of the settings files. Each rule is either a bare tool name (`Bash`, `WebSearch`) or a tool plus a specifier (`Bash(git status:*)`, `Read(/etc/**)`).

**Within one file**, rules evaluate `deny → ask → allow` — the first match wins, so deny always beats ask and ask always beats allow.

**Across files**, the layers **merge** rather than override: a deny in *any* layer blocks the action regardless of allow rules elsewhere. You **cannot override down** — if your user-level settings deny `Bash(rm *)`, no project-level allow re-enables it. That's the safe behavior, but it surprises people who expect a later layer to win.

The most-surprising rule: a **bare-tool deny** (`deny: ["Bash"]`) removes the tool from Claude's context entirely — Claude never sees it. A **scoped deny** (`Bash(rm *)`) keeps the tool and blocks only matching calls.

```mermaid
flowchart TD
  CALL[Tool call] --> MERGE[Merge rules across all layers]
  MERGE --> D{Any layer<br/>DENY match?}
  D -- yes --> BLOCK[Blocked — cannot be overridden]
  D -- no --> A{Any layer<br/>ASK match?}
  A -- yes --> PROMPT[Prompt the user]
  A -- no --> AL{Any layer<br/>ALLOW match?}
  AL -- yes --> RUN[Run without asking]
  AL -- no --> PROMPT
  class BLOCK built
  class D,A,AL fact
```

<!-- step: Rules live in four settings files under permissions.allow / ask / deny. -->
```mermaid-step
flowchart LR
  N1[Rules in 4 files] --> N2[Merge layers] --> N3[Deny wins] --> N4[No override down] --> N5[Bare vs scoped]
  class N1 built
```

<!-- step: Across files the layers MERGE rather than override. -->
```mermaid-step
flowchart LR
  N1[Rules in 4 files] --> N2[Merge layers] --> N3[Deny wins] --> N4[No override down] --> N5[Bare vs scoped]
  class N2 built
```

<!-- step: A deny in ANY layer wins — and you can't override it down from a later layer. -->
```mermaid-step
flowchart LR
  N1[Rules in 4 files] --> N2[Merge layers] --> N3[Deny wins] --> N4[No override down] --> N5[Bare vs scoped]
  class N3 built
```

<!-- step: Within one file the order is deny then ask then allow; first match wins. -->
```mermaid-step
flowchart LR
  N1[Rules in 4 files] --> N2[Merge layers] --> N3[Deny wins] --> N4[No override down] --> N5[Bare vs scoped]
  class N4 built
```

<!-- step: A bare-tool deny hides the tool entirely; a scoped deny blocks only matching calls. -->
```mermaid-step
flowchart LR
  N1[Rules in 4 files] --> N2[Merge layers] --> N3[Deny wins] --> N4[No override down] --> N5[Bare vs scoped]
  class N5 built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  C[Call] --> D{deny<br/>anywhere?}
  D -- yes --> X[Blocked]
  D -- no --> OK[allow / ask]
  class X built
```
