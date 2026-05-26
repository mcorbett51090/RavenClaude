---
id: layout-hook
title: "Layout enforcement"
category: "Marketplace engineering"
kind: ravenclaude-built
order: 50
summary: "A PreToolUse hook plus a CI backstop block off-pattern file creation against .repo-layout.json — because path-scoped rule files load on Read, not Write."
see_also: [audit-gates, hook-lifecycle]
last_verified: 2026-05-26
refresh_when: "The enforce-layout hook, .repo-layout.json schema, or the validate-layout CI workflow changes."
sources:
  - label: "AGENTS.md — Layout & boundary rules"
    url: "AGENTS.md"
  - label: "Claude Code issue #23478"
    url: "https://github.com/anthropics/claude-code/issues/23478"
---

`hooks/enforce-layout.sh` runs `PreToolUse` on `Write|Edit|MultiEdit`: it reads `.repo-layout.json`, matches the target path against `allowed_globs`, and **denies an off-pattern write with a suggested correct location**. If the manifest is absent it silently allows everything — so consumers who install the plugin without a layout manifest aren't surprised.

Why a hook **and** CI: Claude Code issue #23478 confirms that path-scoped rule files (`paths:` frontmatter) load only on **Read**, not on **Write** — they cannot prevent off-pattern file *creation*. So the in-loop hook gives fast feedback during a session (Claude only), and `.github/workflows/validate-layout.yml` is the **cross-tool backstop** that catches direct human commits, Cursor/Codex/Aider edits, and any case where the hook didn't fire.

```mermaid
flowchart TD
  W[Write / Edit / MultiEdit] --> H[enforce-layout.sh · PreToolUse]
  H --> M{path matches an<br/>allowed_glob?}
  M -- yes --> OK[allow]
  M -- no --> DENY[deny + suggest correct path]
  PR[Any commit · any tool] --> CI[validate-layout.yml]
  CI --> CIM{matches allow-list?}
  CIM -- no --> FAIL[CI fails]
  CIM -- yes --> PASS[CI passes]
  class W,H,M,PR fact
  class OK,DENY,CI,CIM,FAIL,PASS built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  W[Write] --> H{matches<br/>allow-list?}
  H -- no --> D[deny + CI backstop]
  H -- yes --> A[allow]
  class D,A built
```
