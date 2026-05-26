---
id: getting-started
title: "Getting started"
category: "Getting started"
kind: ravenclaude-built
order: 5
summary: "Add the marketplace, install ravenclaude-core, run /dashboard. Needs jq + python3; under Copilot CLI it's `ravenclaude install`."
see_also: [comfort-posture, capability-banner]
last_verified: 2026-05-26
refresh_when: "The install steps, requirements, or slash-command surface change."
sources:
  - label: "ravenclaude-core README"
    url: "plugins/ravenclaude-core/README.md"
  - label: "AGENTS.md — Setup commands"
    url: "AGENTS.md"
---

RavenClaude is a Claude Code **plugin marketplace**. To use the core plugin: add the marketplace, install the plugin, reload. `jq` and `python3` are required for the CI workflows and the layout-enforcement hook (both ship in the devcontainer).

```text
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

After install, run **`/dashboard`** to launch the comfort-posture editor (point-and-click permission rules + command-review toggles, with one-click Save & apply). Domain plugins (`power-platform`, `finance`, …) build on core, so install it first. Running under **GitHub Copilot CLI** instead? Use `bash scripts/ravenclaude install` — and from then on, updating is just `git pull`.

```mermaid
flowchart TD
  A[/plugin marketplace add …/] --> B[/plugin install ravenclaude-core/]
  B --> C[/reload-plugins/]
  C --> D[Run /dashboard]
  D --> E[Set comfort posture · opt into command review]
  E --> F[Start working — capability banner orients each session]
  class A,B,C,D,E,F built
```

<!-- mini -->
```mermaid-mini
flowchart LR
  I[install] --> D["/dashboard"] --> P[set posture]
  class I,D,P built
```
