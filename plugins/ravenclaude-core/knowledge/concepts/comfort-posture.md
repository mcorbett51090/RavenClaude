---
id: comfort-posture
title: "Comfort-posture dashboard"
category: "Security"
kind: ravenclaude-built
order: 25
summary: "A point-and-click editor that writes Claude Code permission rules per category and layer — and keeps design check-ins independent of permission level."
see_also: [permission-layers, command-review-tribunal]
node_links:
  R: permission-layers
widget: permission-resolver
try_it:
  label: "Open the Settings tab"
  href: "#/settings"
last_verified: 2026-05-26
refresh_when: "The comfort-posture category set, the layer model, or the design_checkins decoupling changes."
sources:
  - label: "ravenclaude-core constitution"
    url: "plugins/ravenclaude-core/CLAUDE.md"
  - label: "apply-comfort-posture translator"
    url: "plugins/ravenclaude-core/scripts/apply-comfort-posture.py"
---

**Comfort posture** is RavenClaude's friendly front-end over the raw permission model. Instead of hand-editing `settings.json`, you set a level — **deny / ask / allow** — per *category* of action (file reads, code execution, remote mutations, …) and per *layer* (user / local / project). The dashboard's Settings tab serializes that to `.ravenclaude/comfort-posture.yaml`, and `apply-comfort-posture.py` translates it into the actual Claude Code permission rules — so the layer-precedence rules still govern what finally wins.

The load-bearing subtlety: **permission level ≠ design judgment.** Setting a category to `allow` only removes the click-to-approve on tool calls — it does **not** tell Claude to stop surfacing architectural decisions. That behavior is a *separate* flag, `design_checkins` (on by default), so relaxing permissions to move faster never silently mutes design check-ins. The two are deliberately decoupled.

```mermaid
flowchart TD
  U[You set deny/ask/allow<br/>per category · per layer] --> Y[(comfort-posture.yaml)]
  Y --> T[apply-comfort-posture.py]
  T --> R[Claude Code permission rules]
  U --> DC{design_checkins}
  DC -- "on (default)" --> PAUSE[Surface design decisions<br/>at any permission level]
  DC -- off --> FAST[Proceed · report after]
  class Y,T,R,PAUSE,FAST built
  class DC fact
```

<!-- mini -->
```mermaid-mini
flowchart LR
  L[deny/ask/allow<br/>per category] --> Y[(posture.yaml)] --> R[permission rules]
  class Y,R built
```
