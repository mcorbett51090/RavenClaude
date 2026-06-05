---
id: permission-modes
title: "Permission modes"
category: "Platform model"
kind: platform-fact
difficulty: basic
order: 15
summary: "Six modes from default to bypassPermissions — but bypass still prompts on rm -rf /, and auto silently drops broad allow rules."
see_also: [permission-layers, hook-lifecycle]
last_verified: 2026-05-25
refresh_when: "Anthropic adds/renames a permission mode or changes auto-mode's drop-broad-rules behavior."
sources:
  - label: "Choose a permission mode"
    url: "https://code.claude.com/docs/en/permission-modes"
  - label: "Configure permissions"
    url: "https://code.claude.com/docs/en/permissions"
---

The permission **mode** sets the baseline posture on top of your allow/ask/deny rules. There are six: `default` (prompt when uncertain), `acceptEdits` (auto-approve common filesystem Bash inside the cwd), `plan` (read/think only — no writes), `auto` (research-preview classifier-driven autonomy), `dontAsk` (auto-deny anything not explicitly allowed — handy for CI), and `bypassPermissions` (skips most checks).

Two surprises bite. **`bypassPermissions` is not a total kill-switch:** `rm -rf /` and `rm -rf ~` *still* prompt as a circuit breaker, and a `PreToolUse` hook `deny` still blocks. **`auto` mode silently drops broad allow rules** — `Bash(*)`, wildcarded interpreters, `npm run *`, and all `Agent` allows are dropped while it's active (they restore when you leave), and `defaultMode: "auto"` is *ignored* in project settings — it must live in user-level `~/.claude/settings.json`.

```mermaid
flowchart TD
  M[Permission mode] --> DEF[default · prompt on uncertain]
  M --> AE[acceptEdits · auto-approve cwd file ops]
  M --> AUTO[auto · classifier autonomy<br/>drops broad allow rules]
  M --> BP[bypassPermissions · skips most checks]
  BP --> CB{rm -rf / or ~ ?}
  CB -- yes --> STOP[still prompts · circuit breaker]
  CB -- no --> RUN[runs]
  class M,DEF,AE,AUTO,BP fact
  class STOP built
```

<!-- step: The mode sets the baseline posture on top of your allow/ask/deny rules. -->
```mermaid-step
flowchart LR
  N1[Mode baseline] --> N2[Default modes] --> N3[Auto drops allows] --> N4[DontAsk] --> N5[Bypass still blocks]
  class N1 built
```

<!-- step: default prompts on uncertain; acceptEdits auto-approves cwd file ops; plan is read-only. -->
```mermaid-step
flowchart LR
  N1[Mode baseline] --> N2[Default modes] --> N3[Auto drops allows] --> N4[DontAsk] --> N5[Bypass still blocks]
  class N2 built
```

<!-- step: auto is classifier autonomy — but it silently DROPS broad allow rules like Bash star. -->
```mermaid-step
flowchart LR
  N1[Mode baseline] --> N2[Default modes] --> N3[Auto drops allows] --> N4[DontAsk] --> N5[Bypass still blocks]
  class N3 built
```

<!-- step: dontAsk auto-denies anything not explicitly allowed (handy for CI). -->
```mermaid-step
flowchart LR
  N1[Mode baseline] --> N2[Default modes] --> N3[Auto drops allows] --> N4[DontAsk] --> N5[Bypass still blocks]
  class N4 built
```

<!-- step: bypassPermissions skips most checks — but rm -rf / still prompts and a hook deny still blocks. -->
```mermaid-step
flowchart LR
  N1[Mode baseline] --> N2[Default modes] --> N3[Auto drops allows] --> N4[DontAsk] --> N5[Bypass still blocks]
  class N5 built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  D[default] --> A[acceptEdits] --> AU[auto] --> B[bypass]
  B --> S[rm -rf / still blocks]
  class S built
```
