---
id: capability-banner
title: "Capability-orientation banner"
category: "Orientation & capability"
kind: ravenclaude-built
order: 40
summary: "A SessionStart hook injects what the project touches, the auth it holds (names only), and the effective permissions — so the agent never acts as if it has no access."
see_also: [session-start-context, comfort-posture]
last_verified: 2026-05-26
refresh_when: "The capability-orientation hook's banner contents or its salience-not-enforcement framing change."
sources:
  - label: "ravenclaude-core constitution"
    url: "plugins/ravenclaude-core/CLAUDE.md"
  - label: "Claude Code permissions (SessionStart)"
    url: "plugins/ravenclaude-core/knowledge/claude-code-permissions.md"
---

The `capability-orientation.sh` SessionStart hook assembles a **capability banner** and injects it via `additionalContext` every session. It states the project's detected external surface, the auth it holds (env-var **names/presence only — never values; no network calls**), the effective `.claude/settings.json` permissions, and a presence/staleness summary of `environment-context.md`.

Why it exists: the behavioral instruction "read the posture at session start" is prose the model often skips. The hook makes the summary impossible to miss. Crucially, it is a **salience boost, not enforcement** — the real gate is the permission rules; the banner just stops the agent acting as if it has no access (the "did you try X?" round-trip on actions it's already authorized for). The banner is a *pointer*; `environment-context.md` stays the authoritative source for per-environment detail.

```mermaid
flowchart TD
  S[Session starts] --> H[capability-orientation.sh]
  H --> R1[Detect project surface]
  H --> R2[Read auth env-var NAMES · no values · no network]
  H --> R3[Read effective settings.json permissions]
  R1 & R2 & R3 --> B[Banner via additionalContext]
  B --> A[Agent is oriented — but NOT gated]
  A --> G[(Real gate: permission rules)]
  class S,H,R1,R2,R3 built
  class B,A built
  class G fact
```

<!-- mini -->
```mermaid-mini
flowchart LR
  S[SessionStart] --> B[surface + auth + perms]
  B --> A[agent oriented<br/>· not enforcement]
  class B,A built
```
