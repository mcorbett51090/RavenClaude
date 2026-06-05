---
id: hook-lifecycle
title: "Hooks: verdicts & exit codes"
category: "Platform model"
kind: platform-fact
difficulty: expert
order: 20
summary: "Only exit 2 blocks a tool call; a hook deny beats bypass mode, but a hook allow can't override a settings deny."
see_also: [permission-layers, command-review-tribunal]
last_verified: 2026-05-25
refresh_when: "Anthropic changes hook exit-code semantics, the hookSpecificOutput schema, or timeout behavior."
sources:
  - label: "Hooks reference"
    url: "https://code.claude.com/docs/en/hooks"
  - label: "Hooks guide"
    url: "https://code.claude.com/docs/en/hooks-guide"
---

A `PreToolUse` hook reads the pending tool call as JSON on stdin and decides its fate. **Exit codes are the load-bearing, easy-to-get-wrong detail:** only **exit 2** blocks (and the hook's stderr is fed back to the model); **exit 0** allows; and **exit 1 or any other code is a *non-blocking* error — the tool still runs.** The trap is that `exit 1` is the conventional Unix "failure", so a policy hook that fails with `exit 1` *looks* like it blocked but doesn't.

For richer control, a hook can instead print a `hookSpecificOutput.permissionDecision` JSON on **exit 0**: `allow`, `deny`, `ask`, or `defer` (headless-only). When several hooks and rules apply, priority is **`deny` > `defer` > `ask` > `allow`**.

Two asymmetries make this safe: a hook **`deny` beats permission-mode bypass** (it blocks even under `bypassPermissions`), but a hook **`allow` does NOT override a settings `deny`** — hooks can *tighten* but never *loosen*. Note hooks **fail open**: on timeout or crash the tool proceeds, so a hook that must fail closed has to emit its own `deny` before its deadline.

```mermaid
flowchart TD
  H[PreToolUse hook] --> EX{exit code?}
  EX -- "exit 2" --> BLOCK[Blocked · stderr fed to model]
  EX -- "exit 1 / other" --> NB[Non-blocking error · tool still RUNS]
  EX -- "exit 0" --> J{JSON permissionDecision?}
  J -- deny --> DEN[Denied · beats bypass mode]
  J -- ask --> ASK[User prompted]
  J -- "allow / none" --> ALL[Prompt skipped · settings deny still wins]
  class H,EX,J,NB,ASK,ALL fact
  class BLOCK,DEN built
```

<!-- step: A PreToolUse hook reads the pending tool call as JSON on stdin. -->
```mermaid-step
flowchart LR
  N1[Read stdin] --> N2[Exit 2 blocks] --> N3[Exit 1 runs] --> N4[Exit 0 verdict] --> N5[Tighten only]
  class N1 built
```

<!-- step: Exit 2 blocks the call — and the hook's stderr is fed back to the model. -->
```mermaid-step
flowchart LR
  N1[Read stdin] --> N2[Exit 2 blocks] --> N3[Exit 1 runs] --> N4[Exit 0 verdict] --> N5[Tighten only]
  class N2 built
```

<!-- step: Exit 1 (or any other code) is a non-blocking error: the tool still RUNS. The trap. -->
```mermaid-step
flowchart LR
  N1[Read stdin] --> N2[Exit 2 blocks] --> N3[Exit 1 runs] --> N4[Exit 0 verdict] --> N5[Tighten only]
  class N3 built
```

<!-- step: Exit 0 with a permissionDecision JSON: allow / deny / ask (priority deny > defer > ask > allow). -->
```mermaid-step
flowchart LR
  N1[Read stdin] --> N2[Exit 2 blocks] --> N3[Exit 1 runs] --> N4[Exit 0 verdict] --> N5[Tighten only]
  class N4 built
```

<!-- step: Hooks only tighten: a deny beats bypass mode, but an allow can't override a settings deny. -->
```mermaid-step
flowchart LR
  N1[Read stdin] --> N2[Exit 2 blocks] --> N3[Exit 1 runs] --> N4[Exit 0 verdict] --> N5[Tighten only]
  class N5 built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  E{exit?} -- "2" --> B[blocks]
  E -- "0" --> J[JSON verdict]
  E -- "1" --> R[runs anyway]
  class B built
```
