---
id: environment-context
title: "Environment context & discovery"
category: "Orientation & capability"
kind: ravenclaude-built
difficulty: intermediate
order: 42
summary: "An optional file maps which environments your creds reach and what's pre-authorized — so the agent acts without asking where allowed, and stops on forbidden actions."
see_also: [capability-banner, decision-trees]
last_verified: 2026-05-26
refresh_when: "The environment-context pre-action check or the discovery skill's contract changes."
sources:
  - label: "ravenclaude-core constitution"
    url: "plugins/ravenclaude-core/CLAUDE.md"
  - label: "environment-context template"
    url: "plugins/ravenclaude-core/templates/environment-context.md"
---

`.ravenclaude/environment-context.md` (at the **consumer's** project root, optional) records each environment (DEV / TEST / PROD / named), its role, its **pre-authorized action categories**, and a **forbidden** list. The Capability Grounding Protocol does a **pre-action check** against it: if the current environment pre-authorizes the action category, the agent **executes without asking** (no "did you try X?" round-trip); if the action is forbidden, it **stops** for explicit confirmation regardless of role; if the file is silent, it falls through to alternate-methods enumeration.

When the file is absent, the agent offers the **environment-discovery** skill instead of asking you to fill in a template by hand — it probes installed CLIs read-only, decodes any acquired JWTs, and drafts the file for you to save/edit/skip. Discovery never runs without confirmation, is read-only by contract, and **never writes credentials** (those live in env vars / Key Vault; the file holds posture, not secrets).

```mermaid
flowchart TD
  ACT[Agent about to act] --> F{environment-context.md present?}
  F -- no --> ALT[Fall through to alternate-methods]
  F -- yes --> CAT{Action pre-authorized<br/>for current env?}
  CAT -- yes --> RUN[Execute · no prompt]
  CAT -- forbidden --> STOP[Stop · require confirmation]
  CAT -- "not listed" --> ALT
  class ACT,F,CAT fact
  class ALT,RUN,STOP built
```

<!-- step: The agent is about to act. -->
```mermaid-step
flowchart LR
  N1[About to act] --> N2[File present] --> N3[Pre authorized] --> N4[Forbidden stop] --> N5[Silent fallthrough]
  class N1 built
```

<!-- step: Is environment-context.md present? If absent, fall through to alternate-methods. -->
```mermaid-step
flowchart LR
  N1[About to act] --> N2[File present] --> N3[Pre authorized] --> N4[Forbidden stop] --> N5[Silent fallthrough]
  class N2 built
```

<!-- step: Action pre-authorized for the current environment? Execute, no prompt. -->
```mermaid-step
flowchart LR
  N1[About to act] --> N2[File present] --> N3[Pre authorized] --> N4[Forbidden stop] --> N5[Silent fallthrough]
  class N3 built
```

<!-- step: Action forbidden? Stop for explicit confirmation, regardless of role. -->
```mermaid-step
flowchart LR
  N1[About to act] --> N2[File present] --> N3[Pre authorized] --> N4[Forbidden stop] --> N5[Silent fallthrough]
  class N4 built
```

<!-- step: File silent on it? Fall through to alternate-methods. Discovery can draft the file, read-only. -->
```mermaid-step
flowchart LR
  N1[About to act] --> N2[File present] --> N3[Pre authorized] --> N4[Forbidden stop] --> N5[Silent fallthrough]
  class N5 built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  A[Action] --> C{pre-authorized<br/>here?}
  C -- yes --> R[run]
  C -- forbidden --> S[stop]
  class R,S built
```
