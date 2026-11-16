---
id: plugin-lifecycle
title: "Plugin lifecycle (last-used ledger)"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 66
summary: "Per-project last-used tracking for installed marketplace plugins, with opt-in deprecate/uninstall and ask-first ravenclaude-only install — ravenclaude-core is never auto-removed."
see_also: [bifrost, comfort-posture, command-review-tribunal]
last_verified: 2026-11-16
refresh_when: "Telemetry signals, unused_days default, auto_uninstall/auto_install defaults, or the core hard-pin change."
covers:
  - plugins/ravenclaude-core/scripts/plugin-lifecycle.py
  - plugins/ravenclaude-core/scripts/plugin-lifecycle-sweep.sh
  - plugins/ravenclaude-core/scripts/plugin-lifecycle-telemetry.sh
covers_digest: "sha256:1c894ff105b59bd76cfc997efd9b2c405e99fe70c93bb08aedbb0929c99a5d97"
nuance: "auto_uninstall OFF => zero uninstall CLI calls; ON => uninstall -y only for names the resolver accepts. Traversal names are refused before argv. auto_install off|ask|auto (absent=>off); auto --execute needs a matching tip/SHA pin. Core hard-pinned. Never ragnarok."
nuance_evidence:
  measured: 2026-11-16
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

control: `bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh` (46 pass, 0 fail on 2026-11-16).
With `auto_uninstall` OFF the sweep makes zero uninstall CLI
calls; with ON + mock CLI it records executed uninstalls via `claude plugin
uninstall -y` for a name the resolver accepts. A traversal-shaped name is
refused before an install command or an uninstall argv is built.
`auto_install: auto` is honored only when explicit (absent => off);
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

