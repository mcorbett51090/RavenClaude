---
id: saga-log
title: "The Sága audit log"
category: "Security"
kind: ravenclaude-built
order: 32
summary: "Every command-review verdict writes one JSON entry — command, category, tier, per-seat votes, concerns, final verdict — under .ravenclaude/runs/thing/."
see_also: [command-review-tribunal, model-diversity]
last_verified: 2026-05-26
refresh_when: "The Sága log entry shape or its on-disk location changes."
sources:
  - label: "thing skill (operating reference)"
    url: "plugins/ravenclaude-core/skills/thing/SKILL.md"
---

Every tribunal verdict — allow, edit, deny, or ask — writes exactly **one JSON entry** to `.ravenclaude/runs/thing/<id>.json`, the **Sága log**. The entry records the command, its category, the resolved tier, each seat's verdict, the concerns cited, the final verdict (and the revised command on an EDIT), and the duration.

This is the observability substrate: it turns an otherwise opaque "the panel decided" into an auditable trail you can read after the fact to tune the panel, the `gate_floor`, or the bypass patterns. It's **gitignored by default** — the log is local operational data, not something to commit.

```mermaid
flowchart TD
  V[Tribunal renders a verdict] --> E[Write one JSON entry]
  E --> F[command · category · tier<br/>per-seat votes · concerns<br/>final verdict · duration]
  F --> D[(.ravenclaude/runs/thing/&lt;id&gt;.json)]
  D --> U[Audit · tune panel / gate_floor / bypass]
  class V,E,F,D,U built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  V[Verdict] --> J[(Sága JSON entry)]
  J --> A[auditable trail]
  class V,J,A built
```
