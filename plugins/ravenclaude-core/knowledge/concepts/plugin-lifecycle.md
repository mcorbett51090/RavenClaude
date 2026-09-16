---
id: plugin-lifecycle
title: "Plugin lifecycle (last-used ledger)"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 66
summary: "Per-project last-used tracking for installed marketplace plugins, with opt-in deprecate/uninstall and ask-first ravenclaude-only install — ravenclaude-core is never auto-removed."
see_also: [bifrost, comfort-posture, command-review-tribunal]
last_verified: 2026-09-16
refresh_when: "Telemetry signals, unused_days default, auto_uninstall/auto_install defaults, or the core hard-pin change."
covers:
  - plugins/ravenclaude-core/scripts/plugin-lifecycle.py
  - plugins/ravenclaude-core/scripts/plugin-lifecycle-sweep.sh
  - plugins/ravenclaude-core/scripts/plugin-lifecycle-telemetry.sh
covers_digest: "sha256:6bbb35ebcb31a44c392757c6ed379f9c5ec72bfd72ba415bd404e4169eea1561"
nuance: "auto_uninstall OFF => zero uninstall CLI calls. auto_uninstall ON => may shell `claude plugin uninstall … -y` for fail-closed-eligible plugins only. auto_install accepts off|ask|auto (absent/unknown => off); auto still needs a cited need. ravenclaude-core@ravenclaude is a hard pin even if pins:[] is empty. Never ragnarok."
nuance_evidence:
  measured: 2026-09-15
  control: "bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh — M2 zero uninstalls when OFF; EXEC mock CLI when ON; AUTO mode opt-in; M3/MF teeth core never uninstallable; NORG"
  falsifier: "sweep uninstalling when auto_uninstall OFF, shelling cache-reset DR, auto install without cited need, or core appearing in would_uninstall"
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

A SessionStart sweep that uninstalls unused plugins when defaults stay OFF-violating, or an auto-install
path that quietly pulls marketplace packages without ask — and that presence in the
installed list counts as "used."

## The discriminator

control: `bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh` (28 pass).
Measured 2026-09-16: with `auto_uninstall` OFF the sweep makes zero uninstall CLI
calls; with ON + mock CLI it records executed uninstalls via `claude plugin
uninstall -y`. `auto_install: auto` is honored only when explicit (absent => off);
uncited auto stays CTA. Core is hard-pinned (MF teeth).

## Why it matters

Defaults OFF + opt-in execute/auto keep the surface careful. Ask-first ravenclaude-only
install and `/reload-plugins` before usable close the empty-cited and cache-path
AppSec locks. Copilot `-p` and Cursor SessionStart caveats stay honest — no slash
parity claim.

Falsifier: sweep shells uninstall when OFF, cache-reset DR, `auto` installs without
cited need, or core lands in `would_uninstall`.

Probe: `plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh`.

