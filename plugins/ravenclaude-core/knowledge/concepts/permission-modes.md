---
id: permission-modes
title: "Permission modes"
category: "Platform model"
kind: platform-fact
order: 15
summary: "Six modes from default to bypassPermissions — but bypass still prompts on rm -rf /, and auto silently drops broad allow rules."
see_also: [permission-layers, hook-lifecycle]
last_verified: 2026-10-20
refresh_when: "Anthropic adds/renames a permission mode or changes auto-mode's drop-broad-rules behavior."
sources:
  - label: "Choose a permission mode"
    url: "https://code.claude.com/docs/en/permission-modes"
  - label: "Configure permissions"
    url: "https://code.claude.com/docs/en/permissions"
---

The permission **mode** sets the baseline posture on top of your allow/ask/deny rules. There are six: `default` (shown as **Manual** — asks before most edits, shell commands, and network access), `acceptEdits` (auto-approve file edits and common filesystem Bash inside the working directory), `plan` (research and propose — Claude doesn't edit your source until you approve the plan), `auto` (a classifier model reviews actions instead of you; the built-in starting mode for interactive terminal and VS Code sessions since v2.1.283), `dontAsk` (auto-deny every call that would otherwise prompt — handy for CI), and `bypassPermissions` (skips most checks).

Two surprises bite. **`bypassPermissions` is not a total kill-switch:** `rm -rf /` and `rm -rf ~` *still* prompt as a circuit breaker (in a terminal, on a two-minute countdown after which the removal is denied), and a `PreToolUse` hook `deny` still blocks. **`auto` mode silently drops broad allow rules** — `Bash(*)`, wildcarded interpreters, package-manager run commands (e.g. `npm run *`), and all `Agent` and `Monitor` allows are dropped while it's active (they restore when you leave), and `defaultMode: "auto"` is *ignored* when set in `.claude/settings.json` or `.claude/settings.local.json` (the built-in default applies instead) — put it in user-level `~/.claude/settings.json`.

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

<!-- step: default asks first; acceptEdits auto-approves cwd file ops; plan proposes, no source edits until approved. -->
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

<!-- step: dontAsk auto-denies anything that would otherwise prompt (handy for CI). -->
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
