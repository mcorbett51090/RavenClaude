---
id: plugin-lifecycle
title: "Plugin lifecycle (last-used ledger)"
category: "Marketplace engineering"
kind: ravenclaude-built
order: 66
summary: "Per-project last-used tracking for installed marketplace plugins, with opt-in deprecate/uninstall and ask-first ravenclaude-only install — ravenclaude-core is never auto-removed."
see_also: [bifrost, comfort-posture, command-review-tribunal]
last_verified: 2026-09-15
refresh_when: "Telemetry signals, unused_days default, auto_uninstall/auto_install defaults, or the core hard-pin change."
sources:
  - label: "scripts/plugin-lifecycle.py"
    url: "plugins/ravenclaude-core/scripts/plugin-lifecycle.py"
---

**Plugin lifecycle** is RavenClaude's per-project answer to "which installed plugins are actually used here?" It writes a local ledger at `.ravenclaude/plugin-lifecycle.json` (gitignored) and bumps `last_used_at` only when a **skill**, **agent**, or **slash** from that plugin is invoked. Mere SessionStart presence and opening the dashboard do **not** count as use — otherwise unused_days would never trip.

Defaults follow the Runes/Thing class: after P1, tracking is **ON** once a comfort-posture file exists; `auto_uninstall` and `auto_install` stay **OFF** unless the user opts in. Auto-install v1 is **ask-first** and **ravenclaude marketplace only** (`auto` mode is NO-SHIP). `ravenclaude-core@ravenclaude` is a hard pin and is never auto-removed under any posture.

The SessionStart sweep surfaces deprecate notices when tracking is on. It never shells the cache-reset disaster-recovery command, and it does not claim a freshly installed plugin usable until `/reload-plugins`. Host caveats: Copilot CLI under `-p` does not fire SessionStart; Cursor SessionStart is fail-open on malformed hook responses — do not claim slash-install parity there.

```mermaid
flowchart TD
  USE[Skill / agent / slash] --> LEDGER[.ravenclaude/plugin-lifecycle.json]
  SS[SessionStart sweep] --> NOTICE[Deprecate notice]
  SS -.->|auto_uninstall off| NONE[Zero uninstalls]
  ASK[auto_install ask + cited need] --> CONFIRM[User confirm]
  CONFIRM --> INST[/plugin install name@ravenclaude/]
  INST --> RELOAD[/reload-plugins/]
  class USE,LEDGER,NOTICE,CONFIRM,INST,RELOAD built
```
