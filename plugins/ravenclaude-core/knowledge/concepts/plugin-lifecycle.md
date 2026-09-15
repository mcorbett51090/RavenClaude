---
id: plugin-lifecycle
title: "Plugin lifecycle (last-used ledger)"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 66
summary: "Per-project last-used tracking for installed marketplace plugins, with opt-in deprecate/uninstall and ask-first ravenclaude-only install — ravenclaude-core is never auto-removed."
see_also: [bifrost, comfort-posture, command-review-tribunal]
last_verified: 2026-09-15
refresh_when: "Telemetry signals, unused_days default, auto_uninstall/auto_install defaults, or the core hard-pin change."
covers:
  - plugins/ravenclaude-core/scripts/plugin-lifecycle.py
  - plugins/ravenclaude-core/scripts/plugin-lifecycle-sweep.sh
  - plugins/ravenclaude-core/scripts/plugin-lifecycle-telemetry.sh
covers_digest: "sha256:83c081f8414363ddd644f27771294370fab40f81b39728eae61c5a18e53613fb"
nuance: "auto_uninstall OFF still records would_uninstall with executed:false; SessionStart never shells uninstall. auto_install auto is coerced OFF (NO-SHIP). ravenclaude-core@ravenclaude is a hard pin even if pins:[] is empty."
nuance_evidence:
  measured: 2026-09-15
  control: "bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh — M2 zero would_uninstall when OFF; ASK auto coerced off; M3/MF teeth core never uninstallable; plan executed:false"
  falsifier: "sweep invoking uninstall or cache-reset DR, auto mode performing install without ask, or core appearing in would_uninstall"
  probe: "plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh"
nuance_source: "plugins/ravenclaude-core/scripts/plugin-lifecycle.py; AppSec land DIGEST SHIP-WITH-CONDITIONS 2026-09-15"
verify:
  tier: "effect"
  strength: "executed"
  class: "hook-selftest"
  probe: "plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh"
  teeth_exit: 1
sources:
  - label: "scripts/plugin-lifecycle.py"
    url: "plugins/ravenclaude-core/scripts/plugin-lifecycle.py"
---

## What a reader would have assumed instead

A SessionStart sweep that uninstalls unused plugins by default, or an auto-install
path that quietly pulls marketplace packages without ask — and that presence in the
installed list counts as "used."

## The discriminator

control: `bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh` (28 pass).
Measured 2026-09-15: with `auto_uninstall` OFF the sweep records a plan with
`executed: false` and zero uninstalls; `auto_install: auto` is coerced OFF; core is
hard-pinned (MF teeth: neutering `is_core_key` is what makes core uninstallable).

## Why it matters

Defaults OFF + plan-only uninstall keep the surface opt-in. Ask-first ravenclaude-only
install and `/reload-plugins` before usable close the empty-cited and cache-path
AppSec locks. Copilot `-p` and Cursor SessionStart caveats stay honest — no slash
parity claim.

Falsifier: sweep shells uninstall or cache-reset DR, `auto` installs without ask, or
core lands in `would_uninstall`.

Probe: `plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh`.

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
