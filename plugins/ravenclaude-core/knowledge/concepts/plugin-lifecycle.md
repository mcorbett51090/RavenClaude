---
id: plugin-lifecycle
title: "Plugin lifecycle (last-used ledger)"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 66
summary: "Per-project last-used tracking for installed marketplace plugins, with opt-in deprecate/uninstall and ask-first ravenclaude-only install — ravenclaude-core is never auto-removed."
see_also: [bifrost, comfort-posture, command-review-tribunal]
last_verified: 2026-09-19
refresh_when: "Telemetry signals, unused_days default, auto_uninstall/auto_install defaults, or the core hard-pin change."
covers:
  - plugins/ravenclaude-core/scripts/plugin-lifecycle.py
  - plugins/ravenclaude-core/scripts/plugin-lifecycle-sweep.sh
  - plugins/ravenclaude-core/scripts/plugin-lifecycle-telemetry.sh
covers_digest: "sha256:91bc197c98dca552e593ef59249ed0381055c26b07049a6ef6eaed35b19b3332"
nuance: "auto_uninstall OFF => zero uninstall CLI calls; ON => may shell `claude plugin uninstall … -y` for fail-closed-eligible only. auto_install off|ask|auto (absent=>off); prefer ask until tip/SHA pins. auto --execute needs expected tip/SHA (CLI or install_pins) matching observed tip/hash — fail-closed pin_missing/mismatch. Cited need. Core hard-pinned. Never ragnarok."
nuance_evidence:
  measured: 2026-09-19
  control: "bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh — M2/EXEC/AUTO; PINAUTO pin_missing/match/mismatch/install_pins; M3/MF; NORG"
  falsifier: "sweep uninstall when OFF, cache-reset DR, auto install without cited need/pin, or core in would_uninstall"
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

control: `bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh` (41 pass).
Measured 2026-09-19: with `auto_uninstall` OFF the sweep makes zero uninstall CLI
calls; with ON + mock CLI it records executed uninstalls via `claude plugin
uninstall -y`. `auto_install: auto` is honored only when explicit (absent => off);
uncited auto stays CTA. Auto `--execute` is tip/SHA pin-gated (prefer ask).
Core is hard-pinned (MF teeth).

## Why it matters

Defaults OFF + opt-in execute/auto keep the surface careful. Ask-first ravenclaude-only
install and `/reload-plugins` before usable close the empty-cited and cache-path
AppSec locks. Copilot `-p` and Cursor SessionStart caveats stay honest — no slash
parity claim.

Falsifier: sweep shells uninstall when OFF, cache-reset DR, `auto` installs without
cited need or pin, or core lands in `would_uninstall`.

Probe: `plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh`.

